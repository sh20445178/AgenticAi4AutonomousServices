#!/bin/bash

# Setup script for Gemini AI Agent project

echo "🚀 Setting up Gemini AI Agent project..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your Google Gemini API key!"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Get your Google Gemini API key from: https://makersuite.google.com/app/apikey"
echo "2. Edit the .env file and add your API key"
echo "3. Run the agent:"
echo "   python main.py           # Interactive mode"
echo "   python examples.py       # Run examples"
echo "   python agent.py          # Quick test"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "   source venv/bin/activate"