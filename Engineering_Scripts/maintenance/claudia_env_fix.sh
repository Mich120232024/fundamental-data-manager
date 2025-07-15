#!/bin/bash
# Set Claude environment variables for Claudia

echo "🔧 Setting Claude environment for Claudia"
echo "========================================"

# Export Claude home directory
export CLAUDE_HOME="$HOME/.claude"
export CLAUDE_BINARY="/opt/homebrew/bin/claude"
export CLAUDE_CODE_PATH="/opt/homebrew/bin/claude"

# Create a config file for Claudia if needed
CLAUDIA_CONFIG="$HOME/Library/Application Support/Claudia/config.json"
mkdir -p "$(dirname "$CLAUDIA_CONFIG")"

cat > "$CLAUDIA_CONFIG" << EOF
{
  "claudeBinaryPath": "/opt/homebrew/bin/claude",
  "claudeHome": "$HOME/.claude",
  "mcpConfigPath": "$HOME/.claude"
}
EOF

echo "Created Claudia config at: $CLAUDIA_CONFIG"
echo ""
echo "Launching Claudia with environment..."

# Launch with full environment
open -a Claudia --env CLAUDE_HOME="$CLAUDE_HOME" \
                --env CLAUDE_BINARY="$CLAUDE_BINARY" \
                --env CLAUDE_CODE_PATH="$CLAUDE_CODE_PATH" \
                --env PATH="/opt/homebrew/bin:$PATH"

echo ""
echo "✅ Claudia launched with Claude environment variables"

—HEAD_OF_RESEARCH