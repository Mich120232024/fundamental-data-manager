#!/usr/bin/env python3
"""
Simple Claude SDK test - working example
"""
import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def simple_test():
    """Simple working test of Claude SDK"""
    print("🚀 Claude SDK Simple Test")
    print("-" * 40)
    
    # Test 1: Basic math question
    print("\n1️⃣ Testing basic query...")
    async for message in query(prompt="What is 10 + 15? Just give the number."):
        if hasattr(message, 'content') and message.content:
            if isinstance(message.content, list):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(f"   Result: {block.text}")
    
    # Test 2: With system prompt
    print("\n2️⃣ Testing with system prompt...")
    options = ClaudeCodeOptions(
        system_prompt="You are a calculator. Only respond with numbers."
    )
    
    async for message in query(prompt="Calculate: 100 / 4", options=options):
        if hasattr(message, 'content') and message.content:
            if isinstance(message.content, list):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(f"   Result: {block.text}")
    
    # Test 3: Code analysis (no file operations)
    print("\n3️⃣ Testing code analysis...")
    code_prompt = """
    Analyze this Python function and tell me what it does in one sentence:
    
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    """
    
    async for message in query(prompt=code_prompt):
        if hasattr(message, 'content') and message.content:
            if isinstance(message.content, list):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(f"   Analysis: {block.text}")
    
    print("\n✅ All tests completed!")

async def test_streaming():
    """Test streaming responses"""
    print("\n4️⃣ Testing streaming response...")
    
    prompt = "Count from 1 to 5, showing each number on a new line"
    
    async for message in query(prompt=prompt):
        if hasattr(message, 'content') and message.content:
            if isinstance(message.content, list):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(f"   {block.text}")

async def main():
    """Run tests"""
    try:
        await simple_test()
        await test_streaming()
        
        print("\n" + "="*40)
        print("💡 SDK is working correctly!")
        print("   You can now use it for automation")
        print("="*40)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure Claude Code is installed: npm install -g @anthropic-ai/claude-code")
        print("2. The SDK connects to the local Claude Code process")
        print("3. You may need to run 'claude' in another terminal first")

if __name__ == "__main__":
    asyncio.run(main())