"""Centralized logging configuration."""

import logging
import logging.handlers
from pathlib import Path
from config import Config

def setup_logger(name: str) -> logging.Logger:
    """Set up logger with file and console handlers."""
    Config.create_directories()
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    if logger.handlers:
        return logger
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        Config.LOG_DIR / "app.log",
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s - %(message)s')
    )
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
