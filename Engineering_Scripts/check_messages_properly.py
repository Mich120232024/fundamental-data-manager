#!/usr/bin/env python3
"""
Check messages with proper environment loading
"""

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from azure.cosmos import CosmosClient
import json

# Load environment from parent directory
parent_dir = Path(__file__).parent.parent.parent
env_path = parent_dir / '.env'
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

# Get Cosmos DB settings
endpoint = os.getenv('COSMOS_ENDPOINT')
key = os.getenv('COSMOS_KEY')
database_name = os.getenv('COSMOS_DATABASE', 'research-analytics-db')
container_name = 'messages'

print(f"Endpoint: {endpoint[:30]}..." if endpoint else "Endpoint: NOT SET")
print(f"Database: {database_name}")
print(f"Container: {container_name}")

if not endpoint or not key:
    print("\n❌ Missing Cosmos DB credentials!")
    sys.exit(1)

try:
    # Initialize Cosmos client
    client = CosmosClient(endpoint, key)
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    
    print("\n✅ Connected to Cosmos DB successfully!")
    
    # Query for HEAD_OF_ENGINEERING messages
    print("\n📧 Checking messages for HEAD_OF_ENGINEERING...")
    
    # Messages TO HEAD_OF_ENGINEERING
    to_query = """
    SELECT * FROM c 
    WHERE c.to_agent = 'HEAD_OF_ENGINEERING' 
    ORDER BY c.timestamp DESC
    """
    
    to_messages = list(container.query_items(
        query=to_query,
        enable_cross_partition_query=True
    ))
    
    print(f"\nMessages TO HEAD_OF_ENGINEERING: {len(to_messages)}")
    
    # Show recent ones
    if to_messages:
        print("\nMost recent 5:")
        for msg in to_messages[:5]:
            print(f"  - From: {msg.get('from_agent', 'Unknown')}")
            print(f"    Subject: {msg.get('subject', 'No subject')}")
            print(f"    Date: {msg.get('timestamp', 'Unknown')}")
            print(f"    Priority: {msg.get('priority', 'normal')}")
            if msg.get('requires_response'):
                print("    🔴 REQUIRES RESPONSE")
            print()
    
    # Messages FROM HEAD_OF_ENGINEERING
    from_query = """
    SELECT * FROM c 
    WHERE c.from_agent = 'HEAD_OF_ENGINEERING' 
    ORDER BY c.timestamp DESC
    """
    
    from_messages = list(container.query_items(
        query=from_query,
        enable_cross_partition_query=True
    ))
    
    print(f"\nMessages FROM HEAD_OF_ENGINEERING: {len(from_messages)}")
    
    # Check for unanswered messages
    print("\n🔍 Checking for messages that may need responses...")
    
    unanswered = []
    for msg in to_messages:
        if msg.get('requires_response'):
            # Check if there's a response
            msg_time = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
            responded = False
            
            for response in from_messages:
                resp_time = datetime.fromisoformat(response['timestamp'].replace('Z', '+00:00'))
                if (response.get('to_agent') == msg.get('from_agent') and 
                    resp_time > msg_time and
                    (msg.get('subject', '') in response.get('subject', '') or
                     msg.get('id', '') in response.get('content', ''))):
                    responded = True
                    break
            
            if not responded:
                unanswered.append(msg)
    
    if unanswered:
        print(f"\n⚠️  Found {len(unanswered)} messages requiring response:")
        for msg in unanswered[:10]:  # Show up to 10
            print(f"\n  From: {msg.get('from_agent')}")
            print(f"  Subject: {msg.get('subject')}")
            print(f"  Date: {msg.get('timestamp')}")
            print(f"  Priority: {msg.get('priority', 'normal').upper()}")
            if 'content' in msg:
                preview = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
                print(f"  Preview: {preview}")
    else:
        print("\n✅ No unanswered messages requiring response")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print(f"   Type: {type(e).__name__}")
    import traceback
    traceback.print_exc()