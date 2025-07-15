#!/usr/bin/env python3
"""Display the enhanced AI news analysis"""
import os
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

load_dotenv()

# Connect to Cosmos
client = CosmosClient(os.getenv("COSMOS_ENDPOINT"), os.getenv("COSMOS_KEY"))
database = client.get_database_client("research-analytics-db")
container = database.get_container_client("system_inbox")

# Get the enhanced analysis
try:
    report = container.read_item(
        item="ai-news-enhanced-20250707-151516",
        partition_key="AI_NEWS_MONITOR"
    )
    
    print("📧 ENHANCED AI NEWS ANALYSIS")
    print("=" * 80)
    print(f"Subject: {report['subject']}")
    print(f"Priority: {report['priority']}")
    print(f"Recipients: {', '.join(report['recipients'])}")
    print("=" * 80)
    
    # Show the enhanced summary
    print("\n🎯 ACTIONABLE INTELLIGENCE:\n")
    print(report['content']['enhanced_summary'])
    
    # Show key findings
    print("\n" + "=" * 80)
    print("📊 DETAILED FINDINGS PER PROVIDER:")
    print("=" * 80)
    
    for analysis in report['content']['detailed_analysis']:
        provider = analysis['provider']
        dates = analysis['found_dates']
        relevance = analysis['relevance_analysis']
        
        print(f"\n🏢 {provider}")
        print(f"   Dates mentioned: {dates if dates else 'None'}")
        
        # Extract key parts from relevance analysis
        if "RELEVANCE: High" in relevance:
            print("   ⭐ HIGH RELEVANCE")
        elif "RELEVANCE: Medium" in relevance:
            print("   🔸 MEDIUM RELEVANCE")
        else:
            print("   ⚪ LOW RELEVANCE")
            
        if "ACTION:" in relevance:
            action_start = relevance.find("ACTION:")
            action_text = relevance[action_start:].split('\n')[0]
            print(f"   {action_text}")
    
except Exception as e:
    print(f"Error reading enhanced analysis: {e}")

# Also read the markdown file
print("\n" + "=" * 80)
print("📄 SAVED ANALYSIS:")
print("=" * 80)

try:
    with open("ai_news_enhanced_analysis.md", 'r') as f:
        content = f.read()
        print(content)
except:
    print("Could not read ai_news_enhanced_analysis.md")