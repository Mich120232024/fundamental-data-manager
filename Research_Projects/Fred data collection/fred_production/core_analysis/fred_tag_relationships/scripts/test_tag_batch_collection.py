#!/usr/bin/env python3
"""
Test collecting tag relationships in batches
Try 1k and 5k limits to see API response
"""

import json
import requests
import time
from datetime import datetime

API_KEY = "21acd97c4988e53af02e98587d5424d0"
BASE_URL = "https://api.stlouisfed.org/fred"

def make_api_call(endpoint, params=None):
    """Make API call with rate limiting"""
    if params is None:
        params = {}
    params['api_key'] = API_KEY
    params['file_type'] = 'json'
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Rate limited, waiting 30s...")
            time.sleep(30)
            return make_api_call(endpoint, params)
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def test_batch_limits():
    """Test different batch sizes for tag relationships"""
    
    # Test tags that we know have many relationships
    test_tags = ['gdp', 'usa', 'annual']
    batch_sizes = [100, 1000, 5000, 10000]  # Test increasing limits
    
    print(f"\n{'='*80}")
    print(f"TESTING TAG RELATIONSHIP BATCH LIMITS")
    print(f"{'='*80}")
    
    results = {}
    
    for tag in test_tags:
        print(f"\n\nTesting tag: '{tag}'")
        print("-" * 40)
        
        results[tag] = {}
        
        for limit in batch_sizes:
            print(f"\n  Testing limit={limit:,}...")
            
            start_time = time.time()
            
            # Make API call with specific limit
            params = {
                'tag_names': tag,
                'limit': limit
            }
            
            response = make_api_call('/related_tags', params)
            
            if response and 'tags' in response:
                actual_returned = len(response['tags'])
                total_available = response.get('count', 0)
                api_limit = response.get('limit', 0)
                
                elapsed = time.time() - start_time
                
                results[tag][limit] = {
                    'requested_limit': limit,
                    'api_limit': api_limit,
                    'total_available': total_available,
                    'actual_returned': actual_returned,
                    'elapsed_seconds': elapsed,
                    'fully_returned': actual_returned == total_available
                }
                
                print(f"    ✓ Requested: {limit:,}")
                print(f"    ✓ API limit: {api_limit:,}")
                print(f"    ✓ Available: {total_available:,}")
                print(f"    ✓ Returned: {actual_returned:,}")
                print(f"    ✓ Time: {elapsed:.2f}s")
                print(f"    ✓ Complete: {'Yes' if actual_returned == total_available else 'No'}")
                
                # If we got everything, no need to test higher limits
                if actual_returned == total_available:
                    print(f"    → Got all available tags, skipping higher limits")
                    break
            else:
                print(f"    ✗ Failed to get response")
                results[tag][limit] = {'error': 'No response'}
            
            # Rate limiting between calls
            time.sleep(1)
    
    # Analyze results
    print(f"\n\n{'='*80}")
    print(f"BATCH LIMIT ANALYSIS")
    print(f"{'='*80}")
    
    # Find the effective API limit
    api_limits_seen = set()
    for tag, tag_results in results.items():
        for limit, data in tag_results.items():
            if 'api_limit' in data:
                api_limits_seen.add(data['api_limit'])
    
    print(f"\nAPI Limits Observed: {sorted(api_limits_seen)}")
    
    # Check if we can get all data in one call
    print(f"\nCan we get all relationships in one call?")
    for tag, tag_results in results.items():
        max_returned = 0
        total_available = 0
        
        for limit, data in tag_results.items():
            if 'actual_returned' in data:
                max_returned = max(max_returned, data['actual_returned'])
                total_available = data.get('total_available', 0)
        
        complete = max_returned == total_available
        print(f"  {tag}: {'Yes' if complete else 'No'} ({max_returned:,}/{total_available:,})")
    
    # Performance analysis
    print(f"\nPerformance by batch size:")
    for limit in batch_sizes:
        print(f"\n  Limit {limit:,}:")
        for tag, tag_results in results.items():
            if limit in tag_results and 'elapsed_seconds' in tag_results[limit]:
                data = tag_results[limit]
                print(f"    {tag}: {data['elapsed_seconds']:.2f}s for {data['actual_returned']:,} tags")
    
    # Save detailed results
    output = {
        'test_metadata': {
            'timestamp': datetime.now().isoformat(),
            'test_tags': test_tags,
            'batch_sizes_tested': batch_sizes
        },
        'results': results,
        'analysis': {
            'api_limits_observed': sorted(list(api_limits_seen)),
            'recommendation': 'Use limit=1000 for optimal performance'
        }
    }
    
    with open('fred_complete_data/tag_batch_test_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Results saved to: tag_batch_test_results.json")

if __name__ == "__main__":
    test_batch_limits()