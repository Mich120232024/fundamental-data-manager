#!/usr/bin/env python3
"""
Analyze recipient field inconsistency in messages container
Focus on understanding string vs array type inconsistency
"""

import os
import json
import warnings
from pathlib import Path
from collections import defaultdict

warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

def find_env_file():
    """Find .env file in parent directories"""
    current_dir = Path(__file__).parent
    
    possible_paths = [
        current_dir / '.env',
        current_dir.parent / '.env',
        current_dir.parent.parent / '.env',
        current_dir.parent.parent.parent / '.env',
        Path.home() / '.env'
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    return None

def analyze_recipient_inconsistency():
    """Analyze the 'to' field inconsistency across all messages"""
    
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
    
    print("="*80)
    print("RECIPIENT FIELD INCONSISTENCY ANALYSIS")
    print("="*80)
    
    try:
        from azure.cosmos import CosmosClient
        
        client = CosmosClient(endpoint, key)
        database = client.get_database_client(database_name)
        messages_container = database.get_container_client('system_inbox')
        
        # Query all messages to analyze recipient field types
        print("\n🔍 Analyzing all messages in the container...")
        
        query = "SELECT c.id, c.to, c.from, c.type, c.subject, c.timestamp FROM c"
        all_messages = list(messages_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        print(f"Found {len(all_messages)} total messages")
        
        # Analyze field types
        field_analysis = {
            'string_recipients': [],
            'array_recipients': [],
            'other_types': [],
            'missing_to_field': []
        }
        
        type_stats = defaultdict(int)
        
        for msg in all_messages:
            to_field = msg.get('to')
            
            if to_field is None:
                field_analysis['missing_to_field'].append(msg)
            elif isinstance(to_field, str):
                field_analysis['string_recipients'].append(msg)
                type_stats['string'] += 1
            elif isinstance(to_field, list):
                field_analysis['array_recipients'].append(msg)
                type_stats['array'] += 1
            else:
                field_analysis['other_types'].append(msg)
                type_stats[type(to_field).__name__] += 1
        
        # Print statistics
        print("\n📊 RECIPIENT FIELD TYPE STATISTICS:")
        print("="*50)
        for field_type, count in type_stats.items():
            percentage = (count / len(all_messages)) * 100
            print(f"   {field_type}: {count} messages ({percentage:.1f}%)")
        
        missing_count = len(field_analysis['missing_to_field'])
        if missing_count > 0:
            missing_percentage = (missing_count / len(all_messages)) * 100
            print(f"   missing: {missing_count} messages ({missing_percentage:.1f}%)")
        
        # Show examples of each type
        print("\n📋 EXAMPLES OF EACH TYPE:")
        print("="*50)
        
        if field_analysis['string_recipients']:
            print("\n✅ STRING RECIPIENTS (Standard Format):")
            print("-" * 40)
            for i, msg in enumerate(field_analysis['string_recipients'][:5]):
                print(f"{i+1}. ID: {msg.get('id', 'N/A')}")
                print(f"   From: {msg.get('from', 'N/A')}")
                print(f"   To: '{msg.get('to', 'N/A')}'")
                print(f"   Subject: {msg.get('subject', 'N/A')[:50]}...")
                print()
        
        if field_analysis['array_recipients']:
            print("\n❓ ARRAY RECIPIENTS (Inconsistent Format):")
            print("-" * 40)
            for i, msg in enumerate(field_analysis['array_recipients'][:5]):
                print(f"{i+1}. ID: {msg.get('id', 'N/A')}")
                print(f"   From: {msg.get('from', 'N/A')}")
                print(f"   To: {msg.get('to', 'N/A')}")
                print(f"   Subject: {msg.get('subject', 'N/A')[:50]}...")
                print()
        
        if field_analysis['other_types']:
            print("\n⚠️  OTHER TYPES (Unexpected):")
            print("-" * 40)
            for i, msg in enumerate(field_analysis['other_types'][:3]):
                to_field = msg.get('to')
                print(f"{i+1}. ID: {msg.get('id', 'N/A')}")
                print(f"   From: {msg.get('from', 'N/A')}")
                print(f"   To ({type(to_field).__name__}): {to_field}")
                print(f"   Subject: {msg.get('subject', 'N/A')[:50]}...")
                print()
        
        if field_analysis['missing_to_field']:
            print("\n❌ MISSING 'TO' FIELD:")
            print("-" * 40)
            for i, msg in enumerate(field_analysis['missing_to_field'][:3]):
                print(f"{i+1}. ID: {msg.get('id', 'N/A')}")
                print(f"   From: {msg.get('from', 'N/A')}")
                print(f"   Subject: {msg.get('subject', 'N/A')[:50]}...")
                print()
        
        # Analyze patterns
        print("\n🔍 PATTERN ANALYSIS:")
        print("="*50)
        
        # Check if certain message types use arrays
        if field_analysis['array_recipients']:
            array_types = defaultdict(int)
            array_from_agents = defaultdict(int)
            
            for msg in field_analysis['array_recipients']:
                msg_type = msg.get('type', 'UNKNOWN')
                from_agent = msg.get('from', 'UNKNOWN')
                array_types[msg_type] += 1
                array_from_agents[from_agent] += 1
            
            print("\nArray recipients by message type:")
            for msg_type, count in array_types.items():
                print(f"   {msg_type}: {count}")
            
            print("\nArray recipients by sender:")
            for agent, count in array_from_agents.items():
                print(f"   {agent}: {count}")
        
        # Root cause analysis
        print("\n🎯 ROOT CAUSE ANALYSIS:")
        print("="*50)
        
        if type_stats['string'] > type_stats['array']:
            print("✅ FINDING: String format is the dominant pattern")
            print("   - Most messages use string recipients (standard)")
            print("   - Array format appears to be exceptional cases")
            
            if field_analysis['array_recipients']:
                print("\n🔍 Investigating array recipient origins...")
                
                # Check if arrays contain only one element
                single_element_arrays = 0
                multi_element_arrays = 0
                
                for msg in field_analysis['array_recipients']:
                    to_field = msg.get('to', [])
                    if len(to_field) == 1:
                        single_element_arrays += 1
                    else:
                        multi_element_arrays += 1
                
                print(f"   - Single-element arrays: {single_element_arrays}")
                print(f"   - Multi-element arrays: {multi_element_arrays}")
                
                if single_element_arrays > multi_element_arrays:
                    print("   💡 LIKELY CAUSE: Programming error converting strings to arrays")
                else:
                    print("   💡 LIKELY CAUSE: Intentional multi-recipient messaging")
        
        # Data quality assessment
        print("\n📊 DATA QUALITY ASSESSMENT:")
        print("="*50)
        
        total_inconsistent = len(field_analysis['array_recipients']) + len(field_analysis['other_types']) + len(field_analysis['missing_to_field'])
        consistency_score = (type_stats['string'] / len(all_messages)) * 100
        
        print(f"Schema Consistency Score: {consistency_score:.1f}%")
        print(f"Inconsistent Messages: {total_inconsistent}")
        
        if consistency_score >= 90:
            print("✅ ASSESSMENT: Good data quality with minor inconsistencies")
        elif consistency_score >= 75:
            print("⚠️  ASSESSMENT: Moderate data quality issues")
        else:
            print("❌ ASSESSMENT: Poor data quality - significant inconsistencies")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("="*50)
        
        if total_inconsistent > 0:
            print("1. Schema Standardization:")
            print("   - Define 'to' field as string type for single recipients")
            print("   - Create separate 'cc' or 'recipients' array field for multiple recipients")
            print("   - Add application-level validation before storing messages")
            
            print("\n2. Data Cleanup:")
            if field_analysis['array_recipients']:
                print("   - Convert single-element arrays to strings")
                print("   - Handle multi-element arrays appropriately")
            if field_analysis['missing_to_field']:
                print("   - Identify and fix messages missing 'to' field")
            
            print("\n3. Prevention:")
            print("   - Add schema validation in CosmosDBManager.store_message()")
            print("   - Create unit tests for message format validation")
            print("   - Document expected message schema in metadata container")
        else:
            print("✅ No immediate action required - schema is consistent")
        
        return field_analysis, type_stats
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None, None

if __name__ == "__main__":
    analyze_recipient_inconsistency()