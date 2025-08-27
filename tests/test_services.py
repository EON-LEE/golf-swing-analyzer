"""Tests for service layer."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile

from services import GolfSwingAnalysisService
from video_processor import PoseFrame
from exceptions import VideoProcessingError


class TestGolfSwingAnalysisService:
    """Test golf swing analysis service."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return GolfSwingAnalysisService(confidence=0.7)
    
    @pytest.fixture
    def mock_video_file(self):
        """Mock uploaded video file."""
        mock_file = Mock()
        mock_file.read.return_value = b"fake video data"
        return mock_file
    
    @pytest.fixture
    def sample_pose_frames(self):
        """Sample pose frames for testing."""
        return [
            PoseFrame(0, [(0.5, 0.5, 0.0)], 0.9),
            PoseFrame(1, [(0.6, 0.4, 0.1)], 0.8),
            PoseFrame(2, [(0.7, 0.3, 0.2)], 0.85)
        ]
    
    @pytest.mark.asyncio
    async def test_analyze_swing_success(self, service, mock_video_file, sample_pose_frames):
        """Test successful swing analysis."""
        with patch.object(service.video_processor, 'process_video', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = sample_pose_frames
            
            result = await service.analyze_swing(mock_video_file)
            
            assert result['success'] is True
            assert result['frame_count'] == 3
            assert 'metrics' in result
            assert 'phases' in result
    
    @pytest.mark.asyncio
    async def test_analyze_swing_failure(self, service, mock_video_file):
        """Test swing analysis failure."""
        with patch.object(service.video_processor, 'process_video', new_callable=AsyncMock) as mock_process:
            mock_process.side_effect = Exception("Processing failed")
            
            with pytest.raises(VideoProcessingError):
                await service.analyze_swing(mock_video_file)
    
    def test_calculate_metrics(self, service, sample_pose_frames):
        """Test metrics calculation."""
        metrics = service._calculate_metrics(sample_pose_frames)
        
        assert metrics.club_head_speed is not None
        assert metrics.swing_plane_angle is not None
        assert metrics.hip_rotation is not None
        assert metrics.shoulder_rotation is not None
        assert metrics.tempo is not None
    
    def test_detect_swing_phases(self, service, sample_pose_frames):
        """Test swing phase detection."""
        phases = service._detect_swing_phases(sample_pose_frames)
        
        assert isinstance(phases, list)
        assert len(phases) > 0
        assert all(isinstance(phase, str) for phase in phases)
