# Gemini AI Agent Project - Complete Setup Guide

## 📁 Project Overview

You now have a complete Python project for creating an AI agent using Google's Gemini API. The project includes:

### Core Files:
- `agent.py` - Full-featured AI agent with advanced capabilities
- `simple_agent.py` - Minimal version requiring only requests library
- `main.py` - Interactive command-line interface
- `config.py` - Configuration management with environment variables
- `utils.py` - Utility functions for formatting, logging, etc.
- `examples.py` - Usage examples and demonstrations

### Setup Files:
- `requirements.txt` - Python package dependencies
- `setup.sh` - Automated setup script for macOS/Linux
- `test_setup.py` - Verification script to test installation
- `.env.example` - Template for environment variables

### Documentation:
- `README.md` - Comprehensive project documentation
- `QUICKSTART.md` - Quick setup guide
- `TROUBLESHOOTING.md` - Solutions for common issues

## 🚀 Installation Options

### Option 1: Full Installation (Recommended)
```bash
# 1. Install dependencies
pip install google-generativeai python-dotenv pydantic colorama requests

# 2. Create environment file
cp .env.example .env

# 3. Edit .env and add your API key
# GOOGLE_API_KEY=your_actual_api_key_here

# 4. Test the setup
python test_setup.py

# 5. Run the agent
python main.py
```

### Option 2: Minimal Installation (If having network issues)
```bash
# 1. Only install requests (usually available)
pip install requests

# 2. Set environment variable
export GOOGLE_API_KEY="AIzaSyCXZj4nkULw_-7p4Rwu_L8rX8FpmL2SkDE"

# 3. Run simple version
python simple_agent.py
```

### Option 3: Automated Setup (macOS/Linux)
```bash
./setup.sh
# Then edit .env file with your API key
```

## 🔑 Getting Your Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key (starts with "AIza...")
5. Add it to your `.env` file or set as environment variable

## 🎯 Usage Examples

### Interactive Mode
```bash
python main.py
```
Features:
- Real-time chat with AI
- Conversation history
- Save/load conversations
- Commands: `/help`, `/clear`, `/summary`, `/save`, `/exit`

### Simple Mode
```bash
python simple_agent.py
```
Minimal interface with basic chat functionality

### Programmatic Usage
```python
from agent import GeminiAgent

# Initialize
agent = GeminiAgent()

# Simple chat
response = agent.chat("Tell me about Python programming")
print(response)

# With streaming
for chunk in agent.chat_stream("Write a short story"):
    print(chunk, end='', flush=True)

# Async usage
import asyncio
response = await agent.chat_async("What is AI?")
```

### Run Examples
```bash
python examples.py
```
Demonstrates various features and usage patterns

## 🔧 Configuration

### Environment Variables (.env file):
```bash
GOOGLE_API_KEY=AIzaSyCXZj4nkULw_-7p4Rwu_L8rX8FpmL2SkDE    # Required
MODEL_NAME=gemini-pro               # Optional (default: gemini-pro)  
MAX_TOKENS=1000                     # Optional (default: 1000)
TEMPERATURE=0.7                     # Optional (default: 0.7)
DEBUG=False                         # Optional (default: False)
```

### Available Models:
- `gemini-pro` - Standard text model
- `gemini-pro-vision` - Text and image model (future support)

## 🛠️ Troubleshooting

### Common Issues:

1. **Import Errors**: Run `pip install -r requirements.txt`
2. **API Key Error**: Check your `.env` file or environment variable
3. **Network Issues**: See `TROUBLESHOOTING.md` for solutions
4. **Permission Issues**: Use `pip install --user` or virtual environment

### Test Your Setup:
```bash
python test_setup.py
```

### Quick Test:
```bash
python simple_agent.py test
```

## 📊 Features

### Full Agent (`agent.py`):
- ✅ Conversation history management
- ✅ Streaming responses
- ✅ Async support
- ✅ Advanced error handling
- ✅ Logging and debugging
- ✅ Save/load conversations
- ✅ Configurable parameters

### Simple Agent (`simple_agent.py`):
- ✅ Basic chat functionality
- ✅ Minimal dependencies
- ✅ JSON conversation saving
- ✅ Interactive mode
- ✅ Error handling

### Interactive Interface (`main.py`):
- ✅ Colored terminal output
- ✅ Command system
- ✅ Graceful shutdown
- ✅ Auto-save conversations
- ✅ Help system

## 🔄 Next Steps

1. **Get API Key**: [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Configure**: Edit `.env` file with your API key
4. **Test**: Run `python test_setup.py`
5. **Start Chatting**: Run `python main.py`

## 💡 Tips

- Start with `simple_agent.py` if you have dependency issues
- Use the interactive mode (`main.py`) for the best experience
- Check `examples.py` to see all features in action
- Save important conversations with `/save` command
- Use `/help` in interactive mode to see all commands

## 📞 Support

If you encounter issues:
1. Read `TROUBLESHOOTING.md`
2. Run `python test_setup.py` to diagnose problems
3. Try the simple version if the full version fails
4. Check your API key and network connection

Your Gemini AI Agent is ready to use! 🎉