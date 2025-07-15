#!/usr/bin/env python3
"""
Fetch and display the Constitutional Accountability Matrix
"""

from cosmos_db_manager import get_db_manager
import json

def fetch_accountability_matrix():
    """Fetch the accountability matrix document"""
    
    db = get_db_manager()
    documents_container = db.database.get_container_client('documents')
    
    try:
        # Get the accountability matrix
        doc = documents_container.read_item(
            item='DOC-GOV-CONST-002_constitutional_accountability_matrix',
            partition_key='DOC-GOV-CONST-002'
        )
        
        print("\n📋 CONSTITUTIONAL ACCOUNTABILITY MATRIX")
        print("="*80)
        print(f"Document ID: {doc['documentId']}")
        print(f"Title: {doc['title']}")
        print(f"Status: {doc['status']}")
        print("="*80)
        print("\nCONTENT:")
        print(doc['content'])
        
        return doc
        
    except Exception as e:
        print(f"❌ Error fetching accountability matrix: {e}")
        return None

if __name__ == "__main__":
    fetch_accountability_matrix()