"""
Unit tests for hello_world_chatbot.py
"""

import unittest
from hello_world_chatbot import get_bot_response, RESPONSES


class TestChatbot(unittest.TestCase):
    """Test cases for chatbot functionality."""
    
    def test_greeting_responses(self):
        """Test greeting keyword responses."""
        test_cases = ["hello", "hi", "hey", "안녕", "안녕하세요"]
        for greeting in test_cases:
            response = get_bot_response(greeting)
            self.assertEqual(response, RESPONSES["greeting"])
    
    def test_farewell_responses(self):
        """Test farewell keyword responses."""
        test_cases = ["bye", "goodbye", "see you", "안녕히", "잘가"]
        for farewell in test_cases:
            response = get_bot_response(farewell)
            self.assertEqual(response, RESPONSES["farewell"])
    
    def test_help_responses(self):
        """Test help keyword responses."""
        test_cases = ["help", "도움", "commands", "명령어"]
        for help_word in test_cases:
            response = get_bot_response(help_word)
            self.assertEqual(response, RESPONSES["help"])
    
    def test_default_response(self):
        """Test default response for unknown input."""
        response = get_bot_response("random text")
        self.assertEqual(response, RESPONSES["default"])
    
    def test_case_insensitive(self):
        """Test case insensitive matching."""
        self.assertEqual(get_bot_response("HELLO"), RESPONSES["greeting"])
        self.assertEqual(get_bot_response("BYE"), RESPONSES["farewell"])
        self.assertEqual(get_bot_response("HELP"), RESPONSES["help"])


if __name__ == "__main__":
    unittest.main()
