"""Input validation utilities."""

from pathlib import Path
from typing import Optional
import cv2
import magic
from config import Config
from exceptions import ValidationError

def validate_video_file(file_path: Path) -> None:
    """Validate video file format, size, and content."""
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
    
    # Validate MIME type for security
    try:
        mime_type = magic.from_file(str(file_path), mime=True)
        if not mime_type.startswith('video/'):
            raise ValidationError(f"Invalid file type: {mime_type}")
    except Exception:
        pass  # Fall back to OpenCV validation
    
    # Check if video can be opened and has valid properties
    cap = cv2.VideoCapture(str(file_path))
    try:
        if not cap.isOpened():
            raise ValidationError("Cannot open video file")
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if frame_count <= 0:
            raise ValidationError("Video has no frames")
        
        if fps <= 0 or fps > Config.MAX_FRAME_RATE:
            raise ValidationError(f"Invalid frame rate: {fps}")
            
    finally:
        cap.release()

def validate_confidence_score(score: float) -> None:
    """Validate confidence score range."""
    if not isinstance(score, (int, float)):
        raise ValidationError(f"Confidence score must be numeric, got {type(score)}")
    
    if not 0.0 <= score <= 1.0:
        raise ValidationError(f"Confidence score must be between 0.0 and 1.0, got {score}")

def validate_uploaded_file(uploaded_file) -> None:
    """Validate Streamlit uploaded file."""
    if uploaded_file is None:
        raise ValidationError("No file uploaded")
    
    if uploaded_file.size == 0:
        raise ValidationError("Uploaded file is empty")
    
    # Check file extension from name
    file_ext = Path(uploaded_file.name).suffix.lower()
    if file_ext not in Config.SUPPORTED_VIDEO_FORMATS:
        raise ValidationError(f"Unsupported file format: {file_ext}")
