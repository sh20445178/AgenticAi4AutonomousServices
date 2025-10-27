# Installation Troubleshooting Guide

## Network Issues Solutions

If you're experiencing network connectivity issues during installation, try these solutions:

### Method 1: Use pip with different index
```bash
# Try with a different PyPI mirror
pip install -i https://pypi.org/simple/ google-generativeai python-dotenv pydantic colorama requests
```

### Method 2: Install packages individually
```bash
pip install google-generativeai
pip install python-dotenv
pip install pydantic
pip install colorama
pip install requests
```

### Method 3: Use conda (if available)
```bash
conda install -c conda-forge python-dotenv pydantic colorama requests
pip install google-generativeai  # This one usually needs pip
```

### Method 4: Offline Installation
If you have access to another machine with internet:

1. Download packages:
```bash
pip download google-generativeai python-dotenv pydantic colorama requests -d packages/
```

2. Transfer the packages/ folder to your machine

3. Install offline:
```bash
pip install --find-links packages/ --no-index google-generativeai python-dotenv pydantic colorama requests
```

### Method 5: Alternative Gemini Client
If google-generativeai package is not available, you can use direct HTTP requests:

```python
import requests
import json

def call_gemini_api(api_key, message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": message
            }]
        }]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error: {response.status_code} - {response.text}"
```

## Verify Installation

After installation, test with:
```bash
python -c "import google.generativeai; print('SUCCESS: google-generativeai installed')"
python -c "import dotenv; print('SUCCESS: python-dotenv installed')"
python -c "import pydantic; print('SUCCESS: pydantic installed')"
python -c "import colorama; print('SUCCESS: colorama installed')"
```

## Common Issues

### Issue: SSL Certificate Error
```bash
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org google-generativeai
```

### Issue: Permission Denied
```bash
pip install --user google-generativeai python-dotenv pydantic colorama requests
```

### Issue: Proxy Settings
```bash
pip install --proxy http://your-proxy:port google-generativeai
```

If none of these work, you can still use the project structure and manually implement the API calls using the requests library.