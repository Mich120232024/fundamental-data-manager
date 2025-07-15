#!/usr/bin/env python3
"""
Check which files failed to migrate and why
"""

import os
import glob
from datetime import datetime
from azure.cosmos import CosmosClient

# Cosmos credentials
COSMOS_ENDPOINT = "https://cosmos-research-analytics-prod.documents.azure.com:443/"
COSMOS_KEY = "cSq2cHQmhrYnjYPUdjDlAI7RxIOAEswXmDLAAywKVmPL5exy8IlSpUcQxdXtFuSutWRBx1wPqKAYACDbFfQKmA=="
COSMOS_DATABASE = "research-analytics-db"

def check_migration_status():
    """Check which files from Research Library are in Cosmos DB"""
    print("=== Migration Status Check ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Get all files from Research Library
    library_path = "/Users/mikaeleage/Institutional Data Center/Research Library"
    all_files = glob.glob(f"{library_path}/**/*.md", recursive=True)
    print(f"Total files in Research Library: {len(all_files)}")
    
    # Connect to Cosmos DB
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = client.get_database_client(COSMOS_DATABASE)
    container = database.get_container_client("institutional-data-center")
    
    # Get all documents from Cosmos DB
    query = "SELECT c.id, c.title, c.sourceFile FROM c WHERE c.type = 'research_finding'"
    cosmos_docs = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    print(f"Total research documents in Cosmos DB: {len(cosmos_docs)}")
    
    # Create a map of source files in Cosmos
    cosmos_source_files = {doc.get('sourceFile', ''): doc for doc in cosmos_docs if doc.get('sourceFile')}
    
    # Check which files are missing
    missing_files = []
    found_files = []
    encoding_error_files = []
    
    for file_path in all_files:
        if file_path in cosmos_source_files:
            found_files.append(file_path)
        else:
            # Check if it's the encoding error file
            if 'claude_code_solutions.md' in file_path:
                encoding_error_files.append(file_path)
            else:
                missing_files.append(file_path)
    
    print(f"\n📊 MIGRATION STATUS:")
    print(f"✅ Successfully migrated: {len(found_files)} files")
    print(f"❌ Not in Cosmos DB: {len(missing_files)} files")
    print(f"⚠️  Encoding errors: {len(encoding_error_files)} files")
    
    # Show details of missing files
    if missing_files:
        print(f"\n❌ FILES NOT MIGRATED ({len(missing_files)}):")
        for i, file_path in enumerate(missing_files[:10], 1):
            print(f"   {i}. {os.path.basename(file_path)}")
        if len(missing_files) > 10:
            print(f"   ... and {len(missing_files) - 10} more")
    
    if encoding_error_files:
        print(f"\n⚠️  ENCODING ERROR FILES:")
        for file_path in encoding_error_files:
            print(f"   - {os.path.basename(file_path)}")
    
    # Check for duplicates
    print(f"\n🔍 CHECKING FOR DUPLICATES:")
    title_counts = {}
    for doc in cosmos_docs:
        title = doc.get('title', '')
        if title:
            title_counts[title] = title_counts.get(title, 0) + 1
    
    duplicates = {title: count for title, count in title_counts.items() if count > 1}
    if duplicates:
        print(f"Found {len(duplicates)} duplicate titles:")
        for title, count in list(duplicates.items())[:5]:
            print(f"   - '{title[:50]}...' appears {count} times")
    else:
        print("No duplicates found")
    
    return missing_files, encoding_error_files

if __name__ == "__main__":
    missing_files, encoding_error_files = check_migration_status()