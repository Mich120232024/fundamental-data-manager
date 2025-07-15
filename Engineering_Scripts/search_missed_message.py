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

# Search for messages containing the specific text
search_terms = [
    "Research metadata requirements",
    "Container prioritization decisions", 
    "Knowledge relationship structure recommendations",
    "HEAD_OF_ENGINEERING wants our specific input"
]

print("Searching for messages containing specific phrases...\n")

all_messages = list(messages.read_all_items())

for term in search_terms:
    matches = []
    for msg in all_messages:
        content = msg.get('content', '')
        if isinstance(content, dict):
            content = str(content)
        if term in content:
            matches.append(msg)
    
    print(f"Messages containing '{term}': {len(matches)}")
    
    if matches:
        for msg in matches[:2]:  # Show first 2
            print(f"  - {msg.get('from', '?')} → {msg.get('to', '?')}")
            print(f"    Subject: {msg.get('subject', 'No subject')}")
            print(f"    Date: {msg.get('timestamp', '?')}")
            print(f"    ID: {msg.get('id', '?')}")
            print()

# Also search in subjects
print("\nSearching in subjects...")
subject_matches = []
for msg in all_messages:
    subject = str(msg.get('subject', '')).lower()
    if any(word in subject for word in ['metadata', 'prioritization', 'relationship']):
        if 'research' in subject or 'HEAD_OF_RESEARCH' in msg.get('from', ''):
            subject_matches.append(msg)

print(f"\nFound {len(subject_matches)} messages with relevant subjects")

# Show recent ones
subject_matches.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
for msg in subject_matches[:5]:
    print(f"\n- {msg.get('from', '?')} → {msg.get('to', '?')}")
    print(f"  Subject: {msg.get('subject', 'No subject')}")
    print(f"  Date: {msg.get('timestamp', '?')}")
    
# Check if the message might be embedded in another message
print("\n\nChecking for quoted/forwarded messages...")
for msg in all_messages:
    content = msg.get('content', '')
    if isinstance(content, dict):
        content = str(content)
    if '—HEAD_OF_RESEARCH' in content and 'specific input on:' in content:
        print(f"\nFound potential match:")
        print(f"- {msg.get('from', '?')} → {msg.get('to', '?')}")
        print(f"  Subject: {msg.get('subject', 'No subject')}")
        print(f"  Date: {msg.get('timestamp', '?')}")
        print(f"  ID: {msg.get('id', '?')}")
        
        # Show the relevant part
        lines = content.split('\n')
        start_showing = False
        for i, line in enumerate(lines):
            if 'HEAD_OF_ENGINEERING wants our specific input' in line:
                start_showing = True
            if start_showing and i < len(lines) - 1:
                print(f"  > {line}")
                if '—HEAD_OF_RESEARCH' in line:
                    break