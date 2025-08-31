# Hello World Chatbot

A simple conversational chatbot built with Streamlit that responds to greetings and farewells in both Korean and English.

## Features

- **Bilingual Support**: Responds to greetings in Korean and English
- **Interactive Chat Interface**: Clean, user-friendly Streamlit interface
- **Chat History**: Maintains conversation history during the session
- **Smart Responses**: Context-aware responses for greetings, farewells, and general queries
- **Session Management**: Clear chat functionality and message statistics

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup
1. Install required dependencies:
```bash
pip install streamlit
```

2. Clone or download the project files to your local directory

## Usage

### Running the Application
```bash
streamlit run hello_world_chatbot.py
```

The application will start and open in your default web browser at `http://localhost:8501`

### Interacting with the Chatbot

The chatbot recognizes various types of input:

**Greetings** (Korean/English):
- 안녕하세요, 안녕, 하이, 헬로, hello, hi, hey

**Farewells** (Korean/English):
- 안녕히 가세요, 잘 가요, 바이, goodbye, bye, see you

**General Queries**:
- Any other input will receive a helpful default response

### Interface Features

- **Chat Input**: Type your message in the input field at the bottom
- **Chat History**: View all previous messages in the conversation
- **Sidebar Controls**: 
  - Clear chat history
  - View message count
  - See timestamp of last message

## Project Structure

```
SMP-4/
├── hello_world_chatbot.py    # Main application file
└── README.md                 # This documentation
```

## Technical Details

- **Framework**: Streamlit for web interface
- **Language**: Python 3.7+
- **Dependencies**: streamlit, typing (built-in)
- **Architecture**: Single-file application with modular functions

## Troubleshooting

**Common Issues:**

1. **Import Error**: Ensure Streamlit is installed
   ```bash
   pip install streamlit
   ```

2. **Port Already in Use**: If port 8501 is busy, Streamlit will automatically use the next available port

3. **Browser Not Opening**: Manually navigate to the URL shown in the terminal

## License

This project is provided as-is for educational and demonstration purposes.
