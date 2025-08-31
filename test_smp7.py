import pytest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_smp7_file_exists():
    """Test that the SMP-7 hello world file exists"""
    assert os.path.exists("smp7_hello_world.py")

def test_smp7_imports():
    """Test that required imports work"""
    try:
        import streamlit as st
        import time
        assert True
    except ImportError:
        pytest.fail("Required imports not available")

def test_smp7_content():
    """Test that the file contains expected content"""
    with open("smp7_hello_world.py", "r") as f:
        content = f.read()
        assert "Hello World" in content
        assert "SMP-7" in content
        assert "streamlit" in content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
