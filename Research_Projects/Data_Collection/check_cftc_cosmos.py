#!/usr/bin/env python3
"""
Check CFTC API entry in Cosmos DB data-collection-db.api_catalog
Verify all requirements for production readiness
"""

import os
import json
from datetime import datetime
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cosmos DB configuration
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")

# Initialize Cosmos client
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)

def check_cftc_api():
    """Check for CFTC API entry and verify all requirements"""
    
    print("Connecting to Cosmos DB...")
    print(f"Endpoint: {COSMOS_ENDPOINT}")
    
    # Get database and container
    database = client.get_database_client("data-collection-db")
    container = database.get_container_client("api_catalog")
    
    # Query for CFTC entries (check multiple possible IDs)
    possible_ids = ["cftc-api", "cftc-commitments", "cftc-socrata", "cftc", "CFTC"]
    
    print("\nSearching for CFTC API entries...")
    cftc_entries = []
    
    # Try direct reads first
    for api_id in possible_ids:
        try:
            item = container.read_item(item=api_id, partition_key=api_id)
            cftc_entries.append(item)
            print(f"✓ Found entry with ID: {api_id}")
        except:
            print(f"✗ No entry found with ID: {api_id}")
    
    # Also query for any items containing CFTC
    query = "SELECT * FROM c WHERE CONTAINS(LOWER(c.name), 'cftc') OR CONTAINS(LOWER(c.id), 'cftc')"
    print("\nQuerying for any CFTC-related entries...")
    
    try:
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        for item in items:
            if item not in cftc_entries:
                cftc_entries.append(item)
                print(f"✓ Found entry via query: {item.get('id', 'Unknown ID')}")
    except Exception as e:
        print(f"Query error: {e}")
    
    if not cftc_entries:
        print("\n❌ NO CFTC API ENTRY FOUND IN COSMOS DB")
        print("\nChecking all entries in api_catalog...")
        all_items = list(container.query_items(
            query="SELECT c.id, c.name, c.created_date FROM c",
            enable_cross_partition_query=True
        ))
        print(f"\nTotal entries in api_catalog: {len(all_items)}")
        for item in all_items:
            print(f"  - {item['id']}: {item.get('name', 'No name')} (created: {item.get('created_date', 'Unknown')})")
        return
    
    # Analyze each CFTC entry found
    for idx, entry in enumerate(cftc_entries):
        print(f"\n{'='*60}")
        print(f"CFTC Entry #{idx + 1} - ID: {entry.get('id', 'Unknown')}")
        print(f"{'='*60}")
        
        # 1. Check document structure and schema
        print("\n1. DOCUMENT STRUCTURE:")
        print(f"   - ID: {entry.get('id', 'MISSING')}")
        print(f"   - Name: {entry.get('name', 'MISSING')}")
        print(f"   - Type: {entry.get('type', 'MISSING')}")
        print(f"   - Status: {entry.get('status', 'MISSING')}")
        print(f"   - Created Date: {entry.get('created_date', 'MISSING')}")
        print(f"   - Last Updated: {entry.get('last_updated', 'MISSING')}")
        
        # 2. Check for mock data
        print("\n2. DATA VERIFICATION (checking for mock data):")
        
        # Check endpoints
        endpoints = entry.get('endpoints', {})
        if endpoints:
            print(f"   - Endpoints defined: {len(endpoints)}")
            
            # Handle both dict and list structures
            if isinstance(endpoints, dict):
                for ep_name, ep_data in endpoints.items():
                    print(f"     • {ep_name}: {ep_data.get('url', 'No URL')}")
                    
                    # Check example responses
                    if 'example_response' in ep_data:
                        example = ep_data['example_response']
                        if isinstance(example, str):
                            if 'mock' in example.lower() or 'example' in example.lower() or 'test' in example.lower():
                                print(f"       ⚠️  POSSIBLE MOCK DATA in example_response")
                        elif isinstance(example, dict):
                            example_str = json.dumps(example).lower()
                            if 'mock' in example_str or 'test' in example_str:
                                print(f"       ⚠️  POSSIBLE MOCK DATA in example_response")
            elif isinstance(endpoints, list):
                for idx, ep_data in enumerate(endpoints):
                    ep_name = ep_data.get('name', f'Endpoint {idx+1}')
                    print(f"     • {ep_name}: {ep_data.get('url', 'No URL')}")
                    
                    # Check example responses
                    if 'example_response' in ep_data:
                        example = ep_data['example_response']
                        if isinstance(example, str):
                            if 'mock' in example.lower() or 'example' in example.lower() or 'test' in example.lower():
                                print(f"       ⚠️  POSSIBLE MOCK DATA in example_response")
                        elif isinstance(example, dict):
                            example_str = json.dumps(example).lower()
                            if 'mock' in example_str or 'test' in example_str:
                                print(f"       ⚠️  POSSIBLE MOCK DATA in example_response")
        
        # 3. Check dataset count
        print("\n3. DATASET COUNT:")
        datasets = entry.get('datasets', [])
        if datasets:
            print(f"   - Total datasets documented: {len(datasets)}")
            if len(datasets) < 12:
                print(f"   ❌ ONLY {len(datasets)} DATASETS (should be 12)")
            else:
                print(f"   ✓ All 12 datasets documented")
            
            # List datasets
            for ds in datasets[:5]:  # Show first 5
                print(f"     • {ds.get('name', 'Unnamed')}: {ds.get('description', 'No description')[:50]}...")
            if len(datasets) > 5:
                print(f"     ... and {len(datasets) - 5} more datasets")
        else:
            print("   ❌ NO DATASETS DOCUMENTED")
        
        # 4. Check Python functions
        print("\n4. PYTHON FUNCTIONS:")
        functions = entry.get('python_functions', {})
        if functions:
            print(f"   - Functions defined: {len(functions)}")
            for func_name, func_data in functions.items():
                print(f"     • {func_name}: {func_data.get('description', 'No description')[:50]}...")
                if 'tested' in func_data:
                    print(f"       Tested: {func_data['tested']}")
        else:
            print("   ❌ NO PYTHON FUNCTIONS DOCUMENTED")
        
        # 5. Check field count
        print("\n5. FIELD CATALOG:")
        fields = entry.get('fields', {})
        total_fields = 0
        if fields:
            for dataset_name, dataset_fields in fields.items():
                if isinstance(dataset_fields, list):
                    total_fields += len(dataset_fields)
                elif isinstance(dataset_fields, dict):
                    total_fields += len(dataset_fields)
            
            print(f"   - Total fields cataloged: {total_fields}")
            if total_fields < 1421:
                print(f"   ❌ ONLY {total_fields} FIELDS (should be 1,421)")
            else:
                print(f"   ✓ All 1,421 fields cataloged")
        else:
            print("   ❌ NO FIELDS CATALOGED")
        
        # 6. Check timestamps
        print("\n6. UPLOAD VERIFICATION:")
        created = entry.get('created_date', 'Unknown')
        updated = entry.get('last_updated', 'Unknown')
        print(f"   - Created: {created}")
        print(f"   - Last Updated: {updated}")
        
        # 7. Check for production readiness indicators
        print("\n7. PRODUCTION READINESS:")
        auth = entry.get('authentication', {})
        if auth:
            print(f"   ✓ Authentication documented: {auth.get('type', 'Unknown type')}")
        else:
            print("   ❌ No authentication details")
            
        rate_limits = entry.get('rate_limits', {})
        if rate_limits:
            print(f"   ✓ Rate limits documented")
        else:
            print("   ❌ No rate limits documented")
            
        # Check for testing/validation
        testing = entry.get('testing', {})
        validation = entry.get('validation', {})
        if testing or validation:
            print(f"   ✓ Testing/validation information present")
        else:
            print("   ❌ No testing/validation information")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY:")
    print(f"{'='*60}")
    print(f"Total CFTC entries found: {len(cftc_entries)}")
    
    if cftc_entries:
        # Check if any entry meets all criteria
        for entry in cftc_entries:
            datasets = entry.get('datasets', [])
            fields = entry.get('fields', {})
            total_fields = sum(len(f) if isinstance(f, list) else len(f) if isinstance(f, dict) else 0 
                             for f in fields.values()) if fields else 0
            
            if len(datasets) >= 12 and total_fields >= 1421:
                print(f"\n✓ Entry '{entry['id']}' appears to be production-ready!")
            else:
                print(f"\n❌ Entry '{entry['id']}' is incomplete:")
                if len(datasets) < 12:
                    print(f"   - Missing datasets: has {len(datasets)}, needs 12")
                if total_fields < 1421:
                    print(f"   - Missing fields: has {total_fields}, needs 1,421")

if __name__ == "__main__":
    try:
        check_cftc_api()
    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nPlease check:")
        print("1. Cosmos DB credentials are correct")
        print("2. Network connectivity to Azure")
        print("3. Database and container names are correct")