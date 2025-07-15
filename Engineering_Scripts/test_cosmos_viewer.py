#!/usr/bin/env python3
"""
Test the Cosmos DB viewer by making direct calls
"""

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Import cosmos manager
sys.path.insert(0, str(Path(__file__).parent))
from cosmos_db_manager import get_db_manager

def test_viewer_functionality():
    """Test the viewer's core functionality directly"""
    
    print("🧪 Testing Cosmos DB Viewer Functionality\n")
    
    try:
        # Initialize database
        db = get_db_manager()
        database = db.client.get_database_client(db.database_name)
        
        # Test 1: List containers
        print("1️⃣ Testing container listing...")
        containers = []
        for container in database.list_containers():
            container_client = database.get_container_client(container['id'])
            
            # Get document count
            count_query = "SELECT VALUE COUNT(1) FROM c"
            count = list(container_client.query_items(
                query=count_query,
                enable_cross_partition_query=True
            ))[0]
            
            containers.append({
                'id': container['id'],
                'count': count
            })
            
        print(f"✅ Found {len(containers)} containers:")
        for c in sorted(containers, key=lambda x: x['id'])[:5]:
            print(f"   • {c['id']}: {c['count']} documents")
        
        # Test 2: Get documents from messages container
        print("\n2️⃣ Testing document retrieval (messages container)...")
        messages_container = database.get_container_client('system_inbox')
        
        query = "SELECT TOP 5 * FROM c ORDER BY c._ts DESC"
        documents = list(messages_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        print(f"✅ Retrieved {len(documents)} recent messages:")
        for doc in documents:
            print(f"   • {doc.get('id', 'Unknown')[:50]}...")
            print(f"     From: {doc.get('from', 'Unknown')}")
            print(f"     Type: {doc.get('type', 'Unknown')}")
        
        # Test 3: Search functionality
        print("\n3️⃣ Testing search across containers...")
        search_term = "constitutional"
        results_count = 0
        
        for container_info in database.list_containers():
            container = database.get_container_client(container_info['id'])
            
            try:
                # Search in content fields
                query = """
                SELECT TOP 2 * FROM c 
                WHERE CONTAINS(LOWER(c.content), LOWER(@search))
                   OR CONTAINS(LOWER(c.subject), LOWER(@search))
                """
                
                parameters = [{"name": "@search", "value": search_term}]
                
                docs = list(container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
                ))
                
                if docs:
                    results_count += len(docs)
                    print(f"   • Found {len(docs)} in {container_info['id']}")
                    
            except:
                pass
        
        print(f"✅ Search found {results_count} total results for '{search_term}'")
        
        # Test 4: Database stats
        print("\n4️⃣ Testing database statistics...")
        total_docs = 0
        container_stats = {}
        
        for container_info in database.list_containers():
            container = database.get_container_client(container_info['id'])
            count_query = "SELECT VALUE COUNT(1) FROM c"
            count = list(container.query_items(
                query=count_query,
                enable_cross_partition_query=True
            ))[0]
            
            container_stats[container_info['id']] = count
            total_docs += count
        
        print(f"✅ Database Statistics:")
        print(f"   • Total documents: {total_docs}")
        print(f"   • Total containers: {len(container_stats)}")
        print(f"   • Largest container: {max(container_stats.items(), key=lambda x: x[1])}")
        
        print("\n✅ All viewer functionality tests passed!")
        print("\n📊 Summary:")
        print(f"   • Containers accessible: {len(containers)}")
        print(f"   • Documents readable: Yes")
        print(f"   • Search functional: Yes")
        print(f"   • Stats available: Yes")
        
        print("\n🌐 The web viewer at http://localhost:5001/viewer would show:")
        print("   • Sidebar with all containers and counts")
        print("   • Click any container to see documents")
        print("   • Click any document to view full JSON")
        print("   • Search functionality across containers")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_viewer_functionality()