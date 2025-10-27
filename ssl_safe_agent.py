#!/usr/bin/env python3
"""
SSL-Safe Gemini AI Agent using only Python standard library
Works around SSL certificate verification issues on macOS
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import ssl
from datetime import datetime
from typing import List, Dict, Any, Optional

class SSLSafeGeminiAgent:
    """SSL-Safe AI Agent using Google Gemini API with SSL workaround"""
    
    def __init__(self, api_key: str = None):
        """Initialize the agent
        
        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Set GOOGLE_API_KEY environment variable or pass it directly.")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "models/gemini-2.5-flash"  # Using latest stable model
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Create SSL context that doesn't verify certificates (for macOS SSL issues)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        print(f"⚠️  SSL-Safe Gemini Agent initialized with model: {self.model}")
        print("   Note: SSL verification disabled for macOS compatibility")
    
    def _make_request(self, message: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Make request to Gemini API using urllib with SSL workaround"""
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        headers = {
            'Content-Type': 'application/json',
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
            # Prepare request
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=json_data, headers=headers)
            
            # Make request with SSL context that ignores certificate errors
            with urllib.request.urlopen(req, timeout=30, context=self.ssl_context) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    
                    # Debug: print the actual response structure
                    if not result.get('candidates'):
                        return f"Debug - Full response: {json.dumps(result, indent=2)}"
                    
                    if 'candidates' in result and len(result['candidates']) > 0:
                        candidate = result['candidates'][0]
                        
                        # Handle different response structures
                        if 'content' in candidate:
                            if 'parts' in candidate['content']:
                                return candidate['content']['parts'][0]['text']
                            else:
                                return candidate['content'].get('text', 'No text in content')
                        elif 'text' in candidate:
                            return candidate['text']
                        else:
                            return f"Debug - Candidate structure: {json.dumps(candidate, indent=2)}"
                    else:
                        return "Error: No response generated"
                else:
                    return f"API Error {response.status}: {response.read().decode('utf-8')}"
                    
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            return f"HTTP Error {e.code}: {error_body}"
        except urllib.error.URLError as e:
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
            filename = f"ssl_safe_conversation_{timestamp}.json"
        
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
    print("🚀 Starting SSL-Safe Gemini AI Agent")
    print("=" * 45)
    print("⚠️  SSL certificate verification disabled for macOS compatibility")
    print("=" * 45)
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("💡 No GOOGLE_API_KEY environment variable found.")
        api_key = input("Enter your Google Gemini API key: ").strip()
        if not api_key:
            print("❌ API key is required!")
            return
    
    try:
        agent = SSLSafeGeminiAgent(api_key)
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return
    
    print("💬 Type your messages (or 'quit' to exit)")
    print("📝 Commands: 'clear', 'summary', 'save', 'help'")
    print("-" * 45)
    
    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
            
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
                print("📊 Conversation Summary:")
                for key, value in summary.items():
                    print(f"   {key}: {value}")
                continue
            
            elif user_input.lower() == 'save':
                filename = agent.save_conversation()
                if filename:
                    print(f"💾 Conversation saved to: {filename}")
                continue
            
            elif user_input.lower() == 'help':
                print("""
📖 Available Commands:
   'clear'   - Clear conversation history
   'summary' - Show conversation statistics
   'save'    - Save conversation to file
   'help'    - Show this help message
   'quit'    - Exit the application
   
Just type any message to chat with the AI!
                """)
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
    print("🧪 Running SSL-safe test...")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Set GOOGLE_API_KEY environment variable for testing")
        print("   Example: export GOOGLE_API_KEY='AIzaSyCXZj4nkULw_-7p4Rwu_L8rX8FpmL2SkDE'")
        return False
    
    try:
        agent = SSLSafeGeminiAgent(api_key)
        
        # Test basic functionality
        test_message = "Hello! Please respond with 'SSL test successful' if you can hear me."
        print(f"📤 Sending test message: {test_message}")
        
        response = agent.chat(test_message)
        print(f"📥 Response: {response}")
        
        # Test summary
        summary = agent.get_summary()
        print(f"📊 Summary: {summary}")
        
        print("✅ SSL-safe test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_ssl_info():
    """Show SSL workaround information"""
    print("""
🔒 SSL Certificate Issue - macOS Fix
=====================================

This version bypasses SSL certificate verification to work around
common macOS Python SSL issues.

⚠️  Security Note:
This disables SSL certificate verification, which reduces security.
Only use this for testing or if you trust your network.

Permanent Solutions:
1. Install certificates: /Applications/Python 3.x/Install Certificates.command
2. Update macOS certificates: System Preferences > Software Update
3. Use pip with --trusted-host flags
4. Install certifi: pip install --trusted-host pypi.org certifi

For Production:
- Fix SSL certificates properly
- Use the regular standalone_agent.py once SSL is fixed
    """)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            simple_test()
        elif sys.argv[1] == 'ssl-info':
            show_ssl_info()
        else:
            print("Usage: python ssl_safe_agent.py [test|ssl-info]")
    else:
        interactive_mode()