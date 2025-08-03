#!/usr/bin/env python3
"""
Migrate real catalog data to clean API discovery schema
"""

import json
import requests
from azure.cosmos import CosmosClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Cosmos DB connection
COSMOS_ENDPOINT = os.getenv('COSMOS_ENDPOINT')
COSMOS_KEY = os.getenv('COSMOS_KEY')
cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = cosmos_client.get_database_client("data-collection-db")
discovery_container = database.get_container_client("api_discovery")

def convert_catalog_to_discovery(catalog_item):
    """Convert old catalog format to new discovery schema"""
    
    # Extract basic info
    api_id = catalog_item.get('id', '').replace('-complete', '').replace('-', '_')
    name = catalog_item.get('apiName', catalog_item.get('id', 'Unknown API'))
    provider = catalog_item.get('provider', 'Unknown')
    description = f"{name} - {catalog_item.get('category', 'Data API')}"
    
    # Determine discovery status based on existing data
    endpoints_count = len(catalog_item.get('endpoints', []))
    if endpoints_count > 10:
        status = "production_ready"
    elif endpoints_count > 0:
        status = "documented"  
    else:
        status = "not_started"
    
    # Extract access info from tiers
    tiers = catalog_item.get('tiers', [])
    free_tier = next((t for t in tiers if t.get('price', 0) == 0), None)
    
    access_info = {
        "is_free": free_tier is not None,
        "requires_api_key": True if free_tier and 'api_key' in str(free_tier) else False,
        "requires_approval": False,
        "pricing_model": "free" if free_tier else "unknown",
        "rate_limits": free_tier.get('rateLimit', 'unknown') if free_tier else 'unknown'
    }
    
    # Technical info
    base_url = ""
    endpoints = catalog_item.get('endpoints', [])
    if endpoints:
        first_endpoint = endpoints[0]
        if isinstance(first_endpoint, dict):
            base_url = first_endpoint.get('baseUrl', first_endpoint.get('url', ''))
    
    technical_info = {
        "base_url": base_url,
        "protocol": "REST",
        "data_formats": ["JSON"],
        "auth_method": "api_key" if access_info["requires_api_key"] else "none"
    }
    
    # Content summary
    category = catalog_item.get('category', '')
    subcategories = catalog_item.get('subcategories', [])
    
    content_summary = {
        "data_categories": [category.lower()] + [s.lower() for s in subcategories[:3]],
        "geographic_scope": "US" if "US" in str(catalog_item) else "global",
        "update_frequency": "daily",
        "historical_data": True
    }
    
    # Research notes
    research_notes = {
        "documentation_url": "",
        "sample_endpoints": [ep.get('path', ep.get('endpoint', '')) for ep in endpoints[:5] if isinstance(ep, dict)],
        "data_quality": "high" if status == "production_ready" else "medium",
        "last_researched": datetime.utcnow().isoformat() + "Z",
        "researcher_notes": f"Migrated from catalog - {endpoints_count} endpoints documented"
    }
    
    # System metadata
    system_metadata = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "version": 1
    }
    
    return {
        "id": api_id,
        "name": name,
        "provider": provider,
        "description": description,
        "discovery_status": status,
        "access_info": access_info,
        "technical_info": technical_info,
        "content_summary": content_summary,
        "research_notes": research_notes,
        "system_metadata": system_metadata
    }

def main():
    # Get real catalog data
    response = requests.get('http://localhost:8850/api/catalog')
    catalog_data = response.json()
    
    # Filter only APIs with names (real ones)
    real_apis = [item for item in catalog_data if item.get('apiName')]
    
    print(f"Found {len(real_apis)} real APIs to migrate")
    
    # Convert and insert
    migrated_count = 0
    for api in real_apis:
        try:
            discovery_item = convert_catalog_to_discovery(api)
            discovery_container.create_item(discovery_item)
            print(f"✅ Migrated: {discovery_item['name']}")
            migrated_count += 1
        except Exception as e:
            print(f"❌ Failed to migrate {api.get('apiName', 'unknown')}: {e}")
    
    print(f"\n🎉 Migration complete: {migrated_count} APIs migrated to api_discovery container")

if __name__ == "__main__":
    main()