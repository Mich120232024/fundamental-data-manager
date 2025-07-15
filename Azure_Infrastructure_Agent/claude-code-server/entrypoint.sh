#!/bin/bash
# Claude Code MCP Server Entrypoint

set -e

echo "Starting Claude Code MCP Server..."

# Load API key from mounted secret
if [ -f /var/run/secrets/anthropic-api-key/api-key ]; then
    export ANTHROPIC_API_KEY=$(cat /var/run/secrets/anthropic-api-key/api-key)
    echo "✓ API key loaded from Kubernetes secret"
else
    echo "WARNING: API key not found, using environment variable"
fi

# Set environment
export CLAUDE_WORKSPACE=/workspace
export MCP_LOG_LEVEL=${MCP_LOG_LEVEL:-info}

# Log configuration
echo "Configuration:"
echo "- Workspace: $CLAUDE_WORKSPACE"
echo "- Log Level: $MCP_LOG_LEVEL"
echo "- Server Mode: MCP stdio"

# Copy the Python server files
cp /app/claude_code_mcp_server.py /app/server.py
cp /app/mcp_http_bridge.py /app/http_bridge.py || true

# Start the MCP HTTP Bridge (which will start the MCP server internally)
echo "Starting MCP HTTP Bridge..."
exec python3 /app/mcp_http_bridge.py