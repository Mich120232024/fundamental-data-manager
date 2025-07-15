#!/usr/bin/env python3
"""
Simple query script to access any Cosmos DB container
"""

from cosmos_db_manager import get_db_manager
import json

def query_container(container_name, query="SELECT * FROM c", limit=None):
    """Query any container with optional limit"""
    db = get_db_manager()
    
    try:
        container = db.database.get_container_client(container_name)
        
        if limit:
            query = f"SELECT TOP {limit} * FROM c"
        
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        return items
    except Exception as e:
        print(f"Error querying {container_name}: {e}")
        return None

def list_containers():
    """List all available containers"""
    db = get_db_manager()
    containers = list(db.database.list_containers())
    return [c['id'] for c in containers]

def count_documents(container_name):
    """Count documents in container"""
    db = get_db_manager()
    try:
        container = db.database.get_container_client(container_name)
        count_query = "SELECT VALUE COUNT(1) FROM c"
        result = list(container.query_items(query=count_query, enable_cross_partition_query=True))
        return result[0] if result else 0
    except:
        return 0

if __name__ == "__main__":
    print("🔍 COSMOS DB CONTAINER ACCESS")
    print("=" * 40)
    
    # List all containers
    containers = list_containers()
    print(f"Available containers: {containers}")
    
    # Check each container
    for container in containers:
        count = count_documents(container)
        print(f"\n📂 {container}: {count} documents")
        
        if count > 0:
            # Get sample
            sample = query_container(container, limit=2)
            if sample:
                print("   Sample fields:", list(sample[0].keys())[:8], "...")