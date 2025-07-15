#!/usr/bin/env python3
"""
Find the absolute latest message from HEAD_OF_ENGINEERING
"""

import os
import sys
from datetime import datetime, timedelta
from cosmos_db_manager import CosmosDBManager
import json

def find_latest_message():
    """Find the very latest message from HEAD_OF_ENGINEERING"""
    db = CosmosDBManager()
    
    # Get ALL recent messages, not just from HEAD_OF_ENGINEERING
    print("Getting the latest messages in the system...")
    
    # Query for the most recent messages
    query = """
    SELECT TOP 10 * FROM messages 
    ORDER BY messages.timestamp DESC
    """
    
    latest_messages = db.query_messages(query)
    print(f"Found {len(latest_messages)} latest messages\n")
    
    # Display each message
    for i, msg in enumerate(latest_messages, 1):
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
        
        # Check if this message mentions confirmation or setup
        content = msg.get('content', '')
        subject = msg.get('subject', '')
        
        if 'confirm' in content.lower() or 'confirm' in subject.lower() or \
           'setup' in content.lower() or 'setup' in subject.lower() or \
           'new' in content.lower() or 'new' in subject.lower():
            print("*** RELEVANT TO CONFIRMATION/SETUP ***")
        
        # Print full message data in JSON format for debugging
        print(f"\nFULL MESSAGE DATA:")
        print("-" * 80)
        print(json.dumps(msg, indent=2, default=str))
        print("\n" + "=" * 80 + "\n")
    
    # Also specifically look for messages from HEAD_OF_ENGINEERING about confirming something
    print("\n\nSearching specifically for HEAD_OF_ENGINEERING messages with 'confirm' or 'new'...")
    
    query2 = """
    SELECT * FROM messages 
    WHERE messages['from'] = 'HEAD_OF_ENGINEERING'
    AND (CONTAINS(LOWER(messages.subject), 'confirm') 
         OR CONTAINS(LOWER(messages.subject), 'new')
         OR CONTAINS(LOWER(messages.subject), 'setup'))
    ORDER BY messages.timestamp DESC
    OFFSET 0 LIMIT 5
    """
    
    confirm_messages = db.query_messages(query2)
    print(f"Found {len(confirm_messages)} messages from HEAD_OF_ENGINEERING about confirmation/new/setup\n")
    
    for msg in confirm_messages:
        print(f"Subject: {msg.get('subject')}")
        print(f"To: {msg.get('to')}")
        print(f"Timestamp: {msg.get('timestamp')}")
        print(f"Content preview: {str(msg.get('content', ''))[:200]}...")
        print("-" * 80)

if __name__ == "__main__":
    try:
        find_latest_message()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()