# 🔒 SSL Certificate Fix Guide for macOS

## Quick Solution: Use the SSL-Safe Version

**I've created `ssl_safe_agent.py` that bypasses SSL verification for immediate use:**

```bash
cd /Users/sh20445178/Library/CloudStorage/OneDrive-Wipro/PROJECTS/AgenticAI4DB

# Set your API key
export GOOGLE_API_KEY="AIzaSyCXZj4nkULw_-7p4Rwu_L8rX8FpmL2SkDE"

# Run the SSL-safe version
python3 ssl_safe_agent.py
```

⚠️ **Note**: This disables SSL verification for testing purposes.

## Permanent SSL Fixes

### Method 1: Manual Certificate Installation
```bash
# Download and install certificates manually
cd /tmp
curl -O https://curl.se/ca/cacert.pem
sudo mkdir -p /etc/ssl/certs
sudo cp cacert.pem /etc/ssl/certs/
```

### Method 2: Update Python's Certificate Store
```bash
# Find your Python installation
ls /Applications/Python*

# Run the certificate installer (replace 3.12 with your version)
/Applications/Python\ 3.12/Install\ Certificates.command
```

### Method 3: Use System Python
```bash
# Try with system Python instead
/usr/bin/python3 ssl_safe_agent.py
```

### Method 4: Install with Homebrew Python
```bash
# Install Python via Homebrew (if you have Homebrew)
brew install python
$(brew --prefix)/bin/python3 ssl_safe_agent.py
```

### Method 5: Corporate Network Workaround
If you're on a corporate network with firewall/proxy:

```bash
# Set proxy if needed
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port

# Run with proxy
python3 ssl_safe_agent.py
```

## Testing Your Fix

After trying any permanent fix, test with the regular version:
```bash
python3 standalone_agent.py test
```

If it works, use the regular version. If not, use the SSL-safe version.

## API Key Setup

Get your API key from: https://makersuite.google.com/app/apikey

Then either:
1. Set environment variable: `export GOOGLE_API_KEY="your_key"`
2. Or enter it when prompted by the agent

## Which Version to Use

- ✅ **ssl_safe_agent.py** - Use this for immediate testing (bypasses SSL)
- 🔧 **standalone_agent.py** - Use this after fixing SSL (more secure)
- 🎨 **main.py** - Use this after installing packages and fixing SSL

## Security Note

The SSL-safe version is for testing only. For production use:
1. Fix SSL certificates properly
2. Use the regular standalone_agent.py
3. Never disable SSL verification in production

Your AI agent will work with the SSL-safe version while you work on fixing the certificate issues!