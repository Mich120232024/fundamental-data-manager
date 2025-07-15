#!/bin/bash
# Update all agent maintenance checklists and team agendas with memory fix information

echo "Updating all agents with memory server fix information..."

# Memory fix notice to add
MEMORY_FIX='### 🔧 MEMORY SERVER FIXED - 2025-07-05
- ✅ Memory server now correctly configured
- ✅ Use `mcp__memory__` for all operations  
- ✅ Points to: `/Users/mikaeleage/.claude/institutional_memory.json`
- ❌ Do NOT use `mcp__institutional_memory__` (deprecated)
- 📋 See: `/MCP_MEMORY_FIX_2025_07_05.md` for details'

# Update all maintenance checklists
echo "Updating maintenance checklists..."
find /Users/mikaeleage/Research\ \&\ Analytics\ Services/Agent_Shells -name "maintenance_checklist.md" -type f | while read -r file; do
    echo "  - Updating: $(basename $(dirname "$file"))/maintenance_checklist.md"
    
    # Add memory fix notice after first memory-related section
    if ! grep -q "MEMORY SERVER FIXED - 2025-07-05" "$file"; then
        # Create temp file with fix notice
        awk -v fix="$MEMORY_FIX" '
        /memory.*MCP|MCP.*memory/ && !printed {
            print
            print ""
            print fix
            print ""
            printed=1
            next
        }
        {print}
        ' "$file" > "$file.tmp"
        mv "$file.tmp" "$file"
    fi
done

# Update all team agendas
echo "Updating team agendas..."
find /Users/mikaeleage/Research\ \&\ Analytics\ Services/Agent_Shells -name "team_agenda.md" -type f | while read -r file; do
    if [ -s "$file" ]; then  # Only update non-empty files
        echo "  - Updating: $(basename $(dirname "$file"))/team_agenda.md"
        
        # Update the MCP critical section if it exists
        if grep -q "MCP SERVER CONFIGURATION CHANGES" "$file"; then
            sed -i '' '/MCP SERVER CONFIGURATION CHANGES/,/^---$/c\
## 🚨 CRITICAL: MCP SERVER CONFIGURATION CHANGES - ALL AGENTS MUST READ\
\
### **MCP MEMORY SERVER FIXED - 2025-07-05**\
\
**PRIORITY**: CRITICAL - AFFECTS ALL AGENTS  \
**Date Fixed**: 2025-07-05  \
**Fix Applied**: Memory server reconfigured to correct path  \
\
**CURRENT STATUS**:\
- ✅ **FIXED**: Memory server now points to `/Users/mikaeleage/.claude/institutional_memory.json`\
- ✅ **USE**: `mcp__memory__` for all memory operations\
- ❌ **DEPRECATED**: Do not use `mcp__institutional_memory__`\
- ✅ **WORKING**: All 29 institutional memory entities preserved\
\
**WORKING MCP SERVERS**:\
- ✅ `mcp__memory__` - Institutional and dual memory system\
- ✅ `mcp__filesystem__` - File operations\
- ✅ `mcp__brave_search__` - Web search\
- ✅ `mcp__github__` - GitHub operations\
- ✅ `mcp__puppeteer__` - Browser automation\
- ✅ `mcp__azure__` - Azure operations\
- ⚠️ `mcp__firecrawl__` - Payment errors (HTTP 402)\
\
**Fix Documentation**: `/MCP_MEMORY_FIX_2025_07_05.md`\
\
---' "$file"
        fi
    fi
done

# Create a broadcast message for all agents
cat > /Users/mikaeleage/Research\ \&\ Analytics\ Services/URGENT_ALL_AGENTS_MEMORY_FIX.md << 'EOF'
# 🚨 URGENT: MEMORY SERVER FIXED - ALL AGENTS READ

**Date**: 2025-07-05
**Priority**: CRITICAL
**From**: HEAD_OF_RESEARCH

## Memory Server Issue RESOLVED

### What Happened
- Memory MCP servers were showing JSON parsing errors
- Both `mcp__institutional_memory__` and `mcp__memory__` were affected
- Graph query capabilities were unavailable

### The Fix
- Memory server reconfigured to correct file path
- Now points to: `/Users/mikaeleage/.claude/institutional_memory.json`
- All 29 institutional memory entities preserved and accessible

### Action Required
1. **USE ONLY**: `mcp__memory__` for all memory operations
2. **DO NOT USE**: `mcp__institutional_memory__` (deprecated)
3. **If errors persist**: Restart Claude Code to load new configuration

### Testing
```bash
# Test memory access with:
mcp__memory__search_nodes("MEMORY_GOVERNANCE_README")
```

### Dual Memory System Status
- ✅ Institutional memory: Working (29 entities)
- ✅ Personal memories: Unaffected  
- ✅ Access controls: Still enforced
- ✅ Governance rules: Intact

### Documentation
- Full fix details: `/MCP_MEMORY_FIX_2025_07_05.md`
- Configuration guide: `/MCP_CONFIGURATION_GUIDE_CLAUDE_CODE.md`

**All agents must update their workflows to use `mcp__memory__` exclusively.**

—HEAD_OF_RESEARCH
EOF

echo ""
echo "✅ Update complete!"
echo ""
echo "Summary:"
echo "- Updated maintenance checklists with memory fix notice"
echo "- Updated team agendas with current MCP status"
echo "- Created URGENT broadcast message for all agents"
echo ""
echo "Agents are now aware of:"
echo "1. Memory server is fixed"
echo "2. Use mcp__memory__ exclusively"
echo "3. institutional_memory name is deprecated"
echo "4. Full documentation available"