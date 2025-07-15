#!/bin/bash
# Fix Claudia not finding Claude Code

echo "🔧 Fixing Claudia Claude Code Detection"
echo "======================================"

# 1. Create symbolic links for Claudia to find Claude
echo "Creating symbolic links..."
sudo ln -sf /opt/homebrew/bin/claude /usr/local/bin/claude 2>/dev/null
sudo ln -sf /opt/homebrew/bin/node /usr/local/bin/node 2>/dev/null
sudo ln -sf /opt/homebrew/bin/npm /usr/local/bin/npm 2>/dev/null

# 2. Export paths for current session
export PATH="/opt/homebrew/bin:$PATH"
export NODE_PATH="/opt/homebrew/lib/node_modules"

# 3. Check Claude Code config location
echo -e "\nClaude Code config location:"
ls -la ~/Library/Application\ Support/Claude/

# 4. Create Claudia config if needed
CLAUDIA_CONFIG_DIR=~/Library/Application\ Support/Claudia
mkdir -p "$CLAUDIA_CONFIG_DIR"

# 5. Create a launcher script that sets paths
cat > ~/Desktop/Launch_Claudia.command << 'EOF'
#!/bin/bash
# Launch Claudia with correct paths

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
export NODE_PATH="/opt/homebrew/lib/node_modules"

# Launch Claudia
open /Applications/Claudia.app

echo "Claudia launched with correct paths"
EOF

chmod +x ~/Desktop/Launch_Claudia.command

echo -e "\n✅ Fix Applied!"
echo "================================"
echo "Try these solutions in order:"
echo ""
echo "1. RESTART Claudia:"
echo "   - Quit Claudia completely (Cmd+Q)"
echo "   - Launch using the new desktop script:"
echo "   - Double-click 'Launch_Claudia.command' on your Desktop"
echo ""
echo "2. If still not working, try running Claude Code first:"
echo "   claude --version"
echo "   (This ensures Claude Code is initialized)"
echo ""
echo "3. Alternative launch from Terminal:"
echo "   export PATH=\"/opt/homebrew/bin:\$PATH\""
echo "   open /Applications/Claudia.app"
echo ""
echo "4. Check Claudia Settings:"
echo "   - Look for 'Claude Code Path' setting"
echo "   - Set it to: /opt/homebrew/bin/claude"