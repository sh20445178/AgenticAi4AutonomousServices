#!/bin/bash

# Startup script for Gemini AI Chat Application

echo "🚀 Starting Gemini AI Chat Application..."

# Check if API key is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY not found in environment variables"
    echo "Loading from .env file..."
    
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
        echo "✅ Environment variables loaded from .env"
    else
        echo "❌ No .env file found. Please create one with your GOOGLE_API_KEY"
        exit 1
    fi
fi

# Function to start backend server
start_backend() {
    echo "🔧 Starting backend server on port 8080..."
    python3 web_server.py &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
}

# Function to start frontend server
start_frontend() {
    echo "🎨 Starting frontend server on port 3000..."
    python3 frontend_server.py &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "Backend server stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "Frontend server stopped"
    fi
    echo "👋 Goodbye!"
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

# Start servers
start_backend
sleep 2  # Give backend time to start
start_frontend

echo ""
echo "🎉 Gemini AI Chat Application is running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for background processes
wait