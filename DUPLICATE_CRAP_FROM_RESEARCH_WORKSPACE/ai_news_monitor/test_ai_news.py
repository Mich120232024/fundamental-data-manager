#!/usr/bin/env python3
"""
Test version of AI News Monitor - Quick demo
"""
import asyncio
from datetime import datetime
from claude_code_sdk import query, ClaudeCodeOptions

async def quick_ai_news_check():
    """Quick test of AI news checking"""
    print("🚀 AI News Monitor - Quick Test")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test with just 2 providers
    providers = [
        "Anthropic (Claude) - any updates to Claude models or APIs in the last week?",
        "OpenAI - any new features or model updates recently?"
    ]
    
    options = ClaudeCodeOptions(
        system_prompt="You are an AI news analyst. Be very concise - just bullet points of major updates."
    )
    
    all_updates = []
    
    for provider in providers:
        print(f"\n🔍 Checking {provider.split(' - ')[0]}...")
        
        updates = ""
        async for message in query(prompt=provider, options=options):
            if hasattr(message, 'content') and message.content:
                for block in message.content:
                    if hasattr(block, 'text'):
                        updates += block.text
        
        all_updates.append(updates)
        print(updates[:200] + "..." if len(updates) > 200 else updates)
    
    # Create summary
    print("\n📝 Creating summary...")
    summary_prompt = f"""
    Based on these updates, create a 3-line summary:
    
    Provider 1: {all_updates[0][:200]}...
    Provider 2: {all_updates[1][:200]}...
    
    Format: Just 3 key points, one per line.
    """
    
    async for message in query(prompt=summary_prompt, options=options):
        if hasattr(message, 'content') and message.content:
            for block in message.content:
                if hasattr(block, 'text'):
                    print("\n🎯 Key Highlights:")
                    print(block.text)
    
    print("\n✅ Test complete!")
    print("\nTo set up daily runs:")
    print("1. Run: chmod +x ai_news_monitor/setup_cron.sh")
    print("2. Run: ./ai_news_monitor/setup_cron.sh")
    print("3. Follow the instructions to add to crontab")

if __name__ == "__main__":
    asyncio.run(quick_ai_news_check())