#!/usr/bin/env python3
"""
Migrate 5 random research files and verify 100% content preservation
"""

import os
import random
import hashlib
from datetime import datetime
from azure.cosmos import CosmosClient

# Import the migration manager
import sys
sys.path.append('/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/scripts')
from idc_research_migration_v2 import IDCMigrationManager

# Cosmos credentials
COSMOS_ENDPOINT = "https://cosmos-research-analytics-prod.documents.azure.com:443/"
COSMOS_KEY = "cSq2cHQmhrYnjYPUdjDlAI7RxIOAEswXmDLAAywKVmPL5exy8IlSpUcQxdXtFuSutWRBx1wPqKAYACDbFfQKmA=="
COSMOS_DATABASE = "research-analytics-db"

def select_random_files():
    """Select 5 random files from the Research Library"""
    library_path = "/Users/mikaeleage/Institutional Data Center/Research Library"
    
    # Get all .md files
    import glob
    all_files = glob.glob(f"{library_path}/**/*.md", recursive=True)
    
    # Filter out very small files (likely empty or just headers)
    valid_files = []
    for f in all_files:
        try:
            size = os.path.getsize(f)
            if size > 100:  # At least 100 bytes
                valid_files.append(f)
        except:
            pass
    
    # Select 5 random files
    selected = random.sample(valid_files, min(5, len(valid_files)))
    return selected

def calculate_content_hash(content):
    """Calculate SHA256 hash of content for verification"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def main():
    print("=== 5-File Migration and Content Verification ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Select random files
    selected_files = select_random_files()
    print(f"Selected {len(selected_files)} random files for migration:")
    for f in selected_files:
        print(f"  - {os.path.basename(f)}")
    print()
    
    # Initialize migration manager
    manager = IDCMigrationManager()
    
    # Store original content for verification
    original_data = {}
    
    # Read and store original content
    print("📖 Reading original files...")
    for file_path in selected_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            original_data[file_path] = {
                'content': content,
                'size': len(content),
                'hash': calculate_content_hash(content),
                'lines': len(content.splitlines())
            }
            print(f"  ✓ {os.path.basename(file_path)}: {len(content)} characters, {len(content.splitlines())} lines")
    
    # Migrate the files
    print("\n🚀 Migrating files to Cosmos DB...")
    documents = manager.load_actual_research_files()
    
    # Filter to only our selected files
    selected_docs = []
    for doc in documents:
        if doc.get('sourceFile') in selected_files:
            selected_docs.append(doc)
    
    # Perform migration
    batch_results = manager.perform_batch_migration(selected_docs, batch_size=5)
    print(f"  ✓ Migration completed: {manager.migration_stats['successful_ingestions']}/{len(selected_docs)} successful")
    
    # Verify content in Cosmos DB
    print("\n🔍 Verifying content in Cosmos DB...")
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = client.get_database_client(COSMOS_DATABASE)
    container = database.get_container_client("institutional-data-center")
    
    verification_results = []
    
    for file_path in selected_files:
        filename = os.path.basename(file_path)
        print(f"\nVerifying: {filename}")
        
        # Query for the migrated document
        query = "SELECT * FROM c WHERE c.sourceFile = @sourceFile"
        params = [{"name": "@sourceFile", "value": file_path}]
        
        items = list(container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        
        if items:
            doc = items[0]
            cosmos_content = doc.get('content', '')
            cosmos_size = len(cosmos_content)
            cosmos_hash = calculate_content_hash(cosmos_content)
            cosmos_lines = len(cosmos_content.splitlines())
            
            original = original_data[file_path]
            
            # Compare
            match = {
                'file': filename,
                'size_match': cosmos_size == original['size'],
                'hash_match': cosmos_hash == original['hash'],
                'lines_match': cosmos_lines == original['lines'],
                'original_size': original['size'],
                'cosmos_size': cosmos_size,
                'content_preserved': cosmos_content == original['content']
            }
            
            verification_results.append(match)
            
            print(f"  Original: {original['size']} chars, {original['lines']} lines, hash: {original['hash'][:8]}...")
            print(f"  Cosmos:   {cosmos_size} chars, {cosmos_lines} lines, hash: {cosmos_hash[:8]}...")
            print(f"  Size Match: {'✅' if match['size_match'] else '❌'}")
            print(f"  Hash Match: {'✅' if match['hash_match'] else '❌'}")
            print(f"  100% Content Match: {'✅' if match['content_preserved'] else '❌'}")
            
            # If mismatch, show differences
            if not match['content_preserved']:
                print("  ⚠️  CONTENT MISMATCH DETECTED!")
                # Show first difference
                for i, (o, c) in enumerate(zip(original['content'], cosmos_content)):
                    if o != c:
                        print(f"  First difference at position {i}: '{o}' vs '{c}'")
                        break
        else:
            print(f"  ❌ Document not found in Cosmos DB!")
            verification_results.append({
                'file': filename,
                'error': 'Not found in Cosmos DB'
            })
    
    # Summary
    print("\n" + "="*60)
    print("📊 VERIFICATION SUMMARY:")
    print("="*60)
    
    perfect_matches = sum(1 for r in verification_results if r.get('content_preserved', False))
    print(f"\n✅ Perfect matches: {perfect_matches}/{len(verification_results)}")
    
    for result in verification_results:
        if 'error' in result:
            print(f"\n❌ {result['file']}: {result['error']}")
        else:
            status = "✅ PERFECT" if result['content_preserved'] else "❌ MISMATCH"
            print(f"\n{status} {result['file']}:")
            print(f"  - Size: {result['original_size']} → {result['cosmos_size']} {'✅' if result['size_match'] else '❌'}")
            print(f"  - Hash: {'✅' if result['hash_match'] else '❌'}")
            print(f"  - 100% Content: {'✅' if result['content_preserved'] else '❌'}")
    
    print("\n" + "="*60)
    if perfect_matches == len(verification_results):
        print("🎉 ALL FILES MIGRATED WITH 100% CONTENT PRESERVATION!")
    else:
        print("⚠️  Some files have content mismatches - investigation needed")

if __name__ == "__main__":
    main()