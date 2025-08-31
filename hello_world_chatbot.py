"""
Hello World Chatbot - Streamlit Application
A simple chatbot that responds to basic greetings in Korean and English.
"""

import streamlit as st
from typing import Dict, List, Optional
import logging
import re

from config import (
    GREETING_KEYWORDS, FAREWELL_KEYWORDS, RESPONSES, 
    APP_CONFIG, PREVIEW_MAX_LENGTH, MAX_MESSAGE_LENGTH, MAX_MESSAGES_HISTORY,
    ALLOWED_CHARS_PATTERN
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_session_state() -> None:
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []


def get_bot_response(user_input: str) -> str:
    """
    Generate bot response based on user input.
    
    Args:
        user_input: User's message string
        
    Returns:
        Bot's response string
    """
    if not isinstance(user_input, str):
        logger.warning(f"Invalid input type: {type(user_input)}")
        return RESPONSES["default"]
    
    # Sanitize input once
    user_input_clean = user_input.lower().strip()
    
    if not user_input_clean:
        return RESPONSES["default"]
    
    # Check farewell first (more specific than greeting for "안녕")
    for farewell in FAREWELL_KEYWORDS:
        if farewell in user_input_clean:
            return RESPONSES["farewell"]
    
    # Check greetings
    for greeting in GREETING_KEYWORDS:
        if greeting in user_input_clean:
            return RESPONSES["greeting"]
    
    return RESPONSES["default"]


def render_sidebar() -> None:
    """Render sidebar with chat controls and statistics."""
    with st.sidebar:
        st.header(APP_CONFIG["sidebar_header"])
        
        # Clear chat button
        if st.button(APP_CONFIG["clear_button_text"], type="primary"):
            st.session_state.messages = []
            st.rerun()
        
        # Message statistics
        message_count = len(st.session_state.messages)
        st.metric(APP_CONFIG["message_count_label"], message_count)
        
        # Last message preview
        if st.session_state.messages:
            try:
                last_msg = st.session_state.messages[-1].get("content", "")
                if last_msg:
                    preview = (last_msg[:PREVIEW_MAX_LENGTH] + "..." 
                             if len(last_msg) > PREVIEW_MAX_LENGTH else last_msg)
                    st.info(f"{APP_CONFIG['last_message_label']}: {preview}")
            except (IndexError, KeyError, AttributeError) as e:
                logger.error(f"Error displaying last message: {e}")
                st.warning(APP_CONFIG["error_message"])


def render_chat_messages() -> None:
    """Render all chat messages in chronological order."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def validate_user_input(prompt: str) -> Optional[str]:
    """
    Validate user input and return error message if invalid.
    
    Args:
        prompt: User input string
        
    Returns:
        Error message if invalid, None if valid
    """
    if not prompt or not prompt.strip():
        return APP_CONFIG["empty_message_warning"]
    
    cleaned_prompt = prompt.strip()
    
    if len(cleaned_prompt) > MAX_MESSAGE_LENGTH:
        return f"메시지가 너무 깁니다. {MAX_MESSAGE_LENGTH}자 이하로 입력해주세요."
    
    # Check for suspicious patterns (basic security)
    if re.search(r'<script|javascript:|data:', cleaned_prompt, re.IGNORECASE):
        return "허용되지 않는 내용이 포함되어 있습니다."
    
    return None


def add_message_safely(role: str, content: str) -> bool:
    """
    Safely add message to session state with history management.
    
    Args:
        role: Message role (user/assistant)
        content: Message content
        
    Returns:
        True if successful, False otherwise
    """
    try:
        st.session_state.messages.append({"role": role, "content": content})
        
        # Manage message history to prevent memory issues
        if len(st.session_state.messages) > MAX_MESSAGES_HISTORY:
            st.session_state.messages = st.session_state.messages[-MAX_MESSAGES_HISTORY:]
            
        return True
    except Exception as e:
        logger.error(f"Error adding message: {e}")
        return False


def main() -> None:
    """Main application function."""
    try:
        # Page configuration
        st.set_page_config(
            page_title=APP_CONFIG["title"],
            page_icon=APP_CONFIG["page_icon"],
            layout=APP_CONFIG["layout"]
        )
        
        st.title(APP_CONFIG["title"])
        st.caption(APP_CONFIG["caption"])
        
        # Initialize application state
        initialize_session_state()
        
        # Render UI components
        render_sidebar()
        render_chat_messages()
        
        # Handle user input
        if prompt := st.chat_input(APP_CONFIG["input_placeholder"]):
            # Validate input
            error_msg = validate_user_input(prompt)
            if error_msg:
                st.warning(error_msg)
                return
                
            # Add user message
            if not add_message_safely("user", prompt):
                st.error("메시지 저장 중 오류가 발생했습니다.")
                return
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and add bot response
            response = get_bot_response(prompt)
            if not add_message_safely("assistant", response):
                st.error("응답 저장 중 오류가 발생했습니다.")
                return
            
            with st.chat_message("assistant"):
                st.markdown(response)
                
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("애플리케이션 오류가 발생했습니다. 페이지를 새로고침해주세요.")


if __name__ == "__main__":
    main()
