#!/usr/bin/env python3
"""
Test script to verify the Gemini AI Agent setup
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import google.generativeai as genai
        print("✅ google-generativeai imported successfully")
    except ImportError:
        print("❌ google-generativeai not found. Run: pip install google-generativeai")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError:
        print("❌ python-dotenv not found. Run: pip install python-dotenv")
        return False
    
    try:
        import pydantic
        print("✅ pydantic imported successfully")
    except ImportError:
        print("❌ pydantic not found. Run: pip install pydantic")
        return False
    
    try:
        import colorama
        print("✅ colorama imported successfully")
    except ImportError:
        print("❌ colorama not found. Run: pip install colorama")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Please copy .env.example to .env and configure it.")
        return False
    
    # Try to load config
    try:
        from config import config
        print("✅ Configuration loaded successfully")
        
        # Check API key
        if not config.google_api_key or config.google_api_key == "your_gemini_api_key_here":
            print("⚠️  GOOGLE_API_KEY not configured in .env file")
            return False
        
        print(f"✅ API key configured (length: {len(config.google_api_key)})")
        print(f"✅ Model: {config.model_name}")
        print(f"✅ Temperature: {config.temperature}")
        print(f"✅ Max tokens: {config.max_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_agent_creation():
    """Test agent creation"""
    print("\n🤖 Testing agent creation...")
    
    try:
        from agent import GeminiAgent
        agent = GeminiAgent()
        print("✅ Agent created successfully")
        
        # Test basic functionality
        print("🧪 Testing basic chat functionality...")
        response = agent.chat("Hello, can you respond with just 'Test successful'?")
        
        if response and len(response) > 0:
            print("✅ Agent responded successfully")
            print(f"   Response: {response[:100]}...")
            return True
        else:
            print("❌ Agent failed to respond")
            return False
            
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

def test_utilities():
    """Test utility functions"""
    print("\n🛠️  Testing utilities...")
    
    try:
        from utils import print_colored, format_response, validate_api_key
        
        # Test colored printing
        print_colored("✅ Colored printing works", 'green')
        
        # Test text formatting
        long_text = "This is a very long text " * 10
        formatted = format_response(long_text, max_width=50)
        print("✅ Text formatting works")
        
        # Test API key validation
        if validate_api_key("AIzaSyDummyKeyForTesting123456789"):
            print("✅ API key validation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Utilities test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Gemini AI Agent - Setup Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Utilities Test", test_utilities),
        ("Agent Creation Test", test_agent_creation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Your Gemini AI Agent is ready to use.")
        print("\nTo start using the agent:")
        print("  python main.py      # Interactive mode")
        print("  python examples.py  # Run examples")
    else:
        print("❌ Some tests failed. Please check the errors above and fix them.")
        print("\nCommon issues:")
        print("- Missing dependencies: run 'pip install -r requirements.txt'")
        print("- Missing API key: add GOOGLE_API_KEY to .env file")
        print("- Invalid API key: check your Google Gemini API key")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)