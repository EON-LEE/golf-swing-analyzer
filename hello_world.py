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
    try:
        logger.info("Hello World")
        logger.info("안녕하세요, 세계!")
        logger.info("Hello World message displayed successfully")
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
