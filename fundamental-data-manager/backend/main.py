#!/usr/bin/env python3
"""
Fundamental Data Manager - FastAPI Backend
Port: 8850 (dedicated port to avoid conflicts)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uvicorn
from azure.cosmos import CosmosClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_PORT = 8850  # Dedicated port for this service
COSMOS_ENDPOINT = os.getenv('COSMOS_ENDPOINT', 'https://cosmos-research-analytics-prod.documents.azure.com:443/')
COSMOS_KEY = os.getenv('COSMOS_KEY')

# Check if Cosmos key is provided
if not COSMOS_KEY:
    raise ValueError("COSMOS_KEY environment variable must be set")

app = FastAPI(
    title="Fundamental Data Manager API",
    description="Production API for managing and visualizing fundamental economic data",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3850", "http://localhost:3851"],  # React dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Cosmos DB client
cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Fundamental Data Manager API",
        "status": "running",
        "port": API_PORT,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/catalog")
async def get_api_catalog():
    """Get all API entries from Cosmos DB catalog"""
    try:
        database = cosmos_client.get_database_client("data-collection-db")
        container = database.get_container_client("api_catalog")
        
        items = list(container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch API catalog: {str(e)}")

@app.get("/api/databases")
async def list_databases():
    """List all databases and containers in Cosmos DB"""
    try:
        databases = []
        for db in cosmos_client.list_databases():
            db_name = db['id']
            db_client = cosmos_client.get_database_client(db_name)
            containers = []
            try:
                for container in db_client.list_containers():
                    containers.append(container['id'])
            except Exception as e:
                containers = [f"Error: {str(e)}"]
            
            databases.append({
                "database": db_name,
                "containers": containers
            })
        
        return databases
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list databases: {str(e)}")

@app.get("/api/inventory")
async def get_api_inventory():
    """Get all API entries from the larger api_inventory container"""
    try:
        database = cosmos_client.get_database_client("data-collection-db")
        container = database.get_container_client("api_inventory")
        
        items = list(container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch API inventory: {str(e)}")

@app.get("/api/container/{container_name}")
async def get_container_data(container_name: str):
    """Get data from any container in data-collection-db"""
    try:
        database = cosmos_client.get_database_client("data-collection-db")
        container = database.get_container_client(container_name)
        
        # Get count first
        count_items = list(container.query_items(
            query="SELECT VALUE COUNT(1) FROM c",
            enable_cross_partition_query=True
        ))
        count = count_items[0] if count_items else 0
        
        # Get sample items (limit to first 100 for performance)
        items = list(container.query_items(
            query="SELECT * FROM c OFFSET 0 LIMIT 100",
            enable_cross_partition_query=True
        ))
        
        return {
            "container": container_name,
            "total_count": count,
            "sample_items": items,
            "showing": len(items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch from {container_name}: {str(e)}")

@app.get("/api/discovery")
async def get_api_discovery():
    """Get all APIs from the clean discovery schema"""
    try:
        database = cosmos_client.get_database_client("data-collection-db")
        container = database.get_container_client("api_discovery")
        
        items = list(container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch API discovery data: {str(e)}")

@app.get("/api/discovery/{api_id}")
async def get_api_details(api_id: str):
    """Get detailed information for a specific API"""
    try:
        database = cosmos_client.get_database_client("data-collection-db")
        container = database.get_container_client("api_discovery")
        
        try:
            item = container.read_item(item=api_id, partition_key=api_id)
            return item
        except Exception:
            raise HTTPException(status_code=404, detail=f"API with id '{api_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch API details: {str(e)}")

@app.get("/api/stats")
async def get_catalog_stats():
    """Get statistics about the API catalog"""
    try:
        database = cosmos_client.get_database_client("data-collection-db")
        container = database.get_container_client("api_catalog")
        
        items = list(container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        
        stats = {
            "total_apis": len(items),
            "providers": {},
            "categories": {},
            "total_endpoints": 0,
            "total_datasets": 0,
            "total_fields": 0
        }
        
        for item in items:
            # Count by provider
            provider = item.get('provider', 'Unknown')
            stats['providers'][provider] = stats['providers'].get(provider, 0) + 1
            
            # Count by category
            category = item.get('category', 'Unknown')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # Count endpoints and datasets
            endpoints = item.get('endpoints', [])
            datasets = item.get('datasets', [])
            fields = item.get('fields', {})
            
            stats['total_endpoints'] += len(endpoints) if isinstance(endpoints, list) else 0
            stats['total_datasets'] += len(datasets) if isinstance(datasets, list) else 0
            
            # Count fields
            if isinstance(fields, dict):
                for dataset_fields in fields.values():
                    if isinstance(dataset_fields, list):
                        stats['total_fields'] += len(dataset_fields)
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get catalog stats: {str(e)}")

if __name__ == "__main__":
    print(f"🚀 Starting Fundamental Data Manager API on port {API_PORT}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=API_PORT,
        reload=True
    )