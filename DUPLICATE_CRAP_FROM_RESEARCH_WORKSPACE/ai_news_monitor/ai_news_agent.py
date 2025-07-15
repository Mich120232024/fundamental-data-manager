#!/usr/bin/env python3
"""
AI News Monitoring Agent
Checks major AI providers for updates and writes reports to Cosmos DB
"""
import asyncio
import os
import json
from datetime import datetime, timezone
from typing import List, Dict
from claude_code_sdk import query, ClaudeCodeOptions
from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import DefaultAzureCredential

class AINewsMonitor:
    def __init__(self):
        """Initialize the AI News Monitor with Azure connections"""
        # Claude SDK setup
        self.claude_options = ClaudeCodeOptions(
            system_prompt="You are an AI news analyst. Be concise and focus on technical updates, new features, and important announcements."
        )
        
        # Azure Cosmos DB setup
        self.cosmos_endpoint = os.getenv("COSMOS_ENDPOINT", "https://claude-agents-cosmos.documents.azure.com:443/")
        self.cosmos_key = os.getenv("COSMOS_KEY")  # Or use DefaultAzureCredential
        
        # Initialize Cosmos client
        if self.cosmos_key:
            self.cosmos_client = CosmosClient(self.cosmos_endpoint, self.cosmos_key)
        else:
            # Use managed identity in production
            credential = DefaultAzureCredential()
            self.cosmos_client = CosmosClient(self.cosmos_endpoint, credential)
        
        # Database and container
        self.database = self.cosmos_client.get_database_client("claude-agents")
        self.container = self.database.get_container_client("Mailbox")
        
        # AI providers to monitor
        self.providers = [
            {
                "name": "Anthropic",
                "urls": [
                    "https://www.anthropic.com/news",
                    "https://docs.anthropic.com/en/docs/changelog"
                ]
            },
            {
                "name": "OpenAI",
                "urls": [
                    "https://openai.com/blog",
                    "https://platform.openai.com/docs/changelog"
                ]
            },
            {
                "name": "Google Gemini",
                "urls": [
                    "https://blog.google/technology/ai/",
                    "https://ai.google.dev/gemini-api/docs/changelog"
                ]
            },
            {
                "name": "Microsoft Azure AI",
                "urls": [
                    "https://azure.microsoft.com/en-us/blog/topics/ai/",
                    "https://learn.microsoft.com/en-us/azure/ai-services/"
                ]
            },
            {
                "name": "Mistral AI",
                "urls": [
                    "https://mistral.ai/news/",
                    "https://docs.mistral.ai/"
                ]
            }
        ]
    
    async def check_provider_updates(self, provider: Dict) -> Dict:
        """Check a single provider for updates"""
        print(f"🔍 Checking {provider['name']}...")
        
        prompt = f"""
        Check the following sources for {provider['name']} and find the latest technical updates from the past 24-48 hours:
        
        {chr(10).join(provider['urls'])}
        
        Focus on:
        1. New model releases or updates
        2. API changes or new features
        3. Technical improvements or benchmarks
        4. Important announcements for developers
        
        If no recent updates, just say "No significant updates in the past 48 hours."
        
        Format as a brief bullet-point summary.
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
    
    async def generate_summary_report(self, all_updates: List[Dict]) -> str:
        """Generate a summary report from all updates"""
        print("\n📝 Generating summary report...")
        
        # Combine all updates
        combined_updates = "\n\n".join([
            f"## {update['provider']}\n{update['updates']}"
            for update in all_updates
        ])
        
        prompt = f"""
        Based on these AI provider updates, create a concise executive summary:
        
        {combined_updates}
        
        Structure the summary as:
        1. KEY HIGHLIGHTS (most important 3-5 updates)
        2. TECHNICAL TRENDS (patterns across providers)
        3. ACTION ITEMS (what our team should pay attention to)
        
        Keep it brief but informative.
        """
        
        summary = ""
        async for message in query(prompt=prompt, options=self.claude_options):
            if hasattr(message, 'content') and message.content:
                for block in message.content:
                    if hasattr(block, 'text'):
                        summary += block.text
        
        return summary
    
    async def save_to_cosmos(self, report: Dict) -> str:
        """Save the report to Cosmos DB Mailbox"""
        print("\n💾 Saving to Cosmos DB...")
        
        # Create mailbox message
        message = {
            "id": f"ai-news-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "partitionKey": "AI_NEWS_MONITOR",
            "messageType": "AI_NEWS_DAILY_REPORT",
            "sender": {
                "name": "AI_NEWS_MONITOR",
                "role": "Automated Agent"
            },
            "recipients": ["HEAD_OF_RESEARCH", "HEAD_OF_ENGINEERING", "ALL_AGENTS"],
            "subject": f"AI Industry Updates - {datetime.now().strftime('%B %d, %Y')}",
            "content": report,
            "priority": "NORMAL",
            "status": "UNREAD",
            "metadata": {
                "category": "INTELLIGENCE",
                "subcategory": "INDUSTRY_UPDATES",
                "importance": 3,
                "tags": ["ai-news", "daily-report", "automated"],
                "source": "ai_news_monitor"
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert into Cosmos DB
        try:
            self.container.create_item(body=message)
            print(f"✅ Report saved with ID: {message['id']}")
            return message['id']
        except Exception as e:
            print(f"❌ Error saving to Cosmos: {e}")
            # Fallback: save locally
            with open(f"ai_news_report_{message['id']}.json", 'w') as f:
                json.dump(message, f, indent=2)
            return f"LOCAL_{message['id']}"
    
    async def run_daily_check(self):
        """Main execution flow"""
        print("🚀 Starting AI News Monitor")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=" * 50)
        
        # Check each provider
        all_updates = []
        for provider in self.providers:
            try:
                updates = await self.check_provider_updates(provider)
                all_updates.append(updates)
                print(f"✅ {provider['name']} checked")
            except Exception as e:
                print(f"❌ Error checking {provider['name']}: {e}")
                all_updates.append({
                    "provider": provider['name'],
                    "updates": f"Error checking updates: {str(e)}",
                    "checked_at": datetime.now(timezone.utc).isoformat()
                })
        
        # Generate summary
        summary = await self.generate_summary_report(all_updates)
        
        # Create full report
        report = {
            "summary": summary,
            "detailed_updates": all_updates,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "agent_version": "1.0.0"
        }
        
        # Save to Cosmos
        message_id = await self.save_to_cosmos(report)
        
        print("\n" + "=" * 50)
        print("✅ AI News Monitor Complete!")
        print(f"📧 Report ID: {message_id}")
        print("=" * 50)
        
        return report

async def main():
    """Entry point for the agent"""
    monitor = AINewsMonitor()
    await monitor.run_daily_check()

if __name__ == "__main__":
    asyncio.run(main())