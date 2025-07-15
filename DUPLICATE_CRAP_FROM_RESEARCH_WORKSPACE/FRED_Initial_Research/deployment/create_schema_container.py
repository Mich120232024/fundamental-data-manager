#!/usr/bin/env python3
"""
Create a separate container for API schema requirements
This creates a new container with a single document containing all schema requirements and rules
"""

import os
import json
from datetime import datetime
from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Single unified schema document
UNIFIED_SCHEMA_DOCUMENT = {
    "id": "api_schema_definition",
    "type": "schema",
    
    # Schema Requirements - each field explains its requirement
    "schema_requirements": {
        "apiName": "REQUIRED: Display name of the API (e.g., 'OpenWeather API', 'FRED Economic Data API')",
        "provider": "REQUIRED: Organization that provides the API (e.g., 'Federal Reserve Bank', 'Google', 'Microsoft')",
        "version": "REQUIRED: Current API version (e.g., 'v2.0', '1.0', '2025-01-01')",
        "category": "REQUIRED: API category for classification (see validation_rules.allowed_categories)",
        "subcategory": "OPTIONAL: More specific classification within category (e.g., 'stock-market', 'weather-forecast')",
        "description": "REQUIRED: Clear description of what the API does and its primary use cases (100-500 characters)",
        "baseUrl": "REQUIRED: Base endpoint URL without trailing slash (e.g., 'https://api.example.com/v1')",
        "authType": "REQUIRED: Authentication method (see validation_rules.allowed_authTypes)",
        "protocol": "REQUIRED: API protocol (see validation_rules.allowed_protocols)",
        "dataFormat": "REQUIRED: Primary data format (see validation_rules.allowed_dataFormats)",
        "status": "REQUIRED: Current operational status (see validation_rules.allowed_status)",
        
        # Nested structures
        "metadata": {
            "tags": "REQUIRED: Array of 3-10 descriptive tags for search and discovery",
            "rateLimit": {
                "requests": "REQUIRED: Number of allowed requests (integer)",
                "window": "REQUIRED: Time window for rate limit (e.g., '1h', '24h')",
                "tier": "REQUIRED: Rate limit tier name (e.g., 'free', 'basic', 'pro')"
            },
            "pricing": {
                "model": "REQUIRED: Pricing model (see validation_rules.allowed_pricingModels)",
                "currency": "REQUIRED if not free: Currency code (e.g., 'USD', 'EUR')",
                "baseCost": "REQUIRED if not free: Monthly base cost as number",
                "details": "OPTIONAL: Additional pricing details"
            },
            "compliance": {
                "gdpr": "REQUIRED: Boolean - GDPR compliance status",
                "hipaa": "REQUIRED: Boolean - HIPAA compliance status",
                "socType": "OPTIONAL: SOC compliance type if applicable",
                "certifications": "OPTIONAL: Array of other certifications"
            },
            "supportedRegions": "REQUIRED: Array of regions where API is available",
            "sdks": {
                "python": "REQUIRED: Boolean - Python SDK availability",
                "javascript": "REQUIRED: Boolean - JavaScript SDK availability",
                "java": "REQUIRED: Boolean - Java SDK availability",
                "csharp": "REQUIRED: Boolean - C# SDK availability"
            }
        },
        
        "endpoints": "REQUIRED: Array of at least 3 main endpoint examples with path, method, description",
        "documentation": {
            "quickStartUrl": "REQUIRED: URL to getting started guide",
            "referenceUrl": "REQUIRED: URL to API reference",
            "examplesUrl": "OPTIONAL: URL to code examples",
            "changelogUrl": "OPTIONAL: URL to changelog"
        },
        "usageMetrics": {
            "popularity": "REQUIRED: Score 1-100 based on adoption",
            "reliability": "REQUIRED: Uptime percentage (e.g., 99.9)",
            "lastChecked": "REQUIRED: ISO datetime when last verified"
        }
    },
    
    # Validation Rules
    "validation_rules": {
        "allowed_categories": ["financial", "weather", "geospatial", "social_media", "machine_learning", 
                              "blockchain", "healthcare", "government", "utility", "other"],
        "allowed_authTypes": ["api_key", "oauth2", "basic_auth", "jwt", "none"],
        "allowed_protocols": ["REST", "GraphQL", "SOAP", "WebSocket", "gRPC"],
        "allowed_dataFormats": ["JSON", "XML", "CSV", "Binary", "Mixed"],
        "allowed_status": ["active", "deprecated", "beta", "maintenance", "retired"],
        "allowed_pricingModels": ["free", "freemium", "paid", "usage-based", "enterprise"],
        
        "field_constraints": {
            "apiName": {"minLength": 3, "maxLength": 100},
            "description": {"minLength": 50, "maxLength": 500},
            "provider": {"minLength": 2, "maxLength": 100},
            "baseUrl": {"minLength": 10, "maxLength": 500, "pattern": "^https?://"},
            "tags": {"minItems": 3, "maxItems": 10},
            "endpoints": {"minItems": 1, "maxItems": 50},
            "supportedRegions": {"minItems": 1, "maxItems": 50}
        },
        
        "required_fields": [
            "id", "apiName", "provider", "version", "category", "description",
            "baseUrl", "authType", "protocol", "dataFormat", "status"
        ]
    },
    
    # Metadata
    "created_at": datetime.utcnow().isoformat() + "Z",
    "version": "1.0",
    "description": "Complete schema definition for API Registry entries"
}

def create_schema_container():
    """Create a new container specifically for schema definition"""
    
    # Get credentials
    cosmos_url = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    
    if not cosmos_url or not cosmos_key:
        print("❌ Missing Cosmos DB credentials")
        return False
    
    try:
        # Connect to Cosmos DB
        client = CosmosClient(cosmos_url, cosmos_key)
        
        # Create new database for schemas (or use existing)
        database_name = "api-schemas-db"
        print(f"🔄 Creating database: {database_name}")
        database = client.create_database_if_not_exists(database_name)
        
        # Create schema container
        container_name = "schema-definitions"
        print(f"🔄 Creating container: {container_name}")
        
        container = database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path="/type"),
            # No throughput settings for serverless
        )
        
        print(f"✅ Container '{container_name}' ready")
        
        # Insert the unified schema document
        print("📝 Inserting unified schema document...")
        container.upsert_item(UNIFIED_SCHEMA_DOCUMENT)
        
        print("\n✅ Schema container created successfully!")
        print(f"📊 Database: {database_name}")
        print(f"📦 Container: {container_name}")
        print(f"📄 Document: api_schema_definition")
        print("\n🔍 This single document contains:")
        print("   • Schema requirements (what each field needs)")
        print("   • Validation rules (allowed values)")
        print("   • Field constraints (lengths, patterns)")
        
        # Verify by reading back
        doc = container.read_item(
            item="api_schema_definition",
            partition_key="schema"
        )
        
        print(f"\n✅ Verified: Document has {len(doc['schema_requirements'])} requirement definitions")
        print(f"✅ Verified: Document has {len(doc['validation_rules'])} validation rule sets")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating schema container: {e}")
        return False

if __name__ == "__main__":
    create_schema_container()