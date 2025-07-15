#!/usr/bin/env python3
"""
API Registry Schema Requirements Document

This creates a special document in the API registry that defines the schema requirements.
Each field contains a string explaining what that field requires.
This serves as the definitive reference for all APIs added to the registry.
"""

import os
import json
from datetime import datetime
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Schema Requirements Document - Each field explains its requirement
SCHEMA_REQUIREMENTS = {
    "id": "schema_requirements_v1",
    "category": "system",  # Special system category for schema docs
    "apiName": "REQUIRED: Display name of the API (e.g., 'OpenWeather API', 'FRED Economic Data API')",
    "provider": "REQUIRED: Organization that provides the API (e.g., 'Federal Reserve Bank', 'Google', 'Microsoft')",
    "version": "REQUIRED: Current API version (e.g., 'v2.0', '1.0', '2025-01-01')",
    "subcategory": "OPTIONAL: More specific classification within category (e.g., 'stock-market', 'weather-forecast')",
    "description": "REQUIRED: Clear description of what the API does and its primary use cases (100-500 characters)",
    
    # Technical Requirements
    "baseUrl": "REQUIRED: Base endpoint URL without trailing slash (e.g., 'https://api.example.com/v1')",
    "authType": "REQUIRED: One of: 'api_key', 'oauth2', 'basic_auth', 'jwt', 'none'",
    "protocol": "REQUIRED: API protocol - One of: 'REST', 'GraphQL', 'SOAP', 'WebSocket', 'gRPC'",
    "dataFormat": "REQUIRED: Primary data format - One of: 'JSON', 'XML', 'CSV', 'Binary', 'Mixed'",
    "status": "REQUIRED: Current operational status - One of: 'active', 'deprecated', 'beta', 'maintenance', 'retired'",
    
    # Metadata Structure
    "metadata": {
        "description": "Nested object containing detailed API metadata",
        "tags": "REQUIRED: Array of 3-10 descriptive tags for search and discovery (e.g., ['finance', 'real-time', 'market-data'])",
        "rateLimit": {
            "requests": "REQUIRED: Number of allowed requests (integer, e.g., 1000)",
            "window": "REQUIRED: Time window for rate limit (e.g., '1h', '24h', '1m')",
            "tier": "REQUIRED: Rate limit tier name (e.g., 'free', 'basic', 'pro', 'enterprise')"
        },
        "pricing": {
            "model": "REQUIRED: Pricing model - One of: 'free', 'freemium', 'paid', 'usage-based', 'enterprise'",
            "currency": "REQUIRED if not free: Currency code (e.g., 'USD', 'EUR', 'GBP')",
            "baseCost": "REQUIRED if not free: Monthly base cost as number (0 for free tier)",
            "details": "OPTIONAL: Additional pricing details or tiers explanation"
        },
        "compliance": {
            "gdpr": "REQUIRED: Boolean - true if GDPR compliant, false otherwise",
            "hipaa": "REQUIRED: Boolean - true if HIPAA compliant, false otherwise",
            "socType": "OPTIONAL: SOC compliance type if applicable ('SOC1', 'SOC2', 'SOC3', 'none')",
            "certifications": "OPTIONAL: Array of other certifications (e.g., ['ISO27001', 'PCI-DSS'])"
        },
        "supportedRegions": "REQUIRED: Array of geographic regions where API is available (e.g., ['global'], ['us-east', 'eu-west'])",
        "sdks": {
            "python": "REQUIRED: Boolean - official Python SDK available",
            "javascript": "REQUIRED: Boolean - official JavaScript/Node.js SDK available",
            "java": "REQUIRED: Boolean - official Java SDK available",
            "csharp": "REQUIRED: Boolean - official C#/.NET SDK available",
            "go": "OPTIONAL: Boolean - official Go SDK available",
            "ruby": "OPTIONAL: Boolean - official Ruby SDK available"
        }
    },
    
    # Endpoints Requirements
    "endpoints": [
        {
            "description": "REQUIRED: Array of at least 3 main endpoint examples",
            "path": "REQUIRED: Endpoint path template (e.g., '/users/{id}', '/weather/current')",
            "method": "REQUIRED: HTTP method - One of: 'GET', 'POST', 'PUT', 'DELETE', 'PATCH'",
            "description": "REQUIRED: What this endpoint does (50-200 characters)",
            "parameters": [
                {
                    "name": "REQUIRED: Parameter name (e.g., 'api_key', 'user_id')",
                    "type": "REQUIRED: Parameter type - One of: 'string', 'number', 'boolean', 'array', 'object'",
                    "required": "REQUIRED: Boolean - true if parameter is mandatory",
                    "description": "REQUIRED: What this parameter does (20-100 characters)"
                }
            ],
            "responseSchema": "OPTIONAL: JSON schema object or reference describing response structure"
        }
    ],
    
    # Documentation Requirements
    "documentation": {
        "quickStartUrl": "REQUIRED: URL to getting started guide (can be external or blob storage)",
        "referenceUrl": "REQUIRED: URL to complete API reference documentation",
        "examplesUrl": "OPTIONAL: URL to code examples and tutorials",
        "changelogUrl": "OPTIONAL: URL to version history and changelog",
        "openApiSpecUrl": "RECOMMENDED: URL to OpenAPI/Swagger specification if available"
    },
    
    # Usage Metrics Requirements
    "usageMetrics": {
        "popularity": "REQUIRED: Score from 1-100 based on adoption (100 = extremely popular)",
        "reliability": "REQUIRED: Uptime percentage (e.g., 99.9 for 99.9% uptime)",
        "averageResponseTime": "OPTIONAL: Average response time in milliseconds",
        "monthlyUsers": "OPTIONAL: Estimated monthly active users/applications",
        "lastChecked": "REQUIRED: ISO datetime when metrics were last verified"
    },
    
    # Administrative Requirements
    "createdAt": "AUTOMATIC: Set by system when document is created",
    "updatedAt": "AUTOMATIC: Set by system when document is updated",
    "createdBy": "AUTOMATIC: User or agent who created the entry",
    "lastModifiedBy": "AUTOMATIC: User or agent who last modified the entry",
    
    # System Fields
    "_etag": "SYSTEM: Cosmos DB entity tag for optimistic concurrency",
    "_ts": "SYSTEM: Cosmos DB timestamp (Unix epoch)"
}

# Validation Rules Document
VALIDATION_RULES = {
    "id": "validation_rules_v1",
    "category": "system",
    "apiName": "Validation Rules for API Registry",
    "provider": "System",
    "version": "1.0",
    "rules": {
        "required_fields": [
            "id", "category", "apiName", "provider", "version", "baseUrl",
            "authType", "protocol", "dataFormat", "status", "description"
        ],
        "category_values": [
            "financial", "weather", "geospatial", "social_media", 
            "machine_learning", "blockchain", "healthcare", "government", 
            "utility", "other"
        ],
        "authType_values": ["api_key", "oauth2", "basic_auth", "jwt", "none"],
        "protocol_values": ["REST", "GraphQL", "SOAP", "WebSocket", "gRPC"],
        "dataFormat_values": ["JSON", "XML", "CSV", "Binary", "Mixed"],
        "status_values": ["active", "deprecated", "beta", "maintenance", "retired"],
        "pricing_model_values": ["free", "freemium", "paid", "usage-based", "enterprise"],
        "field_lengths": {
            "apiName": {"min": 3, "max": 100},
            "description": {"min": 50, "max": 500},
            "provider": {"min": 2, "max": 100},
            "baseUrl": {"min": 10, "max": 500}
        },
        "array_lengths": {
            "tags": {"min": 3, "max": 10},
            "endpoints": {"min": 1, "max": 50},
            "supportedRegions": {"min": 1, "max": 50}
        }
    }
}

def insert_schema_requirements():
    """Insert schema requirements and validation rules into API registry"""
    
    # Get credentials
    cosmos_url = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    
    if not cosmos_url or not cosmos_key:
        print("❌ Missing Cosmos DB credentials")
        return False
    
    try:
        # Connect to Cosmos DB
        client = CosmosClient(cosmos_url, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        container = database.get_container_client("api_registry")
        
        print("📝 Inserting Schema Requirements into API Registry...")
        
        # Add timestamps
        now = datetime.utcnow().isoformat() + "Z"
        SCHEMA_REQUIREMENTS["createdAt"] = now
        SCHEMA_REQUIREMENTS["updatedAt"] = now
        SCHEMA_REQUIREMENTS["createdBy"] = "system"
        SCHEMA_REQUIREMENTS["lastModifiedBy"] = "system"
        
        VALIDATION_RULES["createdAt"] = now
        VALIDATION_RULES["updatedAt"] = now
        VALIDATION_RULES["createdBy"] = "system"
        VALIDATION_RULES["lastModifiedBy"] = "system"
        
        # Insert schema requirements
        container.upsert_item(SCHEMA_REQUIREMENTS)
        print("✅ Schema requirements document inserted")
        
        # Insert validation rules
        container.upsert_item(VALIDATION_RULES)
        print("✅ Validation rules document inserted")
        
        # Query to verify
        query = "SELECT * FROM c WHERE c.category = 'system'"
        results = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        print(f"\n📊 System documents in registry: {len(results)}")
        for doc in results:
            print(f"   • {doc['id']}: {doc['apiName']}")
        
        print("\n✅ Schema requirements successfully stored in API registry!")
        print("📄 These documents define the requirements for all APIs in the registry")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inserting schema requirements: {e}")
        return False

if __name__ == "__main__":
    insert_schema_requirements()