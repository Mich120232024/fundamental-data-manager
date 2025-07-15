#!/usr/bin/env python3
"""
FRED Approved Schema Collector
Implements exact Delta Lake schema from research team analysis
Collects all 15 standard fields plus relationship mappings
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class FREDApprovedSchemaCollector:
    """Collects FRED metadata exactly matching approved Delta Lake schema"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"
        self.session = requests.Session()
        self.rate_limit_delay = 0.6  # Conservative rate limiting
        
        # Data structures matching Delta Lake tables
        self.fred_series = []
        self.fred_series_categories = []
        self.fred_series_tags = []
        self.fred_series_releases = []
        
        # Track unique entities
        self.categories_seen = set()
        self.tags_seen = set()
        self.releases_seen = set()
        
    def make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request with rate limiting and error handling"""
        time.sleep(self.rate_limit_delay)
        
        url = f"{self.base_url}/{endpoint}"
        params = {**params, 'api_key': self.api_key, 'file_type': 'json'}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Request failed for {endpoint}: {e}")
            return None
    
    def extract_series_metadata(self, series_data: Dict) -> Dict:
        """Extract exactly 15 standard fields matching approved schema"""
        collection_timestamp = datetime.utcnow().isoformat()
        
        return {
            'id': series_data.get('id'),
            'title': series_data.get('title'),
            'units': series_data.get('units'),
            'units_short': series_data.get('units_short'),
            'frequency': series_data.get('frequency'),
            'frequency_short': series_data.get('frequency_short'),
            'seasonal_adjustment': series_data.get('seasonal_adjustment'),
            'seasonal_adjustment_short': series_data.get('seasonal_adjustment_short'),
            'observation_start': series_data.get('observation_start'),
            'observation_end': series_data.get('observation_end'),
            'last_updated': series_data.get('last_updated'),
            'popularity': series_data.get('popularity'),
            'realtime_start': series_data.get('realtime_start'),
            'realtime_end': series_data.get('realtime_end'),
            'notes': series_data.get('notes'),
            'collection_timestamp': collection_timestamp
        }
    
    def collect_series_relationships(self, series_id: str):
        """Collect category, tag, and release relationships for a series"""
        
        # Collect categories
        categories_data = self.make_request(
            'series/categories',
            {'series_id': series_id}
        )
        if categories_data and 'categories' in categories_data:
            for category in categories_data['categories']:
                self.fred_series_categories.append({
                    'series_id': series_id,
                    'category_id': category['id']
                })
                self.categories_seen.add(category['id'])
        
        # Collect tags
        tags_data = self.make_request(
            'series/tags',
            {'series_id': series_id}
        )
        if tags_data and 'tags' in tags_data:
            for tag in tags_data['tags']:
                self.fred_series_tags.append({
                    'series_id': series_id,
                    'tag_name': tag['name'],
                    'group_id': tag.get('group_id', '')
                })
                self.tags_seen.add(tag['name'])
        
        # Collect releases
        releases_data = self.make_request(
            'series/release',
            {'series_id': series_id}
        )
        if releases_data and 'releases' in releases_data:
            for release in releases_data['releases']:
                self.fred_series_releases.append({
                    'series_id': series_id,
                    'release_id': release['id']
                })
                self.releases_seen.add(release['id'])
    
    def collect_category_series(self, category_id: int, max_series: int = None) -> List[str]:
        """Collect all series IDs from a category"""
        series_ids = []
        offset = 0
        limit = 1000  # FRED max
        
        while True:
            data = self.make_request(
                'category/series',
                {
                    'category_id': category_id,
                    'limit': limit,
                    'offset': offset
                }
            )
            
            if not data or 'seriess' not in data:
                break
                
            batch_series = data['seriess']
            for series in batch_series:
                series_ids.append(series['id'])
                # Extract metadata immediately
                metadata = self.extract_series_metadata(series)
                self.fred_series.append(metadata)
                
                if max_series and len(series_ids) >= max_series:
                    return series_ids[:max_series]
            
            if len(batch_series) < limit:
                break
                
            offset += limit
            logging.info(f"Category {category_id}: Collected {len(series_ids)} series...")
        
        return series_ids
    
    def collect_all_categories(self) -> Dict[int, Dict]:
        """Collect complete category tree"""
        categories = {}
        
        def collect_children(parent_id: int = 0):
            data = self.make_request(
                'category/children',
                {'category_id': parent_id}
            )
            
            if data and 'categories' in data:
                for category in data['categories']:
                    cat_id = category['id']
                    categories[cat_id] = category
                    # Recursively collect children
                    collect_children(cat_id)
        
        # Start from root
        collect_children(0)
        logging.info(f"Collected {len(categories)} categories")
        return categories
    
    def collect_full_metadata(self, target_series: int = None, categories_filter: List[int] = None):
        """
        Main collection method matching approved schema
        
        Args:
            target_series: Target number of series to collect (None = all)
            categories_filter: List of category IDs to collect from (None = all)
        """
        logging.info("Starting FRED metadata collection with approved schema")
        
        # Get all categories if not filtered
        if categories_filter is None:
            all_categories = self.collect_all_categories()
            categories_filter = list(all_categories.keys())
        
        total_series = 0
        
        for category_id in categories_filter:
            logging.info(f"Processing category {category_id}")
            
            # Collect series from category
            remaining = None
            if target_series:
                remaining = target_series - total_series
                if remaining <= 0:
                    break
            
            series_ids = self.collect_category_series(category_id, remaining)
            
            # Collect relationships for each series
            for series_id in series_ids:
                self.collect_series_relationships(series_id)
            
            total_series += len(series_ids)
            logging.info(f"Total series collected: {total_series}")
            
            if target_series and total_series >= target_series:
                break
        
        # Summary statistics
        self.print_collection_summary()
        
    def print_collection_summary(self):
        """Print collection statistics"""
        print("\n=== FRED Collection Summary ===")
        print(f"Series collected: {len(self.fred_series)}")
        print(f"Category relationships: {len(self.fred_series_categories)}")
        print(f"Tag relationships: {len(self.fred_series_tags)}")
        print(f"Release relationships: {len(self.fred_series_releases)}")
        print(f"Unique categories: {len(self.categories_seen)}")
        print(f"Unique tags: {len(self.tags_seen)}")
        print(f"Unique releases: {len(self.releases_seen)}")
        
        # Frequency distribution
        if self.fred_series:
            frequencies = {}
            for series in self.fred_series:
                freq = series.get('frequency', 'Unknown')
                frequencies[freq] = frequencies.get(freq, 0) + 1
            print("\nFrequency Distribution:")
            for freq, count in sorted(frequencies.items()):
                print(f"  {freq}: {count}")
    
    def save_to_delta_format(self, output_dir: str):
        """Save data in format ready for Delta Lake ingestion"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save each table as JSON (ready for Spark ingestion)
        tables = {
            'fred_series': self.fred_series,
            'fred_series_categories': self.fred_series_categories,
            'fred_series_tags': self.fred_series_tags,
            'fred_series_releases': self.fred_series_releases
        }
        
        for table_name, data in tables.items():
            output_path = os.path.join(output_dir, f"{table_name}.json")
            with open(output_path, 'w') as f:
                # Write as newline-delimited JSON for Spark
                for record in data:
                    f.write(json.dumps(record) + '\n')
            logging.info(f"Saved {len(data)} records to {output_path}")
        
        # Save collection metadata
        metadata = {
            'collection_timestamp': datetime.utcnow().isoformat(),
            'total_series': len(self.fred_series),
            'total_categories': len(self.categories_seen),
            'total_tags': len(self.tags_seen),
            'total_releases': len(self.releases_seen),
            'schema_version': '1.0',
            'schema_source': 'fred_metadata_schema_analysis.md'
        }
        
        with open(os.path.join(output_dir, 'collection_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\nData saved to {output_dir}/")


def main():
    """Example usage collecting sample data"""
    api_key = os.getenv('FRED_API_KEY')
    if not api_key:
        raise ValueError("FRED_API_KEY not found in environment variables")
    
    collector = FREDApprovedSchemaCollector(api_key)
    
    # Example: Collect 1000 series to test the process
    # For full collection, use: collector.collect_full_metadata()
    collector.collect_full_metadata(
        target_series=1000,  # Collect 1000 series as a test
        categories_filter=None  # Use all categories
    )
    
    # Save in Delta Lake ready format
    output_dir = '/Users/mikaeleage/Fred data collection/delta_lake_staging'
    collector.save_to_delta_format(output_dir)
    
    print("\nCollection complete! Data ready for Azure Synapse ingestion.")


if __name__ == "__main__":
    main()