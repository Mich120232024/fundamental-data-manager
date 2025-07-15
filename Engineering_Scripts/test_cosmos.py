#!/usr/bin/env python3
"""Test Azure Cosmos DB connection and basic operations"""

from azure.cosmos import CosmosClient
from datetime import datetime
import json

def test_cosmos_connection():
    """Test connection to our new Cosmos DB"""
    
    # Connection details
    endpoint = "https://cosmos-research-analytics-prod.documents.azure.com:443/"
    key = "cSq2cHQmhrYnjYPUdjDlAI7RxIOAEswXmDLAAywKVmPL5exy8IlSpUcQxdXtFuSutWRBx1wPqKAYACDbFfQKmA=="
    database_name = "research-analytics-db"
    container_name = "messages"
    
    try:
        print("🔌 Testing Cosmos DB Connection...")
        
        # Initialize client
        client = CosmosClient(endpoint, key)
        print("✅ Client created successfully")
        
        # Get database
        database = client.get_database_client(database_name)
        print(f"✅ Connected to database: {database_name}")
        
        # Get container
        container = database.get_container_client(container_name)
        print(f"✅ Connected to container: {container_name}")
        
        # Create test document
        test_doc = {
            "id": f"test_{datetime.now().isoformat()}",
            "partitionKey": "2025-06",
            "type": "TEST",
            "from": "test_script",
            "to": "cosmos_db",
            "subject": "Connection Test",
            "content": "Testing Cosmos DB connection and basic operations",
            "timestamp": datetime.now().isoformat() + "Z",
            "tags": ["test", "connection"],
            "priority": "low"
        }
        
        print("📝 Creating test document...")
        created_item = container.create_item(test_doc)
        print(f"✅ Document created with ID: {created_item['id']}")
        
        # Query the document
        print("🔍 Querying test document...")
        query = "SELECT * FROM messages WHERE messages.type = 'TEST'"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        print(f"✅ Found {len(items)} test documents")
        
        # Show document details
        if items:
            doc = items[0]
            print(f"   📄 ID: {doc['id']}")
            print(f"   📅 Timestamp: {doc['timestamp']}")
            print(f"   📧 From: {doc['from']} → {doc['to']}")
            print(f"   📝 Subject: {doc['subject']}")
        
        # Test full-text search capability
        print("🔍 Testing search capabilities...")
        search_query = "SELECT * FROM messages WHERE CONTAINS(messages.content, 'connection')"
        search_results = list(container.query_items(search_query, enable_cross_partition_query=True))
        print(f"✅ Search found {len(search_results)} documents containing 'connection'")
        
        # Test partition-based query (more efficient)
        print("🔍 Testing partition-based query...")
        partition_query = "SELECT * FROM messages WHERE messages.partitionKey = '2025-06'"
        partition_results = list(container.query_items(partition_query, partition_key="2025-06"))
        print(f"✅ Partition query found {len(partition_results)} documents in '2025-06'")
        
        # Cleanup test document
        print("🧹 Cleaning up test document...")
        container.delete_item(created_item['id'], partition_key="2025-06")
        print("✅ Test document deleted")
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED!")
        print("="*50)
        print("✅ Connection: Working")
        print("✅ Write operations: Working") 
        print("✅ Cross-partition queries: Working")
        print("✅ Partition-specific queries: Working")
        print("✅ Full-text search: Working")
        print("✅ Document cleanup: Working")
        print("\n🚀 Ready for inbox migration!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_cosmos_connection()