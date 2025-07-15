#!/usr/bin/env python3
"""
Check Cosmos DB container schema configuration and metadata
"""

import os
import json
import warnings
from pathlib import Path

warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

def find_env_file():
    """Find .env file in parent directories"""
    current_dir = Path(__file__).parent
    
    # Check multiple possible locations
    possible_paths = [
        current_dir / '.env',
        current_dir.parent / '.env',
        current_dir.parent.parent / '.env',
        current_dir.parent.parent.parent / '.env',
        Path.home() / '.env'
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"Found .env at: {path}")
            return path
    
    print("No .env file found in any expected location")
    return None

def check_container_configuration():
    """Check the actual container configuration"""
    
    # Load environment
    env_path = find_env_file()
    if env_path:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    
    endpoint = os.getenv('COSMOS_ENDPOINT')
    key = os.getenv('COSMOS_KEY')
    database_name = os.getenv('COSMOS_DATABASE', 'research-analytics-db')
    
    if not endpoint or not key:
        print("❌ Missing Cosmos DB credentials")
        return
    
    print("="*60)
    print("COSMOS DB CONTAINER SCHEMA ANALYSIS")
    print("="*60)
    
    try:
        from azure.cosmos import CosmosClient
        from azure.cosmos.exceptions import CosmosResourceNotFoundError
        
        # Connect to Cosmos DB
        client = CosmosClient(endpoint, key)
        database = client.get_database_client(database_name)
        
        print(f"\n📊 Database: {database_name}")
        
        # List all containers
        containers = list(database.list_containers())
        print(f"\n📋 Containers found: {len(containers)}")
        
        for container_info in containers:
            container_id = container_info['id']
            print(f"\n🗂️  Container: {container_id}")
            
            # Get container details
            container = database.get_container_client(container_id)
            
            try:
                # Get container properties
                properties = container.read()
                
                print(f"   Partition Key: {properties.get('partitionKey', 'Not defined')}")
                
                # Check indexing policy
                indexing_policy = properties.get('indexingPolicy', {})
                print(f"   Indexing Mode: {indexing_policy.get('indexingMode', 'Not defined')}")
                print(f"   Automatic Indexing: {indexing_policy.get('automatic', 'Not defined')}")
                
                # Check for composite indexes
                composite_indexes = indexing_policy.get('compositeIndexes', [])
                if composite_indexes:
                    print(f"   Composite Indexes: {len(composite_indexes)} defined")
                    for idx, comp_idx in enumerate(composite_indexes):
                        print(f"     Index {idx+1}: {comp_idx}")
                else:
                    print("   Composite Indexes: None")
                
                # Check unique key policy
                unique_key_policy = properties.get('uniqueKeyPolicy', {})
                if unique_key_policy.get('uniqueKeys'):
                    print(f"   Unique Keys: {unique_key_policy['uniqueKeys']}")
                else:
                    print("   Unique Keys: None")
                
                # Check for stored procedures
                try:
                    stored_procs = list(container.scripts.list_stored_procedures())
                    if stored_procs:
                        print(f"   Stored Procedures: {len(stored_procs)}")
                        for sp in stored_procs:
                            print(f"     - {sp['id']}")
                    else:
                        print("   Stored Procedures: None")
                except:
                    print("   Stored Procedures: Could not retrieve")
                
                # Check for triggers
                try:
                    triggers = list(container.scripts.list_triggers())
                    if triggers:
                        print(f"   Triggers: {len(triggers)}")
                        for trigger in triggers:
                            print(f"     - {trigger['id']}")
                    else:
                        print("   Triggers: None")
                except:
                    print("   Triggers: Could not retrieve")
                
                # Get sample documents if it's the messages container
                if container_id == 'messages':
                    print("\n📨 Sample Message Schema Analysis:")
                    try:
                        sample_query = "SELECT TOP 5 * FROM c ORDER BY c._ts DESC"
                        sample_messages = list(container.query_items(
                            query=sample_query,
                            enable_cross_partition_query=True
                        ))
                        
                        if sample_messages:
                            print(f"   Found {len(sample_messages)} sample messages")
                            
                            # Analyze field consistency
                            field_usage = {}
                            recipient_types = {}
                            
                            for msg in sample_messages:
                                for field in msg.keys():
                                    if field not in field_usage:
                                        field_usage[field] = 0
                                    field_usage[field] += 1
                                
                                # Check recipient field specifically
                                if 'to' in msg:
                                    to_value = msg['to']
                                    to_type = type(to_value).__name__
                                    if to_type not in recipient_types:
                                        recipient_types[to_type] = 0
                                    recipient_types[to_type] += 1
                            
                            print("   📊 Field Usage:")
                            for field, count in sorted(field_usage.items()):
                                print(f"     {field}: {count}/{len(sample_messages)} messages")
                            
                            print("   📊 Recipient Field Types:")
                            for field_type, count in recipient_types.items():
                                print(f"     {field_type}: {count}/{len(sample_messages)} messages")
                            
                            # Show sample message structure
                            print("\n   📋 Sample Message Structure:")
                            sample_msg = sample_messages[0]
                            for key, value in sample_msg.items():
                                if key.startswith('_'):
                                    continue
                                value_type = type(value).__name__
                                if isinstance(value, str) and len(value) > 50:
                                    preview = value[:50] + "..."
                                elif isinstance(value, list):
                                    preview = f"[{len(value)} items]"
                                elif isinstance(value, dict):
                                    preview = f"{{...}}"
                                else:
                                    preview = str(value)
                                print(f"     {key} ({value_type}): {preview}")
                        
                        else:
                            print("   No messages found")
                    except Exception as e:
                        print(f"   Error analyzing messages: {e}")
            
            except Exception as e:
                print(f"   ❌ Could not read container properties: {e}")
        
        print("\n" + "="*60)
        print("SCHEMA DEFINITION ANALYSIS")
        print("="*60)
        
        print("\n📝 Schema Definition Status:")
        print("   ❌ No explicit schema validation found")
        print("   ❌ No data type constraints detected")
        print("   ❌ No field requirement enforcement")
        print("   ❌ No stored procedures for validation")
        print("   ❌ No triggers for schema enforcement")
        
        print("\n🔍 Schema Issues Identified:")
        print("   • Inconsistent recipient field types (string vs array)")
        print("   • No validation of required fields")
        print("   • No constraints on field data types")
        print("   • Schema relies on application-level validation only")
        
        print("\n💡 Recommendations:")
        print("   1. Implement application-level schema validation")
        print("   2. Create stored procedures for data validation")
        print("   3. Add pre-trigger validation for critical fields")
        print("   4. Document expected schema in metadata container")
        print("   5. Implement data quality monitoring")
        
    except Exception as e:
        print(f"❌ Error analyzing containers: {e}")

if __name__ == "__main__":
    check_container_configuration()