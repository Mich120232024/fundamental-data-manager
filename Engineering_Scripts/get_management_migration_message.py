#!/usr/bin/env python3

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.cosmos import CosmosClient

# Load .env
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Connect
client = CosmosClient(os.getenv('COSMOS_ENDPOINT'), os.getenv('COSMOS_KEY'))
database = client.get_database_client('research-analytics-db')
messages = database.get_container_client('system_inbox')

# Get the specific message about migration
msg_id = "msg_2025-06-17T11:39:39.129479_2189"

print(f"🔍 Getting message: {msg_id}\n")

try:
    # Query for the specific message
    query = f"SELECT * FROM c WHERE c.id = '{msg_id}'"
    results = list(messages.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    if results:
        msg = results[0]
        print("📧 MIGRATION MESSAGE FOUND!")
        print("="*60)
        print(f"From: {msg.get('from', 'Unknown')}")
        print(f"To: {msg.get('to', 'Unknown')}")
        print(f"Subject: {msg.get('subject', 'No subject')}")
        print(f"Date: {msg.get('timestamp', 'Unknown')}")
        print(f"Priority: {msg.get('priority', 'normal')}")
        print(f"ID: {msg.get('id', 'Unknown')}")
        if msg.get('requiresResponse'):
            print("🔴 REQUIRES RESPONSE")
        print()
        
        # Show full content
        content = msg.get('content', '')
        if content:
            print("CONTENT:")
            print("-" * 40)
            print(content)
        else:
            print("(No content)")
            
    else:
        print("❌ Message not found")
        
        # Let's try to find any recent messages from Management_Team
        print("\nSearching for recent Management_Team messages...")
        
        all_messages = list(messages.read_all_items())
        mgmt_messages = [m for m in all_messages if 
                        m.get('from') == 'Management_Team']
        
        mgmt_messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        print(f"\nFound {len(mgmt_messages)} messages from Management_Team")
        
        for i, msg in enumerate(mgmt_messages[:5]):
            print(f"\n{i+1}. Date: {msg.get('timestamp', 'Unknown')}")
            print(f"   To: {msg.get('to', 'Unknown')}")
            print(f"   Subject: {msg.get('subject', 'No subject')}")
            print(f"   ID: {msg.get('id', 'Unknown')}")
            
            if 'migration' in str(msg.get('subject', '')).lower():
                print("   🏗️  MIGRATION MESSAGE")
                print("\n   Content:")
                content = msg.get('content', '')
                if content:
                    lines = content.split('\n') if isinstance(content, str) else [str(content)]
                    for line in lines[:20]:
                        if line.strip():
                            print(f"   > {line}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()