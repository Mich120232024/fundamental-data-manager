#!/usr/bin/env python3
"""
Collect tag relationships using /fred/related_tags endpoint
Feed it various tags from our existing collection to analyze the tag graph
"""

import json
import requests
import time
import os
from datetime import datetime

API_KEY = "21acd97c4988e53af02e98587d5424d0"
BASE_URL = "https://api.stlouisfed.org/fred"

def load_existing_tags():
    """Load tags from our complete collection"""
    with open('fred_complete_data/tags_complete.json', 'r') as f:
        data = json.load(f)
    return data['tags']

def make_api_call(endpoint, params=None):
    """Make API call with rate limiting"""
    if params is None:
        params = {}
    params['api_key'] = API_KEY
    params['file_type'] = 'json'
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.get(url, params=params, timeout=30)
        time.sleep(0.5)  # Rate limiting
        
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

def collect_tag_relationships():
    """Collect relationships for diverse tags"""
    
    # Load existing tags
    all_tags = load_existing_tags()
    
    # Select diverse tags based on different criteria
    selected_tags = []
    
    # 1. Most popular tags (high series count)
    popular_tags = sorted(all_tags, key=lambda x: x.get('series_count', 0), reverse=True)[:20]
    selected_tags.extend([(t['name'], 'popular') for t in popular_tags])
    
    # 2. Different group types
    groups = {}
    for tag in all_tags:
        group = tag.get('group_id', 'unknown')
        if group not in groups:
            groups[group] = []
        groups[group].append(tag)
    
    # Take 5 from each group
    for group, tags in groups.items():
        if tags:
            selected_tags.extend([(t['name'], f'group_{group}') for t in tags[:5]])
    
    # 3. Tags with interesting names
    interesting_keywords = ['crisis', 'recession', 'boom', 'inflation', 'deflation', 
                          'employment', 'trade', 'debt', 'growth', 'decline']
    for keyword in interesting_keywords:
        for tag in all_tags:
            if keyword in tag['name'].lower():
                selected_tags.append((tag['name'], f'keyword_{keyword}'))
                break
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag_name, category in selected_tags:
        if tag_name not in seen:
            seen.add(tag_name)
            unique_tags.append((tag_name, category))
    
    print(f"\n{'='*80}")
    print(f"COLLECTING TAG RELATIONSHIPS")
    print(f"{'='*80}")
    print(f"Selected {len(unique_tags)} unique tags to analyze")
    
    # Create output directory
    output_dir = 'fred_complete_data/tag_relationships'
    os.makedirs(output_dir, exist_ok=True)
    
    all_relationships = {}
    api_calls = 0
    
    for idx, (tag_name, category) in enumerate(unique_tags[:200], 1):  # Limit to 200
        print(f"\n[{idx}/{min(len(unique_tags), 200)}] Tag: {tag_name} (Category: {category})")
        
        # Get related tags
        response = make_api_call('/related_tags', {'tag_names': tag_name})
        api_calls += 1
        
        if response and 'tags' in response:
            related_count = len(response['tags'])
            print(f"  Found {related_count} related tags")
            
            # Store the relationship data
            all_relationships[tag_name] = {
                'source_tag': tag_name,
                'category': category,
                'related_count': related_count,
                'api_response': response
            }
            
            # Show top 5 related tags
            if related_count > 0:
                print(f"  Top related tags:")
                for related_tag in response['tags'][:5]:
                    print(f"    - {related_tag['name']} (count: {related_tag.get('series_count', 0)})")
        else:
            print(f"  Failed to get related tags")
    
    # Analyze the graph structure
    print(f"\n\n{'='*80}")
    print(f"TAG RELATIONSHIP ANALYSIS")
    print(f"{'='*80}")
    
    total_relationships = sum(r['related_count'] for r in all_relationships.values())
    avg_relationships = total_relationships / len(all_relationships) if all_relationships else 0
    
    print(f"\nCollection Summary:")
    print(f"- Tags analyzed: {len(all_relationships)}")
    print(f"- Total relationships found: {total_relationships:,}")
    print(f"- Average relationships per tag: {avg_relationships:.1f}")
    print(f"- API calls made: {api_calls}")
    
    # Find most connected tags
    most_connected = sorted(all_relationships.items(), 
                          key=lambda x: x[1]['related_count'], 
                          reverse=True)[:10]
    
    print(f"\nMost Connected Tags:")
    for tag_name, data in most_connected:
        print(f"  {tag_name}: {data['related_count']} connections")
    
    # Analyze by group
    group_stats = {}
    for tag_name, data in all_relationships.items():
        if data['category'].startswith('group_'):
            group = data['category'].replace('group_', '')
            if group not in group_stats:
                group_stats[group] = []
            group_stats[group].append(data['related_count'])
    
    print(f"\nAverage Connections by Group:")
    for group, counts in sorted(group_stats.items()):
        if counts:
            avg = sum(counts) / len(counts)
            print(f"  {group}: {avg:.1f} connections (from {len(counts)} samples)")
    
    # Save results
    output_file = f"{output_dir}/tag_relationships_analysis.json"
    output = {
        'collection_metadata': {
            'timestamp': datetime.now().isoformat(),
            'tags_analyzed': len(all_relationships),
            'api_calls': api_calls,
            'total_relationships': total_relationships
        },
        'summary_stats': {
            'average_relationships_per_tag': avg_relationships,
            'most_connected_tags': [(tag, data['related_count']) for tag, data in most_connected]
        },
        'relationships': all_relationships
    }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
    
    # Also save a simplified graph format
    graph_file = f"{output_dir}/tag_graph_simplified.json"
    graph_data = {}
    
    for tag_name, data in all_relationships.items():
        connections = []
        for related_tag in data['api_response']['tags'][:20]:  # Top 20 connections
            connections.append({
                'name': related_tag['name'],
                'weight': related_tag.get('series_count', 0)
            })
        graph_data[tag_name] = connections
    
    with open(graph_file, 'w') as f:
        json.dump(graph_data, f, indent=2)
    
    print(f"✅ Simplified graph saved to: {graph_file}")

if __name__ == "__main__":
    collect_tag_relationships()