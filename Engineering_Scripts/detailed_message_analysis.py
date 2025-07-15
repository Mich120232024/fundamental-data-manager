#!/usr/bin/env python3
"""
Detailed analysis of messages including raw JSON structure
"""

import json
from cosmos_db_manager import get_db_manager

def analyze_message_structure(message_id):
    """Analyze the complete structure of a message"""
    print(f"\n🔍 DETAILED ANALYSIS: {message_id}")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Query for the specific message
    query = "SELECT * FROM messages WHERE messages.id = @message_id"
    parameters = [{"name": "@message_id", "value": message_id}]
    
    try:
        results = db.query_messages(query, parameters)
        
        if results:
            msg = results[0]
            
            print(f"📊 Raw Message Structure:")
            print(json.dumps(msg, indent=2, default=str))
            
            print(f"\n📋 All Fields Present:")
            for key, value in msg.items():
                if isinstance(value, str) and len(value) > 100:
                    value_display = value[:100] + "..."
                else:
                    value_display = value
                print(f"   {key}: {value_display}")
            
            return msg
        else:
            print(f"❌ Message not found: {message_id}")
            return None
            
    except Exception as e:
        print(f"❌ Error analyzing message: {e}")
        return None

def check_original_proposal_detailed():
    """Detailed check of the original proposal message"""
    print("🔍 DETAILED ANALYSIS OF ORIGINAL PROPOSAL")
    print("=" * 70)
    
    original_id = "msg_20250617_082842_context_proposal"
    return analyze_message_structure(original_id)

def search_all_messages_with_context():
    """Search through all messages for any containing context/memory references"""
    print("\n🔍 COMPREHENSIVE SEARCH FOR CONTEXT-RELATED CONTENT")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Get all messages and search locally (more reliable than CONTAINS query)
    query = "SELECT * FROM messages ORDER BY messages.timestamp DESC"
    
    try:
        all_messages = db.query_messages(query)
        print(f"📊 Searching through {len(all_messages)} total messages")
        
        context_related = []
        
        for msg in all_messages:
            msg_id = msg.get('id', '')
            subject = str(msg.get('subject', ''))
            content = str(msg.get('content', ''))
            body = str(msg.get('body', ''))
            
            # Combine all text fields for searching
            all_text = f"{subject} {content} {body}".lower()
            
            # Check for context-related keywords
            keywords = [
                'context memory', 'agent context', 'memory proposal', 
                'context proposal', 'msg_20250617_082842_context_proposal',
                'consolidated agent', 'memory system'
            ]
            
            found_keywords = [kw for kw in keywords if kw in all_text]
            
            # Also check for individual keywords with specific context
            if ('context' in all_text and ('agent' in all_text or 'system' in all_text)) or \
               ('memory' in all_text and ('agent' in all_text or 'system' in all_text or 'context' in all_text)):
                found_keywords.append('contextual_match')
            
            if found_keywords:
                context_related.append({
                    'message': msg,
                    'keywords': found_keywords
                })
        
        print(f"\n📋 Found {len(context_related)} context-related messages:")
        
        for item in context_related:
            msg = item['message']
            keywords = item['keywords']
            
            print(f"\n📝 {msg.get('id', 'N/A')}")
            print(f"   Timestamp: {msg.get('timestamp', 'N/A')}")
            print(f"   From: {msg.get('from', 'N/A')}")
            print(f"   To: {msg.get('to', 'N/A')}")
            print(f"   Subject: {msg.get('subject', 'N/A')}")
            print(f"   Keywords found: {', '.join(keywords)}")
            
            # Show content snippet if available
            content = msg.get('content', '') or msg.get('body', '')
            if content:
                content_snippet = content[:200] + "..." if len(content) > 200 else content
                print(f"   Content: {content_snippet}")
        
        return context_related
        
    except Exception as e:
        print(f"❌ Error in comprehensive search: {e}")
        return []

def main():
    """Main analysis function"""
    print("🔍 DETAILED MESSAGE ANALYSIS FOR CONTEXT PROPOSAL FEEDBACK")
    print("=" * 80)
    
    # First, analyze the original proposal in detail
    print("\n1️⃣ ANALYZING ORIGINAL PROPOSAL MESSAGE")
    original = check_original_proposal_detailed()
    
    # Then analyze the flagged potential responses
    print("\n2️⃣ ANALYZING FLAGGED POTENTIAL RESPONSES")
    potential_responses = [
        "2025-06-19T19:45:00Z_0404",
        "2025-06-19T12:45:00Z_0398",
        "2025-06-19T12:30:00Z_0397"
    ]
    
    for message_id in potential_responses:
        analyze_message_structure(message_id)
    
    # Finally, do a comprehensive search
    print("\n3️⃣ COMPREHENSIVE CONTEXT SEARCH")
    context_messages = search_all_messages_with_context()
    
    # Summary
    print("\n📊 FINAL ANALYSIS SUMMARY")
    print("=" * 50)
    
    if original:
        print("✅ Original proposal message exists and is accessible")
        
        # Check who it was sent to
        recipients = original.get('to', [])
        if isinstance(recipients, list):
            print(f"📧 Sent to {len(recipients)} recipients: {', '.join(recipients)}")
        else:
            print(f"📧 Sent to: {recipients}")
    else:
        print("❌ Original proposal message not found or not accessible")
    
    print(f"\n🎯 Context-related messages found: {len(context_messages) if context_messages else 0}")
    
    # Check if any are from the target managers
    target_managers = ["HEAD_OF_ENGINEERING", "HEAD_OF_RESEARCH", "HEAD_OF_DIGITAL_STAFF", "COMPLIANCE_MANAGER"]
    
    if context_messages:
        manager_responses = [
            msg for msg in context_messages 
            if msg['message'].get('from') in target_managers
        ]
        
        if manager_responses:
            print(f"📋 Manager responses found: {len(manager_responses)}")
            for response in manager_responses:
                msg = response['message']
                print(f"   ✅ {msg.get('from')} - {msg.get('id')} - {msg.get('subject', '')[:50]}...")
        else:
            print("❌ No responses found from target managers")
    
    print("\n🏁 DETAILED ANALYSIS COMPLETE")

if __name__ == "__main__":
    main()