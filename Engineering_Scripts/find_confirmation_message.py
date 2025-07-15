#!/usr/bin/env python3
"""
Find specific HEAD_OF_ENGINEERING message about confirming new setup
"""

import os
import sys
from datetime import datetime, timedelta
from cosmos_db_manager import CosmosDBManager
import json

def find_confirmation_message():
    """Find the specific message about confirming new setup"""
    db = CosmosDBManager()
    
    print("Searching for HEAD_OF_ENGINEERING messages about confirming new setup...\n")
    
    # Search in messages from the last day
    end_date = datetime.now().isoformat() + 'Z'
    start_date = (datetime.now() - timedelta(days=1)).isoformat() + 'Z'
    
    # Query for messages from HEAD_OF_ENGINEERING containing key terms
    query = """
    SELECT * FROM messages 
    WHERE messages['from'] = 'HEAD_OF_ENGINEERING'
    AND messages.timestamp >= @start_date
    AND (CONTAINS(messages.content, 'confirm') 
         OR CONTAINS(messages.content, 'setup')
         OR CONTAINS(messages.content, 'new')
         OR CONTAINS(messages.subject, 'confirm')
         OR CONTAINS(messages.subject, 'setup')
         OR CONTAINS(messages.subject, 'new'))
    ORDER BY messages.timestamp DESC
    """
    parameters = [{"name": "@start_date", "value": start_date}]
    
    messages = db.query_messages(query, parameters)
    print(f"Found {len(messages)} potential messages\n")
    
    # Also look for messages TO HEAD_OF_ENGINEERING asking for confirmation
    # Using unified query pattern to handle both string and array recipients
    query2 = """
    SELECT * FROM messages 
    WHERE (messages['to'] = 'HEAD_OF_ENGINEERING' OR ARRAY_CONTAINS(messages['to'], 'HEAD_OF_ENGINEERING'))
    AND messages.timestamp >= @start_date
    AND (CONTAINS(messages.content, 'confirm') 
         OR CONTAINS(messages.content, 'setup')
         OR CONTAINS(messages.subject, 'confirm')
         OR CONTAINS(messages.subject, 'setup'))
    ORDER BY messages.timestamp DESC
    """
    
    to_messages = db.query_messages(query2, parameters)
    print(f"Found {len(to_messages)} messages TO HEAD_OF_ENGINEERING about confirmation\n")
    
    # Display all relevant messages
    all_messages = messages + to_messages
    
    for msg in all_messages:
        content = msg.get('content', '')
        subject = msg.get('subject', '')
        
        # Convert to string if content is a dict
        if isinstance(content, dict):
            content_str = json.dumps(content, indent=2)
        else:
            content_str = str(content)
            
        # Check if this is likely the message about confirming new setup
        if any(phrase in content_str.lower() or phrase in subject.lower() 
               for phrase in ['confirm', 'new setup', 'confirmation', 'ready']):
            
            print("=" * 80)
            print("POTENTIAL MATCH:")
            print("=" * 80)
            print(f"ID: {msg.get('id', 'N/A')}")
            print(f"Timestamp: {msg.get('timestamp', 'N/A')}")
            print(f"From: {msg.get('from', 'N/A')}")
            print(f"To: {msg.get('to', 'N/A')}")
            print(f"Subject: {msg.get('subject', 'N/A')}")
            print(f"Type: {msg.get('type', 'N/A')}")
            print(f"Priority: {msg.get('priority', 'N/A')}")
            print(f"\nCONTENT:")
            print("-" * 80)
            print(content_str)
            print("\n" + "=" * 80 + "\n")
    
    # Also check the very latest messages
    print("\n\nChecking the 5 most recent messages in the system...")
    latest_query = """
    SELECT TOP 5 * FROM messages 
    ORDER BY messages.timestamp DESC
    """
    
    latest = db.query_messages(latest_query)
    for msg in latest:
        if msg.get('from') == 'HEAD_OF_ENGINEERING' or msg.get('to') == 'HEAD_OF_ENGINEERING':
            print(f"\nLatest message involving HEAD_OF_ENGINEERING:")
            print(f"From: {msg.get('from')} -> To: {msg.get('to')}")
            print(f"Subject: {msg.get('subject')}")
            print(f"Timestamp: {msg.get('timestamp')}")
            content = msg.get('content', '')
            if isinstance(content, dict):
                print(f"Content: {json.dumps(content, indent=2)[:500]}...")
            else:
                print(f"Content: {str(content)[:500]}...")

if __name__ == "__main__":
    try:
        find_confirmation_message()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()