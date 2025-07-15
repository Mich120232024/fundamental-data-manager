#!/usr/bin/env python3
"""
Claude Code MCP Server - Production Quality Implementation
Exposes Claude Code functionality via Model Context Protocol
"""
import asyncio
import json
import os
import subprocess
import sys
from typing import Dict, List, Optional, Any, Sequence
from datetime import datetime
import logging

# MCP imports - using the pattern from official examples
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import Server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        Prompt,
        PromptMessage,
        CallToolRequest,
        CallToolResult,
        ListResourcesRequest,
        ListResourcesResult,
        ListToolsRequest,
        ListToolsResult,
        ListPromptsRequest,
        ListPromptsResult,
        GetPromptRequest,
        GetPromptResult,
        ReadResourceRequest,
        ReadResourceResult,
        LATEST_PROTOCOL_VERSION,
    )
    import mcp.server.stdio
except ImportError:
    print("MCP SDK not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    # Re-import after installation
    from mcp.server.models import InitializationOptions
    from mcp.server import Server
    from mcp.types import *
    import mcp.server.stdio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClaudeCodeMCPServer:
    """Production MCP Server wrapping Claude Code CLI functionality"""
    
    def __init__(self):
        self.server = Server("claude-code-mcp-server")
        self._workspace_path = os.environ.get("CLAUDE_WORKSPACE", "/workspace")
        self._setup_handlers()
        self._claude_available = self._check_claude_cli()
        
    def _check_claude_cli(self) -> bool:
        """Check if Claude CLI is available"""
        try:
            result = subprocess.run(
                ["claude", "--version"], 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                logger.info(f"Claude CLI available: {result.stdout.strip()}")
                return True
        except Exception as e:
            logger.error(f"Claude CLI not found: {e}")
        return False
    
    def _setup_handlers(self):
        """Register all MCP protocol handlers"""
        
        # Initialization
        @self.server.initialize
        async def handle_initialize(
            protocol_version: str,
            capabilities: Dict,
            client_info: Optional[Dict] = None
        ) -> InitializationOptions:
            logger.info(f"Initializing with protocol version: {protocol_version}")
            return InitializationOptions(
                server_name="claude-code-mcp-server",
                server_version="1.0.0",
                capabilities=self.server.get_capabilities(
                    notification_options={},
                    experimental_capabilities={}
                )
            )
        
        # Tool handlers
        @self.server.list_tools
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name="execute_task",
                    description="Execute a Claude Code task with full capabilities",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "The task to execute"
                            },
                            "context": {
                                "type": "object",
                                "description": "Optional context for the task"
                            },
                            "model": {
                                "type": "string",
                                "description": "Model to use (sonnet, opus, etc)",
                                "default": "sonnet"
                            },
                            "allow_tools": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tools to allow",
                                "default": ["filesystem", "azure", "github", "memory"]
                            }
                        },
                        "required": ["task"]
                    }
                ),
                Tool(
                    name="analyze_database",
                    description="Analyze Cosmos DB data and provide insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Database query to analyze"
                            },
                            "database_type": {
                                "type": "string",
                                "description": "Type of database",
                                "default": "cosmos_db"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="design_architecture",
                    description="Design system architecture based on requirements",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "requirements": {
                                "type": "string",
                                "description": "System requirements and constraints"
                            },
                            "architecture_type": {
                                "type": "string",
                                "description": "Type of architecture (microservices, monolithic, etc)",
                                "default": "microservices"
                            }
                        },
                        "required": ["requirements"]
                    }
                ),
                Tool(
                    name="analyze_code",
                    description="Analyze code repository for quality, security, and improvements",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Repository path to analyze"
                            },
                            "analysis_type": {
                                "type": "string",
                                "description": "Type of analysis (security, performance, quality, etc)",
                                "default": "comprehensive"
                            },
                            "include_suggestions": {
                                "type": "boolean",
                                "description": "Include improvement suggestions",
                                "default": True
                            }
                        },
                        "required": ["repo_path"]
                    }
                ),
                Tool(
                    name="generate_documentation",
                    description="Generate documentation for code or systems",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "target": {
                                "type": "string",
                                "description": "Target to document (file path, system name, etc)"
                            },
                            "doc_type": {
                                "type": "string",
                                "description": "Type of documentation (api, architecture, user, etc)",
                                "default": "comprehensive"
                            }
                        },
                        "required": ["target"]
                    }
                )
            ]
        
        @self.server.call_tool
        async def handle_call_tool(
            name: str,
            arguments: Optional[Dict[str, Any]] = None
        ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            if not self._claude_available:
                return [TextContent(
                    type="text",
                    text="Error: Claude CLI is not available in this environment"
                )]
            
            try:
                if name == "execute_task":
                    result = await self._execute_task(**arguments)
                elif name == "analyze_database":
                    result = await self._analyze_database(**arguments)
                elif name == "design_architecture":
                    result = await self._design_architecture(**arguments)
                elif name == "analyze_code":
                    result = await self._analyze_code(**arguments)
                elif name == "generate_documentation":
                    result = await self._generate_documentation(**arguments)
                else:
                    result = f"Unknown tool: {name}"
                
                return [TextContent(type="text", text=result)]
                
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]
        
        # Resource handlers
        @self.server.list_resources
        async def handle_list_resources() -> List[Resource]:
            resources = []
            
            # List workspace files
            for root, dirs, files in os.walk(self._workspace_path):
                for file in files:
                    rel_path = os.path.relpath(
                        os.path.join(root, file), 
                        self._workspace_path
                    )
                    resources.append(Resource(
                        uri=f"workspace://{rel_path}",
                        name=rel_path,
                        description=f"File in workspace: {rel_path}",
                        mimeType=self._get_mime_type(file)
                    ))
            
            # Add special resources
            resources.extend([
                Resource(
                    uri="claude://status",
                    name="Claude Code Status",
                    description="Current status of Claude Code CLI",
                    mimeType="application/json"
                ),
                Resource(
                    uri="claude://capabilities",
                    name="Claude Code Capabilities",
                    description="Available Claude Code tools and features",
                    mimeType="application/json"
                )
            ])
            
            return resources
        
        @self.server.read_resource
        async def handle_read_resource(uri: str) -> str:
            if uri.startswith("workspace://"):
                path = uri[12:]  # Remove 'workspace://'
                full_path = os.path.join(self._workspace_path, path)
                
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    with open(full_path, 'r') as f:
                        return f.read()
                else:
                    raise ValueError(f"File not found: {path}")
                    
            elif uri == "claude://status":
                status = {
                    "available": self._claude_available,
                    "workspace": self._workspace_path,
                    "version": await self._get_claude_version()
                }
                return json.dumps(status, indent=2)
                
            elif uri == "claude://capabilities":
                capabilities = {
                    "tools": ["filesystem", "azure", "github", "memory", "cosmos_db"],
                    "models": ["sonnet", "opus", "haiku"],
                    "features": [
                        "code_analysis",
                        "architecture_design",
                        "database_operations",
                        "documentation_generation"
                    ]
                }
                return json.dumps(capabilities, indent=2)
            
            else:
                raise ValueError(f"Unknown resource URI: {uri}")
        
        # Prompt handlers
        @self.server.list_prompts
        async def handle_list_prompts() -> List[Prompt]:
            return [
                Prompt(
                    name="code_review",
                    description="Comprehensive code review prompt",
                    arguments=[
                        {
                            "name": "code",
                            "description": "Code to review",
                            "required": True
                        },
                        {
                            "name": "focus_areas",
                            "description": "Specific areas to focus on",
                            "required": False
                        }
                    ]
                ),
                Prompt(
                    name="architecture_design",
                    description="System architecture design prompt",
                    arguments=[
                        {
                            "name": "requirements",
                            "description": "System requirements",
                            "required": True
                        },
                        {
                            "name": "constraints",
                            "description": "Technical constraints",
                            "required": False
                        }
                    ]
                ),
                Prompt(
                    name="database_optimization",
                    description="Database query optimization prompt",
                    arguments=[
                        {
                            "name": "query",
                            "description": "Query to optimize",
                            "required": True
                        },
                        {
                            "name": "schema",
                            "description": "Database schema",
                            "required": False
                        }
                    ]
                )
            ]
        
        @self.server.get_prompt
        async def handle_get_prompt(
            name: str,
            arguments: Optional[Dict[str, str]] = None
        ) -> GetPromptResult:
            if name == "code_review":
                code = arguments.get("code", "")
                focus_areas = arguments.get("focus_areas", "all aspects")
                
                return GetPromptResult(
                    description="Comprehensive code review",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"""Please perform a comprehensive code review focusing on {focus_areas}.

Code to review:
```
{code}
```

Analyze for:
1. Code quality and best practices
2. Potential bugs and edge cases
3. Performance optimization opportunities
4. Security vulnerabilities
5. Maintainability and readability
6. Testing recommendations

Provide specific, actionable feedback with examples."""
                            )
                        )
                    ]
                )
                
            elif name == "architecture_design":
                requirements = arguments.get("requirements", "")
                constraints = arguments.get("constraints", "none specified")
                
                return GetPromptResult(
                    description="System architecture design",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"""Design a comprehensive system architecture based on these requirements:

Requirements:
{requirements}

Constraints:
{constraints}

Please provide:
1. High-level architecture overview
2. Component breakdown with responsibilities
3. Data flow and storage design
4. API design and integration points
5. Security architecture
6. Scalability and performance considerations
7. Deployment strategy
8. Technology recommendations with justifications

Include diagrams where appropriate using Mermaid or ASCII art."""
                            )
                        )
                    ]
                )
                
            elif name == "database_optimization":
                query = arguments.get("query", "")
                schema = arguments.get("schema", "not provided")
                
                return GetPromptResult(
                    description="Database query optimization",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"""Optimize this database query for performance:

Query:
```sql
{query}
```

Schema information:
{schema}

Please analyze and provide:
1. Query execution plan analysis
2. Performance bottlenecks identification
3. Optimized query versions
4. Index recommendations
5. Schema optimization suggestions
6. Caching strategies
7. Expected performance improvements

Consider both read and write performance impacts."""
                            )
                        )
                    ]
                )
            
            else:
                raise ValueError(f"Unknown prompt: {name}")
    
    async def _execute_task(
        self,
        task: str,
        context: Optional[Dict] = None,
        model: str = "sonnet",
        allow_tools: List[str] = None
    ) -> str:
        """Execute a Claude Code task"""
        if allow_tools is None:
            allow_tools = ["filesystem", "azure", "github", "memory"]
        
        cmd = [
            "claude",
            "--print",
            "--output-format", "json",
            "--model", model,
            "--dangerously-skip-permissions",
            "--allowedTools", ",".join(allow_tools)
        ]
        
        # Build prompt
        prompt = task
        if context:
            prompt = f"Context:\n{json.dumps(context, indent=2)}\n\nTask:\n{task}"
        
        logger.info(f"Executing Claude Code task: {task[:100]}...")
        
        # Execute
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self._workspace_path
        )
        
        stdout, stderr = await process.communicate(prompt.encode())
        
        if process.returncode != 0:
            error_msg = stderr.decode()
            logger.error(f"Claude Code error: {error_msg}")
            return f"Error executing task: {error_msg}"
        
        try:
            result = json.loads(stdout.decode())
            return json.dumps(result, indent=2)
        except json.JSONDecodeError:
            # Return raw output if not JSON
            return stdout.decode()
    
    async def _analyze_database(
        self,
        query: str,
        database_type: str = "cosmos_db"
    ) -> str:
        """Analyze database query"""
        task = f"""Analyze this {database_type} query and provide comprehensive insights:

Query:
{query}

Please provide:
1. Query explanation and what it does
2. Performance analysis and potential bottlenecks
3. Optimization suggestions
4. Security considerations
5. Best practices recommendations
"""
        return await self._execute_task(task)
    
    async def _design_architecture(
        self,
        requirements: str,
        architecture_type: str = "microservices"
    ) -> str:
        """Design system architecture"""
        task = f"""Design a {architecture_type} architecture for these requirements:

{requirements}

Create a comprehensive architecture design including:
1. System overview and components
2. Technology stack recommendations
3. Data architecture
4. API design
5. Security architecture
6. Deployment strategy
7. Scalability considerations
8. Cost estimates
"""
        return await self._execute_task(task)
    
    async def _analyze_code(
        self,
        repo_path: str,
        analysis_type: str = "comprehensive",
        include_suggestions: bool = True
    ) -> str:
        """Analyze code repository"""
        task = f"""Perform a {analysis_type} analysis of the code repository at: {repo_path}

Focus on:
1. Code quality and maintainability
2. Security vulnerabilities
3. Performance issues
4. Architecture patterns
5. Testing coverage
6. Documentation quality
"""
        if include_suggestions:
            task += "\n7. Provide specific improvement suggestions with code examples"
            
        return await self._execute_task(task)
    
    async def _generate_documentation(
        self,
        target: str,
        doc_type: str = "comprehensive"
    ) -> str:
        """Generate documentation"""
        task = f"""Generate {doc_type} documentation for: {target}

Include:
1. Overview and purpose
2. Architecture/structure
3. API documentation (if applicable)
4. Usage examples
5. Configuration options
6. Deployment instructions
7. Troubleshooting guide
"""
        return await self._execute_task(task)
    
    async def _get_claude_version(self) -> str:
        """Get Claude CLI version"""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unavailable"
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type for file"""
        ext = os.path.splitext(filename)[1].lower()
        mime_types = {
            '.py': 'text/x-python',
            '.js': 'text/javascript',
            '.ts': 'text/typescript',
            '.json': 'application/json',
            '.yaml': 'text/yaml',
            '.yml': 'text/yaml',
            '.md': 'text/markdown',
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.css': 'text/css',
            '.sql': 'text/x-sql',
            '.sh': 'text/x-shellscript',
            '.dockerfile': 'text/x-dockerfile',
        }
        return mime_types.get(ext, 'text/plain')


async def main():
    """Main entry point"""
    logger.info("Starting Claude Code MCP Server...")
    
    server = ClaudeCodeMCPServer()
    
    # Run with stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="claude-code-mcp-server",
                server_version="1.0.0"
            )
        )


if __name__ == "__main__":
    asyncio.run(main())