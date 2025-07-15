#!/usr/bin/env python3
"""
Quick test - Check just Anthropic for AI news
"""
import asyncio
import os
from datetime import datetime
from claude_code_sdk import query, ClaudeCodeOptions
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_anthropic_news():
    """Quick test - just check Anthropic"""
    print("🚀 AI News Monitor - Quick Test")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Claude SDK setup
    options = ClaudeCodeOptions(
        system_prompt="You are an AI news analyst. Be very concise - just bullet points."
    )
    
    # Check Anthropic
    print("\n🔍 Checking Anthropic (Claude)...")
    prompt = """
    Check for Anthropic/Claude updates from the last 48 hours:
    - New models or features
    - API changes
    - Important announcements
    
    If no updates, say "No significant updates." Be VERY brief.
    """
    
    updates = ""
    async for message in query(prompt=prompt, options=options):
        if hasattr(message, 'content') and message.content:
            for block in message.content:
                if hasattr(block, 'text'):
                    updates += block.text
    
    print("\n📰 Updates found:")
    print(updates)
    
    # Save to Cosmos DB
    print("\n💾 Saving to Cosmos DB...")
    try:
        cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_KEY")
        
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        container = database.get_container_client("system_inbox")
        
        message = {
            "id": f"ai-news-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "partitionKey": "AI_NEWS_MONITOR",
            "messageType": "AI_NEWS_TEST",
            "sender": {"name": "AI_NEWS_MONITOR", "role": "Test"},
            "recipients": ["HEAD_OF_RESEARCH"],
            "subject": f"AI News Test - {datetime.now().strftime('%B %d, %Y')}",
            "content": {
                "anthropic_updates": updates,
                "test_run": True
            },
            "timestamp": datetime.now().isoformat()
        }
        
        container.create_item(body=message)
        print(f"✅ Saved to Cosmos: {message['id']}")
        
    except Exception as e:
        print(f"❌ Cosmos error: {e}")
        # Save locally
        with open("ai_news_test.json", 'w') as f:
            json.dump({"updates": updates}, f, indent=2)
        print("💾 Saved locally to ai_news_test.json")
    
    print("\n✅ Test complete!")
    print("\nYour first AI news report is ready!")
    print("Check Cosmos DB system_inbox for the message")

if __name__ == "__main__":
    import json
    asyncio.run(test_anthropic_news())