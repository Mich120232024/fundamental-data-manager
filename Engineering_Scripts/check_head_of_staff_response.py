#!/usr/bin/env python3

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.cosmos import CosmosClient
from datetime import datetime

# Load .env
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Connect
client = CosmosClient(os.getenv('COSMOS_ENDPOINT'), os.getenv('COSMOS_KEY'))
database = client.get_database_client('research-analytics-db')
messages = database.get_container_client('system_inbox')

print("🔍 Checking for recent messages from HEAD_OF_DIGITAL_STAFF...")

# Get all messages
all_messages = list(messages.read_all_items())

# Find messages from HEAD_OF_DIGITAL_STAFF to HEAD_OF_ENGINEERING
staff_to_eng = [m for m in all_messages if 
                m.get('from') == 'HEAD_OF_DIGITAL_STAFF' and 
                m.get('to') == 'HEAD_OF_ENGINEERING']

# Sort by timestamp
staff_to_eng.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

print(f"\nTotal messages from HEAD_OF_DIGITAL_STAFF to HEAD_OF_ENGINEERING: {len(staff_to_eng)}")

# Check for very recent ones (last few hours)
recent_cutoff = '2025-06-17T15:00:00Z'  # After we sent the policy notice
very_recent = [m for m in staff_to_eng if m.get('timestamp', '') > recent_cutoff]

print(f"Messages since {recent_cutoff}: {len(very_recent)}")

if very_recent:
    print(f"\n📧 RECENT MESSAGES FROM HEAD_OF_DIGITAL_STAFF:")
    print("="*60)
    
    for msg in very_recent:
        print(f"\nDate: {msg.get('timestamp', 'Unknown')}")
        print(f"Subject: {msg.get('subject', 'No subject')}")
        print(f"ID: {msg.get('id', 'Unknown')}")
        print(f"Priority: {msg.get('priority', 'normal')}")
        if msg.get('requiresResponse'):
            print("🔴 REQUIRES RESPONSE")
        
        # Show content
        content = msg.get('content', '')
        if content:
            print(f"\nCONTENT:")
            print("-" * 40)
            print(content)
        print("="*60)
        
else:
    print("\n📧 Most recent messages from HEAD_OF_DIGITAL_STAFF:")
    print("="*50)
    
    for i, msg in enumerate(staff_to_eng[:3]):
        print(f"\n{i+1}. Date: {msg.get('timestamp', 'Unknown')}")
        print(f"   Subject: {msg.get('subject', 'No subject')}")
        print(f"   ID: {msg.get('id', 'Unknown')}")
        print(f"   Priority: {msg.get('priority', 'normal')}")
        if msg.get('requiresResponse'):
            print("   🔴 REQUIRES RESPONSE")
            
        # Show preview of content for recent ones
        if i == 0:  # Show full content for most recent
            content = msg.get('content', '')
            if content:
                print(f"\n   CONTENT:")
                print("   " + "-" * 38)
                lines = content.split('\n') if isinstance(content, str) else [str(content)]
                for line in lines:
                    if line.strip():
                        print(f"   {line}")

# Also check for any messages sent in response to our policy notice
print(f"\n\n🔍 Checking for responses to our policy implementation notice...")

# Look for messages sent after our notice timestamp
our_notice_time = '2025-06-17T15:42:00Z'
responses = [m for m in all_messages if 
             m.get('timestamp', '') > our_notice_time and
             m.get('to') == 'HEAD_OF_ENGINEERING' and
             ('policy' in str(m.get('subject', '')).lower() or
              'semantic' in str(m.get('subject', '')).lower() or
              'implementation' in str(m.get('subject', '')).lower())]

if responses:
    print(f"\nFound {len(responses)} potential responses to policy notice:")
    for msg in responses:
        print(f"\n- From: {msg.get('from', 'Unknown')}")
        print(f"  Subject: {msg.get('subject', 'No subject')}")
        print(f"  Time: {msg.get('timestamp', 'Unknown')}")
        print(f"  ID: {msg.get('id', 'Unknown')}")
else:
    print("No responses to policy notice found yet.")