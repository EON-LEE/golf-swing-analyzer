"""
Test suite for configuration module
"""

import pytest
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import GREETING_KEYWORDS, FAREWELL_KEYWORDS, RESPONSES, APP_CONFIG, PREVIEW_MAX_LENGTH


class TestConfiguration:
    """Test configuration values."""
    
    def test_greeting_keywords(self):
        """Test greeting keywords are properly defined."""
        assert isinstance(GREETING_KEYWORDS, list)
        assert len(GREETING_KEYWORDS) > 0
        assert "hello" in GREETING_KEYWORDS
        assert "hi" in GREETING_KEYWORDS
        assert "안녕" in GREETING_KEYWORDS
    
    def test_farewell_keywords(self):
        """Test farewell keywords are properly defined."""
        assert isinstance(FAREWELL_KEYWORDS, list)
        assert len(FAREWELL_KEYWORDS) > 0
        assert "bye" in FAREWELL_KEYWORDS
        assert "goodbye" in FAREWELL_KEYWORDS
        assert "잘가" in FAREWELL_KEYWORDS
        assert "안녕히" in FAREWELL_KEYWORDS
    
    def test_responses(self):
        """Test response messages are properly defined."""
        assert isinstance(RESPONSES, dict)
        required_keys = ["greeting", "farewell", "default"]
        
        for key in required_keys:
            assert key in RESPONSES
            assert isinstance(RESPONSES[key], str)
            assert len(RESPONSES[key]) > 0
    
    def test_app_config(self):
        """Test app configuration is properly defined."""
        assert isinstance(APP_CONFIG, dict)
        required_keys = [
            "title", "page_icon", "layout", "caption",
            "input_placeholder", "clear_button_text", "sidebar_header"
        ]
        
        for key in required_keys:
            assert key in APP_CONFIG
            assert isinstance(APP_CONFIG[key], str)
            assert len(APP_CONFIG[key]) > 0
    
    def test_preview_max_length(self):
        """Test preview max length is properly configured."""
        assert isinstance(PREVIEW_MAX_LENGTH, int)
        assert PREVIEW_MAX_LENGTH > 0


if __name__ == "__main__":
    pytest.main([__file__])
