#!/usr/bin/env python3
"""
FRED API Implementation using Generic Framework
Demonstrates how our patterns work with FRED
"""

from api_discovery_framework import APIDiscoveryFramework, APIEndpoint
from typing import Dict, Any, List
import os

class FREDDiscovery(APIDiscoveryFramework):
    """FRED-specific implementation of API discovery"""
    
    def __init__(self, api_key: str):
        base_url = "https://api.stlouisfed.org/fred"
        auth_config = {"api_key": api_key}
        super().__init__("FRED", base_url, auth_config)
        
    def setup_authentication(self):
        """FRED uses API key in query params"""
        self.schema.global_params = {
            'api_key': self.auth_config['api_key'],
            'file_type': 'json'
        }
        
    def discover_endpoints(self) -> Dict[str, APIEndpoint]:
        """Define FRED endpoints based on our analysis"""
        
        # Foundation endpoints (complete collection possible)
        endpoints = {
            'sources': APIEndpoint(
                path='/sources',
                description='Get all sources of economic data',
                data_key='sources',
                collection_strategy='complete'
            ),
            'releases': APIEndpoint(
                path='/releases',
                description='Get all releases',
                data_key='releases',
                collection_strategy='complete',
                optional_params=['realtime_start', 'realtime_end', 'order_by', 'sort_order']
            ),
            'tags': APIEndpoint(
                path='/tags',
                description='Get all tags',
                data_key='tags',
                collection_strategy='complete',
                optional_params=['realtime_start', 'realtime_end', 'search_text']
            ),
            'categories': APIEndpoint(
                path='/categories',
                description='Get all categories',
                data_key='categories',
                collection_strategy='complete'
            ),
            
            # Hierarchical endpoints
            'category_children': APIEndpoint(
                path='/category/children',
                description='Get child categories',
                required_params=['category_id'],
                data_key='categories',
                collection_strategy='sample'
            ),
            'category_series': APIEndpoint(
                path='/category/series',
                description='Get series in a category',
                required_params=['category_id'],
                data_key='seriess',
                collection_strategy='paginated',
                pagination={'type': 'offset', 'limit': 1000}
            ),
            
            # Relationship endpoints
            'series_categories': APIEndpoint(
                path='/series/categories',
                description='Get categories for a series',
                required_params=['series_id'],
                data_key='categories',
                collection_strategy='sample'
            ),
            'series_tags': APIEndpoint(
                path='/series/tags',
                description='Get tags for a series',
                required_params=['series_id'],
                data_key='tags',
                collection_strategy='sample'
            ),
            
            # Data endpoints
            'series': APIEndpoint(
                path='/series',
                description='Get series metadata',
                required_params=['series_id'],
                data_key='seriess',
                collection_strategy='sample'
            ),
            'series_observations': APIEndpoint(
                path='/series/observations',
                description='Get series data points',
                required_params=['series_id'],
                data_key='observations',
                collection_strategy='paginated',
                pagination={'type': 'offset', 'limit': 100000}
            )
        }
        
        self.schema.endpoints = endpoints
        return endpoints
        
    def discover_fred_hierarchy(self):
        """Discover FRED-specific data relationships"""
        print("\n🏗️ Discovering FRED data hierarchy...")
        
        # FRED has a specific hierarchy
        self.schema.data_hierarchy = {
            'sources': ['releases'],
            'releases': ['series'],
            'categories': ['categories', 'series'],  # Self-referential + series
            'tags': ['series'],
            'series': ['observations']
        }
        
    def analyze_fred_patterns(self) -> Dict[str, Any]:
        """Analyze FRED-specific patterns"""
        patterns = {
            'rate_limiting': {
                'type': 'requests_per_minute',
                'limit': 120,
                'strategy': 'exponential_backoff'
            },
            'pagination': {
                'type': 'offset_based',
                'max_limit': 1000,
                'parameters': ['limit', 'offset']
            },
            'data_keys': {
                'sources': 'sources',
                'releases': 'releases',
                'categories': 'categories',
                'tags': 'tags',
                'series': 'seriess',  # Note the double 's'
                'observations': 'observations'
            },
            'id_patterns': {
                'series': 'string (e.g., GDP, UNRATE)',
                'category': 'integer',
                'release': 'integer',
                'source': 'integer',
                'tag': 'string (tag name)'
            },
            'common_parameters': {
                'realtime_start': 'YYYY-MM-DD',
                'realtime_end': 'YYYY-MM-DD',
                'limit': 'integer (max 1000 for most endpoints)',
                'offset': 'integer (for pagination)',
                'order_by': 'various options per endpoint',
                'sort_order': 'asc or desc'
            }
        }
        
        self.schema.common_patterns = patterns
        return patterns


def demonstrate_fred_discovery():
    """Demonstrate the framework with FRED"""
    
    # Initialize discovery
    api_key = os.getenv("FRED_API_KEY", "your_api_key_here")
    fred = FREDDiscovery(api_key)
    
    print("🚀 FRED API Discovery Demo")
    print("="*60)
    
    # Setup
    fred.setup_authentication()
    
    # Discover endpoints
    print("\n📍 Discovering endpoints...")
    endpoints = fred.discover_endpoints()
    print(f"Found {len(endpoints)} endpoints")
    
    # Analyze a sample endpoint
    if 'sources' in endpoints:
        print("\n🔍 Analyzing 'sources' endpoint...")
        analysis = fred.analyze_endpoint(endpoints['sources'])
        print(f"Analysis: {json.dumps(analysis, indent=2)}")
    
    # Discover hierarchy
    fred.discover_fred_hierarchy()
    print(f"\n🏗️ Data hierarchy: {fred.schema.data_hierarchy}")
    
    # Generate collection strategy
    print("\n📋 Generating collection strategy...")
    strategy = fred.generate_collection_strategy()
    print(f"Recommended order: {strategy['collection_order'][:5]}...")
    
    # Export schema
    fred.export_schema("fred_discovered_schema.yaml")
    
    # Generate collection code
    fred.generate_collection_code("fred_generated_collector")
    
    print("\n✅ Discovery complete!")


if __name__ == "__main__":
    import json
    demonstrate_fred_discovery()