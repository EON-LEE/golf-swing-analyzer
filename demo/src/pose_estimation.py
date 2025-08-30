import cv2
import mediapipe as mp
import numpy as np
import logging
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
from config import THRESHOLDS
from utils import calculate_angle_3d

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
                 min_detection_confidence: float = None,
                 min_tracking_confidence: float = None):
        if min_detection_confidence is None:
            min_detection_confidence = THRESHOLDS['min_detection_confidence']
        if min_tracking_confidence is None:
            min_tracking_confidence = THRESHOLDS['min_tracking_confidence']
            
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[PoseLandmarks]]:
        """Process a single frame and return annotated frame with landmarks."""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            annotated_frame = frame.copy()
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS
                )
                
                try:
                    landmarks = self._extract_landmarks(results.pose_landmarks)
                    return annotated_frame, landmarks
                except Exception as e:
                    logger.error(f"Error extracting landmarks: {e}")
                    return annotated_frame, None
            else:
                return annotated_frame, None
                
        except Exception as e:
            logger.error(f"Error in process_frame: {e}")
            return frame, None
    
    def _extract_landmarks(self, landmarks) -> PoseLandmarks:
        """Extract relevant landmarks from MediaPipe results."""
        try:
            return PoseLandmarks(
                left_shoulder=self._get_landmark_coords(landmarks, self.mp_pose.PoseLandmark.LEFT_SHOULDER),
                right_shoulder=self._get_landmark_coords(landmarks, self.mp_pose.PoseLandmark.RIGHT_SHOULDER),
                left_elbow=self._get_landmark_coords(landmarks, self.mp_pose.PoseLandmark.LEFT_ELBOW),
                right_elbow=self._get_landmark_coords(landmarks, self.mp_pose.PoseLandmark.RIGHT_ELBOW),
                left_wrist=self._get_landmark_coords(landmarks, self.mp_pose.PoseLandmark.LEFT_WRIST),
                right_wrist=self._get_landmark_coords(landmarks, self.mp_pose.PoseLandmark.RIGHT_WRIST),
                left_hip=self._get_landmark_coords(landmarks, self.mp_pose.PoseLandmark.LEFT_HIP),
                right_hip=self._get_landmark_coords(landmarks, self.mp_pose.PoseLandmark.RIGHT_HIP),
                left_knee=self._get_landmark_coords(landmarks, self.mp_pose.PoseLandmark.LEFT_KNEE),
                right_knee=self._get_landmark_coords(landmarks, self.mp_pose.PoseLandmark.RIGHT_KNEE),
                left_ankle=self._get_landmark_coords(landmarks, self.mp_pose.PoseLandmark.LEFT_ANKLE),
                right_ankle=self._get_landmark_coords(landmarks, self.mp_pose.PoseLandmark.RIGHT_ANKLE),
                nose=self._get_landmark_coords(landmarks, self.mp_pose.PoseLandmark.NOSE)
            )
        except Exception as e:
            logger.error(f"Error in _extract_landmarks: {e}")
            zero_array = np.array([0.0, 0.0, 0.0])
            return PoseLandmarks(
                left_shoulder=zero_array, right_shoulder=zero_array,
                left_elbow=zero_array, right_elbow=zero_array,
                left_wrist=zero_array, right_wrist=zero_array,
                left_hip=zero_array, right_hip=zero_array,
                left_knee=zero_array, right_knee=zero_array,
                left_ankle=zero_array, right_ankle=zero_array,
                nose=zero_array
            )
    
    def _get_landmark_coords(self, landmarks, landmark_idx) -> np.ndarray:
        """Get coordinates of a specific landmark."""
        try:
            landmark = landmarks.landmark[landmark_idx]
            if hasattr(landmark, 'x') and hasattr(landmark, 'y') and hasattr(landmark, 'z'):
                return np.array([landmark.x, landmark.y, landmark.z], dtype=np.float32)
            elif hasattr(landmark, '__getitem__'):
                return np.array([landmark[0], landmark[1], landmark[2]], dtype=np.float32)
            else:
                return np.array([0.0, 0.0, 0.0], dtype=np.float32)
        except Exception as e:
            logger.warning(f"Error getting landmark coordinates: {e}")
            return np.array([0.0, 0.0, 0.0], dtype=np.float32)

    def calculate_angles(self, landmarks: PoseLandmarks) -> Dict[str, float]:
        """Calculate various angles from pose landmarks."""
        try:
            angles = {}
            
            # Arm angles
            angles['left_arm'] = calculate_angle_3d(
                landmarks.left_shoulder, landmarks.left_elbow, landmarks.left_wrist
            )
            angles['right_arm'] = calculate_angle_3d(
                landmarks.right_shoulder, landmarks.right_elbow, landmarks.right_wrist
            )
            
            # Spine angle (using hip and shoulder centers)
            hip_center = (landmarks.left_hip + landmarks.right_hip) / 2
            shoulder_center = (landmarks.left_shoulder + landmarks.right_shoulder) / 2
            vertical_ref = hip_center + np.array([0, -1, 0])
            
            angles['spine_angle'] = calculate_angle_3d(
                vertical_ref, hip_center, shoulder_center
            )
            
            # Shoulder rotation
            angles['shoulder_rotation'] = calculate_angle_3d(
                landmarks.left_shoulder, shoulder_center, landmarks.right_shoulder
            )
            
            # Hip rotation
            angles['hip_rotation'] = calculate_angle_3d(
                landmarks.left_hip, hip_center, landmarks.right_hip
            )
            
            return angles
            
        except Exception as e:
            logger.error(f"Error calculating angles: {e}")
            return {
                'left_arm': 0.0,
                'right_arm': 0.0,
                'spine_angle': 0.0,
                'shoulder_rotation': 0.0,
                'hip_rotation': 0.0
            }
