#!/usr/bin/env python3
"""
Migrate only the missing files with proper duplicate handling and encoding support
"""

import os
import glob
import hashlib
import chardet
from datetime import datetime
from azure.cosmos import CosmosClient
import sys
sys.path.append('/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/scripts')
from idc_research_migration_v2 import IDCMigrationManager

# Cosmos credentials
COSMOS_ENDPOINT = "https://cosmos-research-analytics-prod.documents.azure.com:443/"
COSMOS_KEY = "cSq2cHQmhrYnjYPUdjDlAI7RxIOAEswXmDLAAywKVmPL5exy8IlSpUcQxdXtFuSutWRBx1wPqKAYACDbFfQKmA=="
COSMOS_DATABASE = "research-analytics-db"

def read_file_with_encoding_detection(file_path):
    """Read file with automatic encoding detection"""
    # First try to detect encoding
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    
    # Try detected encoding first, then fallbacks
    encodings = [encoding, 'utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1', 'cp1252']
    
    for enc in encodings:
        if enc:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                print(f"   ✓ Read with encoding: {enc}")
                return content
            except (UnicodeDecodeError, TypeError):
                continue
    
    # If all else fails, read as binary and decode with errors ignored
    with open(file_path, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')
        print(f"   ⚠️  Read with errors ignored")
        return content

def generate_unique_id(file_path, existing_ids):
    """Generate a unique ID for the document"""
    base_name = os.path.basename(file_path).replace('.md', '').replace(' ', '_').lower()
    
    # Clean the base name
    base_id = ''.join(c if c.isalnum() or c == '_' else '_' for c in base_name)
    base_id = f"research_finding_{base_id}"
    
    # If ID exists, add a counter
    if base_id in existing_ids:
        counter = 1
        while f"{base_id}_v{counter}" in existing_ids:
            counter += 1
        return f"{base_id}_v{counter}"
    
    return base_id

def migrate_missing_files():
    """Migrate only the files that are missing from Cosmos DB"""
    print("=== Migrating Missing Files with Enhanced Support ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Get all files from Research Library
    library_path = "/Users/mikaeleage/Institutional Data Center/Research Library"
    all_files = glob.glob(f"{library_path}/**/*.md", recursive=True)
    
    # Connect to Cosmos DB
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = client.get_database_client(COSMOS_DATABASE)
    container = database.get_container_client("institutional-data-center")
    
    # Get existing documents
    query = "SELECT c.id, c.sourceFile FROM c WHERE c.type = 'research_finding'"
    existing_docs = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    existing_source_files = {doc.get('sourceFile', '') for doc in existing_docs}
    existing_ids = {doc.get('id', '') for doc in existing_docs}
    
    # Find missing files
    missing_files = [f for f in all_files if f not in existing_source_files]
    
    print(f"Found {len(missing_files)} files to migrate")
    
    # Initialize migration manager
    manager = IDCMigrationManager()
    
    # Process missing files
    successful = 0
    failed = 0
    
    for i, file_path in enumerate(missing_files, 1):
        print(f"\n[{i}/{len(missing_files)}] Processing: {os.path.basename(file_path)}")
        
        try:
            # Read file with encoding detection
            content = read_file_with_encoding_detection(file_path)
            
            # Get file metadata
            stat = os.stat(file_path)
            
            # Extract title from content
            lines = content.strip().split('\n')
            title = lines[0].strip('# ').strip() if lines else os.path.basename(file_path)
            
            # Generate unique ID
            doc_id = generate_unique_id(file_path, existing_ids)
            existing_ids.add(doc_id)
            
            # Create document
            document = {
                "id": doc_id,
                "type": "research_finding",
                "category": "research",
                "title": title[:100] + "..." if len(title) > 100 else title,
                "content": content,
                "sourceFile": file_path,
                "fileSize": stat.st_size,
                "createdAt": datetime.utcnow().isoformat(),
                "createdAtEpoch": int(datetime.utcnow().timestamp() * 1000),
                "lastModified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "contentHash": hashlib.sha256(content.encode('utf-8')).hexdigest(),
                "version": "2.0",
                "searchText": f"{title} {content[:500]}".lower(),
                "tags": [],
                "metadata": {
                    "encoding": "utf-8",
                    "lineCount": len(lines),
                    "wordCount": len(content.split()),
                    "characterCount": len(content)
                }
            }
            
            # Insert into Cosmos DB
            container.create_item(body=document)
            print(f"   ✅ Successfully migrated with ID: {doc_id}")
            successful += 1
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"MIGRATION COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Successfully migrated: {successful} files")
    print(f"❌ Failed: {failed} files")
    print(f"📊 Success rate: {(successful / len(missing_files) * 100):.1f}%")
    
    return successful, failed

if __name__ == "__main__":
    # Install chardet if not available
    try:
        import chardet
    except ImportError:
        print("Installing chardet for encoding detection...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "chardet"])
        import chardet
    
    migrate_missing_files()