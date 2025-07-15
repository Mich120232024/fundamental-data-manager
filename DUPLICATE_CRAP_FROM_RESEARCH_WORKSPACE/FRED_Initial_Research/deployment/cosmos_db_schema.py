#!/usr/bin/env python3
"""
FRED API Catalog - Cosmos DB Schema and Container Setup

This module implements the optimized Cosmos DB schema for FRED API catalog
based on best practices for hierarchical data and analytical workloads.

Schema Design:
- Multi-container architecture for optimal performance
- Optimized partition keys for even distribution
- Denormalized hierarchy for efficient traversal
- Selective indexing for cost optimization
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosHttpResponseError
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FREDCosmosDB:
    """FRED API Catalog Cosmos DB Implementation"""
    
    def __init__(self, cosmos_url: str, cosmos_key: str, database_name: str = "fred-data"):
        """Initialize Cosmos DB client and database"""
        self.client = CosmosClient(cosmos_url, cosmos_key)
        self.database_name = database_name
        self.database = None
        
        # Container configurations
        self.containers_config = {
            "fred-catalog": {
                "partition_key": "/pk",
                "default_ttl": None,  # No TTL for catalog data
                "ru_settings": {"max_throughput": 10000},  # Autoscale 1,000-10,000 RU/s
                "indexing_policy": self._get_catalog_indexing_policy()
            },
            "fred-observations": {
                "partition_key": "/series_id", 
                "default_ttl": None,  # TTL per document for archival
                "ru_settings": {"max_throughput": 40000},  # Autoscale 4,000-40,000 RU/s
                "indexing_policy": self._get_observations_indexing_policy()
            },
            "fred-updates": {
                "partition_key": "/date",
                "default_ttl": 7776000,  # 90 days TTL
                "ru_settings": {"offer_throughput": 400},  # Manual 400 RU/s
                "indexing_policy": self._get_updates_indexing_policy()
            }
        }
    
    def _get_catalog_indexing_policy(self) -> Dict:
        """Optimized indexing policy for catalog container"""
        return {
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
    
    def _get_observations_indexing_policy(self) -> Dict:
        """Optimized indexing policy for observations container"""
        return {
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
    
    def _get_updates_indexing_policy(self) -> Dict:
        """Minimal indexing policy for updates container"""
        return {
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
    
    async def initialize_database(self) -> bool:
        """Create database and containers with optimized configuration"""
        try:
            # Create database
            logger.info(f"Creating database: {self.database_name}")
            self.database = self.client.create_database_if_not_exists(self.database_name)
            
            # Create containers
            for container_name, config in self.containers_config.items():
                await self._create_container(container_name, config)
            
            logger.info("Database and containers initialized successfully")
            return True
            
        except CosmosHttpResponseError as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
    
    async def _create_container(self, container_name: str, config: Dict) -> None:
        """Create a container with specified configuration"""
        try:
            logger.info(f"Creating container: {container_name}")
            
            container = self.database.create_container_if_not_exists(
                id=container_name,
                partition_key=PartitionKey(path=config["partition_key"]),
                indexing_policy=config["indexing_policy"],
                default_ttl=config.get("default_ttl"),
                **config["ru_settings"]
            )
            
            logger.info(f"Container {container_name} created successfully")
            
        except CosmosResourceExistsError:
            logger.info(f"Container {container_name} already exists")
        except CosmosHttpResponseError as e:
            logger.error(f"Failed to create container {container_name}: {e}")
            raise

class FREDCategoryDocument:
    """Schema for FRED category documents"""
    
    @staticmethod
    def create(category_data: Dict) -> Dict:
        """Create optimized category document"""
        return {
            "id": str(category_data["id"]),
            "pk": str(category_data["id"]),  # Partition key = id
            "name": category_data["name"],
            "parent_id": str(category_data.get("parent_id", "")),
            "depth": category_data.get("depth", 0),
            "full_path": category_data.get("full_path", []),
            "path_ids": category_data.get("path_ids", []),
            "children": category_data.get("children", []),
            "ancestors": category_data.get("ancestors", []),
            "descendants_count": category_data.get("descendants_count", 0),
            "series_count": category_data.get("series_count", 0),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "type": "category"
        }

class FREDSeriesDocument:
    """Schema for FRED series documents"""
    
    @staticmethod 
    def create(series_data: Dict) -> Dict:
        """Create optimized series document"""
        return {
            "id": series_data["id"],
            "pk": series_data["id"],  # Partition key = series_id
            "title": series_data.get("title", ""),
            "category": {
                "id": str(series_data.get("category_id", "")),
                "name": series_data.get("category_name", ""),
                "full_path": series_data.get("category_path", [])
            },
            "metadata": {
                "frequency": series_data.get("frequency", ""),
                "frequency_short": series_data.get("frequency_short", ""),
                "units": series_data.get("units", ""),
                "units_short": series_data.get("units_short", ""),
                "seasonal_adjustment": series_data.get("seasonal_adjustment", ""),
                "seasonal_adjustment_short": series_data.get("seasonal_adjustment_short", ""),
                "observation_start": series_data.get("observation_start", ""),
                "observation_end": series_data.get("observation_end", ""),
                "last_updated": series_data.get("last_updated", ""),
                "realtime_start": series_data.get("realtime_start", ""),
                "realtime_end": series_data.get("realtime_end", "")
            },
            "relationships": {
                "source_id": series_data.get("source_id"),
                "source_name": series_data.get("source_name", ""),
                "release_id": series_data.get("release_id"),
                "release_name": series_data.get("release_name", ""),
                "tags": series_data.get("tags", [])
            },
            "popularity": series_data.get("popularity", 0),
            "collection_metadata": {
                "collected_at": datetime.utcnow().isoformat() + "Z",
                "collection_version": "1.0",
                "checksum": series_data.get("checksum", "")
            },
            "type": "series"
        }

class FREDSourceDocument:
    """Schema for FRED source documents"""
    
    @staticmethod
    def create(source_data: Dict) -> Dict:
        """Create optimized source document"""
        return {
            "id": str(source_data["id"]),
            "pk": str(source_data["id"]),
            "name": source_data.get("name", ""),
            "link": source_data.get("link", ""),
            "notes": source_data.get("notes", ""),
            "realtime_start": source_data.get("realtime_start", ""),
            "realtime_end": source_data.get("realtime_end", ""),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "type": "source"
        }

class FREDReleaseDocument:
    """Schema for FRED release documents"""
    
    @staticmethod
    def create(release_data: Dict) -> Dict:
        """Create optimized release document"""
        return {
            "id": str(release_data["id"]),
            "pk": str(release_data["id"]),
            "name": release_data.get("name", ""),
            "press_release": release_data.get("press_release", False),
            "link": release_data.get("link", ""),
            "notes": release_data.get("notes", ""),
            "realtime_start": release_data.get("realtime_start", ""),
            "realtime_end": release_data.get("realtime_end", ""),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "type": "release"
        }

class FREDTagDocument:
    """Schema for FRED tag documents"""
    
    @staticmethod
    def create(tag_data: Dict) -> Dict:
        """Create optimized tag document"""
        return {
            "id": tag_data["name"],  # Use tag name as ID
            "pk": tag_data["name"],
            "name": tag_data["name"],
            "group_id": tag_data.get("group_id", ""),
            "notes": tag_data.get("notes", ""),
            "created": tag_data.get("created", ""),
            "popularity": tag_data.get("popularity", 0),
            "series_count": tag_data.get("series_count", 0),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "type": "tag"
        }

# Sample usage and testing
if __name__ == "__main__":
    # Configuration from environment variables
    COSMOS_URL = os.getenv("COSMOS_URL", "https://your-cosmos-account.documents.azure.com:443/")
    COSMOS_KEY = os.getenv("COSMOS_KEY", "your-cosmos-key")
    
    # Initialize Cosmos DB
    fred_cosmos = FREDCosmosDB(COSMOS_URL, COSMOS_KEY)
    
    # Example category document
    sample_category = {
        "id": 32073,
        "name": "Population, Employment, & Labor Markets",
        "parent_id": 32263,
        "depth": 2,
        "full_path": ["U.S. Regional Data", "Population, Employment, & Labor Markets"],
        "path_ids": ["32263", "32073"],
        "children": [{"id": "32445", "name": "States"}],
        "ancestors": [{"id": "32263", "name": "U.S. Regional Data", "depth": 1}],
        "descendants_count": 847,
        "series_count": 124
    }
    
    # Create category document
    category_doc = FREDCategoryDocument.create(sample_category)
    print("Sample Category Document:")
    print(json.dumps(category_doc, indent=2))
    
    # Example series document  
    sample_series = {
        "id": "GDP",
        "title": "Gross Domestic Product",
        "category_id": 18,
        "category_name": "National Accounts",
        "frequency": "Quarterly",
        "frequency_short": "Q",
        "units": "Billions of Dollars",
        "units_short": "Bil. of $",
        "observation_start": "1947-01-01",
        "observation_end": "2024-12-31",
        "last_updated": "2025-06-26T08:30:00Z",
        "source_id": 1,
        "source_name": "Board of Governors of the Federal Reserve System",
        "popularity": 100
    }
    
    # Create series document
    series_doc = FREDSeriesDocument.create(sample_series)
    print("\nSample Series Document:")
    print(json.dumps(series_doc, indent=2))