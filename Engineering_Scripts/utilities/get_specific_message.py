#!/usr/bin/env python3
"""
Get Specific Message from System Inbox
"""

from azure.cosmos import CosmosClient
import json

# Cosmos DB credentials
COSMOS_ENDPOINT = "https://cosmos-research-analytics-prod.documents.azure.com:443/"
COSMOS_KEY = "cSq2cHQmhrYnjYPUdjDlAI7RxIOAEswXmDLAAywKVmPL5exy8IlSpUcQxdXtFuSutWRBx1wPqKAYACDbFfQKmA=="
COSMOS_DATABASE = "research-analytics-db"

def get_specific_message():
    """Get specific message details"""
    
    print("🔍 Getting Specific Message Details")
    print("=" * 60)
    
    try:
        # Initialize Cosmos client
        client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        database = client.get_database_client(COSMOS_DATABASE)
        container = database.get_container_client("system_inbox")
        
        target_id = "msg_engineering_to_research_20250620_053541"
        
        # Get the message by ID
        try:
            message = container.read_item(
                item=target_id,
                partition_key=target_id  # Assuming partition key is the same as ID
            )
            
            print(f"✅ Found message: {target_id}")
            print("=" * 60)
            print("Full message details:")
            print(json.dumps(message, indent=2, default=str))
            
        except Exception as read_error:
            print(f"Direct read failed: {read_error}")
            
            # Try querying instead
            query = f"SELECT * FROM c WHERE c.id = '{target_id}'"
            
            results = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if results:
                message = results[0]
                print(f"✅ Found message via query: {target_id}")
                print("=" * 60)
                print("Full message details:")
                print(json.dumps(message, indent=2, default=str))
            else:
                print(f"❌ Message not found: {target_id}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    get_specific_message()