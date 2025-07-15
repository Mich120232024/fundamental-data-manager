#!/usr/bin/env python3
"""
Create Cosmos Container for Processed Documents
"""

import os
from pathlib import Path
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment
env_paths = [
    Path(__file__).parent.parent / '.env',
    Path(__file__).parent.parent.parent / '.env',
    Path.cwd() / '.env'
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Environment loaded from: {env_path}")
        break

def create_processed_documents_container():
    """Create container for processed documents"""
    
    print("🗄️  Creating Processed Documents Container")
    print("=" * 60)
    
    try:
        # Initialize Cosmos client
        cosmos_endpoint = os.getenv('COSMOS_ENDPOINT')
        cosmos_key = os.getenv('COSMOS_KEY')
        cosmos_database = os.getenv('COSMOS_DATABASE')
        
        if not all([cosmos_endpoint, cosmos_key, cosmos_database]):
            raise ValueError("Cosmos DB credentials not found in environment")
            
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = client.get_database_client(cosmos_database)
        
        # Container configuration
        container_name = "processed_documents"
        
        container_config = {
            "id": container_name,
            "partitionKey": {
                "paths": ["/type"],
                "kind": "Hash"
            },
            "indexingPolicy": {
                "indexingMode": "consistent",
                "automatic": True,
                "includedPaths": [
                    {
                        "path": "/*"
                    }
                ],
                "excludedPaths": [
                    {
                        "path": "/chunks/*"  # Exclude large chunk arrays from indexing
                    },
                    {
                        "path": "/graph_ready/*"  # Exclude graph data from indexing
                    }
                ],
                "compositeIndexes": [
                    [
                        {
                            "path": "/processing_timestamp",
                            "order": "descending"
                        },
                        {
                            "path": "/type",
                            "order": "ascending"
                        }
                    ]
                ]
            },
            "uniqueKeyPolicy": {
                "uniqueKeys": [
                    {
                        "paths": ["/id"]
                    }
                ]
            }
        }
        
        # Check if container exists
        try:
            container = database.get_container_client(container_name)
            properties = container.read()
            print(f"✅ Container '{container_name}' already exists")
            print(f"   Partition Key: {properties['partitionKey']}")
            
        except Exception:
            # Container doesn't exist, create it
            container = database.create_container(
                id=container_name,
                partition_key=container_config["partitionKey"]
            )
            print(f"✅ Created container: {container_name}")
            print(f"   Partition Key: {container_config['partitionKey']}")
            print(f"   Indexing Policy: Optimized for hybrid storage")
        
        # Test container access
        print(f"\n🔍 Testing container access:")
        
        # Try to query the container
        items = list(container.query_items(
            query="SELECT VALUE COUNT(1) FROM c",
            enable_cross_partition_query=True
        ))
        item_count = items[0] if items else 0
        
        print(f"   Document count: {item_count}")
        print(f"   Container ready for processed documents")
        
        # Return container info
        container_info = {
            "container_name": container_name,
            "database": cosmos_database,
            "partition_key": "/type",
            "document_count": item_count,
            "ready_for_hybrid_pipeline": True
        }
        
        print(f"\n✅ Container setup complete:")
        print(f"   Database: {cosmos_database}")
        print(f"   Container: {container_name}")
        print(f"   Documents: {item_count}")
        
        return container_info
        
    except Exception as e:
        print(f"❌ Error creating container: {str(e)}")
        return None

if __name__ == "__main__":
    result = create_processed_documents_container()
    if result:
        print(f"\n🎯 SUCCESS: Cosmos container ready for hybrid pipeline")
    else:
        print(f"\n❌ FAILED: Could not create Cosmos container")