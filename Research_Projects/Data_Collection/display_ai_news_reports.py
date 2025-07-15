#!/usr/bin/env python3
"""Display AI news reports from Cosmos DB"""
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

# Get the demo report
print("📧 OPENING AI NEWS REPORTS FROM COSMOS DB")
print("=" * 80)

try:
    # Get the demo report
    demo_report = container.read_item(
        item="ai-news-demo-20250707-150243", 
        partition_key="AI_NEWS_MONITOR"
    )
    
    print(f"\n📨 EMAIL #1: {demo_report['subject']}")
    print("-" * 80)
    print(f"From: {demo_report['sender']['name']} ({demo_report['sender']['role']})")
    print(f"To: {', '.join(demo_report['recipients'])}")
    print(f"Date: {demo_report['timestamp']}")
    print(f"Priority: {demo_report['priority']}")
    print(f"Status: {demo_report['status']}")
    print("-" * 80)
    print("\n📄 CONTENT:\n")
    
    # Display the summary
    if 'summary' in demo_report['content']:
        print(demo_report['content']['summary'])
    
    # Display detailed updates
    if 'detailed_updates' in demo_report['content']:
        print("\n\n📊 DETAILED PROVIDER UPDATES:")
        print("-" * 80)
        for update in demo_report['content']['detailed_updates']:
            print(f"\n🏢 {update['provider']}")
            print(update['updates'])
            print(f"Checked at: {update['checked_at']}")
    
except Exception as e:
    print(f"Error reading demo report: {e}")

print("\n" + "=" * 80)

# Get the test report
try:
    test_report = container.read_item(
        item="ai-news-test-20250707-145335",
        partition_key="AI_NEWS_MONITOR"
    )
    
    print(f"\n📨 EMAIL #2: {test_report['subject']}")
    print("-" * 80)
    print(f"From: {test_report['sender']['name']} ({test_report['sender']['role']})")
    print(f"To: {', '.join(test_report['recipients'])}")
    print(f"Date: {test_report['timestamp']}")
    print("-" * 80)
    print("\n📄 CONTENT:\n")
    
    # Display content
    if isinstance(test_report['content'], dict):
        print(json.dumps(test_report['content'], indent=2))
    else:
        print(test_report['content'])
        
except Exception as e:
    print(f"Error reading test report: {e}")

print("\n" + "=" * 80)
print("📧 END OF AI NEWS REPORTS")
print("=" * 80)