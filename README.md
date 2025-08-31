# Hello World Chatbot

A simple bilingual chatbot built with Streamlit that responds to greetings in Korean and English.

## Features

- **Bilingual Support**: Responds to greetings in both Korean and English
- **Interactive UI**: Clean Streamlit interface with chat functionality
- **Session Management**: Maintains chat history during the session
- **Chat Controls**: Clear chat history and view message statistics
- **Error Handling**: Comprehensive error handling and user feedback

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

1. Clone or download the project files
2. Install required dependencies:
   ```bash
   pip install streamlit
   ```

## Usage

### Running the Application

1. Navigate to the project directory:
   ```bash
   cd /path/to/hello_world_chatbot
   ```

2. Start the Streamlit application:
   ```bash
   streamlit run hello_world_chatbot.py
   ```

3. Open your web browser and go to the displayed URL (typically `http://localhost:8501`)

### Interacting with the Chatbot

- **Greetings**: Try saying "hello", "hi", "hey", "안녕", or "안녕하세요"
- **Farewells**: Try saying "bye", "goodbye", "see you", "안녕히", or "잘가"
- **Other messages**: The bot will provide a default response

### Chat Controls

- **Clear Chat**: Use the sidebar button to clear all messages
- **Message Count**: View the total number of messages in the sidebar
- **Last Message Preview**: See a preview of the most recent message

## Project Structure

```
hello_world_chatbot.py    # Main application file
README.md                 # This documentation file
```

## Configuration

The application uses configurable constants for easy customization:

- **APP_CONFIG**: UI text and settings
- **GREETING_KEYWORDS**: Words that trigger greeting responses
- **FAREWELL_KEYWORDS**: Words that trigger farewell responses
- **RESPONSES**: Bot response templates

## Technical Details

- **Framework**: Streamlit for web interface
- **Language**: Python 3.7+
- **Dependencies**: streamlit, typing (built-in)
- **Architecture**: Single-file application with modular functions

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure Streamlit is installed with `pip install streamlit`
2. **Port Already in Use**: Streamlit will automatically find an available port
3. **Browser Not Opening**: Manually navigate to the URL shown in the terminal

### Error Messages

The application includes comprehensive error handling and will display helpful messages for common issues.

## License

This project is provided as-is for educational and demonstration purposes.
