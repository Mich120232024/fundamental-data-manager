#!/bin/bash
# Create missing personal memory JSON files for MCP memory servers
# Date: 2025-07-07
# Purpose: Bootstrap personal memory files for dual memory system

echo "Creating personal memory files for all agents..."

# Define the base directory
BASE_DIR="/Users/mikaeleage/.claude"

# Create personal memory files for each agent
agents=(
    "head_of_research"
    "head_of_engineering"
    "data_analyst"
    "azure_infrastructure"
    "full_stack_engineer"
    "research_advanced"
    "research_strategy"
    "research_quantitative"
    "audit_agent"
)

# Create each file with minimal valid JSON
for agent in "${agents[@]}"; do
    file_path="${BASE_DIR}/personal_memory_${agent}.json"
    if [ ! -f "$file_path" ]; then
        echo '{"entities": []}' > "$file_path"
        echo "✅ Created: $file_path"
    else
        echo "⏭️  Exists: $file_path"
    fi
done

# Also check for the software research analyst file name mismatch
if [ -f "${BASE_DIR}/agent_memory_software_research_analyst.json" ]; then
    echo "📝 Note: Found existing agent_memory_software_research_analyst.json"
    echo "   This might need to be renamed to personal_memory_software_research.json"
fi

# List all memory files
echo -e "\n📊 All memory files in ${BASE_DIR}:"
ls -la ${BASE_DIR}/*.json | grep -E "(institutional|personal|agent)_memory"

echo -e "\n✅ Personal memory file creation complete!"
echo "🔄 Next step: Restart Claude Code to reload MCP servers"