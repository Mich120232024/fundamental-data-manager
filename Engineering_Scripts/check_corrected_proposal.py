#!/usr/bin/env python3
"""
Check the corrected proposal that HEAD_OF_DIGITAL_STAFF apparently sent
"""

import json
from cosmos_db_manager import get_db_manager

def check_corrected_proposal():
    """Check the corrected proposal message"""
    print("\n🔍 CHECKING CORRECTED PROPOSAL FROM HEAD_OF_DIGITAL_STAFF")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Get the specific message
    msg_id = "msg_2025-06-17T14:53:09.102085_5972"
    
    query = "SELECT * FROM messages WHERE messages.id = @message_id"
    parameters = [{"name": "@message_id", "value": msg_id}]
    
    try:
        results = db.query_messages(query, parameters)
        
        if results:
            msg = results[0]
            
            print("\n✅ FOUND CORRECTED PROPOSAL!")
            print("\n📄 MESSAGE DETAILS:")
            print(f"   ID: {msg.get('id')}")
            print(f"   Timestamp: {msg.get('timestamp')}")
            print(f"   From: {msg.get('from')}")
            print(f"   To: {msg.get('to')}")
            print(f"   Subject: {msg.get('subject')}")
            print(f"   Priority: {msg.get('priority')}")
            print(f"   Type: {msg.get('type')}")
            
            # Check content location
            has_content = bool(msg.get('content'))
            has_body = bool(msg.get('body'))
            
            print(f"\n📝 CONTENT LOCATION:")
            print(f"   Content field: {'✅ POPULATED' if has_content else '❌ EMPTY'}")
            print(f"   Body field: {'✅ POPULATED' if has_body else '❌ EMPTY'}")
            
            # Show the actual content
            if has_content:
                print(f"\n✅ CONTENT FIELD (correct location):")
                content = msg.get('content', '')
                print(content[:1000] + "..." if len(content) > 1000 else content)
            
            if has_body:
                print(f"\n📄 BODY FIELD:")
                body = msg.get('body', '')
                print(body[:500] + "..." if len(body) > 500 else body)
            
            # Check if this is the actual corrected version
            print(f"\n🔍 VERIFICATION:")
            
            # Compare with original
            original_subject = "Proposal for Consolidated Agent Context Memory System"
            corrected_subject = msg.get('subject', '')
            
            if 'ACTION REQUIRED' in corrected_subject:
                print("   ✅ Subject includes 'ACTION REQUIRED'")
            else:
                print("   ❌ Subject missing 'ACTION REQUIRED'")
            
            if msg.get('priority') == 'high':
                print("   ✅ Priority is HIGH")
            else:
                print(f"   ❌ Priority is {msg.get('priority')} (not high)")
            
            if has_content and not has_body:
                print("   ✅ Content in correct field")
            elif has_body and not has_content:
                print("   ❌ Content still in wrong field")
            elif has_content and has_body:
                print("   ⚠️ Content in both fields")
            
            return msg
            
        else:
            print(f"\n❌ Message not found: {msg_id}")
            return None
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

def check_manager_responses_to_corrected():
    """Check if managers responded to the corrected proposal"""
    print("\n\n🔍 CHECKING MANAGER RESPONSES TO CORRECTED PROPOSAL")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Search for responses after the corrected proposal timestamp
    query = """
    SELECT * FROM messages 
    WHERE messages.timestamp > '2025-06-17T14:53:09Z'
    AND messages.from IN ('HEAD_OF_ENGINEERING', 'HEAD_OF_RESEARCH', 'HEAD_OF_DIGITAL_STAFF', 'COMPLIANCE_MANAGER')
    AND (CONTAINS(LOWER(messages.subject), 'context') OR 
         CONTAINS(LOWER(messages.content), 'context') OR
         CONTAINS(LOWER(messages.content), 'memory'))
    ORDER BY messages.timestamp ASC
    """
    
    try:
        results = db.query_messages(query)
        
        if results:
            print(f"\n✅ Found {len(results)} potential manager responses:")
            
            for msg in results:
                print(f"\n📝 {msg.get('id')}")
                print(f"   From: {msg.get('from')}")
                print(f"   Time: {msg.get('timestamp')}")
                print(f"   Subject: {msg.get('subject')}")
                print(f"   To: {msg.get('to')}")
                
                # Check if referencing the corrected proposal
                content = str(msg.get('content', '')).lower()
                if 'msg_2025-06-17t14:53:09' in content or 'corrected proposal' in content:
                    print(f"   ✅ DIRECT RESPONSE TO CORRECTED PROPOSAL!")
        else:
            print("\n❌ No manager responses found to corrected proposal")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

def summary_report():
    """Generate summary report"""
    print("\n\n📊 SUMMARY: CONTEXT PROPOSAL STATUS")
    print("=" * 70)
    
    print("\n📋 TIMELINE:")
    print("1. 2025-06-17T08:28:42 - Original proposal sent (malformed)")
    print("   - Content in wrong field ('body' not 'content')")
    print("   - Normal priority")
    print("   - Sent by SYSTEM_ARCHITECTURE")
    
    print("\n2. 2025-06-17T14:53:09 - Corrected proposal sent")
    print("   - Sent by HEAD_OF_DIGITAL_STAFF")
    print("   - Subject includes 'ACTION REQUIRED'")
    print("   - Need to verify if content is in correct field")
    
    print("\n3. 2025-06-17 onwards - Manager activity")
    print("   - Need to check if managers saw/responded to corrected version")
    
    print("\n💡 KEY FINDING:")
    print("HEAD_OF_DIGITAL_STAFF appears to have sent a corrected version!")
    print("This explains why some managers may have seen the proposal.")

def main():
    """Main execution"""
    # Check the corrected proposal
    corrected = check_corrected_proposal()
    
    # Check for responses
    check_manager_responses_to_corrected()
    
    # Summary
    summary_report()

if __name__ == "__main__":
    main()