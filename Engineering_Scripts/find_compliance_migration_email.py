#!/usr/bin/env python3

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.cosmos import CosmosClient
from datetime import datetime, timedelta

# Load .env
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Connect
client = CosmosClient(os.getenv('COSMOS_ENDPOINT'), os.getenv('COSMOS_KEY'))
database = client.get_database_client('research-analytics-db')
messages = database.get_container_client('system_inbox')

print("🔍 Searching for COMPLIANCE_MANAGER messages about migration...\n")

# Get all messages
all_messages = list(messages.read_all_items())

# Today's date for filtering
today = datetime.now().strftime('2025-06-17')  # Adjust if needed

# Find messages from COMPLIANCE_MANAGER
compliance_messages = [m for m in all_messages if 
                      m.get('from') == 'COMPLIANCE_MANAGER']

print(f"Total messages from COMPLIANCE_MANAGER: {len(compliance_messages)}")

# Filter for recent ones (last few days)
recent_compliance = []
for msg in compliance_messages:
    timestamp = msg.get('timestamp', '')
    if timestamp and (timestamp.startswith('2025-06-17') or 
                     timestamp.startswith('2025-06-16') or
                     timestamp.startswith('2025-06-15')):
        recent_compliance.append(msg)

print(f"Recent COMPLIANCE_MANAGER messages: {len(recent_compliance)}")

# Sort by timestamp
recent_compliance.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

# Look for migration-related messages
migration_messages = []
for msg in recent_compliance:
    content = str(msg.get('content', '')).lower()
    subject = str(msg.get('subject', '')).lower()
    
    if any(word in content or word in subject for word in 
           ['migration', 'migrate', 'cosmos', 'container', 'database']):
        migration_messages.append(msg)

print(f"\nMigration-related messages from COMPLIANCE_MANAGER: {len(migration_messages)}")

# Show all recent COMPLIANCE_MANAGER messages
print(f"\n📧 All recent COMPLIANCE_MANAGER messages:")
for i, msg in enumerate(recent_compliance[:10]):
    print(f"\n{i+1}. Date: {msg.get('timestamp', 'Unknown')}")
    print(f"   To: {msg.get('to', 'Unknown')}")
    print(f"   Subject: {msg.get('subject', 'No subject')}")
    print(f"   ID: {msg.get('id', 'Unknown')}")
    print(f"   Priority: {msg.get('priority', 'normal')}")
    
    # Check if migration-related
    content = str(msg.get('content', '')).lower()
    subject = str(msg.get('subject', '')).lower()
    
    if any(word in content or word in subject for word in 
           ['migration', 'migrate', 'cosmos', 'container', 'database']):
        print("   🏗️  MIGRATION-RELATED")
        
        # Show content preview
        full_content = msg.get('content', '')
        if isinstance(full_content, str) and len(full_content) > 0:
            lines = full_content.split('\n')
            print("\n   Content preview:")
            for line in lines[:15]:
                if line.strip():
                    print(f"      {line[:100]}...")
        break  # Show full content for first migration message only

# Also check messages TO COMPLIANCE_MANAGER about migration
print(f"\n\n📥 Messages TO COMPLIANCE_MANAGER about migration:")
to_compliance_migration = [m for m in all_messages if 
                          m.get('to') == 'COMPLIANCE_MANAGER' and
                          any(word in str(m.get('content', '')).lower() or 
                              word in str(m.get('subject', '')).lower() 
                              for word in ['migration', 'migrate', 'cosmos'])]

# Show recent ones
to_compliance_migration.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
for msg in to_compliance_migration[:3]:
    print(f"\n- From: {msg.get('from', 'Unknown')}")
    print(f"  Subject: {msg.get('subject', 'No subject')}")
    print(f"  Date: {msg.get('timestamp', 'Unknown')}")
    print(f"  ID: {msg.get('id', 'Unknown')}")

print(f"\n✅ Search complete. Found {len(migration_messages)} migration messages from COMPLIANCE_MANAGER")