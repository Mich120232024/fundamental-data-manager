#!/usr/bin/env python3
"""
Examine specific messages identified as potential responses to the context proposal
"""

import json
from cosmos_db_manager import get_db_manager

def examine_message(message_id):
    """Examine a specific message by ID"""
    print(f"\n🔍 EXAMINING MESSAGE: {message_id}")
    print("=" * 60)
    
    db = get_db_manager()
    
    # Query for the specific message
    query = "SELECT * FROM messages WHERE messages.id = @message_id"
    parameters = [{"name": "@message_id", "value": message_id}]
    
    try:
        results = db.query_messages(query, parameters)
        
        if results:
            msg = results[0]
            
            print(f"📄 Message Details:")
            print(f"   ID: {msg.get('id', 'N/A')}")
            print(f"   Timestamp: {msg.get('timestamp', 'N/A')}")
            print(f"   From: {msg.get('from', 'N/A')}")
            print(f"   To: {msg.get('to', 'N/A')}")
            print(f"   Type: {msg.get('type', 'N/A')}")
            print(f"   Priority: {msg.get('priority', 'N/A')}")
            print(f"   Subject: {msg.get('subject', 'N/A')}")
            
            # Full content
            content = msg.get('content', '')
            if content:
                print(f"\n📝 Full Content:")
                print("-" * 40)
                print(content)
                print("-" * 40)
            else:
                print(f"\n📝 No content found")
            
            # Check for context-related keywords
            subject_str = str(msg.get('subject', '')).lower()
            content_str = str(content).lower()
            
            context_keywords = ['context', 'memory', 'proposal', 'msg_20250617_082842_context_proposal']
            found_keywords = []
            
            for keyword in context_keywords:
                if keyword in subject_str or keyword in content_str:
                    found_keywords.append(keyword)
            
            if found_keywords:
                print(f"\n🎯 Context-related keywords found: {', '.join(found_keywords)}")
            else:
                print(f"\n❌ No context-related keywords found")
            
            return msg
        else:
            print(f"❌ Message not found: {message_id}")
            return None
            
    except Exception as e:
        print(f"❌ Error examining message: {e}")
        return None

def main():
    """Examine the specific messages flagged as potential responses"""
    
    # Messages identified as potential responses from the previous run
    potential_responses = [
        "2025-06-19T19:45:00Z_0404",
        "2025-06-19T12:45:00Z_0398", 
        "2025-06-19T12:30:00Z_0397"
    ]
    
    print("🔍 EXAMINING POTENTIAL MANAGER RESPONSES")
    print("=" * 70)
    print(f"Found {len(potential_responses)} messages to examine")
    
    for message_id in potential_responses:
        examine_message(message_id)
    
    print("\n🏁 EXAMINATION COMPLETE")
    print("\nSUMMARY:")
    print("- These messages were flagged due to keywords like 'memory', 'proposal'")
    print("- Review the full content to determine if they're related to the context proposal")
    print("- Original proposal ID: msg_20250617_082842_context_proposal")

if __name__ == "__main__":
    main()