"""Video processing utilities for golf swing analysis."""

import cv2
import numpy as np
import logging
from typing import Optional, Tuple, List
import os
from config import VIDEO_SETTINGS

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Handles video processing operations."""
    
    def __init__(self):
        """Initialize video processor."""
        self.supported_formats = VIDEO_SETTINGS['supported_formats']
        self.target_height = VIDEO_SETTINGS['target_height']
        logger.info("VideoProcessor initialized")
    
    def validate_video(self, video_path: str) -> bool:
        """
        Validate video file format and accessibility.
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return False
            
            # Check file extension
            file_ext = os.path.splitext(video_path)[1].lower()
            if file_ext not in self.supported_formats:
                logger.error(f"Unsupported format: {file_ext}")
                return False
            
            # Try to open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Cannot open video: {video_path}")
                return False
            
            # Check if video has frames
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            if frame_count == 0:
                logger.error(f"Video has no frames: {video_path}")
                return False
            
            logger.info(f"Video validation successful: {frame_count} frames")
            return True
            
        except Exception as e:
            logger.error(f"Error validating video: {e}")
            return False
    
    def get_video_info(self, video_path: str) -> Optional[dict]:
        """
        Get video information.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video info or None if failed
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
            
            info = {
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'duration': 0
            }
            
            if info['fps'] > 0:
                info['duration'] = info['frame_count'] / info['fps']
            
            cap.release()
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    def resize_frame(self, frame: np.ndarray, target_height: Optional[int] = None) -> np.ndarray:
        """
        Resize frame while maintaining aspect ratio.
        
        Args:
            frame: Input frame
            target_height: Target height (uses default if None)
            
        Returns:
            Resized frame
        """
        try:
            if target_height is None:
                target_height = self.target_height
            
            h, w = frame.shape[:2]
            if h == target_height:
                return frame
            
            aspect_ratio = w / h
            target_width = int(target_height * aspect_ratio)
            
            resized = cv2.resize(frame, (target_width, target_height))
            return resized
            
        except Exception as e:
            logger.error(f"Error resizing frame: {e}")
            return frame
    
    def extract_frames(self, video_path: str, max_frames: Optional[int] = None) -> List[np.ndarray]:
        """
        Extract frames from video.
        
        Args:
            video_path: Path to video file
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of frames
        """
        frames = []
        cap = None
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Cannot open video: {video_path}")
                return frames
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if max_frames is None:
                max_frames = VIDEO_SETTINGS['max_frames']
            
            # Calculate skip ratio
            skip_frames = max(1, total_frames // max_frames) if max_frames < total_frames else 1
            
            frame_count = 0
            extracted_count = 0
            
            while cap.isOpened() and extracted_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % skip_frames == 0:
                    # Resize frame for efficiency
                    resized_frame = self.resize_frame(frame)
                    frames.append(resized_frame)
                    extracted_count += 1
                
                frame_count += 1
            
            logger.info(f"Extracted {len(frames)} frames from {total_frames} total frames")
            return frames
            
        except Exception as e:
            logger.error(f"Error extracting frames: {e}")
            return frames
        finally:
            if cap is not None:
                cap.release()
    
    def create_sequence_image(self, frames: List[np.ndarray], labels: Optional[List[str]] = None) -> Optional[np.ndarray]:
        """
        Create a sequence image from multiple frames.
        
        Args:
            frames: List of frames
            labels: Optional labels for each frame
            
        Returns:
            Combined sequence image or None if failed
        """
        try:
            if not frames:
                return None
            
            # Resize all frames to same height
            processed_frames = []
            for i, frame in enumerate(frames):
                resized = self.resize_frame(frame)
                
                # Add label if provided
                if labels and i < len(labels):
                    cv2.putText(resized, labels[i], (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                processed_frames.append(resized)
            
            # Combine horizontally
            sequence_image = np.hstack(processed_frames)
            return sequence_image
            
        except Exception as e:
            logger.error(f"Error creating sequence image: {e}")
            return None
