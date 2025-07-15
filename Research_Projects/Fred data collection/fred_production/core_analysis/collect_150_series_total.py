#!/usr/bin/env python3
"""
Collect exactly 150 FRED series with metadata
Spread across different leaf categories for diversity
"""

import json
import requests
import time
import os
from datetime import datetime
import random

API_KEY = "21acd97c4988e53af02e98587d5424d0"
BASE_URL = "https://api.stlouisfed.org/fred"

def load_categories():
    """Load all categories"""
    with open('fred_complete_data/categories_complete_hierarchy.json', 'r') as f:
        data = json.load(f)
    return data['categories']

def make_api_call(endpoint, params=None):
    """Make API call with rate limiting"""
    if params is None:
        params = {}
    params['api_key'] = API_KEY
    params['file_type'] = 'json'
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.get(url, params=params, timeout=30)
        time.sleep(0.6)  # Conservative rate
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Rate limited, waiting 30s...")
            time.sleep(30)
            return make_api_call(endpoint, params)
        else:
            print(f"Error {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def collect_150_series():
    """Collect exactly 150 series from diverse categories"""
    
    categories = load_categories()
    
    # Get leaf categories from different depths for diversity
    leaf_categories = [
        (cat_id, cat) for cat_id, cat in categories.items() 
        if cat.get('is_leaf', False)
    ]
    
    # Group by depth for diversity
    by_depth = {}
    for cat_id, cat in leaf_categories:
        depth = cat.get('depth', 0)
        if depth not in by_depth:
            by_depth[depth] = []
        by_depth[depth].append((cat_id, cat))
    
    print("\n" + "="*60)
    print("COLLECTING EXACTLY 150 FRED SERIES")
    print("="*60)
    print(f"Leaf categories by depth:")
    for depth, cats in sorted(by_depth.items()):
        print(f"  Depth {depth}: {len(cats)} categories")
    
    # Select categories to get 150 series total
    selected_categories = []
    for depth in sorted(by_depth.keys()):
        # Take some categories from each depth
        sample_size = min(20, len(by_depth[depth]))  # Up to 20 per depth
        selected_categories.extend(random.sample(by_depth[depth], sample_size))
    
    all_series = {}
    api_calls = 0
    target_series = 150
    
    print(f"\nCollecting from {len(selected_categories)} diverse categories...")
    
    for cat_id, cat in selected_categories:
        if len(all_series) >= target_series:
            break
            
        cat_name = cat.get('name', 'Unknown')
        print(f"\nCategory: {cat_name} (ID: {cat_id}, Depth: {cat.get('depth')})")
        
        # Get series in this category
        response = make_api_call('/category/series', {'category_id': cat_id})
        api_calls += 1
        
        if response and 'seriess' in response:
            series_list = response['seriess']
            print(f"  Found {len(series_list)} series")
            
            # Calculate how many to take from this category
            remaining_needed = target_series - len(all_series)
            to_take = min(remaining_needed, min(len(series_list), 5))  # Max 5 per category
            
            for series in series_list[:to_take]:
                series_id = series['id']
                
                # Get detailed series info
                detail_response = make_api_call('/series', {'series_id': series_id})
                api_calls += 1
                
                if detail_response and 'seriess' in detail_response:
                    series_detail = detail_response['seriess'][0]
                    
                    # Store data
                    all_series[series_id] = {
                        'basic_info': series_detail,
                        'source_category': {
                            'id': cat_id,
                            'name': cat_name,
                            'depth': cat.get('depth')
                        }
                    }
                    
                    print(f"  [{len(all_series)}/150] {series_id}: {series_detail.get('title', '')[:40]}...")
                
                if len(all_series) >= target_series:
                    break
    
    print(f"\n\nCollection complete!")
    print(f"Total series collected: {len(all_series)}")
    print(f"Total API calls: {api_calls}")
    
    # Analyze metadata structure
    print("\n" + "="*60)
    print("METADATA ANALYSIS")
    print("="*60)
    
    # Collect all unique fields and values
    all_fields = set()
    frequencies = set()
    units = set()
    seasonal_adjs = set()
    
    for series_data in all_series.values():
        info = series_data['basic_info']
        all_fields.update(info.keys())
        frequencies.add(info.get('frequency'))
        units.add(info.get('units'))
        seasonal_adjs.add(info.get('seasonal_adjustment'))
    
    print(f"\nMetadata fields found ({len(all_fields)}):")
    for field in sorted(all_fields):
        print(f"  - {field}")
    
    print(f"\nUnique Frequencies ({len(frequencies)}): {sorted(frequencies)}")
    print(f"\nUnique Units ({len(units)}): {sorted(units)[:15]}...")
    print(f"\nSeasonal Adjustments: {sorted(seasonal_adjs)}")
    
    # Save results
    output = {
        'collection_metadata': {
            'timestamp': datetime.now().isoformat(),
            'series_collected': len(all_series),
            'categories_used': len(set(s['source_category']['id'] for s in all_series.values())),
            'api_calls': api_calls,
            'purpose': '150_series_diverse_sample'
        },
        'metadata_structure': {
            'fields': sorted(all_fields),
            'unique_frequencies': sorted(frequencies),
            'unique_units': sorted(units),
            'seasonal_adjustments': sorted(seasonal_adjs)
        },
        'series_data': all_series
    }
    
    with open('fred_complete_data/sample_150_series_complete.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Results saved to: fred_complete_data/sample_150_series_complete.json")

if __name__ == "__main__":
    collect_150_series()