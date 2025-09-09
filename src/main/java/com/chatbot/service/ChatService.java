package com.chatbot.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import java.util.Map;
import java.util.HashMap;
import java.util.regex.Pattern;

@Service
public class ChatService {
    
    private final Map<String, String> responses;
    private final Pattern greetingPattern;
    private final Pattern farewellPattern;
    private final Pattern helpPattern;
    
    @Value("${chatbot.responses.greeting:안녕하세요! Hello! 👋}")
    private String greetingResponse;
    
    @Value("${chatbot.responses.farewell:안녕히 가세요! Goodbye! 👋}")
    private String farewellResponse;
    
    @Value("${chatbot.responses.help:도움말: 안녕, hello, 잘가, bye, 도움, help}")
    private String helpResponse;
    
    @Value("${chatbot.responses.default:죄송해요, 이해하지 못했어요. Sorry, I didn't understand.}")
    private String defaultResponse;
    
    public ChatService() {
        responses = new HashMap<>();
        greetingPattern = Pattern.compile("\\b(안녕|hello|hi|hey)\\b", Pattern.CASE_INSENSITIVE);
        farewellPattern = Pattern.compile("\\b(잘가|bye|goodbye|farewell)\\b", Pattern.CASE_INSENSITIVE);
        helpPattern = Pattern.compile("\\b(도움|help|\\?)\\b", Pattern.CASE_INSENSITIVE);
    }
    
    public String processMessage(String message) {
        if (message == null || message.trim().isEmpty()) {
            return defaultResponse;
        }
        
        String normalizedMessage = message.toLowerCase().trim();
        
        if (greetingPattern.matcher(normalizedMessage).find()) {
            return greetingResponse;
        } else if (farewellPattern.matcher(normalizedMessage).find()) {
            return farewellResponse;
        } else if (helpPattern.matcher(normalizedMessage).find()) {
            return helpResponse;
        }
        
        return defaultResponse;
    }
}
