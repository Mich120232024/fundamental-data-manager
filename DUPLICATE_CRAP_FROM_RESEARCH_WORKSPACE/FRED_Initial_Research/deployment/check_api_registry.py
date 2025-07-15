#!/usr/bin/env python3
"""
Check API Registry Container - Verify deployment and query capabilities
"""

import os
import json
from datetime import datetime
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_api_registry():
    """Check the deployed API registry container"""
    
    # Get credentials
    cosmos_url = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    
    if not cosmos_url or not cosmos_key:
        print("❌ Missing Cosmos DB credentials")
        return False
    
    try:
        # Connect to Cosmos DB
        client = CosmosClient(cosmos_url, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        container = database.get_container_client("api_registry")
        
        print("🔍 Checking API Registry Container...")
        print("="*60)
        
        # 1. Check container properties
        container_properties = container.read()
        print(f"✅ Container Name: {container_properties['id']}")
        print(f"✅ Partition Key: {container_properties['partitionKey']['paths'][0]}")
        print(f"✅ Indexing Mode: {container_properties['indexingPolicy']['indexingMode']}")
        
        # 2. Check indexing policy details
        indexing = container_properties['indexingPolicy']
        print(f"\n📊 Indexing Configuration:")
        print(f"   • Included Paths: {len(indexing.get('includedPaths', []))}")
        print(f"   • Excluded Paths: {len(indexing.get('excludedPaths', []))}")
        print(f"   • Composite Indexes: {len(indexing.get('compositeIndexes', []))}")
        
        # Show excluded paths
        print(f"\n🚫 Excluded from Indexing:")
        for path in indexing.get('excludedPaths', []):
            print(f"   • {path['path']}")
        
        # 3. Test table-like queries
        print(f"\n🗂️  Testing Table-Like Queries:")
        
        # Insert test documents
        test_apis = [
            {
                "id": "api_test_001",
                "category": "financial",
                "apiName": "Test Financial API",
                "provider": "Test Provider 1",
                "status": "active",
                "authType": "api_key",
                "pricing": {"model": "free"},
                "protocol": "REST",
                "dataFormat": "JSON"
            },
            {
                "id": "api_test_002",
                "category": "weather",
                "apiName": "Test Weather API",
                "provider": "Test Provider 2",
                "status": "active",
                "authType": "oauth2",
                "pricing": {"model": "paid"},
                "protocol": "REST",
                "dataFormat": "JSON"
            },
            {
                "id": "api_test_003",
                "category": "financial",
                "apiName": "Test Stock API",
                "provider": "Test Provider 3",
                "status": "deprecated",
                "authType": "api_key",
                "pricing": {"model": "freemium"},
                "protocol": "GraphQL",
                "dataFormat": "JSON"
            }
        ]
        
        # Insert test data
        print("\n📝 Inserting test APIs...")
        for api in test_apis:
            container.upsert_item(api)
        print(f"✅ Inserted {len(test_apis)} test APIs")
        
        # 4. Run various queries
        queries = [
            ("All APIs", "SELECT * FROM c"),
            ("Financial APIs", "SELECT * FROM c WHERE c.category = 'financial'"),
            ("Free APIs", "SELECT * FROM c WHERE c.pricing.model = 'free'"),
            ("Active APIs", "SELECT * FROM c WHERE c.status = 'active'"),
            ("REST APIs", "SELECT * FROM c WHERE c.protocol = 'REST'"),
            ("API Key Auth", "SELECT * FROM c WHERE c.authType = 'api_key'")
        ]
        
        print("\n📊 Query Results:")
        for query_name, query in queries:
            results = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            print(f"   • {query_name}: {len(results)} results")
        
        # 5. Test cross-partition query
        print("\n🔍 Cross-Partition Query Test:")
        cross_query = "SELECT c.apiName, c.category, c.provider FROM c WHERE c.status = 'active'"
        results = list(container.query_items(
            query=cross_query,
            enable_cross_partition_query=True
        ))
        print(f"✅ Found {len(results)} active APIs across partitions:")
        for result in results:
            print(f"   • {result['apiName']} ({result['category']}) by {result['provider']}")
        
        # 6. Test aggregation query
        print("\n📈 Aggregation Query Test:")
        agg_query = "SELECT c.category, COUNT(1) as count FROM c GROUP BY c.category"
        results = list(container.query_items(
            query=agg_query,
            enable_cross_partition_query=True
        ))
        print("API Count by Category:")
        for result in results:
            print(f"   • {result['category']}: {result['count']} APIs")
        
        # 7. Cleanup test data
        print("\n🧹 Cleaning up test data...")
        for api in test_apis:
            container.delete_item(api["id"], partition_key=api["category"])
        print("✅ Test data cleaned up")
        
        # 8. Check for existing data
        print("\n📦 Checking for existing APIs...")
        count_query = "SELECT VALUE COUNT(1) FROM c"
        results = list(container.query_items(
            query=count_query,
            enable_cross_partition_query=True
        ))
        existing_count = results[0] if results else 0
        print(f"📊 Total APIs in registry: {existing_count}")
        
        print("\n" + "="*60)
        print("✅ API Registry container is fully operational!")
        print("✅ Table-like queries working correctly")
        print("✅ Ready for 500 API data loading")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking container: {e}")
        return False

if __name__ == "__main__":
    check_api_registry()