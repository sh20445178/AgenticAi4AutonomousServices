#!/usr/bin/env python3
"""
Main entry point for the Gemini AI Agent
Interactive command-line interface
"""

import sys
import signal
from typing import Optional

try:
    from agent import GeminiAgent
    from utils import print_colored, format_response, save_conversation
    from config import config
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you've installed the requirements: pip install -r requirements.txt")
    sys.exit(1)

class InteractiveAgent:
    """Interactive command-line interface for the Gemini Agent"""
    
    def __init__(self):
        self.agent: Optional[GeminiAgent] = None
        self.running = True
        
        # Setup signal handler for graceful exit
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print_colored("\n\nGracefully shutting down...", 'yellow')
        self.running = False
        
        if self.agent and self.agent.conversation_history:
            filename = self.agent.save_conversation()
            if filename:
                print_colored(f"Conversation saved to: {filename}", 'green')
        
        print_colored("Goodbye! 👋", 'cyan')
        sys.exit(0)
    
    def initialize_agent(self):
        """Initialize the Gemini agent"""
        try:
            print_colored("Initializing Gemini AI Agent...", 'yellow')
            self.agent = GeminiAgent()
            print_colored("✅ Agent initialized successfully!", 'green')
            return True
        except ValueError as e:
            print_colored(f"❌ Configuration error: {e}", 'red')
            print_colored("Please check your .env file and ensure GOOGLE_API_KEY is set.", 'yellow')
            return False
        except Exception as e:
            print_colored(f"❌ Error initializing agent: {e}", 'red')
            return False
    
    def print_help(self):
        """Print available commands"""
        help_text = """
Available commands:
  /help       - Show this help message
  /clear      - Clear conversation history
  /summary    - Show conversation summary
  /save       - Save conversation to file
  /load       - Load conversation from file
  /stream     - Toggle streaming mode
  /exit       - Exit the application
  
Just type your message to chat with the AI agent!
        """
        print_colored(help_text, 'cyan')
    
    def handle_command(self, command: str) -> bool:
        """Handle special commands
        
        Returns:
            True if command was handled, False if it's a regular message
        """
        command = command.strip().lower()
        
        if command == '/help':
            self.print_help()
            return True
        
        elif command == '/clear':
            self.agent.reset_conversation()
            print_colored("🧹 Conversation history cleared!", 'green')
            return True
        
        elif command == '/summary':
            summary = self.agent.get_conversation_summary()
            print_colored("📊 Conversation Summary:", 'cyan')
            for key, value in summary.items():
                print_colored(f"  {key}: {value}", 'white')
            return True
        
        elif command == '/save':
            filename = self.agent.save_conversation()
            if filename:
                print_colored(f"💾 Conversation saved to: {filename}", 'green')
            else:
                print_colored("❌ Failed to save conversation", 'red')
            return True
        
        elif command == '/load':
            filename = input("Enter filename to load: ").strip()
            if filename:
                try:
                    self.agent.load_conversation(filename)
                    print_colored(f"📂 Conversation loaded from: {filename}", 'green')
                except Exception as e:
                    print_colored(f"❌ Error loading conversation: {e}", 'red')
            return True
        
        elif command in ['/exit', '/quit', '/q']:
            self.running = False
            return True
        
        return False
    
    def chat_loop(self):
        """Main chat loop"""
        print_colored("\n🤖 Gemini AI Agent", 'magenta')
        print_colored("Type '/help' for commands or just start chatting!", 'cyan')
        print_colored("Press Ctrl+C to exit gracefully.\n", 'yellow')
        
        while self.running:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for commands
                if user_input.startswith('/'):
                    if self.handle_command(user_input):
                        continue
                
                # Get AI response
                print_colored("🤖 Thinking...", 'yellow')
                
                try:
                    response = self.agent.chat(user_input)
                    
                    # Format and display response
                    formatted_response = format_response(response)
                    print_colored(f"\nAI: {formatted_response}\n", 'blue')
                    
                except Exception as e:
                    print_colored(f"❌ Error getting response: {e}", 'red')
                
            except EOFError:
                # Handle Ctrl+D
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C
                break
    
    def run(self):
        """Run the interactive agent"""
        print_colored("🚀 Starting Gemini AI Agent...", 'cyan')
        
        # Initialize agent
        if not self.initialize_agent():
            return
        
        # Start chat loop
        try:
            self.chat_loop()
        finally:
            # Save conversation on exit
            if self.agent and self.agent.conversation_history:
                filename = self.agent.save_conversation()
                if filename:
                    print_colored(f"💾 Conversation saved to: {filename}", 'green')

def main():
    """Main function"""
    # Check if API key is configured
    try:
        if not config.google_api_key:
            print_colored("❌ GOOGLE_API_KEY not found!", 'red')
            print_colored("Please create a .env file with your Google Gemini API key.", 'yellow')
            print_colored("See .env.example for the required format.", 'yellow')
            return
    except Exception as e:
        print_colored(f"❌ Configuration error: {e}", 'red')
        return
    
    # Start interactive agent
    interactive_agent = InteractiveAgent()
    interactive_agent.run()

if __name__ == "__main__":
    main()