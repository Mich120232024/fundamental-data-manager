#!/usr/bin/env python3
"""
Analyze the 37 documents migrated to the audit container
Access using Azure Cosmos DB credentials from .env
"""

import os
from azure.cosmos import CosmosClient
from datetime import datetime
import json

def load_env_variables():
    """Load environment variables from .env file"""
    env_path = "/Users/mikaeleage/Research & Analytics Services/.env"
    env_vars = {}
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    return env_vars

def connect_to_cosmos():
    """Connect to Azure Cosmos DB using credentials from .env"""
    env_vars = load_env_variables()
    
    endpoint = env_vars.get('COSMOS_ENDPOINT')
    key = env_vars.get('COSMOS_KEY')
    database_name = env_vars.get('COSMOS_DATABASE')
    
    if not all([endpoint, key, database_name]):
        raise ValueError("Missing required Cosmos DB credentials in .env file")
    
    print(f"🔌 Connecting to Cosmos DB...")
    print(f"   Endpoint: {endpoint}")
    print(f"   Database: {database_name}")
    
    client = CosmosClient(endpoint, key)
    database = client.get_database_client(database_name)
    
    return client, database

def explore_containers(database):
    """Explore available containers in the database"""
    print("\n📊 EXPLORING AVAILABLE CONTAINERS")
    print("=" * 50)
    
    containers = list(database.list_containers())
    
    for container_info in containers:
        container_id = container_info['id']
        print(f"\n🗂️  Container: {container_id}")
        
        try:
            container = database.get_container_client(container_id)
            
            # Get container properties
            properties = container.read()
            print(f"   Partition Key: {properties.get('partitionKey', 'Not specified')}")
            
            # Count items in container
            query = "SELECT VALUE COUNT(1) FROM c"
            items = list(container.query_items(query=query, enable_cross_partition_query=True))
            item_count = items[0] if items else 0
            print(f"   Item Count: {item_count}")
            
            # Show sample item structure if items exist
            if item_count > 0:
                sample_query = "SELECT TOP 1 * FROM c"
                sample_items = list(container.query_items(query=sample_query, enable_cross_partition_query=True))
                if sample_items:
                    sample = sample_items[0]
                    print(f"   Sample Fields: {list(sample.keys())[:10]}...")  # Show first 10 fields
                    
        except Exception as e:
            print(f"   ❌ Error accessing container: {e}")
    
    return containers

def analyze_audit_container(database):
    """Analyze the audit container specifically"""
    print("\n🔍 ANALYZING AUDIT CONTAINER")
    print("=" * 50)
    
    try:
        # Try to access audit container
        audit_container = database.get_container_client('audit')
        
        # Count total documents
        count_query = "SELECT VALUE COUNT(1) FROM c"
        count_result = list(audit_container.query_items(query=count_query, enable_cross_partition_query=True))
        total_docs = count_result[0] if count_result else 0
        
        print(f"📄 Total Documents in Audit Container: {total_docs}")
        
        if total_docs == 0:
            print("❌ No documents found in audit container")
            return
        
        # Analyze document types
        type_query = """
        SELECT c.docType, COUNT(1) as count
        FROM c
        GROUP BY c.docType
        """
        
        type_results = list(audit_container.query_items(query=type_query, enable_cross_partition_query=True))
        
        print("\n📊 Document Types:")
        for result in type_results:
            doc_type = result.get('docType', 'Unknown')
            count = result.get('count', 0)
            print(f"   • {doc_type}: {count} documents")
        
        # Analyze workspaces
        workspace_query = """
        SELECT c.workspace, COUNT(1) as count
        FROM c
        GROUP BY c.workspace
        """
        
        workspace_results = list(audit_container.query_items(query=workspace_query, enable_cross_partition_query=True))
        
        print("\n🏢 Workspaces:")
        for result in workspace_results:
            workspace = result.get('workspace', 'Unknown')
            count = result.get('count', 0)
            print(f"   • {workspace}: {count} documents")
        
        # Get sample documents
        sample_query = "SELECT TOP 5 c.id, c.title, c.workspace, c.docType, c.lastModified FROM c"
        sample_docs = list(audit_container.query_items(query=sample_query, enable_cross_partition_query=True))
        
        print("\n📋 Sample Documents:")
        for doc in sample_docs:
            doc_id = doc.get('id', 'No ID')
            title = doc.get('title', 'No Title')
            workspace = doc.get('workspace', 'Unknown')
            doc_type = doc.get('docType', 'Unknown')
            last_modified = doc.get('lastModified', 'Unknown')
            print(f"   • {doc_id}")
            print(f"     Title: {title}")
            print(f"     Workspace: {workspace} | Type: {doc_type}")
            print(f"     Last Modified: {last_modified}")
            print()
        
        # Check for governance documents specifically
        governance_query = """
        SELECT *
        FROM c
        WHERE c.workspace = 'governance'
        """
        
        governance_docs = list(audit_container.query_items(query=governance_query, enable_cross_partition_query=True))
        
        print(f"🏛️ Governance Documents Found: {len(governance_docs)}")
        for doc in governance_docs:
            print(f"   • {doc.get('id', 'No ID')}: {doc.get('title', 'No Title')}")
        
        return total_docs, type_results, workspace_results, sample_docs, governance_docs
        
    except Exception as e:
        print(f"❌ Error accessing audit container: {e}")
        print("   This might indicate the container doesn't exist or has a different name")
        return None

def find_audit_documents(database):
    """Search all containers for audit-related documents"""
    print("\n🔍 SEARCHING ALL CONTAINERS FOR AUDIT DOCUMENTS")
    print("=" * 60)
    
    containers = list(database.list_containers())
    audit_docs_found = []
    
    for container_info in containers:
        container_id = container_info['id']
        print(f"\n📂 Searching container: {container_id}")
        
        try:
            container = database.get_container_client(container_id)
            
            # Search for documents with 'audit' in various fields
            audit_queries = [
                "SELECT * FROM c WHERE CONTAINS(LOWER(c.id), 'audit')",
                "SELECT * FROM c WHERE CONTAINS(LOWER(c.title), 'audit')",
                "SELECT * FROM c WHERE c.docType = 'audit'",
                "SELECT * FROM c WHERE c.category = 'audit'"
            ]
            
            container_audit_docs = []
            for query in audit_queries:
                try:
                    results = list(container.query_items(query=query, enable_cross_partition_query=True))
                    for doc in results:
                        if doc not in container_audit_docs:
                            container_audit_docs.append(doc)
                except:
                    continue
            
            if container_audit_docs:
                print(f"   ✅ Found {len(container_audit_docs)} audit-related documents")
                for doc in container_audit_docs:
                    print(f"      • {doc.get('id', 'No ID')}: {doc.get('title', 'No Title')}")
                    audit_docs_found.extend(container_audit_docs)
            else:
                print(f"   ❌ No audit documents found")
                
        except Exception as e:
            print(f"   ❌ Error searching container {container_id}: {e}")
    
    return audit_docs_found

def main():
    """Main analysis function"""
    print("🔍 ANALYZING COSMOS DB AUDIT CONTAINER")
    print("=" * 60)
    
    try:
        # Connect to Cosmos DB
        client, database = connect_to_cosmos()
        
        # Explore all containers first
        containers = explore_containers(database)
        
        # Try to analyze audit container specifically
        audit_result = analyze_audit_container(database)
        
        # If audit container doesn't exist or has no documents, search all containers
        if audit_result is None or audit_result[0] == 0:
            print("\n🔍 Audit container not found or empty, searching all containers...")
            audit_docs = find_audit_documents(database)
            
            if audit_docs:
                print(f"\n✅ FOUND {len(audit_docs)} AUDIT DOCUMENTS ACROSS ALL CONTAINERS")
                print("=" * 60)
                
                # Analyze the found documents
                workspaces = {}
                doc_types = {}
                
                for doc in audit_docs:
                    workspace = doc.get('workspace', 'Unknown')
                    doc_type = doc.get('docType', 'Unknown')
                    
                    workspaces[workspace] = workspaces.get(workspace, 0) + 1
                    doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
                
                print("\n📊 Distribution by Workspace:")
                for workspace, count in workspaces.items():
                    print(f"   • {workspace}: {count} documents")
                
                print("\n📋 Distribution by Document Type:")
                for doc_type, count in doc_types.items():
                    print(f"   • {doc_type}: {count} documents")
                
            else:
                print("\n❌ No audit documents found in any container")
        
        print("\n✅ ANALYSIS COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()