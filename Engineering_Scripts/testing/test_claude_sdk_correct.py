#!/usr/bin/env python3
"""
Test Claude SDK installation and basic functionality
"""
import asyncio
import os
from claude_code_sdk import query, ClaudeCodeOptions, PermissionMode

async def test_basic_query():
    """Test basic SDK query"""
    print("🔍 Testing Claude SDK query...")
    
    try:
        # Simple query test
        print("\n📝 Running simple query...")
        messages = []
        
        async for message in query(prompt="What is 2 + 2? Just give me the number."):
            messages.append(message)
            print(f"Message type: {type(message).__name__}")
            if hasattr(message, 'content'):
                print(f"Content: {message.content}")
        
        print(f"\n✅ Received {len(messages)} messages")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

async def test_with_options():
    """Test query with options"""
    print("\n🔧 Testing query with options...")
    
    try:
        # Create options
        options = ClaudeCodeOptions(
            system_prompt="You are a helpful assistant. Be very concise.",
            cwd="/Users/mikaeleage/Research & Analytics Services",
            permission_mode=PermissionMode.bypass_permissions  # For testing
        )
        
        messages = []
        async for message in query(
            prompt="List the files in the current directory (just show first 3)",
            options=options
        ):
            messages.append(message)
            if hasattr(message, 'content'):
                print(f"Content: {message.content[:100]}...")  # First 100 chars
        
        print(f"✅ Query with options completed")
        
    except Exception as e:
        print(f"❌ Query with options failed: {e}")

async def test_tool_use():
    """Test tool usage through SDK"""
    print("\n🛠️  Testing tool usage...")
    
    try:
        options = ClaudeCodeOptions(
            permission_mode=PermissionMode.bypass_permissions,
            cwd="/Users/mikaeleage/Research & Analytics Services"
        )
        
        async for message in query(
            prompt="Create a file called test_sdk_file.txt with content 'Hello from SDK'",
            options=options
        ):
            if hasattr(message, 'content'):
                print(f"Response: {message.content[:100]}...")
        
        # Check if file was created
        if os.path.exists("/Users/mikaeleage/Research & Analytics Services/test_sdk_file.txt"):
            print("✅ File created successfully!")
            # Clean up
            os.remove("/Users/mikaeleage/Research & Analytics Services/test_sdk_file.txt")
            print("🧹 Test file cleaned up")
        else:
            print("⚠️  File creation might have failed")
            
    except Exception as e:
        print(f"❌ Tool usage test failed: {e}")

async def main():
    """Run all tests"""
    print("=" * 50)
    print("CLAUDE SDK TEST SUITE")
    print("=" * 50)
    
    # Check if Claude Code CLI is running
    try:
        # Test basic query
        await test_basic_query()
        
        # Test with options
        await test_with_options()
        
        # Test tool usage
        await test_tool_use()
        
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        print("\n💡 Make sure Claude Code CLI is running:")
        print("   Run: claude --mcp-debug")
        print("   Or: claude --no-interactive")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())