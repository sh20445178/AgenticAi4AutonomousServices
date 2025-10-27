#!/usr/bin/env python3
"""
Simple example of using the Gemini AI Agent
"""

from agent import GeminiAgent
from utils import print_colored

def simple_example():
    """Simple example usage"""
    try:
        # Initialize the agent
        print_colored("Initializing Gemini Agent...", 'yellow')
        agent = GeminiAgent()
        
        # Example conversations
        examples = [
            "Hello! What can you help me with?",
            "Explain quantum computing in simple terms",
            "Write a short Python function to calculate fibonacci numbers",
            "What are the best practices for AI development?"
        ]
        
        print_colored("🤖 Running example conversations:", 'cyan')
        
        for i, question in enumerate(examples, 1):
            print_colored(f"\n--- Example {i} ---", 'magenta')
            print_colored(f"Question: {question}", 'white')
            
            response = agent.chat(question)
            print_colored(f"Response: {response[:200]}...", 'blue')
        
        # Show conversation summary
        summary = agent.get_conversation_summary()
        print_colored(f"\n📊 Conversation Summary:", 'cyan')
        print_colored(f"Total messages: {summary['total_messages']}", 'white')
        print_colored(f"Model used: {summary['model_used']}", 'white')
        
        # Save the conversation
        filename = agent.save_conversation()
        if filename:
            print_colored(f"💾 Conversation saved to: {filename}", 'green')
        
    except Exception as e:
        print_colored(f"❌ Error: {e}", 'red')

def streaming_example():
    """Example of streaming responses"""
    try:
        print_colored("\n🌊 Streaming Example:", 'cyan')
        agent = GeminiAgent()
        
        question = "Write a short story about a robot learning to paint"
        print_colored(f"Question: {question}", 'white')
        print_colored("Streaming response:", 'blue')
        
        for chunk in agent.chat_stream(question):
            print(chunk, end='', flush=True)
        
        print("\n")
        
    except Exception as e:
        print_colored(f"❌ Streaming error: {e}", 'red')

async def async_example():
    """Example of async usage"""
    import asyncio
    
    try:
        print_colored("\n⚡ Async Example:", 'cyan')
        agent = GeminiAgent()
        
        questions = [
            "What is machine learning?",
            "Explain neural networks",
            "What is the future of AI?"
        ]
        
        # Process multiple questions concurrently
        tasks = [agent.chat_async(q, include_history=False) for q in questions]
        responses = await asyncio.gather(*tasks)
        
        for question, response in zip(questions, responses):
            print_colored(f"Q: {question}", 'white')
            print_colored(f"A: {response[:100]}...\n", 'blue')
        
    except Exception as e:
        print_colored(f"❌ Async error: {e}", 'red')

if __name__ == "__main__":
    import asyncio
    
    print_colored("🚀 Gemini AI Agent Examples", 'magenta')
    
    # Run examples
    simple_example()
    streaming_example()
    
    # Run async example
    print_colored("Running async example...", 'yellow')
    asyncio.run(async_example())
    
    print_colored("✅ All examples completed!", 'green')