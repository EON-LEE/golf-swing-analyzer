#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hello World Chat Application - SMP-7 Implementation
A simple Streamlit-based chat interface with intentional bugs for testing.
"""

import streamlit as st
import time
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_animated_chart() -> plt.Figure:
    """
    Create a simple animated chart for testing purposes.
    
    Returns:
        matplotlib.pyplot.Figure: A figure containing a sine wave plot
        
    Raises:
        RuntimeError: If chart creation fails
    """
    try:
        fig, ax = plt.subplots(figsize=(8, 6))
        x = np.linspace(0, 2*np.pi, 100)
        y = np.sin(x)
        ax.plot(x, y, 'b-', linewidth=2)
        ax.set_title("Simple Sine Wave", fontsize=14)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.grid(True, alpha=0.3)
        return fig
    except Exception as e:
        logger.error(f"Failed to create chart: {e}")
        raise RuntimeError(f"Chart creation failed: {e}") from e

def generate_response(prompt: str) -> str:
    """
    Generate appropriate response based on user input.
    
    Args:
        prompt: User input message
        
    Returns:
        str: Generated response message
    """
    prompt_lower = prompt.lower().strip()
    
    if "hello" in prompt_lower:
        return "Hello there! How are you?"
    elif "bye" in prompt_lower or "goodbye" in prompt_lower:
        return "Goodbye! See you later!"
    elif "how are you" in prompt_lower:
        return "I'm doing great, thank you for asking!"
    elif "help" in prompt_lower:
        return "I can respond to greetings like 'hello' and 'bye'. Try saying hello!"
    else:
        return "I heard you! Thanks for your message."


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        logger.info("Initialized session state with empty messages list")


def display_chat_messages() -> None:
    """Display all chat messages in the correct chronological order."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(prompt: str) -> None:
    """
    Process user input and generate response.
    
    Args:
        prompt: User input message
    """
    if not prompt.strip():
        st.warning("Please enter a message.")
        return
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and add response
    response = generate_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
        
    with st.chat_message("assistant"):
        st.markdown(response)
    
    logger.info(f"Processed message: {prompt[:50]}...")


def render_sidebar() -> None:
    """Render sidebar with chat controls and statistics."""
    with st.sidebar:
        st.header("Chat Settings")
        
        # Clear chat functionality
        if st.button("Clear Chat", type="primary"):
            st.session_state.messages = []
            st.rerun()
            logger.info("Chat cleared by user")
        
        # Chat statistics
        st.subheader("Statistics")
        message_count = len(st.session_state.messages)
        user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
        assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        
        st.metric("Total messages", message_count)
        st.metric("Your messages", user_messages)
        st.metric("Bot responses", assistant_messages)
        
        # Last message preview
        st.subheader("Last Message")
        if st.session_state.messages:
            last_message = st.session_state.messages[-1]
            role = "You" if last_message["role"] == "user" else "Bot"
            content = last_message["content"]
            preview = content[:30] + "..." if len(content) > 30 else content
            st.write(f"**{role}:** {preview}")
        else:
            st.write("No messages yet")


def main() -> None:
    """
    Main function to run the Streamlit chat application.
    
    This function initializes the app, handles user interactions,
    and manages the chat interface.
    """
    try:
        # Page configuration
        st.set_page_config(
            page_title="Hello World Chat",
            page_icon="🌍",
            layout="centered"
        )
        
        # Initialize session state
        initialize_session_state()
        
        # Main interface
        st.title("Hello World Chat App 🌍")
        st.write("Welcome to our simple chat application! Say hello to get started.")
        
        # Display existing messages
        display_chat_messages()
        
        # Handle new user input
        if prompt := st.chat_input("Say hello..."):
            handle_user_input(prompt)
        
        # Render sidebar
        render_sidebar()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An error occurred. Please refresh the page.")
        raise


if __name__ == "__main__":
    main()
