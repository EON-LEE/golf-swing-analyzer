"""Health check and monitoring utilities."""

import psutil
import time
from typing import Dict, Any
from pathlib import Path

from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class HealthChecker:
    """System health monitoring."""
    
    @staticmethod
    def get_system_health() -> Dict[str, Any]:
        """Get comprehensive system health status."""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "system": HealthChecker._get_system_metrics(),
            "application": HealthChecker._get_app_metrics(),
            "dependencies": HealthChecker._check_dependencies()
        }
    
    @staticmethod
    def _get_system_metrics() -> Dict[str, Any]:
        """Get system resource metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
    
    @staticmethod
    def _get_app_metrics() -> Dict[str, Any]:
        """Get application-specific metrics."""
        log_dir_size = sum(
            f.stat().st_size for f in Config.LOG_DIR.rglob('*') if f.is_file()
        ) if Config.LOG_DIR.exists() else 0
        
        cache_dir_size = sum(
            f.stat().st_size for f in Config.CACHE_DIR.rglob('*') if f.is_file()
        ) if Config.CACHE_DIR.exists() else 0
        
        return {
            "log_directory_size_mb": log_dir_size / (1024 * 1024),
            "cache_directory_size_mb": cache_dir_size / (1024 * 1024),
            "config": Config.get_config_dict()
        }
    
    @staticmethod
    def _check_dependencies() -> Dict[str, bool]:
        """Check if critical dependencies are available."""
        dependencies = {}
        
        try:
            import cv2
            dependencies["opencv"] = True
        except ImportError:
            dependencies["opencv"] = False
        
        try:
            import mediapipe
            dependencies["mediapipe"] = True
        except ImportError:
            dependencies["mediapipe"] = False
        
        try:
            import numpy
            dependencies["numpy"] = True
        except ImportError:
            dependencies["numpy"] = False
        
        return dependencies
    
    @staticmethod
    def is_healthy() -> bool:
        """Quick health check."""
        try:
            health = HealthChecker.get_system_health()
            
            # Check critical thresholds
            if health["system"]["memory_percent"] > 90:
                return False
            
            if health["system"]["disk_percent"] > 95:
                return False
            
            # Check dependencies
            critical_deps = ["opencv", "mediapipe", "numpy"]
            if not all(health["dependencies"].get(dep, False) for dep in critical_deps):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
