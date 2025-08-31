"""
Hello World Chatbot - Streamlit Application
A simple chatbot that responds to basic greetings in Korean and English.
"""

import streamlit as st
from typing import Dict, List

# Configuration constants
APP_CONFIG: Dict[str, str] = {
    "title": "Hello World Chatbot",
    "page_icon": "🤖",
    "layout": "centered",
    "caption": "A simple greeting chatbot supporting Korean and English",
    "sidebar_header": "Chat Controls",
    "clear_button_text": "Clear Chat",
    "message_count_label": "Messages",
    "last_message_label": "Last Message",
    "input_placeholder": "Type your message here...",
    "empty_message_warning": "Please enter a message",
    "error_message": "Error displaying message"
}

GREETING_KEYWORDS: List[str] = ["hello", "hi", "hey", "안녕", "안녕하세요"]
FAREWELL_KEYWORDS: List[str] = ["bye", "goodbye", "see you", "안녕히", "잘가"]

RESPONSES: Dict[str, str] = {
    "greeting": "Hello! How can I help you today? 안녕하세요!",
    "farewell": "Goodbye! Have a great day! 안녕히 가세요!",
    "default": "I'm a simple chatbot. Try saying hello or goodbye!"
}

PREVIEW_MAX_LENGTH: int = 50


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
    user_input_lower = user_input.lower().strip()
    
    # Farewell responses (check first to avoid conflict with "안녕")
    if any(farewell in user_input_lower for farewell in FAREWELL_KEYWORDS):
        return RESPONSES["farewell"]
    
    # Greeting responses
    elif any(greeting in user_input_lower for greeting in GREETING_KEYWORDS):
        return RESPONSES["greeting"]
    
    # Default response
    else:
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
                last_msg = st.session_state.messages[-1]["content"]
                preview = last_msg[:PREVIEW_MAX_LENGTH] + "..." if len(last_msg) > PREVIEW_MAX_LENGTH else last_msg
                st.info(f"{APP_CONFIG['last_message_label']}: {preview}")
            except (IndexError, KeyError, TypeError):
                st.warning(APP_CONFIG["error_message"])


def render_chat_messages() -> None:
    """Render all chat messages in chronological order."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


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
            prompt = prompt.strip()
            if not prompt:
                st.warning(APP_CONFIG["empty_message_warning"])
                return
                
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and add bot response
            response = get_bot_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            with st.chat_message("assistant"):
                st.markdown(response)
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please refresh the page and try again.")


if __name__ == "__main__":
    main()
