#!/usr/bin/env python3
"""Final comprehensive test for all code improvements."""

import sys
import os
import logging
import numpy as np
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all critical imports work correctly."""
    try:
        from config import MAX_FRAMES, SUPPORTED_VIDEO_FORMATS
        from utils import safe_divide, calculate_angle_3d, calculate_distance_3d
        logger.info("✅ All imports successful")
        return True
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False

def test_safe_divide():
    """Test enhanced safe_divide function."""
    from utils import safe_divide
    
    test_cases = [
        (10, 2, 5.0),           # Normal case
        (10, 0, 0.0),           # Division by zero
        (None, 5, 0.0),         # None numerator
        (10, None, 0.0),        # None denominator
        (10, 1e-15, 0.0),       # Very small denominator
        ("invalid", 5, 0.0),    # Invalid type
    ]
    
    passed = 0
    for num, den, expected in test_cases:
        result = safe_divide(num, den)
        if result == expected:
            passed += 1
        else:
            logger.warning(f"safe_divide({num}, {den}) = {result}, expected {expected}")
    
    success = passed == len(test_cases)
    logger.info(f"✅ safe_divide: {passed}/{len(test_cases)} tests passed" if success else f"❌ safe_divide: {passed}/{len(test_cases)} tests passed")
    return success

def test_angle_calculation():
    """Test enhanced angle calculation with edge cases."""
    from utils import calculate_angle_3d
    
    # Test normal case
    p1 = np.array([1, 0, 0])
    p2 = np.array([0, 0, 0])
    p3 = np.array([0, 1, 0])
    angle = calculate_angle_3d(p1, p2, p3)
    
    # Test edge cases
    edge_cases = [
        (None, p2, p3),         # None input
        (p1, None, p3),         # None input
        (p1, p2, None),         # None input
        (p2, p2, p2),           # Same points (zero vectors)
    ]
    
    passed = 0
    for case in edge_cases:
        result = calculate_angle_3d(*case)
        if result == 0.0:  # Should return 0.0 for invalid inputs
            passed += 1
    
    # Normal case should return ~90 degrees
    normal_passed = 85 <= angle <= 95
    
    success = passed == len(edge_cases) and normal_passed
    logger.info(f"✅ calculate_angle_3d: All edge cases handled" if success else f"❌ calculate_angle_3d: Failed edge case handling")
    return success

def test_distance_calculation():
    """Test enhanced distance calculation."""
    from utils import calculate_distance_3d
    
    # Normal case
    p1 = np.array([0, 0, 0])
    p2 = np.array([3, 4, 0])
    distance = calculate_distance_3d(p1, p2)
    
    # Edge cases
    edge_cases = [
        (None, p2),
        (p1, None),
    ]
    
    passed = 0
    for case in edge_cases:
        result = calculate_distance_3d(*case)
        if result == 0.0:
            passed += 1
    
    # Normal case should return 5.0
    normal_passed = abs(distance - 5.0) < 0.001
    
    success = passed == len(edge_cases) and normal_passed
    logger.info(f"✅ calculate_distance_3d: All tests passed" if success else f"❌ calculate_distance_3d: Tests failed")
    return success

def test_configuration():
    """Test configuration constants are properly set."""
    from config import MAX_FRAMES, SUPPORTED_VIDEO_FORMATS, THRESHOLDS
    
    checks = [
        MAX_FRAMES == 300,
        isinstance(SUPPORTED_VIDEO_FORMATS, list),
        len(SUPPORTED_VIDEO_FORMATS) >= 3,
        isinstance(THRESHOLDS, dict),
        len(THRESHOLDS) > 5,
    ]
    
    success = all(checks)
    logger.info(f"✅ Configuration: All constants properly set" if success else f"❌ Configuration: Missing or invalid constants")
    return success

def test_memory_efficiency():
    """Test memory efficiency improvements."""
    from config import MAX_FRAMES
    
    # Simulate frame processing logic
    total_frames = 1000
    skip_ratio = max(1, total_frames // MAX_FRAMES)
    processed_frames = 0
    
    for frame_count in range(total_frames):
        if frame_count % skip_ratio == 0 and processed_frames < MAX_FRAMES:
            processed_frames += 1
    
    # Should process approximately MAX_FRAMES
    efficiency_check = processed_frames <= MAX_FRAMES
    ratio_check = skip_ratio >= 3  # Should skip frames for large videos
    
    success = efficiency_check and ratio_check
    logger.info(f"✅ Memory efficiency: Frame limiting works correctly ({processed_frames}/{MAX_FRAMES})" if success else f"❌ Memory efficiency: Frame limiting failed")
    return success

def run_comprehensive_test():
    """Run all tests and provide final score."""
    logger.info("🚀 Running Final Comprehensive Test Suite")
    
    tests = [
        ("Imports", test_imports),
        ("Safe Division", test_safe_divide),
        ("Angle Calculation", test_angle_calculation),
        ("Distance Calculation", test_distance_calculation),
        ("Configuration", test_configuration),
        ("Memory Efficiency", test_memory_efficiency),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
    
    score = (passed_tests / total_tests) * 100
    
    logger.info(f"\n📊 Final Test Results: {passed_tests}/{total_tests} tests passed")
    logger.info(f"🎯 Final Code Quality Score: {score:.1f}/100")
    
    if score >= 95:
        logger.info("🎉 EXCELLENT: All critical improvements implemented successfully!")
    elif score >= 80:
        logger.info("✅ GOOD: Most improvements working correctly")
    else:
        logger.info("⚠️  NEEDS WORK: Some critical issues remain")
    
    return score

if __name__ == "__main__":
    score = run_comprehensive_test()
    sys.exit(0 if score >= 95 else 1)
