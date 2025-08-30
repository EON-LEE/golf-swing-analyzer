#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for datetime_utils module.
"""

import unittest
from unittest.mock import patch
from datetime import datetime
import logging

from datetime_utils import get_current_datetime


class TestDatetimeUtils(unittest.TestCase):
    """Test cases for datetime utility functions."""

    def setUp(self):
        """Set up test fixtures."""
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Clean up after tests."""
        logging.disable(logging.NOTSET)

    def test_get_current_datetime_format(self):
        """Test that get_current_datetime returns proper ISO format."""
        result = get_current_datetime()
        
        # Verify it's a string
        self.assertIsInstance(result, str)
        
        # Verify it can be parsed back to datetime
        parsed_datetime = datetime.fromisoformat(result)
        self.assertIsInstance(parsed_datetime, datetime)

    @patch('datetime_utils.datetime')
    def test_get_current_datetime_mocked(self, mock_datetime):
        """Test get_current_datetime with mocked datetime."""
        # Mock datetime.now() to return a fixed datetime
        fixed_datetime = datetime(2023, 12, 25, 10, 30, 45, 123456)
        mock_datetime.now.return_value = fixed_datetime
        
        result = get_current_datetime()
        expected = "2023-12-25T10:30:45.123456"
        
        self.assertEqual(result, expected)
        mock_datetime.now.assert_called_once()

    @patch('datetime_utils.datetime')
    def test_get_current_datetime_exception(self, mock_datetime):
        """Test get_current_datetime handles exceptions properly."""
        # Mock datetime.now() to raise an exception
        mock_datetime.now.side_effect = Exception("Test exception")
        
        with self.assertRaises(RuntimeError) as context:
            get_current_datetime()
        
        self.assertIn("Datetime retrieval failed", str(context.exception))


if __name__ == '__main__':
    unittest.main()
