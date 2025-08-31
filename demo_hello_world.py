#!/usr/bin/env python3
"""
Beautiful Streamlit Hello World Demo
SMP-7: AstraSprint AI Auto Test Implementation
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_animated_chart(points: int = 100) -> go.Figure:
    """
    Create beautiful animated visualization.
    
    Args:
        points: Number of points to generate (default: 100)
        
    Returns:
        Plotly figure object
        
    Raises:
        ValueError: If points is not a positive integer
    """
    if not isinstance(points, int) or points <= 0:
        raise ValueError("Points must be a positive integer")
    
    if points > 1000:  # Prevent excessive memory usage
        logger.warning(f"Large point count ({points}) may impact performance")
        points = min(points, 1000)
    
    try:
        t = np.linspace(0, 2*np.pi, points)
        x = np.cos(t)
        y = np.sin(t)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines+markers',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8, color='#4ECDC4'),
            name='Hello World Curve'
        ))
        
        fig.update_layout(
            title="🌟 Beautiful Hello World Visualization",
            xaxis_title="X축",
            yaxis_title="Y축",
            template="plotly_dark",
            height=400,
            showlegend=True
        )
        
        logger.debug(f"Created chart with {points} points")
        return fig
        
    except Exception as e:
        logger.error(f"Failed to create chart: {e}")
        # Return a simple fallback chart
        fig = go.Figure()
        fig.add_annotation(text="Chart creation failed", x=0.5, y=0.5)
        return fig

def main():
    """Main Streamlit application with enhanced error handling"""
    try:
        # Page config
        st.set_page_config(
            page_title="Hello World Demo",
            page_icon="🌟",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS with security considerations
        st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            color: #FF6B6B;
            text-align: center;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .sub-header {
            font-size: 1.5rem;
            color: #4ECDC4;
            text-align: center;
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown('<h1 class="main-header">🌟 Hello World! 안녕하세요! 🌟</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Beautiful Streamlit Demo - SMP-7 Implementation</p>', unsafe_allow_html=True)
        
        # Sidebar with validation
        with st.sidebar:
            st.header("🎨 Demo Controls")
            language = st.selectbox("언어 / Language", ["한국어", "English"])
            show_chart = st.checkbox("차트 표시 / Show Chart", value=True)
            animation_speed = st.slider("Animation Speed", 1, 10, 5)
        
        # Main content
        col1, col2 = st.columns(2)
        
        with col1:
            if language == "한국어":
                st.subheader("🚀 프로젝트 정보")
                st.info("골프 스윙 3D 분석기 프로젝트의 아름다운 데모입니다!")
                st.success("✅ Streamlit 데모가 성공적으로 실행되었습니다!")
            else:
                st.subheader("🚀 Project Information")
                st.info("Beautiful demo for Golf Swing 3D Analyzer project!")
                st.success("✅ Streamlit demo is running successfully!")
            
            # Interactive elements with input validation
            user_name = st.text_input("이름을 입력하세요 / Enter your name:", "World", max_chars=50)
            # Sanitize user input
            user_name = user_name.strip()[:50] if user_name else "World"
            
            if st.button("🎉 Say Hello!"):
                st.balloons()
                # Escape user input for security
                safe_name = st.text(user_name)  # This automatically escapes HTML
                st.write(f"### Hello, {user_name}! 안녕하세요, {user_name}님!")
        
        with col2:
            if show_chart:
                st.subheader("📊 Interactive Visualization")
                try:
                    # Use animation_speed to adjust chart complexity
                    points = min(50 + animation_speed * 10, 200)
                    fig = create_animated_chart(points)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Chart creation failed: {e}")
                    logger.error(f"Chart error: {e}")
            
            # Status info
            st.subheader("📋 System Status")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.metric("Current Time", current_time)
            st.metric("Demo Status", "Active", delta="Running")
        
        # Footer
        st.markdown("---")
        st.markdown(
            "**SMP-7 Implementation** | "
            "🏌️ Golf Swing 3D Analyzer | "
            f"⏰ Last updated: {current_time}"
        )
        
        logger.info(f"Demo accessed at {current_time}")
        
    except Exception as e:
        st.error("An error occurred while loading the demo")
        logger.error(f"Demo error: {e}")
        st.exception(e)  # Show detailed error in development

if __name__ == "__main__":
    main()
