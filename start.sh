#!/bin/bash

# Argus Digital Sentinel - Startup Script
echo "🔍 Starting Argus Digital Sentinel..."
echo "Have you been pwnd? Preventing self-sabotage and career suicide from the get-go with MANUS AI"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Check if frontend is built
if [ ! -d "src/static/assets" ]; then
    echo "🔧 Building frontend..."
    cd argus-frontend
    npm install
    npm run build
    cd ..
    cp -r argus-frontend/dist/* src/static/
    echo "✅ Frontend built successfully"
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set. AI analysis will not work."
    echo "   Set it with: export OPENAI_API_KEY='your-key-here'"
    echo ""
fi

# Activate virtual environment
source .venv/bin/activate

# Start the application
echo "🚀 Starting Argus Digital Sentinel on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python src/main.py

