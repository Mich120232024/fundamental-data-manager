#!/usr/bin/env python3
"""
FRED API Catalog - Single Container Deployment

Deploy new Cosmos DB database with fred-catalog container for API metadata.
Designed to be read as table structure through interface for data collection.

This implements the API catalog agreed with HEAD_OF_RESEARCH and documented in team agenda.
"""

import json
import logging
import os
from datetime import datetime
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosHttpResponseError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FREDCatalogDeployment:
    """Deploy FRED API Catalog as table-structured Cosmos DB container"""
    
    def __init__(self, cosmos_url: str, cosmos_key: str):
        """Initialize Cosmos DB client"""
        self.client = CosmosClient(cosmos_url, cosmos_key)
        self.database_name = "fred-api-catalog"
        self.container_name = "fred-catalog"
        self.database = None
        self.container = None
    
    def deploy_database_and_container(self) -> bool:
        """Deploy new database with fred-catalog container"""
        try:
            logger.info("🚀 Deploying FRED API Catalog Database")
            
            # Create database
            logger.info(f"Creating database: {self.database_name}")
            self.database = self.client.create_database_if_not_exists(self.database_name)
            logger.info(f"✅ Database '{self.database_name}' ready")
            
            # Create fred-catalog container with table structure design
            logger.info(f"Creating container: {self.container_name}")
            
            container_config = {
                "id": self.container_name,
                "partition_key": PartitionKey(path="/pk"),
                "max_throughput": 4000,  # Autoscale 400-4000 RU/s for catalog
                "indexing_policy": {
                    "automatic": True,
                    "indexingMode": "consistent",
                    "includedPaths": [
                        {"path": "/pk/?"},           # Partition key
                        {"path": "/type/?"},         # Document type for table queries
                        {"path": "/id/?"},           # Primary identifier
                        {"path": "/name/?"},         # Name field for all entities
                        {"path": "/parent_id/?"},    # Category hierarchy
                        {"path": "/depth/?"},        # Category depth
                        {"path": "/frequency/?"},    # Series frequency
                        {"path": "/source_id/?"},    # Source relationships
                        {"path": "/popularity/?"},   # Series popularity
                        {"path": "/last_updated/?"}  # Update tracking
                    ],
                    "excludedPaths": [
                        {"path": "/notes/?"},           # Large text fields
                        {"path": "/children/*"},        # Array content
                        {"path": "/ancestors/*"},       # Array content  
                        {"path": "/tags/*"},           # Tag arrays
                        {"path": "/_etag/?"}           # System fields
                    ],
                    "compositeIndexes": [
                        [
                            {"path": "/type", "order": "ascending"},
                            {"path": "/name", "order": "ascending"}
                        ],
                        [
                            {"path": "/parent_id", "order": "ascending"},
                            {"path": "/depth", "order": "ascending"}
                        ],
                        [
                            {"path": "/type", "order": "ascending"},
                            {"path": "/frequency", "order": "ascending"}
                        ]
                    ]
                }
            }
            
            self.container = self.database.create_container_if_not_exists(**container_config)
            logger.info(f"✅ Container '{self.container_name}' created successfully")
            
            # Print deployment summary
            self._print_deployment_info()
            
            return True
            
        except CosmosHttpResponseError as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False
    
    def _print_deployment_info(self):
        """Print deployment information and table structure"""
        logger.info("\n" + "="*60)
        logger.info("FRED API CATALOG DEPLOYMENT COMPLETE")
        logger.info("="*60)
        logger.info(f"📊 Database: {self.database_name}")
        logger.info(f"📊 Container: {self.container_name}")
        logger.info(f"📊 Partition Key: /pk")
        logger.info(f"📊 Throughput: 400-4000 RU/s (autoscale)")
        logger.info(f"📊 Expected Cost: ~$32-320/month")
        
        logger.info(f"\n🗂️  TABLE STRUCTURE FOR INTERFACE:")
        logger.info(f"   ├── Categories (5,183 records)")
        logger.info(f"   ├── Series (~830,000 records)")  
        logger.info(f"   ├── Sources (117 records)")
        logger.info(f"   ├── Releases (326 records)")
        logger.info(f"   └── Tags (8,000+ records)")
        
        logger.info(f"\n🔍 QUERY PATTERNS:")
        logger.info(f"   • SELECT * FROM c WHERE c.type = 'category'")
        logger.info(f"   • SELECT * FROM c WHERE c.type = 'series' AND c.frequency = 'Monthly'")
        logger.info(f"   • SELECT * FROM c WHERE c.parent_id = '32073'")
        logger.info(f"   • SELECT * FROM c WHERE c.source_id = 1")
        
        logger.info("="*60)
    
    def insert_foundation_data(self, data_dir: str) -> bool:
        """Load FRED foundation data into catalog container"""
        try:
            logger.info("📥 Loading FRED foundation data...")
            
            # Load categories
            categories_file = os.path.join(data_dir, "categories", "categories_complete_hierarchy.json")
            if os.path.exists(categories_file):
                with open(categories_file, 'r') as f:
                    categories_data = json.load(f)
                    
                # Convert to table-structured documents
                category_count = 0
                for cat_id, cat_data in categories_data.items():
                    doc = {
                        "id": f"category_{cat_id}",
                        "pk": f"category_{cat_id}",
                        "type": "category",
                        "category_id": int(cat_id),
                        "name": cat_data.get("name", ""),
                        "parent_id": cat_data.get("parent_id", ""),
                        "depth": cat_data.get("depth", 0),
                        "children_count": len(cat_data.get("children", [])),
                        "last_updated": datetime.utcnow().isoformat() + "Z"
                    }
                    
                    self.container.upsert_item(doc)
                    category_count += 1
                    
                    if category_count % 100 == 0:
                        logger.info(f"   Loaded {category_count} categories...")
                
                logger.info(f"✅ Loaded {category_count} categories")
            
            # Load sources
            sources_file = os.path.join(data_dir, "sources", "sources_all.json")
            if os.path.exists(sources_file):
                with open(sources_file, 'r') as f:
                    sources_data = json.load(f)
                    
                source_count = 0
                for source in sources_data.get("sources", []):
                    doc = {
                        "id": f"source_{source['id']}",
                        "pk": f"source_{source['id']}",
                        "type": "source",
                        "source_id": source["id"],
                        "name": source.get("name", ""),
                        "link": source.get("link", ""),
                        "last_updated": datetime.utcnow().isoformat() + "Z"
                    }
                    
                    self.container.upsert_item(doc)
                    source_count += 1
                
                logger.info(f"✅ Loaded {source_count} sources")
            
            # Load releases
            releases_file = os.path.join(data_dir, "sources", "releases_all.json")
            if os.path.exists(releases_file):
                with open(releases_file, 'r') as f:
                    releases_data = json.load(f)
                    
                release_count = 0
                for release in releases_data.get("releases", []):
                    doc = {
                        "id": f"release_{release['id']}",
                        "pk": f"release_{release['id']}",
                        "type": "release",
                        "release_id": release["id"],
                        "name": release.get("name", ""),
                        "link": release.get("link", ""),
                        "press_release": release.get("press_release", False),
                        "last_updated": datetime.utcnow().isoformat() + "Z"
                    }
                    
                    self.container.upsert_item(doc)
                    release_count += 1
                
                logger.info(f"✅ Loaded {release_count} releases")
            
            # Load sample series metadata
            series_file = os.path.join(data_dir, "metadata", "sample_150_series_complete.json")
            if os.path.exists(series_file):
                with open(series_file, 'r') as f:
                    series_data = json.load(f)
                    
                series_count = 0
                for series in series_data.get("series", []):
                    doc = {
                        "id": f"series_{series['id']}",
                        "pk": f"series_{series['id']}",
                        "type": "series",
                        "series_id": series["id"],
                        "name": series.get("title", ""),
                        "title": series.get("title", ""),
                        "frequency": series.get("frequency", ""),
                        "frequency_short": series.get("frequency_short", ""),
                        "units": series.get("units", ""),
                        "units_short": series.get("units_short", ""),
                        "observation_start": series.get("observation_start", ""),
                        "observation_end": series.get("observation_end", ""),
                        "popularity": series.get("popularity", 0),
                        "last_updated": series.get("last_updated", ""),
                        "source_id": series.get("source_id", ""),
                        "release_id": series.get("release_id", "")
                    }
                    
                    self.container.upsert_item(doc)
                    series_count += 1
                
                logger.info(f"✅ Loaded {series_count} sample series")
            
            logger.info("🎉 Foundation data loading complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Foundation data loading failed: {e}")
            return False
    
    def validate_table_structure(self) -> bool:
        """Validate that data can be queried as table structure"""
        try:
            logger.info("🔍 Validating table structure queries...")
            
            # Test table-style queries
            queries = [
                ("Categories", "SELECT * FROM c WHERE c.type = 'category'"),
                ("Series", "SELECT * FROM c WHERE c.type = 'series'"),
                ("Sources", "SELECT * FROM c WHERE c.type = 'source'"),
                ("Releases", "SELECT * FROM c WHERE c.type = 'release'"),
                ("Category by depth", "SELECT * FROM c WHERE c.type = 'category' AND c.depth = 2"),
                ("Series by frequency", "SELECT * FROM c WHERE c.type = 'series' AND c.frequency = 'Monthly'")
            ]
            
            for query_name, query in queries:
                items = list(self.container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ))
                logger.info(f"   {query_name}: {len(items)} records")
            
            logger.info("✅ Table structure validation complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Table structure validation failed: {e}")
            return False
    
    def generate_interface_documentation(self) -> str:
        """Generate documentation for interface integration"""
        docs = f"""
# FRED API Catalog - Interface Integration

## Database Connection
- **Database**: {self.database_name}
- **Container**: {self.container_name}
- **Partition Key**: /pk

## Table Structure

### Categories Table (type = 'category')
```sql
SELECT category_id, name, parent_id, depth, children_count 
FROM c WHERE c.type = 'category'
```

### Series Table (type = 'series')  
```sql
SELECT series_id, title, frequency, units, observation_start, observation_end, popularity
FROM c WHERE c.type = 'series'
```

### Sources Table (type = 'source')
```sql
SELECT source_id, name, link
FROM c WHERE c.type = 'source'
```

### Releases Table (type = 'release')
```sql
SELECT release_id, name, link, press_release
FROM c WHERE c.type = 'release'
```

## Common Interface Queries

### Get all categories for dropdown
```sql
SELECT c.category_id, c.name, c.parent_id 
FROM c WHERE c.type = 'category' 
ORDER BY c.name
```

### Get series by category
```sql
SELECT c.series_id, c.title, c.frequency, c.units
FROM c WHERE c.type = 'series' AND c.category_id = @categoryId
```

### Get category hierarchy
```sql
SELECT c.category_id, c.name, c.depth, c.parent_id
FROM c WHERE c.type = 'category' AND c.parent_id = @parentId
ORDER BY c.name
```

Ready for interface integration!
"""
        return docs

def main():
    """Deploy FRED API Catalog"""
    # Get credentials from environment or prompt
    cosmos_url = os.getenv("COSMOS_URL")
    cosmos_key = os.getenv("COSMOS_KEY")
    
    if not cosmos_url or not cosmos_key:
        print("❌ Missing COSMOS_URL or COSMOS_KEY environment variables")
        print("Set these in your .env file or environment")
        return False
    
    # Deploy catalog
    deployment = FREDCatalogDeployment(cosmos_url, cosmos_key)
    
    if not deployment.deploy_database_and_container():
        print("❌ Deployment failed")
        return False
    
    # Load foundation data
    data_dir = "../data"
    if not deployment.insert_foundation_data(data_dir):
        print("❌ Data loading failed")
        return False
    
    # Validate table structure
    if not deployment.validate_table_structure():
        print("❌ Validation failed")
        return False
    
    # Generate interface docs
    interface_docs = deployment.generate_interface_documentation()
    with open("INTERFACE_INTEGRATION.md", "w") as f:
        f.write(interface_docs)
    
    print("🎉 FRED API Catalog deployment complete!")
    print("📄 Interface documentation saved to INTERFACE_INTEGRATION.md")
    
    return True

if __name__ == "__main__":
    main()