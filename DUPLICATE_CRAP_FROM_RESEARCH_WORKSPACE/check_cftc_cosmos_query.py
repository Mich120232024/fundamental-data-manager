#!/usr/bin/env python3
"""
Query CFTC API entry in Cosmos DB using cross-partition query
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
    """Check for CFTC API entry using query"""
    
    print("Connecting to Cosmos DB...")
    print(f"Endpoint: {COSMOS_ENDPOINT}")
    
    # Get database and container
    database = client.get_database_client("data-collection-db")
    container = database.get_container_client("api_catalog")
    
    # Query for the CFTC entry
    print("\nQuerying for usa-cftc-complete...")
    query = "SELECT * FROM c WHERE c.id = 'usa-cftc-complete'"
    
    items = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    if not items:
        print("❌ No CFTC entry found!")
        return
    
    print(f"✓ Found {len(items)} CFTC entry/entries")
    
    for cftc_entry in items:
        # Save full document
        with open("cftc_cosmos_entry.json", "w") as f:
            json.dump(cftc_entry, f, indent=2)
        print("\n✓ Full document saved to: cftc_cosmos_entry.json")
        
        # Analyze the entry
        print("\n" + "="*80)
        print("CFTC API CATALOG VERIFICATION")
        print("="*80)
        
        # 1. Basic info
        print("\n1. BASIC INFORMATION:")
        print(f"   - ID: {cftc_entry.get('id')}")
        print(f"   - Type: {cftc_entry.get('type')}")
        print(f"   - Partition Key: {cftc_entry.get('partitionKey', 'Not specified')}")
        
        # 2. Check endpoints
        print("\n2. ENDPOINTS:")
        endpoints = cftc_entry.get('endpoints', [])
        if isinstance(endpoints, list):
            print(f"   - Total endpoints: {len(endpoints)}")
            if len(endpoints) == 12:
                print("   ✓ All 12 endpoints documented")
            else:
                print(f"   ❌ Only {len(endpoints)} endpoints (expected 12)")
            
            # List endpoint names
            for idx, ep in enumerate(endpoints[:5]):
                name = ep.get('name', ep.get('dataset', f'Endpoint {idx+1}'))
                print(f"     • {name}")
            if len(endpoints) > 5:
                print(f"     ... and {len(endpoints) - 5} more")
        
        # 3. Check datasets
        print("\n3. DATASETS:")
        datasets = cftc_entry.get('datasets', [])
        if isinstance(datasets, list):
            print(f"   - Total datasets: {len(datasets)}")
            if len(datasets) == 12:
                print("   ✓ All 12 datasets documented")
            else:
                print(f"   ❌ Only {len(datasets)} datasets (expected 12)")
            
            # List dataset names
            for idx, ds in enumerate(datasets[:5]):
                name = ds.get('name', ds.get('dataset', f'Dataset {idx+1}'))
                print(f"     • {name}")
            if len(datasets) > 5:
                print(f"     ... and {len(datasets) - 5} more")
        
        # 4. Check fields
        print("\n4. FIELDS CATALOG:")
        fields = cftc_entry.get('fields', {})
        if isinstance(fields, dict):
            total_fields = 0
            for dataset_name, dataset_fields in fields.items():
                if isinstance(dataset_fields, list):
                    total_fields += len(dataset_fields)
                elif isinstance(dataset_fields, dict):
                    total_fields += len(dataset_fields)
            
            print(f"   - Total fields cataloged: {total_fields}")
            if total_fields >= 1421:
                print("   ✓ All 1,421 fields cataloged")
            else:
                print(f"   ❌ Only {total_fields} fields (expected 1,421)")
            
            # Show field count by dataset
            print("   - Fields by dataset:")
            for dataset_name, dataset_fields in list(fields.items())[:5]:
                field_count = len(dataset_fields) if isinstance(dataset_fields, (list, dict)) else 0
                print(f"     • {dataset_name}: {field_count} fields")
            if len(fields) > 5:
                print(f"     ... and {len(fields) - 5} more datasets")
        
        # 5. Check for mock data
        print("\n5. DATA VERIFICATION:")
        doc_str = json.dumps(cftc_entry).lower()
        
        # Check for mock indicators
        mock_found = False
        if 'mock' in doc_str or 'test data' in doc_str or 'example data' in doc_str:
            print("   ⚠️  WARNING: Found potential mock data indicators")
            mock_found = True
        
        # Check sample data
        sample_count = 0
        real_data_indicators = ['contract_market_code', 'open_interest', 'noncomm_positions', 'cftc_contract']
        
        for endpoint in endpoints if isinstance(endpoints, list) else []:
            if 'sample_data' in endpoint or 'example_response' in endpoint:
                sample_count += 1
                sample = endpoint.get('sample_data', endpoint.get('example_response', {}))
                sample_str = str(sample).lower()
                
                # Check for real CFTC data indicators
                has_real_data = any(indicator in sample_str for indicator in real_data_indicators)
                if has_real_data:
                    print(f"   ✓ Endpoint '{endpoint.get('name', 'Unknown')}' has real CFTC data")
                else:
                    print(f"   ⚠️  Endpoint '{endpoint.get('name', 'Unknown')}' may have mock data")
        
        if not mock_found and sample_count > 0:
            print(f"   ✓ {sample_count} endpoints have sample data")
        
        # 6. Check Python functions
        print("\n6. PYTHON FUNCTIONS:")
        functions = cftc_entry.get('python_functions', {})
        if functions:
            print(f"   - Total functions: {len(functions)}")
            for func_name in list(functions.keys())[:5]:
                print(f"     • {func_name}")
            if len(functions) > 5:
                print(f"     ... and {len(functions) - 5} more functions")
        else:
            print("   ❌ No Python functions documented")
        
        # 7. Check timestamps
        print("\n7. TIMESTAMPS:")
        timestamp_keys = ['created_date', 'last_updated', 'uploaded_date', 'modified_date', '_ts']
        found_timestamps = {}
        for key in timestamp_keys:
            if key in cftc_entry:
                value = cftc_entry[key]
                if key == '_ts':
                    # Cosmos DB timestamp is Unix timestamp in seconds
                    try:
                        value = datetime.fromtimestamp(value).isoformat()
                    except:
                        pass
                found_timestamps[key] = value
        
        if found_timestamps:
            for key, value in found_timestamps.items():
                print(f"   - {key}: {value}")
        else:
            print("   ❌ No timestamps found")
        
        # 8. Summary
        print("\n" + "="*80)
        print("VERIFICATION SUMMARY:")
        print("="*80)
        
        checks = {
            "Document exists": True,
            "Has 12 endpoints": len(endpoints) == 12 if isinstance(endpoints, list) else False,
            "Has 12 datasets": len(datasets) == 12 if isinstance(datasets, list) else False,
            "Has 1,421+ fields": total_fields >= 1421 if isinstance(fields, dict) else False,
            "No mock data found": not mock_found,
            "Has timestamps": len(found_timestamps) > 0,
            "Has Python functions": len(functions) > 0
        }
        
        passed_checks = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        
        for check, passed in checks.items():
            print(f"{'✓' if passed else '❌'} {check}")
        
        print(f"\nScore: {passed_checks}/{total_checks}")
        
        if all(checks.values()):
            print("\n✅ CFTC API entry is PRODUCTION-READY!")
        else:
            print("\n⚠️  CFTC API entry needs attention")

if __name__ == "__main__":
    try:
        check_cftc_api()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()