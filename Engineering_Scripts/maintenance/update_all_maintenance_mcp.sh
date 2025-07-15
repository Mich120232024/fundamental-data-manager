#!/bin/bash
# Update all agent maintenance checklists with MCP critical notes

echo "Updating all agent maintenance checklists with MCP critical information..."

# Find all maintenance checklists
find /Users/mikaeleage/Research\ \&\ Analytics\ Services/Agent_Shells -name "maintenance_checklist.md" -type f | while read -r file; do
    echo "Updating: $file"
    
    # Check if file contains institutional_memory references
    if grep -q "institutional_memory" "$file"; then
        # Replace institutional_memory with memory
        sed -i '' 's/mcp__institutional_memory__/mcp__memory__/g' "$file"
        sed -i '' 's/institutional_memory:search_nodes/memory:search_nodes/g' "$file"
        
        # Add warning note if not already present
        if ! grep -q "IMPORTANT MCP NOTE" "$file"; then
            # Add after the first memory-related line
            sed -i '' '/memory.*search_nodes/a\
- [ ] **IMPORTANT MCP NOTE**: Use `mcp__memory__` NOT `mcp__institutional_memory__` (has JSON errors)\
- [ ] **If MCP fails**: Access memory directly at `/Users/mikaeleage/.claude/institutional_memory.json`' "$file"
        fi
    fi
    
    # Ensure all files have reference to the guide
    if ! grep -q "MCP_CRITICAL_NOTES_ALL_AGENTS.md" "$file"; then
        # Add reference at the beginning of the maintenance routine
        sed -i '' '1,/## 📋.*MAINTENANCE ROUTINE/s/## 📋.*MAINTENANCE ROUTINE/## 📋 PRIORITY MAINTENANCE ROUTINE\
\
### 🚨 MCP CRITICAL UPDATE\
**MUST READ**: `/MCP_CRITICAL_NOTES_ALL_AGENTS.md` - Critical MCP server changes affecting all agents\
&/' "$file"
    fi
done

echo "✅ All maintenance checklists updated!"
echo ""
echo "Summary of changes:"
echo "1. Replaced institutional_memory with memory server"
echo "2. Added warnings about JSON errors"
echo "3. Added fallback instructions for direct file access"
echo "4. Added reference to MCP_CRITICAL_NOTES_ALL_AGENTS.md"