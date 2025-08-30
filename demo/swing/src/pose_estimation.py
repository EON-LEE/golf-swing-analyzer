import cv2
import mediapipe as mp
import numpy as np
import logging
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
from utils import calculate_angle_3d, validate_landmarks_data

logger = logging.getLogger(__name__)

@dataclass
class PoseLandmarks:
    """Data class for storing pose landmarks."""
    left_shoulder: np.ndarray
    right_shoulder: np.ndarray
    left_elbow: np.ndarray
    right_elbow: np.ndarray
    left_wrist: np.ndarray
    right_wrist: np.ndarray
    left_hip: np.ndarray
    right_hip: np.ndarray
    left_knee: np.ndarray
    right_knee: np.ndarray
    left_ankle: np.ndarray
    right_ankle: np.ndarray
    nose: np.ndarray

class PoseEstimator:
    """Handles pose estimation using MediaPipe."""
    
    def __init__(self, 
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        try:
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence
            )
            self.mp_drawing = mp.solutions.drawing_utils
            logger.info("PoseEstimator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PoseEstimator: {e}")
            raise
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[PoseLandmarks]]:
        """Process a single frame and return annotated frame with landmarks."""
        if frame is None or frame.size == 0:
            logger.warning("Empty frame received")
            return frame, None
            
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            annotated_frame = frame.copy()
            landmarks = None
            
            if results.pose_landmarks:
                # Draw landmarks
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS
                )
                
                # Extract landmarks
                landmarks = self._extract_landmarks(results.pose_landmarks, frame.shape)
                
            return annotated_frame, landmarks
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return frame, None
    
    def _extract_landmarks(self, pose_landmarks, frame_shape) -> Optional[PoseLandmarks]:
        """Extract key landmarks from MediaPipe results."""
        try:
            h, w = frame_shape[:2]
            
            # MediaPipe landmark indices
            landmark_indices = {
                'nose': 0,
                'left_shoulder': 11,
                'right_shoulder': 12,
                'left_elbow': 13,
                'right_elbow': 14,
                'left_wrist': 15,
                'right_wrist': 16,
                'left_hip': 23,
                'right_hip': 24,
                'left_knee': 25,
                'right_knee': 26,
                'left_ankle': 27,
                'right_ankle': 28
            }
            
            landmarks_dict = {}
            for name, idx in landmark_indices.items():
                if idx < len(pose_landmarks.landmark):
                    landmark = pose_landmarks.landmark[idx]
                    landmarks_dict[name] = np.array([
                        landmark.x * w,
                        landmark.y * h,
                        landmark.z
                    ], dtype=np.float32)
                else:
                    landmarks_dict[name] = np.array([0.0, 0.0, 0.0], dtype=np.float32)
            
            # Validate extracted landmarks
            if not validate_landmarks_data(landmarks_dict):
                logger.warning("Invalid landmarks data")
                return None
            
            return PoseLandmarks(**landmarks_dict)
            
        except Exception as e:
            logger.error(f"Error extracting landmarks: {e}")
            return None
    
    def calculate_angles(self, landmarks: PoseLandmarks) -> Dict[str, float]:
        """Calculate various angles from pose landmarks."""
        if landmarks is None:
            return {}
            
        try:
            angles = {}
            
            # Arm angles
            angles['right_arm'] = self._calculate_angle(
                landmarks.right_shoulder,
                landmarks.right_elbow,
                landmarks.right_wrist
            )
            
            angles['left_arm'] = self._calculate_angle(
                landmarks.left_shoulder,
                landmarks.left_elbow,
                landmarks.left_wrist
            )
            
            # Knee angles
            angles['right_knee_angle'] = self._calculate_angle(
                landmarks.right_hip,
                landmarks.right_knee,
                landmarks.right_ankle
            )
            
            angles['left_knee_angle'] = self._calculate_angle(
                landmarks.left_hip,
                landmarks.left_knee,
                landmarks.left_ankle
            )
            
            # Shoulder and hip rotation
            angles['shoulder_angle'] = self._calculate_shoulder_rotation(landmarks)
            angles['hip_angle'] = self._calculate_hip_rotation(landmarks)
            
            # Spine angle
            angles['spine_angle'] = self._calculate_spine_angle(landmarks)
            
            return angles
            
        except Exception as e:
            logger.error(f"Error calculating angles: {e}")
            return {}
    
    def _calculate_angle(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Calculate angle between three points."""
        try:
            if np.allclose(p1, 0) or np.allclose(p2, 0) or np.allclose(p3, 0):
                return 0.0
                
            v1 = p1 - p2
            v2 = p3 - p2
            
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = np.arccos(cos_angle)
            
            return float(np.degrees(angle))
        except Exception:
            return 0.0
    
    def _calculate_shoulder_rotation(self, landmarks: PoseLandmarks) -> float:
        """Calculate shoulder rotation angle."""
        try:
            shoulder_vector = landmarks.right_shoulder - landmarks.left_shoulder
            return float(np.degrees(np.arctan2(shoulder_vector[1], shoulder_vector[0])))
        except Exception:
            return 0.0
    
    def _calculate_hip_rotation(self, landmarks: PoseLandmarks) -> float:
        """Calculate hip rotation angle."""
        try:
            hip_vector = landmarks.right_hip - landmarks.left_hip
            return float(np.degrees(np.arctan2(hip_vector[1], hip_vector[0])))
        except Exception:
            return 0.0
    
    def _calculate_spine_angle(self, landmarks: PoseLandmarks) -> float:
        """Calculate spine angle."""
        try:
            hip_center = (landmarks.left_hip + landmarks.right_hip) / 2
            shoulder_center = (landmarks.left_shoulder + landmarks.right_shoulder) / 2
            spine_vector = shoulder_center - hip_center
            return float(np.degrees(np.arctan2(spine_vector[0], spine_vector[1])))
        except Exception:
            return 0.0
    
    def __del__(self):
        """Clean up resources."""
        try:
            if hasattr(self, 'pose'):
                self.pose.close()
        except Exception as e:
            logger.error(f"Error closing pose estimator: {e}")
