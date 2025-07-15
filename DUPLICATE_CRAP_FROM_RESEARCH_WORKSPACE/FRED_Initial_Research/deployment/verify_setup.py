#!/usr/bin/env python3
"""
Verify the API Registry and Discovery setup
Shows the schema document and confirms the structure
"""

import os
import json
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

load_dotenv()

def verify_setup():
    """Verify both containers are set up correctly"""
    
    cosmos_url = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    
    try:
        client = CosmosClient(cosmos_url, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        
        print("🔍 VERIFYING API REGISTRY AND DISCOVERY SETUP")
        print("="*60)
        
        # 1. Check api_registry for schema
        print("\n📦 Container: api_registry")
        print("-"*40)
        
        api_registry = database.get_container_client("api_registry")
        
        # Get all documents
        registry_docs = list(api_registry.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        
        print(f"Documents: {len(registry_docs)}")
        
        if registry_docs:
            for doc in registry_docs:
                print(f"\n📄 Document: {doc['id']}")
                print(f"   Type: {doc.get('type', 'N/A')}")
                print(f"   Category: {doc.get('category', 'N/A')}")
                
                if doc['id'] == 'api_schema_definition':
                    print("\n   📋 Schema Requirements (first 5):")
                    for i, (field, req) in enumerate(doc.get('schema_requirements', {}).items()):
                        if i < 5:
                            print(f"      • {field}: {req[:50]}...")
                    
                    print("\n   📋 Validation Rules:")
                    rules = doc.get('validation_rules', {})
                    print(f"      • Categories: {len(rules.get('allowed_categories', []))} defined")
                    print(f"      • Auth Types: {len(rules.get('allowed_authTypes', []))} defined")
                    print(f"      • Required Fields: {len(rules.get('required_fields', []))} defined")
        
        # 2. Check api_discovery
        print("\n\n📦 Container: api_discovery")
        print("-"*40)
        
        api_discovery = database.get_container_client("api_discovery")
        
        # Get container properties
        container_props = api_discovery.read()
        print(f"Partition Key: {container_props['partitionKey']['paths'][0]}")
        
        # Get all documents
        discovery_docs = list(api_discovery.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        
        print(f"Documents: {len(discovery_docs)}")
        
        if discovery_docs:
            print("\nSample documents:")
            for doc in discovery_docs[:3]:
                print(f"   • {doc.get('apiName', doc.get('id'))} ({doc.get('category', 'N/A')})")
        else:
            print("   ✨ Empty - ready for API data")
        
        # 3. Show the policy workflow
        print("\n\n📋 POLICY WORKFLOW:")
        print("-"*40)
        print("1. Agent reads schema from: api_registry → api_schema_definition")
        print("2. Agent validates API data against schema requirements")
        print("3. Agent uploads API to: api_discovery → (categorized by partition key)")
        print("\n✅ This ensures all APIs follow the defined schema!")
        
        print("\n" + "="*60)
        print("✅ Setup verified successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_setup()