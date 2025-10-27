# Google Gemini AI Agent

A Python project for creating an AI agent powered by Google's Gemini API.

## Features

- Interactive AI agent with conversation capabilities
- Google Gemini API integration
- Environment variable management
- Async support for better performance
- Structured conversation history
- Error handling and logging

## Setup

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

4. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Usage

### Basic Usage
```bash
python main.py
```

### Interactive Mode
```bash
python agent.py
```

## Project Structure

```
AgenticAI4DB/
├── main.py              # Main application entry point
├── agent.py             # AI Agent class implementation
├── config.py            # Configuration management
├── utils.py             # Utility functions
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Configuration

The agent can be configured through environment variables:

- `GOOGLE_API_KEY`: Your Google Gemini API key (required)
- `MODEL_NAME`: Gemini model to use (default: gemini-pro)
- `MAX_TOKENS`: Maximum tokens for responses (default: 1000)
- `TEMPERATURE`: Response creativity (default: 0.7)

## Example

```python
from agent import GeminiAgent

# Initialize the agent
agent = GeminiAgent()

# Start a conversation
response = agent.chat("Hello! Tell me about artificial intelligence.")
print(response)
```

## License

MIT License