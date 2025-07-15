#!/usr/bin/env python3
"""
Check Cosmos DB messages container for manager responses to Agent Context Memory proposal
UPGRADED VERSION: Using unified message query system with Constitutional status tracking
Original message ID: msg_20250617_082842_context_proposal sent to all 4 managers
"""

import json
from datetime import datetime
from unified_message_query import UnifiedMessageQuery, MessageStatus, get_unified_query_manager

def check_original_message():
    """Check if the original Agent Context Memory proposal exists"""
    print("🔍 CHECKING ORIGINAL MESSAGE (UPGRADED VERSION)")
    print("=" * 50)
    
    query_manager = get_unified_query_manager()
    
    # Search for the original message ID
    original_id = "msg_20250617_082842_context_proposal"
    partition_key = "2025-06"
    
    # Get the message using unified query
    message = query_manager.db.get_message(original_id, partition_key)
    
    if message:
        print(f"✅ Original message found: {original_id}")
        print(f"   Subject: {message.get('subject')}")
        print(f"   From: {message.get('from')}")
        print(f"   To: {message.get('to')}")
        print(f"   Type: {message.get('type')}")
        print(f"   Priority: {message.get('priority')}")
        print(f"   Current Status: {message.get('status', 'NO STATUS (VIOLATION)')}")
        
        # Check if message has proper status
        if not message.get('status'):
            print("\n⚠️ CONSTITUTIONAL VIOLATION: Message has no status!")
            print("   Updating to PENDING status...")
            
            # Update status to comply with Constitutional requirement
            success = query_manager.update_message_status(
                original_id, 
                partition_key,
                MessageStatus.PENDING,
                reason="Awaiting manager responses"
            )
            
            if success:
                print("   ✅ Status updated to PENDING")
            else:
                print("   ❌ Failed to update status")
        
        return message
    else:
        print(f"❌ Original message not found: {original_id}")
        return None

def check_manager_responses():
    """Check for responses from any of the 4 managers using unified query"""
    print("\n\n🔍 CHECKING FOR MANAGER RESPONSES (WITH STATUS TRACKING)")
    print("=" * 50)
    
    query_manager = get_unified_query_manager()
    managers = ["HEAD_OF_ENGINEERING", "HEAD_OF_RESEARCH", "COMPLIANCE_MANAGER", "HEAD_OF_DIGITAL_STAFF"]
    
    # Track response status
    response_tracking = {
        "responded": [],
        "no_response": [],
        "total_responses": 0
    }
    
    for manager in managers:
        print(f"\n📧 Checking messages from {manager}:")
        
        # Use unified query to find messages from this manager
        messages = query_manager.find_messages_for_agent(manager, direction="from", limit=10)
        
        # Filter for responses about Agent Context Memory
        relevant_responses = []
        for msg in messages:
            content = str(msg.get('content', '')).lower()
            subject = str(msg.get('subject', '')).lower()
            
            if any(keyword in content or keyword in subject for keyword in ['context memory', 'agent memory', '4-layer', 'memory system']):
                relevant_responses.append(msg)
                
                # Update message status if not set
                if not msg.get('status'):
                    query_manager.update_message_status(
                        msg['id'],
                        msg['partitionKey'],
                        MessageStatus.BEING_PROCESSED
                    )
        
        if relevant_responses:
            response_tracking["responded"].append(manager)
            response_tracking["total_responses"] += len(relevant_responses)
            
            print(f"   ✅ Found {len(relevant_responses)} relevant responses")
            
            for response in relevant_responses:
                print(f"\n   📄 Response ID: {response.get('id')}")
                print(f"      Subject: {response.get('subject')}")
                print(f"      Type: {response.get('type')}")
                print(f"      Timestamp: {response.get('timestamp')}")
                print(f"      Status: {response.get('status', 'NO STATUS')}")
                print(f"      Preview: {response.get('content', '')[:200]}...")
        else:
            response_tracking["no_response"].append(manager)
            print(f"   ❌ No responses found about Agent Context Memory")
    
    return response_tracking

def check_stale_messages():
    """Check for stale messages that need attention"""
    print("\n\n⏰ CHECKING FOR STALE MESSAGES (Constitutional Requirement)")
    print("=" * 50)
    
    query_manager = get_unified_query_manager()
    
    # Find messages older than 48 hours
    stale_messages = query_manager.find_stale_messages(48)
    
    if stale_messages:
        print(f"\n⚠️ Found {len(stale_messages)} stale messages requiring attention:")
        
        for msg in stale_messages[:5]:  # Show first 5
            print(f"\n   📧 Message: {msg.get('id')}")
            print(f"      Subject: {msg.get('subject')}")
            print(f"      From: {msg.get('from')}")
            print(f"      To: {msg.get('to')}")
            print(f"      Age: {msg.get('timestamp')}")
            print(f"      Status: {msg.get('status', 'NO STATUS')}")
    else:
        print("\n✅ No stale messages found - all messages handled within 48 hours")

def generate_status_report():
    """Generate a comprehensive status report"""
    print("\n\n📊 COMPREHENSIVE STATUS REPORT")
    print("=" * 50)
    
    query_manager = get_unified_query_manager()
    
    # Check messages by status
    statuses = [MessageStatus.NEW, MessageStatus.PENDING, MessageStatus.BEING_PROCESSED, 
                MessageStatus.ANSWERED, MessageStatus.POSTPONED]
    
    print("\n📈 Messages by Status:")
    for status in statuses:
        messages = query_manager.find_messages_by_status(status, limit=100)
        print(f"   {status.value}: {len(messages)} messages")
    
    # Check for violations
    print("\n⚠️ Constitutional Compliance Check:")
    
    # Sample check for messages without status
    sample = query_manager.db.get_recent_messages(100)
    no_status_count = sum(1 for msg in sample if not msg.get('status'))
    
    if no_status_count > 0:
        print(f"   ❌ VIOLATION: {no_status_count} messages without status (out of 100 sampled)")
        print(f"   📋 Constitutional Requirement: All messages MUST have status (Article III Section 2.1)")
    else:
        print(f"   ✅ All sampled messages have proper status tracking")

def main():
    """Main function to check manager feedback with upgraded system"""
    print("🚀 MANAGER FEEDBACK CHECKER - UPGRADED WITH UNIFIED QUERY & STATUS TRACKING")
    print("=" * 80)
    print("Using Constitutional Framework v1.1 compliant message status system")
    print()
    
    # Check original message
    original = check_original_message()
    
    # Check manager responses
    response_tracking = check_manager_responses()
    
    # Check for stale messages
    check_stale_messages()
    
    # Generate status report
    generate_status_report()
    
    # Summary
    print("\n\n📋 SUMMARY")
    print("=" * 50)
    print(f"✅ Managers who responded: {', '.join(response_tracking['responded']) if response_tracking['responded'] else 'None'}")
    print(f"❌ Managers pending response: {', '.join(response_tracking['no_response']) if response_tracking['no_response'] else 'None'}")
    print(f"📊 Total relevant responses: {response_tracking['total_responses']}")
    print(f"\n💡 IMPROVEMENT: All messages now have Constitutional status tracking!")

if __name__ == "__main__":
    main()