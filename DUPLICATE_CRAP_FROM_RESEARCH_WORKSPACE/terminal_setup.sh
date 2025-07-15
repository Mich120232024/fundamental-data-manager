#!/bin/bash
# Terminal Setup Script - Default Configuration
# Created by HEAD_OF_RESEARCH
# Purpose: Set up named terminal sessions for research workspace

echo "🔧 Setting up default terminal configuration..."

# Create tmux sessions for research workspace
tmux new-session -d -s "research_main" -c "/Users/mikaeleage/Research & Analytics Services"
tmux new-session -d -s "data_analysis" -c "/Users/mikaeleage/Research & Analytics Services"
tmux new-session -d -s "claude_router" -c "/Users/mikaeleage/Research & Analytics Services"
tmux new-session -d -s "monitoring" -c "/Users/mikaeleage/Research & Analytics Services"

# Set terminal titles using osascript (for macOS Terminal.app)
osascript -e 'tell application "Terminal" to set custom title of front window to "Research Main"' 2>/dev/null || true
osascript -e 'tell application "Terminal" to set custom title of front window to "Data Analysis"' 2>/dev/null || true
osascript -e 'tell application "Terminal" to set custom title of front window to "Claude Router"' 2>/dev/null || true
osascript -e 'tell application "Terminal" to set custom title of front window to "Monitoring"' 2>/dev/null || true

echo "✅ Terminal configuration complete"
echo "Available sessions:"
tmux list-sessions

# Add to shell profile for automatic execution
SHELL_PROFILE="$HOME/.zshrc"
if [[ ! -f "$SHELL_PROFILE" ]]; then
    SHELL_PROFILE="$HOME/.bash_profile"
fi

# Add terminal setup to profile if not already present
if ! grep -q "terminal_setup.sh" "$SHELL_PROFILE"; then
    echo "# Auto-setup terminal sessions" >> "$SHELL_PROFILE"
    echo "if command -v tmux &> /dev/null; then" >> "$SHELL_PROFILE"
    echo "    /Users/mikaeleage/Research\ \&\ Analytics\ Services/Projects/terminal_setup.sh" >> "$SHELL_PROFILE"
    echo "fi" >> "$SHELL_PROFILE"
    echo "✅ Added to shell profile: $SHELL_PROFILE"
fi