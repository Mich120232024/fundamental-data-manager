#!/usr/bin/env python3
"""
Enhanced AI News Analyzer - Checks recency and relevance to your system
"""
import os
import json
import re
from datetime import datetime, timedelta, timezone
from azure.cosmos import CosmosClient
from claude_code_sdk import query, ClaudeCodeOptions
from dotenv import load_dotenv

load_dotenv()

class EnhancedAINewsAnalyzer:
    def __init__(self):
        self.cosmos_client = CosmosClient(os.getenv("COSMOS_ENDPOINT"), os.getenv("COSMOS_KEY"))
        self.database = self.cosmos_client.get_database_client("research-analytics-db")
        self.container = self.database.get_container_client("system_inbox")
        
        # Your system context
        self.system_context = {
            "current_tools": ["Claude SDK", "MCP servers", "Azure Synapse", "FRED data"],
            "challenges": ["MCP stability", "frontend debugging", "cost optimization", "process outsourcing"],
            "agent_system": ["multi-agent architecture", "Cosmos DB mailbox", "swarm AI"],
            "priorities": ["automation", "cost reduction", "reliability", "scalability"]
        }
        
    def extract_dates_from_content(self, content):
        """Extract dates mentioned in the content"""
        # Look for patterns like "January 7", "Jan 7", "2025-01-07", etc.
        date_patterns = [
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\byesterday\b',
            r'\btoday\b',
            r'\blast week\b',
            r'\bthis week\b'
        ]
        
        found_dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_dates.extend(matches)
        
        return found_dates
    
    async def analyze_news_relevance(self, news_item):
        """Analyze if news is relevant to our system and how we could benefit"""
        
        options = ClaudeCodeOptions(
            system_prompt="You are an AI system architect analyzing news for practical implementation benefits."
        )
        
        prompt = f"""
        Analyze this AI news update for relevance to our system:
        
        UPDATE: {news_item}
        
        OUR SYSTEM CONTEXT:
        - Current tools: {', '.join(self.system_context['current_tools'])}
        - Challenges: {', '.join(self.system_context['challenges'])}
        - Architecture: {', '.join(self.system_context['agent_system'])}
        - Priorities: {', '.join(self.system_context['priorities'])}
        
        ANALYZE:
        1. Is this update from the last 1-2 days? (Look for specific dates)
        2. How does it relate to our current setup?
        3. What specific benefits could we gain?
        4. Should we take any immediate action?
        
        Format response as:
        RECENCY: [New/Old/Unknown]
        RELEVANCE: [High/Medium/Low]
        BENEFITS: [Specific benefits]
        ACTION: [Immediate action if any]
        """
        
        analysis = ""
        async for message in query(prompt=prompt, options=options):
            if hasattr(message, 'content') and message.content:
                for block in message.content:
                    if hasattr(block, 'text'):
                        analysis += block.text
        
        return analysis
    
    async def get_latest_ai_news(self):
        """Get the latest AI news from Cosmos DB"""
        # Get the full report that just completed
        try:
            item = self.container.read_item(
                item="ai-news-full-20250707-150919",
                partition_key="AI_NEWS_MONITOR"
            )
            return item
        except:
            # Fallback to query
            query_text = """
            SELECT * FROM c 
            WHERE c.partitionKey = 'AI_NEWS_MONITOR' 
            AND c.messageType = 'AI_NEWS_WEEKLY_REPORT'
            ORDER BY c.timestamp DESC
            OFFSET 0 LIMIT 1
            """
            items = list(self.container.query_items(query=query_text, enable_cross_partition_query=True))
            return items[0] if items else None
    
    async def analyze_and_enhance_report(self):
        """Analyze the latest report and add relevance analysis"""
        print("🔍 Enhanced AI News Analysis")
        print("=" * 60)
        
        # Get latest report
        report = await self.get_latest_ai_news()
        if not report:
            print("❌ No AI news report found")
            return
        
        print(f"📧 Analyzing report: {report['id']}")
        print(f"Generated at: {report.get('timestamp', 'Unknown')}")
        
        # Analyze each provider's updates
        enhanced_updates = []
        
        if 'content' in report and 'detailed_updates' in report['content']:
            for update in report['content']['detailed_updates']:
                provider = update.get('provider', 'Unknown')
                updates_text = update.get('updates', '')
                
                print(f"\n🏢 Analyzing {provider}...")
                
                # Extract dates from content
                found_dates = self.extract_dates_from_content(updates_text)
                print(f"   Dates found: {found_dates if found_dates else 'None'}")
                
                # Analyze relevance
                analysis = await self.analyze_news_relevance(updates_text)
                
                enhanced_updates.append({
                    "provider": provider,
                    "original_updates": updates_text,
                    "found_dates": found_dates,
                    "relevance_analysis": analysis
                })
                
                # Show analysis preview
                if "RELEVANCE: High" in analysis:
                    print(f"   ⭐ HIGH RELEVANCE DETECTED!")
                print(f"   Analysis preview: {analysis[:100]}...")
        
        # Create enhanced report
        print("\n📝 Creating enhanced report with relevance analysis...")
        
        enhanced_prompt = f"""
        Based on these analyzed AI updates, create an actionable summary for our team:
        
        SYSTEM PRIORITIES:
        - MCP stability issues
        - Frontend debugging needs  
        - Cost optimization
        - Process outsourcing to Azure
        
        UPDATES WITH ANALYSIS:
        {json.dumps(enhanced_updates, indent=2)[:3000]}...
        
        Create a report with:
        1. TRULY NEW UPDATES (last 1-2 days only)
        2. HIGH RELEVANCE ITEMS (directly help our priorities)
        3. IMMEDIATE ACTIONS (what to do today)
        4. COST SAVINGS OPPORTUNITIES
        5. INTEGRATION POSSIBILITIES
        
        Be specific and actionable.
        """
        
        options = ClaudeCodeOptions(
            system_prompt="You are a technical advisor creating actionable recommendations."
        )
        
        enhanced_summary = ""
        async for message in query(prompt=enhanced_prompt, options=options):
            if hasattr(message, 'content') and message.content:
                for block in message.content:
                    if hasattr(block, 'text'):
                        enhanced_summary += block.text
        
        # Save enhanced report
        enhanced_report = {
            "id": f"ai-news-enhanced-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "partitionKey": "AI_NEWS_MONITOR",
            "messageType": "AI_NEWS_ENHANCED_ANALYSIS",
            "subject": f"🎯 [ACTIONABLE] AI Updates Analysis - {datetime.now().strftime('%B %d, %Y')}",
            "sender": {"name": "AI_NEWS_ANALYZER", "role": "Intelligence Analyst"},
            "recipients": ["HEAD_OF_RESEARCH", "HEAD_OF_ENGINEERING"],
            "content": {
                "enhanced_summary": enhanced_summary,
                "detailed_analysis": enhanced_updates,
                "original_report_id": report['id'],
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            },
            "priority": "HIGH",
            "status": "UNREAD",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            self.container.create_item(body=enhanced_report)
            print(f"\n✅ Enhanced analysis saved!")
            print(f"📧 Message ID: {enhanced_report['id']}")
            
            # Save locally too
            with open("ai_news_enhanced_analysis.md", 'w') as f:
                f.write(enhanced_summary)
            
            print(f"\n📄 ENHANCED SUMMARY PREVIEW:")
            print("=" * 60)
            print(enhanced_summary[:500] + "...")
            
        except Exception as e:
            print(f"❌ Error saving: {e}")
            with open("ai_news_enhanced_fallback.json", 'w') as f:
                json.dump(enhanced_report, f, indent=2)

async def main():
    analyzer = EnhancedAINewsAnalyzer()
    await analyzer.analyze_and_enhance_report()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())