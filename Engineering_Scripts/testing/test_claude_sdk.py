#!/usr/bin/env python3
"""
Test Claude SDK installation and basic functionality
"""
import asyncio
import os
from claude_code_sdk import ClaudeCode

async def test_basic_connection():
    """Test basic SDK connection"""
    print("🔍 Testing Claude SDK...")
    
    try:
        # Initialize Claude SDK
        claude = ClaudeCode()
        print("✅ Claude SDK imported successfully")
        
        # Test basic task
        print("\n📝 Running simple task...")
        result = await claude.run_task("What is 2 + 2?")
        print(f"Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

async def test_with_api_key():
    """Test with API key if available"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if api_key:
        print(f"\n🔑 API Key found (first 10 chars): {api_key[:10]}...")
        try:
            claude = ClaudeCode(api_key=api_key)
            print("✅ Initialized with API key")
        except Exception as e:
            print(f"❌ API key initialization failed: {e}")
    else:
        print("\n⚠️  No ANTHROPIC_API_KEY environment variable found")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key-here'")

async def test_session_creation():
    """Test session creation"""
    print("\n🔧 Testing session creation...")
    
    try:
        claude = ClaudeCode()
        
        # Try to create a session
        session = await claude.create_session(
            agent_context="test_agent"
        )
        print("✅ Session created successfully")
        
    except Exception as e:
        print(f"❌ Session creation failed: {e}")

async def main():
    """Run all tests"""
    print("=" * 50)
    print("CLAUDE SDK TEST SUITE")
    print("=" * 50)
    
    # Test basic import and connection
    success = await test_basic_connection()
    
    # Test API key setup
    await test_with_api_key()
    
    # Test session creation
    await test_session_creation()
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())