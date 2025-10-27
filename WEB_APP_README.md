# 🌐 Gemini AI Chat Web Application

A modern, responsive web frontend for your Gemini AI agent with a Python backend API.

## 🎨 Features

### Frontend (Web Interface)
- **Modern Chat UI** - Clean, responsive design inspired by Google's Material Design
- **Real-time Messaging** - Instant chat with your AI agent
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Dark/Light Theme Support** - Comfortable viewing in any environment
- **Settings Panel** - Adjust AI creativity (temperature) and response length
- **Chat Management** - New chat, clear history, export conversations
- **Typing Indicators** - Visual feedback when AI is processing
- **Toast Notifications** - User-friendly success/error messages
- **Suggested Prompts** - Quick-start conversation starters
- **Markdown Support** - Rich text formatting in responses

### Backend (Python API)
- **RESTful API** - Clean HTTP endpoints for frontend communication
- **SSL-Safe** - Bypasses macOS SSL certificate issues
- **CORS Enabled** - Allows cross-origin requests from frontend
- **Error Handling** - Robust error management and logging
- **Conversation History** - Maintains context across messages
- **Configurable AI Settings** - Adjustable temperature and token limits

## 📁 Project Structure

```
AgenticAI4DB/
├── 🌐 web_server.py          # Backend API server (port 8080)
├── 🎨 frontend_server.py     # Frontend file server (port 3000)
├── 🚀 start_app.sh           # Launch both servers
├── frontend/                 # Web frontend files
│   ├── index.html            # Main HTML page
│   ├── styles.css            # Modern CSS styling
│   └── script.js             # JavaScript functionality
├── ssl_safe_agent.py         # SSL-safe CLI agent
├── standalone_agent.py       # Standard CLI agent
└── .env                      # Configuration file
```

## 🚀 Quick Start

### Method 1: Use Startup Script (Recommended)
```bash
cd /Users/sh20445178/Library/CloudStorage/OneDrive-Wipro/PROJECTS/AgenticAI4DB

# Make sure your API key is in .env file
./start_app.sh
```

### Method 2: Manual Launch
```bash
# Terminal 1: Start backend server
export GOOGLE_API_KEY="your_api_key_here"
python3 web_server.py

# Terminal 2: Start frontend server  
python3 frontend_server.py

# Open http://localhost:3000 in your browser
```

## 🔧 Configuration

### Environment Variables (.env file):
```bash
GOOGLE_API_KEY=your_actual_api_key_here
MODEL_NAME=models/gemini-2.5-flash
MAX_TOKENS=1000
TEMPERATURE=0.7
DEBUG=False
```

### Server Ports:
- **Backend API**: `http://localhost:8080`
- **Frontend Web**: `http://localhost:3000`

## 🎯 API Endpoints

### Backend API (Port 8080)

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | Serves embedded HTML interface |
| `/api/status` | GET | Check API connection status |
| `/api/chat` | POST | Send message to AI agent |
| `/api/clear` | POST | Clear conversation history |
| `/api/history` | GET | Get conversation history |

### Example API Usage

#### Send Message
```javascript
fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        message: "Hello AI!",
        temperature: 0.7,
        maxTokens: 1000
    })
})
```

#### Clear History
```javascript
fetch('/api/clear', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
})
```

## 🎨 Frontend Features

### Chat Interface
- **Message Bubbles** - Distinct styling for user and AI messages
- **Timestamps** - Shows when each message was sent
- **Auto-scroll** - Automatically scrolls to latest messages
- **Character Counter** - Shows input length with color coding
- **Auto-resize** - Input field expands as you type

### Settings Panel
- **Temperature Slider** - Control AI creativity (0.0 - 1.0)
- **Max Tokens Slider** - Control response length (100 - 2000)
- **Model Info** - Shows current AI model being used
- **Status Indicator** - Real-time connection status

### Mobile Support
- **Responsive Design** - Adapts to all screen sizes
- **Touch-friendly** - Optimized for mobile interaction
- **Collapsible Sidebar** - Space-efficient on small screens

## 🔒 Security & SSL

The backend uses SSL-safe connections to handle macOS certificate issues:
- **SSL Context** - Custom SSL context that bypasses verification
- **CORS Headers** - Proper cross-origin resource sharing
- **Input Validation** - Server-side input sanitization
- **Error Handling** - Safe error messages without exposing internals

## 🛠️ Customization

### Styling
Edit `frontend/styles.css` to customize:
- Colors and themes
- Typography and fonts
- Layout and spacing
- Animations and transitions

### Functionality
Edit `frontend/script.js` to add:
- New features and controls
- Custom message formatting
- Additional API endpoints
- Enhanced error handling

### Backend
Edit `web_server.py` to modify:
- API endpoints and responses
- AI model configuration
- Request processing logic
- Authentication if needed

## 📱 Usage Tips

### Chat Commands
- **Enter** - Send message
- **Shift+Enter** - New line in message
- **Settings Panel** - Adjust AI behavior
- **Export** - Download chat history
- **Clear** - Reset conversation

### Best Practices
- Use descriptive prompts for better AI responses
- Adjust temperature for creative vs. factual responses
- Export important conversations before clearing
- Check connection status if responses seem slow

## 🔍 Troubleshooting

### Common Issues

1. **"Unable to connect to AI service"**
   - Ensure backend server is running on port 8080
   - Check your GOOGLE_API_KEY in .env file
   - Verify API key is valid and has quota

2. **Frontend not loading**
   - Ensure frontend server is running on port 3000
   - Check for port conflicts
   - Try refreshing the browser

3. **CORS errors**
   - Both servers must be running
   - Check browser console for specific errors
   - Ensure proper CORS headers in backend

4. **API key errors**
   - Verify API key format (starts with "AIza")
   - Check Google AI Studio for key status
   - Ensure key has Gemini API access

### Debug Mode
Set `DEBUG=True` in .env file for detailed logging.

## 🎉 Success!

Your Gemini AI Chat Web Application is now ready!

**Enjoy chatting with your AI assistant in a beautiful web interface!** 🚀

### What You Can Do:
- Ask questions and get intelligent responses
- Adjust AI creativity and response length
- Export and save conversations
- Use on any device with a web browser
- Customize the interface to your liking

**Happy coding and chatting!** 🎉