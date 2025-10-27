#!/usr/bin/env python3
"""
Web API Server for Gemini AI Agent
Provides REST API endpoints for the frontend
"""

import json
import os
import sys
import http.server
import socketserver
import urllib.parse
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from typing import List, Dict, Any, Optional
import threading

class GeminiWebAPI:
    """Web API wrapper for Gemini AI Agent"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "models/gemini-2.5-flash"
        self.conversation_history: List[Dict[str, Any]] = []
        
        # SSL context for macOS compatibility
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        print(f"✅ Gemini Web API initialized with model: {self.model}")
    
    def _make_request(self, message: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Make request to Gemini API"""
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        headers = {'Content-Type': 'application/json'}
        
        data = {
            "contents": [{
                "parts": [{"text": message}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        try:
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=json_data, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30, context=self.ssl_context) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    
                    if 'candidates' in result and len(result['candidates']) > 0:
                        candidate = result['candidates'][0]
                        
                        if 'content' in candidate:
                            if 'parts' in candidate['content']:
                                return candidate['content']['parts'][0]['text']
                            else:
                                return candidate['content'].get('text', 'No text in content')
                        elif 'text' in candidate:
                            return candidate['text']
                        else:
                            return "Error: Unexpected response format"
                    else:
                        return "Error: No response generated"
                else:
                    return f"API Error {response.status}"
                    
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat(self, message: str, include_history: bool = True) -> Dict[str, Any]:
        """Chat with AI and return structured response"""
        
        # Prepare message with context
        if include_history and self.conversation_history:
            context_messages = []
            for entry in self.conversation_history[-5:]:
                role = "Human" if entry['role'] == 'user' else "Assistant"
                context_messages.append(f"{role}: {entry['content']}")
            
            context = "\n".join(context_messages)
            full_message = f"Previous conversation:\n{context}\n\nCurrent message: {message}"
        else:
            full_message = message
        
        # Get response
        response_text = self._make_request(full_message)
        
        # Add to history
        timestamp = datetime.now().isoformat()
        self.conversation_history.append({
            'timestamp': timestamp,
            'role': 'user',
            'content': message
        })
        
        self.conversation_history.append({
            'timestamp': timestamp,
            'role': 'assistant',
            'content': response_text
        })
        
        # Keep history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return {
            'success': True,
            'response': response_text,
            'timestamp': timestamp
        }
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self) -> Dict[str, Any]:
        """Clear conversation history"""
        self.conversation_history.clear()
        return {'success': True, 'message': 'History cleared'}

# Global API instance
gemini_api = None

class APIHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the web API"""
    
    def _send_cors_headers(self):
        """Send CORS headers for cross-origin requests"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        path = urllib.parse.urlparse(self.path).path
        
        if path == '/':
            # Serve the new frontend HTML page
            if os.path.exists('frontend/index.html'):
                self._serve_static_file('/frontend/index.html')
            else:
                # Fallback to embedded HTML
                self._serve_html_page()
        elif path == '/api/history':
            # Get conversation history
            history = gemini_api.get_history()
            self._send_json_response({'success': True, 'history': history})
        elif path == '/api/status':
            # API status check
            self._send_json_response({'success': True, 'status': 'running', 'model': gemini_api.model})
        elif path.startswith('/frontend/') or path in ['/favicon.svg', '/logo.svg']:
            # Serve static files from frontend directory
            self._serve_static_file(path)
        else:
            self._send_json_response({'error': 'Not found'}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        path = urllib.parse.urlparse(self.path).path
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            if path == '/api/chat':
                # Chat endpoint
                message = data.get('message', '')
                if not message:
                    self._send_json_response({'error': 'Message is required'}, 400)
                    return
                
                response = gemini_api.chat(message)
                self._send_json_response(response)
                
            elif path == '/api/clear':
                # Clear history endpoint
                response = gemini_api.clear_history()
                self._send_json_response(response)
                
            else:
                self._send_json_response({'error': 'Not found'}, 404)
                
        except json.JSONDecodeError:
            self._send_json_response({'error': 'Invalid JSON'}, 400)
        except Exception as e:
            self._send_json_response({'error': str(e)}, 500)
    
    def _serve_html_page(self):
        """Serve the main HTML page"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini AI Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 800px;
            height: 80vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .chat-header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .status-bar {
            position: absolute;
            top: 10px;
            right: 15px;
            background: rgba(255,255,255,0.2);
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 5px;
        }
        
        .message.ai .message-content {
            background: white;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 5px;
        }
        
        .message-time {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 5px;
        }
        
        .chat-input-area {
            padding: 20px;
            border-top: 1px solid #e0e0e0;
            background: white;
        }
        
        .input-container {
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }
        
        .chat-input {
            flex: 1;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            padding: 12px 20px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
            resize: none;
            min-height: 50px;
            max-height: 120px;
        }
        
        .chat-input:focus {
            border-color: #667eea;
        }
        
        .send-btn, .clear-btn {
            padding: 12px 20px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .send-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .clear-btn {
            background: #ff6b6b;
            color: white;
        }
        
        .send-btn:hover, .clear-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .send-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 10px;
            color: #666;
        }
        
        .loading.show {
            display: block;
        }
        
        .typing-indicator {
            display: none;
            align-items: center;
            gap: 5px;
            color: #666;
            font-style: italic;
        }
        
        .typing-indicator.show {
            display: flex;
        }
        
        .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
            animation: typing 1.4s infinite;
        }
        
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
        
        .error-message {
            background: #ffe6e6;
            border: 1px solid #ffcccc;
            color: #cc0000;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            display: none;
        }
        
        @media (max-width: 768px) {
            .chat-container {
                width: 95%;
                height: 90vh;
            }
            
            .message-content {
                max-width: 85%;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="status-bar" id="statusBar">🟢 Online</div>
            <h1>🤖 Gemini AI Assistant</h1>
            <p>Powered by Google Gemini AI</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="error-message" id="errorMessage"></div>
            <div class="message ai">
                <div class="message-content">
                    <div>Hello! I'm your AI assistant powered by Google Gemini. How can I help you today?</div>
                    <div class="message-time" id="welcomeTime"></div>
                </div>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="typing-indicator">
                AI is thinking
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
        
        <div class="chat-input-area">
            <div class="input-container">
                <textarea 
                    class="chat-input" 
                    id="chatInput" 
                    placeholder="Type your message here..."
                    rows="1"
                ></textarea>
                <button class="send-btn" id="sendBtn">Send</button>
                <button class="clear-btn" id="clearBtn">Clear</button>
            </div>
        </div>
    </div>

    <script>
        class GeminiChat {
            constructor() {
                this.chatMessages = document.getElementById('chatMessages');
                this.chatInput = document.getElementById('chatInput');
                this.sendBtn = document.getElementById('sendBtn');
                this.clearBtn = document.getElementById('clearBtn');
                this.loading = document.getElementById('loading');
                this.errorMessage = document.getElementById('errorMessage');
                this.statusBar = document.getElementById('statusBar');
                
                this.init();
            }
            
            init() {
                // Set welcome time
                document.getElementById('welcomeTime').textContent = new Date().toLocaleTimeString();
                
                // Event listeners
                this.sendBtn.addEventListener('click', () => this.sendMessage());
                this.clearBtn.addEventListener('click', () => this.clearChat());
                
                this.chatInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.sendMessage();
                    }
                });
                
                // Auto-resize textarea
                this.chatInput.addEventListener('input', () => {
                    this.chatInput.style.height = 'auto';
                    this.chatInput.style.height = this.chatInput.scrollHeight + 'px';
                });
                
                // Check API status
                this.checkStatus();
            }
            
            async checkStatus() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    
                    if (data.success) {
                        this.statusBar.innerHTML = '🟢 Online';
                        this.statusBar.style.background = 'rgba(76, 175, 80, 0.3)';
                    } else {
                        throw new Error('API not responding');
                    }
                } catch (error) {
                    this.statusBar.innerHTML = '🔴 Offline';
                    this.statusBar.style.background = 'rgba(244, 67, 54, 0.3)';
                    this.showError('Unable to connect to AI service');
                }
            }
            
            async sendMessage() {
                const message = this.chatInput.value.trim();
                if (!message) return;
                
                // Add user message
                this.addMessage(message, 'user');
                this.chatInput.value = '';
                this.chatInput.style.height = 'auto';
                
                // Show loading
                this.setLoading(true);
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        this.addMessage(data.response, 'ai');
                        this.hideError();
                    } else {
                        throw new Error(data.error || 'Unknown error');
                    }
                } catch (error) {
                    this.showError('Failed to get AI response: ' + error.message);
                    this.addMessage('Sorry, I encountered an error. Please try again.', 'ai');
                } finally {
                    this.setLoading(false);
                }
            }
            
            async clearChat() {
                if (confirm('Are you sure you want to clear the chat history?')) {
                    try {
                        const response = await fetch('/api/clear', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({})
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            // Clear messages except welcome message
                            const messages = this.chatMessages.querySelectorAll('.message');
                            messages.forEach((msg, index) => {
                                if (index > 0) { // Keep first welcome message
                                    msg.remove();
                                }
                            });
                            this.hideError();
                        }
                    } catch (error) {
                        this.showError('Failed to clear chat: ' + error.message);
                    }
                }
            }
            
            addMessage(content, type) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                
                const textDiv = document.createElement('div');
                textDiv.textContent = content;
                
                const timeDiv = document.createElement('div');
                timeDiv.className = 'message-time';
                timeDiv.textContent = new Date().toLocaleTimeString();
                
                contentDiv.appendChild(textDiv);
                contentDiv.appendChild(timeDiv);
                messageDiv.appendChild(contentDiv);
                
                this.chatMessages.appendChild(messageDiv);
                this.scrollToBottom();
            }
            
            setLoading(show) {
                this.loading.classList.toggle('show', show);
                this.sendBtn.disabled = show;
                if (show) {
                    this.scrollToBottom();
                }
            }
            
            showError(message) {
                this.errorMessage.textContent = message;
                this.errorMessage.style.display = 'block';
            }
            
            hideError() {
                this.errorMessage.style.display = 'none';
            }
            
            scrollToBottom() {
                setTimeout(() => {
                    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
                }, 100);
            }
        }
        
        // Initialize chat when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new GeminiChat();
        });
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def _serve_static_file(self, path: str):
        """Serve static files (CSS, JS, SVG, etc.)"""
        try:
            # Map request path to file path
            if path.startswith('/frontend/'):
                file_path = path[1:]  # Remove leading slash
            elif path in ['/favicon.svg', '/logo.svg']:
                file_path = f'frontend{path}'
            else:
                self._send_json_response({'error': 'File not found'}, 404)
                return
            
            # Check if file exists
            if not os.path.exists(file_path):
                self._send_json_response({'error': 'File not found'}, 404)
                return
            
            # Determine content type
            content_type = 'text/plain'
            if path.endswith('.css'):
                content_type = 'text/css'
            elif path.endswith('.js'):
                content_type = 'text/javascript'
            elif path.endswith('.svg'):
                content_type = 'image/svg+xml'
            elif path.endswith('.html'):
                content_type = 'text/html'
            elif path.endswith('.json'):
                content_type = 'application/json'
            
            # Read and serve file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except Exception as e:
            print(f"Error serving static file {path}: {e}")
            self._send_json_response({'error': 'Internal server error'}, 500)

def start_web_server(port=8080):
    """Start the web server"""
    global gemini_api
    
    # Initialize Gemini API
    try:
        gemini_api = GeminiWebAPI()
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Please set GOOGLE_API_KEY environment variable")
        return False
    
    # Start server
    try:
        with socketserver.TCPServer(("", port), APIHandler) as httpd:
            server_url = f"http://localhost:{port}"
            print(f"🌐 Web server started at {server_url}")
            print(f"📱 Open {server_url} in your browser to use the chat interface")
            print("Press Ctrl+C to stop the server")
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return True
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number, using default 8080")
    
    start_web_server(port)