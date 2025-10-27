import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai package not installed. Run: pip install -r requirements.txt")
    exit(1)

from config import config
from utils import setup_logging, print_colored, format_response, truncate_text

class GeminiAgent:
    """AI Agent powered by Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini Agent
        
        Args:
            api_key: Optional API key override. If not provided, uses config.
        """
        self.api_key = api_key or config.google_api_key
        self.model_name = config.model_name
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature
        
        # Setup logging
        self.logger = setup_logging(config.debug)
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        try:
            self.model = genai.GenerativeModel(self.model_name)
            self.logger.info(f"Initialized Gemini model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize model: {e}")
            raise
        
        # Conversation history
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Generation config
        self.generation_config = genai.types.GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )
    
    def add_to_history(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add message to conversation history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'content': content,
            'metadata': metadata or {}
        }
        self.conversation_history.append(entry)
        
        # Keep history manageable (last 50 messages)
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def chat(self, message: str, include_history: bool = True) -> str:
        """Send a message to Gemini and get response
        
        Args:
            message: User message
            include_history: Whether to include conversation context
            
        Returns:
            AI response text
        """
        try:
            # Log the user message
            self.logger.info(f"User message: {truncate_text(message)}")
            
            # Prepare context if requested
            if include_history and self.conversation_history:
                # Build context from recent conversation
                context_messages = []
                for entry in self.conversation_history[-10:]:  # Last 10 messages
                    role = "Human" if entry['role'] == 'user' else "Assistant"
                    context_messages.append(f"{role}: {entry['content']}")
                
                context = "\n".join(context_messages)
                full_message = f"Context:\n{context}\n\nCurrent message: {message}"
            else:
                full_message = message
            
            # Generate response
            response = self.model.generate_content(
                full_message,
                generation_config=self.generation_config
            )
            
            # Extract response text
            response_text = response.text if response.text else "I couldn't generate a response."
            
            # Add to history
            self.add_to_history('user', message)
            self.add_to_history('assistant', response_text, {
                'model': self.model_name,
                'temperature': self.temperature,
                'max_tokens': self.max_tokens
            })
            
            self.logger.info(f"Generated response: {truncate_text(response_text)}")
            
            return response_text
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.logger.error(error_msg)
            return f"I encountered an error: {str(e)}"
    
    async def chat_async(self, message: str, include_history: bool = True) -> str:
        """Async version of chat method"""
        # For now, run the sync version in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.chat, message, include_history)
    
    def chat_stream(self, message: str, include_history: bool = True):
        """Stream response from Gemini (generator)"""
        try:
            # Prepare message with context
            if include_history and self.conversation_history:
                context_messages = []
                for entry in self.conversation_history[-10:]:
                    role = "Human" if entry['role'] == 'user' else "Assistant"
                    context_messages.append(f"{role}: {entry['content']}")
                
                context = "\n".join(context_messages)
                full_message = f"Context:\n{context}\n\nCurrent message: {message}"
            else:
                full_message = message
            
            # Generate streaming response
            response = self.model.generate_content(
                full_message,
                generation_config=self.generation_config,
                stream=True
            )
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text
            
            # Add to history after streaming is complete
            self.add_to_history('user', message)
            self.add_to_history('assistant', full_response)
            
        except Exception as e:
            error_msg = f"Error in streaming: {str(e)}"
            self.logger.error(error_msg)
            yield f"Error: {str(e)}"
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        self.logger.info("Conversation history cleared")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        return {
            'total_messages': len(self.conversation_history),
            'user_messages': len([msg for msg in self.conversation_history if msg['role'] == 'user']),
            'assistant_messages': len([msg for msg in self.conversation_history if msg['role'] == 'assistant']),
            'start_time': self.conversation_history[0]['timestamp'] if self.conversation_history else None,
            'last_message_time': self.conversation_history[-1]['timestamp'] if self.conversation_history else None,
            'model_used': self.model_name,
            'settings': {
                'temperature': self.temperature,
                'max_tokens': self.max_tokens
            }
        }
    
    def save_conversation(self, filename: str = None) -> str:
        """Save conversation to file"""
        from utils import save_conversation
        return save_conversation(self.conversation_history, filename)
    
    def load_conversation(self, filename: str):
        """Load conversation from file"""
        from utils import load_conversation
        self.conversation_history = load_conversation(filename)

if __name__ == "__main__":
    # Simple test
    try:
        agent = GeminiAgent()
        print_colored("Gemini Agent initialized successfully!", 'green')
        
        response = agent.chat("Hello! Can you introduce yourself?")
        print_colored(f"Response: {response}", 'blue')
        
    except Exception as e:
        print_colored(f"Error: {e}", 'red')