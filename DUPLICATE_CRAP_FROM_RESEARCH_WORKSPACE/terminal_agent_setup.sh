#!/bin/bash
# Terminal Agent Setup Script - Exact Configuration from Picture
# Created by HEAD_OF_RESEARCH
# Purpose: Set up 9 named terminal tabs with keyboard shortcuts for agent system

echo "🔧 Setting up agent terminal configuration..."

# Function to create terminal tab with specific name
create_terminal_tab() {
    local tab_name="$1"
    local shortcut="$2"
    
    osascript -e "
    tell application \"Terminal\"
        activate
        tell application \"System Events\" to keystroke \"t\" using command down
        delay 0.5
        set custom title of front window to \"$tab_name\"
        do script \"echo 'Terminal: $tab_name (Shortcut: ⌘$shortcut)'\" in front window
        do script \"cd '/Users/mikaeleage/Research & Analytics Services'\" in front window
    end tell"
}

# Create all 9 terminal tabs as shown in picture
echo "Creating terminal tabs..."

# Tab 1: Audit (node) - ⌘1
create_terminal_tab "Audit (node)" "1"

# Tab 2: Head of Research - ⌘2
create_terminal_tab "Head of Research (node)" "2"

# Tab 3: Head of engineering - ⌘3
create_terminal_tab "Head of engineering (node)" "3"

# Tab 4: Data Engineer - ⌘4
create_terminal_tab "Data Engineer" "4"

# Tab 5: Azure Engineer - ⌘5
create_terminal_tab "Azure Engineer" "5"

# Tab 6: Software Engineer - ⌘6
create_terminal_tab "Software Engineer" "6"

# Tab 7: Advanced Research - ⌘7
create_terminal_tab "Advanced Research" "7"

# Tab 8: Strategy Analyst - ⌘8
create_terminal_tab "Strategy Analyst" "8"

# Tab 9: Quant Analyst (node) - ⌘9
create_terminal_tab "Quant Analyst (node)" "9"

echo "✅ Agent terminal configuration complete"
echo "Use ⌘1-⌘9 to switch between agent terminals"

# Create startup script for automatic execution
cat > "/Users/mikaeleage/Research & Analytics Services/Projects/startup_terminals.sh" << 'EOF'
#!/bin/bash
# Auto-start agent terminal configuration
/Users/mikaeleage/Research\ \&\ Analytics\ Services/Projects/terminal_agent_setup.sh
EOF

chmod +x "/Users/mikaeleage/Research & Analytics Services/Projects/startup_terminals.sh"

echo "✅ Created startup script for automatic terminal setup"
echo "Run: bash '/Users/mikaeleage/Research & Analytics Services/Projects/startup_terminals.sh'"