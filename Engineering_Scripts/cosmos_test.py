#!/usr/bin/env python3
"""
Simple Cosmos DB Connection Test
Tests basic connectivity and queries for HEAD_OF_ENGINEERING messages
"""

import os
import warnings
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Suppress SSL warning
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

# Load environment variables
load_dotenv()

def test_cosmos_connection():
    """Test Cosmos DB connection and query for messages"""
    
    # Import Cosmos DB client
    try:
        from azure.cosmos import CosmosClient
        from azure.cosmos.exceptions import CosmosHttpResponseError
    except ImportError:
        print("❌ Error: azure-cosmos not installed")
        print("   Run: pip3 install azure-cosmos")
        return
    
    # Get configuration
    endpoint = os.getenv('COSMOS_ENDPOINT')
    key = os.getenv('COSMOS_KEY')
    database_name = os.getenv('COSMOS_DATABASE_NAME')
    container_name = os.getenv('COSMOS_CONTAINER_NAME')
    
    # Check required variables
    if not all([endpoint, key, database_name, container_name]):
        print("❌ Missing required environment variables!")
        print("\nPlease create a .env file with:")
        print("COSMOS_ENDPOINT=https://<your-account>.documents.azure.com")
        print("COSMOS_KEY=<your-key>")
        print("COSMOS_DATABASE_NAME=<your-database>")
        print("COSMOS_CONTAINER_NAME=<your-container>")
        return
    
    # Fix endpoint format if needed
    if not endpoint.startswith('https://'):
        endpoint = f'https://{endpoint}'
        print(f"ℹ️  Fixed endpoint format: {endpoint}")
    
    try:
        # Create client
        print(f"\n🔗 Connecting to Cosmos DB...")
        print(f"   Endpoint: {endpoint.replace('.documents.azure.com', '.***.azure.com')}")
        
        client = CosmosClient(endpoint, credential=key)
        
        # Get database and container
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        print(f"   Database: {database_name}")
        print(f"   Container: {container_name}")
        
        # Test connection with a simple query
        print("\n✅ Connection successful!")
        
        # Count total messages
        count_query = "SELECT VALUE COUNT(1) FROM c"
        count = list(container.query_items(
            query=count_query,
            enable_cross_partition_query=True
        ))[0]
        print(f"\n📊 Total messages in container: {count}")
        
        # Query for HEAD_OF_ENGINEERING messages
        print("\n🔍 Searching for HEAD_OF_ENGINEERING messages...")
        
        # Last 30 days
        cutoff_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
        query = """
        SELECT TOP 20 
            c.id,
            c.sender,
            c.recipient,
            c.subject,
            c.timestamp,
            c.priority,
            c.status
        FROM c
        WHERE (c.sender = 'HEAD_OF_ENGINEERING' OR c.recipient = 'HEAD_OF_ENGINEERING')
        AND c.timestamp > @cutoff_date
        ORDER BY c.timestamp DESC
        """
        
        messages = list(container.query_items(
            query=query,
            parameters=[{"name": "@cutoff_date", "value": cutoff_date}],
            enable_cross_partition_query=True
        ))
        
        if messages:
            print(f"\n✅ Found {len(messages)} message(s) in the last 30 days:\n")
            
            for i, msg in enumerate(messages, 1):
                print(f"Message {i}:")
                print(f"  ID: {msg.get('id', 'N/A')}")
                print(f"  From: {msg.get('sender', 'N/A')}")
                print(f"  To: {msg.get('recipient', 'N/A')}")
                print(f"  Subject: {msg.get('subject', 'N/A')}")
                print(f"  Priority: {msg.get('priority', 'N/A')}")
                print(f"  Status: {msg.get('status', 'N/A')}")
                print(f"  Time: {msg.get('timestamp', 'N/A')}")
                print()
        else:
            print("\nℹ️  No HEAD_OF_ENGINEERING messages found in the last 30 days")
            
            # Try a broader search
            print("\n🔍 Trying broader search for any recent messages...")
            any_query = "SELECT TOP 5 c.id, c.sender, c.recipient, c.timestamp FROM c ORDER BY c.timestamp DESC"
            any_messages = list(container.query_items(
                query=any_query,
                enable_cross_partition_query=True
            ))
            
            if any_messages:
                print(f"\n✅ Found {len(any_messages)} recent message(s):")
                for msg in any_messages:
                    print(f"  {msg.get('sender', 'N/A')} → {msg.get('recipient', 'N/A')} at {msg.get('timestamp', 'N/A')}")
        
    except CosmosHttpResponseError as e:
        print(f"\n❌ Cosmos DB Error: {e.status_code}")
        print(f"   Message: {e.message}")
        
        if e.status_code == 401:
            print("\n💡 Fix: Check your Cosmos DB key is correct")
        elif e.status_code == 403:
            print("\n💡 Fix: Check firewall rules and access permissions")
        elif "One of the input values is invalid" in str(e):
            print("\n💡 Fix: Check endpoint format - should be https://<account>.documents.azure.com")
            
    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}")
        print(f"   Details: {str(e)}")

if __name__ == "__main__":
    print("🚀 Cosmos DB Connection Test\n")
    test_cosmos_connection()
    print("\n✨ Test complete!")