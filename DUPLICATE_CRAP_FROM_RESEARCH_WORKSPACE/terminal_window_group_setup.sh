#!/bin/bash
# Terminal Window Group Setup - Persistent Configuration
# Created by HEAD_OF_RESEARCH
# Purpose: Create persistent Terminal window arrangement saved in macOS Terminal

echo "🔧 Creating Terminal Window Group configuration..."

# Create the terminal window group via AppleScript
osascript << 'EOF'
tell application "Terminal"
    activate
    
    -- Create new window group
    set newGroup to make new window group with properties {name:"Agent System"}
    
    -- Create all 9 terminal tabs with exact names from picture
    set tab1 to make new tab in newGroup with properties {custom title:"Audit (node)"}
    set tab2 to make new tab in newGroup with properties {custom title:"Head of Research (node)"}
    set tab3 to make new tab in newGroup with properties {custom title:"Head of engineering (node)"}
    set tab4 to make new tab in newGroup with properties {custom title:"Data Engineer"}
    set tab5 to make new tab in newGroup with properties {custom title:"Azure Engineer"}
    set tab6 to make new tab in newGroup with properties {custom title:"Software Engineer"}
    set tab7 to make new tab in newGroup with properties {custom title:"Advanced Research"}
    set tab8 to make new tab in newGroup with properties {custom title:"Strategy Analyst"}
    set tab9 to make new tab in newGroup with properties {custom title:"Quant Analyst (node)"}
    
    -- Set working directory for all tabs
    repeat with i from 1 to 9
        do script "cd '/Users/mikaeleage/Research & Analytics Services'" in tab i of newGroup
    end repeat
    
    -- Save the window group
    save newGroup in file ((path to desktop as string) & "Agent_System_Terminal_Group.terminal")
    
end tell
EOF

# Alternative: Create Terminal settings file directly
cat > "/Users/mikaeleage/Research & Analytics Services/Projects/Agent_System.terminal" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WindowGroups</key>
    <array>
        <dict>
            <key>WindowGroupName</key>
            <string>Agent System</string>
            <key>WindowGroupTabs</key>
            <array>
                <dict>
                    <key>TabTitle</key>
                    <string>Audit (node)</string>
                    <key>WorkingDirectory</key>
                    <string>/Users/mikaeleage/Research &amp; Analytics Services</string>
                </dict>
                <dict>
                    <key>TabTitle</key>
                    <string>Head of Research (node)</string>
                    <key>WorkingDirectory</key>
                    <string>/Users/mikaeleage/Research &amp; Analytics Services</string>
                </dict>
                <dict>
                    <key>TabTitle</key>
                    <string>Head of engineering (node)</string>
                    <key>WorkingDirectory</key>
                    <string>/Users/mikaeleage/Research &amp; Analytics Services</string>
                </dict>
                <dict>
                    <key>TabTitle</key>
                    <string>Data Engineer</string>
                    <key>WorkingDirectory</key>
                    <string>/Users/mikaeleage/Research &amp; Analytics Services</string>
                </dict>
                <dict>
                    <key>TabTitle</key>
                    <string>Azure Engineer</string>
                    <key>WorkingDirectory</key>
                    <string>/Users/mikaeleage/Research &amp; Analytics Services</string>
                </dict>
                <dict>
                    <key>TabTitle</key>
                    <string>Software Engineer</string>
                    <key>WorkingDirectory</key>
                    <string>/Users/mikaeleage/Research &amp; Analytics Services</string>
                </dict>
                <dict>
                    <key>TabTitle</key>
                    <string>Advanced Research</string>
                    <key>WorkingDirectory</key>
                    <string>/Users/mikaeleage/Research &amp; Analytics Services</string>
                </dict>
                <dict>
                    <key>TabTitle</key>
                    <string>Strategy Analyst</string>
                    <key>WorkingDirectory</key>
                    <string>/Users/mikaeleage/Research &amp; Analytics Services</string>
                </dict>
                <dict>
                    <key>TabTitle</key>
                    <string>Quant Analyst (node)</string>
                    <key>WorkingDirectory</key>
                    <string>/Users/mikaeleage/Research &amp; Analytics Services</string>
                </dict>
            </array>
        </dict>
    </array>
</dict>
</plist>
EOF

echo "✅ Terminal window group configuration created"
echo "📁 Location: /Users/mikaeleage/Research & Analytics Services/Projects/Agent_System.terminal"
echo ""
echo "TO USE THIS CONFIGURATION:"
echo "1. Open Terminal"
echo "2. Go to File → Import..."
echo "3. Select: Agent_System.terminal"
echo "4. Go to Terminal → Preferences → Window Groups"
echo "5. Select 'Agent System' and click 'Use Group'"
echo ""
echo "OR double-click the Agent_System.terminal file to open directly"