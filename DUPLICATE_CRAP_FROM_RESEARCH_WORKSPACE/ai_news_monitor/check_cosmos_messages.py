#!/usr/bin/env python3
"""
Check for AI news messages in Cosmos DB
"""
import os
from azure.cosmos import CosmosClient
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_ai_news_messages():
    """Check for AI news messages in Cosmos DB"""
    print("🔍 Checking Cosmos DB for AI News messages...")
    print("=" * 50)
    
    try:
        # Connect to Cosmos DB
        cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_KEY")
        
        print(f"Endpoint: {cosmos_endpoint}")
        
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        container = database.get_container_client("system_inbox")
        
        # Query for AI news messages
        query = """
        SELECT * FROM c 
        WHERE c.sender.name = 'AI_NEWS_MONITOR'
        ORDER BY c.timestamp DESC
        """
        
        messages = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        print(f"\n📊 Found {len(messages)} AI News messages")
        
        if messages:
            print("\nRecent messages:")
            for msg in messages[:5]:  # Show last 5
                print(f"\n📅 {msg.get('timestamp', 'No timestamp')}")
                print(f"📌 ID: {msg.get('id')}")
                print(f"📨 Subject: {msg.get('subject', 'No subject')}")
                print(f"📋 Type: {msg.get('messageType', 'Unknown')}")
                
                # Check content
                content = msg.get('content', {})
                if isinstance(content, dict):
                    if 'summary' in content:
                        print(f"✅ Has summary report")
                    if 'detailed_updates' in content:
                        print(f"✅ Has detailed updates from {len(content.get('detailed_updates', []))} providers")
        else:
            print("\n❌ No AI News messages found")
            print("\nPossible reasons:")
            print("1. The cron job isn't running")
            print("2. The script is saving to a different Cosmos instance")
            print("3. There's an error in the script")
            
        # Also check for any test messages
        print("\n🔍 Checking for test messages...")
        test_query = """
        SELECT * FROM c 
        WHERE c.messageType = 'AI_NEWS_TEST'
        ORDER BY c.timestamp DESC
        """
        
        test_messages = list(container.query_items(
            query=test_query,
            enable_cross_partition_query=True
        ))
        
        if test_messages:
            print(f"📊 Found {len(test_messages)} test messages")
        
    except Exception as e:
        print(f"\n❌ Error connecting to Cosmos: {e}")
        print("\nThis might mean:")
        print("1. Wrong credentials")
        print("2. Network issues")
        print("3. Database/container doesn't exist")

if __name__ == "__main__":
    check_ai_news_messages()