#!/usr/bin/env python3
"""
Quick Claude SDK demo - Ready to use!
"""
import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def main():
    print("🚀 Claude SDK is working!")
    print("-" * 40)
    
    # Example 1: Simple query
    print("\nExample 1: Math calculation")
    async for msg in query(prompt="Calculate: 42 * 3"):
        if hasattr(msg, 'content') and msg.content:
            for block in msg.content:
                if hasattr(block, 'text'):
                    print(f"Result: {block.text}")
    
    # Example 2: With options
    print("\nExample 2: Custom system prompt")
    options = ClaudeCodeOptions(
        system_prompt="You are a helpful but very concise assistant."
    )
    
    async for msg in query(prompt="What is Python?", options=options):
        if hasattr(msg, 'content') and msg.content:
            for block in msg.content:
                if hasattr(block, 'text'):
                    print(f"Answer: {block.text}")
    
    print("\n✅ SDK is ready for automation!")
    print("\nYou can now:")
    print("- Automate agent tasks")
    print("- Batch process queries")
    print("- Build Azure integration bridges")
    print("- Create cost-optimized routing")

if __name__ == "__main__":
    asyncio.run(main())