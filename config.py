#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration module for SMP-7 Hello World Chat Application
Centralized configuration management with validation and error handling
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Union

# Project metadata
PROJECT_NAME = "Hello World Chat App"
PROJECT_VERSION = "1.0.0"
PROJECT_DESCRIPTION = "Simple Streamlit chat application for SMP-7 testing"

# Logging configuration with enhanced settings
LOGGING_CONFIG: Dict[str, Any] = {
    'level': logging.INFO,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
    'handlers': ['console']
}

# File paths with validation
BASE_DIR = Path(__file__).parent.resolve()
DEMO_DIR = BASE_DIR / "demo"
LOGS_DIR = BASE_DIR / "logs" 
CACHE_DIR = BASE_DIR / "cache"
REF_DIR = BASE_DIR / "ref"

# Application settings
APP_CONFIG = {
    'title': 'Hello World Chat App 🌍',
    'page_icon': '🌍',
    'layout': 'centered',
    'max_message_length': 1000,
    'max_messages_history': 100
}

# Video processing settings (legacy from golf swing analyzer)
VIDEO_CONFIG = {
    'supported_formats': ['.mp4', '.avi', '.mov'],
    'max_file_size_mb': 100,
    'max_frames': 300,
    'default_fps': 30
}

# Pipeline test configuration with enhanced validation
PIPELINE_CONFIG = {
    'timeout_seconds': 10,
    'git_repo_path': str(BASE_DIR),
    'required_documentation_sections': [
        "AstraSprint Pipeline Integration",
        "SMP-9",
        "Feature Documentation"
    ],
    'test_files': ['test_hello_world.py', 'test_config.py', 'test_datetime_utils.py']
}

# Test configuration with comprehensive settings
TEST_CONFIG = {
    'verbosity': 2,
    'timeout': 30,
    'log_capture': True,
    'strict_mode': True,
    'coverage_threshold': 80
}


def validate_config_section(section: str, config: Dict[str, Any]) -> bool:
    """
    Validate configuration section for completeness and correctness.
    
    Args:
        section: Configuration section name
        config: Configuration dictionary to validate
        
    Returns:
        bool: True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    if not isinstance(config, dict):
        raise ValueError(f"Configuration for '{section}' must be a dictionary")
    
    if not config:
        raise ValueError(f"Configuration for '{section}' cannot be empty")
    
    # Section-specific validation
    if section == 'pipeline' and 'git_repo_path' in config:
        repo_path = Path(config['git_repo_path'])
        if not repo_path.exists():
            logging.warning(f"Git repository path does not exist: {repo_path}")
    
    return True


def get_config(section: str) -> Dict[str, Any]:
    """
    Get configuration for a specific section with validation.
    
    Args:
        section: Configuration section name
        
    Returns:
        Dict containing validated configuration for the section
        
    Raises:
        KeyError: If section doesn't exist
        ValueError: If configuration is invalid
    """
    configs = {
        'logging': LOGGING_CONFIG,
        'app': APP_CONFIG,
        'video': VIDEO_CONFIG,
        'pipeline': PIPELINE_CONFIG,
        'test': TEST_CONFIG
    }
    
    if section not in configs:
        available_sections = ', '.join(configs.keys())
        raise KeyError(
            f"Configuration section '{section}' not found. "
            f"Available sections: {available_sections}"
        )
    
    config = configs[section].copy()  # Return a copy to prevent modification
    validate_config_section(section, config)
    
    return config


def setup_logging() -> None:
    """
    Set up logging configuration for the application with error handling.
    
    Raises:
        RuntimeError: If logging setup fails
    """
    try:
        config = get_config('logging')
        logging.basicConfig(**{k: v for k, v in config.items() if k != 'handlers'})
        logging.info("Logging configuration initialized successfully")
    except Exception as e:
        # Fallback to basic logging if configuration fails
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Failed to setup logging configuration: {e}")
        raise RuntimeError(f"Logging setup failed: {e}") from e


def ensure_directories() -> None:
    """
    Ensure all required directories exist with proper error handling.
    
    Raises:
        OSError: If directory creation fails
    """
    directories = [DEMO_DIR, LOGS_DIR, CACHE_DIR, REF_DIR]
    
    for directory in directories:
        try:
            directory.mkdir(exist_ok=True, parents=True)
            logging.debug(f"Directory ensured: {directory}")
        except OSError as e:
            logging.error(f"Failed to create directory {directory}: {e}")
            raise OSError(f"Directory creation failed for {directory}: {e}") from e


def get_environment_info() -> Dict[str, str]:
    """
    Get current environment information for debugging.
    
    Returns:
        Dict containing environment information
    """
    return {
        'python_version': os.sys.version,
        'working_directory': str(Path.cwd()),
        'base_directory': str(BASE_DIR),
        'user': os.getenv('USER', 'unknown'),
        'platform': os.sys.platform
    }


if __name__ == "__main__":
    # Test configuration access and validation
    try:
        print(f"Project: {PROJECT_NAME} v{PROJECT_VERSION}")
        print(f"Base directory: {BASE_DIR}")
        
        # Test all configuration sections
        for section in ['logging', 'app', 'video', 'pipeline', 'test']:
            config = get_config(section)
            print(f"✅ {section.title()} config: {len(config)} settings")
        
        # Test directory creation
        ensure_directories()
        print("✅ All directories ensured")
        
        # Display environment info
        env_info = get_environment_info()
        print(f"Environment: {env_info['platform']}")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        raise
