#!/usr/bin/env python3
"""
FRED API Schema Response Analyzer
Makes real API calls and captures exact response schemas for catalog entry
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from pathlib import Path

# Set up environment
env_path = Path("/Users/mikaeleage/Research & Analytics Services/Agent_Shells/Data_Analyst/.env")
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

class FREDSchemaResponseAnalyzer:
    """Analyze FRED API responses and generate exact schemas"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"
        self.geofred_base_url = "https://api.stlouisfed.org/geofred"
        self.session = requests.Session()
        
        # Results storage
        self.endpoint_schemas = {}
        self.sample_responses = {}
        self.call_structures = {}
        
    def make_api_call(self, endpoint_name: str, base_url: str, path: str, params: Dict) -> Dict:
        """Make API call and capture full details"""
        time.sleep(0.6)  # Rate limiting
        
        url = f"{base_url}{path}"
        full_params = {**params, 'api_key': self.api_key, 'file_type': 'json'}
        
        # Store call structure
        call_structure = {
            'method': 'GET',
            'base_url': base_url,
            'path': path,
            'full_url': url,
            'parameters_sent': full_params,
            'example_call': f"{url}?" + "&".join([f"{k}={v}" for k, v in full_params.items()]),
            'curl_example': f"curl -X GET \"{url}?" + "&".join([f"{k}={v}" for k, v in full_params.items()]) + "\"",
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            response = self.session.get(url, params=full_params)
            response.raise_for_status()
            data = response.json()
            
            # Analyze response
            schema = self.generate_json_schema(data)
            
            # Store results
            self.call_structures[endpoint_name] = call_structure
            self.sample_responses[endpoint_name] = data
            self.endpoint_schemas[endpoint_name] = schema
            
            print(f"✅ {endpoint_name}: {response.status_code} - {self.count_records(data)} records")
            return data
            
        except Exception as e:
            print(f"❌ {endpoint_name}: Failed - {str(e)}")
            call_structure['error'] = str(e)
            self.call_structures[endpoint_name] = call_structure
            return None
    
    def generate_json_schema(self, data: Any, name: str = "root") -> Dict:
        """Generate JSON schema from actual data"""
        if isinstance(data, dict):
            properties = {}
            required = []
            
            for key, value in data.items():
                properties[key] = self.generate_json_schema(value, key)
                if value is not None and value != "":
                    required.append(key)
            
            schema = {
                "type": "object",
                "properties": properties
            }
            if required:
                schema["required"] = required
            return schema
            
        elif isinstance(data, list):
            if data:
                # Use first item to determine array schema
                items_schema = self.generate_json_schema(data[0], f"{name}_item")
                return {
                    "type": "array",
                    "items": items_schema,
                    "minItems": 0
                }
            else:
                return {
                    "type": "array",
                    "items": {}
                }
                
        elif isinstance(data, str):
            # Try to detect date patterns
            if self.is_date_string(data):
                return {"type": "string", "format": "date"}
            elif self.is_datetime_string(data):
                return {"type": "string", "format": "date-time"}
            else:
                return {"type": "string"}
                
        elif isinstance(data, bool):
            return {"type": "boolean"}
            
        elif isinstance(data, int):
            return {"type": "integer"}
            
        elif isinstance(data, float):
            return {"type": "number"}
            
        elif data is None:
            return {"type": "null"}
            
        else:
            return {"type": "string"}
    
    def is_date_string(self, s: str) -> bool:
        """Check if string is a date"""
        try:
            datetime.strptime(s, '%Y-%m-%d')
            return True
        except:
            return False
    
    def is_datetime_string(self, s: str) -> bool:
        """Check if string is a datetime"""
        datetime_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S UTC'
        ]
        for fmt in datetime_formats:
            try:
                datetime.strptime(s, fmt)
                return True
            except:
                continue
        return False
    
    def count_records(self, data: Dict) -> int:
        """Count data records in response"""
        data_keys = ['sources', 'releases', 'categories', 'seriess', 'observations', 'tags', 'release_dates', 'vintage_dates']
        for key in data_keys:
            if key in data and isinstance(data[key], list):
                return len(data[key])
        return 0
    
    def analyze_key_endpoints(self):
        """Analyze key FRED endpoints with different call patterns"""
        
        print("Analyzing FRED API Response Schemas...")
        print("=" * 60)
        
        # Key endpoints to analyze for schema patterns
        test_endpoints = [
            {
                'name': 'sources_single',
                'description': 'Get single data source',
                'base_url': self.base_url,
                'path': '/source',
                'params': {'source_id': 1},
                'call_type': 'single_item'
            },
            {
                'name': 'sources_bulk',
                'description': 'Get multiple data sources',
                'base_url': self.base_url,
                'path': '/sources',
                'params': {'limit': 10},
                'call_type': 'bulk_items'
            },
            {
                'name': 'series_metadata',
                'description': 'Get series metadata',
                'base_url': self.base_url,
                'path': '/series',
                'params': {'series_id': 'GDP'},
                'call_type': 'single_item'
            },
            {
                'name': 'series_observations',
                'description': 'Get series data observations',
                'base_url': self.base_url,
                'path': '/series/observations',
                'params': {'series_id': 'GDP', 'limit': 10},
                'call_type': 'bulk_observations'
            },
            {
                'name': 'series_search',
                'description': 'Search for series',
                'base_url': self.base_url,
                'path': '/series/search',
                'params': {'search_text': 'GDP unemployment', 'limit': 5},
                'call_type': 'search_results'
            },
            {
                'name': 'releases_bulk',
                'description': 'Get multiple releases',
                'base_url': self.base_url,
                'path': '/releases',
                'params': {'limit': 10},
                'call_type': 'bulk_items'
            },
            {
                'name': 'releases_calendar',
                'description': 'Get release calendar',
                'base_url': self.base_url,
                'path': '/releases/dates',
                'params': {'limit': 10, 'realtime_start': '2025-06-01', 'realtime_end': '2025-12-31'},
                'call_type': 'calendar_items'
            },
            {
                'name': 'categories_navigation',
                'description': 'Navigate category tree',
                'base_url': self.base_url,
                'path': '/category/children',
                'params': {'category_id': 0},
                'call_type': 'navigation_items'
            },
            {
                'name': 'category_series_bulk',
                'description': 'Get series in category',
                'base_url': self.base_url,
                'path': '/category/series',
                'params': {'category_id': 125, 'limit': 10},
                'call_type': 'bulk_items'
            },
            {
                'name': 'series_vintage_dates',
                'description': 'Get vintage dates for series',
                'base_url': self.base_url,
                'path': '/series/vintagedates',
                'params': {'series_id': 'GDP', 'limit': 10},
                'call_type': 'vintage_data'
            },
            {
                'name': 'tags_bulk',
                'description': 'Get multiple tags',
                'base_url': self.base_url,
                'path': '/tags',
                'params': {'limit': 10},
                'call_type': 'bulk_items'
            },
            {
                'name': 'series_relationships',
                'description': 'Get series categories relationship',
                'base_url': self.base_url,
                'path': '/series/categories',
                'params': {'series_id': 'GDP'},
                'call_type': 'relationship_data'
            }
        ]
        
        # Test each endpoint
        for endpoint in test_endpoints:
            print(f"Testing {endpoint['name']}: {endpoint['description']}")
            self.make_api_call(
                endpoint['name'],
                endpoint['base_url'],
                endpoint['path'],
                endpoint['params']
            )
        
        # Test GeoFRED if accessible
        try:
            print("\nTesting GeoFRED endpoints...")
            
            # Try to get series group info first
            geofred_endpoints = [
                {
                    'name': 'geofred_series_group',
                    'description': 'Get geographic series group info',
                    'base_url': self.geofred_base_url,
                    'path': '/series/group',
                    'params': {'series_id': 'WIPCPI'},
                    'call_type': 'geo_metadata'
                }
            ]
            
            for endpoint in geofred_endpoints:
                print(f"Testing {endpoint['name']}: {endpoint['description']}")
                self.make_api_call(
                    endpoint['name'],
                    endpoint['base_url'],
                    endpoint['path'],
                    endpoint['params']
                )
                
        except Exception as e:
            print(f"GeoFRED testing skipped: {e}")
    
    def generate_schema_documentation(self) -> Dict:
        """Generate comprehensive schema documentation"""
        
        schema_doc = {
            'api_name': 'FRED API',
            'analysis_date': datetime.utcnow().isoformat(),
            'total_endpoints_analyzed': len(self.endpoint_schemas),
            'call_patterns': {
                'single_item': 'Retrieve one specific resource by ID',
                'bulk_items': 'Retrieve multiple resources with pagination',
                'search_results': 'Search and filter resources',
                'observations': 'Time series data values',
                'relationships': 'Related entities and mappings',
                'calendar': 'Date-based scheduling information',
                'vintage': 'Historical data revisions'
            },
            'endpoints': {}
        }
        
        for endpoint_name, schema in self.endpoint_schemas.items():
            call_structure = self.call_structures.get(endpoint_name, {})
            sample_response = self.sample_responses.get(endpoint_name, {})
            
            endpoint_doc = {
                'endpoint_name': endpoint_name,
                'call_structure': call_structure,
                'response_schema': schema,
                'sample_response': sample_response,
                'schema_analysis': {
                    'data_location': self.find_data_location(sample_response),
                    'record_count': self.count_records(sample_response),
                    'has_pagination': self.has_pagination(sample_response),
                    'metadata_fields': self.extract_metadata_fields(sample_response)
                }
            }
            
            schema_doc['endpoints'][endpoint_name] = endpoint_doc
        
        return schema_doc
    
    def find_data_location(self, data: Dict) -> str:
        """Find where actual data is located"""
        if not data:
            return None
            
        data_keys = ['sources', 'releases', 'categories', 'seriess', 'observations', 'tags', 'release_dates', 'vintage_dates']
        for key in data_keys:
            if key in data and isinstance(data[key], list):
                return f"$.{key}"
        return None
    
    def has_pagination(self, data: Dict) -> bool:
        """Check if response has pagination"""
        pagination_keys = ['limit', 'offset', 'count']
        return any(key in data for key in pagination_keys)
    
    def extract_metadata_fields(self, data: Dict) -> List[str]:
        """Extract metadata field names"""
        if not data:
            return []
            
        metadata_keys = ['realtime_start', 'realtime_end', 'order_by', 'sort_order', 
                        'observation_start', 'observation_end', 'units', 'frequency',
                        'limit', 'offset', 'count']
        return [key for key in metadata_keys if key in data]
    
    def save_comprehensive_schemas(self, output_path: str):
        """Save all schemas and analysis"""
        schema_doc = self.generate_schema_documentation()
        
        with open(output_path, 'w') as f:
            json.dump(schema_doc, f, indent=2, default=str)
        
        print(f"\nComprehensive schema analysis saved to: {output_path}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("SCHEMA ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Endpoints analyzed: {len(self.endpoint_schemas)}")
        print(f"Successful responses: {len([e for e in self.call_structures.values() if 'error' not in e])}")
        print(f"Failed responses: {len([e for e in self.call_structures.values() if 'error' in e])}")
        
        print("\nCall Structure Examples:")
        for endpoint_name, call_struct in list(self.call_structures.items())[:3]:
            if 'error' not in call_struct:
                print(f"\n{endpoint_name}:")
                print(f"  URL: {call_struct['example_call'][:100]}...")
                print(f"  Records: {self.count_records(self.sample_responses.get(endpoint_name, {}))}")


def main():
    """Run comprehensive schema analysis"""
    api_key = os.environ.get('FRED_API_KEY')
    if not api_key:
        print("ERROR: FRED_API_KEY not found in environment")
        return
    
    analyzer = FREDSchemaResponseAnalyzer(api_key)
    analyzer.analyze_key_endpoints()
    
    # Save comprehensive results
    output_path = '/Users/mikaeleage/Fred data collection/fred_response_schemas_complete.json'
    analyzer.save_comprehensive_schemas(output_path)


if __name__ == "__main__":
    main()