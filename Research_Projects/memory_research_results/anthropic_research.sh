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
