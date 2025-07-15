#!/usr/bin/env python3
"""
Simple analysis of recipient field types using read_all_items
"""

import os
import warnings
from pathlib import Path
from collections import defaultdict

warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

def find_env_file():
    """Find .env file in parent directories"""
    current_dir = Path(__file__).parent
    
    possible_paths = [
        current_dir.parent.parent.parent / '.env',
        current_dir.parent.parent / '.env', 
        current_dir.parent / '.env',
        current_dir / '.env'
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    return None

def main():
    """Analyze recipient field inconsistency"""
    
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
    print("COSMOS DB MESSAGE SCHEMA ANALYSIS")
    print("="*80)
    
    try:
        from azure.cosmos import CosmosClient
        
        client = CosmosClient(endpoint, key)
        database = client.get_database_client(database_name)
        messages_container = database.get_container_client('system_inbox')
        
        # Get all messages using read_all_items
        print("\n🔍 Reading all messages from container...")
        all_messages = list(messages_container.read_all_items())
        
        print(f"Found {len(all_messages)} total messages")
        
        # Analyze recipient field types
        recipient_types = defaultdict(int)
        examples = defaultdict(list)
        
        for msg in all_messages:
            to_field = msg.get('to')
            
            if to_field is None:
                field_type = 'missing'
            else:
                field_type = type(to_field).__name__
            
            recipient_types[field_type] += 1
            
            # Store examples (limit to 3 per type)
            if len(examples[field_type]) < 3:
                examples[field_type].append({
                    'id': msg.get('id', 'N/A'),
                    'from': msg.get('from', 'N/A'),
                    'to': to_field,
                    'subject': msg.get('subject', 'N/A')[:50] + '...' if msg.get('subject') else 'N/A',
                    'timestamp': msg.get('timestamp', 'N/A')
                })
        
        # Print results
        print("\n📊 RECIPIENT FIELD TYPE ANALYSIS:")
        print("="*60)
        
        total_messages = len(all_messages)
        for field_type, count in sorted(recipient_types.items()):
            percentage = (count / total_messages) * 100
            print(f"   {field_type:12} : {count:4} messages ({percentage:5.1f}%)")
        
        print("\n📋 EXAMPLES BY TYPE:")
        print("="*60)
        
        for field_type, example_list in examples.items():
            print(f"\n🔍 {field_type.upper()} EXAMPLES:")
            print("-" * 40)
            
            for i, example in enumerate(example_list, 1):
                print(f"{i}. ID: {example['id']}")
                print(f"   From: {example['from']}")
                print(f"   To: {repr(example['to'])}")
                print(f"   Subject: {example['subject']}")
                print(f"   Time: {example['timestamp']}")
                print()
        
        # Check for inconsistency patterns
        print("\n🎯 INCONSISTENCY ANALYSIS:")
        print("="*60)
        
        if 'str' in recipient_types and 'list' in recipient_types:
            str_count = recipient_types['str']
            list_count = recipient_types['list']
            
            print(f"❌ SCHEMA INCONSISTENCY DETECTED:")
            print(f"   - String recipients: {str_count} ({(str_count/total_messages)*100:.1f}%)")
            print(f"   - Array recipients:  {list_count} ({(list_count/total_messages)*100:.1f}%)")
            
            if str_count > list_count:
                print(f"\n💡 DOMINANT PATTERN: String recipients")
                print(f"   - Array format appears to be exceptional/erroneous")
            else:
                print(f"\n💡 DOMINANT PATTERN: Array recipients")
                print(f"   - String format appears to be exceptional/erroneous")
                
            # Analyze array contents
            print(f"\n🔍 ARRAY RECIPIENT ANALYSIS:")
            if 'list' in examples:
                for example in examples['list']:
                    to_list = example['to']
                    print(f"   - {example['id']}: {len(to_list)} recipients -> {to_list}")
        
        elif 'str' in recipient_types:
            print("✅ CONSISTENT SCHEMA: All recipients are strings")
        elif 'list' in recipient_types:
            print("✅ CONSISTENT SCHEMA: All recipients are arrays")
        
        # Check other schema consistency
        print("\n📋 OTHER FIELD CONSISTENCY CHECK:")
        print("="*60)
        
        # Check content vs body field usage
        content_count = 0
        body_count = 0
        both_count = 0
        neither_count = 0
        
        for msg in all_messages:
            has_content = 'content' in msg and msg['content'] is not None
            has_body = 'body' in msg and msg['body'] is not None
            
            if has_content and has_body:
                both_count += 1
            elif has_content:
                content_count += 1
            elif has_body:
                body_count += 1
            else:
                neither_count += 1
        
        print(f"Content field usage:")
        print(f"   - Only 'content': {content_count} messages")
        print(f"   - Only 'body':    {body_count} messages")
        print(f"   - Both fields:    {both_count} messages")
        print(f"   - Neither field:  {neither_count} messages")
        
        if body_count > 0:
            print(f"\n❌ CONTENT FIELD INCONSISTENCY:")
            print(f"   - Some messages use 'body' instead of 'content'")
            print(f"   - This could cause messages to be missed by readers")
        
        # Final assessment
        print("\n🎯 SCHEMA DEFINITION ASSESSMENT:")
        print("="*60)
        
        issues = []
        if 'str' in recipient_types and 'list' in recipient_types:
            issues.append("Inconsistent recipient field types (string vs array)")
        if body_count > 0:
            issues.append("Inconsistent content field names ('content' vs 'body')")
        if 'missing' in recipient_types:
            issues.append("Messages missing required 'to' field")
        
        if issues:
            print("❌ SCHEMA ISSUES FOUND:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
            
            print("\n💡 ROOT CAUSE:")
            print("   - No formal schema validation in Cosmos DB")
            print("   - Application-level validation is inconsistent")
            print("   - Different message creation paths use different field names")
            print("   - Migration from files may have introduced inconsistencies")
            
            print("\n🔧 RECOMMENDATIONS:")
            print("   1. Implement strict schema validation in CosmosDBManager")
            print("   2. Standardize on 'to' as string, 'cc' as array for multiple recipients")
            print("   3. Always use 'content' field, never 'body'")
            print("   4. Add data cleanup script to fix existing inconsistencies")
            print("   5. Add unit tests to prevent future schema violations")
        else:
            print("✅ SCHEMA IS CONSISTENT")
            print("   - Well-defined message structure")
            print("   - Consistent field usage across all messages")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    main()