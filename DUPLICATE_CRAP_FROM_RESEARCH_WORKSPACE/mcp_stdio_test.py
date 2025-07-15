#!/usr/bin/env python3
"""
MCP STDIO Protocol Test - Real MCP Communication
"""
import json
import subprocess
import sys

def test_mcp_protocol():
    """Test the actual MCP protocol over stdio."""
    print("🔗 Testing MCP Protocol (stdio transport)")
    print("=" * 50)
    
    # MCP initialization request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    print("📤 Sending initialization request...")
    print(f"Request: {json.dumps(init_request, indent=2)}")
    
    try:
        # Start MCP server process
        process = subprocess.Popen(
            [sys.executable, "simple_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send request and get response
        stdout, stderr = process.communicate(
            input=json.dumps(init_request) + "\n",
            timeout=10
        )
        
        print("\n📥 Server Response:")
        if stdout.strip():
            try:
                response = json.loads(stdout.strip())
                print(json.dumps(response, indent=2))
                print("\n✅ MCP Protocol Communication: SUCCESS!")
            except json.JSONDecodeError:
                print(f"Raw output: {stdout}")
                print("⚠️ Response not valid JSON, but server responded")
        else:
            print("No stdout response")
            
        if stderr:
            print(f"\n📝 Server logs:")
            print(stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Request timed out - server might be waiting for more input")
        process.kill()
    except Exception as e:
        print(f"❌ Error: {e}")

def simple_stdio_test():
    """Simple test sending JSON to the MCP server."""
    print("\n🧪 Simple STDIO Test")
    print("=" * 30)
    
    # Simple test message
    test_message = {"test": "hello from client"}
    
    try:
        process = subprocess.Popen(
            [sys.executable, "simple_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(
            input=json.dumps(test_message) + "\n",
            timeout=5
        )
        
        print("📤 Sent:", json.dumps(test_message))
        print("📥 Response:", stdout.strip() if stdout.strip() else "No response")
        print("📝 Logs:", stderr.strip() if stderr.strip() else "No logs")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_mcp_protocol()
    simple_stdio_test()