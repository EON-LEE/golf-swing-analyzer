import streamlit as st
import logging
import logging.handlers
import os
import tempfile
from typing import Dict, Optional, Tuple
import uuid
import io

import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from config import MAX_FRAMES

# Streamlit 페이지 설정
st.set_page_config(
    page_title="골프 스윙 분석기",
    page_icon="🏌️",
    layout="wide"
)

# 로깅 설정
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

file_handler = logging.handlers.RotatingFileHandler(
    os.path.join(LOG_DIR, "app.log"),
    maxBytes=10*1024*1024,
    backupCount=5
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)
logger = logging.getLogger(__name__)

# 임시 디렉토리 설정
TEMP_DIR = os.path.join(tempfile.gettempdir(), "golf_swing_analyzer")
os.makedirs(TEMP_DIR, exist_ok=True)

# 세션 상태 초기화
if 'models' not in st.session_state:
    st.session_state.models = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

@st.cache_resource(ttl=None)
def load_models():
    """모델 로드 및 캐싱"""
    try:
        import importlib
        import pose_estimation
        import swing_analyzer
        import video_processor
        import analysis_service
        
        # 모듈 리로드
        importlib.reload(pose_estimation)
        importlib.reload(swing_analyzer)
        importlib.reload(video_processor)
        importlib.reload(analysis_service)
        
        # 클래스 임포트
        from pose_estimation import PoseEstimator
        from swing_analyzer import SwingAnalyzer
        from video_processor import VideoProcessor
        from analysis_service import SwingAnalysisService
        
        logger.info("Initializing models...")
        pose_estimator = PoseEstimator()
        swing_analyzer = SwingAnalyzer()
        video_processor = VideoProcessor()
        analysis_service = SwingAnalysisService()
        
        return (
            pose_estimator,
            swing_analyzer,
            video_processor,
            analysis_service
        )
    except Exception as e:
        logger.error(f"모델 로딩 중 오류: {str(e)}", exc_info=True)
        st.error(f"모델 로딩 중 오류가 발생했습니다: {str(e)}")
        return None

def get_models() -> Optional[Tuple]:
    """세션에서 모델 가져오기"""
    try:
        if st.session_state.models is None:
            logger.info("Loading models for the first time...")
            st.session_state.models = load_models()
            if st.session_state.models is not None:
                logger.info("Models loaded successfully")
            else:
                logger.error("Failed to load models")
        return st.session_state.models
    except Exception as e:
        logger.error(f"Error in get_models: {str(e)}", exc_info=True)
        return None

def save_uploaded_file(uploaded_file) -> Optional[str]:
    """업로드된 파일을 저장하고 경로를 반환"""
    temp_path = None
    try:
        if uploaded_file is None:
            return None
        
        # File size validation (100MB limit)
        if uploaded_file.size > 100 * 1024 * 1024:
            st.error("파일 크기가 너무 큽니다. 100MB 이하의 파일만 업로드 가능합니다.")
            return None
            
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in ['.mp4', '.avi', '.mov']:
            st.error("지원하지 않는 파일 형식입니다. MP4, AVI, MOV 파일만 업로드 가능합니다.")
            return None
        
        # Validate file name
        if not uploaded_file.name or len(uploaded_file.name.strip()) == 0:
            st.error("유효하지 않은 파일명입니다.")
            return None
            
        video_id = f"output_video_{str(uuid.uuid4())[:8]}{file_ext}"
        temp_path = os.path.join(TEMP_DIR, video_id)
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Verify file was written correctly
        if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
            st.error("파일 저장에 실패했습니다.")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return None
            
        return temp_path
    except Exception as e:
        logger.error(f"파일 저장 중 오류: {str(e)}")
        st.error(f"파일 저장 중 오류가 발생했습니다: {str(e)}")
        # Clean up failed file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return None

def analyze_swing(video_path: str, models: Tuple) -> Optional[Dict]:
    """골프 스윙 비디오 분석"""
    try:
        if not os.path.exists(video_path):
            st.error("비디오 파일을 찾을 수 없습니다.")
            return None
            
        if models is None:
            st.error("필요한 모델이 로드되지 않았습니다.")
            return None
            
        pose_estimator, swing_analyzer, _, _ = models

        logger.info(f"Starting analysis for video: {video_path}")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        frames_data = []
        frame_angles = []
        frame_count = 0
        processed_frames = 0
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            st.error("비디오 파일을 열 수 없습니다.")
            return None
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            st.error("비디오 파일이 비어있습니다.")
            cap.release()
            return None
        
        # Calculate frame skip ratio for large videos
        skip_ratio = max(1, total_frames // MAX_FRAMES) if total_frames > MAX_FRAMES else 1
        
        # 프레임 처리
        try:
            while cap.isOpened() and processed_frames < MAX_FRAMES:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Skip frames based on ratio
                if frame_count % skip_ratio != 0:
                    frame_count += 1
                    continue
                
            try:
                processed_frame, landmarks = pose_estimator.process_frame(frame)
                if landmarks:
                    angles = pose_estimator.calculate_angles(landmarks)
                    frame_angles.append(angles)
                    
                    # landmarks를 딕셔너리로 변환
                    landmarks_data = {
                        'left_shoulder': landmarks.left_shoulder.tolist(),
                        'right_shoulder': landmarks.right_shoulder.tolist(),
                        'left_elbow': landmarks.left_elbow.tolist(),
                        'right_elbow': landmarks.right_elbow.tolist(),
                        'left_wrist': landmarks.left_wrist.tolist(),
                        'right_wrist': landmarks.right_wrist.tolist(),
                        'left_hip': landmarks.left_hip.tolist(),
                        'right_hip': landmarks.right_hip.tolist(),
                        'left_knee': landmarks.left_knee.tolist(),
                        'right_knee': landmarks.right_knee.tolist(),
                        'left_ankle': landmarks.left_ankle.tolist(),
                        'right_ankle': landmarks.right_ankle.tolist(),
                        'nose': landmarks.nose.tolist() if hasattr(landmarks, 'nose') else [0, 0, 0]
                    }
                    
                    frames_data.append({
                        'angles': angles,
                        'landmarks': landmarks_data
                    })
                    processed_frames += 1
            except Exception as frame_error:
                logger.error(f"프레임 {frame_count} 처리 중 오류: {str(frame_error)}")
                continue
                    
            frame_count += 1
            progress = min(100, int((processed_frames / MAX_FRAMES) * 100))
            progress_bar.progress(progress)
            status_text.text(f"프레임 처리 중... ({processed_frames}/{min(MAX_FRAMES, total_frames)})")
        finally:
            cap.release()
            progress_bar.empty()
            status_text.empty()

        if not frames_data:
            st.error("비디오에서 유효한 프레임을 찾을 수 없습니다.")
            return None

        logger.info(f"분석 완료: {len(frames_data)} 프레임 처리됨")
        
        # 키 프레임 설정 - 0-based 인덱스 사용
        total_valid_frames = len(frames_data)
        key_frames = {
            'address': 0,  # 첫 번째 유효한 프레임을 어드레스로 설정
            'backswing': min(int(total_valid_frames * 0.3), total_valid_frames - 1),
            'top': min(int(total_valid_frames * 0.5), total_valid_frames - 1),
            'impact': min(int(total_valid_frames * 0.7), total_valid_frames - 1),
            'follow_through': min(int(total_valid_frames * 0.85), total_valid_frames - 1),
            'finish': total_valid_frames - 1  # 마지막 유효한 프레임
        }
        
        # 메트릭스 계산
        try:
            metrics = swing_analyzer._calculate_metrics(frames_data, key_frames)
            
            # 스윙 평가 수행
            evaluations = swing_analyzer._evaluate_swing(frames_data, key_frames, metrics)
            
            return {
                "message": "분석이 완료되었습니다.",
                "frames": frames_data,
                "metrics": metrics,
                "key_frames": key_frames,
                "evaluations": evaluations
            }
        except Exception as e:
            logger.error(f"Error in analyze_swing: {str(e)}", exc_info=True)
            st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
            return None
    except Exception as e:
        logger.error(f"Error in analyze_swing: {str(e)}", exc_info=True)
        st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
        return None

def create_sequence_image(video_path: str, key_frames: Dict[str, int]) -> Optional[np.ndarray]:
    """스윙 시퀀스 이미지 생성"""
    try:
        if not os.path.exists(video_path):
            st.error("비디오 파일을 찾을 수 없습니다.")
            return None
            
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            st.error("비디오 파일을 열 수 없습니다.")
            return None
            
        frames = []
        frame_order = ['address', 'backswing', 'impact', 'follow_through', 'finish']
        
        for phase in frame_order:
            frame_idx = key_frames.get(phase)
            if frame_idx is not None:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    cv2.putText(frame, phase.upper(), (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    frames.append(frame)
        
        cap.release()
        
        if not frames:
            st.error("시퀀스 이미지를 생성할 프레임이 없습니다.")
            return None
            
        target_height = 480
        processed_frames = []
        for frame in frames:
            h, w = frame.shape[:2]
            aspect = w / h
            target_width = int(target_height * aspect)
            processed_frames.append(cv2.resize(frame, (target_width, target_height)))
            
        return np.hstack(processed_frames)
        
    except Exception as e:
        logger.error(f"Error creating sequence image: {str(e)}")
        st.error(f"시퀀스 이미지 생성 중 오류가 발생했습니다: {str(e)}")
        return None

def create_angle_graph(analysis_data: Dict) -> Optional[bytes]:
    """각도 변화 그래프 생성"""
    try:
        plt.figure(figsize=(12, 6))
        frames = analysis_data.get('frames', [])
        if not frames:
            st.error("그래프를 생성할 데이터가 없습니다.")
            return None
            
        frame_indices = range(len(frames))
        angles = {
            'Right Arm': [frame['angles'].get('right_arm', 0) for frame in frames],
            'Left Arm': [frame['angles'].get('left_arm', 0) for frame in frames],
            'Shoulders': [frame['angles'].get('shoulder_angle', 0) for frame in frames],
            'Hips': [frame['angles'].get('hips_inclination', 0) for frame in frames]
        }
        
        for label, values in angles.items():
            plt.plot(frame_indices, values, label=label)
            
        key_frames = analysis_data.get('key_frames', {})
        for phase, frame_idx in key_frames.items():
            if frame_idx < len(frames):
                plt.axvline(x=frame_idx, color='r', linestyle='--', alpha=0.3)
                plt.text(frame_idx, plt.ylim()[1], phase.upper(), 
                        rotation=45, ha='right')
        
        plt.title('Angle Changes During Swing')
        plt.xlabel('Frame')
        plt.ylabel('Angle (degrees)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close()
        buf.seek(0)
        return buf.getvalue()
        
    except Exception as e:
        logger.error(f"Error creating angle graph: {str(e)}")
        st.error(f"각도 그래프 생성 중 오류가 발생했습니다: {str(e)}")
        return None

def main():
    """메인 애플리케이션"""
    st.title("골프 스윙 분석기 🏌️")
    st.write("골프 스윙 영상을 업로드하여 자세를 분석해보세요!")

    # 모델 로드
    models = get_models()
    if models is None:
        st.error("필요한 모델을 로드할 수 없습니다. 관리자에게 문의하세요.")
        return

    uploaded_file = st.file_uploader("골프 스윙 영상 업로드", type=['mp4', 'avi', 'mov'])
    
    if uploaded_file is not None:
        temp_path = save_uploaded_file(uploaded_file)
        
        if temp_path:
            st.video(temp_path)
            
            if st.button("스윙 분석 시작"):
                with st.spinner("스윙을 분석하고 있습니다..."):
                    analysis_result = analyze_swing(temp_path, models)
                    
                    if analysis_result:
                        st.session_state.analysis_complete = True
                        st.success("분석이 완료되었습니다!")
                        
                        tab1, tab2, tab3, tab4 = st.tabs(["스윙 시퀀스", "각도 그래프", "상세 메트릭스", "스윙 평가"])
                        
                        with tab1:
                            st.subheader("스윙 시퀀스")
                            sequence_img = create_sequence_image(temp_path, analysis_result['key_frames'])
                            if sequence_img is not None:
                                sequence_img_rgb = cv2.cvtColor(sequence_img, cv2.COLOR_BGR2RGB)
                                st.image(sequence_img_rgb, use_column_width=True)
                        
                        with tab2:
                            st.subheader("각도 변화 그래프")
                            graph_bytes = create_angle_graph(analysis_result)
                            if graph_bytes:
                                st.image(graph_bytes)
                                
                                # 그래프 해석 추가
                                st.markdown("### 📊 그래프 해석")
                                metrics = analysis_result.get('metrics', {})
                                
                                st.markdown("""
                                #### 주요 지표 설명:
                                - **어깨 회전 (Shoulders)**: 백스윙에서 어깨의 회전 각도를 보여줍니다. 이상적인 최대 회전은 80도 이상입니다.
                                - **팔 각도 (Right/Left Arm)**: 팔의 펴짐 정도를 나타냅니다. 어드레스와 임팩트에서 165-180도가 이상적입니다.
                                - **힙 회전 (Hips)**: 골반의 회전 각도입니다. 임팩트 시점에서 45도 이상이 권장됩니다.
                                """)
                                
                                # 현재 스윙의 특징 분석
                                st.markdown("#### 🎯 현재 스윙 분석")
                                shoulder_rotation = metrics.get('shoulder_rotation', 0)
                                impact_angle = metrics.get('impact_angle', 0)
                                hip_rotation = metrics.get('hip_rotation', 0)
                                
                                analysis_text = []
                                if shoulder_rotation >= 80:
                                    analysis_text.append("✅ 어깨 회전이 충분합니다 ({}도)".format(round(shoulder_rotation, 1)))
                                else:
                                    analysis_text.append("❌ 어깨 회전이 부족합니다 ({}도, 목표: 80도 이상)".format(round(shoulder_rotation, 1)))
                                    
                                if 165 <= impact_angle <= 180:
                                    analysis_text.append("✅ 임팩트 시 팔 각도가 이상적입니다 ({}도)".format(round(impact_angle, 1)))
                                else:
                                    analysis_text.append("❌ 임팩트 시 팔 각도 개선이 필요합니다 ({}도, 목표: 165-180도)".format(round(impact_angle, 1)))
                                    
                                if hip_rotation >= 45:
                                    analysis_text.append("✅ 힙 회전이 충분합니다 ({}도)".format(round(hip_rotation, 1)))
                                else:
                                    analysis_text.append("❌ 힙 회전이 부족합니다 ({}도, 목표: 45도 이상)".format(round(hip_rotation, 1)))
                                
                                for text in analysis_text:
                                    st.markdown(text)
                                    
                        with tab3:
                            st.subheader("상세 메트릭스")
                            metrics = analysis_result['metrics']
                            cols = st.columns(3)
                            for idx, (metric_name, value) in enumerate(metrics.items()):
                                with cols[idx % 3]:
                                    st.metric(
                                        label=metric_name,
                                        value=f"{value:.2f}°" if isinstance(value, (int, float)) else value
                                    )
                        
                        with tab4:
                            st.subheader("스윙 평가")
                            
                            # 평가 기준 표 생성
                            st.markdown("### ⚖️ 평가 기준")
                            
                            criteria_data = {
                                "스윙 단계": ["어드레스 자세", "어드레스 자세", 
                                            "탑 자세", "탑 자세",
                                            "임팩트 자세", "임팩트 자세",
                                            "팔로우 스루", "팔로우 스루",
                                            "피니시 자세", "피니시 자세"],
                                "평가 항목": ["팔 각도", "자세 안정성",
                                            "어깨 회전", "머리 안정성",
                                            "팔 각도", "힙 회전",
                                            "팔로우 스루 완성도", "균형",
                                            "마무리 동작", "균형"],
                                "기준값": ["165-180도", "척추 각도 30도 이상",
                                         "최소 80도 이상", "초기 위치에서 움직임 0.1 이하",
                                         "165-180도", "45도 이상",
                                         "팔 각도 120도 이하", "오른쪽 무릎 각도 160도 이하",
                                         "팔 각도 120도 이하", "오른쪽 무릎 각도 160도 이하"],
                                "중요도": ["⭐⭐⭐", "⭐⭐",
                                         "⭐⭐⭐", "⭐⭐",
                                         "⭐⭐⭐", "⭐⭐⭐",
                                         "⭐⭐", "⭐⭐",
                                         "⭐⭐", "⭐⭐"]
                            }
                            
                            import pandas as pd
                            criteria_df = pd.DataFrame(criteria_data)
                            
                            # 표 스타일링을 위한 CSS
                            st.markdown("""
                            <style>
                            table {
                                width: 100%;
                                border-collapse: collapse;
                            }
                            th {
                                background-color: #1E1E1E;
                                color: white;
                                text-align: center !important;
                            }
                            td {
                                text-align: center !important;
                            }
                            tr:nth-child(odd) {
                                background-color: #2E2E2E;
                            }
                            </style>
                            """, unsafe_allow_html=True)
                            
                            # 표 출력
                            st.table(criteria_df)
                            
                            # 중요도 설명
                            st.markdown("""
                            #### 📝 중요도 설명
                            - ⭐⭐⭐ : 스윙의 핵심 요소
                            - ⭐⭐ : 보조적 중요 요소
                            """)
                            
                            st.markdown("---")
                            
                            if 'evaluations' in analysis_result:
                                evaluations = analysis_result['evaluations']
                                frames_data = analysis_result['frames']
                                key_frames = analysis_result['key_frames']
                                
                                # 각 스윙 단계별 평가 표시
                                phase_names = {
                                    'address': '어드레스 자세',
                                    'top': '탑 자세',
                                    'impact': '임팩트 자세',
                                    'follow_through': '팔로우 스루',
                                    'finish': '피니시 자세'
                                }
                                
                                check_names = {
                                    'Arm Angle Straight': '팔이 곧게 뻗어있나요? (165-180도)',
                                    'Posture Stable': '자세가 안정적인가요? (척추 각도 30도 이상)',
                                    'Shoulder Rotation Good': '어깨 회전이 충분한가요? (80도 이상)',
                                    'Head Stable': '머리가 안정적인가요? (움직임 0.1 이하)',
                                    'Hip Rotation Good': '힙 회전이 충분한가요? (45도 이상)',
                                    'Follow Through Complete': '팔로우 스루가 완성되었나요? (120도 이하)',
                                    'Balance Maintained': '균형이 잘 잡혔나요? (무릎 각도 160도 이하)',
                                    'Arm Straight': '팔이 곧게 뻗어있나요? (165-180도)'
                                }
                                
                                for phase, phase_evaluations in evaluations.items():
                                    st.markdown(f"### {phase_names.get(phase, phase)}")
                                    
                                    # 현재 프레임의 각도 데이터 가져오기
                                    frame_idx = key_frames.get(phase, 0)
                                    current_frame = frames_data[frame_idx] if frame_idx < len(frames_data) else None
                                    
                                    # 평가 결과를 표 형식으로 표시
                                    results = []
                                    for check_name, is_passed in phase_evaluations.items():
                                        current_value = None
                                        if current_frame:
                                            if check_name in ['Arm Angle Straight', 'Arm Straight']:
                                                current_value = current_frame['angles'].get('right_arm', 0)
                                            elif check_name == 'Posture Stable':
                                                current_value = current_frame['angles'].get('spine_angle', 0)
                                            elif check_name == 'Shoulder Rotation Good':
                                                current_value = current_frame['angles'].get('shoulder_angle', 0)
                                            elif check_name == 'Hip Rotation Good':
                                                current_value = current_frame['angles'].get('hip_angle', 0)
                                            elif check_name == 'Balance Maintained':
                                                current_value = current_frame['angles'].get('right_leg', 0)
                                            elif check_name == 'Head Stable':
                                                current_value = analysis_result['metrics'].get('head_movement', 0)
                                        
                                        result_text = "✅ 좋습니다" if is_passed else "❌ 개선이 필요합니다"
                                        if current_value is not None:
                                            result_text += f" (현재: {current_value:.1f}°)"
                                        
                                        results.append({
                                            "체크 항목": check_names.get(check_name, check_name),
                                            "결과": result_text
                                        })
                                    
                                    # 데이터프레임으로 변환하여 표시
                                    df = pd.DataFrame(results)
                                    st.table(df)
                                    
                                    # 단계별 조언 추가
                                    if not all(phase_evaluations.values()):
                                        st.markdown("#### 💡 조언")
                                        for check_name, is_passed in phase_evaluations.items():
                                            if not is_passed:
                                                current_value = None
                                                if current_frame:
                                                    if check_name in ['Arm Angle Straight', 'Arm Straight']:
                                                        current_value = current_frame['angles'].get('right_arm', 0)
                                                    elif check_name == 'Posture Stable':
                                                        current_value = current_frame['angles'].get('spine_angle', 0)
                                                    elif check_name == 'Shoulder Rotation Good':
                                                        current_value = current_frame['angles'].get('shoulder_angle', 0)
                                                    elif check_name == 'Hip Rotation Good':
                                                        current_value = current_frame['angles'].get('hip_angle', 0)
                                                    elif check_name == 'Balance Maintained':
                                                        current_value = current_frame['angles'].get('right_leg', 0)
                                                    elif check_name == 'Head Stable':
                                                        current_value = analysis_result['metrics'].get('head_movement', 0)
                                                
                                                advice = get_swing_advice(phase, check_name)
                                                if current_value is not None:
                                                    advice += f" (현재: {current_value:.1f}°)"
                                                st.info(advice)
                                    
                                    # 구분선 추가
                                    st.markdown("---")
                            else:
                                st.warning("평가 데이터가 없습니다.")

def get_swing_advice(phase: str, check_name: str) -> str:
    """스윙 단계와 체크 항목에 따른 조언을 반환합니다."""
    advice_dict = {
        'address': {
            'Arm Angle Straight': "팔을 더 곧게 펴보세요. 이상적인 각도는 165-180도 입니다.",
            'Posture Stable': "상체를 약간 숙이고, 무게 중심을 발 중앙에 두어 안정적인 자세를 만드세요."
        },
        'top': {
            'Shoulder Rotation Good': "백스윙 시 어깨 회전을 더 크게 해보세요. 파워를 위해서는 최소 80도 이상이 필요합니다.",
            'Head Stable': "백스윙 중에도 머리 위치를 최대한 고정하세요. 일관된 스윙을 위해 중요합니다."
        },
        'impact': {
            'Arm Straight': "임팩트 시점에서 팔을 더 곧게 펴보세요. 이상적인 각도는 165-180도 입니다.",
            'Hip Rotation Good': "임팩트 시 힙 회전을 더 적극적으로 해보세요. 최소 45도 이상 회전이 필요합니다."
        },
        'follow_through': {
            'Follow Through Complete': "팔로우 스루 동작을 더 크게 해보세요. 자연스러운 마무리가 중요합니다.",
            'Balance Maintained': "팔로우 스루 시 균형을 잘 잡아주세요. 체중 이동이 자연스러워야 합니다."
        },
        'finish': {
            'Follow Through Complete': "피니시 동작을 완성도 있게 마무리해주세요. 상체를 목표 방향으로 회전시키세요.",
            'Balance Maintained': "피니시 자세에서 균형을 잘 잡아주세요. 오른발 안쪽으로 체중을 이동하세요."
        }
    }
    
    return advice_dict.get(phase, {}).get(check_name, "자세를 전반적으로 점검해보세요.")

if __name__ == "__main__":
    main() 