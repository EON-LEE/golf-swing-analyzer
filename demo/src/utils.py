"""Utility functions for golf swing analysis."""

import numpy as np
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero or inputs are None."""
    try:
        if numerator is None or denominator is None:
            return default
        if abs(denominator) < 1e-10:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default

def calculate_angle_3d(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """Calculate angle between three 3D points."""
    try:
        if p1 is None or p2 is None or p3 is None:
            return 0.0
            
        v1 = np.array(p1) - np.array(p2)
        v2 = np.array(p3) - np.array(p2)
        
        # Check for zero vectors
        norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if norm1 < 1e-10 or norm2 < 1e-10:
            return 0.0
        
        cos_angle = np.dot(v1, v2) / (norm1 * norm2)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        
        return np.degrees(np.arccos(cos_angle))
    except Exception as e:
        logger.warning(f"Error calculating 3D angle: {e}")
        return 0.0

def normalize_angle(angle: float) -> float:
    """Normalize angle to 0-360 degree range."""
    while angle < 0:
        angle += 360
    while angle >= 360:
        angle -= 360
    return angle

def format_angle(angle: float) -> str:
    """Format angle for display."""
    return f"{angle:.1f}°"

def validate_video_file(file_path: str) -> bool:
    """Validate video file format and accessibility."""
    from config import SUPPORTED_VIDEO_FORMATS
    
    if not os.path.exists(file_path):
        return False
    
    file_ext = os.path.splitext(file_path)[1].lower()
    return file_ext in SUPPORTED_VIDEO_FORMATS

def get_video_info(file_path: str) -> Dict[str, Any]:
    """Get video file information."""
    try:
        import cv2
        cap = cv2.VideoCapture(file_path)
        info = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        }
        cap.release()
        return info
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return {}

def calculate_distance_3d(p1: np.ndarray, p2: np.ndarray) -> float:
    """Calculate 3D distance between two points."""
    try:
        if p1 is None or p2 is None:
            return 0.0
        return float(np.linalg.norm(np.array(p1) - np.array(p2)))
    except Exception:
        return 0.0
