#!/usr/bin/env python3
"""
Setup API Discovery Container - Create api_discovery container for actual API entries
While api_registry will hold the schema definition
"""

import os
from datetime import datetime
from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv

load_dotenv()

def setup_api_discovery():
    """Create api_discovery container and put schema in api_registry"""
    
    cosmos_url = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    
    if not cosmos_url or not cosmos_key:
        print("❌ Missing Cosmos DB credentials")
        return False
    
    try:
        client = CosmosClient(cosmos_url, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        
        # 1. Create api_discovery container for actual APIs
        print("🔄 Creating api_discovery container for API entries...")
        
        api_discovery = database.create_container_if_not_exists(
            id="api_discovery",
            partition_key=PartitionKey(path="/category"),
            # Serverless - no throughput settings
        )
        
        print("✅ api_discovery container created")
        
        # 2. Put schema document in api_registry
        print("\n🔄 Adding schema document to api_registry...")
        
        api_registry = database.get_container_client("api_registry")
        
        # Single unified schema document based on api_registry_cosmos_schema.py
        schema_document = {
            "id": "api_schema_definition",
            "type": "schema",
            "category": "system",  # Partition key
            
            # Schema Requirements - based on API_DOCUMENT_SCHEMA
            "schema_requirements": {
                "apiName": "REQUIRED: Display name of the API (e.g., 'OpenWeather API', 'FRED Economic Data API')",
                "provider": "REQUIRED: Organization that provides the API (e.g., 'Federal Reserve Bank', 'Google', 'Microsoft')",
                "version": "REQUIRED: Current API version (e.g., 'v2.0', '1.0', '2025-01-01')",
                "category": "REQUIRED: API category for classification (see validation_rules.allowed_categories)",
                "subcategory": "OPTIONAL: More specific classification within category",
                "description": "REQUIRED: Clear description of what the API does (100-500 characters)",
                "baseUrl": "REQUIRED: Base endpoint URL without trailing slash",
                "authType": "REQUIRED: Authentication method (see validation_rules.allowed_authTypes)",
                "protocol": "REQUIRED: API protocol (see validation_rules.allowed_protocols)",
                "dataFormat": "REQUIRED: Primary data format (see validation_rules.allowed_dataFormats)",
                "status": "REQUIRED: Current operational status (see validation_rules.allowed_status)",
                
                "metadata": {
                    "tags": "REQUIRED: Array of 3-10 descriptive tags",
                    "rateLimit": {
                        "requests": "REQUIRED: Number of allowed requests",
                        "window": "REQUIRED: Time window (e.g., '1h', '24h')",
                        "tier": "REQUIRED: Tier name (e.g., 'free', 'basic')"
                    },
                    "pricing": {
                        "model": "REQUIRED: Pricing model (see allowed values)",
                        "currency": "REQUIRED if not free: Currency code",
                        "baseCost": "REQUIRED if not free: Monthly base cost"
                    },
                    "compliance": {
                        "gdpr": "REQUIRED: Boolean - GDPR compliance",
                        "hipaa": "REQUIRED: Boolean - HIPAA compliance"
                    },
                    "supportedRegions": "REQUIRED: Array of regions",
                    "sdks": {
                        "python": "REQUIRED: Boolean",
                        "javascript": "REQUIRED: Boolean",
                        "java": "REQUIRED: Boolean",
                        "csharp": "REQUIRED: Boolean"
                    }
                }
            },
            
            # Validation Rules
            "validation_rules": {
                "allowed_categories": ["financial", "weather", "geospatial", "social_media", 
                                      "machine_learning", "blockchain", "healthcare", 
                                      "government", "utility", "other"],
                "allowed_authTypes": ["api_key", "oauth2", "basic_auth", "jwt", "none"],
                "allowed_protocols": ["REST", "GraphQL", "SOAP", "WebSocket", "gRPC"],
                "allowed_dataFormats": ["JSON", "XML", "CSV", "Binary", "Mixed"],
                "allowed_status": ["active", "deprecated", "beta", "maintenance", "retired"],
                "allowed_pricingModels": ["free", "freemium", "paid", "usage-based", "enterprise"],
                
                "field_constraints": {
                    "apiName": {"minLength": 3, "maxLength": 100},
                    "description": {"minLength": 50, "maxLength": 500},
                    "provider": {"minLength": 2, "maxLength": 100},
                    "tags": {"minItems": 3, "maxItems": 10}
                },
                
                "required_fields": [
                    "id", "apiName", "provider", "version", "category", 
                    "description", "baseUrl", "authType", "protocol", 
                    "dataFormat", "status"
                ]
            },
            
            "created_at": datetime.utcnow().isoformat() + "Z",
            "version": "1.0"
        }
        
        api_registry.upsert_item(schema_document)
        print("✅ Schema document added to api_registry")
        
        # 3. Clean up the separate schema database we created earlier
        print("\n🧹 Cleaning up separate schema database...")
        try:
            client.delete_database("api-schemas-db")
            print("✅ Removed api-schemas-db")
        except:
            print("ℹ️  No separate schema database to clean up")
        
        # Summary
        print("\n" + "="*60)
        print("✅ SETUP COMPLETE!")
        print("="*60)
        print("\n📊 Database: research-analytics-db")
        print("\n📦 Containers:")
        print("   1. api_registry → Contains schema definition")
        print("      • Document: api_schema_definition")
        print("      • Purpose: Defines requirements and validation rules")
        print("\n   2. api_discovery → For actual API entries")
        print("      • Partition key: /category")
        print("      • Purpose: Store the 500+ APIs")
        print("\n✨ Ready to load APIs into api_discovery container!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    setup_api_discovery()