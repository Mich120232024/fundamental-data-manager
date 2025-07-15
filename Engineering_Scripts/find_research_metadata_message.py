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

# Get all messages
all_messages = list(messages.read_all_items())
print(f"Total messages: {len(all_messages)}")

# Find messages from HEAD_OF_RESEARCH to HEAD_OF_ENGINEERING
research_to_eng = [m for m in all_messages if 
                   m.get('from') == 'HEAD_OF_RESEARCH' and 
                   m.get('to') == 'HEAD_OF_ENGINEERING']

print(f"\nMessages from HEAD_OF_RESEARCH to HEAD_OF_ENGINEERING: {len(research_to_eng)}")

# Sort by date
research_to_eng.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

# Show all of them
for i, msg in enumerate(research_to_eng):
    print(f"\n{i+1}. Date: {msg.get('timestamp', 'Unknown')}")
    print(f"   Subject: {msg.get('subject', 'No subject')}")
    print(f"   ID: {msg.get('id', 'Unknown')}")
    print(f"   Priority: {msg.get('priority', 'normal')}")
    if msg.get('requiresResponse'):
        print("   🔴 REQUIRES RESPONSE")
    
    # Check if this is about metadata
    content = str(msg.get('content', '')).lower()
    subject = str(msg.get('subject', '')).lower()
    
    if 'metadata' in content or 'metadata' in subject:
        print("   ⚠️  MENTIONS METADATA")
    if 'container' in content or 'container' in subject:
        print("   ⚠️  MENTIONS CONTAINER")
    if 'prioritization' in content:
        print("   ⚠️  MENTIONS PRIORITIZATION")
        
    # Show preview of content if it might be the one
    if any(word in content for word in ['metadata', 'container', 'prioritization', 'requirements']):
        print("\n   Content preview:")
        lines = msg.get('content', '').split('\n')
        for line in lines[:10]:
            if line.strip():
                print(f"      {line[:80]}...")

# Also check for messages that might have mentioned this but with different agent names
print("\n\nChecking for messages about research metadata requirements...")
metadata_messages = [m for m in all_messages if
                    ('metadata' in str(m.get('content', '')).lower() and
                     'research' in str(m.get('content', '')).lower() and
                     'requirements' in str(m.get('content', '')).lower())]

print(f"\nFound {len(metadata_messages)} messages about research metadata requirements")

for msg in metadata_messages[:5]:
    print(f"\n- {msg.get('from', '?')} → {msg.get('to', '?')}")
    print(f"  Subject: {msg.get('subject', 'No subject')}")
    print(f"  Date: {msg.get('timestamp', '?')}")
    print(f"  ID: {msg.get('id', '?')}")