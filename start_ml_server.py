#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def main():
    try:
        from ml_enhanced_server import start_ml_enhanced_server
        
        print("🚀 Starting ML-Enhanced AgenticAI4DB Server...")
        
        if not os.getenv('GOOGLE_API_KEY'):
            print("❌ GOOGLE_API_KEY environment variable not set")
            print("Please run: export GOOGLE_API_KEY='your-api-key'")
            return
        
        start_ml_enhanced_server(port=8080)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Some ML features may be disabled due to missing dependencies")
        # Try to start basic server
        try:
            from web_server import start_server
            print("🔄 Starting basic server without ML features...")
            start_server(port=8080)
        except Exception as e2:
            print(f"❌ Error starting server: {e2}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
