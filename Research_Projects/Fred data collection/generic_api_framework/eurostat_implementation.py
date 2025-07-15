#!/usr/bin/env python3
"""
Eurostat API Implementation using Generic Framework
Demonstrates how the framework adapts to different APIs
"""

from api_discovery_framework import APIDiscoveryFramework, APIEndpoint
from typing import Dict, Any, List
import json

class EurostatDiscovery(APIDiscoveryFramework):
    """Eurostat-specific implementation of API discovery"""
    
    def __init__(self):
        # Eurostat API v2.1
        base_url = "https://ec.europa.eu/eurostat/api/dissemination"
        super().__init__("Eurostat", base_url, {})
        
    def setup_authentication(self):
        """Eurostat API is public, no auth needed"""
        self.schema.global_params = {
            'format': 'JSON',
            'lang': 'EN'
        }
        
    def discover_endpoints(self) -> Dict[str, APIEndpoint]:
        """Define Eurostat endpoints based on their API structure"""
        
        endpoints = {
            # Metadata endpoints
            'dataflows': APIEndpoint(
                path='/catalogue/v2.1/dataflows',
                description='Get all available datasets (dataflows)',
                collection_strategy='complete',
                data_key='dataflows'
            ),
            'datastructure': APIEndpoint(
                path='/catalogue/v2.1/datastructure/{dataflow_id}',
                description='Get structure/metadata of a specific dataset',
                required_params=['dataflow_id'],
                collection_strategy='sample',
                data_key='dataStructure'
            ),
            'codelist': APIEndpoint(
                path='/catalogue/v2.1/codelist/{agency}/{id}/{version}',
                description='Get code lists (dimensions values)',
                required_params=['agency', 'id', 'version'],
                collection_strategy='sample',
                data_key='codelist'
            ),
            
            # Data endpoints
            'dataset': APIEndpoint(
                path='/statistics/v2.1/data/{datasetCode}',
                description='Get actual statistical data',
                required_params=['datasetCode'],
                optional_params=['precision', 'geo', 'time', 'na_item'],
                collection_strategy='paginated',
                pagination={'type': 'offset', 'limit': 100}
            ),
            
            # Navigation/Browse endpoints
            'navigation_tree': APIEndpoint(
                path='/catalogue/v2.1/navigation',
                description='Get hierarchical navigation tree of themes',
                collection_strategy='complete',
                data_key='navigation'
            ),
            'theme_datasets': APIEndpoint(
                path='/catalogue/v2.1/theme/{theme_code}/datasets',
                description='Get datasets for a specific theme',
                required_params=['theme_code'],
                collection_strategy='complete',
                data_key='datasets'
            )
        }
        
        self.schema.endpoints = endpoints
        return endpoints
        
    def discover_eurostat_hierarchy(self):
        """Discover Eurostat-specific data relationships"""
        print("\n🏗️ Discovering Eurostat data hierarchy...")
        
        # Eurostat has a theme-based hierarchy
        self.schema.data_hierarchy = {
            'themes': ['datasets'],
            'datasets': ['dimensions', 'observations'],
            'dimensions': ['codelists'],
            'navigation': ['themes', 'subthemes']
        }
        
    def analyze_eurostat_patterns(self) -> Dict[str, Any]:
        """Analyze Eurostat-specific patterns"""
        patterns = {
            'data_format': {
                'primary': 'SDMX-JSON',
                'alternatives': ['CSV', 'TSV', 'XML'],
                'time_series': True
            },
            'filtering': {
                'dimension_based': True,
                'time_period': 'ISO 8601 periods',
                'geo_codes': 'Eurostat geo nomenclature'
            },
            'metadata_structure': {
                'uses_dsd': True,  # Data Structure Definition
                'codelists': 'Separate endpoint for dimension values',
                'multilingual': True
            },
            'common_dimensions': {
                'geo': 'Geographic entity',
                'time': 'Time period',
                'unit': 'Unit of measure',
                'na_item': 'National accounts item'
            }
        }
        
        self.schema.common_patterns = patterns
        return patterns


class BankOfJapanDiscovery(APIDiscoveryFramework):
    """Bank of Japan API implementation"""
    
    def __init__(self):
        # Bank of Japan Time-Series Data Search
        base_url = "https://api.boj.or.jp/api/v1"
        super().__init__("BankOfJapan", base_url, {})
        
    def setup_authentication(self):
        """BoJ API is public"""
        self.schema.global_params = {
            'lang': 'en'
        }
        
    def discover_endpoints(self) -> Dict[str, APIEndpoint]:
        """Define Bank of Japan endpoints"""
        
        endpoints = {
            'statistics_list': APIEndpoint(
                path='/statistics/list',
                description='Get list of all statistics',
                collection_strategy='complete',
                data_key='statistics'
            ),
            'statistics_metadata': APIEndpoint(
                path='/statistics/{stats_code}/metadata',
                description='Get metadata for specific statistics',
                required_params=['stats_code'],
                collection_strategy='sample'
            ),
            'timeseries_data': APIEndpoint(
                path='/timeseries/{series_code}',
                description='Get time series data',
                required_params=['series_code'],
                optional_params=['from', 'to', 'frequency'],
                collection_strategy='paginated',
                pagination={'type': 'date_range'}
            ),
            'data_categories': APIEndpoint(
                path='/categories',
                description='Get data categories',
                collection_strategy='complete',
                data_key='categories'
            )
        }
        
        self.schema.endpoints = endpoints
        return endpoints


def create_universal_discovery_config():
    """Create a configuration for discovering any economic data API"""
    
    config = {
        'discovery_patterns': {
            'endpoint_indicators': {
                'metadata': ['meta', 'structure', 'schema', 'catalog', 'dictionary'],
                'data': ['data', 'series', 'observations', 'values', 'statistics'],
                'hierarchy': ['categories', 'themes', 'topics', 'groups'],
                'relationships': ['tags', 'links', 'related', 'connections']
            },
            'pagination_indicators': {
                'offset': ['offset', 'skip', 'start', 'from'],
                'page': ['page', 'pageNumber', 'page_num'],
                'cursor': ['cursor', 'token', 'continuation'],
                'size': ['limit', 'size', 'count', 'per_page']
            },
            'time_patterns': {
                'period': ['period', 'date', 'time', 'timestamp'],
                'range': ['from', 'to', 'start_date', 'end_date'],
                'frequency': ['frequency', 'freq', 'periodicity']
            }
        },
        'collection_strategies': {
            'foundation_first': [
                'metadata',
                'structure', 
                'categories',
                'dimensions'
            ],
            'hierarchical': [
                'parent_child_relationships',
                'recursive_discovery'
            ],
            'data_collection': [
                'sample_first',
                'validate_structure',
                'bulk_collection'
            ]
        },
        'optimization_rules': {
            'rate_limiting': 'adaptive_backoff',
            'caching': 'metadata_cache',
            'parallel_collection': 'thread_pool',
            'checkpoint_strategy': 'incremental_save'
        }
    }
    
    return config


def demonstrate_universal_discovery():
    """Demonstrate the framework with multiple APIs"""
    
    print("🌐 Universal Economic Data API Discovery")
    print("="*60)
    
    # Test with Eurostat
    print("\n📊 EUROSTAT Discovery:")
    eurostat = EurostatDiscovery()
    eurostat.setup_authentication()
    eurostat_endpoints = eurostat.discover_endpoints()
    print(f"Discovered {len(eurostat_endpoints)} Eurostat endpoints")
    
    # Test with Bank of Japan
    print("\n🏦 Bank of Japan Discovery:")
    boj = BankOfJapanDiscovery()
    boj.setup_authentication()
    boj_endpoints = boj.discover_endpoints()
    print(f"Discovered {len(boj_endpoints)} BoJ endpoints")
    
    # Show universal config
    print("\n🔧 Universal Discovery Configuration:")
    config = create_universal_discovery_config()
    print(json.dumps(config, indent=2))
    
    print("\n✅ Multi-API discovery demonstration complete!")


if __name__ == "__main__":
    demonstrate_universal_discovery()