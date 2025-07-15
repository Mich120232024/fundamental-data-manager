#!/usr/bin/env python3
"""
Generate a quick AI news report with real updates
"""
import asyncio
import os
from datetime import datetime, timezone
from claude_code_sdk import query, ClaudeCodeOptions
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

async def generate_quick_report():
    """Generate a quick AI news report"""
    print("🚀 Generating Quick AI News Report")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Claude SDK setup
    options = ClaudeCodeOptions(
        system_prompt="You are an AI industry analyst. Provide concise, factual updates about AI developments from the last week. Focus on real, verifiable news."
    )
    
    # Quick check for all providers in one prompt
    prompt = """
    Check for the latest AI industry updates from the past week (focus on real, announced developments):
    
    1. **Anthropic/Claude**: Any new models, features, or announcements?
    2. **OpenAI**: GPT updates, new features, or API changes?
    3. **Google**: Gemini updates, Vertex AI, or other AI products?
    4. **Microsoft**: Azure AI, Copilot, or AI infrastructure updates?
    5. **Meta**: Llama updates or AI research?
    6. **Others**: xAI, Mistral, Cohere, or emerging players?
    
    For each provider with updates:
    - List the specific announcement/update
    - Include the date if known
    - Keep it factual and brief (2-3 bullets max per provider)
    
    If a provider has no significant updates, skip them.
    Format as markdown with clear sections.
    """
    
    print("\n🔍 Checking for AI industry updates...")
    updates = ""
    async for message in query(prompt=prompt, options=options):
        if hasattr(message, 'content') and message.content:
            for block in message.content:
                if hasattr(block, 'text'):
                    updates += block.text
    
    # Generate executive summary
    print("\n📝 Generating executive summary...")
    summary_prompt = f"""
    Based on these AI industry updates, create a brief executive summary:
    
    {updates}
    
    Include:
    1. Top 3-4 most significant developments
    2. Key industry trend (1-2 sentences)
    3. One actionable recommendation for our team
    
    Keep it under 150 words total.
    """
    
    summary = ""
    async for message in query(prompt=summary_prompt, options=options):
        if hasattr(message, 'content') and message.content:
            for block in message.content:
                if hasattr(block, 'text'):
                    summary += block.text
    
    # Create report
    report = {
        "summary": summary,
        "detailed_updates": updates,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report_type": "quick_scan"
    }
    
    # Display the report
    print("\n" + "="*80)
    print("📧 AI INDUSTRY UPDATE - QUICK SCAN")
    print("="*80)
    print(f"📅 Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("="*80)
    
    print("\n📋 EXECUTIVE SUMMARY:")
    print("-"*80)
    print(summary)
    print("-"*80)
    
    print("\n📰 DETAILED UPDATES:")
    print("-"*80)
    print(updates)
    print("-"*80)
    
    # Save to Cosmos DB
    print("\n💾 Saving to Cosmos DB...")
    try:
        cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_KEY")
        
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        container = database.get_container_client("system_inbox")
        
        message = {
            "id": f"ai-news-quick-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "partitionKey": "AI_NEWS_MONITOR",
            "messageType": "AI_NEWS_QUICK_SCAN",
            "sender": {
                "name": "AI_NEWS_MONITOR",
                "role": "Quick Scanner"
            },
            "recipients": ["HEAD_OF_RESEARCH", "HEAD_OF_ENGINEERING"],
            "subject": f"🚀 AI Industry Quick Scan - {datetime.now().strftime('%B %d, %Y')}",
            "content": report,
            "priority": "NORMAL",
            "status": "UNREAD",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        container.create_item(body=message)
        print(f"✅ Saved to Cosmos DB: {message['id']}")
        
    except Exception as e:
        print(f"❌ Error saving to Cosmos: {e}")
        # Save locally as backup
        with open("quick_ai_news_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        print("💾 Saved locally to quick_ai_news_report.json")
    
    print("\n✅ Quick report complete!")

if __name__ == "__main__":
    asyncio.run(generate_quick_report())