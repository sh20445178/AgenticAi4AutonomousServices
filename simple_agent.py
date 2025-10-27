#!/usr/bin/env python3
"""
Simple Gemini AI Agent using only standard library + requests
No external dependencies except requests (which is usually available)
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import requests
except ImportError:
    print("Error: requests library is required. Install with: pip install requests")
    sys.exit(1)

class SimpleGeminiAgent:
    """Simple AI Agent using Google Gemini API with minimal dependencies"""
    
    def __init__(self, api_key: str = None):
        """Initialize the agent
        
        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Set GOOGLE_API_KEY environment variable or pass it directly.")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-pro"
        self.conversation_history: List[Dict[str, Any]] = []
        
        print(f"✅ Simple Gemini Agent initialized with model: {self.model}")
    
    def _make_request(self, message: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Make request to Gemini API"""
        url = f"{self.base_url}/{self.model}:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': self.api_key
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": message
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    return "Error: No response generated"
            else:
                return f"API Error {response.status_code}: {response.text}"
                
        except requests.exceptions.RequestException as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat(self, message: str, include_history: bool = True) -> str:
        """Chat with the AI agent"""
        print(f"🤖 Processing: {message[:50]}...")
        
        # Prepare message with context if requested
        if include_history and self.conversation_history:
            context_messages = []
            for entry in self.conversation_history[-5:]:  # Last 5 messages
                role = "Human" if entry['role'] == 'user' else "Assistant"
                context_messages.append(f"{role}: {entry['content']}")
            
            context = "\n".join(context_messages)
            full_message = f"Previous conversation:\n{context}\n\nCurrent message: {message}"
        else:
            full_message = message
        
        # Get response
        response = self._make_request(full_message)
        
        # Add to history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'role': 'user',
            'content': message
        })
        
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'role': 'assistant',
            'content': response
        })
        
        # Keep history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return response
    
    def save_conversation(self, filename: str = None) -> str:
        """Save conversation to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simple_conversation_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            return filename
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return None
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        print("🧹 Conversation history cleared")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        return {
            'total_messages': len(self.conversation_history),
            'user_messages': len([msg for msg in self.conversation_history if msg['role'] == 'user']),
            'assistant_messages': len([msg for msg in self.conversation_history if msg['role'] == 'assistant']),
            'start_time': self.conversation_history[0]['timestamp'] if self.conversation_history else None,
            'model': self.model
        }

def interactive_mode():
    """Run interactive chat mode"""
    print("🚀 Starting Simple Gemini AI Agent")
    print("=" * 40)
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        api_key = input("Enter your Google Gemini API key: ").strip()
        if not api_key:
            print("❌ API key is required!")
            return
    
    try:
        agent = SimpleGeminiAgent(api_key)
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return
    
    print("💬 Type your messages (or 'quit' to exit)")
    print("📝 Commands: 'clear', 'summary', 'save'")
    print("-" * 40)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                # Save conversation before exit
                filename = agent.save_conversation()
                if filename:
                    print(f"💾 Conversation saved to: {filename}")
                print("👋 Goodbye!")
                break
            
            elif user_input.lower() == 'clear':
                agent.clear_history()
                continue
            
            elif user_input.lower() == 'summary':
                summary = agent.get_summary()
                print("📊 Summary:")
                for key, value in summary.items():
                    print(f"  {key}: {value}")
                continue
            
            elif user_input.lower() == 'save':
                filename = agent.save_conversation()
                if filename:
                    print(f"💾 Conversation saved to: {filename}")
                continue
            
            # Get AI response
            response = agent.chat(user_input)
            print(f"\n🤖 AI: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def simple_test():
    """Simple test function"""
    print("🧪 Running simple test...")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Set GOOGLE_API_KEY environment variable for testing")
        return
    
    try:
        agent = SimpleGeminiAgent(api_key)
        
        # Test basic functionality
        response = agent.chat("Hello! Please respond with 'Test successful' if you can hear me.")
        print(f"📤 Test message: Hello! Please respond with 'Test successful' if you can hear me.")
        print(f"📥 Response: {response}")
        
        # Test summary
        summary = agent.get_summary()
        print(f"📊 Summary: {summary}")
        
        print("✅ Simple test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        simple_test()
    else:
        interactive_mode()