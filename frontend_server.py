#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend files
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

class FrontendHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent / "frontend"), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_frontend_server(port=3000):
    """Start the frontend server"""
    try:
        with socketserver.TCPServer(("", port), FrontendHandler) as httpd:
            frontend_url = f"http://localhost:{port}"
            print(f"🌐 Frontend server started at {frontend_url}")
            print(f"📱 Open {frontend_url} in your browser")
            print("Make sure the backend server (web_server.py) is also running on port 8080")
            print("Press Ctrl+C to stop the server")
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped")
        return True
    except Exception as e:
        print(f"❌ Frontend server error: {e}")
        return False

if __name__ == "__main__":
    port = 3000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number, using default 3000")
    
    start_frontend_server(port)