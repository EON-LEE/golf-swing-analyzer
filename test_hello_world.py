#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test module for Hello World functionality
Comprehensive test suite with proper setup and teardown
"""

import unittest
import logging
from io import StringIO
from unittest.mock import patch, MagicMock
from hello_world import hello_world, main


class TestHelloWorld(unittest.TestCase):
    """Test cases for hello_world function"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.log_capture = StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        self.logger = logging.getLogger('hello_world')
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)
        # Store original handlers to restore later
        self.original_handlers = self.logger.handlers[:]

    def tearDown(self):
        """Clean up after each test method."""
        self.logger.removeHandler(self.handler)
        self.log_capture.close()

    def test_hello_world_output(self):
        """Test that hello_world logs correct messages"""
        hello_world()
        log_output = self.log_capture.getvalue()
        
        # Verify both English and Korean messages are logged
        self.assertIn("Hello World", log_output)
        self.assertIn("안녕하세요, 세계!", log_output)
        self.assertIn("successfully", log_output)

    def test_hello_world_no_exception(self):
        """Test that hello_world executes without exceptions"""
        try:
            hello_world()
        except Exception as e:
            self.fail(f"hello_world() raised {type(e).__name__} unexpectedly: {e}")

    def test_hello_world_return_type(self):
        """Test that hello_world returns None"""
        result = hello_world()
        self.assertIsNone(result)

    @patch('hello_world.logger')
    def test_hello_world_logging_calls(self, mock_logger):
        """Test that hello_world makes expected logging calls"""
        hello_world()
        
        # Verify logger.info was called 3 times
        self.assertEqual(mock_logger.info.call_count, 3)
        
        # Verify specific log messages
        expected_calls = [
            "Hello World",
            "안녕하세요, 세계!",
            "Hello World message displayed successfully"
        ]
        
        actual_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        self.assertEqual(actual_calls, expected_calls)

    @patch('hello_world.logger')
    def test_hello_world_exception_handling(self, mock_logger):
        """Test exception handling in hello_world"""
        # Make logger.info raise an exception
        mock_logger.info.side_effect = Exception("Test exception")
        
        with self.assertRaises(RuntimeError) as context:
            hello_world()
        
        # Verify error message contains original exception
        self.assertIn("Test exception", str(context.exception))
        mock_logger.error.assert_called_once()

    def test_main_function_success(self):
        """Test main function executes successfully"""
        with patch('hello_world.hello_world') as mock_hello:
            main()  # Should not raise SystemExit on success
            mock_hello.assert_called_once()

    def test_main_function_error_handling(self):
        """Test main function handles errors properly"""
        with patch('hello_world.hello_world') as mock_hello:
            mock_hello.side_effect = RuntimeError("Test error")
            
            with self.assertRaises(SystemExit) as context:
                main()
            
            self.assertEqual(context.exception.code, 1)


class TestModuleIntegration(unittest.TestCase):
    """Integration tests for the module"""

    def test_module_imports(self):
        """Test that all required modules can be imported"""
        import hello_world
        self.assertTrue(hasattr(hello_world, 'hello_world'))
        self.assertTrue(hasattr(hello_world, 'main'))
        self.assertTrue(hasattr(hello_world, 'logger'))

    def test_logging_configuration(self):
        """Test that logging is properly configured"""
        import hello_world
        logger = hello_world.logger
        self.assertEqual(logger.name, 'hello_world')
        self.assertGreaterEqual(logger.level, logging.INFO)


class TestStreamlitDemo(unittest.TestCase):
    """Test cases for Streamlit demo functionality"""

    @patch('demo_hello_world.st')
    def test_demo_main_function(self, mock_st):
        """Test that demo main function runs without errors"""
        # Mock Streamlit components
        mock_st.set_page_config = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
        mock_st.sidebar = MagicMock()
        
        try:
            import demo_hello_world
            demo_hello_world.main()
        except ImportError:
            self.skipTest("demo_hello_world module not available")
        except Exception as e:
            self.fail(f"Demo main() raised {type(e).__name__}: {e}")

    def test_demo_chart_creation(self):
        """Test chart creation function"""
        try:
            import demo_hello_world
            fig = demo_hello_world.create_animated_chart()
            self.assertIsNotNone(fig)
        except ImportError:
            self.skipTest("demo_hello_world module not available")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
