"""Custom exceptions for Golf Swing Analyzer."""

class GolfAnalyzerError(Exception):
    """Base exception for golf analyzer."""
    pass

class VideoProcessingError(GolfAnalyzerError):
    """Video processing related errors."""
    pass

class PoseEstimationError(GolfAnalyzerError):
    """Pose estimation related errors."""
    pass

class ConfigurationError(GolfAnalyzerError):
    """Configuration related errors."""
    pass
