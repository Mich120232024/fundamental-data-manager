#!/usr/bin/env python3
"""
Check messages for HEAD_OF_ENGINEERING with proper imports
"""

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from azure.cosmos import CosmosClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import our cosmos manager
from Engineering_Workspace.scripts.cosmos_db_manager import CosmosDBManager, get_db_manager

# Use the manager
db = get_db_manager()

print("🔍 Checking messages for HEAD_OF_ENGINEERING...\n")

# Count total messages
total_query = "SELECT VALUE COUNT(1) FROM c"
total = db.container.query_items(
    query=total_query,
    enable_cross_partition_query=True
).next()

print(f"Total messages in database: {total}")

# Messages TO HEAD_OF_ENGINEERING
to_query = """
SELECT * FROM c 
WHERE c.to_agent = 'HEAD_OF_ENGINEERING' 
ORDER BY c.timestamp DESC
"""

to_messages = list(db.container.query_items(
    query=to_query,
    enable_cross_partition_query=True
))

print(f"\nMessages TO HEAD_OF_ENGINEERING: {len(to_messages)}")

if to_messages:
    print("\nRecent messages TO HEAD_OF_ENGINEERING:")
    for i, msg in enumerate(to_messages[:5]):
        print(f"\n{i+1}. From: {msg.get('from_agent', 'Unknown')}")
        print(f"   Subject: {msg.get('subject', 'No subject')}")
        print(f"   Date: {msg.get('timestamp', 'Unknown')}")
        print(f"   Priority: {msg.get('priority', 'normal').upper()}")
        if msg.get('requires_response'):
            print("   🔴 REQUIRES RESPONSE")

# Messages FROM HEAD_OF_ENGINEERING  
from_query = """
SELECT * FROM c 
WHERE c.from_agent = 'HEAD_OF_ENGINEERING' 
ORDER BY c.timestamp DESC
"""

from_messages = list(db.container.query_items(
    query=from_query,
    enable_cross_partition_query=True
))

print(f"\nMessages FROM HEAD_OF_ENGINEERING: {len(from_messages)}")

# Check for messages mentioning research team
research_query = """
SELECT * FROM c 
WHERE (CONTAINS(LOWER(c.content), 'research') OR 
       CONTAINS(LOWER(c.subject), 'research') OR
       c.from_agent = 'HEAD_OF_RESEARCH' OR 
       c.to_agent = 'HEAD_OF_RESEARCH')
AND c.timestamp > '2025-06-15'
ORDER BY c.timestamp DESC
"""

research_messages = list(db.container.query_items(
    query=research_query,
    enable_cross_partition_query=True
))

print(f"\nRecent messages about RESEARCH: {len(research_messages)}")

if research_messages:
    print("\nRecent research-related messages:")
    for i, msg in enumerate(research_messages[:5]):
        print(f"\n{i+1}. {msg.get('from_agent', '?')} → {msg.get('to_agent', '?')}")
        print(f"   Subject: {msg.get('subject', 'No subject')}")
        print(f"   Date: {msg.get('timestamp', 'Unknown')}")
        
# Look for any message we might have missed from June 16
june16_query = """
SELECT * FROM c 
WHERE c.timestamp >= '2025-06-16' AND c.timestamp < '2025-06-17'
AND (c.to_agent = 'HEAD_OF_ENGINEERING' OR 
     c.from_agent = 'HEAD_OF_RESEARCH' OR
     CONTAINS(LOWER(c.subject), 'metadata') OR
     CONTAINS(LOWER(c.subject), 'container'))
ORDER BY c.timestamp DESC
"""

june16_messages = list(db.container.query_items(
    query=june16_query,
    enable_cross_partition_query=True
))

print(f"\nMessages from June 16 about metadata/containers: {len(june16_messages)}")

if june16_messages:
    print("\nJune 16 messages found:")
    for msg in june16_messages:
        print(f"\n- {msg.get('from_agent', '?')} → {msg.get('to_agent', '?')}")
        print(f"  Subject: {msg.get('subject', 'No subject')}")
        print(f"  ID: {msg.get('id', 'Unknown')}")
        if 'metadata requirements' in str(msg.get('content', '')).lower():
            print("  ⚠️  CONTAINS REQUEST FOR METADATA REQUIREMENTS")