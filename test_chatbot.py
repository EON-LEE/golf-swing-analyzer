"""
Test suite for Hello World Chatbot
"""

import pytest
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from hello_world_chatbot import get_bot_response


class TestBotResponse:
    """Test bot response generation."""
    
    def test_hello_responses(self):
        """Test greeting responses."""
        test_cases = [
            ("hello", "Hello World! 안녕하세요!"),
            ("Hello", "Hello World! 안녕하세요!"),
            ("hi", "Hello World! 안녕하세요!"),
            ("안녕", "Hello World! 안녕하세요!"),
            ("Hello there", "Hello World! 안녕하세요!"),
        ]
        
        for input_msg, expected in test_cases:
            assert get_bot_response(input_msg) == expected
    
    def test_goodbye_responses(self):
        """Test farewell responses."""
        test_cases = [
            ("bye", "Goodbye! 안녕히 가세요!"),
            ("Bye", "Goodbye! 안녕히 가세요!"),
            ("goodbye", "Goodbye! 안녕히 가세요!"),
            ("잘가", "Goodbye! 안녕히 가세요!"),
            ("안녕히", "Goodbye! 안녕히 가세요!"),
        ]
        
        for input_msg, expected in test_cases:
            assert get_bot_response(input_msg) == expected
    
    def test_default_response(self):
        """Test default response for unknown inputs."""
        test_cases = [
            "how are you",
            "what's up",
            "random text",
            "123456",
            "!@#$%",
            "",
            "   ",
        ]
        
        expected = "죄송해요, 이해하지 못했어요."
        for input_msg in test_cases:
            assert get_bot_response(input_msg) == expected
    
    def test_input_normalization(self):
        """Test input normalization (whitespace, case)."""
        test_cases = [
            ("  hello  ", "Hello World! 안녕하세요!"),
            ("HELLO", "Hello World! 안녕하세요!"),
            ("  BYE  ", "Goodbye! 안녕히 가세요!"),
        ]
        
        for input_msg, expected in test_cases:
            assert get_bot_response(input_msg) == expected


class TestIntegration:
    """Integration tests."""
    
    def test_response_consistency(self):
        """Test that responses are consistent across multiple calls."""
        test_input = "hello"
        expected = "Hello World! 안녕하세요!"
        
        # Call multiple times
        for _ in range(5):
            assert get_bot_response(test_input) == expected
    
    def test_all_response_types(self):
        """Test that all response types are strings."""
        test_inputs = ["hello", "bye", "unknown", "", "   "]
        
        for input_msg in test_inputs:
            response = get_bot_response(input_msg)
            assert isinstance(response, str)
            assert len(response) > 0
    
    def test_edge_cases(self):
        """Test edge cases and special characters."""
        test_cases = [
            ("hello!", "Hello World! 안녕하세요!"),
            ("BYE!!!", "Goodbye! 안녕히 가세요!"),
            ("안녕하세요", "Hello World! 안녕하세요!"),
            ("안녕히 가세요", "Goodbye! 안녕히 가세요!"),
        ]
        
        for input_msg, expected in test_cases:
            assert get_bot_response(input_msg) == expected


if __name__ == "__main__":
    pytest.main([__file__])
