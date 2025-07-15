#!/usr/bin/env python3
"""
Quick API Registry Browser - Simple viewer for the API registry container

A lightweight browser that doesn't require additional packages.
"""

import os
import json
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def quick_browse():
    """Quick browse API registry"""
    
    # Get credentials
    cosmos_url = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    
    if not cosmos_url or not cosmos_key:
        print("❌ Missing Cosmos DB credentials")
        return
    
    try:
        # Connect to Cosmos DB
        client = CosmosClient(cosmos_url, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        container = database.get_container_client("api_registry")
        
        while True:
            print("\n" + "="*60)
            print("🔍 API REGISTRY QUICK BROWSER")
            print("="*60)
            print("1. View all APIs")
            print("2. View by category") 
            print("3. View schema requirements")
            print("4. Search by name")
            print("5. Container statistics")
            print("0. Exit")
            
            choice = input("\nChoice: ").strip()
            
            if choice == "0":
                break
                
            elif choice == "1":
                # View all APIs
                print("\n📊 All APIs in Registry:")
                print("-"*60)
                
                query = "SELECT * FROM c WHERE c.category != 'system' ORDER BY c.apiName"
                results = list(container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ))
                
                if not results:
                    print("No API documents found (only system docs exist)")
                else:
                    print(f"\nFound {len(results)} APIs:\n")
                    print(f"{'#':<4} {'Name':<30} {'Category':<15} {'Status':<10}")
                    print("-"*60)
                    
                    for i, doc in enumerate(results):
                        name = doc.get('apiName', doc.get('id', 'N/A'))[:28]
                        category = doc.get('category', 'N/A')[:13]
                        status = doc.get('status', 'N/A')[:8]
                        print(f"{i+1:<4} {name:<30} {category:<15} {status:<10}")
                
                input("\nPress Enter to continue...")
                
            elif choice == "2":
                # View by category
                print("\n📁 View by Category:")
                
                # Get categories
                query = "SELECT DISTINCT c.category FROM c"
                categories = list(container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ))
                
                print("\nAvailable categories:")
                for i, cat in enumerate(categories):
                    print(f"  {i+1}. {cat['category']}")
                
                cat_choice = input("\nSelect category: ").strip()
                try:
                    category = categories[int(cat_choice)-1]['category']
                    
                    query = f"SELECT * FROM c WHERE c.category = '{category}'"
                    results = list(container.query_items(
                        query=query,
                        enable_cross_partition_query=True
                    ))
                    
                    print(f"\n📊 APIs in '{category}' category:")
                    print("-"*60)
                    
                    for i, doc in enumerate(results):
                        print(f"\n{i+1}. {doc.get('apiName', doc.get('id'))}")
                        print(f"   Provider: {doc.get('provider', 'N/A')}")
                        print(f"   Status: {doc.get('status', 'N/A')}")
                        print(f"   Auth: {doc.get('authType', 'N/A')}")
                        
                except (ValueError, IndexError):
                    print("❌ Invalid selection")
                
                input("\nPress Enter to continue...")
                
            elif choice == "3":
                # View schema requirements
                print("\n📋 Schema Requirements:")
                print("-"*60)
                
                try:
                    schema_doc = container.read_item(
                        item="schema_requirements_v1",
                        partition_key="system"
                    )
                    
                    print("\nKey field requirements:\n")
                    
                    fields = ["apiName", "provider", "baseUrl", "authType", "status"]
                    for field in fields:
                        if field in schema_doc:
                            print(f"{field}:")
                            print(f"  → {schema_doc[field]}\n")
                    
                except Exception as e:
                    print(f"Schema document not found: {e}")
                
                input("\nPress Enter to continue...")
                
            elif choice == "4":
                # Search by name
                search = input("\n🔍 Enter search term: ").strip()
                
                if search:
                    query = f"""
                    SELECT * FROM c 
                    WHERE CONTAINS(LOWER(c.apiName), LOWER('{search}'))
                       OR CONTAINS(LOWER(c.provider), LOWER('{search}'))
                    """
                    
                    results = list(container.query_items(
                        query=query,
                        enable_cross_partition_query=True
                    ))
                    
                    print(f"\n📊 Search results for '{search}':")
                    print("-"*60)
                    
                    if not results:
                        print("No matches found")
                    else:
                        for i, doc in enumerate(results):
                            print(f"\n{i+1}. {doc.get('apiName', doc.get('id'))}")
                            print(f"   Provider: {doc.get('provider', 'N/A')}")
                            print(f"   Category: {doc.get('category', 'N/A')}")
                            print(f"   Description: {doc.get('description', 'N/A')[:60]}...")
                
                input("\nPress Enter to continue...")
                
            elif choice == "5":
                # Statistics
                print("\n📊 Container Statistics:")
                print("-"*60)
                
                # Total count
                query = "SELECT VALUE COUNT(1) FROM c"
                total = list(container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ))[0]
                
                print(f"Total documents: {total}")
                
                # Count by category
                categories = ["system", "financial", "weather", "geospatial", "other"]
                print("\nDocuments by category:")
                
                for cat in categories:
                    query = f"SELECT VALUE COUNT(1) FROM c WHERE c.category = '{cat}'"
                    count = list(container.query_items(
                        query=query,
                        enable_cross_partition_query=True
                    ))[0]
                    
                    if count > 0:
                        print(f"  • {cat}: {count}")
                
                # System docs
                query = "SELECT c.id, c.apiName FROM c WHERE c.category = 'system'"
                system_docs = list(container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ))
                
                if system_docs:
                    print("\nSystem documents:")
                    for doc in system_docs:
                        print(f"  • {doc['id']}")
                
                input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_browse()