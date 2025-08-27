"""Input validation utilities."""

from pathlib import Path
from typing import Optional
import cv2
from config import Config
from exceptions import ValidationError

def validate_video_file(file_path: Path) -> None:
    """Validate video file format and size."""
    if not file_path.exists():
        raise ValidationError(f"File does not exist: {file_path}")
    
    # Check file extension
    if file_path.suffix.lower() not in Config.SUPPORTED_VIDEO_FORMATS:
        raise ValidationError(
            f"Unsupported format. Supported: {Config.SUPPORTED_VIDEO_FORMATS}"
        )
    
    # Check file size
    size_mb = file_path.stat().st_size / (1024 * 1024)
    if size_mb > Config.MAX_VIDEO_SIZE_MB:
        raise ValidationError(
            f"File too large: {size_mb:.1f}MB (max: {Config.MAX_VIDEO_SIZE_MB}MB)"
        )
    
    # Check if video can be opened
    cap = cv2.VideoCapture(str(file_path))
    if not cap.isOpened():
        cap.release()
        raise ValidationError("Cannot open video file")
    cap.release()

def validate_confidence_score(score: float) -> None:
    """Validate confidence score range."""
    if not 0.0 <= score <= 1.0:
        raise ValidationError(f"Confidence score must be between 0.0 and 1.0, got {score}")
