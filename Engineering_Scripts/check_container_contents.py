#!/usr/bin/env python3
"""
Check the contents of institutional-data-center container
"""

import os
import json
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_container():
    """Check if institutional-data-center container has any documents"""
    endpoint = os.getenv('COSMOS_ENDPOINT')
    key = os.getenv('COSMOS_KEY')
    database_name = os.getenv('COSMOS_DATABASE', 'research-analytics-db')
    
    if not endpoint or not key:
        print("❌ ERROR: COSMOS_ENDPOINT and COSMOS_KEY must be set in .env file")
        return
    
    client = CosmosClient(endpoint, key)
    database = client.get_database_client(database_name)
    
    # Check institutional-data-center container
    container_name = 'institutional-data-center'
    try:
        container = database.get_container_client(container_name)
        
        # Get total count
        query = "SELECT VALUE COUNT(1) FROM c"
        result = list(container.query_items(query, enable_cross_partition_query=True))
        total_count = result[0] if result else 0
        
        print(f"\n📊 Container: {container_name}")
        print(f"Total documents: {total_count}")
        
        if total_count > 0:
            # Get sample documents
            sample_query = "SELECT TOP 5 * FROM c"
            samples = list(container.query_items(sample_query, enable_cross_partition_query=True))
            
            print("\nSample documents:")
            for i, doc in enumerate(samples, 1):
                print(f"\n{i}. ID: {doc.get('id', 'N/A')}")
                print(f"   Type: {doc.get('type', 'N/A')}")
                print(f"   Keys: {', '.join(doc.keys())}")
                
    except Exception as e:
        print(f"❌ Error accessing {container_name}: {str(e)}")
    
    # Also check messages container
    print("\n" + "="*80)
    container_name = 'messages'
    try:
        container = database.get_container_client(container_name)
        
        # Search for institutional or SAM related content
        queries = [
            ("Multi-box mentions", "SELECT * FROM c WHERE CONTAINS(LOWER(c.content), 'multi-box') OR CONTAINS(LOWER(c.content), 'multibox')"),
            ("SAM mentions", "SELECT * FROM c WHERE CONTAINS(LOWER(c.content), 'sam') OR CONTAINS(LOWER(c.subject), 'sam')"),
            ("Governance mentions", "SELECT * FROM c WHERE CONTAINS(LOWER(c.content), 'governance') AND CONTAINS(LOWER(c.content), 'adoption')"),
            ("Architecture issues", "SELECT * FROM c WHERE CONTAINS(LOWER(c.content), 'architecture') AND (CONTAINS(LOWER(c.content), 'issue') OR CONTAINS(LOWER(c.content), 'bug'))")
        ]
        
        print(f"\n📊 Container: {container_name}")
        for label, query in queries:
            try:
                results = list(container.query_items(query, enable_cross_partition_query=True))
                print(f"\n{label}: {len(results)} documents found")
                
                if results:
                    # Show first result
                    doc = results[0]
                    print(f"  Sample - ID: {doc.get('id', 'N/A')}")
                    print(f"  From: {doc.get('from', 'N/A')}")
                    print(f"  Subject: {doc.get('subject', 'N/A')}")
                    print(f"  Date: {doc.get('timestamp', 'N/A')}")
                    content = doc.get('content', '')
                    if content:
                        preview = content[:200] + "..." if len(content) > 200 else content
                        print(f"  Content preview: {preview}")
                        
            except Exception as e:
                print(f"  Query error: {str(e)}")
                
    except Exception as e:
        print(f"❌ Error accessing {container_name}: {str(e)}")

if __name__ == "__main__":
    check_container()