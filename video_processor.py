"""Video processing and pose estimation."""

import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from config import Config
from utils.logger import setup_logger
from utils.validators import validate_video_file, validate_confidence_score
from utils.error_handler import log_performance

logger = setup_logger(__name__)

@dataclass
class PoseFrame:
    """Single frame pose data."""
    frame_number: int
    landmarks: Optional[List[Tuple[float, float, float]]]
    confidence: float

class VideoProcessor:
    """Process golf swing videos and extract pose data."""
    
    def __init__(self, confidence: float = Config.MEDIAPIPE_CONFIDENCE):
        validate_confidence_score(confidence)
        self.confidence = confidence
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=confidence,
            min_tracking_confidence=Config.MEDIAPIPE_TRACKING_CONFIDENCE
        )
    
    @log_performance
    def process_video(self, video_path: Path) -> List[PoseFrame]:
        """Extract pose data from video."""
        validate_video_file(video_path)
        
        cap = cv2.VideoCapture(str(video_path))
        frames = []
        frame_number = 0
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(rgb_frame)
                
                landmarks = None
                confidence = 0.0
                
                if results.pose_landmarks:
                    landmarks = [
                        (lm.x, lm.y, lm.z) 
                        for lm in results.pose_landmarks.landmark
                    ]
                    confidence = np.mean([lm.visibility for lm in results.pose_landmarks.landmark])
                
                frames.append(PoseFrame(frame_number, landmarks, confidence))
                frame_number += 1
                
        finally:
            cap.release()
        
        logger.info(f"Processed {len(frames)} frames from {video_path.name}")
        return frames
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'pose'):
            self.pose.close()
