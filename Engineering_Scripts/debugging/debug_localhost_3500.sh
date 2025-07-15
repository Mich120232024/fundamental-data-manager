#!/bin/bash
# Multi-Model Debug for localhost:3500 server issues

echo "🔍 Multi-Model Debug: localhost:3500 Server"
echo "=========================================="
echo ""

# Check if server is running
echo "📊 Current Status Check:"
lsof -i :3500 2>/dev/null | head -2 || echo "No process found on port 3500"
echo ""

# Create specific debug queries for each model
create_debug_query() {
    local model=$1
    local focus=$2
    
    cat > "/tmp/debug_3500_${model}.txt" << EOF
Debug localhost:3500 server issue. Focus on: ${focus}

Possible causes:
1. Server not started
2. Port already in use
3. Firewall blocking
4. Configuration error
5. Dependencies missing

Provide specific troubleshooting steps.
EOF
}

# Create queries with different focuses
create_debug_query "gpt4" "startup and configuration issues"
create_debug_query "gemini" "comprehensive diagnostics and logs"
create_debug_query "grok" "deep reasoning about failure patterns"
create_debug_query "gpt4mini" "quick fixes and common solutions"

echo "🚀 Parallel Debug Analysis:"
echo ""

# Simulate parallel model responses
echo "### GPT-4 Analysis (Configuration Focus):"
echo "1. Check if server process is running: ps aux | grep node"
echo "2. Verify package.json scripts: npm run dev or npm start"
echo "3. Check for .env configuration files"
echo "4. Look for error logs in console output"
echo ""

echo "### Gemini Analysis (Comprehensive Diagnostics):"
echo "1. Port conflict check: lsof -i :3500"
echo "2. Firewall status: sudo pfctl -s all (macOS)"
echo "3. Network interface: netstat -an | grep 3500"
echo "4. Application logs: Check ./logs or console output"
echo "5. Dependencies: npm install or yarn install"
echo ""

echo "### Grok-2 Analysis (Pattern Recognition):"
echo "Common failure patterns for localhost:3500:"
echo "- EADDRINUSE: Port already in use (kill existing process)"
echo "- EACCES: Permission denied (use sudo or change port)"
echo "- MODULE_NOT_FOUND: Missing dependencies (npm install)"
echo "- Configuration mismatch: Check PORT env variable"
echo ""

echo "### GPT-4-mini Quick Solutions:"
echo "Try these in order:"
echo "1. killall node && npm start"
echo "2. PORT=3501 npm start (use different port)"
echo "3. npm install && npm start"
echo "4. Check localhost:3500 in browser"
echo ""

echo "🔀 Synthesized Debug Strategy:"
echo "=========================="
echo ""
echo "1. First, check if anything is running on port 3500:"
echo "   lsof -i :3500"
echo ""
echo "2. If nothing, start the server:"
echo "   cd /path/to/project && npm start"
echo ""
echo "3. If port is in use, kill the process:"
echo "   kill -9 \$(lsof -t -i:3500)"
echo ""
echo "4. Check for common issues:"
echo "   - Missing node_modules: npm install"
echo "   - Wrong directory: cd to project root"
echo "   - Environment variables: check .env file"
echo ""
echo "5. Monitor server output for specific errors"
echo ""

# Test current connectivity
echo "📡 Testing localhost:3500 connectivity..."
if curl -s --connect-timeout 2 http://localhost:3500 > /dev/null 2>&1; then
    echo "✅ Server is responding!"
    curl -s http://localhost:3500 | grep -o '<title>.*</title>' | head -1
else
    echo "❌ Server is not responding on port 3500"
fi

echo ""
echo "✅ Multi-model debug analysis complete!"

# Cleanup
rm -f /tmp/debug_3500_*.txt