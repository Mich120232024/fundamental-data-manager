#!/bin/bash
# Fix team agenda files with MCP critical information

echo "Fixing team agenda files with MCP critical information..."

# Create temporary file with MCP section
cat > /tmp/mcp_section.md << 'EOF'
## 🚨 CRITICAL: MCP SERVER CONFIGURATION CHANGES - ALL AGENTS MUST READ

### **MCP (Model Context Protocol) CRITICAL UPDATE FOR ALL AGENTS**

**PRIORITY**: CRITICAL - AFFECTS ALL AGENTS  
**Date Added**: 2025-07-05  
**Authority**: System-wide configuration change  

**CRITICAL ISSUE**: The institutional_memory MCP server has JSON parsing errors and is NOT functional.

**IMMEDIATE ACTIONS REQUIRED**:
1. **USE**: `mcp__memory__` instead of `mcp__institutional_memory__`
2. **BOTH access the same memory file** - just different server names
3. **If MCP fails**: Access memory directly at `/Users/mikaeleage/.claude/institutional_memory.json`
4. **Update your maintenance checklists**: Replace all references to institutional_memory

**WORKING MCP SERVERS**:
- ✅ `mcp__memory__` - Use this for institutional memory
- ✅ `mcp__filesystem__` - File operations
- ✅ `mcp__brave_search__` - Web search
- ✅ `mcp__github__` - GitHub operations
- ✅ `mcp__puppeteer__` - Browser automation
- ✅ `mcp__azure__` - Azure operations
- ❌ `mcp__institutional_memory__` - DO NOT USE (JSON errors)
- ⚠️ `mcp__firecrawl__` - Payment errors (HTTP 402)

**CONFIGURATION METHOD**:
- ❌ **NEVER**: Edit mcp.json files manually
- ✅ **ALWAYS**: Use `claude mcp add` command
- **Full Guide**: `/MCP_CONFIGURATION_GUIDE_CLAUDE_CODE.md`

**Critical Notes Document**: `/MCP_CRITICAL_NOTES_ALL_AGENTS.md`

---

EOF

# Function to restore basic team agenda structure
restore_basic_agenda() {
    local file="$1"
    local agent_name="$2"
    
    cat > "$file" << EOF
# TEAM AGENDA
**Last Updated**: 2025-07-05

---

EOF
    
    # Add MCP section
    cat /tmp/mcp_section.md >> "$file"
    
    echo "## 🎯 CURRENT PRIORITIES" >> "$file"
    echo "" >> "$file"
    echo "**Status**: Please update with current priorities" >> "$file"
    echo "" >> "$file"
    echo "---" >> "$file"
    echo "" >> "$file"
    echo "**Agent**: $agent_name" >> "$file"
}

# Define agent names
declare -A agents=(
    ["HEAD_OF_ENGINEERING"]="HEAD_OF_ENGINEERING"
    ["Data_Analyst"]="Data_Analyst"
    ["Full_Stack_Software_Engineer"]="Full_Stack_Software_Engineer"
    ["Azure_Infrastructure_Agent"]="Azure_Infrastructure_Agent"
    ["System_Orchestrator"]="System_Orchestrator"
    ["AUDIT_AGENT"]="AUDIT_AGENT"
    ["Research_Advanced_Analyst"]="Research_Advanced_Analyst"
    ["Research_Quantitative_Analyst"]="Research_Quantitative_Analyst"
    ["Research_Strategy_Analyst"]="Research_Strategy_Analyst"
)

# Fix all team agenda files except HEAD_OF_RESEARCH
for agent_dir in "${!agents[@]}"; do
    file="/Users/mikaeleage/Research & Analytics Services/Agent_Shells/${agent_dir}/team_agenda.md"
    
    if [ -f "$file" ]; then
        echo "Fixing: $file"
        
        # Check if file is empty or corrupted
        if [ ! -s "$file" ] || ! grep -q "TEAM AGENDA\|AGENDA" "$file"; then
            echo "  - File is empty or corrupted, restoring basic structure..."
            restore_basic_agenda "$file" "${agents[$agent_dir]}"
        else
            echo "  - File has content, checking for MCP section..."
            if ! grep -q "MCP SERVER CONFIGURATION CHANGES" "$file"; then
                echo "  - Adding MCP section..."
                # Insert MCP section after first ---
                awk 'BEGIN {found=0} /^---$/ && !found {print; print ""; system("cat /tmp/mcp_section.md"); found=1; next} {print}' "$file" > "$file.tmp"
                mv "$file.tmp" "$file"
                # Update date
                sed -i '' 's/\*\*Last Updated\*\*: .*/\*\*Last Updated\*\*: 2025-07-05/' "$file"
            else
                echo "  - MCP section already exists"
            fi
        fi
    else
        echo "Creating: $file"
        mkdir -p "$(dirname "$file")"
        restore_basic_agenda "$file" "${agents[$agent_dir]}"
    fi
done

# Clean up
rm -f /tmp/mcp_section.md

echo ""
echo "✅ All team agenda files fixed with MCP critical information!"