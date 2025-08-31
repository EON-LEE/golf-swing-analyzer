# Hello World Chatbot

A simple Streamlit-based chatbot that responds to basic greetings in Korean and English.

## Features

- Bilingual support (English and Korean)
- Interactive chat interface
- Message history with statistics
- Clear chat functionality
- Responsive design

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:
   ```bash
   pip install streamlit
   ```

## Usage

Run the application:
```bash
streamlit run hello_world_chatbot.py
```

The chatbot will open in your default web browser at `http://localhost:8501`.

## Supported Commands

- **Greetings**: hello, hi, hey, 안녕, 안녕하세요
- **Farewells**: bye, goodbye, see you, 안녕히, 잘가
- **Other messages**: Receives a default response

## Project Structure

```
SMP-4/
├── hello_world_chatbot.py    # Main application file
└── README.md                 # This file
```

## Dependencies

- `streamlit`: Web application framework
- `typing`: Type hints (built-in Python module)
