#!/usr/bin/env python3
"""
Simple Claude Code MCP Server - Local Demo
"""
import asyncio
import logging
import threading
from typing import Dict, Any

import structlog
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = structlog.get_logger(__name__)

# Create FastMCP server
mcp = FastMCP("Claude-Code-Local")

# Health check FastAPI app
health_app = FastAPI()

@health_app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Claude Code MCP Server", "version": "local-demo"}

@health_app.get("/ready")
async def ready_check():
    return {"status": "ready", "mcp_server": "active"}

# MCP Tools
@mcp.tool()
def list_files(directory: str = ".") -> Dict[str, Any]:
    """List files in a directory."""
    import os
    try:
        files = []
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            files.append({
                "name": item,
                "type": "directory" if os.path.isdir(path) else "file",
                "size": os.path.getsize(path) if os.path.isfile(path) else None
            })
        return {
            "directory": directory,
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def read_file(file_path: str) -> Dict[str, Any]:
    """Read contents of a file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return {
            "file_path": file_path,
            "content": content[:1000] + "..." if len(content) > 1000 else content,
            "size": len(content)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    import platform
    import os
    return {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "architecture": platform.machine(),
        "current_directory": os.getcwd(),
        "user": os.getenv('USER', 'unknown')
    }

def run_health_server():
    """Run health check server in background thread."""
    uvicorn.run(health_app, host="127.0.0.1", port=8082, log_level="info")

def main():
    """Main function to start the MCP server."""
    logger.info("🚀 Starting Claude Code MCP Server (Local Demo)")
    logger.info("📊 Health endpoints: http://localhost:8082/health")
    logger.info("🔧 MCP Tools: list_files, read_file, get_system_info")
    
    try:
        # Start health server in background thread
        health_thread = threading.Thread(target=run_health_server, daemon=True)
        health_thread.start()
        logger.info("✅ Health server started on http://localhost:8082")
        
        # Start MCP server on stdio transport
        logger.info("🔗 Starting MCP server on stdio transport...")
        logger.info("💡 Connect with: echo '{}' | python simple_mcp_server.py")
        
        # Run MCP server (synchronous for stdio)
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested")
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        raise

if __name__ == "__main__":
    main()