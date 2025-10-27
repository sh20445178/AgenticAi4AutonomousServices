#!/usr/bin/env python3
"""
Test script to find available Gemini models
"""

import json
import os
import urllib.request
import urllib.error
import ssl

def list_models(api_key):
    """List available Gemini models"""
    
    # Create SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Try different API versions
    api_versions = ["v1beta", "v1"]
    
    for version in api_versions:
        try:
            url = f"https://generativelanguage.googleapis.com/{version}/models?key={api_key}"
            
            print(f"\n🔍 Checking API version: {version}")
            print(f"URL: {url}")
            
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    
                    if 'models' in result:
                        print(f"✅ Found {len(result['models'])} models in {version}:")
                        for model in result['models']:
                            model_name = model.get('name', 'Unknown')
                            supported_methods = model.get('supportedGenerationMethods', [])
                            if 'generateContent' in supported_methods:
                                print(f"  ✅ {model_name} - supports generateContent")
                            else:
                                print(f"  ❌ {model_name} - methods: {supported_methods}")
                    else:
                        print(f"❌ No models found in response for {version}")
                        print(f"Response: {result}")
                else:
                    print(f"❌ HTTP {response.status} for {version}")
                    
        except Exception as e:
            print(f"❌ Error checking {version}: {e}")

if __name__ == "__main__":
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Set GOOGLE_API_KEY environment variable")
        exit(1)
    
    print("🔍 Discovering available Gemini models...")
    list_models(api_key)