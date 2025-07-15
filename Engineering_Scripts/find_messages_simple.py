#!/usr/bin/env python3

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.cosmos import CosmosClient

# Load .env from parent directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Connect to Cosmos
endpoint = os.getenv('COSMOS_ENDPOINT')
key = os.getenv('COSMOS_KEY')
database_name = 'research-analytics-db'

client = CosmosClient(endpoint, key)
database = client.get_database_client(database_name)
messages = database.get_container_client('system_inbox')

print("Searching for messages...\n")

# Get all messages and filter locally
all_messages = list(messages.read_all_items())
print(f"Total messages found: {len(all_messages)}")

# Filter for HEAD_OF_ENGINEERING
eng_messages = [m for m in all_messages if 
                m.get('to_agent') == 'HEAD_OF_ENGINEERING' or 
                m.get('from_agent') == 'HEAD_OF_ENGINEERING']

print(f"\nMessages involving HEAD_OF_ENGINEERING: {len(eng_messages)}")

# Filter for HEAD_OF_RESEARCH  
research_messages = [m for m in all_messages if
                    m.get('from_agent') == 'HEAD_OF_RESEARCH' or
                    m.get('to_agent') == 'HEAD_OF_RESEARCH']

print(f"Messages involving HEAD_OF_RESEARCH: {len(research_messages)}")

# Look for the specific message about metadata
metadata_messages = [m for m in all_messages if
                    'metadata' in str(m.get('subject', '')).lower() or
                    'metadata requirements' in str(m.get('content', '')).lower()]

print(f"\nMessages mentioning metadata: {len(metadata_messages)}")

if metadata_messages:
    print("\nMetadata-related messages:")
    for msg in metadata_messages[:5]:
        print(f"\n- {msg.get('from_agent', '?')} → {msg.get('to_agent', '?')}")
        print(f"  Subject: {msg.get('subject', 'No subject')}")
        print(f"  Date: {msg.get('timestamp', '?')}")
        print(f"  ID: {msg.get('id', '?')}")

# Show recent messages
recent = sorted(all_messages, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
print(f"\n10 Most recent messages:")
for msg in recent:
    print(f"\n- {msg.get('from_agent', '?')} → {msg.get('to_agent', '?')}")
    print(f"  Subject: {msg.get('subject', 'No subject')[:60]}...")
    print(f"  Time: {msg.get('timestamp', '?')}")