#!/usr/bin/env python3
"""
Simple MCP Server Test - Direct Tool Testing
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import our MCP server directly
from mcp_demo import list_files, get_system_info, read_small_file

def test_tools():
    """Test all MCP tools directly."""
    print("🧪 Direct MCP Tool Testing")
    print("=" * 40)
    
    # Test 1: System Info
    print("\n1️⃣ Testing get_system_info():")
    try:
        result = get_system_info()
        print("✅ Success!")
        for key, value in result.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: List Files
    print("\n2️⃣ Testing list_files():")
    try:
        result = list_files(".")
        print("✅ Success!")
        print(f"   Directory: {result['directory']}")
        print(f"   File count: {result['count']}")
        print("   First 5 files:")
        for file in result.get('files', [])[:5]:
            print(f"     - {file['name']} ({file['type']})")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Read File
    print("\n3️⃣ Testing read_small_file():")
    try:
        result = read_small_file("mcp_demo.py")
        print("✅ Success!")
        print(f"   File: {result['file_path']}")
        print(f"   Content length: {len(result.get('content', ''))}")
        print(f"   Truncated: {result.get('truncated', False)}")
        print("   First 100 chars:")
        print(f"   {result.get('content', '')[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    test_tools()