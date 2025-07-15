#!/usr/bin/env python3
"""
Trigger full AI news report right now - all providers
"""
import asyncio
import os
import json
from datetime import datetime, timezone
from claude_code_sdk import query, ClaudeCodeOptions
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def trigger_full_report():
    """Run full AI news check NOW"""
    print("🚀 AI News Monitor - FULL REPORT")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Claude SDK setup
    options = ClaudeCodeOptions(
        system_prompt="You are an AI news analyst. Be concise and focus on technical updates, new features, and important announcements."
    )
    
    # All providers to check
    providers = [
        {
            "name": "Anthropic (Claude)",
            "check": "Check for Anthropic Claude updates: new models, API changes, Claude Code features"
        },
        {
            "name": "OpenAI",
            "check": "Check for OpenAI updates: GPT models, API changes, new features, ChatGPT updates"
        },
        {
            "name": "Google Gemini",
            "check": "Check for Google Gemini/Bard updates: new models, API features, Vertex AI changes"
        },
        {
            "name": "Microsoft Azure AI",
            "check": "Check for Microsoft Azure AI updates: new services, model deployments, cognitive services"
        }
    ]
    
    print(f"\n🔍 Checking {len(providers)} AI providers...")
    
    all_updates = []
    
    # Check each provider
    for i, provider in enumerate(providers, 1):
        print(f"\n[{i}/{len(providers)}] 🔍 Checking {provider['name']}...")
        
        prompt = f"""
        {provider['check']} from the last week.
        
        Look for:
        - New model releases
        - API updates or changes  
        - Major feature announcements
        - Performance improvements
        
        Format as 2-3 bullet points. If no updates, say "No significant updates this week."
        """
        
        updates = ""
        try:
            async for message in query(prompt=prompt, options=options):
                if hasattr(message, 'content') and message.content:
                    for block in message.content:
                        if hasattr(block, 'text'):
                            updates += block.text
            
            all_updates.append({
                "provider": provider['name'],
                "updates": updates,
                "checked_at": datetime.now(timezone.utc).isoformat()
            })
            
            # Show preview
            preview = updates[:100] + "..." if len(updates) > 100 else updates
            print(f"   {preview}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            all_updates.append({
                "provider": provider['name'],
                "updates": f"Error checking: {str(e)}",
                "checked_at": datetime.now(timezone.utc).isoformat()
            })
    
    # Create executive summary
    print(f"\n📝 Creating executive summary...")
    
    combined_updates = "\n\n".join([
        f"### {update['provider']}\n{update['updates']}"
        for update in all_updates
    ])
    
    summary_prompt = f"""
    Create a brief executive summary of these AI industry updates:
    
    {combined_updates}
    
    Format as:
    # AI Industry Weekly Update - {datetime.now().strftime('%B %d, %Y')}
    
    ## 🎯 Key Highlights
    (Top 3-5 most important updates across all providers)
    
    ## 📊 Industry Trends  
    (What patterns do you see?)
    
    ## 💡 Recommendations
    (What should our team pay attention to?)
    
    Keep it concise but informative.
    """
    
    summary = ""
    try:
        async for message in query(prompt=summary_prompt, options=options):
            if hasattr(message, 'content') and message.content:
                for block in message.content:
                    if hasattr(block, 'text'):
                        summary += block.text
    except Exception as e:
        summary = f"Error generating summary: {e}"
    
    # Create full report
    report = {
        "summary": summary,
        "detailed_updates": all_updates,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "providers_checked": len(providers)
    }
    
    # Save to Cosmos DB
    print(f"\n💾 Saving full report to Cosmos DB...")
    
    try:
        cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_KEY")
        
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        container = database.get_container_client("system_inbox")
        
        message_id = f"ai-news-full-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        message = {
            "id": message_id,
            "partitionKey": "AI_NEWS_MONITOR",
            "messageType": "AI_NEWS_WEEKLY_REPORT",
            "sender": {
                "name": "AI_NEWS_MONITOR",
                "role": "Automated Agent"
            },
            "recipients": ["HEAD_OF_RESEARCH", "HEAD_OF_ENGINEERING", "ALL_AGENTS"],
            "subject": f"🤖 AI Industry Weekly Update - {datetime.now().strftime('%B %d, %Y')}",
            "content": report,
            "priority": "NORMAL",
            "status": "UNREAD",
            "metadata": {
                "category": "INTELLIGENCE",
                "subcategory": "INDUSTRY_UPDATES",
                "importance": 4,
                "tags": ["ai-news", "weekly-report", "automated", "full-scan"],
                "source": "ai_news_monitor_full"
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
        
        container.create_item(body=message)
        
        print(f"✅ FULL REPORT SAVED!")
        print(f"📧 Message ID: {message_id}")
        print(f"📮 Location: Cosmos DB > system_inbox")
        print(f"📊 Providers checked: {len(providers)}")
        
        # Also save locally for review
        with open("latest_full_ai_news.json", 'w') as f:
            json.dump(message, f, indent=2)
        
        with open("latest_ai_summary.md", 'w') as f:
            f.write(summary)
        
        print(f"💾 Local copies saved:")
        print(f"   - latest_full_ai_news.json")
        print(f"   - latest_ai_summary.md")
        
    except Exception as e:
        print(f"❌ Cosmos error: {e}")
        # Fallback to local save
        filename = f"ai_news_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"💾 Saved locally: {filename}")
    
    print("\n" + "=" * 60)
    print("🎉 FULL AI NEWS REPORT COMPLETE!")
    print("📧 Check your Cosmos DB system_inbox for the email")
    print("🔄 This is what you'll get every morning at 8 AM")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(trigger_full_report())