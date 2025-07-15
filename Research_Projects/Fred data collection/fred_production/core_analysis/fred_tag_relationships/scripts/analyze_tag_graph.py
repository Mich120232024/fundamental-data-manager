#!/usr/bin/env python3
"""
Analyze the tag graph structure from collected relationships
"""

import json
from collections import defaultdict

def analyze_tag_graph():
    """Analyze tag relationship patterns"""
    
    # Load the collected relationships
    with open('fred_complete_data/tag_relationships/tag_relationships_sample.json', 'r') as f:
        data = json.load(f)
    
    relationships = data['relationships']
    
    print("\n" + "="*80)
    print("TAG GRAPH STRUCTURE ANALYSIS")
    print("="*80)
    
    # 1. Build adjacency matrix
    graph = defaultdict(set)
    edge_weights = defaultdict(int)
    
    for source_tag, rel_data in relationships.items():
        if 'top_related' in rel_data:
            for related in rel_data['top_related']:
                target = related['name']
                weight = related['series_count']
                graph[source_tag].add(target)
                graph[target].add(source_tag)  # Bidirectional
                edge_weights[(source_tag, target)] = weight
    
    print(f"\nGraph Statistics:")
    print(f"- Nodes (unique tags): {len(graph)}")
    print(f"- Edges: {sum(len(v) for v in graph.values()) // 2}")
    
    # 2. Find central nodes (highest degree)
    node_degrees = [(tag, len(connections)) for tag, connections in graph.items()]
    node_degrees.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nMost Connected Nodes (Degree Centrality):")
    for tag, degree in node_degrees[:15]:
        print(f"  {tag}: {degree} direct connections")
    
    # 3. Identify clusters by tag groups
    tag_groups = defaultdict(list)
    
    # From our sample, extract group patterns
    for source_tag, rel_data in relationships.items():
        if 'top_related' in rel_data:
            for related in rel_data['top_related']:
                if related.get('group_id'):
                    tag_groups[related['group_id']].append(related['name'])
    
    print(f"\nTag Groups Found:")
    for group, tags in sorted(tag_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        unique_tags = len(set(tags))
        print(f"  {group}: {unique_tags} unique tags")
    
    # 4. Path analysis - find connections between economic indicators
    economic_tags = ['gdp', 'inflation', 'unemployment', 'employment']
    
    print(f"\nEconomic Indicator Connections:")
    for i, tag1 in enumerate(economic_tags):
        if tag1 not in graph:
            continue
        for tag2 in economic_tags[i+1:]:
            if tag2 not in graph:
                continue
            
            # Find common connections
            common = graph[tag1].intersection(graph[tag2])
            if common:
                print(f"\n  {tag1} ↔ {tag2}:")
                print(f"    Common connections: {len(common)}")
                # Show top 5 by weight
                weighted_common = []
                for tag in common:
                    w1 = edge_weights.get((tag1, tag), 0)
                    w2 = edge_weights.get((tag2, tag), 0)
                    weighted_common.append((tag, max(w1, w2)))
                
                weighted_common.sort(key=lambda x: x[1], reverse=True)
                for tag, weight in weighted_common[:5]:
                    print(f"      - {tag} (weight: {weight:,})")
    
    # 5. Create simplified visualization data
    print(f"\n\nGRAPH VISUALIZATION DATA")
    print("="*80)
    
    # Select key nodes for visualization
    viz_nodes = set()
    
    # Add all successful source tags
    for tag, rel_data in relationships.items():
        if 'related_count' in rel_data:
            viz_nodes.add(tag)
    
    # Add top connected tags
    for tag, _ in node_degrees[:20]:
        viz_nodes.add(tag)
    
    # Create node and edge lists for visualization
    nodes = []
    edges = []
    
    for tag in viz_nodes:
        # Determine node properties
        node_data = {
            'id': tag,
            'label': tag,
            'degree': len(graph.get(tag, [])),
            'category': 'hub' if len(graph.get(tag, [])) > 15 else 'normal'
        }
        
        # Set category based on source data
        for source_tag, rel_data in relationships.items():
            if source_tag == tag:
                node_data['category'] = rel_data.get('category', 'normal')
                break
        
        nodes.append(node_data)
    
    # Add edges between viz nodes
    seen_edges = set()
    for source in viz_nodes:
        if source in graph:
            for target in graph[source]:
                if target in viz_nodes:
                    edge_key = tuple(sorted([source, target]))
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        weight = edge_weights.get((source, target), 0)
                        if weight == 0:
                            weight = edge_weights.get((target, source), 0)
                        
                        edges.append({
                            'source': source,
                            'target': target,
                            'weight': weight
                        })
    
    # Save visualization data
    viz_data = {
        'nodes': nodes,
        'edges': edges,
        'stats': {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'categories': list(set(n['category'] for n in nodes))
        }
    }
    
    with open('fred_complete_data/tag_relationships/tag_graph_viz.json', 'w') as f:
        json.dump(viz_data, f, indent=2)
    
    print(f"\nVisualization data:")
    print(f"- Nodes: {len(nodes)}")
    print(f"- Edges: {len(edges)}")
    print(f"- Categories: {viz_data['stats']['categories']}")
    
    print(f"\n✅ Graph analysis complete!")
    print(f"✅ Visualization data saved to: tag_graph_viz.json")

if __name__ == "__main__":
    analyze_tag_graph()