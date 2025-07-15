#!/usr/bin/env python3
"""
View API Registry - One-time view of the container contents
"""

import os
import json
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def view_registry():
    """View API registry contents"""
    
    # Get credentials
    cosmos_url = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    
    if not cosmos_url or not cosmos_key:
        print("❌ Missing Cosmos DB credentials")
        return
    
    try:
        # Connect to Cosmos DB
        client = CosmosClient(cosmos_url, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        container = database.get_container_client("api_registry")
        
        print("\n" + "="*70)
        print("🔍 API REGISTRY CONTAINER VIEW")
        print("="*70)
        
        # 1. Container Statistics
        print("\n📊 CONTAINER STATISTICS:")
        print("-"*50)
        
        query = "SELECT VALUE COUNT(1) FROM c"
        total = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))[0]
        
        print(f"Total documents: {total}")
        
        # Count by category
        for cat in ["system", "financial", "weather", "geospatial", "other"]:
            query = f"SELECT VALUE COUNT(1) FROM c WHERE c.category = '{cat}'"
            count = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))[0]
            
            if count > 0:
                print(f"  • {cat}: {count} documents")
        
        # 2. System Documents
        print("\n📋 SYSTEM DOCUMENTS:")
        print("-"*50)
        
        query = "SELECT * FROM c WHERE c.category = 'system'"
        system_docs = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        for doc in system_docs:
            print(f"\n{doc['id']}:")
            print(f"  Name: {doc.get('apiName', 'N/A')}")
            print(f"  Provider: {doc.get('provider', 'N/A')}")
            print(f"  Version: {doc.get('version', 'N/A')}")
            
            # Show sample requirements
            if doc['id'] == 'schema_requirements_v1':
                print("\n  Sample field requirements:")
                print(f"    apiName: {doc['apiName'][:60]}...")
                print(f"    authType: {doc['authType'][:60]}...")
                
        # 3. API Documents
        print("\n\n📚 API DOCUMENTS:")
        print("-"*50)
        
        query = "SELECT * FROM c WHERE c.category != 'system' ORDER BY c.apiName"
        api_docs = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        if not api_docs:
            print("No API documents found yet (only system documents exist)")
        else:
            print(f"\nFound {len(api_docs)} APIs:\n")
            print(f"{'#':<4} {'Name':<35} {'Provider':<25} {'Category':<15}")
            print("-"*80)
            
            for i, doc in enumerate(api_docs, 1):
                name = doc.get('apiName', doc.get('id', 'N/A'))[:33]
                provider = doc.get('provider', 'N/A')[:23]
                category = doc.get('category', 'N/A')[:13]
                print(f"{i:<4} {name:<35} {provider:<25} {category:<15}")
        
        # 4. Container Properties
        print("\n\n⚙️  CONTAINER CONFIGURATION:")
        print("-"*50)
        
        container_props = container.read()
        print(f"Container ID: {container_props['id']}")
        print(f"Partition Key: {container_props['partitionKey']['paths'][0]}")
        print(f"Indexing Mode: {container_props['indexingPolicy']['indexingMode']}")
        
        indexing = container_props['indexingPolicy']
        print(f"Included Paths: {len(indexing.get('includedPaths', []))}")
        print(f"Excluded Paths: {len(indexing.get('excludedPaths', []))}")
        print(f"Composite Indexes: {len(indexing.get('compositeIndexes', []))}")
        
        print("\n" + "="*70)
        print("✅ API Registry is ready for data!")
        print("📝 Schema requirements are defined in 'schema_requirements_v1'")
        print("📚 Add APIs using the defined schema structure")
        print("="*70)
        
    except Exception as e:
        print(f"❌ Error viewing registry: {e}")

if __name__ == "__main__":
    view_registry()