"""Tests for video processor module."""

import pytest
from pathlib import Path
from video_processor import VideoProcessor
from utils.validators import ValidationError

class TestVideoProcessor:
    """Test video processing functionality."""
    
    def test_init_with_valid_confidence(self):
        """Test initialization with valid confidence."""
        processor = VideoProcessor(confidence=0.7)
        assert processor.confidence == 0.7
    
    def test_init_with_invalid_confidence(self):
        """Test initialization with invalid confidence."""
        with pytest.raises(ValidationError):
            VideoProcessor(confidence=1.5)
    
    def test_process_nonexistent_file(self):
        """Test processing non-existent file."""
        processor = VideoProcessor()
        fake_path = Path("nonexistent.mp4")
        
        with pytest.raises(ValidationError):
            processor.process_video(fake_path)
