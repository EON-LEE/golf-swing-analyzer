# Hello World Chatbot (Java)

A simple bilingual chatbot built with Spring Boot that responds to greetings in Korean and English.

## Features

- **Bilingual Support**: Responds to greetings in both Korean and English
- **Interactive UI**: Clean web interface with chat functionality
- **Chat History**: Maintains conversation history during the session
- **Real-time Responses**: Instant bot responses to user input

## Installation

1. Install Java 17 or higher
2. Install Maven 3.6 or higher

## Usage

1. Run the application:
   ```bash
   mvn spring-boot:run
   ```

2. Open your browser to `http://localhost:8080`

3. Start chatting! Try these examples:
   - English: "Hello", "Hi", "Goodbye", "Bye", "Help"
   - Korean: "안녕", "안녕하세요", "잘가", "도움"

## Supported Commands

- **Greetings**: hello, hi, 안녕, 안녕하세요
- **Farewells**: bye, goodbye, 잘가
- **Help**: help, 도움
- **Other**: Any other input receives a default response

## Project Structure

```
SMP-7/
├── src/main/java/com/chatbot/
│   ├── ChatbotApplication.java    # Main Spring Boot application
│   └── ChatController.java        # Chat controller
├── src/main/resources/
│   ├── templates/chat.html        # Chat interface
│   └── static/css/style.css       # Styles
├── pom.xml                        # Maven configuration
└── README.md                      # Project documentation
```

## Build

```bash
mvn clean package
java -jar target/hello-world-chatbot-1.0.0.jar
```
