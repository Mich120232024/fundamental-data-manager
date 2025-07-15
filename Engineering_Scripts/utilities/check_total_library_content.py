#!/usr/bin/env python3
"""
Check ALL content in the IDC library to ensure no loss
"""

import json
from datetime import datetime
from azure.cosmos import CosmosClient

# Cosmos credentials
COSMOS_ENDPOINT = "https://cosmos-research-analytics-prod.documents.azure.com:443/"
COSMOS_KEY = "cSq2cHQmhrYnjYPUdjDlAI7RxIOAEswXmDLAAywKVmPL5exy8IlSpUcQxdXtFuSutWRBx1wPqKAYACDbFfQKmA=="
COSMOS_DATABASE = "research-analytics-db"

def check_all_content():
    """Check all documents in the IDC library"""
    print("=== Complete IDC Library Content Check ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    try:
        # Connect to Cosmos DB
        client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        database = client.get_database_client(COSMOS_DATABASE)
        container = database.get_container_client("institutional-data-center")
        
        # Get ALL documents
        query = "SELECT * FROM c"
        all_docs = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        print(f"Total documents in library: {len(all_docs)}")
        print()
        
        # Categorize documents
        real_research = []
        test_data = []
        infrastructure = []
        
        total_content_size = 0
        
        for doc in all_docs:
            doc_id = doc.get('id', '')
            title = doc.get('title', '')
            content = doc.get('content', '')
            source_file = doc.get('sourceFile', '')
            
            # Calculate content size
            if isinstance(content, str):
                content_size = len(content)
            elif isinstance(content, dict):
                content_size = len(json.dumps(content))
            else:
                content_size = 0
            
            total_content_size += content_size
            
            # Categorize
            if source_file and '/Institutional Data Center/Research Library/' in source_file:
                real_research.append({
                    'id': doc_id,
                    'title': title[:50] + '...' if len(title) > 50 else title,
                    'size': content_size,
                    'source': source_file
                })
            elif 'test' in doc_id.lower() or 'verification' in title.lower():
                test_data.append({
                    'id': doc_id,
                    'title': title[:50] + '...' if len(title) > 50 else title,
                    'size': content_size
                })
            else:
                infrastructure.append({
                    'id': doc_id,
                    'title': title[:50] + '...' if len(title) > 50 else title,
                    'size': content_size
                })
        
        # Report findings
        print("📊 CONTENT BREAKDOWN:")
        print(f"\n1. Real Research Documents: {len(real_research)}")
        if real_research:
            total_research_size = sum(d['size'] for d in real_research)
            print(f"   Total size: {total_research_size:,} characters")
            print("   Sample files:")
            for doc in real_research[:5]:
                print(f"   - {doc['title']} ({doc['size']:,} chars)")
        
        print(f"\n2. Test/Verification Data: {len(test_data)}")
        if test_data:
            total_test_size = sum(d['size'] for d in test_data)
            print(f"   Total size: {total_test_size:,} characters")
            print("   Sample files:")
            for doc in test_data[:5]:
                print(f"   - {doc['title']} ({doc['size']:,} chars)")
        
        print(f"\n3. Infrastructure/Other: {len(infrastructure)}")
        if infrastructure:
            total_infra_size = sum(d['size'] for d in infrastructure)
            print(f"   Total size: {total_infra_size:,} characters")
            print("   Sample files:")
            for doc in infrastructure[:5]:
                print(f"   - {doc['title']} ({doc['size']:,} chars)")
        
        print(f"\n📈 TOTAL CONTENT SIZE: {total_content_size:,} characters")
        
        # Check for duplicates
        print("\n🔍 DUPLICATE CHECK:")
        titles = {}
        duplicates = []
        
        for doc in all_docs:
            title = doc.get('title', '')
            if title in titles:
                duplicates.append(title)
            else:
                titles[title] = 1
        
        if duplicates:
            print(f"⚠️  Found {len(duplicates)} duplicate titles:")
            for dup in duplicates[:5]:
                print(f"   - {dup}")
        else:
            print("✅ No duplicate titles found")
        
        # Check for empty content
        print("\n📄 CONTENT INTEGRITY CHECK:")
        empty_docs = []
        small_docs = []
        
        for doc in all_docs:
            content = doc.get('content', '')
            if isinstance(content, str):
                size = len(content)
            elif isinstance(content, dict):
                size = len(json.dumps(content))
            else:
                size = 0
            
            if size == 0:
                empty_docs.append(doc.get('title', doc.get('id', 'Unknown')))
            elif size < 100:
                small_docs.append((doc.get('title', doc.get('id', 'Unknown')), size))
        
        if empty_docs:
            print(f"⚠️  {len(empty_docs)} documents with empty content")
        else:
            print("✅ No empty documents")
        
        if small_docs:
            print(f"⚠️  {len(small_docs)} documents with less than 100 characters")
        else:
            print("✅ All documents have substantial content")
        
        # Summary
        print("\n" + "="*60)
        print("📊 LIBRARY HEALTH SUMMARY:")
        print("="*60)
        print(f"Total Documents: {len(all_docs)}")
        print(f"Real Research Files: {len(real_research)}")
        print(f"Total Content Size: {total_content_size:,} characters")
        print(f"Average Document Size: {total_content_size // len(all_docs):,} characters" if all_docs else "No documents")
        
        if real_research:
            print(f"\n✅ Research Library contains {len(real_research)} real research documents")
            print(f"✅ Total research content: {sum(d['size'] for d in real_research):,} characters")
        else:
            print("\n⚠️  No real research documents found from Research Library source")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_all_content()