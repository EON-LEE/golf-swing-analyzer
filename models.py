"""Data models for golf swing analysis."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import numpy as np

class SwingPhase(Enum):
    """Golf swing phases."""
    ADDRESS = "address"
    BACKSWING = "backswing"
    TOP = "top"
    DOWNSWING = "downswing"
    IMPACT = "impact"
    FOLLOW_THROUGH = "follow_through"

@dataclass
class Joint:
    """3D joint position."""
    x: float
    y: float
    z: float
    confidence: float = 0.0

@dataclass
class SwingMetrics:
    """Key swing analysis metrics."""
    club_head_speed: Optional[float] = None
    swing_plane_angle: Optional[float] = None
    hip_rotation: Optional[float] = None
    shoulder_rotation: Optional[float] = None
    tempo: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "club_head_speed": self.club_head_speed,
            "swing_plane_angle": self.swing_plane_angle,
            "hip_rotation": self.hip_rotation,
            "shoulder_rotation": self.shoulder_rotation,
            "tempo": self.tempo
        }
