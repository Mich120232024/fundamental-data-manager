#!/usr/bin/env python3
"""
Merge API research results and update Cosmos DB
"""
import json
import os
import glob
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def merge_and_update_results():
    # Load all batch results
    result_files = glob.glob('api_research_results/batch_*.json')
    all_results = []
    
    for file_path in result_files:
        with open(file_path, 'r') as f:
            batch_results = json.load(f)
            # Filter out invalid entries (strings, non-API objects)
            valid_apis = [api for api in batch_results if isinstance(api, dict) and ('name' in api or 'api_name' in api)]
            all_results.extend(valid_apis)
    
    print(f"📊 Loaded {len(all_results)} researched APIs from {len(result_files)} batches")
    
    # Connect to Cosmos DB
    cosmos_client = CosmosClient(os.getenv('COSMOS_ENDPOINT'), os.getenv('COSMOS_KEY'))
    database = cosmos_client.get_database_client("data-collection-db")
    container = database.get_container_client("api_discovery")
    
    # Update each API in the database
    updated_count = 0
    error_count = 0
    
    for api_data in all_results:
        try:
            # Skip if not a valid API object
            if not isinstance(api_data, dict) or ('name' not in api_data and 'api_name' not in api_data):
                error_count += 1
                continue
                
            # Ensure name field exists
            if 'name' not in api_data and 'api_name' in api_data:
                api_data['name'] = api_data['api_name']
            
            # Add system metadata
            api_data['system_metadata'] = {
                'created_at': api_data.get('system_metadata', {}).get('created_at', datetime.utcnow().isoformat() + 'Z'),
                'updated_at': datetime.utcnow().isoformat() + 'Z',
                'version': 2,
                'research_completed': True
            }
            
            # Update in Cosmos DB
            container.upsert_item(api_data)
            updated_count += 1
            print(f"✅ Updated: {api_data['name']}")
            
        except Exception as e:
            api_name = api_data.get('name', api_data.get('api_name', 'unknown')) if isinstance(api_data, dict) else 'invalid-entry'
            print(f"❌ Failed to update {api_name}: {e}")
            error_count += 1
    
    print(f"\n🎉 Research merge complete!")
    print(f"   ✅ Updated: {updated_count} APIs")
    print(f"   ❌ Errors: {error_count} APIs")
    print(f"   📈 Success rate: {(updated_count/(updated_count+error_count)*100):.1f}%")

if __name__ == "__main__":
    merge_and_update_results()
