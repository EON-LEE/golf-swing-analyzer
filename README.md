# Hello World Chatbot

A simple bilingual chatbot built with Streamlit that responds to greetings in Korean and English.

## Features

- **Bilingual Support**: Responds to greetings in both Korean and English
- **Interactive UI**: Clean Streamlit interface with chat functionality
- **Chat History**: Maintains conversation history during the session
- **Sidebar Controls**: Clear chat and view message statistics
- **Real-time Responses**: Instant bot responses to user input

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:
   ```bash
   pip install streamlit
   ```

## Usage

1. Run the application:
   ```bash
   streamlit run hello_world_chatbot.py
   ```

2. Open your browser to the displayed URL (typically `http://localhost:8501`)

3. Start chatting! Try these examples:
   - English: "Hello", "Hi", "Hey", "Goodbye", "Bye", "Help"
   - Korean: "안녕", "안녕하세요", "안녕히", "잘가", "도움"

## Supported Commands

- **Greetings**: hello, hi, hey, 안녕, 안녕하세요
- **Farewells**: bye, goodbye, see you, 안녕히, 잘가
- **Help**: help, 도움, commands, 명령어
- **Other**: Any other input receives a default response

## Project Structure

```
SMP-4/
├── hello_world_chatbot.py    # Main Streamlit application
└── README.md                 # Project documentation
```
