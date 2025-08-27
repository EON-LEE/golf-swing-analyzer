"""Error handling utilities."""

import functools
import streamlit as st
from typing import Callable, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)

def handle_errors(func: Callable) -> Callable:
    """Decorator for handling errors in Streamlit apps."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            st.error(f"오류가 발생했습니다: {str(e)}")
            return None
    return wrapper

def log_performance(func: Callable) -> Callable:
    """Decorator for logging function performance."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f}s")
        return result
    return wrapper
