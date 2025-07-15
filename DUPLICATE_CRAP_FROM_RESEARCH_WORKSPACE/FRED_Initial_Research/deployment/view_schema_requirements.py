#!/usr/bin/env python3
"""
View Schema Requirements from API Registry

Shows how the schema requirements are stored with explanations in each field.
"""

import os
import json
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def view_schema_requirements():
    """View and display schema requirements in a readable format"""
    
    # Get credentials
    cosmos_url = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    
    try:
        # Connect to Cosmos DB
        client = CosmosClient(cosmos_url, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        container = database.get_container_client("api_registry")
        
        print("📋 API Registry Schema Requirements")
        print("="*60)
        
        # Get schema requirements document
        schema_doc = container.read_item(
            item="schema_requirements_v1",
            partition_key="system"
        )
        
        print("\n🔍 Schema Requirements Document Structure:")
        print("Each field contains a string explaining what that field requires.\n")
        
        # Display flat fields
        print("📌 BASIC FIELDS:")
        basic_fields = ["apiName", "provider", "version", "description", 
                       "baseUrl", "authType", "protocol", "dataFormat", "status"]
        for field in basic_fields:
            if field in schema_doc:
                print(f"\n{field}:")
                print(f"  → {schema_doc[field]}")
        
        # Display metadata structure
        print("\n\n📌 METADATA STRUCTURE:")
        if "metadata" in schema_doc:
            metadata = schema_doc["metadata"]
            
            # Tags
            print(f"\nmetadata.tags:")
            print(f"  → {metadata['tags']}")
            
            # Rate Limit
            print(f"\nmetadata.rateLimit:")
            for key, value in metadata["rateLimit"].items():
                print(f"  .{key}: {value}")
            
            # Pricing
            print(f"\nmetadata.pricing:")
            for key, value in metadata["pricing"].items():
                print(f"  .{key}: {value}")
            
            # Compliance
            print(f"\nmetadata.compliance:")
            for key, value in metadata["compliance"].items():
                print(f"  .{key}: {value}")
            
            # SDKs
            print(f"\nmetadata.sdks:")
            for key, value in metadata["sdks"].items():
                print(f"  .{key}: {value}")
        
        # Display validation rules
        print("\n\n📌 VALIDATION RULES:")
        validation_doc = container.read_item(
            item="validation_rules_v1",
            partition_key="system"
        )
        
        if "rules" in validation_doc:
            rules = validation_doc["rules"]
            
            print(f"\nAllowed Categories: {', '.join(rules['category_values'])}")
            print(f"Allowed Auth Types: {', '.join(rules['authType_values'])}")
            print(f"Allowed Protocols: {', '.join(rules['protocol_values'])}")
            print(f"Allowed Status Values: {', '.join(rules['status_values'])}")
            
            print(f"\nField Length Requirements:")
            for field, limits in rules['field_lengths'].items():
                print(f"  {field}: {limits['min']}-{limits['max']} characters")
            
            print(f"\nArray Length Requirements:")
            for field, limits in rules['array_lengths'].items():
                print(f"  {field}: {limits['min']}-{limits['max']} items")
        
        print("\n" + "="*60)
        print("✅ Schema requirements define what each field must contain")
        print("✅ Use these requirements when adding new APIs to the registry")
        
    except Exception as e:
        print(f"❌ Error viewing schema requirements: {e}")

if __name__ == "__main__":
    view_schema_requirements()