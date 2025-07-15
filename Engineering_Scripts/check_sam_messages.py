#!/usr/bin/env python3
"""
Check cloud messaging system for messages from SAM
"""

import json
from datetime import datetime
from cosmos_db_manager import CosmosDBManager

def format_content_preview(content, max_length=200):
    """Safely format content preview"""
    if content is None:
        return "No content"
    if isinstance(content, str):
        return content[:max_length] + "..." if len(content) > max_length else content
    else:
        content_str = str(content)
        return content_str[:max_length] + "..." if len(content_str) > max_length else content_str

def check_sam_messages():
    """Query for all messages from SAM"""
    try:
        db = CosmosDBManager()
        
        print("Checking cloud messaging system for messages from SAM...")
        print("=" * 80)
        
        # Query for messages where SAM is the sender
        from_sam_query = """
        SELECT * FROM messages 
        WHERE messages['from'] = 'SAM'
        ORDER BY messages.timestamp DESC
        """
        
        from_sam_messages = db.query_messages(from_sam_query)
        
        print(f"\nFound {len(from_sam_messages)} messages FROM SAM:")
        print("-" * 80)
        
        for msg in from_sam_messages:
            print(f"\nID: {msg.get('id')}")
            print(f"To: {msg.get('to')}")
            print(f"Type: {msg.get('type')}")
            print(f"Subject: {msg.get('subject')}")
            print(f"Timestamp: {msg.get('timestamp')}")
            print(f"Priority: {msg.get('priority', 'medium')}")
            print(f"Requires Response: {msg.get('requiresResponse', False)}")
            print(f"Content Preview: {format_content_preview(msg.get('content'))}")
            print("-" * 40)
        
        # Query for messages mentioning SAM in content
        print(f"\n\nSearching for messages mentioning SAM in content...")
        print("=" * 80)
        
        sam_mention_query = """
        SELECT * FROM messages 
        WHERE CONTAINS(messages.content, 'SAM')
        ORDER BY messages.timestamp DESC
        """
        
        sam_mentions = db.query_messages(sam_mention_query)
        
        print(f"\nFound {len(sam_mentions)} messages mentioning SAM:")
        print("-" * 80)
        
        for msg in sam_mentions:
            if msg.get('from') != 'SAM':  # Don't duplicate messages already shown
                print(f"\nID: {msg.get('id')}")
                print(f"From: {msg.get('from')}")
                print(f"To: {msg.get('to')}")
                print(f"Type: {msg.get('type')}")
                print(f"Subject: {msg.get('subject')}")
                print(f"Timestamp: {msg.get('timestamp')}")
                print(f"Content Preview: {format_content_preview(msg.get('content'))}")
                print("-" * 40)
        
        # Check for messages to HEAD_OF_RESEARCH or Management_Team that might be from SAM
        print(f"\n\nChecking for messages to HEAD_OF_RESEARCH or Management_Team...")
        print("=" * 80)
        
        target_query = """
        SELECT * FROM messages 
        WHERE (messages['to'] = 'HEAD_OF_RESEARCH' 
               OR ARRAY_CONTAINS(messages['to'], 'HEAD_OF_RESEARCH')
               OR messages['to'] = 'Management_Team'
               OR ARRAY_CONTAINS(messages['to'], 'Management_Team'))
        ORDER BY messages.timestamp DESC
        """
        
        target_messages = db.query_messages(target_query)
        
        # Filter for recent ones that might require response
        recent_important = []
        for msg in target_messages:
            if msg.get('requiresResponse') or 'constitutional' in msg.get('subject', '').lower() or 'role review' in msg.get('subject', '').lower():
                recent_important.append(msg)
        
        print(f"\nFound {len(recent_important)} messages requiring attention:")
        print("-" * 80)
        
        for msg in recent_important[:10]:  # Show top 10
            print(f"\nID: {msg.get('id')}")
            print(f"From: {msg.get('from')}")
            print(f"To: {msg.get('to')}")
            print(f"Type: {msg.get('type')}")
            print(f"Subject: {msg.get('subject')}")
            print(f"Timestamp: {msg.get('timestamp')}")
            print(f"Priority: {msg.get('priority', 'medium')}")
            print(f"Requires Response: {msg.get('requiresResponse', False)}")
            print(f"Content Preview: {format_content_preview(msg.get('content'))}")
            print("-" * 40)
        
        # Summary
        print(f"\n\nSUMMARY:")
        print("=" * 80)
        print(f"Total messages FROM SAM: {len(from_sam_messages)}")
        print(f"Total messages mentioning SAM: {len(sam_mentions)}")
        print(f"Messages requiring attention: {len(recent_important)}")
        
        if from_sam_messages:
            most_recent = from_sam_messages[0]
            print(f"\nMost recent message from SAM:")
            print(f"  - Subject: {most_recent.get('subject')}")
            print(f"  - Timestamp: {most_recent.get('timestamp')}")
            print(f"  - To: {most_recent.get('to')}")
            
        # Look for specific requests
        print(f"\n\nSPECIFIC REQUESTS FROM SAM:")
        print("=" * 80)
        
        for msg in from_sam_messages:
            if msg.get('requiresResponse'):
                print(f"\n📌 REQUIRES RESPONSE:")
                print(f"   Subject: {msg.get('subject')}")
                print(f"   To: {msg.get('to')}")
                print(f"   Timestamp: {msg.get('timestamp')}")
                print(f"   Priority: {msg.get('priority', 'medium')}")
                print(f"   Content: {format_content_preview(msg.get('content'), 500)}")
        
    except Exception as e:
        print(f"Error checking SAM messages: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_sam_messages()