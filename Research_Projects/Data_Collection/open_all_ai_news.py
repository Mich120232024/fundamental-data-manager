#!/usr/bin/env python3
"""Open and display all AI news reports from Cosmos DB"""
import os
import json
from datetime import datetime, timedelta
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

load_dotenv()

# Connect to Cosmos
client = CosmosClient(os.getenv("COSMOS_ENDPOINT"), os.getenv("COSMOS_KEY"))
database = client.get_database_client("research-analytics-db")
container = database.get_container_client("system_inbox")

# Query for all AI news messages
query = """
SELECT * FROM c 
WHERE c.partitionKey = 'AI_NEWS_MONITOR'
ORDER BY c.timestamp DESC
"""

items = list(container.query_items(
    query=query,
    enable_cross_partition_query=True
))

print("📧 ALL AI NEWS REPORTS IN YOUR COSMOS DB INBOX")
print("=" * 80)
print(f"Found {len(items)} AI news messages\n")

for i, item in enumerate(items, 1):
    print(f"\n{'='*80}")
    print(f"📨 EMAIL #{i}")
    print(f"{'='*80}")
    print(f"ID: {item['id']}")
    print(f"Subject: {item.get('subject', 'No subject')}")
    print(f"From: {item.get('sender', {}).get('name', 'Unknown')}")
    print(f"To: {', '.join(item.get('recipients', []))}")
    print(f"Date: {item.get('timestamp', 'Unknown')}")
    print(f"Type: {item.get('messageType', 'Unknown')}")
    print(f"Status: {item.get('status', 'Unknown')}")
    print("-" * 80)
    
    # Display content based on type
    content = item.get('content', {})
    
    if isinstance(content, dict):
        # Check for summary
        if 'summary' in content:
            print("\n📄 SUMMARY:\n")
            print(content['summary'])
        
        # Check for detailed updates
        if 'detailed_updates' in content:
            print("\n\n📊 DETAILED UPDATES:")
            print("-" * 80)
            for update in content['detailed_updates']:
                print(f"\n🏢 {update.get('provider', 'Unknown')}")
                print(update.get('updates', 'No updates'))
        
        # Check for other content types
        if 'anthropic_updates' in content:
            print("\n📄 CONTENT:")
            print(f"Anthropic Updates: {content['anthropic_updates']}")
            
        # If no specific format, show all content
        if not any(k in content for k in ['summary', 'detailed_updates', 'anthropic_updates']):
            print("\n📄 RAW CONTENT:")
            print(json.dumps(content, indent=2))
    else:
        print("\n📄 CONTENT:")
        print(content)

print("\n" + "=" * 80)
print(f"📧 END OF AI NEWS REPORTS ({len(items)} total)")
print("=" * 80)