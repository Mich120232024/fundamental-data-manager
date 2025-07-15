#!/usr/bin/env python3
"""
MCP HTTP Bridge - Exposes MCP stdio server via HTTP/WebSocket
Based on MCP server proxy patterns
"""
import asyncio
import json
import logging
import subprocess
import sys
import os
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPServerProxy:
    """Proxy that bridges HTTP/WebSocket to stdio MCP server"""
    
    def __init__(self, server_command: list):
        self.server_command = server_command
        self.process: Optional[subprocess.Popen] = None
        self.read_task: Optional[asyncio.Task] = None
        self.write_lock = asyncio.Lock()
        
    async def start(self):
        """Start the MCP server process"""
        logger.info(f"Starting MCP server: {' '.join(self.server_command)}")
        
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "PYTHONUNBUFFERED": "1"}
        )
        
        # Start reading stderr for logs
        asyncio.create_task(self._read_stderr())
        
    async def stop(self):
        """Stop the MCP server process"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
            
    async def _read_stderr(self):
        """Read stderr for logging"""
        if not self.process or not self.process.stderr:
            return
            
        while True:
            line = await self.process.stderr.readline()
            if not line:
                break
            logger.info(f"MCP Server: {line.decode().strip()}")
            
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the MCP server and get response"""
        if not self.process or not self.process.stdin or not self.process.stdout:
            raise RuntimeError("MCP server not running")
            
        # Send message
        async with self.write_lock:
            message_bytes = json.dumps(message).encode() + b'\n'
            self.process.stdin.write(message_bytes)
            await self.process.stdin.drain()
            
        # Read response
        response_line = await self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("MCP server closed connection")
            
        return json.loads(response_line.decode())
    
    async def handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connection for streaming"""
        await websocket.accept()
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Forward to MCP server
                response = await self.send_message(message)
                
                # Send response back
                await websocket.send_text(json.dumps(response))
                
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await websocket.close()


# Global proxy instance
proxy: Optional[MCPServerProxy] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MCP server lifecycle"""
    global proxy
    
    # Start MCP server
    proxy = MCPServerProxy([sys.executable, "/app/claude_code_mcp_server.py"])
    await proxy.start()
    
    yield
    
    # Stop MCP server
    if proxy:
        await proxy.stop()


app = FastAPI(
    title="Claude Code MCP HTTP Bridge",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "claude-code-mcp-http-bridge",
        "mcp_server": "running" if proxy and proxy.process else "stopped"
    }


@app.post("/mcp/initialize")
async def initialize(request: Dict[str, Any]):
    """Initialize MCP connection"""
    if not proxy:
        raise HTTPException(status_code=503, detail="MCP server not available")
        
    response = await proxy.send_message({
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": request,
        "id": 1
    })
    
    return response


@app.post("/mcp/tools/list")
async def list_tools():
    """List available tools"""
    if not proxy:
        raise HTTPException(status_code=503, detail="MCP server not available")
        
    response = await proxy.send_message({
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    })
    
    return response


@app.post("/mcp/tools/call")
async def call_tool(request: Dict[str, Any]):
    """Call a tool"""
    if not proxy:
        raise HTTPException(status_code=503, detail="MCP server not available")
        
    response = await proxy.send_message({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": request,
        "id": 3
    })
    
    return response


@app.post("/mcp/resources/list")
async def list_resources():
    """List available resources"""
    if not proxy:
        raise HTTPException(status_code=503, detail="MCP server not available")
        
    response = await proxy.send_message({
        "jsonrpc": "2.0",
        "method": "resources/list",
        "params": {},
        "id": 4
    })
    
    return response


@app.post("/mcp/resources/read")
async def read_resource(request: Dict[str, Any]):
    """Read a resource"""
    if not proxy:
        raise HTTPException(status_code=503, detail="MCP server not available")
        
    response = await proxy.send_message({
        "jsonrpc": "2.0",
        "method": "resources/read",
        "params": request,
        "id": 5
    })
    
    return response


@app.post("/mcp/prompts/list")
async def list_prompts():
    """List available prompts"""
    if not proxy:
        raise HTTPException(status_code=503, detail="MCP server not available")
        
    response = await proxy.send_message({
        "jsonrpc": "2.0",
        "method": "prompts/list",
        "params": {},
        "id": 6
    })
    
    return response


@app.post("/mcp/prompts/get")
async def get_prompt(request: Dict[str, Any]):
    """Get a prompt"""
    if not proxy:
        raise HTTPException(status_code=503, detail="MCP server not available")
        
    response = await proxy.send_message({
        "jsonrpc": "2.0",
        "method": "prompts/get",
        "params": request,
        "id": 7
    })
    
    return response


@app.websocket("/mcp/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming MCP communication"""
    if not proxy:
        await websocket.close(code=1003, reason="MCP server not available")
        return
        
    await proxy.handle_websocket(websocket)


# Simplified API endpoints for common operations

@app.post("/api/execute")
async def execute_task(request: Dict[str, Any]):
    """Execute a Claude Code task (simplified API)"""
    tool_request = {
        "name": "execute_task",
        "arguments": request
    }
    
    return await call_tool(tool_request)


@app.post("/api/analyze/database")
async def analyze_database(request: Dict[str, Any]):
    """Analyze database query (simplified API)"""
    tool_request = {
        "name": "analyze_database",
        "arguments": request
    }
    
    return await call_tool(tool_request)


@app.post("/api/design/architecture")
async def design_architecture(request: Dict[str, Any]):
    """Design system architecture (simplified API)"""
    tool_request = {
        "name": "design_architecture",
        "arguments": request
    }
    
    return await call_tool(tool_request)


@app.post("/api/analyze/code")
async def analyze_code(request: Dict[str, Any]):
    """Analyze code repository (simplified API)"""
    tool_request = {
        "name": "analyze_code",
        "arguments": request
    }
    
    return await call_tool(tool_request)


if __name__ == "__main__":
    # Run the HTTP bridge
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )