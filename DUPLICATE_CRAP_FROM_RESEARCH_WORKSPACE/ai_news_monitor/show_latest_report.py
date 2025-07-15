#!/usr/bin/env python3
"""
Show the latest AI news report from Cosmos DB
"""
import os
from azure.cosmos import CosmosClient
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def show_latest_report():
    """Get and display the latest AI news report"""
    try:
        # Connect to Cosmos DB
        cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_KEY")
        
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        container = database.get_container_client("system_inbox")
        
        # Query for the latest AI news report
        query = """
        SELECT TOP 1 * FROM c 
        WHERE c.sender.name = 'AI_NEWS_MONITOR'
        AND (c.messageType = 'AI_NEWS_WEEKLY_REPORT' 
             OR c.messageType = 'AI_NEWS_DEMO_REPORT'
             OR c.messageType = 'AI_NEWS_FULL_REPORT')
        ORDER BY c.timestamp DESC
        """
        
        messages = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        if messages:
            report = messages[0]
            print("="*80)
            print(f"📧 LATEST AI NEWS REPORT")
            print("="*80)
            print(f"📅 Date: {report.get('timestamp', 'Unknown')}")
            print(f"📌 ID: {report.get('id')}")
            print(f"📨 Subject: {report.get('subject')}")
            print(f"👤 Recipients: {', '.join(report.get('recipients', []))}")
            print("="*80)
            
            content = report.get('content', {})
            
            # Show summary if available
            if isinstance(content, dict) and 'summary' in content:
                print("\n📋 EXECUTIVE SUMMARY:")
                print("-"*80)
                print(content['summary'])
                print("-"*80)
            
            # Show detailed updates
            if isinstance(content, dict) and 'detailed_updates' in content:
                print("\n📰 DETAILED UPDATES BY PROVIDER:")
                print("-"*80)
                for update in content['detailed_updates']:
                    print(f"\n🏢 {update.get('provider', 'Unknown Provider')}")
                    print(f"⏰ Checked: {update.get('checked_at', 'Unknown')}")
                    print(f"\n{update.get('updates', 'No updates')}")
                    print("-"*40)
            
            # Show enhanced analysis if available
            if isinstance(content, dict) and 'enhanced_analysis' in content:
                analysis = content['enhanced_analysis']
                print("\n🔍 ENHANCED ANALYSIS:")
                print("-"*80)
                
                if 'executive_summary' in analysis:
                    print("\n📊 Executive Summary:")
                    print(analysis['executive_summary'])
                
                if 'key_takeaways' in analysis:
                    print("\n🎯 Key Takeaways:")
                    for takeaway in analysis['key_takeaways']:
                        print(f"  • {takeaway}")
                
                if 'competitive_landscape' in analysis:
                    print("\n🏆 Competitive Landscape:")
                    print(analysis['competitive_landscape'])
                
                if 'strategic_recommendations' in analysis:
                    print("\n💡 Strategic Recommendations:")
                    for rec in analysis['strategic_recommendations']:
                        print(f"  • {rec}")
            
            print("\n="*80)
            print("✅ Report displayed successfully")
            
            # Save to file for reference
            with open("latest_ai_news_display.json", 'w') as f:
                json.dump(report, f, indent=2)
            print("📄 Full report saved to: latest_ai_news_display.json")
            
        else:
            print("❌ No AI news reports found in Cosmos DB")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    show_latest_report()