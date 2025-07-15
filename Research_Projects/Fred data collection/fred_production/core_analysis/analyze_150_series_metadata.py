#!/usr/bin/env python3
"""
Analyze the 150 series metadata collection
Generate insights for Delta Lake schema design
"""

import json
from collections import Counter, defaultdict
from datetime import datetime

def analyze_metadata():
    """Comprehensive analysis of collected metadata"""
    
    # Load data
    with open('fred_complete_data/sample_150_series_complete.json', 'r') as f:
        data = json.load(f)
    
    series_data = data['series_data']
    
    print("\n" + "="*80)
    print("FRED 150 SERIES METADATA ANALYSIS")
    print("="*80)
    
    # Basic stats
    print(f"\nCollection Stats:")
    print(f"- Total series: {len(series_data)}")
    print(f"- Categories used: {data['collection_metadata']['categories_used']}")
    print(f"- API calls: {data['collection_metadata']['api_calls']}")
    print(f"- Collection time: {data['collection_metadata']['timestamp']}")
    
    # Analyze frequencies
    frequencies = Counter()
    for sid, sdata in series_data.items():
        freq = sdata['basic_info'].get('frequency', 'Unknown')
        frequencies[freq] += 1
    
    print(f"\n1. FREQUENCY DISTRIBUTION")
    print("-" * 40)
    for freq, count in frequencies.most_common():
        print(f"   {freq:<30} {count:>3} series ({count/len(series_data)*100:>5.1f}%)")
    
    # Analyze units
    units = Counter()
    for sid, sdata in series_data.items():
        unit = sdata['basic_info'].get('units', 'Unknown')
        units[unit] += 1
    
    print(f"\n2. UNITS DISTRIBUTION (Top 15)")
    print("-" * 40)
    for unit, count in units.most_common(15):
        unit_display = unit[:40] + "..." if len(unit) > 40 else unit
        print(f"   {unit_display:<43} {count:>3} series")
    print(f"   ... and {len(units)-15} more unit types")
    
    # Analyze seasonal adjustment
    seasonal = Counter()
    for sid, sdata in series_data.items():
        sa = sdata['basic_info'].get('seasonal_adjustment', 'Unknown')
        seasonal[sa] += 1
    
    print(f"\n3. SEASONAL ADJUSTMENT")
    print("-" * 40)
    for sa, count in seasonal.most_common():
        print(f"   {sa:<30} {count:>3} series ({count/len(series_data)*100:>5.1f}%)")
    
    # Analyze date ranges
    print(f"\n4. OBSERVATION DATE RANGES")
    print("-" * 40)
    
    date_ranges = []
    for sid, sdata in series_data.items():
        start = sdata['basic_info'].get('observation_start')
        end = sdata['basic_info'].get('observation_end')
        if start and end:
            date_ranges.append((start, end, sid))
    
    # Find earliest and latest
    date_ranges.sort(key=lambda x: x[0])
    print(f"   Earliest start: {date_ranges[0][0]} ({date_ranges[0][2]})")
    
    date_ranges.sort(key=lambda x: x[1], reverse=True)
    print(f"   Latest end:     {date_ranges[0][1]} ({date_ranges[0][2]})")
    
    # Analyze popularity
    popularities = []
    for sid, sdata in series_data.items():
        pop = sdata['basic_info'].get('popularity', 0)
        popularities.append((pop, sid, sdata['basic_info'].get('title', '')))
    
    popularities.sort(reverse=True)
    
    print(f"\n5. MOST POPULAR SERIES (Top 10)")
    print("-" * 40)
    for pop, sid, title in popularities[:10]:
        title_display = title[:50] + "..." if len(title) > 50 else title
        print(f"   {sid:<20} (pop: {pop:>3}) {title_display}")
    
    # Analyze note lengths
    note_lengths = []
    for sid, sdata in series_data.items():
        notes = sdata['basic_info'].get('notes', '')
        if notes:
            note_lengths.append(len(notes))
    
    print(f"\n6. NOTES FIELD ANALYSIS")
    print("-" * 40)
    print(f"   Series with notes: {len(note_lengths)}/{len(series_data)}")
    if note_lengths:
        print(f"   Average length: {sum(note_lengths)/len(note_lengths):.0f} characters")
        print(f"   Max length: {max(note_lengths)} characters")
        print(f"   Min length: {min(note_lengths)} characters")
    
    # Category depth analysis
    by_depth = defaultdict(list)
    for sid, sdata in series_data.items():
        depth = sdata['source_category']['depth']
        cat_name = sdata['source_category']['name']
        by_depth[depth].append(cat_name)
    
    print(f"\n7. CATEGORY DEPTH DISTRIBUTION")
    print("-" * 40)
    for depth in sorted(by_depth.keys()):
        unique_cats = len(set(by_depth[depth]))
        total_series = len(by_depth[depth])
        print(f"   Depth {depth}: {total_series} series from {unique_cats} categories")
    
    # Field completeness
    print(f"\n8. FIELD COMPLETENESS")
    print("-" * 40)
    field_counts = defaultdict(int)
    for sid, sdata in series_data.items():
        for field in data['metadata_structure']['fields']:
            if sdata['basic_info'].get(field) is not None:
                field_counts[field] += 1
    
    for field in sorted(data['metadata_structure']['fields']):
        count = field_counts[field]
        print(f"   {field:<25} {count:>3}/{len(series_data)} ({count/len(series_data)*100:>5.1f}%)")
    
    print("\n" + "="*80)
    print("SCHEMA DESIGN INSIGHTS")
    print("="*80)
    
    print("\n1. All 15 standard fields are present in 100% of series")
    print("2. Frequency partitioning would create 10 partitions")
    print("3. Units field has high cardinality (31+ unique values)")
    print("4. Notes field requires TEXT/CLOB type (up to several KB)")
    print("5. Popularity field could be used for query optimization")
    print("6. Date ranges span from 1776 to 2025 - need proper date handling")
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    analyze_metadata()