#!/usr/bin/env python3
"""
Generic API Discovery and Collection Framework
Designed to work with any REST API (FRED, Eurostat, Bank of Japan, etc.)
"""

import json
import requests
import time
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Set, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections import defaultdict
import yaml

@dataclass
class APIEndpoint:
    """Represents a single API endpoint"""
    path: str
    method: str = "GET"
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_params: List[str] = field(default_factory=list)
    optional_params: List[str] = field(default_factory=list)
    data_key: Optional[str] = None
    pagination: Dict[str, Any] = field(default_factory=dict)
    rate_limit: Dict[str, Any] = field(default_factory=dict)
    example_response: Optional[Dict] = None
    related_endpoints: List[str] = field(default_factory=list)
    collection_strategy: str = "sample"  # sample, complete, or paginated

@dataclass
class APISchema:
    """Represents the complete API structure"""
    name: str
    base_url: str
    version: str = ""
    authentication: Dict[str, Any] = field(default_factory=dict)
    global_params: Dict[str, Any] = field(default_factory=dict)
    rate_limits: Dict[str, Any] = field(default_factory=dict)
    endpoints: Dict[str, APIEndpoint] = field(default_factory=dict)
    data_hierarchy: Dict[str, List[str]] = field(default_factory=dict)
    common_patterns: Dict[str, Any] = field(default_factory=dict)

class APIDiscoveryFramework(ABC):
    """Abstract base class for API discovery"""
    
    def __init__(self, api_name: str, base_url: str, auth_config: Dict[str, Any]):
        self.api_name = api_name
        self.base_url = base_url.rstrip('/')
        self.auth_config = auth_config
        self.schema = APISchema(name=api_name, base_url=base_url)
        self.session = requests.Session()
        self.stats = {
            'api_calls': 0,
            'endpoints_discovered': 0,
            'rate_limits_hit': 0,
            'start_time': datetime.now()
        }
        
    @abstractmethod
    def setup_authentication(self):
        """Setup API authentication"""
        pass
        
    @abstractmethod
    def discover_endpoints(self) -> Dict[str, APIEndpoint]:
        """Discover available API endpoints"""
        pass
        
    def analyze_endpoint(self, endpoint: APIEndpoint) -> Dict[str, Any]:
        """Analyze a single endpoint to understand its structure"""
        print(f"\n🔍 Analyzing endpoint: {endpoint.path}")
        
        # Make sample request
        response = self._make_request(endpoint)
        if not response:
            return {}
            
        analysis = {
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'headers': dict(response.headers),
            'data_structure': {}
        }
        
        if response.status_code == 200:
            data = response.json()
            analysis['data_structure'] = self._analyze_json_structure(data)
            analysis['data_keys'] = list(data.keys()) if isinstance(data, dict) else []
            analysis['record_count'] = self._count_records(data)
            analysis['pagination_detected'] = self._detect_pagination(data)
            
        return analysis
        
    def _analyze_json_structure(self, data: Any, max_depth: int = 3, current_depth: int = 0) -> Dict:
        """Recursively analyze JSON structure"""
        if current_depth >= max_depth:
            return {"type": type(data).__name__, "truncated": True}
            
        if isinstance(data, dict):
            structure = {
                "type": "object",
                "keys": {}
            }
            for key, value in data.items():
                structure["keys"][key] = self._analyze_json_structure(value, max_depth, current_depth + 1)
            return structure
            
        elif isinstance(data, list):
            if not data:
                return {"type": "array", "items": "empty"}
            # Analyze first item as sample
            return {
                "type": "array",
                "length": len(data),
                "items": self._analyze_json_structure(data[0], max_depth, current_depth + 1)
            }
            
        else:
            return {
                "type": type(data).__name__,
                "sample": str(data)[:50] if data else None
            }
            
    def _count_records(self, data: Any) -> int:
        """Count records in response"""
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            # Look for common data keys
            for key in ['data', 'results', 'items', 'records', 'values']:
                if key in data and isinstance(data[key], list):
                    return len(data[key])
        return 0
        
    def _detect_pagination(self, data: Dict) -> Dict[str, Any]:
        """Detect pagination patterns"""
        pagination_hints = {
            'has_pagination': False,
            'pagination_type': None,
            'indicators': []
        }
        
        if not isinstance(data, dict):
            return pagination_hints
            
        # Check for common pagination patterns
        pagination_keys = {
            'offset': ['offset', 'skip', 'start'],
            'page': ['page', 'pageNumber', 'page_number'],
            'cursor': ['cursor', 'next_cursor', 'continuation_token'],
            'link': ['next', 'next_url', 'next_link']
        }
        
        for ptype, keys in pagination_keys.items():
            for key in keys:
                if key in data:
                    pagination_hints['has_pagination'] = True
                    pagination_hints['pagination_type'] = ptype
                    pagination_hints['indicators'].append(key)
                    
        # Check for total count indicators
        count_keys = ['total', 'totalCount', 'total_count', 'count']
        for key in count_keys:
            if key in data:
                pagination_hints['total_count_key'] = key
                pagination_hints['total_count'] = data[key]
                
        return pagination_hints
        
    def _make_request(self, endpoint: APIEndpoint, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make API request with rate limiting"""
        url = f"{self.base_url}{endpoint.path}"
        
        # Merge parameters
        final_params = {}
        final_params.update(self.schema.global_params)
        final_params.update(endpoint.parameters)
        if params:
            final_params.update(params)
            
        try:
            response = self.session.request(
                method=endpoint.method,
                url=url,
                params=final_params,
                timeout=30
            )
            self.stats['api_calls'] += 1
            
            if response.status_code == 429:
                self.stats['rate_limits_hit'] += 1
                print(f"⚠️ Rate limited! Waiting...")
                time.sleep(10)
                return None
                
            return response
            
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
            
    def discover_data_hierarchy(self):
        """Discover relationships between endpoints"""
        print("\n🔗 Discovering data hierarchy...")
        
        hierarchy = defaultdict(list)
        
        # Analyze endpoint paths to find relationships
        for name, endpoint in self.schema.endpoints.items():
            parts = endpoint.path.strip('/').split('/')
            
            # Look for parent-child relationships
            if len(parts) >= 2:
                # Pattern: /parent/{id}/child
                if '{' in parts[-2] and '}' in parts[-2]:
                    parent = parts[-3] if len(parts) > 2 else 'root'
                    child = parts[-1]
                    hierarchy[parent].append(child)
                    
        self.schema.data_hierarchy = dict(hierarchy)
        
    def generate_collection_strategy(self) -> Dict[str, Any]:
        """Generate optimal collection strategy"""
        strategy = {
            'collection_order': [],
            'endpoint_strategies': {},
            'dependencies': defaultdict(list)
        }
        
        # Classify endpoints
        for name, endpoint in self.schema.endpoints.items():
            # Determine collection strategy
            if 'id' in endpoint.required_params or '{id}' in endpoint.path:
                endpoint.collection_strategy = 'sample'
            elif endpoint.pagination:
                endpoint.collection_strategy = 'paginated'
            else:
                endpoint.collection_strategy = 'complete'
                
            strategy['endpoint_strategies'][name] = {
                'strategy': endpoint.collection_strategy,
                'priority': self._calculate_priority(endpoint),
                'estimated_calls': self._estimate_api_calls(endpoint)
            }
            
        # Sort by priority
        sorted_endpoints = sorted(
            strategy['endpoint_strategies'].items(),
            key=lambda x: x[1]['priority'],
            reverse=True
        )
        
        strategy['collection_order'] = [ep[0] for ep in sorted_endpoints]
        
        return strategy
        
    def _calculate_priority(self, endpoint: APIEndpoint) -> int:
        """Calculate collection priority for an endpoint"""
        priority = 0
        
        # Foundation data gets highest priority
        foundation_indicators = ['sources', 'categories', 'tags', 'metadata']
        for indicator in foundation_indicators:
            if indicator in endpoint.path.lower():
                priority += 10
                
        # Complete collections get higher priority
        if endpoint.collection_strategy == 'complete':
            priority += 5
            
        # Endpoints with no dependencies get higher priority
        if not endpoint.required_params:
            priority += 3
            
        return priority
        
    def _estimate_api_calls(self, endpoint: APIEndpoint) -> int:
        """Estimate number of API calls needed"""
        if endpoint.collection_strategy == 'sample':
            return 1
        elif endpoint.collection_strategy == 'complete':
            return 1  # Assuming single call gets all data
        else:  # paginated
            # This would need to be refined based on actual data
            return 10  # Rough estimate
            
    def export_schema(self, output_path: str):
        """Export discovered schema to file"""
        schema_dict = {
            'api_name': self.schema.name,
            'base_url': self.schema.base_url,
            'version': self.schema.version,
            'discovered_at': datetime.now().isoformat(),
            'endpoints': {}
        }
        
        for name, endpoint in self.schema.endpoints.items():
            schema_dict['endpoints'][name] = {
                'path': endpoint.path,
                'method': endpoint.method,
                'description': endpoint.description,
                'parameters': endpoint.parameters,
                'required_params': endpoint.required_params,
                'optional_params': endpoint.optional_params,
                'data_key': endpoint.data_key,
                'pagination': endpoint.pagination,
                'collection_strategy': endpoint.collection_strategy
            }
            
        with open(output_path, 'w') as f:
            yaml.dump(schema_dict, f, default_flow_style=False)
            
        print(f"✅ Schema exported to: {output_path}")
        
    def generate_collection_code(self, output_dir: str):
        """Generate collection code for the API"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate main collector class
        collector_code = self._generate_collector_template()
        
        with open(os.path.join(output_dir, f"{self.api_name.lower()}_collector.py"), 'w') as f:
            f.write(collector_code)
            
        print(f"✅ Collection code generated in: {output_dir}")
        
    def _generate_collector_template(self) -> str:
        """Generate collector code template"""
        template = f'''#!/usr/bin/env python3
"""
Auto-generated collector for {self.api_name} API
Generated: {datetime.now().isoformat()}
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

class {self.api_name}Collector:
    def __init__(self, config: Dict[str, Any]):
        self.base_url = "{self.base_url}"
        self.config = config
        self.session = requests.Session()
        self.stats = {{
            'api_calls': 0,
            'records_collected': 0,
            'errors': 0,
            'start_time': datetime.now()
        }}
        
    def collect_all(self):
        """Collect data from all endpoints"""
        # Implementation based on discovered schema
        pass
'''
        return template


class GenericAPICollector:
    """Generic collector that works with any discovered API schema"""
    
    def __init__(self, schema_path: str, output_dir: str):
        with open(schema_path, 'r') as f:
            self.schema = yaml.safe_load(f)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def collect_endpoint(self, endpoint_name: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Collect data from a specific endpoint"""
        endpoint = self.schema['endpoints'].get(endpoint_name)
        if not endpoint:
            raise ValueError(f"Endpoint '{endpoint_name}' not found in schema")
            
        # Implementation would follow the patterns from FRED collector
        # but be generic enough to work with any API
        pass