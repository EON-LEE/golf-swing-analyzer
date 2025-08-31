#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hello World module for SMP-3 Golf Swing Analyzer
Simple greeting functionality with Korean support
"""

import logging

# Configure logging with proper format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def hello_world() -> None:
    """
    Display Hello World message in English and Korean.
    
    Raises:
        RuntimeError: If message display fails
    """
    messages = [
        "Hello World",
        "안녕하세요, 세계!",
        "Hello World message displayed successfully"
    ]
    
    try:
        for i, message in enumerate(messages, 1):
            logger.info(message)
            # Validate logging worked by checking if handlers exist
            if not logger.handlers and not logging.getLogger().handlers:
                raise RuntimeError("Logging system not properly configured")
        
        logger.debug(f"Successfully displayed {len(messages)} messages")
        
    except Exception as e:
        error_msg = f"Error displaying hello world message: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def main() -> None:
    """Main entry point for the module."""
    try:
        hello_world()
    except RuntimeError as e:
        logger.critical(f"Application failed: {e}")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
