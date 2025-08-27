"""Golf Swing 3D Analyzer - Main Application."""

import streamlit as st
from pathlib import Path
from config import Config
from utils.logger import setup_logger
from utils.error_handler import handle_errors

logger = setup_logger(__name__)

@handle_errors
def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Golf Swing 3D Analyzer",
        page_icon="⛳",
        layout="wide"
    )
    
    st.title("⛳ Golf Swing 3D Analyzer")
    st.markdown("골프 스윙 분석을 위한 AI 기반 도구")
    
    # Initialize configuration
    Config.create_directories()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("설정")
        confidence = st.slider(
            "포즈 추정 신뢰도",
            0.1, 1.0, Config.MEDIAPIPE_CONFIDENCE
        )
    
    # File upload
    uploaded_file = st.file_uploader(
        "골프 스윙 비디오 업로드",
        type=['mp4', 'avi', 'mov'],
        help=f"최대 파일 크기: {Config.MAX_VIDEO_SIZE_MB}MB"
    )
    
    if uploaded_file:
        st.success(f"파일 업로드 완료: {uploaded_file.name}")
        # TODO: Add video processing logic

if __name__ == "__main__":
    main()
