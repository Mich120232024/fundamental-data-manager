#\!/usr/bin/env python3
"""Search IDC for documents related to SAM's critical issues"""

import json
from datetime import datetime
from azure.cosmos import CosmosClient
import os

# Get connection details
endpoint = os.getenv('COSMOS_ENDPOINT', 'https://cosmos-research-analytics-prod.documents.azure.com:443/')
key = os.getenv('COSMOS_KEY')

# Initialize client
client = CosmosClient(endpoint, key)
database = client.get_database_client('research-analytics-db')
container = database.get_container_client('institutional-data-center')

def search_idc():
    print("Searching IDC for documents related to SAM's issues...\n")
    
    # First, let's see what's actually in the IDC
    print("1. Checking what documents exist in IDC...")
    basic_query = "SELECT c.id, c.title, c.type, c.domain, c.pk FROM c"
    
    all_docs = list(container.query_items(
        query=basic_query,
        enable_cross_partition_query=True
    ))
    
    print(f"Total documents in IDC: {len(all_docs)}")
    
    # Show document types
    doc_types = {}
    for doc in all_docs:
        doc_type = doc.get('type', 'unknown')
        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
    
    print("\nDocument types in IDC:")
    for doc_type, count in doc_types.items():
        print(f"  - {doc_type}: {count}")
    
    # Now search for relevant content
    print("\n2. Searching for architecture/governance content...")
    
    relevant_docs = []
    
    # Search in all documents for keywords
    for doc in all_docs:
        # Get full document
        full_doc = container.read_item(item=doc['id'], partition_key=doc['pk'])
        
        # Convert to string for searching
        doc_str = json.dumps(full_doc).lower()
        
        # Check for relevant keywords
        keywords = ['multi-box', 'message fail', 'architecture', 'governance', 
                   'adoption', 'methods', 'role', 'constitutional', 'bug', 
                   'deployment', 'communication']
        
        for keyword in keywords:
            if keyword in doc_str:
                relevant_docs.append({
                    'id': full_doc.get('id'),
                    'title': full_doc.get('title', 'N/A'),
                    'type': full_doc.get('type', 'N/A'),
                    'domain': full_doc.get('domain', 'N/A'),
                    'matched_keyword': keyword
                })
                break
    
    print(f"\nFound {len(relevant_docs)} potentially relevant documents:")
    for doc in relevant_docs[:10]:  # Show first 10
        print(f"\n- ID: {doc['id']}")
        print(f"  Title: {doc['title']}")
        print(f"  Type: {doc['type']}")
        print(f"  Domain: {doc['domain']}")
        print(f"  Matched: {doc['matched_keyword']}")
    
    # Look specifically for governance policies
    print("\n3. Checking governance policies...")
    gov_query = "SELECT * FROM c WHERE c.type = 'governance_policy'"
    
    gov_docs = list(container.query_items(
        query=gov_query,
        enable_cross_partition_query=True
    ))
    
    print(f"\nFound {len(gov_docs)} governance policies")
    for doc in gov_docs[:5]:
        print(f"\n- {doc.get('title', doc.get('id'))}")
        if 'content' in doc:
            content = str(doc['content'])[:300]
            print(f"  Content preview: {content}...")

if __name__ == "__main__":
    search_idc()
