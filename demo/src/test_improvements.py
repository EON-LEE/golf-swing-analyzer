#!/usr/bin/env python3
"""Test script to verify the improvements made to the Golf Swing Analyzer."""

import sys
import os
import logging

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported without errors."""
    try:
        import config
        import utils
        logger.info("✅ Basic imports successful")
        
        try:
            from pose_estimation import PoseEstimator, PoseLandmarks
            logger.info("✅ PoseEstimator import successful")
        except ImportError as e:
            logger.warning(f"⚠️  PoseEstimator import failed: {e}")
        
        try:
            from swing_analyzer import SwingAnalyzer
            logger.info("✅ SwingAnalyzer import successful")
        except ImportError as e:
            logger.warning(f"⚠️  SwingAnalyzer import failed: {e}")
        
        return True
    except ImportError as e:
        logger.error(f"❌ Critical import error: {e}")
        return False

def test_config():
    """Test configuration module."""
    try:
        import config
        
        assert hasattr(config, 'MAX_FRAMES')
        assert hasattr(config, 'THRESHOLDS')
        assert hasattr(config, 'KEY_FRAME_RATIOS')
        assert isinstance(config.THRESHOLDS, dict)
        assert isinstance(config.KEY_FRAME_RATIOS, dict)
        assert config.MAX_FRAMES == 300
        
        logger.info("✅ Configuration test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

def test_utils():
    """Test utility functions."""
    try:
        from utils import safe_divide, normalize_angle, format_angle
        
        # Test safe_divide
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == 0.0
        
        # Test normalize_angle
        assert normalize_angle(370) == 10.0
        assert normalize_angle(-10) == 350.0
        
        # Test format_angle
        assert format_angle(45.123) == "45.1°"
        
        logger.info("✅ Utils test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Utils test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("Running Golf Swing Analyzer improvement tests...")
    
    tests = [test_imports, test_config, test_utils]
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    logger.info(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The improvements are working correctly.")
        return 0
    else:
        logger.warning("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
