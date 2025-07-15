#!/usr/bin/env python3
"""
FRED API Catalog - Cosmos DB Database Creation Script

This script creates the Cosmos DB database and containers for the FRED API catalog
with optimized schema, indexing, and partition key configuration.

Prerequisites:
- Azure Cosmos DB account created
- Connection string and key available
- Poetry environment with azure-cosmos package

Usage:
    python create_cosmos_database.py --cosmos-url <url> --cosmos-key <key>
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from typing import Dict, List
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosHttpResponseError

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cosmos_db_creation.log')
    ]
)
logger = logging.getLogger(__name__)

class FREDCosmosDBSetup:
    """Setup and configuration for FRED Cosmos DB"""
    
    def __init__(self, cosmos_url: str, cosmos_key: str, database_name: str = "fred-data"):
        """Initialize Cosmos DB client"""
        logger.info(f"Initializing Cosmos DB client for: {cosmos_url}")
        self.client = CosmosClient(cosmos_url, cosmos_key)
        self.database_name = database_name
        self.database = None
        
        # Container configurations with cost-optimized settings
        self.containers_config = {
            "fred-catalog": {
                "description": "Main catalog for categories, series, sources, releases, and tags",
                "partition_key": "/pk",
                "default_ttl": None,
                "offer_throughput": None,  # Use autoscale
                "max_throughput": 10000,   # Autoscale 1,000-10,000 RU/s
                "expected_size": "~1GB at full scale",
                "estimated_docs": "~840,000 documents",
                "indexing_policy": {
                    "automatic": True,
                    "indexingMode": "consistent",
                    "includedPaths": [
                        {"path": "/pk/?"},
                        {"path": "/type/?"},
                        {"path": "/parent_id/?"},
                        {"path": "/depth/?"},
                        {"path": "/name/?"},
                        {"path": "/category/id/?"},
                        {"path": "/metadata/frequency/?"},
                        {"path": "/metadata/last_updated/?"},
                        {"path": "/relationships/source_id/?"},
                        {"path": "/popularity/?"}
                    ],
                    "excludedPaths": [
                        {"path": "/children/*"},
                        {"path": "/ancestors/*"},
                        {"path": "/metadata/notes/?"},
                        {"path": "/relationships/tags/*"},
                        {"path": "/collection_metadata/*"},
                        {"path": "/_etag/?"}
                    ],
                    "compositeIndexes": [
                        [
                            {"path": "/parent_id", "order": "ascending"},
                            {"path": "/depth", "order": "ascending"}
                        ],
                        [
                            {"path": "/type", "order": "ascending"}, 
                            {"path": "/name", "order": "ascending"}
                        ],
                        [
                            {"path": "/category/id", "order": "ascending"},
                            {"path": "/metadata/frequency", "order": "ascending"}
                        ],
                        [
                            {"path": "/metadata/last_updated", "order": "descending"},
                            {"path": "/type", "order": "ascending"}
                        ]
                    ]
                }
            },
            "fred-observations": {
                "description": "Time series observation data with high volume capacity",
                "partition_key": "/series_id",
                "default_ttl": None,  # TTL managed per document for archival
                "offer_throughput": None,  # Use autoscale
                "max_throughput": 40000,   # Autoscale 4,000-40,000 RU/s
                "expected_size": "2-5TB potential",
                "estimated_docs": "~100M observations",
                "indexing_policy": {
                    "automatic": True,
                    "indexingMode": "consistent",
                    "includedPaths": [
                        {"path": "/series_id/?"},
                        {"path": "/date/?"},
                        {"path": "/value/?"},
                        {"path": "/realtime_start/?"},
                        {"path": "/realtime_end/?"}
                    ],
                    "excludedPaths": [
                        {"path": "/_etag/?"}
                    ],
                    "compositeIndexes": [
                        [
                            {"path": "/series_id", "order": "ascending"},
                            {"path": "/date", "order": "ascending"}
                        ],
                        [
                            {"path": "/series_id", "order": "ascending"},
                            {"path": "/realtime_start", "order": "descending"}
                        ]
                    ]
                }
            },
            "fred-updates": {
                "description": "Change tracking and audit trail with auto-cleanup",
                "partition_key": "/date", 
                "default_ttl": 7776000,  # 90 days TTL
                "offer_throughput": 400,  # Manual provisioning for predictable cost
                "max_throughput": None,
                "expected_size": "<100MB annually",
                "estimated_docs": "~50,000 update records/year",
                "indexing_policy": {
                    "automatic": True,
                    "indexingMode": "consistent",
                    "includedPaths": [
                        {"path": "/date/?"},
                        {"path": "/type/?"},
                        {"path": "/series_id/?"}
                    ],
                    "excludedPaths": [
                        {"path": "/*"}
                    ]
                }
            }
        }
    
    def create_database_and_containers(self) -> bool:
        """Create database and all containers with optimized configuration"""
        try:
            # Create database
            logger.info(f"Creating database: {self.database_name}")
            self.database = self.client.create_database_if_not_exists(self.database_name)
            logger.info(f"Database '{self.database_name}' ready")
            
            # Create containers
            for container_name, config in self.containers_config.items():
                success = self._create_container(container_name, config)
                if not success:
                    logger.error(f"Failed to create container: {container_name}")
                    return False
            
            # Print summary
            self._print_deployment_summary()
            
            logger.info("✅ Database and containers created successfully")
            return True
            
        except CosmosHttpResponseError as e:
            logger.error(f"❌ Failed to create database: {e}")
            return False
    
    def _create_container(self, container_name: str, config: Dict) -> bool:
        """Create a single container with specified configuration"""
        try:
            logger.info(f"Creating container: {container_name}")
            logger.info(f"  Description: {config['description']}")
            logger.info(f"  Partition Key: {config['partition_key']}")
            logger.info(f"  Expected Size: {config['expected_size']}")
            
            # Prepare container creation parameters
            create_params = {
                "id": container_name,
                "partition_key": PartitionKey(path=config["partition_key"]),
                "indexing_policy": config["indexing_policy"]
            }
            
            # Add TTL if specified
            if config.get("default_ttl") is not None:
                create_params["default_ttl"] = config["default_ttl"]
                logger.info(f"  TTL: {config['default_ttl']} seconds (90 days)")
            
            # Add throughput settings
            if config.get("offer_throughput"):
                create_params["offer_throughput"] = config["offer_throughput"]
                logger.info(f"  Throughput: {config['offer_throughput']} RU/s (manual)")
            elif config.get("max_throughput"):
                create_params["max_throughput"] = config["max_throughput"]
                min_throughput = config["max_throughput"] // 10
                logger.info(f"  Throughput: {min_throughput}-{config['max_throughput']} RU/s (autoscale)")
            
            # Create container
            container = self.database.create_container_if_not_exists(**create_params)
            
            logger.info(f"✅ Container '{container_name}' created successfully")
            return True
            
        except CosmosResourceExistsError:
            logger.info(f"✅ Container '{container_name}' already exists")
            return True
        except CosmosHttpResponseError as e:
            logger.error(f"❌ Failed to create container '{container_name}': {e}")
            return False
    
    def _print_deployment_summary(self):
        """Print deployment summary with cost estimates"""
        logger.info("\n" + "="*60)
        logger.info("FRED COSMOS DB DEPLOYMENT SUMMARY")
        logger.info("="*60)
        
        total_min_cost = 0
        total_max_cost = 0
        
        for container_name, config in self.containers_config.items():
            logger.info(f"\n📊 {container_name.upper()}")
            logger.info(f"   Purpose: {config['description']}")
            logger.info(f"   Partition: {config['partition_key']}")
            logger.info(f"   Size: {config['expected_size']}")
            logger.info(f"   Documents: {config['estimated_docs']}")
            
            # Cost estimation (rough)
            if config.get("offer_throughput"):
                ru = config["offer_throughput"]
                cost = ru * 0.008 * 24 * 30  # $0.008 per 100 RU/s per hour
                logger.info(f"   Cost: ~${cost:.0f}/month ({ru} RU/s manual)")
                total_min_cost += cost
                total_max_cost += cost
            elif config.get("max_throughput"):
                min_ru = config["max_throughput"] // 10
                max_ru = config["max_throughput"]
                min_cost = min_ru * 0.008 * 24 * 30
                max_cost = max_ru * 0.008 * 24 * 30
                logger.info(f"   Cost: ${min_cost:.0f}-${max_cost:.0f}/month ({min_ru}-{max_ru} RU/s autoscale)")
                total_min_cost += min_cost
                total_max_cost += max_cost
        
        logger.info(f"\n💰 TOTAL ESTIMATED COST: ${total_min_cost:.0f}-${total_max_cost:.0f}/month")
        logger.info(f"\n🎯 OPTIMIZATION RECOMMENDATIONS:")
        logger.info(f"   • Monitor RU consumption and adjust autoscale limits")
        logger.info(f"   • Enable reserved capacity for 30% cost savings")
        logger.info(f"   • Use analytical store for historical data analytics")
        logger.info(f"   • Implement data archival for older observations")
        logger.info("="*60)
    
    def validate_containers(self) -> bool:
        """Validate that all containers were created successfully"""
        try:
            logger.info("Validating container creation...")
            
            for container_name in self.containers_config.keys():
                container = self.database.get_container_client(container_name)
                container_properties = container.read()
                
                logger.info(f"✅ {container_name}: {container_properties['id']}")
                logger.info(f"   Partition Key: {container_properties['partitionKey']['paths'][0]}")
                
                # Check indexing policy
                indexing_policy = container_properties.get('indexingPolicy', {})
                included_paths = len(indexing_policy.get('includedPaths', []))
                excluded_paths = len(indexing_policy.get('excludedPaths', []))
                composite_indexes = len(indexing_policy.get('compositeIndexes', []))
                
                logger.info(f"   Indexing: {included_paths} included, {excluded_paths} excluded, {composite_indexes} composite")
            
            logger.info("✅ All containers validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Container validation failed: {e}")
            return False
    
    def insert_sample_data(self) -> bool:
        """Insert sample documents to test the schema"""
        try:
            logger.info("Inserting sample data for schema validation...")
            
            # Sample category document
            catalog_container = self.database.get_container_client("fred-catalog")
            
            sample_category = {
                "id": "test_category_32073",
                "pk": "test_category_32073",
                "name": "Population, Employment, & Labor Markets",
                "parent_id": "32263", 
                "depth": 2,
                "full_path": ["U.S. Regional Data", "Population, Employment, & Labor Markets"],
                "path_ids": ["32263", "32073"],
                "children": [{"id": "32445", "name": "States"}],
                "ancestors": [{"id": "32263", "name": "U.S. Regional Data", "depth": 1}],
                "descendants_count": 847,
                "series_count": 124,
                "last_updated": "2025-06-26T15:00:00Z",
                "type": "category"
            }
            
            catalog_container.upsert_item(sample_category)
            logger.info("✅ Sample category inserted")
            
            # Sample series document
            sample_series = {
                "id": "test_GDP",
                "pk": "test_GDP",
                "title": "Gross Domestic Product",
                "category": {
                    "id": "18",
                    "name": "National Accounts",
                    "full_path": ["National Accounts"]
                },
                "metadata": {
                    "frequency": "Quarterly",
                    "frequency_short": "Q",
                    "units": "Billions of Dollars",
                    "units_short": "Bil. of $",
                    "observation_start": "1947-01-01",
                    "observation_end": "2024-12-31",
                    "last_updated": "2025-06-26T08:30:00Z"
                },
                "relationships": {
                    "source_id": 1,
                    "source_name": "Board of Governors of the Federal Reserve System",
                    "release_id": 53,
                    "release_name": "Gross Domestic Product",
                    "tags": [
                        {"name": "gdp", "group": "concept"},
                        {"name": "quarterly", "group": "frequency"}
                    ]
                },
                "popularity": 100,
                "collection_metadata": {
                    "collected_at": "2025-06-26T15:00:00Z",
                    "collection_version": "1.0",
                    "checksum": "test123"
                },
                "type": "series"
            }
            
            catalog_container.upsert_item(sample_series)
            logger.info("✅ Sample series inserted")
            
            # Sample update document
            updates_container = self.database.get_container_client("fred-updates")
            
            sample_update = {
                "id": "test_update_001",
                "date": "2025-06-26",
                "type": "series_created",
                "series_id": "test_GDP",
                "details": {
                    "action": "initial_collection",
                    "timestamp": "2025-06-26T15:00:00Z"
                }
            }
            
            updates_container.upsert_item(sample_update)
            logger.info("✅ Sample update inserted")
            
            logger.info("✅ Sample data insertion completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sample data insertion failed: {e}")
            return False
    
    def cleanup_sample_data(self) -> bool:
        """Remove sample test documents"""
        try:
            logger.info("Cleaning up sample data...")
            
            catalog_container = self.database.get_container_client("fred-catalog")
            updates_container = self.database.get_container_client("fred-updates")
            
            # Delete sample documents
            catalog_container.delete_item("test_category_32073", partition_key="test_category_32073")
            catalog_container.delete_item("test_GDP", partition_key="test_GDP")
            updates_container.delete_item("test_update_001", partition_key="2025-06-26")
            
            logger.info("✅ Sample data cleaned up")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sample data cleanup failed: {e}")
            return False

def main():
    """Main function to create FRED Cosmos DB"""
    parser = argparse.ArgumentParser(description="Create FRED API Catalog Cosmos DB")
    parser.add_argument("--cosmos-url", required=True, help="Cosmos DB URL")
    parser.add_argument("--cosmos-key", required=True, help="Cosmos DB Key")
    parser.add_argument("--database-name", default="fred-data", help="Database name")
    parser.add_argument("--validate", action="store_true", help="Validate containers after creation")
    parser.add_argument("--test-data", action="store_true", help="Insert and cleanup test data")
    
    args = parser.parse_args()
    
    # Initialize setup
    setup = FREDCosmosDBSetup(
        cosmos_url=args.cosmos_url,
        cosmos_key=args.cosmos_key,
        database_name=args.database_name
    )
    
    # Create database and containers
    if not setup.create_database_and_containers():
        logger.error("Failed to create database and containers")
        sys.exit(1)
    
    # Validate if requested
    if args.validate:
        if not setup.validate_containers():
            logger.error("Container validation failed")
            sys.exit(1)
    
    # Test with sample data if requested
    if args.test_data:
        if not setup.insert_sample_data():
            logger.error("Sample data insertion failed")
            sys.exit(1)
        
        if not setup.cleanup_sample_data():
            logger.error("Sample data cleanup failed")
            sys.exit(1)
    
    logger.info("🎉 FRED Cosmos DB setup completed successfully!")
    logger.info(f"Database: {args.database_name}")
    logger.info("Next steps:")
    logger.info("1. Load FRED foundation data from JSON files")
    logger.info("2. Configure change feed for real-time updates")
    logger.info("3. Set up monitoring and alerting")
    logger.info("4. Test query performance and optimize")

if __name__ == "__main__":
    main()