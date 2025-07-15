#!/usr/bin/env python3
"""Check if AI news reports are in Cosmos"""
import os
from datetime import datetime, timedelta
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

load_dotenv()

# Connect to Cosmos
client = CosmosClient(os.getenv("COSMOS_ENDPOINT"), os.getenv("COSMOS_KEY"))
database = client.get_database_client("research-analytics-db")
container = database.get_container_client("system_inbox")

# Query for recent AI news messages
query = """
SELECT * FROM c 
WHERE c.partitionKey = 'AI_NEWS_MONITOR' 
AND c.timestamp > @cutoff
ORDER BY c.timestamp DESC
"""

cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
items = list(container.query_items(
    query=query,
    parameters=[{"name": "@cutoff", "value": cutoff}],
    enable_cross_partition_query=True
))

print(f"🔍 AI News Reports in Cosmos (last hour):")
print("=" * 60)

if items:
    for item in items:
        print(f"\n📧 ID: {item['id']}")
        print(f"   Type: {item['messageType']}")
        print(f"   Subject: {item.get('subject', 'N/A')}")
        print(f"   Time: {item.get('timestamp', 'N/A')}")
        print(f"   Recipients: {', '.join(item.get('recipients', []))}")
        
        # Show content preview
        if 'content' in item and 'summary' in item['content']:
            summary = item['content']['summary']
            preview = summary[:200] + "..." if len(summary) > 200 else summary
            print(f"   Preview: {preview}")
else:
    print("No AI news reports found in the last hour")

print("\n" + "=" * 60)