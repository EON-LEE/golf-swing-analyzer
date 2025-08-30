import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import cv2
import logging
from pose_estimation import PoseEstimator
from config import MAX_FRAMES, THRESHOLDS, KEY_FRAME_RATIOS
from utils import safe_divide, validate_video_file

logger = logging.getLogger(__name__)

class SwingAnalyzer:
    """골프 스윙을 분석하는 클래스"""

    def __init__(self):
        self.pose_estimator = PoseEstimator()

    def analyze_video(self, video_path: str) -> Dict:
        """비디오를 분석하고 결과를 반환합니다."""
        logger.info("Starting video analysis")
        
        if not validate_video_file(video_path):
            raise ValueError("Invalid video file")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("비디오를 열 수 없습니다.")
        
        try:
            frames_data = self._collect_frames(cap)
            if not frames_data:
                raise ValueError("유효한 프레임을 찾을 수 없습니다.")
            
            key_frames = self._detect_key_frames(frames_data)
            logger.info(f"Detected {len(key_frames)} key frames")
            
            analysis_result = self._analyze_swing(frames_data, key_frames)
            logger.info("Analysis completed successfully")
            
            return analysis_result
            
        finally:
            cap.release()

    def _collect_frames(self, cap) -> List[Dict]:
        """비디오에서 프레임 데이터를 수집합니다."""
        frames_data = []
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame skip ratio to limit to MAX_FRAMES
        skip_ratio = max(1, total_frames // MAX_FRAMES)
        
        while cap.isOpened() and len(frames_data) < MAX_FRAMES:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Skip frames based on ratio
            if frame_count % skip_ratio != 0:
                frame_count += 1
                continue
                
            try:
                annotated_frame, landmarks = self.pose_estimator.process_frame(frame)
                
                if landmarks:
                    angles = self.pose_estimator.calculate_angles(landmarks)
                    
                    frame_data = {
                        'frame_number': frame_count,
                        'landmarks': landmarks,
                        'angles': angles,
                        'annotated_frame': annotated_frame
                    }
                    frames_data.append(frame_data)
                    
            except Exception as e:
                logger.warning(f"Error processing frame {frame_count}: {e}")
                
            frame_count += 1
            
        logger.info(f"Collected {len(frames_data)} valid frames from {frame_count} total frames")
        return frames_data

    def _detect_key_frames(self, frames_data: List[Dict]) -> Dict[str, int]:
        """스윙의 주요 프레임을 감지합니다."""
        if not frames_data:
            return {}
            
        try:
            total_frames = len(frames_data)
            key_frames = {}
            
            for phase, ratio in KEY_FRAME_RATIOS.items():
                frame_idx = int(ratio * (total_frames - 1))
                key_frames[phase] = min(frame_idx, total_frames - 1)
                
            return key_frames
            
        except Exception as e:
            logger.error(f"Error detecting key frames: {e}")
            return {'address': 0, 'impact': len(frames_data) // 2, 'finish': len(frames_data) - 1}

    def _analyze_swing(self, frames_data: List[Dict], key_frames: Dict[str, int]) -> Dict:
        """스윙을 분석하고 결과를 반환합니다."""
        try:
            metrics = self._calculate_metrics(frames_data, key_frames)
            evaluations = self._evaluate_swing(frames_data, key_frames, metrics)
            
            return {
                'metrics': metrics,
                'evaluations': evaluations,
                'key_frames': key_frames,
                'total_frames': len(frames_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing swing: {e}")
            return {
                'metrics': {},
                'evaluations': {},
                'key_frames': key_frames,
                'total_frames': len(frames_data),
                'error': str(e)
            }

    def _calculate_metrics(self, frames_data: List[Dict], key_frames: Dict[str, int]) -> Dict:
        """스윙 메트릭을 계산합니다."""
        try:
            metrics = {}
            
            if 'impact' in key_frames and key_frames['impact'] < len(frames_data):
                impact_frame = frames_data[key_frames['impact']]
                angles = impact_frame.get('angles', {})
                
                metrics['impact_arm_angle'] = angles.get('right_arm', 0)
                metrics['impact_spine_angle'] = angles.get('spine_angle', 0)
                metrics['impact_shoulder_rotation'] = angles.get('shoulder_rotation', 0)
                
            # Calculate swing tempo
            if len(frames_data) > 1:
                metrics['swing_tempo'] = len(frames_data) / 30.0  # Assuming 30 FPS
                
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {}

    def _evaluate_swing(self, frames_data: List[Dict], key_frames: Dict[str, int], metrics: Dict) -> Dict:
        """스윙을 평가합니다."""
        try:
            evaluations = {}
            
            # Arm angle evaluation
            impact_arm_angle = metrics.get('impact_arm_angle', 0)
            if impact_arm_angle >= THRESHOLDS['arm_angle_min']:
                evaluations['arm_extension'] = 'Good'
            else:
                evaluations['arm_extension'] = 'Needs improvement'
                
            # Spine angle evaluation
            spine_angle = metrics.get('impact_spine_angle', 0)
            if spine_angle >= THRESHOLDS['spine_angle_min']:
                evaluations['posture'] = 'Good'
            else:
                evaluations['posture'] = 'Needs improvement'
                
            # Overall score
            good_count = sum(1 for eval in evaluations.values() if eval == 'Good')
            total_count = len(evaluations)
            evaluations['overall_score'] = safe_divide(good_count, total_count, 0) * 100
            
            return evaluations
            
        except Exception as e:
            logger.error(f"Error evaluating swing: {e}")
            return {'overall_score': 0}
