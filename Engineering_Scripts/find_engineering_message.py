#!/usr/bin/env python3
"""
Find specific message from HEAD_OF_ENGINEERING about migration/new setup
"""

import os
import sys
from datetime import datetime, timedelta
from cosmos_db_manager import CosmosDBManager

def find_engineering_messages():
    """Find recent messages from HEAD_OF_ENGINEERING"""
    db = CosmosDBManager()
    
    # Get messages from last 24 hours
    end_date = datetime.now().isoformat() + 'Z'
    start_date = (datetime.now() - timedelta(hours=24)).isoformat() + 'Z'
    
    print(f"Searching for messages from HEAD_OF_ENGINEERING...")
    print(f"Time range: {start_date} to {end_date}\n")
    
    # Query 1: All recent messages from HEAD_OF_ENGINEERING
    query1 = """
    SELECT * FROM messages 
    WHERE messages['from'] = 'HEAD_OF_ENGINEERING'
    AND messages.timestamp >= @start_date
    ORDER BY messages.timestamp DESC
    """
    parameters1 = [{"name": "@start_date", "value": start_date}]
    
    print("Executing query for messages FROM HEAD_OF_ENGINEERING...")
    messages_from = db.query_messages(query1, parameters1)
    print(f"Found {len(messages_from)} messages from HEAD_OF_ENGINEERING\n")
    
    # Query 2: Messages mentioning migration/setup/confirmation
    query2 = """
    SELECT * FROM messages 
    WHERE messages.timestamp >= @start_date
    AND (CONTAINS(LOWER(messages.content), 'migration') 
         OR CONTAINS(LOWER(messages.content), 'setup')
         OR CONTAINS(LOWER(messages.content), 'confirm')
         OR CONTAINS(LOWER(messages.subject), 'migration')
         OR CONTAINS(LOWER(messages.subject), 'setup')
         OR CONTAINS(LOWER(messages.subject), 'confirm'))
    ORDER BY messages.timestamp DESC
    """
    
    print("Executing query for messages about migration/setup/confirmation...")
    relevant_messages = db.query_messages(query2, parameters1)
    print(f"Found {len(relevant_messages)} messages mentioning migration/setup/confirmation\n")
    
    # Display messages from HEAD_OF_ENGINEERING
    print("=" * 80)
    print("MESSAGES FROM HEAD_OF_ENGINEERING:")
    print("=" * 80)
    
    for i, msg in enumerate(messages_from, 1):
        print(f"\n--- Message {i} ---")
        print(f"ID: {msg.get('id', 'N/A')}")
        print(f"Timestamp: {msg.get('timestamp', 'N/A')}")
        print(f"From: {msg.get('from', 'N/A')}")
        print(f"To: {msg.get('to', 'N/A')}")
        print(f"Subject: {msg.get('subject', 'N/A')}")
        print(f"Type: {msg.get('type', 'N/A')}")
        print(f"Priority: {msg.get('priority', 'N/A')}")
        print(f"Requires Response: {msg.get('requiresResponse', False)}")
        print(f"\nContent:\n{'-' * 40}")
        print(msg.get('content', 'No content'))
        print("-" * 80)
    
    # Also check relevant messages that might be from HEAD_OF_ENGINEERING
    print("\n" + "=" * 80)
    print("RELEVANT MESSAGES ABOUT MIGRATION/SETUP/CONFIRMATION:")
    print("=" * 80)
    
    for msg in relevant_messages:
        if msg.get('from') == 'HEAD_OF_ENGINEERING' or msg.get('to') == 'HEAD_OF_ENGINEERING':
            print(f"\n--- Relevant Message ---")
            print(f"ID: {msg.get('id', 'N/A')}")
            print(f"Timestamp: {msg.get('timestamp', 'N/A')}")
            print(f"From: {msg.get('from', 'N/A')}")
            print(f"To: {msg.get('to', 'N/A')}")
            print(f"Subject: {msg.get('subject', 'N/A')}")
            print(f"\nContent Preview:\n{'-' * 40}")
            content = msg.get('content', 'No content')
            # Show first 500 chars if content is long
            if len(content) > 500:
                print(content[:500] + "...")
            else:
                print(content)
            print("-" * 80)

if __name__ == "__main__":
    try:
        find_engineering_messages()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()