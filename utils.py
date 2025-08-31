#!/usr/bin/env python3
"""Utility functions for the Golf Swing Analyzer."""

import numpy as np
from typing import Union, Optional

def safe_divide(numerator: Union[float, int, None], denominator: Union[float, int, None]) -> float:
    """Safely divide two numbers, handling edge cases."""
    try:
        if numerator is None or denominator is None:
            return 0.0
        if abs(denominator) < 1e-10:
            return 0.0
        return float(numerator) / float(denominator)
    except (TypeError, ValueError):
        return 0.0

def calculate_angle_3d(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """Calculate angle between three 3D points."""
    try:
        # Handle None values
        if p1 is None or p2 is None or p3 is None:
            return 0.0
        
        # Convert to numpy arrays if needed
        p1 = np.asarray(p1)
        p2 = np.asarray(p2)
        p3 = np.asarray(p3)
        
        v1 = p1 - p2
        v2 = p3 - p2
        
        # Check for zero vectors
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 < 1e-10 or norm2 < 1e-10:
            return 0.0
        
        cos_angle = np.dot(v1, v2) / (norm1 * norm2)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        
        return np.degrees(np.arccos(cos_angle))
    except (ValueError, ZeroDivisionError, TypeError):
        return 0.0

def calculate_distance_3d(p1: np.ndarray, p2: np.ndarray) -> float:
    """Calculate Euclidean distance between two 3D points."""
    try:
        # Handle None values
        if p1 is None or p2 is None:
            return 0.0
        
        # Convert to numpy arrays if needed
        p1 = np.asarray(p1)
        p2 = np.asarray(p2)
        
        return float(np.linalg.norm(p1 - p2))
    except (ValueError, TypeError):
        return 0.0
