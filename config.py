#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration module for SMP-3 Golf Swing Analyzer
Centralized configuration management for better maintainability
"""

import logging
from pathlib import Path
from typing import Dict, Any

# Project metadata
PROJECT_NAME = "Golf Swing 3D Analyzer"
PROJECT_VERSION = "1.0.0"
PROJECT_DESCRIPTION = "골프 스윙 분석을 위한 FastAPI 기반 백엔드 서비스"

# Logging configuration
LOGGING_CONFIG: Dict[str, Any] = {
    'level': logging.INFO,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
}

# File paths
BASE_DIR = Path(__file__).parent
DEMO_DIR = BASE_DIR / "demo"
LOGS_DIR = BASE_DIR / "logs" 
CACHE_DIR = BASE_DIR / "cache"
REF_DIR = BASE_DIR / "ref"

# Video processing settings
VIDEO_CONFIG = {
    'supported_formats': ['.mp4', '.avi', '.mov'],
    'max_file_size_mb': 100,
    'max_frames': 300,
    'default_fps': 30
}

# Pipeline test configuration
PIPELINE_CONFIG = {
    'timeout_seconds': 10,
    'git_repo_path': '/tmp/q-workspace/SMP-3',
    'required_documentation_sections': [
        "AstraSprint Pipeline Integration",
        "SMP-9",
        "Feature Documentation"
    ]
}

# Test configuration
TEST_CONFIG = {
    'verbosity': 2,
    'timeout': 30,
    'log_capture': True
}

def get_config(section: str) -> Dict[str, Any]:
    """
    Get configuration for a specific section.
    
    Args:
        section: Configuration section name
        
    Returns:
        Dict containing configuration for the section
        
    Raises:
        KeyError: If section doesn't exist
    """
    configs = {
        'logging': LOGGING_CONFIG,
        'video': VIDEO_CONFIG,
        'pipeline': PIPELINE_CONFIG,
        'test': TEST_CONFIG
    }
    
    if section not in configs:
        raise KeyError(f"Configuration section '{section}' not found")
    
    return configs[section]


def setup_logging() -> None:
    """Set up logging configuration for the application."""
    logging.basicConfig(**LOGGING_CONFIG)


def ensure_directories() -> None:
    """Ensure all required directories exist."""
    directories = [DEMO_DIR, LOGS_DIR, CACHE_DIR, REF_DIR]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)


if __name__ == "__main__":
    # Test configuration access
    print(f"Project: {PROJECT_NAME} v{PROJECT_VERSION}")
    print(f"Base directory: {BASE_DIR}")
    
    # Test configuration retrieval
    for section in ['logging', 'video', 'pipeline', 'test']:
        config = get_config(section)
        print(f"{section.title()} config: {len(config)} settings")
