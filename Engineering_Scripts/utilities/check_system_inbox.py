#!/usr/bin/env python3
"""
Check System Inbox for Messages
Azure Cosmos DB Only - No Local Inbox References
"""

from azure.cosmos import CosmosClient
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Cosmos DB credentials from environment variables
COSMOS_ENDPOINT = os.getenv('COSMOS_ENDPOINT')
COSMOS_KEY = os.getenv('COSMOS_KEY')
COSMOS_DATABASE = "research-analytics-db"

def check_messages():
    """Check system inbox for messages"""
    
    print("📨 Checking System Inbox in Cosmos DB (Azure Only)")
    print("=" * 60)
    
    # Validate environment variables
    if not COSMOS_ENDPOINT or not COSMOS_KEY:
        print("❌ Error: Missing Cosmos DB credentials in environment variables")
        print("   Please ensure COSMOS_ENDPOINT and COSMOS_KEY are set in .env file")
        return []
    
    try:
        # Initialize Cosmos client
        client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        database = client.get_database_client(COSMOS_DATABASE)
        container = database.get_container_client("system_inbox")
        
        # Query for all messages
        query = """
        SELECT c.id, c.from_agent, c.to_agent, c.subject, c.timestamp, c.message
        FROM c 
        ORDER BY c.timestamp DESC
        """
        
        messages = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        print(f"📧 Found {len(messages)} messages in system inbox")
        print()
        
        # Look for the specific message
        target_id = "msg_engineering_to_research_20250620_053541"
        
        for msg in messages:
            print(f"📨 Message ID: {msg['id']}")
            print(f"   From: {msg.get('from_agent', 'Unknown')}")
            print(f"   To: {msg.get('to_agent', 'Unknown')}")
            print(f"   Subject: {msg.get('subject', 'No subject')}")
            print(f"   Time: {msg.get('timestamp', 'Unknown')}")
            
            if msg['id'] == target_id:
                print(f"\n🎯 FOUND TARGET MESSAGE: {target_id}")
                print("=" * 60)
                print("Message Content:")
                print(msg.get('message', 'No message content'))
                print("=" * 60)
            
            print()
        
        return messages
        
    except Exception as e:
        print(f"❌ Error checking inbox: {str(e)}")
        return []

if __name__ == "__main__":
    check_messages()