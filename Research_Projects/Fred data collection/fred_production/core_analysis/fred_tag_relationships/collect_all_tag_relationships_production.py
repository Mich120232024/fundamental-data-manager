#!/usr/bin/env python3
"""
PRODUCTION SCRIPT: Collect ALL FRED Tag Relationships
No sampling - complete collection of all 5,941 tags
Estimated: 30,000 API calls, 5-6 hours
"""

import json
import requests
import time
import os
from datetime import datetime
from pathlib import Path

API_KEY = "21acd97c4988e53af02e98587d5424d0"
BASE_URL = "https://api.stlouisfed.org/fred"

# Adaptive rate limiting
MIN_SLEEP = 0.5
MAX_SLEEP = 1.0
current_sleep = MIN_SLEEP

def make_api_call(endpoint, params=None):
    """Make API call with adaptive rate limiting"""
    global current_sleep
    
    if params is None:
        params = {}
    params['api_key'] = API_KEY
    params['file_type'] = 'json'
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.get(url, params=params, timeout=30)
        time.sleep(current_sleep)
        
        if response.status_code == 200:
            # Success - speed up slightly
            current_sleep = max(MIN_SLEEP, current_sleep * 0.95)
            return response.json()
        elif response.status_code == 429:
            # Rate limited - slow down
            print(f"    Rate limited, increasing delay to {current_sleep * 1.5:.2f}s")
            current_sleep = min(MAX_SLEEP, current_sleep * 1.5)
            time.sleep(30)
            return make_api_call(endpoint, params)
        else:
            print(f"    Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"    Exception: {e}")
        return None

def load_checkpoint():
    """Load checkpoint to resume collection"""
    checkpoint_file = 'fred_complete_data/tag_relationships/checkpoint.json'
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            return json.load(f)
    return {'completed_tags': [], 'last_tag_index': 0}

def save_checkpoint(checkpoint):
    """Save checkpoint for resilience"""
    checkpoint_file = 'fred_complete_data/tag_relationships/checkpoint.json'
    with open(checkpoint_file, 'w') as f:
        json.dump(checkpoint, f)

def collect_all_relationships_for_tag(tag_name):
    """Collect ALL relationships for a single tag using pagination"""
    all_related = []
    offset = 0
    limit = 1000
    api_calls = 0
    
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
            all_related.extend(batch)
            
            # Check if we got everything
            if len(batch) < limit:
                break
                
            offset += limit
        else:
            print(f"    Failed at offset {offset}")
            break
    
    return all_related, api_calls

def main():
    """Collect ALL tag relationships - no sampling"""
    
    print("\n" + "="*80)
    print("FRED TAG RELATIONSHIPS - COMPLETE PRODUCTION COLLECTION")
    print("="*80)
    
    # Load all tags
    with open('fred_complete_data/tags_complete.json', 'r') as f:
        all_tags = json.load(f)['tags']
    
    print(f"Total tags to process: {len(all_tags):,}")
    
    # Sort by series_count descending (most important first)
    all_tags.sort(key=lambda x: x.get('series_count', 0), reverse=True)
    
    # Create output directory
    output_dir = 'fred_complete_data/tag_relationships/complete'
    os.makedirs(output_dir, exist_ok=True)
    
    # Load checkpoint
    checkpoint = load_checkpoint()
    start_index = checkpoint['last_tag_index']
    completed_tags = set(checkpoint['completed_tags'])
    
    print(f"Starting from index: {start_index}")
    print(f"Previously completed: {len(completed_tags)} tags")
    
    # Collection stats
    total_api_calls = 0
    total_relationships = 0
    start_time = datetime.now()
    
    # Process all tags
    for idx, tag in enumerate(all_tags[start_index:], start_index):
        tag_name = tag['name']
        
        # Skip if already completed
        if tag_name in completed_tags:
            continue
        
        print(f"\n[{idx+1}/{len(all_tags)}] Processing: {tag_name}")
        print(f"  Series count: {tag.get('series_count', 0):,}")
        
        # Collect ALL relationships
        related_tags, api_calls = collect_all_relationships_for_tag(tag_name)
        total_api_calls += api_calls
        total_relationships += len(related_tags)
        
        print(f"  Found {len(related_tags):,} relationships in {api_calls} API calls")
        
        # Save individual tag file
        tag_data = {
            'source_tag': tag_name,
            'tag_metadata': tag,
            'relationship_count': len(related_tags),
            'api_calls': api_calls,
            'collected_at': datetime.now().isoformat(),
            'related_tags': related_tags
        }
        
        # Save with sanitized filename
        safe_filename = tag_name.replace('/', '_').replace(':', '_')
        tag_file = f"{output_dir}/tag_{safe_filename}.json"
        with open(tag_file, 'w') as f:
            json.dump(tag_data, f)
        
        # Update checkpoint
        completed_tags.add(tag_name)
        checkpoint = {
            'completed_tags': list(completed_tags),
            'last_tag_index': idx + 1,
            'total_api_calls': total_api_calls,
            'total_relationships': total_relationships,
            'last_updated': datetime.now().isoformat()
        }
        save_checkpoint(checkpoint)
        
        # Progress report every 100 tags
        if (idx + 1) % 100 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = (idx + 1 - start_index) / (elapsed / 3600)  # tags per hour
            eta_hours = (len(all_tags) - idx - 1) / rate if rate > 0 else 0
            
            print(f"\n--- Progress Report ---")
            print(f"Processed: {idx + 1}/{len(all_tags)} tags")
            print(f"API calls: {total_api_calls:,}")
            print(f"Relationships: {total_relationships:,}")
            print(f"Rate: {rate:.1f} tags/hour")
            print(f"ETA: {eta_hours:.1f} hours")
    
    # Final summary
    elapsed_total = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "="*80)
    print("COLLECTION COMPLETE")
    print("="*80)
    print(f"Total tags processed: {len(completed_tags):,}")
    print(f"Total API calls: {total_api_calls:,}")
    print(f"Total relationships: {total_relationships:,}")
    print(f"Total time: {elapsed_total/3600:.2f} hours")
    print(f"Average API calls per tag: {total_api_calls/len(completed_tags):.1f}")
    
    # Save final summary
    summary = {
        'collection_metadata': {
            'total_tags': len(all_tags),
            'processed_tags': len(completed_tags),
            'total_api_calls': total_api_calls,
            'total_relationships': total_relationships,
            'start_time': start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'elapsed_hours': elapsed_total/3600
        },
        'completed_tags': list(completed_tags)
    }
    
    with open(f'{output_dir}/../collection_complete_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Complete collection finished!")
    print(f"✅ All data saved to: {output_dir}")

if __name__ == "__main__":
    main()