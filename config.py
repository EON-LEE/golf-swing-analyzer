"""
Configuration settings for Hello World Chatbot
"""

from typing import Dict, List

# Bot response configurations
GREETING_KEYWORDS: List[str] = ["hello", "hi", "안녕"]
FAREWELL_KEYWORDS: List[str] = ["bye", "goodbye", "잘가", "안녕히"]

RESPONSES: Dict[str, str] = {
    "greeting": "Hello World! 안녕하세요!",
    "farewell": "Goodbye! 안녕히 가세요!",
    "default": "죄송해요, 이해하지 못했어요."
}

# UI Configuration
APP_CONFIG: Dict[str, str] = {
    "title": "Hello World 채팅봇",
    "page_icon": "💬",
    "layout": "centered",
    "caption": "간단한 인사말 채팅봇입니다.",
    "input_placeholder": "메시지를 입력하세요...",
    "clear_button_text": "채팅 클리어",
    "sidebar_header": "설정",
    "message_count_label": "메시지 수",
    "last_message_label": "마지막 메시지",
    "empty_message_warning": "빈 메시지는 보낼 수 없습니다.",
    "error_message": "마지막 메시지: 오류 발생"
}

# Message preview settings
PREVIEW_MAX_LENGTH: int = 20
