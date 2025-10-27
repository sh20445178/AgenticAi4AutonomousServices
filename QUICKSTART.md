# Quick Start Guide - Gemini AI Agent

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 3. Configure Environment
```bash
cp .env.example .env
```
Edit `.env` file and replace `your_gemini_api_key_here` with your actual API key.

### 4. Test Setup
```bash
python test_setup.py
```

### 5. Start Using
```bash
python main.py          # Interactive chat
python examples.py      # Run examples
```

## 🎯 Quick Example

```python
from agent import GeminiAgent

# Initialize agent
agent = GeminiAgent()

# Chat with AI
response = agent.chat("Hello! Tell me about Python programming.")
print(response)
```

## 📱 Features

- ✅ Interactive chat interface
- ✅ Conversation history
- ✅ Streaming responses
- ✅ Async support
- ✅ Save/load conversations
- ✅ Colored terminal output
- ✅ Error handling & logging

## 🛠️ Commands (in interactive mode)

- `/help` - Show help
- `/clear` - Clear conversation
- `/summary` - Show stats
- `/save` - Save conversation
- `/exit` - Exit

## 🔧 Configuration (.env file)

```bash
GOOGLE_API_KEY=AIzaSyCXZj4nkULw_-7p4Rwu_L8rX8FpmL2SkDE
MODEL_NAME=gemini-pro
MAX_TOKENS=1000
TEMPERATURE=0.7
DEBUG=False
```

## 📁 Project Structure

```
AgenticAI4DB/
├── main.py           # Interactive interface
├── agent.py          # AI Agent class
├── config.py         # Configuration
├── utils.py          # Utilities
├── examples.py       # Usage examples
├── test_setup.py     # Setup verification
├── requirements.txt  # Dependencies
└── .env             # Your config (create this)
```