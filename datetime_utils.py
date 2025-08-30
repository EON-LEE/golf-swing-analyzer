#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Datetime utility functions for the Golf Swing 3D Analyzer.
"""

import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def get_current_datetime() -> str:
    """
    Return the current date and time as an ISO format string.
    
    Returns:
        str: Current datetime in ISO format (YYYY-MM-DDTHH:MM:SS.ffffff)
        
    Raises:
        RuntimeError: If datetime retrieval fails
    """
    try:
        current_time = datetime.now()
        iso_string = current_time.isoformat()
        logger.debug(f"Generated current datetime: {iso_string}")
        return iso_string
    except Exception as e:
        logger.error(f"Failed to get current datetime: {e}")
        raise RuntimeError(f"Datetime retrieval failed: {e}")
