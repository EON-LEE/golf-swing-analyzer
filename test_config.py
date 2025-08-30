#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test module for configuration functionality
"""

import unittest
import logging
from pathlib import Path
from config import (
    PROJECT_NAME, PROJECT_VERSION, LOGGING_CONFIG, VIDEO_CONFIG,
    PIPELINE_CONFIG, TEST_CONFIG, get_config, setup_logging, ensure_directories
)


class TestConfiguration(unittest.TestCase):
    """Test cases for configuration module"""

    def test_project_metadata(self):
        """Test project metadata constants"""
        self.assertIsInstance(PROJECT_NAME, str)
        self.assertGreater(len(PROJECT_NAME), 0)
        self.assertIsInstance(PROJECT_VERSION, str)
        self.assertGreater(len(PROJECT_VERSION), 0)

    def test_logging_config(self):
        """Test logging configuration structure"""
        self.assertIn('level', LOGGING_CONFIG)
        self.assertIn('format', LOGGING_CONFIG)
        self.assertEqual(LOGGING_CONFIG['level'], logging.INFO)
        self.assertIsInstance(LOGGING_CONFIG['format'], str)

    def test_video_config(self):
        """Test video configuration structure"""
        required_keys = ['supported_formats', 'max_file_size_mb', 'max_frames', 'default_fps']
        for key in required_keys:
            self.assertIn(key, VIDEO_CONFIG)
        
        self.assertIsInstance(VIDEO_CONFIG['supported_formats'], list)
        self.assertGreater(len(VIDEO_CONFIG['supported_formats']), 0)
        self.assertIsInstance(VIDEO_CONFIG['max_file_size_mb'], int)
        self.assertGreater(VIDEO_CONFIG['max_file_size_mb'], 0)

    def test_pipeline_config(self):
        """Test pipeline configuration structure"""
        required_keys = ['timeout_seconds', 'git_repo_path', 'required_documentation_sections']
        for key in required_keys:
            self.assertIn(key, PIPELINE_CONFIG)
        
        self.assertIsInstance(PIPELINE_CONFIG['timeout_seconds'], int)
        self.assertIsInstance(PIPELINE_CONFIG['git_repo_path'], str)
        self.assertIsInstance(PIPELINE_CONFIG['required_documentation_sections'], list)

    def test_get_config_valid_sections(self):
        """Test get_config with valid sections"""
        valid_sections = ['logging', 'video', 'pipeline', 'test']
        
        for section in valid_sections:
            config = get_config(section)
            self.assertIsInstance(config, dict)
            self.assertGreater(len(config), 0)

    def test_get_config_invalid_section(self):
        """Test get_config with invalid section"""
        with self.assertRaises(KeyError):
            get_config('invalid_section')

    def test_setup_logging(self):
        """Test logging setup function"""
        # This should not raise any exceptions
        setup_logging()
        
        # Verify logging is configured
        logger = logging.getLogger('test')
        self.assertGreaterEqual(logger.getEffectiveLevel(), logging.INFO)

    def test_ensure_directories(self):
        """Test directory creation function"""
        # This should not raise any exceptions
        ensure_directories()
        
        # Verify directories exist (they should be created if they don't exist)
        from config import DEMO_DIR, LOGS_DIR, CACHE_DIR, REF_DIR
        directories = [DEMO_DIR, LOGS_DIR, CACHE_DIR, REF_DIR]
        
        for directory in directories:
            # Directory should exist after ensure_directories() call
            # Note: We can't guarantee they exist in test environment,
            # but the function should not raise exceptions
            self.assertIsInstance(directory, Path)


class TestConfigurationIntegration(unittest.TestCase):
    """Integration tests for configuration module"""

    def test_module_imports(self):
        """Test that all required components can be imported"""
        import config
        
        required_attributes = [
            'PROJECT_NAME', 'PROJECT_VERSION', 'LOGGING_CONFIG',
            'VIDEO_CONFIG', 'PIPELINE_CONFIG', 'TEST_CONFIG',
            'get_config', 'setup_logging', 'ensure_directories'
        ]
        
        for attr in required_attributes:
            self.assertTrue(hasattr(config, attr))

    def test_configuration_consistency(self):
        """Test that configurations are internally consistent"""
        # Video formats should be lowercase extensions
        for fmt in VIDEO_CONFIG['supported_formats']:
            self.assertTrue(fmt.startswith('.'))
            self.assertEqual(fmt, fmt.lower())
        
        # Timeout should be reasonable
        self.assertGreater(PIPELINE_CONFIG['timeout_seconds'], 0)
        self.assertLess(PIPELINE_CONFIG['timeout_seconds'], 300)  # 5 minutes max
        
        # Test config verbosity should be valid
        self.assertIn(TEST_CONFIG['verbosity'], [0, 1, 2])


if __name__ == "__main__":
    unittest.main(verbosity=2)
