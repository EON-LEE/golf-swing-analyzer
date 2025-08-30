import streamlit as st
import logging
import logging.handlers
import os
import tempfile
from typing import Dict, Optional, Tuple
import uuid
import io
import time

import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import plotly.graph_objects as go

from config import (
    MAX_FRAMES, SUPPORTED_VIDEO_FORMATS, LOG_LEVEL, 
    LOG_MAX_BYTES, LOG_BACKUP_COUNT, KEY_FRAME_RATIOS
)
from utils import validate_video_file, get_video_info, cleanup_temp_files

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
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

file_handler = logging.handlers.RotatingFileHandler(
    os.path.join(LOG_DIR, "app.log"),
    maxBytes=LOG_MAX_BYTES,
    backupCount=LOG_BACKUP_COUNT
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)
logger = logging.getLogger(__name__)

# 임시 디렉토리 설정
TEMP_DIR = os.path.join(tempfile.gettempdir(), "golf_swing_analyzer")
os.makedirs(TEMP_DIR, exist_ok=True)

# 지원되는 비디오 형식
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov']

def validate_video_file(file_path: str, supported_formats: list) -> bool:
    """비디오 파일 유효성 검사"""
    try:
        if not os.path.exists(file_path):
            return False
        
        # 파일 크기 확인 (최소 1KB)
        if os.path.getsize(file_path) < 1024:
            return False
        
        # OpenCV로 비디오 열기 테스트
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return False
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        
        return frame_count > 0
    except Exception:
        return False

# 세션 상태 초기화
if 'models' not in st.session_state:
    st.session_state.models = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

@st.cache_resource(ttl=None)
def load_models():
    """모델 로드 및 캐싱"""
    try:
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
        
        logger.info("Models loaded successfully")
        return (pose_estimator, swing_analyzer, video_processor, analysis_service)
        
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
    try:
        if uploaded_file is None:
            return None
        
        # 파일 크기 검사 (최대 100MB)
        max_size = 100 * 1024 * 1024
        if uploaded_file.size > max_size:
            st.error(f"파일 크기가 너무 큽니다. 최대 {max_size // (1024*1024)}MB까지 업로드 가능합니다.")
            return None
            
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in SUPPORTED_VIDEO_FORMATS:
            st.error(f"지원하지 않는 파일 형식입니다. {', '.join(SUPPORTED_VIDEO_FORMATS)} 파일만 업로드 가능합니다.")
            return None
        
        # 파일명 검증
        if not uploaded_file.name or len(uploaded_file.name.strip()) == 0:
            st.error("유효하지 않은 파일명입니다.")
            return None
            
        video_id = f"output_video_{str(uuid.uuid4())[:8]}{file_ext}"
        temp_path = os.path.join(TEMP_DIR, video_id)
        
        # 임시 디렉토리 확인
        os.makedirs(TEMP_DIR, exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # 파일 유효성 검사
        if not validate_video_file(temp_path, SUPPORTED_VIDEO_FORMATS):
            if os.path.exists(temp_path):
                os.remove(temp_path)
            st.error("업로드된 파일이 유효하지 않습니다.")
            return None
        
        logger.info(f"File saved successfully: {temp_path}")
        return temp_path
    except Exception as e:
        logger.error(f"파일 저장 중 오류: {str(e)}")
        st.error(f"파일 저장 중 오류가 발생했습니다: {str(e)}")
        return None

def analyze_swing(video_path: str, models: Tuple) -> Optional[Dict]:
    """골프 스윙 비디오 분석 - 메모리 효율적으로 개선"""
    cap = None
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
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            st.error("비디오 파일을 열 수 없습니다.")
            return None
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            st.error("비디오 파일이 비어있습니다.")
            return None
        
        # 메모리 효율적인 프레임 처리
        frames_data = []
        frame_count = 0
        skip_frames = max(1, total_frames // MAX_FRAMES)  # 설정된 최대 프레임으로 제한
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # 프레임 스킵으로 메모리 사용량 줄이기
            if frame_count % skip_frames == 0:
                try:
                    processed_frame, landmarks = pose_estimator.process_frame(frame)
                    if landmarks:
                        angles = pose_estimator.calculate_angles(landmarks)
                        
                        # 랜드마크를 딕셔너리로 변환
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
                        
                except Exception as frame_error:
                    logger.warning(f"프레임 {frame_count} 처리 중 오류: {str(frame_error)}")
                    continue
                    
            frame_count += 1
            if frame_count % 10 == 0:  # 진행률 업데이트 빈도 줄이기
                progress = int((frame_count / total_frames) * 100)
                progress_bar.progress(progress)
                status_text.text(f"프레임 처리 중... {progress}%")
                
        if not frames_data:
            st.error("비디오에서 유효한 프레임을 찾을 수 없습니다.")
            return None

        logger.info(f"분석 완료: {len(frames_data)} 프레임 처리됨")
        
        # 키 프레임 설정 - 설정 파일의 비율 사용
        total_valid_frames = len(frames_data)
        key_frames = {}
        for phase, ratio in KEY_FRAME_RATIOS.items():
            if ratio == 0.0:
                key_frames[phase] = 0
            elif ratio == 1.0:
                key_frames[phase] = total_valid_frames - 1
            else:
                key_frames[phase] = min(int(total_valid_frames * ratio), total_valid_frames - 1)
        
        # 메트릭스 계산
        metrics = swing_analyzer._calculate_metrics(frames_data, key_frames)
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
    finally:
        if cap is not None:
            cap.release()
        progress_bar.empty()
        status_text.empty()

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

    # 임시 파일 정리
    cleanup_temp_files(TEMP_DIR)

    # 모델 로드
    models = get_models()
    if models is None:
        st.error("필요한 모델을 로드할 수 없습니다. 관리자에게 문의하세요.")
        return

    # 세션 상태 초기화
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 0
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'temp_path' not in st.session_state:
        st.session_state.temp_path = None

    uploaded_file = st.file_uploader("골프 스윙 영상 업로드", type=['mp4', 'avi', 'mov'])
    
    if uploaded_file is not None:
        temp_path = save_uploaded_file(uploaded_file)
        st.session_state.temp_path = temp_path
        
        if temp_path:
            st.video(temp_path)
            
            if st.button("스윙 분석 시작"):
                with st.spinner("스윙을 분석하고 있습니다..."):
                    analysis_result = analyze_swing(temp_path, models)
                    
                    if analysis_result:
                        st.session_state.analysis_result = analysis_result
                        st.session_state.analysis_complete = True
                        st.success("분석이 완료되었습니다!")

    # 분석 결과가 있을 때만 탭 표시
    if st.session_state.get('analysis_complete', False) and st.session_state.analysis_result:
        tab_names = ["스윙 시퀀스", "각도 그래프", "3D 분석", "상세 메트릭스", "스윙 평가"]
        tabs = st.tabs(tab_names)

        with tabs[0]:
            show_swing_sequence_with_state(st.session_state.temp_path, st.session_state.analysis_result)
        
        with tabs[1]:
            show_angle_graph(st.session_state.analysis_result)
            
        with tabs[2]:
            show_3d_analysis_with_state(st.session_state.analysis_result)
            
        with tabs[3]:
            show_detailed_metrics(st.session_state.analysis_result)
        
        with tabs[4]:
            show_swing_evaluation(st.session_state.analysis_result)

def show_swing_sequence_with_state(temp_path, analysis_result):
    """스윙 시퀀스 표시 (상태 관리 포함)"""
    st.subheader("스윙 시퀀스")
    
    # 정적 시퀀스 이미지
    sequence_img = create_sequence_image(temp_path, analysis_result['key_frames'])
    if sequence_img is not None:
        sequence_img_rgb = cv2.cvtColor(sequence_img, cv2.COLOR_BGR2RGB)
        st.image(sequence_img_rgb, use_column_width=True)
    
    # 프레임별 재생 기능 추가
    st.subheader("프레임별 재생")
    
    # 세션 상태 초기화
    if 'seq_current_frame' not in st.session_state:
        st.session_state.seq_current_frame = 0
    if 'seq_is_playing' not in st.session_state:
        st.session_state.seq_is_playing = False
    
    # 컨트롤 컬럼 생성
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
    
    # 재생 컨트롤
    with col1:
        if st.button("⏮️ 처음으로", key="seq_first"):
            st.session_state.seq_current_frame = 0
            st.session_state.seq_is_playing = False
    
    with col2:
        if st.button("▶️ 재생" if not st.session_state.seq_is_playing else "⏸️ 일시정지", key="seq_play"):
            st.session_state.seq_is_playing = not st.session_state.seq_is_playing
    
    with col3:
        if st.button("⏭️ 끝으로", key="seq_last"):
            st.session_state.seq_current_frame = len(analysis_result['frames']) - 1
            st.session_state.seq_is_playing = False
    
    # 프레임 슬라이더
    with col4:
        st.session_state.seq_current_frame = st.slider(
            "프레임",
            0,
            len(analysis_result['frames']) - 1,
            st.session_state.seq_current_frame,
            key="seq_slider"
        )
    
    # 현재 프레임 표시
    current_frame_data = analysis_result['frames'][st.session_state.seq_current_frame]
    
    # 프레임 정보를 시각화
    col_pose, col_info = st.columns([2, 1])
    
    with col_pose:
        # 포즈 시각화
        fig = create_pose_visualization(current_frame_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_info:
        # 현재 프레임의 각도 정보 표시
        st.markdown("### 현재 프레임 정보")
        angles = current_frame_data['angles']
        
        # 주요 각도 표시
        st.metric("어깨 회전", f"{angles.get('shoulder_angle', 0):.1f}°")
        st.metric("오른팔 각도", f"{angles.get('right_arm', 0):.1f}°")
        st.metric("왼팔 각도", f"{angles.get('left_arm', 0):.1f}°")
        st.metric("오른쪽 무릎", f"{angles.get('right_knee_angle', 0):.1f}°")
        st.metric("왼쪽 무릎", f"{angles.get('left_knee_angle', 0):.1f}°")
    
    # 자동 재생 로직
    if st.session_state.seq_is_playing:
        if st.session_state.seq_current_frame < len(analysis_result['frames']) - 1:
            st.session_state.seq_current_frame += 1
            time.sleep(0.1)  # 프레임 간 딜레이
            st.rerun()
        else:
            st.session_state.seq_is_playing = False
            st.rerun()

def show_3d_analysis_with_state(analysis_result):
    """3D 분석 결과 표시 (상태 관리 포함)"""
    st.subheader("3D 스윙 분석")
    
    # 세션 상태 초기화
    if 'three_d_frame_idx' not in st.session_state:
        st.session_state.three_d_frame_idx = 0
    if 'three_d_is_playing' not in st.session_state:
        st.session_state.three_d_is_playing = False
    
    # 3D 포즈 시각화
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("3D 포즈 뷰어")
        st.session_state.three_d_frame_idx = st.slider(
            "프레임 선택", 
            0, 
            len(analysis_result['frames']) - 1, 
            st.session_state.three_d_frame_idx,
            key="3d_frame_slider"
        )
        
        # Plotly를 사용한 3D 시각화
        fig = create_3d_pose_plot(analysis_result['frames'][st.session_state.three_d_frame_idx])
        st.plotly_chart(fig, use_container_width=True)
        
        # 재생 컨트롤
        cols = st.columns(3)
        if cols[0].button("⏮️ 처음으로", key="3d_first"):
            st.session_state.three_d_frame_idx = 0
            st.session_state.three_d_is_playing = False
        if cols[1].button("▶️ 재생" if not st.session_state.three_d_is_playing else "⏸️ 일시정지", key="3d_play"):
            st.session_state.three_d_is_playing = not st.session_state.three_d_is_playing
        if cols[2].button("⏭️ 끝으로", key="3d_last"):
            st.session_state.three_d_frame_idx = len(analysis_result['frames']) - 1
            st.session_state.three_d_is_playing = False
    
    with col2:
        st.subheader("3D 메트릭스")
        show_3d_metrics(analysis_result, st.session_state.three_d_frame_idx)
    
    # 자동 재생 로직
    if st.session_state.three_d_is_playing:
        if st.session_state.three_d_frame_idx < len(analysis_result['frames']) - 1:
            st.session_state.three_d_frame_idx += 1
            time.sleep(0.1)  # 프레임 간 딜레이
            st.rerun()
        else:
            st.session_state.three_d_is_playing = False
            st.rerun()

def create_pose_visualization(frame_data: Dict) -> go.Figure:
    """프레임 데이터를 사용하여 2D 포즈 시각화 생성"""
    # Plotly 피겨 생성
    fig = go.Figure()
    
    # 랜드마크 연결 정의
    connections = [
        ('left_shoulder', 'right_shoulder'),
        ('left_shoulder', 'left_elbow'),
        ('left_elbow', 'left_wrist'),
        ('right_shoulder', 'right_elbow'),
        ('right_elbow', 'right_wrist'),
        ('left_shoulder', 'left_hip'),
        ('right_shoulder', 'right_hip'),
        ('left_hip', 'right_hip'),
        ('left_hip', 'left_knee'),
        ('left_knee', 'left_ankle'),
        ('right_hip', 'right_knee'),
        ('right_knee', 'right_ankle')
    ]
    
    landmarks = frame_data['landmarks']
    
    # 랜드마크 점 추가
    for name, point in landmarks.items():
        fig.add_trace(go.Scatter(
            x=[point[0]], 
            y=[point[1]],
            mode='markers+text',
            name=name,
            text=[name],
            textposition='top center',
            marker=dict(size=10, color='blue'),
            showlegend=False
        ))
    
    # 연결선 추가
    for start, end in connections:
        if start in landmarks and end in landmarks:
            start_point = landmarks[start]
            end_point = landmarks[end]
            fig.add_trace(go.Scatter(
                x=[start_point[0], end_point[0]],
                y=[start_point[1], end_point[1]],
                mode='lines',
                line=dict(width=2, color='red'),
                showlegend=False
            ))
    
    # 레이아웃 설정
    fig.update_layout(
        showlegend=False,
        yaxis=dict(
            scaleanchor="x",
            scaleratio=1,
            range=[1, 0]  # y축 반전
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='white',
        width=600,
        height=600
    )
    
    return fig

def create_3d_pose_plot(frame_data: Dict) -> go.Figure:
    """프레임 데이터를 사용하여 3D 포즈 플롯 생성"""
    try:
        fig = go.Figure()
        
        # 디버그: 랜드마크 좌표 로깅
        logger.debug("3D Pose Landmarks:")
        for name, point in frame_data['landmarks'].items():
            logger.debug(f"{name}: {point}")
        
        # 좌표계 변환: MediaPipe의 좌표계를 골프 자세에 맞게 변환
        # MediaPipe: Y-up, X-right, Z-forward
        # 골프 자세: Y-up (height), X-right (width), Z-forward (depth)
        landmarks_transformed = {}
        for name, point in frame_data['landmarks'].items():
            landmarks_transformed[name] = [
                point[0],     # x -> x (right/left)
                point[1],     # y -> y (up/down)
                point[2]      # z -> z (forward/backward)
            ]
        
        # 랜드마크 점 추가
        for name, point in landmarks_transformed.items():
            fig.add_trace(go.Scatter3d(
                x=[point[0]],
                y=[point[1]],
                z=[point[2]],
                mode='markers+text',
                name=name,
                text=[name],
                textposition='top center',
                marker=dict(
                    size=8,
                    color='blue',
                    symbol='circle'
                ),
                showlegend=False
            ))
        
        # 스켈레톤 연결선 추가
        connections = [
            ('left_shoulder', 'right_shoulder'),
            ('left_shoulder', 'left_elbow'),
            ('left_elbow', 'left_wrist'),
            ('right_shoulder', 'right_elbow'),
            ('right_elbow', 'right_wrist'),
            ('left_shoulder', 'left_hip'),
            ('right_shoulder', 'right_hip'),
            ('left_hip', 'right_hip'),
            ('left_hip', 'left_knee'),
            ('left_knee', 'left_ankle'),
            ('right_hip', 'right_knee'),
            ('right_knee', 'right_ankle')
        ]
        
        for start, end in connections:
            if start in landmarks_transformed and end in landmarks_transformed:
                start_point = landmarks_transformed[start]
                end_point = landmarks_transformed[end]
                fig.add_trace(go.Scatter3d(
                    x=[start_point[0], end_point[0]],
                    y=[start_point[1], end_point[1]],
                    z=[start_point[2], end_point[2]],
                    mode='lines',
                    line=dict(color='red', width=5),
                    showlegend=False
                ))
        
        # 좌표축 추가
        axis_length = 0.5
        origin = [0, 0, 0]
        
        # X축 (빨간색) - 좌우
        fig.add_trace(go.Scatter3d(
            x=[origin[0], origin[0] + axis_length],
            y=[origin[1], origin[1]],
            z=[origin[2], origin[2]],
            mode='lines+text',
            line=dict(color='red', width=3),
            text=['', 'X'],
            showlegend=False
        ))
        
        # Y축 (초록색) - 상하
        fig.add_trace(go.Scatter3d(
            x=[origin[0], origin[0]],
            y=[origin[1], origin[1] + axis_length],
            z=[origin[2], origin[2]],
            mode='lines+text',
            line=dict(color='green', width=3),
            text=['', 'Y'],
            showlegend=False
        ))
        
        # Z축 (파란색) - 앞뒤
        fig.add_trace(go.Scatter3d(
            x=[origin[0], origin[0]],
            y=[origin[1], origin[1]],
            z=[origin[2], origin[2] + axis_length],
            mode='lines+text',
            line=dict(color='blue', width=3),
            text=['', 'Z'],
            showlegend=False
        ))
        
        # 바닥 그리드 추가 (X-Z 평면)
        grid_size = 1.0
        grid_points = np.linspace(-grid_size/2, grid_size/2, 10)
        for x in grid_points:
            fig.add_trace(go.Scatter3d(
                x=[x, x],
                y=[0, 0],
                z=[-grid_size/2, grid_size/2],
                mode='lines',
                line=dict(color='gray', width=1),
                showlegend=False
            ))
        for z in grid_points:
            fig.add_trace(go.Scatter3d(
                x=[-grid_size/2, grid_size/2],
                y=[0, 0],
                z=[z, z],
                mode='lines',
                line=dict(color='gray', width=1),
                showlegend=False
            ))
        
        # 카메라 뷰 설정 - 정면에서 바라보는 각도로 설정
        camera = dict(
            up=dict(x=0, y=1, z=0),  # Y축이 위쪽
            center=dict(x=0, y=0, z=0),
            eye=dict(x=0, y=0, z=2.0)  # 정면에서 바라보기
        )
        
        # 레이아웃 설정
        fig.update_layout(
            scene=dict(
                xaxis=dict(title='X (좌우)', range=[-1, 1]),
                yaxis=dict(title='Y (상하)', range=[0, 2]),
                zaxis=dict(title='Z (앞뒤)', range=[-1, 1]),
                aspectmode='data',
                camera=camera
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            width=800,
            height=600
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating 3D pose plot: {str(e)}")
        return go.Figure()

def show_3d_metrics(analysis_result, frame_idx):
    """3D 메트릭스 표시"""
    frame_data = analysis_result['frames'][frame_idx]
    
    # 현재 프레임의 3D 각도 계산
    angles_3d = calculate_3d_angles(frame_data['landmarks'])
    
    # 메트릭스 표시
    st.metric("척추 각도", f"{angles_3d['spine_angle']:.1f}°")
    st.metric("어깨 회전", f"{angles_3d['shoulder_rotation']:.1f}°")
    st.metric("힙 회전", f"{angles_3d['hip_rotation']:.1f}°")
    st.metric("팔 각도 (오른쪽)", f"{angles_3d['right_arm_angle']:.1f}°")
    st.metric("무릎 각도 (오른쪽)", f"{angles_3d['right_knee_angle']:.1f}°")

def calculate_3d_angles(landmarks):
    """3D 각도 계산"""
    import numpy as np
    
    def calculate_angle(p1, p2, p3):
        """세 점 사이의 3D 각도 계산"""
        v1 = np.array(p1) - np.array(p2)
        v2 = np.array(p3) - np.array(p2)
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
    
    # 척추 각도
    hip_center = np.mean([landmarks['left_hip'], landmarks['right_hip']], axis=0)
    shoulder_center = np.mean([landmarks['left_shoulder'], landmarks['right_shoulder']], axis=0)
    vertical = hip_center + np.array([0, 1, 0])
    spine_angle = calculate_angle(vertical, hip_center, shoulder_center)
    
    # 어깨 회전
    shoulder_vector = np.array(landmarks['right_shoulder']) - np.array(landmarks['left_shoulder'])
    forward = np.array([0, 0, 1])
    shoulder_rotation = np.degrees(np.arctan2(shoulder_vector[0], shoulder_vector[2]))
    
    # 힙 회전
    hip_vector = np.array(landmarks['right_hip']) - np.array(landmarks['left_hip'])
    hip_rotation = np.degrees(np.arctan2(hip_vector[0], hip_vector[2]))
    
    # 오른팔 각도
    right_arm_angle = calculate_angle(
        landmarks['right_shoulder'],
        landmarks['right_elbow'],
        landmarks['right_wrist']
    )
    
    # 오른쪽 무릎 각도
    right_knee_angle = calculate_angle(
        landmarks['right_hip'],
        landmarks['right_knee'],
        landmarks['right_ankle']
    )
    
    return {
        'spine_angle': spine_angle,
        'shoulder_rotation': shoulder_rotation,
        'hip_rotation': hip_rotation,
        'right_arm_angle': right_arm_angle,
        'right_knee_angle': right_knee_angle
    }

def show_angle_graph(analysis_result):
    """각도 그래프 표시"""
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

def show_detailed_metrics(analysis_result):
    """상세 메트릭스 표시"""
    st.subheader("상세 메트릭스")
    metrics = analysis_result['metrics']
    cols = st.columns(3)
    for idx, (metric_name, value) in enumerate(metrics.items()):
        with cols[idx % 3]:
            st.metric(
                label=metric_name,
                value=f"{value:.2f}°" if isinstance(value, (int, float)) else value
            )

def show_swing_evaluation(analysis_result):
    """스윙 평가 표시"""
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