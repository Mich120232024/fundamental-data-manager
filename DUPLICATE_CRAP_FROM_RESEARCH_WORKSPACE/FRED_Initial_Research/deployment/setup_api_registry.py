#!/usr/bin/env python3
"""
API Registry Setup - Deploy api_registry container to existing Cosmos DB

Uses the schema defined in api_registry_cosmos_schema.py to create
the api_registry container in the existing research-analytics-db.
"""

import os
import sys
import json
import logging
from datetime import datetime
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosHttpResponseError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for schema imports
sys.path.append('/Users/mikaeleage/Research & Analytics Services')
from api_registry_cosmos_schema import APICategory, APIAuthType, APIStatus

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIRegistrySetup:
    """Setup API Registry container in existing Cosmos DB"""
    
    def __init__(self, cosmos_url: str, cosmos_key: str):
        """Initialize with existing database connection"""
        self.client = CosmosClient(cosmos_url, cosmos_key)
        self.database_name = "research-analytics-db"  # Existing database
        self.container_name = "api_registry"          # New container
        self.database = None
        self.container = None
    
    def setup_api_registry_container(self) -> bool:
        """Create api_registry container with optimized schema"""
        try:
            logger.info("🚀 Setting up API Registry in existing Cosmos DB")
            
            # Get existing database
            logger.info(f"Connecting to existing database: {self.database_name}")
            self.database = self.client.get_database_client(self.database_name)
            
            # Create api_registry container
            logger.info(f"Creating container: {self.container_name}")
            
            container_config = {
                "id": self.container_name,
                "partition_key": PartitionKey(path="/category"),  # As per schema design
                # Note: Serverless account - no throughput configuration needed
                "indexing_policy": self._get_optimized_indexing_policy()
            }
            
            self.container = self.database.create_container_if_not_exists(**container_config)
            logger.info(f"✅ Container '{self.container_name}' created successfully")
            
            # Print setup summary
            self._print_setup_info()
            
            return True
            
        except CosmosHttpResponseError as e:
            logger.error(f"❌ Container setup failed: {e}")
            return False
    
    def _get_optimized_indexing_policy(self) -> dict:
        """Schema-based indexing policy for table-like queries"""
        return {
            "automatic": True,
            "indexingMode": "consistent",
            "includedPaths": [
                {"path": "/*"}    # Include all paths by default
            ],
            "excludedPaths": [
                # Large text fields and arrays
                {"path": "/endpoints/*"},       # Entire endpoints array
                {"path": "/documentation/*"},   # Documentation array
                {"path": "/usage/*"},          # Usage examples
                {"path": "/notes/?"},          # Large notes field
                
                # System fields
                {"path": "/_etag/?"},
                {"path": "/_ts/?"}
            ],
            "compositeIndexes": [
                # Table-like queries
                [
                    {"path": "/category", "order": "ascending"},
                    {"path": "/apiName", "order": "ascending"}
                ],
                [
                    {"path": "/status", "order": "ascending"},
                    {"path": "/usageMetrics/popularity", "order": "descending"}
                ],
                [
                    {"path": "/pricing/model", "order": "ascending"},
                    {"path": "/authType", "order": "ascending"}
                ],
                # Agent discovery patterns
                [
                    {"path": "/category", "order": "ascending"},
                    {"path": "/usageMetrics/reliability", "order": "descending"}
                ]
            ]
        }
    
    def _print_setup_info(self):
        """Print setup information and usage examples"""
        logger.info("\n" + "="*60)
        logger.info("API REGISTRY CONTAINER SETUP COMPLETE")
        logger.info("="*60)
        logger.info(f"📊 Database: {self.database_name}")
        logger.info(f"📊 Container: {self.container_name}")
        logger.info(f"📊 Partition Key: /category")
        logger.info(f"📊 Serverless: Pay-per-request pricing")
        logger.info(f"📊 Expected APIs: 500")
        
        logger.info(f"\n🗂️  TABLE-LIKE QUERY EXAMPLES:")
        logger.info(f"   • SELECT * FROM c WHERE c.category = 'financial'")
        logger.info(f"   • SELECT * FROM c WHERE c.pricing.model = 'free'")
        logger.info(f"   • SELECT * FROM c WHERE c.status = 'active'")
        logger.info(f"   • SELECT * FROM c WHERE c.authType = 'api_key'")
        
        logger.info(f"\n🔍 AGENT DISCOVERY PATTERNS:")
        logger.info(f"   • Search by category and reliability")
        logger.info(f"   • Filter by authentication type")
        logger.info(f"   • Sort by popularity scores")
        logger.info(f"   • Find free vs paid APIs")
        
        logger.info("="*60)
    
    def validate_container_setup(self) -> bool:
        """Validate container creation and indexing"""
        try:
            logger.info("🔍 Validating container setup...")
            
            # Check container properties
            container_properties = self.container.read()
            logger.info(f"✅ Container ID: {container_properties['id']}")
            logger.info(f"✅ Partition Key: {container_properties['partitionKey']['paths'][0]}")
            
            # Check indexing policy
            indexing_policy = container_properties.get('indexingPolicy', {})
            included_paths = len(indexing_policy.get('includedPaths', []))
            excluded_paths = len(indexing_policy.get('excludedPaths', []))
            composite_indexes = len(indexing_policy.get('compositeIndexes', []))
            
            logger.info(f"✅ Indexing: {included_paths} included paths")
            logger.info(f"✅ Indexing: {excluded_paths} excluded paths") 
            logger.info(f"✅ Indexing: {composite_indexes} composite indexes")
            
            logger.info("✅ Container validation complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Container validation failed: {e}")
            return False
    
    def insert_sample_api(self) -> bool:
        """Insert sample API document to test schema"""
        try:
            logger.info("📝 Inserting sample API document...")
            
            # Sample API document following the schema
            sample_api = {
                "id": "api_sample_001",
                "category": "financial",  # Partition key
                "apiName": "Sample Financial API",
                "provider": "Test Provider",
                "version": "v1.0",
                "description": "Sample financial data API for testing",
                "baseUrl": "https://api.sample.com/v1",
                "authType": "api_key",
                "protocol": "REST",
                "dataFormat": "JSON",
                "status": "active",
                "tags": ["finance", "market-data", "real-time"],
                
                "pricing": {
                    "model": "freemium",
                    "currency": "USD",
                    "baseCost": 0,
                    "tiers": [
                        {
                            "name": "free",
                            "requestsPerMonth": 1000,
                            "cost": 0
                        }
                    ]
                },
                
                "usageMetrics": {
                    "popularity": 85,
                    "reliability": 99.5,
                    "averageResponseTime": 250,
                    "monthlyUsers": 1500,
                    "lastChecked": datetime.utcnow().isoformat() + "Z"
                },
                
                "endpoints": [
                    {
                        "path": "/quotes",
                        "method": "GET",
                        "description": "Get stock quotes",
                        "parameters": [
                            {
                                "name": "symbol",
                                "type": "string",
                                "required": True,
                                "description": "Stock symbol"
                            }
                        ]
                    }
                ],
                
                "compliance": ["SOC2", "GDPR"],
                "regional": {
                    "global": True,
                    "regions": ["US", "EU", "APAC"]
                },
                
                "createdAt": datetime.utcnow().isoformat() + "Z",
                "lastModified": datetime.utcnow().isoformat() + "Z"
            }
            
            # Insert document
            result = self.container.upsert_item(sample_api)
            logger.info(f"✅ Sample API inserted with ID: {result['id']}")
            
            # Test table-like query
            query = "SELECT * FROM c WHERE c.category = 'financial'"
            results = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            logger.info(f"✅ Query test: Found {len(results)} financial APIs")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Sample data insertion failed: {e}")
            return False
    
    def cleanup_sample_data(self) -> bool:
        """Remove sample test data"""
        try:
            logger.info("🧹 Cleaning up sample data...")
            self.container.delete_item("api_sample_001", partition_key="financial")
            logger.info("✅ Sample data cleaned up")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sample data cleanup failed: {e}")
            return False

def main():
    """Setup API Registry container"""
    # Get credentials from environment
    cosmos_url = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    
    if not cosmos_url or not cosmos_key:
        print("❌ Missing COSMOS_ENDPOINT or COSMOS_KEY environment variables")
        print("Check your .env file configuration")
        return False
    
    # Setup API Registry
    setup = APIRegistrySetup(cosmos_url, cosmos_key)
    
    if not setup.setup_api_registry_container():
        print("❌ Container setup failed")
        return False
    
    if not setup.validate_container_setup():
        print("❌ Container validation failed")
        return False
    
    # Test with sample data
    if not setup.insert_sample_api():
        print("❌ Sample data test failed")
        return False
    
    if not setup.cleanup_sample_data():
        print("❌ Sample data cleanup failed")
        return False
    
    print("🎉 API Registry container setup complete!")
    print("📄 Ready for 500 API data loading")
    print(f"📊 Container: api_registry in {setup.database_name}")
    
    return True

if __name__ == "__main__":
    main()