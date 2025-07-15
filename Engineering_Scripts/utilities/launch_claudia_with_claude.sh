#!/bin/bash
# Launch Claudia with Claude Code properly in PATH

echo "🚀 Launching Claudia with Claude Code integration"
echo "================================================"

# Ensure Claude Code is initialized first
echo "Initializing Claude Code..."
/opt/homebrew/bin/claude --version

# Set up environment
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
export NODE_PATH="/opt/homebrew/lib/node_modules"

# Set Claude Code path explicitly
export CLAUDE_CODE_PATH="/opt/homebrew/bin/claude"

# Create a temporary wrapper that Claudia might look for
mkdir -p ~/.local/bin
ln -sf /opt/homebrew/bin/claude ~/.local/bin/claude 2>/dev/null

# Also ensure it's in common locations
sudo ln -sf /opt/homebrew/bin/claude /usr/bin/claude 2>/dev/null || true

# Launch Claudia
echo ""
echo "Launching Claudia..."
open -a Claudia --env PATH="$PATH" --env NODE_PATH="$NODE_PATH" --env CLAUDE_CODE_PATH="$CLAUDE_CODE_PATH"

echo ""
echo "✅ Claudia launched with environment:"
echo "PATH includes: /opt/homebrew/bin"
echo "CLAUDE_CODE_PATH: $CLAUDE_CODE_PATH"
echo ""
echo "If you still see 'Failed to load MCP servers', try:"
echo "1. Click 'Retry' in Claudia"
echo "2. Go to Settings → Claude Code Path"
echo "3. Set it to: /opt/homebrew/bin/claude"