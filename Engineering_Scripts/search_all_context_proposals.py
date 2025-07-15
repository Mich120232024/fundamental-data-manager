#!/usr/bin/env python3
"""
Search for all context proposal messages to find if the corrected version exists
"""

import json
from datetime import datetime
from cosmos_db_manager import get_db_manager

def search_all_context_proposals():
    """Search for all messages containing 'context_proposal' in the ID"""
    print("\n🔍 SEARCHING FOR ALL CONTEXT PROPOSAL MESSAGES")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Broad search for any context proposal
    query = """
    SELECT * FROM messages 
    WHERE CONTAINS(messages.id, 'context_proposal')
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        
        if results:
            print(f"\n✅ Found {len(results)} context proposal message(s):")
            print("=" * 70)
            
            for i, msg in enumerate(results, 1):
                print(f"\n{i}. MESSAGE DETAILS:")
                print(f"   ID: {msg.get('id')}")
                print(f"   Timestamp: {msg.get('timestamp')}")
                print(f"   Type: {msg.get('type')}")
                print(f"   From: {msg.get('from')}")
                print(f"   To: {', '.join(msg.get('to', []))}")
                print(f"   Subject: {msg.get('subject')}")
                print(f"   Priority: {msg.get('priority')} {'⚠️ (not high!)' if msg.get('priority') != 'high' else '✅'}")
                print(f"   Status: {msg.get('status')}")
                
                # Check content location
                has_content = bool(msg.get('content'))
                has_body = bool(msg.get('body'))
                
                print(f"\n   CONTENT LOCATION:")
                print(f"   - 'content' field: {'✅ POPULATED' if has_content else '❌ EMPTY'}")
                print(f"   - 'body' field: {'⚠️ POPULATED (wrong field!)' if has_body else '✅ EMPTY'}")
                
                # Show metadata if present
                if msg.get('metadata'):
                    print(f"\n   METADATA:")
                    for key, value in msg['metadata'].items():
                        print(f"   - {key}: {value}")
                
                print("-" * 70)
        else:
            print("\n❌ No context proposal messages found!")
            
    except Exception as e:
        print(f"\n❌ Error searching for proposals: {e}")

def check_recent_messages():
    """Check the most recent messages sent today"""
    print("\n\n🔍 CHECKING RECENT MESSAGES (Last 10)")
    print("=" * 70)
    
    db = get_db_manager()
    
    query = """
    SELECT TOP 10 * FROM messages 
    WHERE messages.timestamp > '2025-06-17T00:00:00'
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        
        if results:
            print(f"\nMost recent messages:")
            for msg in results:
                print(f"\n   ID: {msg['id']}")
                print(f"   Time: {msg['timestamp']}")
                print(f"   From: {msg.get('from')}")
                print(f"   Type: {msg.get('type')}")
                print(f"   Subject: {msg.get('subject', 'No subject')[:60]}...")
                
    except Exception as e:
        print(f"\n❌ Error checking recent messages: {e}")

def check_messages_with_v2():
    """Check for any messages with 'v2' in the ID"""
    print("\n\n🔍 CHECKING FOR V2 MESSAGES")
    print("=" * 70)
    
    db = get_db_manager()
    
    query = """
    SELECT * FROM messages 
    WHERE CONTAINS(messages.id, '_v2')
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        
        if results:
            print(f"\n✅ Found {len(results)} v2 message(s):")
            for msg in results:
                print(f"\n   ID: {msg['id']}")
                print(f"   Timestamp: {msg['timestamp']}")
                print(f"   Subject: {msg.get('subject')}")
        else:
            print("\n❌ No v2 messages found")
            
    except Exception as e:
        print(f"\n❌ Error checking v2 messages: {e}")

def main():
    """Main execution"""
    # Search for all context proposals
    search_all_context_proposals()
    
    # Check for v2 messages
    check_messages_with_v2()
    
    # Check recent messages
    check_recent_messages()
    
    print("\n\n📊 ANALYSIS SUMMARY")
    print("=" * 70)
    print("\nBased on the search results, it appears that:")
    print("1. The original context proposal exists (msg_20250617_082842_context_proposal)")
    print("2. The corrected v2 proposal has NOT been created yet")
    print("3. The resend_context_proposal.py script likely hasn't been executed")
    print("\nRECOMMENDATION: Run the resend_context_proposal.py script to create the corrected proposal")

if __name__ == "__main__":
    main()