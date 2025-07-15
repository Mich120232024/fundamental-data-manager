#!/usr/bin/env python3
"""
Check CFTC API entry in Cosmos DB with detailed output
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

def check_cftc_api_detailed():
    """Check for CFTC API entry with full document output"""
    
    print("Connecting to Cosmos DB...")
    print(f"Endpoint: {COSMOS_ENDPOINT}")
    
    # Get database and container
    database = client.get_database_client("data-collection-db")
    container = database.get_container_client("api_catalog")
    
    # First, let's see what's in the container
    print("\nListing all entries in api_catalog...")
    all_items = list(container.query_items(
        query="SELECT c.id, c.name, c.type FROM c",
        enable_cross_partition_query=True
    ))
    
    print(f"\nTotal entries: {len(all_items)}")
    for item in all_items:
        print(f"  - {item['id']}: {item.get('name', 'No name')} ({item.get('type', 'No type')})")
    
    # Now get the CFTC entry
    print("\n" + "="*80)
    print("Fetching usa-cftc-complete entry...")
    print("="*80)
    
    try:
        cftc_entry = container.read_item(item="usa-cftc-complete", partition_key="usa-cftc-complete")
        
        # Save full document for inspection
        with open("cftc_cosmos_entry.json", "w") as f:
            json.dump(cftc_entry, f, indent=2)
        print("\n✓ Full document saved to: cftc_cosmos_entry.json")
        
        # Print key information
        print("\nDOCUMENT STRUCTURE:")
        print(f"- ID: {cftc_entry.get('id')}")
        print(f"- Type: {cftc_entry.get('type')}")
        print(f"- Top-level keys: {list(cftc_entry.keys())}")
        
        # Check endpoints structure
        print("\nENDPOINTS STRUCTURE:")
        endpoints = cftc_entry.get('endpoints', [])
        print(f"- Type: {type(endpoints)}")
        print(f"- Count: {len(endpoints)}")
        
        if isinstance(endpoints, list) and endpoints:
            print("\nFirst endpoint sample:")
            print(json.dumps(endpoints[0], indent=2)[:500] + "...")
        
        # Check datasets structure
        print("\nDATASETS STRUCTURE:")
        datasets = cftc_entry.get('datasets', [])
        print(f"- Type: {type(datasets)}")
        print(f"- Count: {len(datasets)}")
        
        if isinstance(datasets, list) and datasets:
            print("\nDataset names:")
            for ds in datasets:
                print(f"  • {ds.get('name', 'Unnamed')}")
        
        # Check fields structure
        print("\nFIELDS STRUCTURE:")
        fields = cftc_entry.get('fields', {})
        print(f"- Type: {type(fields)}")
        
        if isinstance(fields, dict):
            print(f"- Dataset keys: {list(fields.keys())[:5]}..." if len(fields) > 5 else f"- Dataset keys: {list(fields.keys())}")
            
            # Count total fields
            total_fields = 0
            for dataset_name, dataset_fields in fields.items():
                if isinstance(dataset_fields, list):
                    total_fields += len(dataset_fields)
                elif isinstance(dataset_fields, dict):
                    total_fields += len(dataset_fields)
            print(f"- Total fields across all datasets: {total_fields}")
        
        # Check for mock data indicators
        print("\nDATA VERIFICATION:")
        doc_str = json.dumps(cftc_entry).lower()
        mock_indicators = ['mock', 'test', 'example', 'sample', 'dummy', 'fake']
        found_indicators = [ind for ind in mock_indicators if ind in doc_str]
        
        if found_indicators:
            print(f"⚠️  WARNING: Found potential mock data indicators: {found_indicators}")
            print("   Checking context...")
            
            # Check specific fields for mock data
            for endpoint in endpoints[:3] if isinstance(endpoints, list) else []:
                if 'example' in str(endpoint).lower():
                    print(f"   - Found 'example' in endpoint: {endpoint.get('name', 'Unknown')}")
        else:
            print("✓ No obvious mock data indicators found")
        
        # Check timestamps
        print("\nTIMESTAMPS:")
        for key in ['created_date', 'last_updated', 'uploaded_date', 'modified_date']:
            if key in cftc_entry:
                print(f"- {key}: {cftc_entry[key]}")
        
        # Summary
        print("\n" + "="*80)
        print("VERIFICATION SUMMARY:")
        print("="*80)
        
        checks = {
            "Document exists": True,
            "Has 12 endpoints": len(endpoints) == 12,
            "Has 12 datasets": len(datasets) == 12,
            "Has 1,421+ fields": total_fields >= 1421 if isinstance(fields, dict) else False,
            "No mock data indicators": len(found_indicators) == 0,
            "Has timestamps": any(key in cftc_entry for key in ['created_date', 'last_updated', 'uploaded_date'])
        }
        
        for check, passed in checks.items():
            print(f"{'✓' if passed else '❌'} {check}")
        
        if all(checks.values()):
            print("\n✅ CFTC API entry appears to be production-ready!")
        else:
            print("\n⚠️  CFTC API entry has some issues that need attention")
            
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    try:
        check_cftc_api_detailed()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()