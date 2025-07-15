#!/usr/bin/env python3
"""
Clean up api_registry container - remove test data and schema documents
"""

import os
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

load_dotenv()

def cleanup_api_registry():
    """Remove test data and schema documents from api_registry"""
    
    cosmos_url = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    
    try:
        client = CosmosClient(cosmos_url, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        container = database.get_container_client("api_registry")
        
        print("🧹 Cleaning up api_registry container...")
        
        # Get all documents
        all_docs = list(container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        
        print(f"Found {len(all_docs)} documents to review")
        
        deleted_count = 0
        for doc in all_docs:
            # Delete test APIs and system documents
            if (doc.get('id', '').startswith('api_test_') or 
                doc.get('id', '').startswith('test_') or
                doc.get('category') == 'system' or
                doc.get('id') in ['schema_requirements_v1', 'validation_rules_v1']):
                
                print(f"  Deleting: {doc['id']} (category: {doc.get('category', 'N/A')})")
                container.delete_item(doc['id'], partition_key=doc.get('category', doc.get('pk')))
                deleted_count += 1
        
        print(f"\n✅ Cleaned up {deleted_count} documents")
        
        # Verify
        remaining = list(container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        
        print(f"📊 Remaining documents: {len(remaining)}")
        
        if remaining:
            print("\nRemaining documents:")
            for doc in remaining:
                print(f"  • {doc['id']} ({doc.get('category', 'N/A')})")
        else:
            print("✨ Container is now empty and ready for real API data")
        
        print("\n✅ api_registry is now clean!")
        print("📋 Schema definition is in: api-schemas-db → schema-definitions → api_schema_definition")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    cleanup_api_registry()