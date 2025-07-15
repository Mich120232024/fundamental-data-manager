#!/usr/bin/env python3

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import os
import json
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

# Get one message to see structure
sample = next(messages.read_all_items(max_item_count=1), None)

if sample:
    print("Sample message structure:")
    print(json.dumps(sample, indent=2, default=str))
    print("\n\nKey fields found:")
    for key in sample.keys():
        print(f"- {key}: {type(sample[key]).__name__}")
        
# Now search properly
print("\n\nSearching with correct field names...")

all_messages = list(messages.read_all_items())

# Check different possible field names
from_fields = ['from_agent', 'from', 'sender', 'fromAgent']
to_fields = ['to_agent', 'to', 'recipient', 'toAgent']

# Find which fields are used
used_from = None
used_to = None

for msg in all_messages[:10]:
    for field in from_fields:
        if field in msg:
            used_from = field
            break
    for field in to_fields:
        if field in msg:
            used_to = field
            break
    if used_from and used_to:
        break

print(f"\nField names found:")
print(f"From field: {used_from}")
print(f"To field: {used_to}")

if used_from and used_to:
    # Now search properly
    eng_messages = [m for m in all_messages if 
                    m.get(used_to) == 'HEAD_OF_ENGINEERING' or 
                    m.get(used_from) == 'HEAD_OF_ENGINEERING']
    
    research_messages = [m for m in all_messages if
                        m.get(used_from) == 'HEAD_OF_RESEARCH' or
                        m.get(used_to) == 'HEAD_OF_RESEARCH']
    
    print(f"\nMessages involving HEAD_OF_ENGINEERING: {len(eng_messages)}")
    print(f"Messages involving HEAD_OF_RESEARCH: {len(research_messages)}")
    
    # Show some
    if eng_messages:
        print("\nHEAD_OF_ENGINEERING messages:")
        for msg in eng_messages[:3]:
            print(f"\n- {msg.get(used_from, '?')} → {msg.get(used_to, '?')}")
            print(f"  Subject: {msg.get('subject', 'No subject')[:60]}...")
            print(f"  Time: {msg.get('timestamp', '?')}")
            
    if research_messages:
        print("\nHEAD_OF_RESEARCH messages:")
        for msg in research_messages[:3]:
            print(f"\n- {msg.get(used_from, '?')} → {msg.get(used_to, '?')}")
            print(f"  Subject: {msg.get('subject', 'No subject')[:60]}...")
            print(f"  Time: {msg.get('timestamp', '?')}")