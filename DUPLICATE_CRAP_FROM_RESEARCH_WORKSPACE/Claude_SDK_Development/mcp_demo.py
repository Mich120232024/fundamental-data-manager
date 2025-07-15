#!/usr/bin/env python3
"""
MCP Server Demo - Shows Available Tools
"""
import os
import platform
from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("Claude-Code-Demo")

@mcp.tool()
def list_files(directory: str = ".") -> dict:
    """List files in a directory."""
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
            "files": files[:10],  # Limit to first 10
            "count": len(files)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_system_info() -> dict:
    """Get system information."""
    return {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "architecture": platform.machine(),
        "current_directory": os.getcwd(),
        "user": os.getenv('USER', 'unknown'),
        "home": os.getenv('HOME', 'unknown')
    }

@mcp.tool()
def read_small_file(file_path: str) -> dict:
    """Read a small file (first 500 chars)."""
    try:
        with open(file_path, 'r') as f:
            content = f.read(500)
        return {
            "file_path": file_path,
            "content": content,
            "truncated": len(open(file_path, 'r').read()) > 500
        }
    except Exception as e:
        return {"error": str(e)}

def demo_tools():
    """Demonstrate the MCP tools."""
    print("🚀 MCP Server Demo - Available Tools")
    print("=" * 50)
    
    print("\n1️⃣ System Info:")
    result = get_system_info()
    for key, value in result.items():
        print(f"   {key}: {value}")
    
    print("\n2️⃣ List Files (current directory):")
    result = list_files(".")
    print(f"   Directory: {result['directory']}")
    print(f"   Total files: {result['count']}")
    if 'files' in result:
        for file in result['files']:
            print(f"   - {file['name']} ({file['type']})")
    
    print("\n3️⃣ Read File Demo (this script):")
    result = read_small_file(__file__)
    if 'content' in result:
        print(f"   File: {result['file_path']}")
        print(f"   First 200 chars: {result['content'][:200]}...")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    print("\n✅ MCP Server Tools Working!")
    print("\n🔗 To use with Claude Code:")
    print("   1. Add this server to your MCP configuration")
    print("   2. Tools: list_files, get_system_info, read_small_file")

if __name__ == "__main__":
    demo_tools()