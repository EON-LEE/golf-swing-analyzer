#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Datetime utilities for SMP-7 Hello World Chat Application
Provides standardized datetime handling with timezone support
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Union

# Configure module logger
logger = logging.getLogger(__name__)

# Default datetime format for consistency
DEFAULT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
HUMAN_READABLE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_current_datetime() -> str:
    """
    Return the current date and time as an ISO format string.
    
    This function maintains backward compatibility with the original implementation
    while providing enhanced error handling.
    
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
        raise RuntimeError(f"Datetime retrieval failed: {e}") from e


def get_current_datetime_utc(
    format_str: Optional[str] = None,
    use_utc: bool = True
) -> str:
    """
    Get current datetime as formatted string with enhanced error handling.
    
    Args:
        format_str: Optional custom format string. Defaults to ISO format.
        use_utc: Whether to use UTC timezone. Defaults to True.
        
    Returns:
        str: Formatted datetime string
        
    Raises:
        ValueError: If format string is invalid
        RuntimeError: If datetime generation fails
        
    Examples:
        >>> get_current_datetime_utc()
        '2025-08-31T10:52:29.749000Z'
        >>> get_current_datetime_utc(HUMAN_READABLE_FORMAT, use_utc=False)
        '2025-08-31 10:52:29'
    """
    try:
        # Validate format string if provided
        if format_str is not None and not isinstance(format_str, str):
            raise ValueError("Format string must be a string")
        
        # Get current datetime
        if use_utc:
            now = datetime.now(timezone.utc)
        else:
            now = datetime.now()
        
        # Use default format if none provided
        if format_str is None:
            format_str = DEFAULT_DATETIME_FORMAT
        
        # Format datetime
        formatted_datetime = now.strftime(format_str)
        
        logger.debug(f"Generated datetime: {formatted_datetime}")
        return formatted_datetime
        
    except ValueError as e:
        logger.error(f"Invalid datetime format: {e}")
        raise ValueError(f"Invalid datetime format: {e}") from e
    except Exception as e:
        logger.error(f"Failed to generate datetime: {e}")
        raise RuntimeError(f"Datetime generation failed: {e}") from e


def parse_datetime_string(
    datetime_str: str,
    format_str: Optional[str] = None
) -> datetime:
    """
    Parse datetime string into datetime object.
    
    Args:
        datetime_str: Datetime string to parse
        format_str: Format string for parsing. Auto-detects if None.
        
    Returns:
        datetime: Parsed datetime object
        
    Raises:
        ValueError: If datetime string cannot be parsed
    """
    if not isinstance(datetime_str, str) or not datetime_str.strip():
        raise ValueError("Datetime string must be a non-empty string")
    
    # Try common formats if none specified
    formats_to_try = [
        format_str,
        DEFAULT_DATETIME_FORMAT,
        HUMAN_READABLE_FORMAT,
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f"  # ISO format without Z
    ] if format_str is None else [format_str]
    
    # Remove None values
    formats_to_try = [f for f in formats_to_try if f is not None]
    
    for fmt in formats_to_try:
        try:
            return datetime.strptime(datetime_str.strip(), fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse datetime string: {datetime_str}")


def format_datetime(
    dt: datetime,
    format_str: str = DEFAULT_DATETIME_FORMAT
) -> str:
    """
    Format datetime object to string.
    
    Args:
        dt: Datetime object to format
        format_str: Format string to use
        
    Returns:
        str: Formatted datetime string
        
    Raises:
        ValueError: If inputs are invalid
    """
    if not isinstance(dt, datetime):
        raise ValueError("Input must be a datetime object")
    
    if not isinstance(format_str, str):
        raise ValueError("Format string must be a string")
    
    try:
        return dt.strftime(format_str)
    except Exception as e:
        raise ValueError(f"Failed to format datetime: {e}") from e


def get_timestamp() -> float:
    """
    Get current timestamp as float.
    
    Returns:
        float: Current timestamp
    """
    return datetime.now(timezone.utc).timestamp()


def is_valid_datetime_format(format_str: str) -> bool:
    """
    Check if a format string is valid for datetime formatting.
    
    Args:
        format_str: Format string to validate
        
    Returns:
        bool: True if format is valid
    """
    try:
        test_datetime = datetime.now()
        test_datetime.strftime(format_str)
        return True
    except (ValueError, TypeError):
        return False


if __name__ == "__main__":
    # Test datetime utilities
    try:
        print("Testing datetime utilities...")
        
        # Test original function (backward compatibility)
        current = get_current_datetime()
        print(f"Current datetime (original): {current}")
        
        # Test enhanced function
        current_utc = get_current_datetime_utc()
        print(f"Current UTC datetime: {current_utc}")
        
        # Test human readable format
        readable = get_current_datetime_utc(HUMAN_READABLE_FORMAT, use_utc=False)
        print(f"Human readable: {readable}")
        
        # Test parsing
        parsed = parse_datetime_string(current)
        print(f"Parsed datetime: {parsed}")
        
        # Test formatting
        formatted = format_datetime(parsed, HUMAN_READABLE_FORMAT)
        print(f"Reformatted: {formatted}")
        
        # Test timestamp
        timestamp = get_timestamp()
        print(f"Timestamp: {timestamp}")
        
        # Test format validation
        valid_format = is_valid_datetime_format("%Y-%m-%d")
        invalid_format = is_valid_datetime_format("%invalid%")
        print(f"Valid format test: {valid_format}")
        print(f"Invalid format test: {invalid_format}")
        
        print("✅ All datetime utility tests passed")
        
    except Exception as e:
        print(f"❌ Datetime utility test failed: {e}")
        raise
