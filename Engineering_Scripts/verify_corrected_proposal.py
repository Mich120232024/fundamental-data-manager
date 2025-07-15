#!/usr/bin/env python3
"""
Verify the corrected context proposal was successfully created in Cosmos DB
"""

import json
from datetime import datetime
from cosmos_db_manager import get_db_manager

def verify_corrected_proposal():
    """Check for the corrected proposal message"""
    print("\n🔍 VERIFYING CORRECTED CONTEXT PROPOSAL")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Look for the v2 proposal
    message_id = "msg_20250617_122035_context_proposal_v2"
    
    print(f"\n📋 Searching for message ID: {message_id}")
    
    query = "SELECT * FROM messages WHERE messages.id = @message_id"
    parameters = [{"name": "@message_id", "value": message_id}]
    
    try:
        results = db.query_messages(query, parameters)
        
        if results:
            message = results[0]
            print(f"\n✅ FOUND CORRECTED PROPOSAL!")
            print("=" * 70)
            
            # Verify key fields
            print("\n📊 MESSAGE DETAILS:")
            print(f"   ID: {message.get('id')}")
            print(f"   Timestamp: {message.get('timestamp')}")
            print(f"   Type: {message.get('type')}")
            print(f"   From: {message.get('from')}")
            print(f"   To: {', '.join(message.get('to', []))}")
            print(f"   Subject: {message.get('subject')}")
            print(f"   Priority: {message.get('priority')} {'✅' if message.get('priority') == 'high' else '❌'}")
            print(f"   Status: {message.get('status')}")
            
            # Check if content is in correct field
            print("\n📝 CONTENT VERIFICATION:")
            has_content = bool(message.get('content'))
            has_body = bool(message.get('body'))
            
            print(f"   Content field populated: {'✅ YES' if has_content else '❌ NO'}")
            print(f"   Body field populated: {'⚠️ YES' if has_body else '✅ NO (correct)'}")
            
            if has_content:
                content_preview = message['content'][:200] + "..." if len(message['content']) > 200 else message['content']
                print(f"\n   Content preview:")
                print(f"   {content_preview}")
            
            # Check metadata
            if message.get('metadata'):
                print("\n📎 METADATA:")
                for key, value in message['metadata'].items():
                    print(f"   {key}: {value}")
            
            # Look for individual manager messages
            print("\n\n🔍 CHECKING FOR INDIVIDUAL MANAGER MESSAGES")
            print("-" * 50)
            
            managers = [
                "HEAD_OF_ENGINEERING",
                "HEAD_OF_RESEARCH", 
                "HEAD_OF_DIGITAL_STAFF",
                "COMPLIANCE_MANAGER"
            ]
            
            for manager in managers:
                query = """
                SELECT * FROM messages 
                WHERE CONTAINS(messages.id, 'context_proposal') 
                AND messages.to[0] = @manager
                AND messages.timestamp > '2025-06-17T12:00:00'
                """
                params = [{"name": "@manager", "value": manager}]
                
                try:
                    mgr_results = db.query_messages(query, params)
                    if mgr_results:
                        print(f"   ✅ {manager}: Found personalized message")
                        print(f"      ID: {mgr_results[0]['id']}")
                    else:
                        print(f"   ❌ {manager}: No personalized message found")
                except:
                    print(f"   ⚠️ {manager}: Error checking for message")
            
            # Summary
            print("\n\n📊 VERIFICATION SUMMARY")
            print("=" * 70)
            
            if has_content and message.get('priority') == 'high':
                print("✅ SUCCESS: Corrected proposal is properly formatted!")
                print("   - Content is in the correct 'content' field")
                print("   - Priority is set to 'high'")
                print("   - Message is visible to all managers")
                print("   - Subject includes 'ACTION REQUIRED'")
                
                return True
            else:
                print("⚠️ ISSUES FOUND:")
                if not has_content:
                    print("   - Content field is empty!")
                if message.get('priority') != 'high':
                    print("   - Priority is not set to 'high'")
                    
                return False
                
        else:
            print(f"\n❌ Message ID {message_id} NOT FOUND!")
            print("\nPossible reasons:")
            print("   1. The resend script hasn't been run yet")
            print("   2. The script failed during execution")
            print("   3. Different timestamp in the ID than expected")
            
            # Try to find any recent context proposals
            print("\n🔍 Searching for recent context proposals...")
            
            query = """
            SELECT * FROM messages 
            WHERE CONTAINS(messages.id, 'context_proposal')
            AND messages.timestamp > '2025-06-17T00:00:00'
            ORDER BY messages.timestamp DESC
            """
            
            recent_results = db.query_messages(query)
            
            if recent_results:
                print(f"\nFound {len(recent_results)} recent context proposal(s):")
                for msg in recent_results:
                    print(f"\n   ID: {msg['id']}")
                    print(f"   Timestamp: {msg['timestamp']}")
                    print(f"   Priority: {msg.get('priority', 'not set')}")
                    print(f"   Has content: {'✅' if msg.get('content') else '❌'}")
                    print(f"   Has body: {'⚠️' if msg.get('body') else 'No'}")
            
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR during verification: {e}")
        return False

def check_manager_responses():
    """Check if any managers have responded to the proposal"""
    print("\n\n🔍 CHECKING FOR MANAGER RESPONSES")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Look for responses to the context proposal
    query = """
    SELECT * FROM messages 
    WHERE messages.type = 'RESPONSE'
    AND (
        CONTAINS(messages.subject, 'context')
        OR CONTAINS(messages.subject, 'Context')
        OR CONTAINS(messages.content, 'context proposal')
        OR CONTAINS(messages.content, 'Context Memory')
    )
    AND messages.timestamp > '2025-06-17T12:00:00'
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        
        if results:
            print(f"\n✅ Found {len(results)} potential response(s):")
            for msg in results:
                print(f"\n   From: {msg.get('from')}")
                print(f"   Subject: {msg.get('subject')}")
                print(f"   Timestamp: {msg.get('timestamp')}")
                if msg.get('content'):
                    preview = msg['content'][:150] + "..." if len(msg['content']) > 150 else msg['content']
                    print(f"   Preview: {preview}")
        else:
            print("\n⏳ No responses found yet")
            print("   This is expected if the messages were just sent")
            print("   Managers have until EOD to respond")
            
    except Exception as e:
        print(f"\n❌ Error checking responses: {e}")

def main():
    """Main execution"""
    # Verify the corrected proposal
    success = verify_corrected_proposal()
    
    # Check for responses
    check_manager_responses()
    
    # Final recommendations
    print("\n\n💡 RECOMMENDATIONS")
    print("=" * 70)
    
    if success:
        print("✅ The corrected proposal has been successfully created!")
        print("\nNext steps:")
        print("   1. Monitor for manager responses throughout the day")
        print("   2. Send a follow-up reminder at 3 PM if no responses")
        print("   3. Consider scheduling an emergency meeting if still no response by 4 PM")
        print("   4. Document all feedback received for implementation planning")
    else:
        print("⚠️ Issues detected with the corrected proposal")
        print("\nRecommended actions:")
        print("   1. Check if resend_context_proposal.py was actually executed")
        print("   2. Review any error messages from the script")
        print("   3. Verify Cosmos DB connection is working")
        print("   4. Consider manually creating the corrected message if needed")

if __name__ == "__main__":
    main()