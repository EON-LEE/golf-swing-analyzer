"""Configuration management for Golf Swing Analyzer."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from exceptions import ConfigurationError

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # Environment
    ENV = os.getenv("ENV", "development")
    DEBUG = ENV == "development"
    
    # Directories
    BASE_DIR = Path(__file__).parent
    LOG_DIR = BASE_DIR / "logs"
    CACHE_DIR = BASE_DIR / "cache"
    TEMP_DIR = BASE_DIR / "temp"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG" if DEBUG else "INFO")
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # MediaPipe
    MEDIAPIPE_CONFIDENCE = float(os.getenv("MEDIAPIPE_CONFIDENCE", "0.5"))
    MEDIAPIPE_TRACKING_CONFIDENCE = float(os.getenv("MEDIAPIPE_TRACKING_CONFIDENCE", "0.5"))
    
    # Video processing
    MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", "100"))
    SUPPORTED_VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".mkv"]
    MAX_FRAME_RATE = int(os.getenv("MAX_FRAME_RATE", "30"))
    
    # Performance
    ASYNC_BATCH_SIZE = int(os.getenv("ASYNC_BATCH_SIZE", "10"))
    MAX_CONCURRENT_PROCESSES = int(os.getenv("MAX_CONCURRENT_PROCESSES", "4"))
    
    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories."""
        for dir_path in [cls.LOG_DIR, cls.CACHE_DIR, cls.TEMP_DIR]:
            dir_path.mkdir(exist_ok=True)
    
    @classmethod
    def validate_config(cls) -> None:
        """Validate configuration values."""
        if not 0.0 <= cls.MEDIAPIPE_CONFIDENCE <= 1.0:
            raise ConfigurationError("MEDIAPIPE_CONFIDENCE must be between 0.0 and 1.0")
        
        if cls.MAX_VIDEO_SIZE_MB <= 0:
            raise ConfigurationError("MAX_VIDEO_SIZE_MB must be positive")
        
        if cls.MAX_FRAME_RATE <= 0:
            raise ConfigurationError("MAX_FRAME_RATE must be positive")
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return {
            "env": cls.ENV,
            "debug": cls.DEBUG,
            "log_level": cls.LOG_LEVEL,
            "mediapipe_confidence": cls.MEDIAPIPE_CONFIDENCE,
            "max_video_size_mb": cls.MAX_VIDEO_SIZE_MB,
            "max_frame_rate": cls.MAX_FRAME_RATE,
        }
