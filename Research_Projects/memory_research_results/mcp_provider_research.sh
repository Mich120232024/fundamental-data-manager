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
