"""Service layer for golf swing analysis."""

import asyncio
from pathlib import Path
from typing import List, Optional
import tempfile

from video_processor import VideoProcessor, PoseFrame
from models import SwingMetrics, SwingPhase
from utils.logger import setup_logger
from exceptions import VideoProcessingError

logger = setup_logger(__name__)


class GolfSwingAnalysisService:
    """Main service for golf swing analysis."""
    
    def __init__(self, confidence: float = 0.5):
        self.video_processor = VideoProcessor(confidence)
    
    async def analyze_swing(self, video_file) -> dict:
        """Analyze golf swing from uploaded video."""
        tmp_path = None
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(video_file.read())
                tmp_path = Path(tmp_file.name)
            
            logger.info(f"Processing video: {video_file.name} ({tmp_path.stat().st_size} bytes)")
            
            # Process video
            pose_frames = await self.video_processor.process_video(tmp_path)
            
            if not pose_frames:
                raise VideoProcessingError("No pose data extracted from video")
            
            # Calculate metrics
            metrics = self._calculate_metrics(pose_frames)
            phases = self._detect_swing_phases(pose_frames)
            
            logger.info(f"Analysis complete: {len(pose_frames)} frames, {len(phases)} phases")
            
            return {
                "success": True,
                "frame_count": len(pose_frames),
                "metrics": metrics.to_dict(),
                "phases": phases
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise VideoProcessingError(f"Failed to analyze swing: {e}")
        finally:
            # Clean up temporary file
            if tmp_path and tmp_path.exists():
                try:
                    tmp_path.unlink()
                    logger.debug(f"Cleaned up temporary file: {tmp_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {tmp_path}: {e}")
    
    def _calculate_metrics(self, frames: List[PoseFrame]) -> SwingMetrics:
        """Calculate swing metrics from pose frames."""
        # Placeholder implementation
        return SwingMetrics(
            club_head_speed=120.5,
            swing_plane_angle=45.2,
            hip_rotation=85.0,
            shoulder_rotation=95.0,
            tempo=1.2
        )
    
    def _detect_swing_phases(self, frames: List[PoseFrame]) -> List[str]:
        """Detect swing phases from pose data."""
        # Placeholder implementation
        return [phase.value for phase in SwingPhase]
