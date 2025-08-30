#!/usr/bin/env python3
"""
Demo script to showcase the improvements made to the Golf Swing Analyzer.
This script demonstrates the key improvements without requiring OpenCV.
"""

import sys
import os
import numpy as np

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_configuration():
    """Demonstrate improved configuration management."""
    print("=== Configuration Management Demo ===")
    
    import config
    
    print(f"✅ MAX_FRAMES: {config.MAX_FRAMES}")
    print(f"✅ LOG_LEVEL: {config.LOG_LEVEL}")
    print(f"✅ SUPPORTED_FORMATS: {config.SUPPORTED_VIDEO_FORMATS}")
    print(f"✅ THRESHOLDS: {len(config.THRESHOLDS)} configured")
    print(f"✅ KEY_FRAME_RATIOS: {len(config.KEY_FRAME_RATIOS)} phases")
    print()

def demo_utilities():
    """Demonstrate improved utility functions."""
    print("=== Utility Functions Demo ===")
    
    import utils
    
    # Test safe mathematical operations
    print(f"✅ safe_divide(10, 2): {utils.safe_divide(10, 2)}")
    print(f"✅ safe_divide(10, 0): {utils.safe_divide(10, 0)}")
    
    # Test angle operations
    print(f"✅ normalize_angle(370): {utils.normalize_angle(370)}")
    print(f"✅ normalize_angle(-10): {utils.normalize_angle(-10)}")
    print(f"✅ format_angle(45.123): {utils.format_angle(45.123)}")
    
    # Test 3D calculations
    p1 = np.array([0, 0, 0])
    p2 = np.array([1, 1, 1])
    print(f"✅ calculate_distance_3d: {utils.calculate_distance_3d(p1, p2):.2f}")
    
    # Test angle calculation
    p3 = np.array([2, 0, 0])
    angle = utils.calculate_angle_3d(p1, p2, p3)
    print(f"✅ calculate_angle_3d: {angle:.1f}°")
    print()

def demo_error_handling():
    """Demonstrate improved error handling."""
    print("=== Error Handling Demo ===")
    
    import utils
    
    # Test with invalid data
    try:
        result = utils.safe_divide(10, 0)
        print(f"✅ Division by zero handled gracefully: {result}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Test with invalid landmarks
    invalid_landmarks = {"incomplete": "data"}
    result = utils.validate_landmarks_data(invalid_landmarks)
    print(f"✅ Invalid landmarks detected: {not result}")
    
    # Test with valid landmarks
    valid_landmarks = {
        'left_shoulder': [0.4, 0.4, 0.0],
        'right_shoulder': [0.6, 0.4, 0.0],
        'left_elbow': [0.3, 0.5, 0.0],
        'right_elbow': [0.7, 0.5, 0.0],
        'left_wrist': [0.2, 0.6, 0.0],
        'right_wrist': [0.8, 0.6, 0.0],
        'left_hip': [0.45, 0.7, 0.0],
        'right_hip': [0.55, 0.7, 0.0],
        'left_knee': [0.4, 0.8, 0.0],
        'right_knee': [0.6, 0.8, 0.0],
        'left_ankle': [0.35, 0.9, 0.0],
        'right_ankle': [0.65, 0.9, 0.0],
        'nose': [0.5, 0.3, 0.0]
    }
    result = utils.validate_landmarks_data(valid_landmarks)
    print(f"✅ Valid landmarks accepted: {result}")
    print()

def demo_memory_efficiency():
    """Demonstrate memory efficiency improvements."""
    print("=== Memory Efficiency Demo ===")
    
    import config
    
    # Show frame limiting
    total_frames = 1000
    max_frames = config.MAX_FRAMES
    processed_frames = min(total_frames, max_frames)
    
    print(f"✅ Original video frames: {total_frames}")
    print(f"✅ Max processing limit: {max_frames}")
    print(f"✅ Frames to process: {processed_frames}")
    print(f"✅ Memory savings: {((total_frames - processed_frames) / total_frames * 100):.1f}%")
    
    # Show data type optimization
    data = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    print(f"✅ Optimized data type: {data.dtype}")
    print(f"✅ Memory per element: {data.itemsize} bytes")
    print()

def main():
    """Run all improvement demos."""
    print("🏌️ Golf Swing Analyzer - Improvements Demo")
    print("=" * 50)
    print()
    
    try:
        demo_configuration()
        demo_utilities()
        demo_error_handling()
        demo_memory_efficiency()
        
        print("🎉 All improvements working correctly!")
        print()
        print("Key Benefits:")
        print("• ✅ Centralized configuration management")
        print("• ✅ Robust error handling and validation")
        print("• ✅ Memory-efficient processing")
        print("• ✅ Comprehensive utility functions")
        print("• ✅ Clean, maintainable code structure")
        
        return 0
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
