#!/usr/bin/env python3
"""
AI News Monitoring Agent - Local Version
Runs on your Mac with cron, uses Claude SDK
"""
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from claude_code_sdk import query, ClaudeCodeOptions
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AINewsMonitorLocal:
    def __init__(self):
        """Initialize the AI News Monitor"""
        # Claude SDK setup
        self.claude_options = ClaudeCodeOptions(
            system_prompt="You are an AI news analyst. Be concise and focus on technical updates, new features, and important announcements. Always cite specific dates when available."
        )
        
        # Cosmos DB setup (using your existing connection)
        self.cosmos_endpoint = os.getenv("COSMOS_ENDPOINT", "https://cosmos-research-analytics-prod.documents.azure.com:443/")
        self.cosmos_key = os.getenv("COSMOS_KEY")
        
        # AI providers to monitor
        self.providers = [
            {
                "name": "Anthropic (Claude)",
                "check": "Check Anthropic's website and docs for: new Claude models, API updates, Claude Code features, SDK updates"
            },
            {
                "name": "OpenAI",
                "check": "Check OpenAI's blog and platform docs for: new GPT models, API changes, new features, pricing updates"
            },
            {
                "name": "Google Gemini",
                "check": "Check Google AI blog for: Gemini updates, Vertex AI features, new models, API changes"
            },
            {
                "name": "Mistral AI",
                "check": "Check Mistral's website for: new models, API updates, performance improvements"
            },
            {
                "name": "Meta AI (Llama)",
                "check": "Check Meta AI news for: new Llama models, open source releases, research papers"
            }
        ]
    
    async def check_provider(self, provider):
        """Check a single provider for updates"""
        print(f"🔍 Checking {provider['name']}...")
        
        prompt = f"""
        {provider['check']}
        
        Look for updates from the last 48 hours. If you find updates, summarize them in 3-5 bullet points.
        If no recent updates, say "No significant updates in the past 48 hours."
        
        Be specific about what changed and when.
        """
        
        updates = ""
        async for message in query(prompt=prompt, options=self.claude_options):
            if hasattr(message, 'content') and message.content:
                for block in message.content:
                    if hasattr(block, 'text'):
                        updates += block.text
        
        return {
            "provider": provider['name'],
            "updates": updates,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def create_summary(self, all_updates):
        """Create executive summary"""
        print("\n📝 Creating summary report...")
        
        updates_text = "\n\n".join([
            f"### {u['provider']}\n{u['updates']}"
            for u in all_updates
        ])
        
        prompt = f"""
        Create a brief executive summary of these AI industry updates:
        
        {updates_text}
        
        Format:
        # AI Industry Update - {datetime.now().strftime('%B %d, %Y')}
        
        ## 🎯 Key Highlights
        (Top 3-5 most important updates)
        
        ## 📊 Trends
        (What patterns do you see?)
        
        ## 💡 Action Items
        (What should our team pay attention to?)
        
        Keep it concise but informative.
        """
        
        summary = ""
        async for message in query(prompt=prompt, options=self.claude_options):
            if hasattr(message, 'content') and message.content:
                for block in message.content:
                    if hasattr(block, 'text'):
                        summary += block.text
        
        return summary
    
    def save_to_cosmos(self, report):
        """Save report to Cosmos DB"""
        try:
            client = CosmosClient(self.cosmos_endpoint, self.cosmos_key)
            database = client.get_database_client("research-analytics-db")
            container = database.get_container_client("system_inbox")
            
            message = {
                "id": f"ai-news-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "partitionKey": "AI_NEWS_MONITOR",
                "messageType": "AI_NEWS_REPORT",
                "sender": {"name": "AI_NEWS_MONITOR", "role": "Automated Agent"},
                "recipients": ["HEAD_OF_RESEARCH", "HEAD_OF_ENGINEERING"],
                "subject": f"AI Industry Updates - {datetime.now().strftime('%B %d, %Y')}",
                "content": report,
                "priority": "NORMAL",
                "status": "UNREAD",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            container.create_item(body=message)
            print(f"✅ Saved to Cosmos DB: {message['id']}")
            return message['id']
            
        except Exception as e:
            print(f"⚠️  Cosmos DB error: {e}")
            # Fallback to local file
            filename = f"ai_news_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"💾 Saved locally: {filename}")
            return filename
    
    async def run(self):
        """Main execution"""
        print("🚀 AI News Monitor - Starting daily check")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Check all providers
        all_updates = []
        for provider in self.providers:
            try:
                updates = await self.check_provider(provider)
                all_updates.append(updates)
            except Exception as e:
                print(f"❌ Error checking {provider['name']}: {e}")
        
        # Create summary
        summary = await self.create_summary(all_updates)
        
        # Create report
        report = {
            "summary": summary,
            "details": all_updates,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Save report
        report_id = self.save_to_cosmos(report)
        
        print("\n" + "=" * 50)
        print("✅ AI News Monitor Complete!")
        print(f"📧 Report: {report_id}")
        
        # Also save a local copy for review
        with open("latest_ai_news.md", 'w') as f:
            f.write(summary)
        
        return report

async def main():
    monitor = AINewsMonitorLocal()
    await monitor.run()

if __name__ == "__main__":
    asyncio.run(main())