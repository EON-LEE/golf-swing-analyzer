"""Configuration constants for golf swing analysis."""

# Video processing settings
MAX_FRAMES = 300
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov']

# Logging settings
LOG_LEVEL = 'INFO'

# Pose estimation thresholds
THRESHOLDS = {
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.5,
    'arm_angle_min': 165,
    'arm_angle_max': 180,
    'shoulder_rotation_min': 80,
    'hip_rotation_min': 45,
    'spine_angle_min': 30,
    'head_movement_max': 0.1,
    'follow_through_max': 120,
    'balance_knee_max': 160,
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
