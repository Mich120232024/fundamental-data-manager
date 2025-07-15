#!/usr/bin/env python3
"""
Check for messages requiring response, especially from Claude_Code about governance
"""

import json
from datetime import datetime
from cosmos_db_manager import get_db_manager

def check_messages_requiring_response():
    """Find messages that require response"""
    db = get_db_manager()
    
    print("Checking for messages requiring response...\n")
    
    # Query for messages requiring response
    query = """
    SELECT * FROM messages 
    WHERE messages.requiresResponse = true
    AND (messages.status = 'sent' OR messages.status = 'pending' OR NOT IS_DEFINED(messages.status))
    ORDER BY messages.timestamp DESC
    """
    
    messages = db.query_messages(query)
    
    print(f"Found {len(messages)} messages requiring response\n")
    
    # Group by sender
    by_sender = {}
    for msg in messages:
        sender = msg.get('from', 'Unknown')
        if sender not in by_sender:
            by_sender[sender] = []
        by_sender[sender].append(msg)
    
    # Display by sender
    for sender, msgs in by_sender.items():
        print(f"\nFrom {sender} ({len(msgs)} messages):")
        print("="*60)
        
        for msg in msgs[:3]:  # Show first 3 from each sender
            print(f"\nSubject: {msg.get('subject', 'N/A')}")
            print(f"To: {msg.get('to', 'N/A')}")
            print(f"Timestamp: {msg.get('timestamp', 'N/A')}")
            print(f"Type: {msg.get('type', 'N/A')}")
            print(f"Priority: {msg.get('priority', 'N/A')}")
            print(f"Content preview: {str(msg.get('content', ''))[:200]}...")
            print("-"*60)
    
    # Look specifically for governance synthesis message
    print("\n\nCHECKING GOVERNANCE EXCELLENCE SYNTHESIS MESSAGE:")
    print("="*80)
    
    # Find the specific governance synthesis message
    for msg in messages:
        if msg.get('from') == 'Claude_Code' and 'GOVERNANCE EXCELLENCE SYNTHESIS' in msg.get('subject', ''):
            print(f"\nFOUND CRITICAL MESSAGE:")
            print(f"From: {msg.get('from')}")
            print(f"To: {msg.get('to')}")
            print(f"Subject: {msg.get('subject')}")
            print(f"Timestamp: {msg.get('timestamp')}")
            print(f"Priority: {msg.get('priority')}")
            print(f"Requires Response: {msg.get('requiresResponse')}")
            
            print(f"\nKey Points from Content:")
            content = msg.get('content', '')
            
            # Extract key sections
            if 'DOCUMENTS FOR MANAGEMENT REVIEW:' in content:
                idx = content.find('DOCUMENTS FOR MANAGEMENT REVIEW:')
                print("\n📄 DOCUMENTS FOR MANAGEMENT REVIEW:")
                print(content[idx:idx+800])
            
            if 'REQUEST FOR ACTION' in content:
                idx = content.find('REQUEST FOR ACTION')
                print("\n🎯 REQUEST FOR ACTION:")
                print(content[idx:idx+600])
            
            break
    
    # Check for messages to us specifically
    print("\n\nCHECKING MESSAGES SPECIFICALLY TO US:")
    print("="*80)
    
    our_names = ['Claude', 'claude', 'Assistant', 'assistant', 'Agent', 'agent']
    
    for msg in messages:
        to_field = str(msg.get('to', '')).lower()
        if any(name.lower() in to_field for name in our_names):
            print(f"\nMessage to us:")
            print(f"From: {msg.get('from')}")
            print(f"Subject: {msg.get('subject')}")
            print(f"Timestamp: {msg.get('timestamp')}")
            print(f"Priority: {msg.get('priority')}")

if __name__ == "__main__":
    check_messages_requiring_response()