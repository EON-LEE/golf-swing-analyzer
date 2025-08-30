import numpy as np
from typing import List, Dict, Optional
import cv2
from pose_estimation import PoseEstimator
import logging
from config import THRESHOLDS, KEY_FRAME_RATIOS
from utils import validate_landmarks_data, safe_divide, filter_outliers

logger = logging.getLogger(__name__)

class SwingAnalyzer:
    """골프 스윙을 분석하는 클래스"""

    def __init__(self):
        self.pose_estimator = PoseEstimator()

    def _calculate_metrics(self, frames_data: List[Dict], key_frames: Dict[str, int]) -> Dict[str, float]:
        """Calculate swing metrics from frame data."""
        try:
            if not frames_data:
                logger.warning("No frames data provided for metrics calculation")
                return {}
            
            metrics = {}
            
            # Extract angle sequences
            shoulder_angles = [frame['angles'].get('shoulder_angle', 0) for frame in frames_data]
            right_arm_angles = [frame['angles'].get('right_arm', 0) for frame in frames_data]
            hip_angles = [frame['angles'].get('hip_angle', 0) for frame in frames_data]
            
            # Filter outliers
            shoulder_angles = filter_outliers(shoulder_angles)
            right_arm_angles = filter_outliers(right_arm_angles)
            hip_angles = filter_outliers(hip_angles)
            
            # Calculate key metrics
            metrics['shoulder_rotation'] = max(shoulder_angles) - min(shoulder_angles) if shoulder_angles else 0
            metrics['impact_angle'] = right_arm_angles[key_frames.get('impact', 0)] if right_arm_angles else 0
            metrics['hip_rotation'] = max(hip_angles) - min(hip_angles) if hip_angles else 0
            
            # Head stability (calculate movement variance)
            head_positions = []
            for frame in frames_data:
                if 'landmarks' in frame and 'nose' in frame['landmarks']:
                    head_positions.append(frame['landmarks']['nose'][:2])  # x, y only
            
            if head_positions:
                head_positions = np.array(head_positions)
                metrics['head_movement'] = np.std(head_positions) if len(head_positions) > 1 else 0
            else:
                metrics['head_movement'] = 0
            
            # Swing tempo (frames between key positions)
            total_frames = len(frames_data)
            if total_frames > 0:
                backswing_frames = key_frames.get('top', 0) - key_frames.get('address', 0)
                downswing_frames = key_frames.get('impact', 0) - key_frames.get('top', 0)
                metrics['tempo_ratio'] = safe_divide(backswing_frames, downswing_frames, 1.0)
            else:
                metrics['tempo_ratio'] = 1.0
            
            logger.info(f"Calculated metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {}

    def _evaluate_swing(self, frames_data: List[Dict], key_frames: Dict[str, int], metrics: Dict[str, float]) -> Dict[str, Dict[str, bool]]:
        """Evaluate swing quality based on calculated metrics."""
        try:
            evaluations = {}
            
            # Evaluate each key frame
            for phase, frame_idx in key_frames.items():
                if frame_idx >= len(frames_data):
                    continue
                    
                frame_data = frames_data[frame_idx]
                angles = frame_data.get('angles', {})
                evaluations[phase] = {}
                
                if phase == 'address':
                    # Address position evaluation
                    right_arm = angles.get('right_arm', 0)
                    evaluations[phase]['Arm Angle Straight'] = right_arm >= THRESHOLDS['arm_angle_straight']
                    
                    spine_angle = angles.get('spine_angle', 0)
                    evaluations[phase]['Posture Stable'] = abs(spine_angle) >= THRESHOLDS['spine_angle_stable']
                
                elif phase == 'top':
                    # Top of backswing evaluation
                    shoulder_rotation = metrics.get('shoulder_rotation', 0)
                    evaluations[phase]['Shoulder Rotation Good'] = shoulder_rotation >= THRESHOLDS['shoulder_rotation_good']
                    
                    head_movement = metrics.get('head_movement', 0)
                    evaluations[phase]['Head Stable'] = head_movement <= THRESHOLDS['head_movement_stable']
                
                elif phase == 'impact':
                    # Impact position evaluation
                    right_arm = angles.get('right_arm', 0)
                    evaluations[phase]['Arm Straight'] = right_arm >= THRESHOLDS['arm_angle_straight']
                    
                    hip_rotation = metrics.get('hip_rotation', 0)
                    evaluations[phase]['Hip Rotation Good'] = hip_rotation >= THRESHOLDS['hip_rotation_good']
                
                elif phase in ['follow_through', 'finish']:
                    # Follow through and finish evaluation
                    right_arm = angles.get('right_arm', 0)
                    evaluations[phase]['Follow Through Complete'] = right_arm <= THRESHOLDS['follow_through_complete']
                    
                    right_knee = angles.get('right_knee_angle', 0)
                    evaluations[phase]['Balance Maintained'] = right_knee <= THRESHOLDS['balance_maintained']
            
            logger.info(f"Swing evaluations completed: {evaluations}")
            return evaluations
            
        except Exception as e:
            logger.error(f"Error evaluating swing: {e}")
            return {}

    def analyze_video(self, video_path: str) -> Dict:
        """비디오를 분석하고 결과를 반환합니다."""
        logger.info("Starting video analysis")
        
        cap = None
        try:
            # 비디오 캡처 초기화
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError("비디오를 열 수 없습니다.")
            
            # 프레임 데이터 수집
            frames_data = self._collect_frames(cap)
            if not frames_data:
                raise ValueError("유효한 프레임을 찾을 수 없습니다.")
            
            # 키 프레임 감지
            key_frames = self._detect_key_frames(frames_data)
            logger.debug(f"Detected key frames: {key_frames}")
            
            # 메트릭스 계산
            metrics = self._calculate_metrics(frames_data, key_frames)
            
            # 스윙 평가
            evaluations = self._evaluate_swing(frames_data, key_frames, metrics)
            
            return {
                "message": "분석이 완료되었습니다.",
                "frames": frames_data,
                "metrics": metrics,
                "key_frames": key_frames,
                "evaluations": evaluations
            }
            
        except Exception as e:
            logger.error(f"Error in video analysis: {e}")
            raise
        finally:
            if cap is not None:
                cap.release()

    def _collect_frames(self, cap) -> List[Dict]:
        """비디오에서 프레임 데이터를 수집합니다."""
        frames_data = []
        frame_count = 0
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                processed_frame, landmarks = self.pose_estimator.process_frame(frame)
                
                if landmarks:
                    angles = self.pose_estimator.calculate_angles(landmarks)
                    
                    # Convert landmarks to serializable format
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
                        'nose': landmarks.nose.tolist()
                    }
                    
                    frames_data.append({
                        'frame_number': frame_count,
                        'angles': angles,
                        'landmarks': landmarks_data
                    })
                
                frame_count += 1
                
        except Exception as e:
            logger.error(f"Error collecting frames: {e}")
        
        logger.info(f"Collected {len(frames_data)} valid frames from {frame_count} total frames")
        return frames_data

    def _detect_key_frames(self, frames_data: List[Dict]) -> Dict[str, int]:
        """키 프레임을 감지합니다."""
        try:
            total_frames = len(frames_data)
            if total_frames == 0:
                return {}
            
            # Simple ratio-based key frame detection
            key_frames = {}
            for phase, ratio in KEY_FRAME_RATIOS.items():
                frame_idx = min(int(total_frames * ratio), total_frames - 1)
                key_frames[phase] = frame_idx
            
            logger.debug(f"Detected key frames: {key_frames}")
            return key_frames
            
        except Exception as e:
            logger.error(f"Error detecting key frames: {e}")
            return {}
        return frames_data

    def _detect_key_frames(self, frames_data: List[Dict]) -> Dict[str, int]:
        """주요 스윙 단계의 프레임을 감지합니다."""
        if not frames_data:
            return {}
            
        # 기본값 설정
        key_frames = {
            'address': None,
            'backswing': None,
            'top': None,
            'impact': None,
            'follow_through': None,
            'finish': None
        }
        
        # 어드레스 프레임 감지
        address_frame = self._detect_address_frame(frames_data)
        key_frames['address'] = address_frame if address_frame is not None else 0
        
        # 각도 변화를 기반으로 키 프레임 감지
        max_shoulder_rotation = 0
        min_arm_angle = float('inf')
        
        for i, frame in enumerate(frames_data):
            if i < key_frames['address']:  # 어드레스 이전 프레임은 무시
                continue
                
            angles = frame['angles']
            shoulder_angle = angles.get('shoulder_angle', 0)
            arm_angle = angles.get('right_arm', 0)
            
            # 백스윙 감지 (어깨 회전 증가)
            if shoulder_angle > max_shoulder_rotation:
                max_shoulder_rotation = shoulder_angle
                key_frames['backswing'] = i
            
            # 탑 감지 (팔 각도 최소)
            if arm_angle < min_arm_angle:
                min_arm_angle = arm_angle
                key_frames['top'] = i
        
        # 나머지 키 프레임 설정
        if key_frames['top'] is not None:
            remaining_frames = len(frames_data) - key_frames['top']
            key_frames['impact'] = key_frames['top'] + (remaining_frames // 3)
            key_frames['follow_through'] = key_frames['impact'] + (remaining_frames // 3)
            key_frames['finish'] = len(frames_data) - 1
        
        return key_frames

    def _detect_address_frame(self, frames_data: List[Dict]) -> Optional[int]:
        """어드레스 프레임을 감지합니다."""
        STABLE_FRAMES_REQUIRED = 5  # 안정된 자세로 판단하기 위한 연속 프레임 수
        ANGLE_THRESHOLD = 5  # 각도 변화 허용 범위 (도)
        POSITION_THRESHOLD = 0.05  # 위치 변화 허용 범위
        
        stable_frame_count = 0
        last_angles = None
        last_positions = None
        
        for i, frame in enumerate(frames_data):
            current_angles = frame['angles']
            current_positions = {
                'right_shoulder': np.array(frame['landmarks']['right_shoulder']),
                'left_shoulder': np.array(frame['landmarks']['left_shoulder']),
                'right_hip': np.array(frame['landmarks']['right_hip']),
                'left_hip': np.array(frame['landmarks']['left_hip'])
            }
            
            # 첫 프레임이면 기준값으로 설정
            if last_angles is None:
                last_angles = current_angles
                last_positions = current_positions
                continue
            
            # 자세 안정성 체크
            is_stable = True
            
            # 각도 안정성 체크
            for angle_key in ['right_arm', 'left_arm', 'spine_angle']:
                if abs(current_angles.get(angle_key, 0) - last_angles.get(angle_key, 0)) > ANGLE_THRESHOLD:
                    is_stable = False
                    break
            
            # 위치 안정성 체크
            if is_stable:
                for pos_key in current_positions:
                    if np.linalg.norm(current_positions[pos_key] - last_positions[pos_key]) > POSITION_THRESHOLD:
                        is_stable = False
                        break
            
            # 어드레스 조건 체크
            if is_stable:
                right_arm_angle = current_angles.get('right_arm', 0)
                spine_angle = current_angles.get('spine_angle', 0)
                
                # 어드레스 자세 조건
                if (160 <= right_arm_angle <= 180 and  # 팔이 거의 펴진 상태
                    20 <= spine_angle <= 45):          # 적절한 척추 각도
                    stable_frame_count += 1
                else:
                    stable_frame_count = 0
            else:
                stable_frame_count = 0
            
            # 충분한 시간 동안 안정된 자세가 유지되면 어드레스로 판단
            if stable_frame_count >= STABLE_FRAMES_REQUIRED:
                return i - STABLE_FRAMES_REQUIRED + 1
            
            last_angles = current_angles
            last_positions = current_positions
        
        return None  # 어드레스 프레임을 찾지 못한 경우

    def _analyze_swing(self, frames_data: List[Dict], key_frames: Dict[str, int]) -> Dict:
        """스윙을 분석하고 메트릭스와 평가를 생성합니다."""
        # 메트릭스 계산
        metrics = self._calculate_metrics(frames_data, key_frames)
        
        # 평가 생성
        evaluations = self._evaluate_swing(frames_data, key_frames, metrics)
        
        return {
            'frames': frames_data,
            'key_frames': key_frames,
            'metrics': metrics,
            'evaluations': evaluations
        }

    def _calculate_metrics(self, frames_data: List[Dict], key_frames: Dict[str, int]) -> Dict[str, float]:
        """Calculate swing metrics efficiently."""
        if not frames_data:
            logger.warning("No frames data available for metrics calculation")
            return self._get_default_metrics()
            
        metrics = self._get_default_metrics()
        
        try:
            # Calculate rotation metrics
            shoulder_angles = [frame['angles'].get('shoulder_angle', 0) for frame in frames_data]
            hip_angles = [frame['angles'].get('hip_angle', 0) for frame in frames_data]
            
            metrics['shoulder_rotation'] = max(shoulder_angles) if shoulder_angles else 0.0
            metrics['hip_rotation'] = max(hip_angles) if hip_angles else 0.0
            
            # Calculate head movement
            metrics['head_movement'] = self._calculate_head_movement(frames_data)
            
            # Calculate key frame angles
            for phase, frame_idx in key_frames.items():
                if frame_idx is not None and 0 <= frame_idx < len(frames_data):
                    angle = frames_data[frame_idx]['angles'].get('right_arm', 0)
                    if phase == 'top':
                        metrics['backswing_angle'] = angle
                    elif phase == 'impact':
                        metrics['impact_angle'] = angle
                    elif phase == 'finish':
                        metrics['follow_through_angle'] = angle
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return metrics
    
    def _get_default_metrics(self) -> Dict[str, float]:
        """Get default metrics dictionary."""
        return {
            'shoulder_rotation': 0.0,
            'hip_rotation': 0.0,
            'head_movement': 0.0,
            'backswing_angle': 0.0,
            'impact_angle': 0.0,
            'follow_through_angle': 0.0
        }
    
    def _calculate_head_movement(self, frames_data: List[Dict]) -> float:
        """Calculate maximum head movement during swing."""
        try:
            if not frames_data or 'landmarks' not in frames_data[0]:
                return 0.0
                
            initial_nose = frames_data[0]['landmarks'].get('nose')
            if initial_nose is None:
                return 0.0
                
            initial_pos = np.array(initial_nose)
            max_movement = 0.0
            
            for frame in frames_data[1:]:
                nose_pos = frame['landmarks'].get('nose')
                if nose_pos is not None:
                    current_pos = np.array(nose_pos)
                    movement = np.linalg.norm(current_pos - initial_pos)
                    max_movement = max(max_movement, movement)
            
            return float(max_movement)
            
        except Exception as e:
            logger.error(f"Error calculating head movement: {str(e)}")
            return 0.0

    def _evaluate_swing(self, frames_data: List[Dict], key_frames: Dict[str, int], metrics: Dict[str, float]) -> Dict[str, Dict[str, bool]]:
        """Evaluate swing performance using configuration thresholds."""
        evaluations = {}
        
        try:
            # Address evaluation
            if self._is_valid_frame_index('address', key_frames, frames_data):
                address_frame = frames_data[key_frames['address']]
                evaluations['address'] = {
                    'Arm Angle Straight': self._check_arm_angle(
                        address_frame, 
                        THRESHOLDS['arm_angle_min'], 
                        THRESHOLDS['arm_angle_max']
                    ),
                    'Posture Stable': self._check_spine_angle(
                        address_frame, 
                        THRESHOLDS['spine_angle_min']
                    )
                }
            
            # Top evaluation
            if self._is_valid_frame_index('top', key_frames, frames_data):
                evaluations['top'] = {
                    'Shoulder Rotation Good': metrics.get('shoulder_rotation', 0) >= THRESHOLDS['shoulder_rotation_min'],
                    'Head Stable': metrics.get('head_movement', 0) <= THRESHOLDS['head_movement_max']
                }
            
            # Impact evaluation
            if self._is_valid_frame_index('impact', key_frames, frames_data):
                impact_frame = frames_data[key_frames['impact']]
                evaluations['impact'] = {
                    'Arm Straight': self._check_arm_angle(
                        impact_frame, 
                        THRESHOLDS['arm_angle_min'], 
                        THRESHOLDS['arm_angle_max']
                    ),
                    'Hip Rotation Good': metrics.get('hip_rotation', 0) >= THRESHOLDS['hip_rotation_min']
                }
            
            # Follow through evaluation
            if self._is_valid_frame_index('follow_through', key_frames, frames_data):
                follow_frame = frames_data[key_frames['follow_through']]
                evaluations['follow_through'] = {
                    'Follow Through Complete': follow_frame['angles'].get('right_arm', 0) <= THRESHOLDS['follow_through_max'],
                    'Balance Maintained': follow_frame['angles'].get('right_knee_angle', 0) <= THRESHOLDS['balance_knee_max']
                }
            
            # Finish evaluation
            if self._is_valid_frame_index('finish', key_frames, frames_data):
                finish_frame = frames_data[key_frames['finish']]
                evaluations['finish'] = {
                    'Follow Through Complete': finish_frame['angles'].get('right_arm', 0) <= THRESHOLDS['follow_through_max'],
                    'Balance Maintained': finish_frame['angles'].get('right_knee_angle', 0) <= THRESHOLDS['balance_knee_max']
                }
            
            return evaluations
            
        except Exception as e:
            logger.error(f"Error evaluating swing: {str(e)}")
            return {}
    
    def _is_valid_frame_index(self, phase: str, key_frames: Dict[str, int], frames_data: List[Dict]) -> bool:
        """Check if frame index is valid."""
        frame_idx = key_frames.get(phase)
        return frame_idx is not None and 0 <= frame_idx < len(frames_data)
    
    def _check_arm_angle(self, frame: Dict, min_angle: float, max_angle: float) -> bool:
        """Check if arm angle is within range."""
        arm_angle = frame['angles'].get('right_arm', 0)
        return min_angle <= arm_angle <= max_angle
    
    def _check_spine_angle(self, frame: Dict, min_angle: float) -> bool:
        """Check if spine angle meets minimum requirement."""
        spine_angle = frame['angles'].get('spine_angle', 0)
        return spine_angle >= min_angle

    def _landmarks_to_dict(self, landmarks) -> Dict[str, List[float]]:
        """랜드마크를 딕셔너리로 변환합니다."""
        return {
            'nose': landmarks.nose.tolist() if hasattr(landmarks, 'nose') else None,
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
            'right_ankle': landmarks.right_ankle.tolist()
        } 