"""Utility functions for golf swing analysis."""

import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def validate_landmarks_data(landmarks_data: Dict[str, Any]) -> bool:
    """Validate landmarks data structure."""
    required_landmarks = [
        'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
        'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
        'left_knee', 'right_knee', 'left_ankle', 'right_ankle', 'nose'
    ]
    
    for landmark in required_landmarks:
        if landmark not in landmarks_data:
            logger.warning(f"Missing landmark: {landmark}")
            return False
        
        if not isinstance(landmarks_data[landmark], (list, np.ndarray)):
            logger.warning(f"Invalid landmark format: {landmark}")
            return False
            
        if len(landmarks_data[landmark]) != 3:
            logger.warning(f"Invalid landmark dimensions: {landmark}")
            return False
    
    return True

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if abs(denominator) < 1e-10:
        return default
    return numerator / denominator

def calculate_angle_3d(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """Calculate angle between three 3D points."""
    try:
        v1 = np.array(p1) - np.array(p2)
        v2 = np.array(p3) - np.array(p2)
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        
        return np.degrees(np.arccos(cos_angle))
    except Exception as e:
        logger.warning(f"Error calculating 3D angle: {e}")
        return 0.0

def normalize_coordinates(landmarks: Dict[str, list]) -> Dict[str, list]:
    """Normalize landmark coordinates to [0, 1] range."""
    normalized = {}
    
    # Find bounds
    all_x = [point[0] for point in landmarks.values()]
    all_y = [point[1] for point in landmarks.values()]
    
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Normalize
    for name, point in landmarks.items():
        normalized[name] = [
            safe_divide(point[0] - min_x, max_x - min_x),
            safe_divide(point[1] - min_y, max_y - min_y),
            point[2] if len(point) > 2 else 0.0
        ]
    
    return normalized

def filter_outliers(values: list, threshold: float = 2.0) -> list:
    """Remove outliers from a list of values using z-score."""
    if len(values) < 3:
        return values
    
    mean_val = np.mean(values)
    std_val = np.std(values)
    
    if std_val == 0:
        return values
    
    filtered = []
    for val in values:
        z_score = abs((val - mean_val) / std_val)
        if z_score <= threshold:
            filtered.append(val)
    
    return filtered if filtered else values

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
    import os
    from config import SUPPORTED_VIDEO_FORMATS
    
    if not os.path.exists(file_path):
        return False
    
    file_ext = os.path.splitext(file_path)[1].lower()
    return file_ext in SUPPORTED_VIDEO_FORMATS

def get_video_info(file_path: str) -> Dict[str, Any]:
    """Get video file information."""
    import cv2
    
    try:
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

def cleanup_temp_files(temp_dir: str) -> None:
    """Clean up temporary files."""
    import os
    import shutil
    
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")
    except Exception as e:
        logger.error(f"Error cleaning up temp files: {e}")

def calculate_distance_3d(p1: np.ndarray, p2: np.ndarray) -> float:
    """Calculate 3D distance between two points."""
    try:
        return float(np.linalg.norm(np.array(p1) - np.array(p2)))
    except Exception:
        return 0.0
