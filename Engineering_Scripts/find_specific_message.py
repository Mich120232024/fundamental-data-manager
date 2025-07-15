#!/usr/bin/env python3
"""
Find specific message from HEAD_OF_ENGINEERING about confirming new setup
"""

import os
import sys
from datetime import datetime, timedelta
from cosmos_db_manager import CosmosDBManager

def find_specific_messages():
    """Find very recent messages from HEAD_OF_ENGINEERING with full content"""
    db = CosmosDBManager()
    
    # Get messages from last 4 hours (very recent)
    end_date = datetime.now().isoformat() + 'Z'
    start_date = (datetime.now() - timedelta(hours=4)).isoformat() + 'Z'
    
    print(f"Searching for VERY RECENT messages from HEAD_OF_ENGINEERING...")
    print(f"Time range: {start_date} to {end_date}\n")
    
    # Query for very recent messages from HEAD_OF_ENGINEERING
    query = """
    SELECT * FROM messages 
    WHERE messages['from'] = 'HEAD_OF_ENGINEERING'
    AND messages.timestamp >= @start_date
    ORDER BY messages.timestamp DESC
    """
    parameters = [{"name": "@start_date", "value": start_date}]
    
    messages = db.query_messages(query, parameters)
    print(f"Found {len(messages)} very recent messages from HEAD_OF_ENGINEERING\n")
    
    # Display full content of each message
    for i, msg in enumerate(messages, 1):
        print("=" * 80)
        print(f"MESSAGE {i}:")
        print("=" * 80)
        print(f"ID: {msg.get('id', 'N/A')}")
        print(f"Timestamp: {msg.get('timestamp', 'N/A')}")
        print(f"From: {msg.get('from', 'N/A')}")
        print(f"To: {msg.get('to', 'N/A')}")
        print(f"Subject: {msg.get('subject', 'N/A')}")
        print(f"Type: {msg.get('type', 'N/A')}")
        print(f"Priority: {msg.get('priority', 'N/A')}")
        print(f"Requires Response: {msg.get('requiresResponse', False)}")
        
        # Print full content
        print(f"\nFULL CONTENT:")
        print("-" * 80)
        content = msg.get('content', 'No content')
        print(content)
        print("\n" + "=" * 80 + "\n")
    
    # Also search for messages TO HEAD_OF_ENGINEERING about new setup/confirmation
    print("\nSearching for messages TO HEAD_OF_ENGINEERING about setup/confirmation...")
    
    # Using unified query pattern to handle both string and array recipients
    query2 = """
    SELECT * FROM messages 
    WHERE (messages['to'] = 'HEAD_OF_ENGINEERING' OR ARRAY_CONTAINS(messages['to'], 'HEAD_OF_ENGINEERING'))
    AND messages.timestamp >= @start_date
    AND (CONTAINS(LOWER(messages.content), 'setup')
         OR CONTAINS(LOWER(messages.content), 'confirm')
         OR CONTAINS(LOWER(messages.subject), 'setup')
         OR CONTAINS(LOWER(messages.subject), 'confirm'))
    ORDER BY messages.timestamp DESC
    """
    
    messages_to = db.query_messages(query2, parameters)
    print(f"Found {len(messages_to)} messages TO HEAD_OF_ENGINEERING about setup/confirmation\n")
    
    for i, msg in enumerate(messages_to, 1):
        print("=" * 80)
        print(f"MESSAGE TO HEAD_OF_ENGINEERING {i}:")
        print("=" * 80)
        print(f"ID: {msg.get('id', 'N/A')}")
        print(f"Timestamp: {msg.get('timestamp', 'N/A')}")
        print(f"From: {msg.get('from', 'N/A')}")
        print(f"To: {msg.get('to', 'N/A')}")
        print(f"Subject: {msg.get('subject', 'N/A')}")
        
        # Print content preview
        print(f"\nCONTENT PREVIEW:")
        print("-" * 80)
        content = msg.get('content', 'No content')
        if len(content) > 800:
            print(content[:800] + "...")
        else:
            print(content)
        print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    try:
        find_specific_messages()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()