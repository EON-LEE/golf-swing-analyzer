package com.chatbot;

import com.chatbot.service.ChatService;
import com.chatbot.config.ChatConfig;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.web.util.HtmlUtils;
import org.springframework.validation.annotation.Validated;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import jakarta.validation.ConstraintViolationException;

@Controller
@Validated
public class ChatController {
    
    private static final Logger logger = LoggerFactory.getLogger(ChatController.class);
    
    private final ChatService chatService;
    private final ChatConfig chatConfig;
    
    @Autowired
    public ChatController(ChatService chatService, ChatConfig chatConfig) {
        this.chatService = chatService;
        this.chatConfig = chatConfig;
    }
    
    @GetMapping("/")
    public String chat() {
        return "chat";
    }
    
    @PostMapping("/message")
    @ResponseBody
    public ResponseEntity<String> processMessage(
            @RequestParam 
            @NotBlank(message = "메시지를 입력해주세요. Please enter a message.")
            @Size(max = 500, message = "메시지가 너무 깁니다. Message too long.")
            String message) {
        
        try {
            String sanitizedMessage = HtmlUtils.htmlEscape(message.trim());
            
            if (chatConfig.isEnableLogging()) {
                logger.info("Processing message: {}", sanitizedMessage);
            }
            
            String response = chatService.processMessage(sanitizedMessage);
            return ResponseEntity.ok(response);
            
        } catch (ConstraintViolationException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        } catch (Exception e) {
            logger.error("Error processing message: {}", message, e);
            return ResponseEntity.internalServerError()
                .body("오류가 발생했습니다. An error occurred.");
        }
    }
}
