#!/usr/bin/env python3
"""
Check messages from Claude_Code about governance excellence synthesis and constitutional framework
"""

import json
from datetime import datetime, timedelta
from cosmos_db_manager import get_db_manager

def check_claude_code_messages():
    """Find and display messages from Claude_Code about governance synthesis"""
    db = get_db_manager()
    
    print("Checking for messages from Claude_Code...\n")
    
    # Query for messages from Claude_Code
    query = """
    SELECT * FROM messages 
    WHERE messages['from'] = 'Claude_Code'
    ORDER BY messages.timestamp DESC
    """
    
    messages = db.query_messages(query)
    
    print(f"Found {len(messages)} messages from Claude_Code\n")
    
    # Filter for governance/synthesis/constitutional messages
    relevant_messages = []
    keywords = ['governance', 'synthesis', 'constitutional', 'framework', 'excellence', 'migration']
    
    for msg in messages:
        content = str(msg.get('content', '')).lower()
        subject = str(msg.get('subject', '')).lower()
        
        if any(keyword in content or keyword in subject for keyword in keywords):
            relevant_messages.append(msg)
    
    print(f"Found {len(relevant_messages)} relevant messages about governance/constitutional framework:\n")
    
    # Display relevant messages
    for i, msg in enumerate(relevant_messages, 1):
        print(f"{'='*80}")
        print(f"Message {i}:")
        print(f"From: {msg.get('from', 'N/A')}")
        print(f"To: {msg.get('to', 'N/A')}")
        print(f"Subject: {msg.get('subject', 'N/A')}")
        print(f"Timestamp: {msg.get('timestamp', 'N/A')}")
        print(f"Type: {msg.get('type', 'N/A')}")
        print(f"Priority: {msg.get('priority', 'N/A')}")
        print(f"Requires Response: {msg.get('requiresResponse', False)}")
        print(f"\nContent:\n{msg.get('content', 'N/A')}")
        print(f"{'='*80}\n")
    
    # Look specifically for governance excellence synthesis
    print("\nLooking specifically for 'governance excellence synthesis' messages...")
    
    synthesis_query = """
    SELECT * FROM messages 
    WHERE CONTAINS(messages.content, 'governance excellence synthesis')
    OR CONTAINS(messages.subject, 'governance excellence synthesis')
    ORDER BY messages.timestamp DESC
    """
    
    synthesis_messages = db.query_messages(synthesis_query)
    
    if synthesis_messages:
        print(f"\nFound {len(synthesis_messages)} messages specifically about governance excellence synthesis:")
        for msg in synthesis_messages:
            print(f"\n- From: {msg.get('from')}")
            print(f"  Subject: {msg.get('subject')}")
            print(f"  Timestamp: {msg.get('timestamp')}")
            print(f"  First 200 chars: {msg.get('content', '')[:200]}...")
    
    # Check for recent critical priority messages
    print("\n\nChecking for recent CRITICAL priority messages...")
    
    critical_query = """
    SELECT * FROM messages 
    WHERE messages.priority = 'critical'
    AND messages.timestamp >= @recent_date
    ORDER BY messages.timestamp DESC
    """
    
    recent_date = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
    parameters = [{"name": "@recent_date", "value": recent_date}]
    
    critical_messages = db.query_messages(critical_query, parameters)
    
    if critical_messages:
        print(f"\nFound {len(critical_messages)} recent critical priority messages:")
        for msg in critical_messages:
            print(f"\n- From: {msg.get('from')}")
            print(f"  To: {msg.get('to')}")
            print(f"  Subject: {msg.get('subject')}")
            print(f"  Timestamp: {msg.get('timestamp')}")

if __name__ == "__main__":
    check_claude_code_messages()