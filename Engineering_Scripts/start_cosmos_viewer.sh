#!/bin/bash
# Start Cosmos DB Viewer

echo "🚀 Starting Cosmos DB Viewer..."
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask..."
    pip3 install flask flask-cors
fi

# Change to script directory
cd "$(dirname "$0")"

# Start the server
echo "🌐 Starting server on http://localhost:5000/viewer"
echo "   Press Ctrl+C to stop"
echo ""

python3 cosmos_viewer_server.py