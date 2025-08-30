"""Configuration constants for golf swing analysis."""

# Video processing settings
MAX_FRAMES = 300
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov']

# Logging settings
LOG_LEVEL = 'INFO'
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Pose estimation thresholds
THRESHOLDS = {
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.5,
    'arm_angle_min': 165,  # degrees
    'arm_angle_max': 180,  # degrees
    'shoulder_rotation_min': 80,  # degrees
    'hip_rotation_min': 45,  # degrees
    'spine_angle_min': 30,  # degrees
    'head_movement_max': 0.1,  # normalized units
    'follow_through_max': 120,  # degrees
    'balance_knee_max': 160,  # degrees
}

# Key frame detection ratios
KEY_FRAME_RATIOS = {
    'address': 0.0,
    'backswing': 0.3,
    'top': 0.5,
    'impact': 0.7,
    'follow_through': 0.85,
    'finish': 1.0
}

# Video processing settings
VIDEO_SETTINGS = {
    'max_frames': MAX_FRAMES,
    'skip_frame_ratio': 1,
    'target_height': 480,
    'supported_formats': SUPPORTED_VIDEO_FORMATS
}

# Logging settings
LOG_SETTINGS = {
    'level': LOG_LEVEL,
    'max_bytes': LOG_MAX_BYTES,
    'backup_count': LOG_BACKUP_COUNT,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
