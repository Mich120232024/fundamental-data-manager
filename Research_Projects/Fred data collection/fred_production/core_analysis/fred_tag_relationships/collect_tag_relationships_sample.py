#!/usr/bin/env python3
"""
Collect a sample of tag relationships to analyze the tag graph structure
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
        time.sleep(0.6)  # Conservative rate limiting
        
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

def collect_sample_relationships():
    """Collect relationships for a diverse sample of tags"""
    
    # Define a focused set of important tags to analyze
    sample_tags = [
        # Economic indicators
        ('gdp', 'economic'),
        ('inflation', 'economic'),
        ('unemployment', 'economic'),
        ('recession', 'economic'),
        ('interest rate', 'economic'),
        
        # Geographic
        ('usa', 'geographic'),
        ('china', 'geographic'),
        ('europe', 'geographic'),
        ('japan', 'geographic'),
        
        # Frequency
        ('annual', 'frequency'),
        ('quarterly', 'frequency'),
        ('monthly', 'frequency'),
        ('daily', 'frequency'),
        
        # Sources
        ('bls', 'source'),
        ('bea', 'source'),
        ('census', 'source'),
        ('frb', 'source'),
        
        # Sectors
        ('manufacturing', 'sector'),
        ('housing', 'sector'),
        ('retail', 'sector'),
        ('finance', 'sector'),
        
        # Types
        ('index', 'type'),
        ('rate', 'type'),
        ('price', 'type'),
        ('employment', 'type'),
        
        # Special topics
        ('covid', 'special'),
        ('pandemic', 'special'),
        ('crisis', 'special'),
        ('forecast', 'special')
    ]
    
    print(f"\n{'='*80}")
    print(f"COLLECTING TAG RELATIONSHIPS SAMPLE")
    print(f"{'='*80}")
    print(f"Analyzing {len(sample_tags)} strategic tags")
    
    # Create output directory
    output_dir = 'fred_complete_data/tag_relationships'
    os.makedirs(output_dir, exist_ok=True)
    
    all_relationships = {}
    api_calls = 0
    
    for idx, (tag_name, category) in enumerate(sample_tags, 1):
        print(f"\n[{idx}/{len(sample_tags)}] Tag: '{tag_name}' (Category: {category})")
        
        # Get related tags
        response = make_api_call('/related_tags', {'tag_names': tag_name})
        api_calls += 1
        
        if response and 'tags' in response:
            related_count = response.get('count', len(response['tags']))
            print(f"  Found {related_count} related tags")
            
            # Store the relationship data
            all_relationships[tag_name] = {
                'source_tag': tag_name,
                'category': category,
                'related_count': related_count,
                'total_available': response.get('count', related_count),
                'limit': response.get('limit', 1000),
                'top_related': []
            }
            
            # Store top 10 related tags with details
            for related_tag in response['tags'][:10]:
                all_relationships[tag_name]['top_related'].append({
                    'name': related_tag['name'],
                    'group_id': related_tag.get('group_id'),
                    'series_count': related_tag.get('series_count', 0),
                    'popularity': related_tag.get('popularity', 0)
                })
                
            # Show top 5
            print(f"  Top 5 related tags:")
            for i, related_tag in enumerate(response['tags'][:5], 1):
                print(f"    {i}. {related_tag['name']} ({related_tag.get('series_count', 0)} series)")
        else:
            print(f"  ❌ Failed to get related tags")
            all_relationships[tag_name] = {
                'source_tag': tag_name,
                'category': category,
                'error': 'Failed to retrieve'
            }
    
    # Analyze the graph structure
    print(f"\n\n{'='*80}")
    print(f"TAG RELATIONSHIP ANALYSIS")
    print(f"{'='*80}")
    
    # Basic stats
    successful = [r for r in all_relationships.values() if 'related_count' in r]
    total_relationships = sum(r['related_count'] for r in successful)
    avg_relationships = total_relationships / len(successful) if successful else 0
    
    print(f"\nCollection Summary:")
    print(f"- Tags analyzed: {len(all_relationships)}")
    print(f"- Successful: {len(successful)}")
    print(f"- Total relationships found: {total_relationships:,}")
    print(f"- Average relationships per tag: {avg_relationships:.1f}")
    print(f"- API calls made: {api_calls}")
    
    # Most connected tags
    most_connected = sorted(
        [(k, v['related_count']) for k, v in all_relationships.items() if 'related_count' in v],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    print(f"\nMost Connected Tags:")
    for tag_name, count in most_connected:
        print(f"  '{tag_name}': {count:,} connections")
    
    # Category analysis
    category_stats = {}
    for data in successful:
        cat = data['category']
        if cat not in category_stats:
            category_stats[cat] = []
        category_stats[cat].append(data['related_count'])
    
    print(f"\nAverage Connections by Category:")
    for cat, counts in sorted(category_stats.items()):
        avg = sum(counts) / len(counts)
        print(f"  {cat}: {avg:.1f} avg connections ({len(counts)} tags)")
    
    # Common connections (tags that appear related to multiple source tags)
    connection_frequency = {}
    for data in successful:
        for related in data.get('top_related', []):
            tag = related['name']
            if tag not in connection_frequency:
                connection_frequency[tag] = 0
            connection_frequency[tag] += 1
    
    print(f"\nMost Common Related Tags (appear in multiple relationships):")
    common_connections = sorted(connection_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    for tag, freq in common_connections:
        print(f"  '{tag}': appears in {freq} tag relationships")
    
    # Save results
    output_file = f"{output_dir}/tag_relationships_sample.json"
    output = {
        'collection_metadata': {
            'timestamp': datetime.now().isoformat(),
            'tags_analyzed': len(all_relationships),
            'successful': len(successful),
            'api_calls': api_calls,
            'total_relationships': total_relationships
        },
        'summary_stats': {
            'average_relationships_per_tag': avg_relationships,
            'most_connected_tags': most_connected,
            'category_averages': {cat: sum(counts)/len(counts) for cat, counts in category_stats.items()},
            'most_common_connections': common_connections
        },
        'relationships': all_relationships
    }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
    print(f"✅ Analysis complete!")

if __name__ == "__main__":
    collect_sample_relationships()