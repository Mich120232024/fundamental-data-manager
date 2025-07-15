#!/usr/bin/env python3
"""
Claude Code MCP Server
Exposes Claude Code functionality via Model Context Protocol
"""
import asyncio
import json
import os
import subprocess
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# We'll use the basic MCP server pattern since FastMCP might not be available
from mcp.server import Server, StdioServerTransport
from mcp.server.models import Tool, Resource, Prompt
from mcp.types import TextContent, ImageContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeCodeMCPServer:
    """MCP Server that wraps Claude Code CLI functionality"""
    
    def __init__(self):
        self.server = Server("claude-code-mcp-server")
        self.setup_handlers()
        
    def setup_handlers(self):
        """Register MCP handlers"""
        # Tools
        self.server.register_tool(
            "execute_task",
            self.execute_task,
            description="Execute a Claude Code task",
            input_schema={
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "The task to execute"},
                    "context": {"type": "object", "description": "Optional context"},
                    "model": {"type": "string", "default": "sonnet"}
                },
                "required": ["task"]
            }
        )
        
        self.server.register_tool(
            "analyze_database",
            self.analyze_database,
            description="Analyze Cosmos DB data with Claude Code",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Database query to analyze"}
                },
                "required": ["query"]
            }
        )
        
        self.server.register_tool(
            "design_architecture",
            self.design_architecture,
            description="Design system architecture using Claude Code",
            input_schema={
                "type": "object",
                "properties": {
                    "requirements": {"type": "string", "description": "System requirements"}
                },
                "required": ["requirements"]
            }
        )
        
        self.server.register_tool(
            "analyze_code",
            self.analyze_code,
            description="Analyze code repository",
            input_schema={
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "Repository path"},
                    "analysis_type": {"type": "string", "default": "general"}
                },
                "required": ["repo_path"]
            }
        )
        
        # Resources
        self.server.register_resource(
            "workspace://{path}",
            self.get_workspace_content,
            description="Get content from workspace"
        )
        
        # Prompts
        self.server.register_prompt(
            "code_review",
            self.code_review_prompt,
            description="Generate a code review prompt"
        )
        
        self.server.register_prompt(
            "architecture_doc",
            self.architecture_doc_prompt,
            description="Generate architecture documentation prompt"
        )
    
    async def execute_task(self, task: str, context: Optional[Dict] = None, model: str = "sonnet") -> Dict:
        """Execute a Claude Code task"""
        try:
            # Build command
            cmd = [
                "claude",
                "--print",
                "--output-format", "json",
                "--model", model,
                "--dangerously-skip-permissions"
            ]
            
            # Add allowed tools
            cmd.extend(["--allowedTools", "filesystem,azure,github,memory"])
            
            # Create prompt with context if provided
            prompt = task
            if context:
                prompt = f"Context: {json.dumps(context)}\n\nTask: {task}"
            
            # Execute Claude Code
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(prompt.encode())
            
            if process.returncode != 0:
                raise Exception(f"Claude Code error: {stderr.decode()}")
            
            result = json.loads(stdout.decode())
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def analyze_database(self, query: str) -> Dict:
        """Analyze database query"""
        task = f"Analyze this Cosmos DB query and provide insights: {query}"
        return await self.execute_task(task)
    
    async def design_architecture(self, requirements: str) -> Dict:
        """Design system architecture"""
        task = f"Design a system architecture for these requirements: {requirements}"
        return await self.execute_task(task)
    
    async def analyze_code(self, repo_path: str, analysis_type: str = "general") -> Dict:
        """Analyze code repository"""
        task = f"Analyze the code repository at {repo_path} for {analysis_type}"
        return await self.execute_task(task)
    
    async def get_workspace_content(self, path: str) -> Dict:
        """Get content from workspace"""
        try:
            workspace_path = f"/workspace/{path}"
            if os.path.exists(workspace_path):
                with open(workspace_path, 'r') as f:
                    content = f.read()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": content,
                            "mimeType": "text/plain"
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"File not found: {path}"
                        }
                    ],
                    "isError": True
                }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error reading file: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def code_review_prompt(self, code: str) -> Dict:
        """Generate code review prompt"""
        return {
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Please review the following code and provide feedback on:\n"
                                f"1. Code quality and best practices\n"
                                f"2. Potential bugs or issues\n"
                                f"3. Performance considerations\n"
                                f"4. Security concerns\n\n"
                                f"Code:\n```\n{code}\n```"
                    }
                }
            ]
        }
    
    async def architecture_doc_prompt(self, description: str) -> Dict:
        """Generate architecture documentation prompt"""
        return {
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Create comprehensive architecture documentation for:\n{description}\n\n"
                                f"Include:\n"
                                f"1. System overview\n"
                                f"2. Component diagram\n"
                                f"3. Data flow\n"
                                f"4. Technology stack\n"
                                f"5. Deployment architecture\n"
                                f"6. Security considerations"
                    }
                }
            ]
        }
    
    async def run(self):
        """Run the MCP server"""
        # For stdio transport (default)
        transport = StdioServerTransport()
        await self.server.connect(transport)
        logger.info("Claude Code MCP Server started on stdio")
        await transport.serve()


# Alternative HTTP-based MCP server using FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn

app = FastAPI(title="Claude Code MCP HTTP Server")

# Store server instance
mcp_server = None

@app.on_event("startup")
async def startup():
    global mcp_server
    mcp_server = ClaudeCodeMCPServer()
    logger.info("Claude Code MCP HTTP Server started")

@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """Handle MCP requests over HTTP"""
    # This would need the MCP HTTP transport implementation
    # For now, we'll use the stdio version
    body = await request.json()
    
    # Route to appropriate handler based on request type
    if body.get("method") == "tools/call":
        tool_name = body.get("params", {}).get("name")
        arguments = body.get("params", {}).get("arguments", {})
        
        # Map to our tools
        if tool_name == "execute_task":
            result = await mcp_server.execute_task(**arguments)
        elif tool_name == "analyze_database":
            result = await mcp_server.analyze_database(**arguments)
        elif tool_name == "design_architecture":
            result = await mcp_server.design_architecture(**arguments)
        elif tool_name == "analyze_code":
            result = await mcp_server.analyze_code(**arguments)
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        return {"result": result}
    
    return {"error": "Unsupported method"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "claude-code-mcp-server"}


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # Run HTTP server
        uvicorn.run(app, host="0.0.0.0", port=8080)
    else:
        # Run stdio server (default)
        server = ClaudeCodeMCPServer()
        asyncio.run(server.run())