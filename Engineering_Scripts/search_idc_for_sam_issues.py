#\!/usr/bin/env python3
"""Search IDC for documents related to SAM's critical issues"""

import json
from cosmos_db_manager import get_db_manager

def search_idc():
    db = get_db_manager()
    db.select_database('research-analytics-db')
    db.select_container('institutional-data-center')
    
    print("Searching IDC for relevant documents...\n")
    
    # Search 1: Multi-box architecture
    query1 = """
    SELECT * FROM c 
    WHERE CONTAINS(LOWER(c.searchText), 'multi-box') 
    OR CONTAINS(LOWER(c.searchText), 'message fail')
    OR CONTAINS(LOWER(c.searchText), 'architecture')
    """
    
    # Search 2: Governance methods adoption
    query2 = """
    SELECT * FROM c 
    WHERE CONTAINS(LOWER(c.searchText), 'governance') 
    OR CONTAINS(LOWER(c.searchText), 'adoption')
    OR CONTAINS(LOWER(c.searchText), 'methods')
    """
    
    # Search 3: Role definitions
    query3 = """
    SELECT * FROM c 
    WHERE CONTAINS(LOWER(c.searchText), 'role') 
    OR CONTAINS(LOWER(c.searchText), 'constitutional')
    OR c.type = 'governance_policy'
    """
    
    results = []
    
    for query_name, query in [("Architecture Issues", query1), 
                               ("Governance Adoption", query2),
                               ("Role Definitions", query3)]:
        print(f"\nSearching for {query_name}...")
        try:
            items = db.query_items(query)
            print(f"Found {len(items)} documents")
            for item in items[:3]:  # Show first 3 of each
                print(f"\n- ID: {item.get('id')}")
                print(f"  Title: {item.get('title', 'N/A')}")
                print(f"  Type: {item.get('type', 'N/A')}")
                print(f"  Domain: {item.get('domain', 'N/A')}")
                if 'content' in item:
                    content_preview = str(item['content'])[:200] + "..."
                    print(f"  Content: {content_preview}")
            results.extend(items)
        except Exception as e:
            print(f"Error: {e}")
    
    return results

if __name__ == "__main__":
    results = search_idc()
    print(f"\n\nTotal documents found: {len(results)}")
