#!/usr/bin/env python3
"""
CORRECTED MIGRATION: Convert 500 potential APIs from inventory to clean discovery schema
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

def convert_inventory_to_discovery(inventory_item):
    """Convert messy inventory format to clean discovery schema for research"""
    
    # Basic info - clean up the names
    api_id = inventory_item.get('id', 'unknown')
    name = inventory_item.get('display_name', inventory_item.get('name', 'Unknown API'))
    provider = inventory_item.get('provider', 'Unknown Provider')
    description = inventory_item.get('description', 'API requiring research')
    
    # Map status to discovery_status 
    current_status = inventory_item.get('status', 'new')
    status_mapping = {
        'new': 'not_started',
        'discovered': 'researching', 
        'existing': 'documented',
        'production': 'production_ready',
        'planned': 'not_started'
    }
    discovery_status = status_mapping.get(current_status, 'not_started')
    
    # Access info - mostly unknown, needs research
    access_info = {
        "is_free": None,  # Unknown - needs research 
        "requires_api_key": None,  # Unknown - needs research
        "requires_approval": False,
        "pricing_model": "unknown", 
        "rate_limits": "unknown"
    }
    
    # Technical info from existing data where available
    tech_info = inventory_item.get('technical', {})
    technical_info = {
        "base_url": tech_info.get('base_url', ''),
        "protocol": tech_info.get('protocol', 'REST'),
        "data_formats": ["JSON"],  # Default assumption
        "auth_method": tech_info.get('authentication', {}).get('type', 'unknown')
    }
    
    # Content summary - extract what we can
    classification = inventory_item.get('classification', {})
    content_summary = {
        "data_categories": [classification.get('primary_category', 'unknown')],
        "geographic_scope": classification.get('geographical_scope', 'unknown'),
        "update_frequency": "unknown",
        "historical_data": None  # Unknown - needs research
    }
    
    # Generate tags based on available information
    tags = []
    if classification.get('primary_category'):
        tags.append(classification['primary_category'].lower())
    if provider and provider != 'Unknown Provider':
        tags.append(provider.lower().replace(' ', '_'))
    if classification.get('geographical_scope') and classification['geographical_scope'] != 'unknown':
        tags.append(classification['geographical_scope'].lower())
    if current_status:
        tags.append(f"status_{current_status}")
    # Add some default tags for research workflow
    tags.extend(['api', 'research_needed'])
    
    # Research notes - mark as needing research
    endpoints_list = inventory_item.get('endpoints_list', [])
    sample_endpoints = []
    if endpoints_list:
        sample_endpoints = [ep.get('path', '') for ep in endpoints_list[:3] if isinstance(ep, dict)]
    
    research_notes = {
        "documentation_url": inventory_item.get('documentation', {}).get('official_docs', ''),
        "sample_endpoints": sample_endpoints,
        "data_quality": "unknown",
        "last_researched": None,
        "researcher_notes": f"Potential API - needs full research. Status: {current_status}"
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
        "discovery_status": discovery_status,
        "tags": tags,
        "access_info": access_info,
        "technical_info": technical_info,
        "content_summary": content_summary,
        "research_notes": research_notes,
        "system_metadata": system_metadata
    }

def is_real_api(inventory_item):
    """Filter out metadata entries - only keep real API entries"""
    item_id = inventory_item.get('id', '')
    
    # Skip metadata entries
    if (item_id.startswith('schema_') or 
        item_id.startswith('status_') or 
        item_id.startswith('category_')):
        return False
    
    # Skip entries that look like category definitions
    name = inventory_item.get('name', inventory_item.get('display_name', ''))
    if name in ['new', 'ready_to_mount', 'azure_ready', 'ai_ready', 'production',
                'financial', 'alternative-data', 'technology', 'healthcare', 'emerging-tech',
                'smart-city', 'government', 'academic-research', 'energy-commodities',
                'real-estate', 'legal-regulatory', 'crypto-blockchain', 'retail-consumer',
                'transportation-logistics', 'agriculture-food', 'environmental-climate',
                'media-entertainment', 'regional-data']:
        return False
    
    return True

def main():
    # Get the 500 potential APIs from inventory
    response = requests.get('http://localhost:8850/api/inventory')
    inventory_data = response.json()
    
    # Filter to only real APIs
    real_apis = [api for api in inventory_data if is_real_api(api)]
    
    print(f"Found {len(inventory_data)} total items, filtering to {len(real_apis)} real APIs")
    
    # Convert and insert all potential APIs
    migrated_count = 0
    errors = []
    
    for api in real_apis:
        try:
            discovery_item = convert_inventory_to_discovery(api)
            discovery_container.create_item(discovery_item)
            print(f"✅ Added potential API: {discovery_item['name']}")
            migrated_count += 1
        except Exception as e:
            error_msg = f"❌ Failed to migrate {api.get('name', 'unknown')}: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    print(f"\n🎉 Migration complete:")
    print(f"   📋 {migrated_count} potential APIs added to discovery")
    print(f"   ❌ {len(errors)} errors")
    
    if errors:
        print("\nErrors encountered:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"   {error}")

if __name__ == "__main__":
    main()