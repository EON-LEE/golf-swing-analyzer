"""Golf Swing 3D Analyzer - Main Application."""

import asyncio
import streamlit as st
from pathlib import Path

from config import Config
from services import GolfSwingAnalysisService
from utils.logger import setup_logger
from utils.error_handler import handle_errors
from exceptions import VideoProcessingError

logger = setup_logger(__name__)


@handle_errors
def main():
    """Main application entry point."""
    # Initialize and validate configuration
    try:
        Config.validate_config()
        Config.create_directories()
    except Exception as e:
        st.error(f"❌ 설정 오류: {e}")
        return
    
    st.set_page_config(
        page_title="Golf Swing 3D Analyzer",
        page_icon="⛳",
        layout="wide"
    )
    
    st.title("⛳ Golf Swing 3D Analyzer")
    st.markdown("골프 스윙 분석을 위한 AI 기반 도구")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("설정")
        confidence = st.slider(
            "포즈 추정 신뢰도",
            0.1, 1.0, Config.MEDIAPIPE_CONFIDENCE,
            help="높을수록 정확하지만 느려집니다"
        )
        
        st.subheader("지원 형식")
        st.write("• MP4, AVI, MOV")
        st.write(f"• 최대 {Config.MAX_VIDEO_SIZE_MB}MB")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("비디오 업로드")
        uploaded_file = st.file_uploader(
            "골프 스윙 비디오를 선택하세요",
            type=['mp4', 'avi', 'mov'],
            help=f"최대 파일 크기: {Config.MAX_VIDEO_SIZE_MB}MB"
        )
        
        if uploaded_file:
            try:
                # Validate uploaded file
                from utils.validators import validate_uploaded_file
                validate_uploaded_file(uploaded_file)
                
                st.success(f"✅ 파일 업로드 완료: {uploaded_file.name}")
                
                # Show file info
                file_size_mb = uploaded_file.size / (1024 * 1024)
                st.info(f"📁 파일 크기: {file_size_mb:.1f}MB")
                
            except Exception as e:
                st.error(f"❌ 파일 검증 실패: {e}")
                uploaded_file = None
            
            if st.button("🔍 분석 시작", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("비디오 처리 중...")
                    progress_bar.progress(25)
                    
                    # Run async analysis
                    service = GolfSwingAnalysisService(confidence)
                    
                    status_text.text("포즈 추정 중...")
                    progress_bar.progress(50)
                    
                    result = asyncio.run(service.analyze_swing(uploaded_file))
                    
                    progress_bar.progress(100)
                    status_text.text("분석 완료!")
                    
                    st.session_state['analysis_result'] = result
                    st.success("✅ 분석 완료!")
                    
                except VideoProcessingError as e:
                    st.error(f"❌ 비디오 처리 실패: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    st.error(f"❌ 예상치 못한 오류가 발생했습니다. 다시 시도해주세요.")
                finally:
                    progress_bar.empty()
                    status_text.empty()
    
    with col2:
        st.subheader("분석 결과")
        
        if 'analysis_result' in st.session_state:
            result = st.session_state['analysis_result']
            
            # Display metrics
            metrics = result['metrics']
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric("클럽 헤드 스피드", f"{metrics['club_head_speed']:.1f} mph")
                st.metric("스윙 플레인 각도", f"{metrics['swing_plane_angle']:.1f}°")
            
            with col2_2:
                st.metric("엉덩이 회전", f"{metrics['hip_rotation']:.1f}°")
                st.metric("어깨 회전", f"{metrics['shoulder_rotation']:.1f}°")
            
            st.metric("템포", f"{metrics['tempo']:.1f}s")
            
            # Display phases
            st.subheader("스윙 단계")
            phases = result['phases']
            for i, phase in enumerate(phases, 1):
                st.write(f"{i}. {phase.replace('_', ' ').title()}")
        
        else:
            st.info("비디오를 업로드하고 분석을 시작하세요.")


if __name__ == "__main__":
    main()
