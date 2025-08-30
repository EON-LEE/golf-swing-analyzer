"""Service layer for golf swing analysis."""

import logging
from typing import Dict, Optional
from swing_analyzer import SwingAnalyzer
from pose_estimation import PoseEstimator
import os

logger = logging.getLogger(__name__)

class SwingAnalysisService:
    """High-level service for golf swing analysis."""
    
    def __init__(self):
        """Initialize the analysis service."""
        try:
            self.swing_analyzer = SwingAnalyzer()
            self.pose_estimator = PoseEstimator()
            logger.info("SwingAnalysisService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SwingAnalysisService: {e}")
            raise
    
    def analyze_swing_video(self, video_path: str) -> Optional[Dict]:
        """
        Analyze a golf swing video and return comprehensive results.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary containing analysis results or None if failed
        """
        try:
            # Validate input
            if not video_path or not os.path.exists(video_path):
                logger.error(f"Invalid video path: {video_path}")
                return None
            
            logger.info(f"Starting analysis for video: {video_path}")
            
            # Perform analysis
            result = self.swing_analyzer.analyze_video(video_path)
            
            if result:
                logger.info("Analysis completed successfully")
                return result
            else:
                logger.warning("Analysis returned empty result")
                return None
                
        except Exception as e:
            logger.error(f"Error in swing analysis: {e}")
            return None
    
    def validate_video_file(self, video_path: str) -> bool:
        """
        Validate if the video file is suitable for analysis.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not os.path.exists(video_path):
                return False
            
            # Check file extension
            valid_extensions = ['.mp4', '.avi', '.mov']
            file_ext = os.path.splitext(video_path)[1].lower()
            
            if file_ext not in valid_extensions:
                logger.warning(f"Unsupported file format: {file_ext}")
                return False
            
            # Check file size (should be reasonable)
            file_size = os.path.getsize(video_path)
            max_size = 500 * 1024 * 1024  # 500MB
            
            if file_size > max_size:
                logger.warning(f"File too large: {file_size} bytes")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating video file: {e}")
            return False
    
    def get_analysis_summary(self, analysis_result: Dict) -> Dict:
        """
        Generate a summary of the analysis results.
        
        Args:
            analysis_result: Full analysis results
            
        Returns:
            Summary dictionary
        """
        try:
            if not analysis_result:
                return {}
            
            metrics = analysis_result.get('metrics', {})
            evaluations = analysis_result.get('evaluations', {})
            
            # Calculate overall score
            total_checks = 0
            passed_checks = 0
            
            for phase_evals in evaluations.values():
                for check_result in phase_evals.values():
                    total_checks += 1
                    if check_result:
                        passed_checks += 1
            
            overall_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
            
            # Identify key strengths and weaknesses
            strengths = []
            weaknesses = []
            
            for phase, phase_evals in evaluations.items():
                for check_name, passed in phase_evals.items():
                    if passed:
                        strengths.append(f"{phase}: {check_name}")
                    else:
                        weaknesses.append(f"{phase}: {check_name}")
            
            summary = {
                'overall_score': round(overall_score, 1),
                'total_frames': len(analysis_result.get('frames', [])),
                'key_metrics': {
                    'shoulder_rotation': metrics.get('shoulder_rotation', 0),
                    'impact_angle': metrics.get('impact_angle', 0),
                    'hip_rotation': metrics.get('hip_rotation', 0),
                    'head_stability': metrics.get('head_movement', 0)
                },
                'strengths': strengths[:3],  # Top 3 strengths
                'areas_for_improvement': weaknesses[:3],  # Top 3 areas to improve
                'total_checks': total_checks,
                'passed_checks': passed_checks
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating analysis summary: {e}")
            return {}
