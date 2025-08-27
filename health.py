"""Health check system for Golf Swing Analyzer."""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional
import cv2
import mediapipe as mp
import numpy as np
import psutil
import time

from config import Config
from utils.logger import setup_logger
from exceptions import ConfigurationError

logger = setup_logger(__name__)


class HealthChecker:
    """System health and dependency checker."""
    
    def __init__(self):
        self.checks = []
        self.results = {}
    
    async def run_all_checks(self) -> Dict[str, bool]:
        """Run all health checks."""
        checks = [
            self._check_python_version(),
            self._check_dependencies(),
            self._check_directories(),
            self._check_mediapipe(),
            self._check_opencv(),
            self._check_config(),
            self._check_disk_space(),
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        for i, result in enumerate(results):
            check_name = checks[i].__name__.replace('_check_', '')
            self.results[check_name] = not isinstance(result, Exception)
            if isinstance(result, Exception):
                logger.error(f"Health check failed - {check_name}: {result}")
        
        return self.results
    
    async def _check_python_version(self) -> bool:
        """Check Python version compatibility."""
        version = sys.version_info
        if version < (3, 8):
            raise ConfigurationError(f"Python 3.8+ required, got {version.major}.{version.minor}")
        return True
    
    async def _check_dependencies(self) -> bool:
        """Check critical dependencies."""
        try:
            import streamlit
            import cv2
            import mediapipe
            import numpy
            return True
        except ImportError as e:
            raise ConfigurationError(f"Missing dependency: {e}")
    
    async def _check_directories(self) -> bool:
        """Check required directories exist and are writable."""
        for dir_path in [Config.LOG_DIR, Config.CACHE_DIR, Config.TEMP_DIR]:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # Test write permission
            test_file = dir_path / ".health_check"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except Exception as e:
                raise ConfigurationError(f"Cannot write to {dir_path}: {e}")
        return True
    
    async def _check_mediapipe(self) -> bool:
        """Check MediaPipe functionality."""
        try:
            mp_pose = mp.solutions.pose
            pose = mp_pose.Pose(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            # Test with dummy frame
            dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            results = pose.process(dummy_frame)
            pose.close()
            return True
        except Exception as e:
            raise ConfigurationError(f"MediaPipe error: {e}")
    
    async def _check_opencv(self) -> bool:
        """Check OpenCV functionality."""
        try:
            # Test basic OpenCV operations
            test_array = np.zeros((100, 100, 3), dtype=np.uint8)
            gray = cv2.cvtColor(test_array, cv2.COLOR_BGR2GRAY)
            return True
        except Exception as e:
            raise ConfigurationError(f"OpenCV error: {e}")
    
    async def _check_config(self) -> bool:
        """Validate configuration."""
        try:
            Config.validate_config()
            return True
        except Exception as e:
            raise ConfigurationError(f"Config validation failed: {e}")
    
    async def _check_disk_space(self) -> bool:
        """Check available disk space."""
        import shutil
        
        for dir_path in [Config.LOG_DIR, Config.CACHE_DIR, Config.TEMP_DIR]:
            free_bytes = shutil.disk_usage(dir_path).free
            free_mb = free_bytes / (1024 * 1024)
            
            if free_mb < 100:  # Require at least 100MB
                raise ConfigurationError(f"Low disk space in {dir_path}: {free_mb:.1f}MB")
        return True
    
    def get_health_summary(self) -> Dict[str, any]:
        """Get health check summary."""
        total_checks = len(self.results)
        passed_checks = sum(self.results.values())
        
        return {
            "overall_health": passed_checks == total_checks,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "details": self.results
        }
    
    @staticmethod
    def get_system_metrics() -> Dict[str, any]:
        """Get system resource metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "timestamp": time.time()
        }


async def main():
    """Run health checks."""
    checker = HealthChecker()
    await checker.run_all_checks()
    
    summary = checker.get_health_summary()
    
    print(f"Health Check Results:")
    print(f"Overall: {'✅ HEALTHY' if summary['overall_health'] else '❌ UNHEALTHY'}")
    print(f"Passed: {summary['passed_checks']}/{summary['total_checks']}")
    
    for check, result in summary['details'].items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
    
    return summary['overall_health']


if __name__ == "__main__":
    healthy = asyncio.run(main())
    sys.exit(0 if healthy else 1)
