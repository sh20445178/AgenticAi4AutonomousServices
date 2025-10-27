#!/usr/bin/env python3
"""
Demo ML Server for AgenticAI4DB
Works without ML dependencies - demonstrates the framework with mock data
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def main():
    print("🚀 Starting AgenticAI4DB Demo ML Server...")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  GOOGLE_API_KEY environment variable not set")
        print("   You can still test the ML interface, but AI responses will be limited")
        print()
    
    try:
        # Try to start the basic web server first
        from web_server import start_web_server
        
        print("🌐 Starting web server with ML interface...")
        print("📊 ML features will show demo data (no dependencies required)")
        print("🔧 To enable full ML features, install: numpy, pandas, scikit-learn, tensorflow")
        print()
        print("📱 Server will be available at: http://localhost:8080")
        print("🧠 ML Analysis Tools will be visible in the interface")
        print("Press Ctrl+C to stop the server")
        print()
        
        # Start the basic server
        start_web_server(port=8080)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please check that web_server.py exists and is properly configured")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()