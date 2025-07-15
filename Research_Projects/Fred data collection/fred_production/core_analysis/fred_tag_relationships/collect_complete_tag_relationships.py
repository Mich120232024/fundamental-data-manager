#!/usr/bin/env python3
"""
Collect complete tag relationships using pagination
Since API limit is 1000, we need to paginate for tags with more relationships
"""

import json
import requests
import time
import os
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
            print("    Rate limited, waiting 30s...")
            time.sleep(30)
            return make_api_call(endpoint, params)
        else:
            print(f"    Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"    Exception: {e}")
        return None

def collect_complete_tag_relationships(tag_name):
    """Collect all relationships for a single tag using pagination"""
    
    all_related_tags = []
    offset = 0
    limit = 1000  # Maximum allowed
    total_count = None
    api_calls = 0
    
    print(f"\nCollecting relationships for '{tag_name}':")
    
    while True:
        params = {
            'tag_names': tag_name,
            'limit': limit,
            'offset': offset
        }
        
        response = make_api_call('/related_tags', params)
        api_calls += 1
        
        if response and 'tags' in response:
            batch = response['tags']
            all_related_tags.extend(batch)
            
            if total_count is None:
                total_count = response.get('count', 0)
            
            print(f"  Batch {api_calls}: Got {len(batch)} tags (Total: {len(all_related_tags)}/{total_count})")
            
            # Check if we got everything
            if len(batch) < limit or len(all_related_tags) >= total_count:
                break
            
            offset += limit
            time.sleep(0.5)  # Rate limiting
        else:
            print(f"  Failed to get batch at offset {offset}")
            break
    
    return {
        'tag': tag_name,
        'total_count': total_count,
        'collected_count': len(all_related_tags),
        'api_calls': api_calls,
        'complete': len(all_related_tags) == total_count,
        'related_tags': all_related_tags
    }

def main():
    """Collect complete relationships for key tags"""
    
    # Test with tags that have many relationships
    test_tags = [
        'gdp',      # 4,277 relationships
        'usa',      # 5,918 relationships
        'annual',   # 5,134 relationships
        'inflation' # 758 relationships (fits in one call)
    ]
    
    print(f"\n{'='*80}")
    print(f"COLLECTING COMPLETE TAG RELATIONSHIPS WITH PAGINATION")
    print(f"{'='*80}")
    
    output_dir = 'fred_complete_data/tag_relationships'
    os.makedirs(output_dir, exist_ok=True)
    
    all_results = {}
    total_api_calls = 0
    
    for tag in test_tags:
        result = collect_complete_tag_relationships(tag)
        all_results[tag] = result
        total_api_calls += result['api_calls']
        
        # Save individual tag results
        tag_file = f"{output_dir}/complete_{tag}_relationships.json"
        with open(tag_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"  ✓ Saved to: {tag_file}")
    
    # Summary
    print(f"\n\n{'='*80}")
    print(f"COLLECTION SUMMARY")
    print(f"{'='*80}")
    
    for tag, result in all_results.items():
        print(f"\n{tag}:")
        print(f"  Total relationships: {result['total_count']:,}")
        print(f"  Collected: {result['collected_count']:,}")
        print(f"  API calls: {result['api_calls']}")
        print(f"  Complete: {'✓' if result['complete'] else '✗'}")
    
    print(f"\nTotal API calls: {total_api_calls}")
    
    # Analyze the complete graph
    print(f"\n\n{'='*80}")
    print(f"COMPLETE GRAPH ANALYSIS")
    print(f"{'='*80}")
    
    # Find common relationships across all tags
    tag_frequency = {}
    
    for tag, result in all_results.items():
        print(f"\nTop 10 tags related to '{tag}':")
        for i, related in enumerate(result['related_tags'][:10]):
            print(f"  {i+1}. {related['name']} ({related.get('series_count', 0):,} series)")
            
            # Track frequency
            related_name = related['name']
            if related_name not in tag_frequency:
                tag_frequency[related_name] = 0
            tag_frequency[related_name] += 1
    
    # Most common relationships
    print(f"\n\nTags that appear in ALL {len(test_tags)} relationships:")
    common_to_all = [tag for tag, freq in tag_frequency.items() if freq == len(test_tags)]
    for tag in sorted(common_to_all)[:20]:
        print(f"  - {tag}")
    
    # Save summary
    summary = {
        'collection_metadata': {
            'timestamp': datetime.now().isoformat(),
            'tags_analyzed': test_tags,
            'total_api_calls': total_api_calls
        },
        'results': {tag: {
            'total_count': result['total_count'],
            'collected_count': result['collected_count'],
            'api_calls': result['api_calls'],
            'complete': result['complete']
        } for tag, result in all_results.items()},
        'common_relationships': {
            'appearing_in_all': common_to_all,
            'frequency_counts': dict(sorted(tag_frequency.items(), 
                                          key=lambda x: x[1], 
                                          reverse=True)[:50])
        }
    }
    
    with open(f'{output_dir}/complete_collection_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Complete collection finished!")
    print(f"✅ Summary saved to: complete_collection_summary.json")

if __name__ == "__main__":
    main()