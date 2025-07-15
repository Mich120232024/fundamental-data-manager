#!/bin/bash
# Claudia Installation Script
# This script installs prerequisites and builds Claudia

echo "🚀 Claudia Installation Script"
echo "============================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Install Rust
echo -e "\n📦 Step 1: Installing Rust..."
if command_exists rustc; then
    echo -e "${GREEN}✓ Rust already installed${NC}"
else
    echo "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
    echo -e "${GREEN}✓ Rust installed${NC}"
fi

# Step 2: Install Bun
echo -e "\n📦 Step 2: Installing Bun..."
if command_exists bun; then
    echo -e "${GREEN}✓ Bun already installed${NC}"
else
    echo "Installing Bun..."
    curl -fsSL https://bun.sh/install | bash
    export BUN_INSTALL="$HOME/.bun"
    export PATH="$BUN_INSTALL/bin:$PATH"
    echo -e "${GREEN}✓ Bun installed${NC}"
fi

# Step 3: Clone Claudia
echo -e "\n📦 Step 3: Cloning Claudia repository..."
cd ~/Downloads
if [ -d "claudia" ]; then
    echo "Claudia directory exists, updating..."
    cd claudia
    git pull
else
    git clone https://github.com/getAsterisk/claudia.git
    cd claudia
fi
echo -e "${GREEN}✓ Repository ready${NC}"

# Step 4: Install dependencies
echo -e "\n📦 Step 4: Installing dependencies..."
bun install
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 5: Build Claudia
echo -e "\n🔨 Step 5: Building Claudia (this may take a few minutes)..."
bun run tauri build

# Check if build succeeded
if [ -f "src-tauri/target/release/bundle/macos/Claudia.app/Contents/MacOS/Claudia" ]; then
    echo -e "${GREEN}✓ Build successful!${NC}"
    
    # Step 6: Install to Applications
    echo -e "\n📦 Step 6: Installing to Applications..."
    cp -r src-tauri/target/release/bundle/macos/Claudia.app /Applications/
    
    # Remove quarantine attribute
    xattr -cr /Applications/Claudia.app
    
    echo -e "${GREEN}✓ Claudia installed to /Applications${NC}"
    
    echo -e "\n🎉 Installation Complete!"
    echo "================================"
    echo "To launch Claudia:"
    echo "1. Open Finder → Applications"
    echo "2. Double-click Claudia"
    echo "3. If security warning appears:"
    echo "   - Go to System Settings → Privacy & Security"
    echo "   - Click 'Open Anyway'"
    echo ""
    echo "First time setup:"
    echo "- Claudia will import your MCP servers automatically"
    echo "- Test each server connection in the UI"
    echo "- Check the analytics dashboard for usage"
else
    echo -e "${RED}✗ Build failed. Check error messages above.${NC}"
    echo "Common fixes:"
    echo "1. Make sure Xcode Command Line Tools are installed:"
    echo "   xcode-select --install"
    echo "2. For Apple Silicon, try:"
    echo "   rustup target add aarch64-apple-darwin"
    exit 1
fi