#!/usr/bin/env python3
"""
MCP Client Test - Interactive Testing of MCP Server
"""
import json
import subprocess
import sys
from typing import Dict, Any

class MCPClient:
    def __init__(self, server_script: str):
        self.server_script = server_script
        
    def call_tool(self, tool_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call an MCP tool and return the result."""
        if parameters is None:
            parameters = {}
            
        # Create MCP request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": parameters
            }
        }
        
        try:
            # Start the MCP server process
            process = subprocess.Popen(
                [sys.executable, self.server_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send request
            stdout, stderr = process.communicate(json.dumps(request))
            
            if stderr:
                print(f"Server stderr: {stderr}")
                
            # Parse response
            if stdout.strip():
                return json.loads(stdout)
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            return {"error": f"Client error: {str(e)}"}

def interactive_test():
    """Interactive testing menu."""
    client = MCPClient("simple_mcp_server.py")
    
    print("🧪 MCP Server Interactive Test Client")
    print("=" * 50)
    
    while True:
        print("\nAvailable Tests:")
        print("1. Test system_info tool")
        print("2. Test list_files tool (current directory)")
        print("3. Test list_files tool (custom directory)")
        print("4. Test read_file tool")
        print("5. Run all tests")
        print("6. Exit")
        
        choice = input("\nSelect test (1-6): ").strip()
        
        if choice == "1":
            print("\n🔧 Testing get_system_info...")
            result = client.call_tool("get_system_info")
            print(json.dumps(result, indent=2))
            
        elif choice == "2":
            print("\n📁 Testing list_files (current directory)...")
            result = client.call_tool("list_files")
            print(json.dumps(result, indent=2))
            
        elif choice == "3":
            directory = input("Enter directory path: ").strip()
            print(f"\n📁 Testing list_files ({directory})...")
            result = client.call_tool("list_files", {"directory": directory})
            print(json.dumps(result, indent=2))
            
        elif choice == "4":
            file_path = input("Enter file path: ").strip()
            print(f"\n📄 Testing read_file ({file_path})...")
            result = client.call_tool("read_file", {"file_path": file_path})
            print(json.dumps(result, indent=2))
            
        elif choice == "5":
            print("\n🔄 Running all tests...")
            
            # Test 1: System info
            print("\n1️⃣ System Info:")
            result = client.call_tool("get_system_info")
            if "error" not in result:
                print("✅ PASS")
            else:
                print(f"❌ FAIL: {result}")
            
            # Test 2: List files
            print("\n2️⃣ List Files:")
            result = client.call_tool("list_files")
            if "error" not in result and "files" in result:
                print(f"✅ PASS (found {result.get('count', 0)} files)")
            else:
                print(f"❌ FAIL: {result}")
            
            # Test 3: Read this script
            print("\n3️⃣ Read File:")
            result = client.call_tool("read_file", {"file_path": __file__})
            if "error" not in result and "content" in result:
                print("✅ PASS")
            else:
                print(f"❌ FAIL: {result}")
                
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please select 1-6.")

def quick_test():
    """Quick automated test of all tools."""
    print("⚡ Quick MCP Server Test")
    print("=" * 30)
    
    client = MCPClient("simple_mcp_server.py")
    
    tests = [
        ("get_system_info", {}),
        ("list_files", {}),
        ("read_file", {"file_path": "mcp_demo.py"})
    ]
    
    for tool_name, params in tests:
        print(f"\nTesting {tool_name}...")
        result = client.call_tool(tool_name, params)
        
        if "error" in result:
            print(f"❌ {tool_name}: {result['error']}")
        else:
            print(f"✅ {tool_name}: Success")
            if tool_name == "list_files" and "count" in result:
                print(f"   Found {result['count']} items")
            elif tool_name == "read_file" and "size" in result:
                print(f"   Read {result['size']} characters")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        interactive_test()