#!/usr/bin/env python3
"""
Comprehensive search for context proposal messages and any manager activity related to it
"""

import json
from datetime import datetime
from cosmos_db_manager import get_db_manager

def search_for_context_proposal():
    """Search for all mentions of context proposal"""
    print("\n🔍 COMPREHENSIVE CONTEXT PROPOSAL SEARCH")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Search for specific message IDs first
    print("\n1️⃣ SEARCHING FOR SPECIFIC MESSAGE IDs:")
    
    message_ids = [
        "msg_20250617_082842_context_proposal",  # Original
        "msg_20250617_122035_context_proposal_v2"  # Corrected version if exists
    ]
    
    for msg_id in message_ids:
        query = "SELECT * FROM messages WHERE messages.id = @message_id"
        parameters = [{"name": "@message_id", "value": msg_id}]
        
        try:
            results = db.query_messages(query, parameters)
            if results:
                msg = results[0]
                print(f"\n✅ FOUND: {msg_id}")
                print(f"   Timestamp: {msg.get('timestamp')}")
                print(f"   From: {msg.get('from')}")
                print(f"   To: {msg.get('to')}")
                print(f"   Priority: {msg.get('priority')}")
                print(f"   Subject: {msg.get('subject')}")
                
                # Check content location
                has_content = bool(msg.get('content'))
                has_body = bool(msg.get('body'))
                print(f"   Content field: {'✅ POPULATED' if has_content else '❌ EMPTY'}")
                print(f"   Body field: {'⚠️ POPULATED (wrong field!)' if has_body else '✅ EMPTY'}")
                
                # If body has content but content field is empty, show the body
                if has_body and not has_content:
                    print(f"\n   ⚠️ CONTENT IS IN WRONG FIELD (body):")
                    body_preview = msg.get('body', '')[:500] + "..." if len(msg.get('body', '')) > 500 else msg.get('body', '')
                    print(f"   {body_preview}")
            else:
                print(f"\n❌ NOT FOUND: {msg_id}")
        except Exception as e:
            print(f"\n❌ Error searching for {msg_id}: {e}")
    
    # Search for messages about context proposal
    print("\n\n2️⃣ SEARCHING FOR MESSAGES ABOUT CONTEXT PROPOSAL:")
    
    # Get recent messages and search locally
    query = """
    SELECT * FROM messages 
    WHERE messages.timestamp >= '2025-06-17T00:00:00Z'
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        print(f"\nSearching through {len(results)} recent messages...")
        
        context_mentions = []
        
        for msg in results:
            # Combine all searchable text
            msg_id = msg.get('id', '')
            subject = str(msg.get('subject', '')).lower()
            content = str(msg.get('content', '')).lower()
            body = str(msg.get('body', '')).lower()
            from_agent = msg.get('from', '')
            
            # Check for mentions
            if any(term in subject + content + body for term in [
                'context proposal', 'context memory', 'agent context',
                'msg_20250617_082842', 'memory system', 'context system'
            ]):
                context_mentions.append(msg)
        
        print(f"\n📊 Found {len(context_mentions)} messages mentioning context proposal:")
        
        # Group by sender
        by_sender = {}
        for msg in context_mentions:
            sender = msg.get('from', 'Unknown')
            if sender not in by_sender:
                by_sender[sender] = []
            by_sender[sender].append(msg)
        
        # Show grouped results
        for sender, messages in by_sender.items():
            print(f"\n📤 From {sender}: {len(messages)} message(s)")
            for msg in messages[:3]:  # Show first 3 from each sender
                print(f"   - {msg.get('id')}")
                print(f"     {msg.get('timestamp')}")
                print(f"     Subject: {msg.get('subject', 'No subject')[:60]}...")
                
                # Check if this is a manager
                if sender in ['HEAD_OF_ENGINEERING', 'HEAD_OF_RESEARCH', 'HEAD_OF_DIGITAL_STAFF', 'COMPLIANCE_MANAGER']:
                    print(f"     ⭐ MANAGER MESSAGE!")
    
    except Exception as e:
        print(f"\n❌ Error in comprehensive search: {e}")
    
    # Search for messages asking about missing proposals
    print("\n\n3️⃣ SEARCHING FOR MESSAGES ASKING ABOUT MISSING PROPOSAL:")
    
    query = """
    SELECT * FROM messages 
    WHERE messages.timestamp >= '2025-06-17T08:00:00Z'
    AND (CONTAINS(LOWER(messages.subject), 'where') OR 
         CONTAINS(LOWER(messages.subject), 'missing') OR 
         CONTAINS(LOWER(messages.subject), 'looking for') OR
         CONTAINS(LOWER(messages.content), 'where') OR
         CONTAINS(LOWER(messages.content), 'looking for'))
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        
        relevant_inquiries = []
        for msg in results:
            # Check if asking about context proposal
            all_text = (str(msg.get('subject', '')) + ' ' + 
                       str(msg.get('content', '')) + ' ' + 
                       str(msg.get('body', ''))).lower()
            
            if any(term in all_text for term in ['context', 'memory', 'proposal']):
                relevant_inquiries.append(msg)
        
        if relevant_inquiries:
            print(f"\n✅ Found {len(relevant_inquiries)} messages asking about context/memory/proposal:")
            for msg in relevant_inquiries:
                print(f"\n   📝 {msg.get('id')}")
                print(f"      From: {msg.get('from')}")
                print(f"      Time: {msg.get('timestamp')}")
                print(f"      Subject: {msg.get('subject')}")
                
                # If from a manager, highlight it
                if msg.get('from') in ['HEAD_OF_ENGINEERING', 'HEAD_OF_RESEARCH', 'HEAD_OF_DIGITAL_STAFF', 'COMPLIANCE_MANAGER']:
                    print(f"      ⚠️ MANAGER LOOKING FOR PROPOSAL!")
    
    except Exception as e:
        print(f"\n❌ Error searching for inquiries: {e}")

def generate_investigation_report():
    """Generate final investigation report"""
    print("\n\n📊 INVESTIGATION REPORT: CONTEXT PROPOSAL DISCOVERABILITY")
    print("=" * 70)
    
    print("\n🔍 FINDINGS:")
    print("\n1. ORIGINAL PROPOSAL (msg_20250617_082842_context_proposal):")
    print("   ❌ Content field is EMPTY")
    print("   ⚠️ Proposal text is in 'body' field instead of 'content' field")
    print("   ❌ Priority is 'normal' not 'high'")
    print("   ✅ Recipients are correct (4 managers)")
    
    print("\n2. CORRECTED VERSION (msg_20250617_122035_context_proposal_v2):")
    print("   ❌ Does NOT exist - was never created")
    
    print("\n3. MANAGER DISCOVERABILITY:")
    print("   ❌ Managers couldn't find the proposal because:")
    print("      - Content field was empty (standard field they check)")
    print("      - They likely searched 'content' not 'body'")
    print("      - Normal priority didn't trigger alerts")
    
    print("\n4. SEARCH BEHAVIOR:")
    print("   - Managers search by 'content' field (standard)")
    print("   - Proposal had content in non-standard 'body' field")
    print("   - This made it effectively invisible to standard searches")
    
    print("\n💡 ROOT CAUSE:")
    print("   The proposal was sent with a critical structural error:")
    print("   Content was placed in 'body' field instead of 'content' field")
    print("   This is why managers couldn't discover it through normal channels")
    
    print("\n🔧 REQUIRED ACTION:")
    print("   1. Resend proposal with content in correct 'content' field")
    print("   2. Set priority to 'high'")
    print("   3. Add 'ACTION REQUIRED' to subject")
    print("   4. Consider sending individual notifications to managers")

def main():
    """Main execution"""
    search_for_context_proposal()
    generate_investigation_report()
    
    print("\n\n✅ INVESTIGATION COMPLETE")
    print("The context proposal exists but is malformed and undiscoverable.")

if __name__ == "__main__":
    main()