#!/bin/bash
# Update all team agenda files with MCP critical information

echo "Updating all team agenda files with MCP critical information..."

# MCP critical section to add
MCP_SECTION='## 🚨 CRITICAL: MCP SERVER CONFIGURATION CHANGES - ALL AGENTS MUST READ

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

'

# Find all team_agenda.md files except HEAD_OF_RESEARCH (already updated)
find /Users/mikaeleage/Research\ \&\ Analytics\ Services/Agent_Shells -name "team_agenda.md" -type f | grep -v HEAD_OF_RESEARCH | while read -r file; do
    echo "Updating: $file"
    
    # Check if MCP section already exists
    if grep -q "MCP SERVER CONFIGURATION CHANGES" "$file"; then
        echo "  - MCP section already exists, skipping..."
        continue
    fi
    
    # Create temporary file with MCP section added after the header
    awk -v mcp="$MCP_SECTION" '
    BEGIN { printed = 0 }
    /^---$/ && !printed { 
        print $0
        print ""
        print mcp
        printed = 1
        next
    }
    { print }
    ' "$file" > "$file.tmp"
    
    # Replace original file
    mv "$file.tmp" "$file"
    
    # Update last updated date
    sed -i '' 's/\*\*Last Updated\*\*: .*/\*\*Last Updated\*\*: 2025-07-05/' "$file"
    
    echo "  - Updated successfully!"
done

echo ""
echo "✅ All team agenda files updated with MCP critical information!"
echo ""
echo "Summary of updates:"
echo "1. Added MCP server critical update section"
echo "2. Warned about institutional_memory JSON errors"
echo "3. Instructed to use memory server instead"
echo "4. Updated last modified dates to 2025-07-05"