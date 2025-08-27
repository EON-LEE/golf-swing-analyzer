"""Video processing and pose estimation."""

import asyncio
import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path
from typing import List, Dict, Optional, Tuple, AsyncGenerator
from dataclasses import dataclass
from contextlib import asynccontextmanager

from config import Config
from utils.logger import setup_logger
from utils.validators import validate_video_file, validate_confidence_score
from utils.error_handler import log_performance
from exceptions import VideoProcessingError

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
        self._pose = None
    
    @asynccontextmanager
    async def _get_pose_estimator(self):
        """Context manager for MediaPipe pose estimator."""
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            min_detection_confidence=self.confidence,
            min_tracking_confidence=Config.MEDIAPIPE_TRACKING_CONFIDENCE
        )
        try:
            yield pose
        finally:
            pose.close()
    
    @log_performance
    async def process_video(self, video_path: Path) -> List[PoseFrame]:
        """Extract pose data from video asynchronously."""
        validate_video_file(video_path)
        
        async with self._get_pose_estimator() as pose:
            return await self._process_frames(video_path, pose)
    
    async def _process_frames(self, video_path: Path, pose) -> List[PoseFrame]:
        """Process video frames."""
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise VideoProcessingError(f"Cannot open video: {video_path}")
        
        frames = []
        frame_number = 0
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                pose_frame = await self._process_single_frame(frame, frame_number, pose)
                frames.append(pose_frame)
                frame_number += 1
                
                # Yield control periodically
                if frame_number % 10 == 0:
                    await asyncio.sleep(0)
                    
        finally:
            cap.release()
        
        logger.info(f"Processed {len(frames)} frames from {video_path.name}")
        return frames
    
    async def _process_single_frame(self, frame: np.ndarray, frame_number: int, pose) -> PoseFrame:
        """Process a single frame."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        
        landmarks = None
        confidence = 0.0
        
        if results.pose_landmarks:
            landmarks = [
                (lm.x, lm.y, lm.z) 
                for lm in results.pose_landmarks.landmark
            ]
            confidence = np.mean([lm.visibility for lm in results.pose_landmarks.landmark])
        
        return PoseFrame(frame_number, landmarks, confidence)
