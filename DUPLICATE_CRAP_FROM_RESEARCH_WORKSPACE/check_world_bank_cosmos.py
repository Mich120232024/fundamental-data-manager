#!/usr/bin/env python3
"""Check World Bank API entry in Cosmos DB for updates"""

import os
import json
from datetime import datetime
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cosmos DB configuration
COSMOS_ENDPOINT = os.getenv('COSMOS_ENDPOINT')
COSMOS_KEY = os.getenv('COSMOS_KEY')
DATABASE_NAME = 'data-collection-db'
CONTAINER_NAME = 'api_catalog'

def check_world_bank_entry():
    """Check the World Bank API entry and analyze changes"""
    
    # Initialize Cosmos client
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    
    # Query for World Bank entry
    query = "SELECT * FROM c WHERE c.id = 'world-bank-indicators'"
    
    try:
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        if not items:
            print("❌ World Bank API entry not found!")
            return
        
        entry = items[0]
        
        print("=== WORLD BANK API ENTRY ANALYSIS ===\n")
        
        # Basic information
        print(f"ID: {entry.get('id')}")
        print(f"Name: {entry.get('name')}")
        print(f"Provider: {entry.get('provider')}")
        print(f"Category: {entry.get('category')}")
        print(f"Status: {entry.get('status')}")
        print(f"Last Updated: {entry.get('lastUpdated')}")
        print(f"Version: {entry.get('version')}")
        
        # Check timestamps
        if 'lastUpdated' in entry:
            last_updated = datetime.fromisoformat(entry['lastUpdated'].replace('Z', '+00:00'))
            current_time = datetime.utcnow()
            time_diff = current_time - last_updated
            print(f"Time since last update: {time_diff}")
        
        # Check for mock data issues
        print("\n=== MOCK DATA ISSUE CHECKS ===")
        
        # Check sourceNote fields for "foo" in endpoints
        foo_count = 0
        clean_count = 0
        if 'endpoints' in entry:
            for endpoint in entry['endpoints']:
                if 'sampleResponse' in endpoint and isinstance(endpoint['sampleResponse'], list) and len(endpoint['sampleResponse']) > 1:
                    # Check the data array (second element)
                    data_array = endpoint['sampleResponse'][1]
                    if isinstance(data_array, list):
                        for item in data_array:
                            if isinstance(item, dict) and 'sourceNote' in item:
                                if item['sourceNote'] == 'foo':
                                    foo_count += 1
                                else:
                                    clean_count += 1
        
        print(f"✓ 'foo' in sourceNote fields: {foo_count} occurrences")
        print(f"✓ Clean sourceNote fields: {clean_count} occurrences")
        
        # Check sample responses
        sample_count = 0
        populated_samples = 0
        if 'endpoints' in entry:
            for endpoint in entry['endpoints']:
                if 'sampleResponse' in endpoint:
                    sample_count += 1
                    if endpoint['sampleResponse'] and len(str(endpoint['sampleResponse'])) > 10:
                        populated_samples += 1
        
        print(f"✓ Sample responses: {sample_count} total, {populated_samples} populated")
        
        # Check country count from metadata
        country_count = entry.get('metadata', {}).get('totalCountries', 0)
        if country_count == 0 and 'discoveryMetadata' in entry:
            country_count = entry['discoveryMetadata'].get('totalCountries', 0)
        
        print(f"✓ Country count: {country_count} (expected: 296)")
        
        # Check specific improvements
        print("\n=== DETAILED ANALYSIS ===")
        
        # Check endpoints and their sample responses
        if 'endpoints' in entry:
            print("\nEndpoint Analysis:")
            print(f"Total endpoints: {len(entry['endpoints'])}")
            
            for i, endpoint in enumerate(entry['endpoints'][:3]):  # Show first 3
                print(f"\n  Endpoint {i+1}: {endpoint.get('endpoint', 'N/A')}")
                print(f"    URL: {endpoint.get('url', 'N/A')}")
                print(f"    Description: {endpoint.get('description', 'N/A')[:80]}...")
                
                if 'sampleResponse' in endpoint:
                    sample = endpoint['sampleResponse']
                    if isinstance(sample, list) and len(sample) >= 2:
                        metadata = sample[0]
                        data = sample[1]
                        print(f"    Sample Response Structure: [metadata, data]")
                        print(f"    Metadata: {json.dumps(metadata, indent=6)[:200]}...")
                        if isinstance(data, list) and len(data) > 0:
                            print(f"    Data points: {len(data)}")
                            # Check for sourceNote in data
                            has_source_note = any(isinstance(item, dict) and 'sourceNote' in item for item in data)
                            if has_source_note:
                                print(f"    Contains sourceNote fields: Yes")
                                # Check first item with sourceNote
                                for item in data:
                                    if isinstance(item, dict) and 'sourceNote' in item:
                                        print(f"    Sample sourceNote: '{item['sourceNote'][:100]}...'")
                                        break
                    else:
                        print(f"    Sample Response: {str(sample)[:100]}...")
        
        # Check key indicators
        if 'keyIndicators' in entry:
            print(f"\nKey Indicators Analysis:")
            categories = list(entry['keyIndicators'].keys())
            print(f"  Categories: {', '.join(categories)}")
            total_indicators = sum(len(entry['keyIndicators'][cat]) for cat in categories)
            print(f"  Total key indicators: {total_indicators}")
        
        # Check authentication
        if 'authentication' in entry:
            print(f"\nAuthentication:")
            print(f"  Type: {entry['authentication'].get('type')}")
            print(f"  Required: {entry['authentication'].get('required')}")
        
        # Check rate limits
        if 'rateLimits' in entry:
            print(f"\nRate Limits:")
            rate_limits = entry['rateLimits']
            if isinstance(rate_limits, list):
                for limit in rate_limits:
                    if isinstance(limit, dict):
                        print(f"  {limit.get('period')}: {limit.get('limit')} requests")
                    else:
                        print(f"  {limit}")
            else:
                print(f"  {rate_limits}")
        
        # Summary of fixes
        print("\n=== ISSUE RESOLUTION SUMMARY ===")
        
        issues_fixed = []
        issues_remaining = []
        
        if foo_count == 0:
            issues_fixed.append("✅ 'foo' removed from sourceNote fields")
        else:
            issues_remaining.append(f"❌ 'foo' still in {foo_count} sourceNote fields")
        
        if sample_count > 0 and populated_samples == sample_count:
            issues_fixed.append("✅ All sample responses populated with data")
        elif sample_count > 0 and populated_samples > 0:
            issues_fixed.append(f"✅ {populated_samples}/{sample_count} sample responses have data")
            if populated_samples < sample_count:
                issues_remaining.append(f"⚠️  {sample_count - populated_samples} sample responses incomplete")
        else:
            issues_remaining.append("❌ Sample responses not populated")
        
        if country_count == 296:
            issues_fixed.append("✅ Country count corrected to 296")
        else:
            issues_remaining.append(f"❌ Country count is {country_count}, expected 296")
        
        print("\nFixed Issues:")
        for issue in issues_fixed:
            print(f"  {issue}")
        
        if issues_remaining:
            print("\nRemaining Issues:")
            for issue in issues_remaining:
                print(f"  {issue}")
        
        # Additional metadata
        print("\n=== ADDITIONAL METADATA ===")
        if 'metadata' in entry:
            metadata = entry['metadata']
            print(f"Created: {metadata.get('created')}")
            print(f"Created By: {metadata.get('createdBy')}")
            print(f"Updated By: {metadata.get('updatedBy')}")
            print(f"Source: {metadata.get('source')}")
            print(f"Tags: {', '.join(metadata.get('tags', []))}")
        
        # Show raw structure for debugging
        print("\n=== RAW DOCUMENT STRUCTURE ===")
        print(f"Document keys: {list(entry.keys())}")
        
        # Save the full document for reference
        with open('world_bank_api_entry_latest.json', 'w') as f:
            json.dump(entry, f, indent=2)
        print("\n✓ Full document saved to: world_bank_api_entry_latest.json")
        
    except Exception as e:
        print(f"❌ Error querying Cosmos DB: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_world_bank_entry()