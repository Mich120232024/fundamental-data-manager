#!/bin/bash
# Start User Management Dashboard

echo "🚀 Starting User Management Dashboard..."
echo ""

# Stop any existing cosmos viewer
pkill -f cosmos_viewer_server.py 2>/dev/null || true

# Change to backend directory
cd "$(dirname "$0")/backend"

# Check if Python packages are installed
echo "📦 Checking dependencies..."
python3 -c "import flask, flask_cors, azure.cosmos, dotenv" 2>/dev/null || {
    echo "Installing required packages..."
    pip3 install -r ../config/requirements.txt
}

# Start the dashboard
echo "🌐 Starting dashboard server..."
echo "   Main Interface: http://localhost:5001/"
echo "   Debug Mode: http://localhost:5001/debug"
echo "   Press Ctrl+C to stop"
echo ""

python3 app.py