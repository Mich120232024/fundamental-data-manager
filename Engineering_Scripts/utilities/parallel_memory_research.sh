#!/bin/bash
# Parallel MCP Memory Documentation Research
# Date: 2025-07-08
# Uses background processes instead of tmux

echo "🚀 Starting Parallel MCP Memory Research"
echo "========================================"
echo ""

# Create research directory
mkdir -p ~/memory_research_results
cd ~/memory_research_results

# Create research scripts for each agent
echo "📝 Creating research scripts..."

# Script 1: Anthropic Documentation Research
cat > anthropic_research.sh << 'EOF'
#!/bin/bash
echo "📚 Anthropic Docs Researcher starting..."
echo "Using model: deepseek-chat"
echo ""

# Use Claude Router to research Anthropic docs
ccr code <<'PROMPT'
/model deepseek,deepseek-chat
Research MCP memory server documentation from Anthropic. 

Search for:
- MCP memory server setup and configuration
- JSON file format requirements  
- Common parsing errors and fixes
- Memory server initialization
- How to debug "Expected property name or '}' in JSON at position 1" error

Please check:
1. https://docs.anthropic.com/en/docs/claude-code/mcp
2. Any documentation about memory servers
3. Configuration file formats

Save your findings to ~/memory_research_results/anthropic_findings.md with proper markdown formatting.
PROMPT
EOF

# Script 2: MCP Provider Documentation Research  
cat > mcp_provider_research.sh << 'EOF'
#!/bin/bash
echo "🔧 MCP Provider Researcher starting..."
echo "Using model: gemini-2.5-flash"
echo ""

# Use Claude Router to research MCP provider docs
ccr code <<'PROMPT'
/model gemini,gemini-2.5-flash
Research the official MCP server-memory documentation.

Look for:
- GitHub repo: @modelcontextprotocol/server-memory
- Configuration requirements
- JSON schema specifications
- Troubleshooting guide for parsing errors
- How memory servers handle JSON files

Focus on:
1. Proper JSON format for memory files
2. Configuration setup in MCP settings
3. Common errors and their solutions
4. Memory server initialization process

Save your findings to ~/memory_research_results/mcp_provider_findings.md with proper markdown formatting.
PROMPT
EOF

# Make scripts executable
chmod +x anthropic_research.sh
chmod +x mcp_provider_research.sh

echo "🚀 Launching parallel research agents..."
echo ""

# Launch both researchers in background
./anthropic_research.sh > anthropic_log.txt 2>&1 &
PID1=$!
echo "✅ Anthropic researcher launched (PID: $PID1)"

./mcp_provider_research.sh > mcp_provider_log.txt 2>&1 &
PID2=$!
echo "✅ MCP Provider researcher launched (PID: $PID2)"

echo ""
echo "📊 Research in progress..."
echo ""
echo "Monitor logs:"
echo "  tail -f ~/memory_research_results/anthropic_log.txt"
echo "  tail -f ~/memory_research_results/mcp_provider_log.txt"
echo ""
echo "Check process status:"
echo "  ps -p $PID1,$PID2"
echo ""
echo "📁 Results will be saved to:"
echo "  ~/memory_research_results/anthropic_findings.md"
echo "  ~/memory_research_results/mcp_provider_findings.md"
echo ""
echo "⏱️  Research typically takes 2-3 minutes..."

# Optional: Wait and show status
sleep 5
echo ""
echo "🔍 Current status:"
if ps -p $PID1 > /dev/null; then
    echo "  Anthropic researcher: Running"
else
    echo "  Anthropic researcher: Completed"
fi

if ps -p $PID2 > /dev/null; then
    echo "  MCP Provider researcher: Running"
else
    echo "  MCP Provider researcher: Completed"
fi

echo ""
echo "💡 Tip: This script demonstrates parallel processing with Claude Router!"
echo "Each agent uses a different model for diverse perspectives."

—HEAD_OF_RESEARCH