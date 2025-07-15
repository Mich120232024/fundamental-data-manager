#!/usr/bin/env python3
"""
Check Cosmos DB messages container for manager responses to Agent Context Memory proposal
Original message ID: msg_20250617_082842_context_proposal sent to all 4 managers
"""

import json
from datetime import datetime
from cosmos_db_manager import get_db_manager

def check_original_message():
    """Check if the original Agent Context Memory proposal exists"""
    print("🔍 CHECKING ORIGINAL MESSAGE")
    print("=" * 50)
    
    db = get_db_manager()
    
    # Search for the original message ID
    original_id = "msg_20250617_082842_context_proposal"
    
    # Query for the original message
    query = "SELECT * FROM messages WHERE messages.id = @message_id"
    parameters = [{"name": "@message_id", "value": original_id}]
    
    try:
        results = db.query_messages(query, parameters)
        
        if results:
            print(f"✅ Original message found: {original_id}")
            original = results[0]
            print(f"   Timestamp: {original.get('timestamp', 'N/A')}")
            print(f"   From: {original.get('from', 'N/A')}")
            print(f"   To: {original.get('to', 'N/A')}")
            print(f"   Subject: {original.get('subject', 'N/A')}")
            print(f"   Type: {original.get('type', 'N/A')}")
            print(f"   Requires Response: {original.get('requiresResponse', 'N/A')}")
            
            # Show snippet of content
            content = original.get('content', '')
            if content:
                snippet = content[:200] + "..." if len(content) > 200 else content
                print(f"   Content preview: {snippet}")
            
            return original
        else:
            print(f"❌ Original message not found: {original_id}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking original message: {e}")
        return None

def check_manager_responses():
    """Check for any responses from the 4 managers"""
    print("\n🔍 CHECKING MANAGER RESPONSES")
    print("=" * 50)
    
    db = get_db_manager()
    
    # List of managers to check
    managers = [
        "HEAD_OF_ENGINEERING",
        "HEAD_OF_RESEARCH",
        "HEAD_OF_SECURITY",
        "HEAD_OF_OPERATIONS"
    ]
    
    # Check for responses from each manager
    responses_found = []
    
    for manager in managers:
        print(f"\n📋 Checking responses from {manager}:")
        
        # Query for messages from this manager after the proposal timestamp
        query = """
        SELECT * FROM messages 
        WHERE messages["from"] = @manager 
        AND messages.timestamp >= @start_time
        ORDER BY messages.timestamp DESC
        """
        
        parameters = [
            {"name": "@manager", "value": manager},
            {"name": "@start_time", "value": "2025-06-17T08:28:42Z"}
        ]
        
        try:
            manager_messages = db.query_messages(query, parameters)
            
            if manager_messages:
                print(f"   Found {len(manager_messages)} messages from {manager}")
                
                # Check each message for context memory references
                for msg in manager_messages:
                    msg_id = msg.get('id', 'N/A')
                    timestamp = msg.get('timestamp', 'N/A')
                    subject = msg.get('subject', '')
                    content = msg.get('content', '')
                    
                    # Check if this message references the context proposal
                    subject_str = str(subject).lower() if subject else ""
                    content_str = str(content).lower() if content else ""
                    
                    is_response = (
                        'context' in subject_str or 
                        'context' in content_str or
                        'memory' in subject_str or
                        'memory' in content_str or
                        'proposal' in subject_str or
                        'proposal' in content_str or
                        'msg_20250617_082842_context_proposal' in content_str
                    )
                    
                    if is_response:
                        print(f"   📝 POTENTIAL RESPONSE FOUND:")
                        print(f"      ID: {msg_id}")
                        print(f"      Timestamp: {timestamp}")
                        print(f"      Subject: {subject}")
                        print(f"      To: {msg.get('to', 'N/A')}")
                        
                        # Show content snippet
                        content_snippet = content[:300] + "..." if len(content) > 300 else content
                        print(f"      Content: {content_snippet}")
                        
                        responses_found.append({
                            'manager': manager,
                            'message': msg
                        })
                    else:
                        print(f"   📄 Other message: {msg_id} - {subject[:50]}...")
                        
            else:
                print(f"   No messages found from {manager} since proposal time")
                
        except Exception as e:
            print(f"   ❌ Error checking {manager}: {e}")
    
    return responses_found

def check_context_related_messages():
    """Search for any messages containing context/memory keywords"""
    print("\n🔍 SEARCHING FOR CONTEXT-RELATED MESSAGES")
    print("=" * 50)
    
    db = get_db_manager()
    
    # Search for messages containing relevant keywords
    keywords = ['context memory', 'agent context', 'memory proposal', 'context proposal']
    
    all_context_messages = []
    
    for keyword in keywords:
        print(f"\n🔎 Searching for: '{keyword}'")
        
        try:
            # Use the search function from cosmos_db_manager
            results = db.search_messages(keyword)
            
            if results:
                print(f"   Found {len(results)} messages containing '{keyword}'")
                
                for msg in results:
                    msg_id = msg.get('id', 'N/A')
                    timestamp = msg.get('timestamp', 'N/A')
                    from_agent = msg.get('from', 'N/A')
                    to_agent = msg.get('to', 'N/A')
                    subject = msg.get('subject', '')
                    
                    print(f"   📝 {msg_id}")
                    print(f"      {timestamp} | {from_agent} → {to_agent}")
                    print(f"      Subject: {subject}")
                    
                    # Check if this is from a manager
                    if from_agent in ["HEAD_OF_ENGINEERING", "HEAD_OF_RESEARCH", "HEAD_OF_SECURITY", "HEAD_OF_OPERATIONS"]:
                        print(f"      ⭐ MANAGER RESPONSE DETECTED!")
                        all_context_messages.append(msg)
                    
                    print()
                    
            else:
                print(f"   No messages found containing '{keyword}'")
                
        except Exception as e:
            print(f"   ❌ Error searching for '{keyword}': {e}")
    
    return all_context_messages

def check_recent_manager_activity():
    """Check recent activity from all managers"""
    print("\n🔍 RECENT MANAGER ACTIVITY")
    print("=" * 50)
    
    db = get_db_manager()
    
    managers = [
        "HEAD_OF_ENGINEERING",
        "HEAD_OF_RESEARCH", 
        "HEAD_OF_SECURITY",
        "HEAD_OF_OPERATIONS"
    ]
    
    for manager in managers:
        print(f"\n📋 Recent activity from {manager}:")
        
        try:
            # Get recent messages from this manager
            recent_messages = db.get_messages_by_agent(manager, direction="from", limit=5)
            
            if recent_messages:
                print(f"   Found {len(recent_messages)} recent messages")
                
                for msg in recent_messages:
                    msg_id = msg.get('id', 'N/A')
                    timestamp = msg.get('timestamp', 'N/A')
                    to_agent = msg.get('to', 'N/A')
                    subject = msg.get('subject', '')
                    
                    print(f"   📄 {msg_id}")
                    print(f"      {timestamp} → {to_agent}")
                    print(f"      Subject: {subject[:80]}...")
                    
            else:
                print(f"   No recent messages found from {manager}")
                
        except Exception as e:
            print(f"   ❌ Error checking {manager}: {e}")

def generate_summary_report(responses_found, context_messages):
    """Generate a summary report of findings"""
    print("\n📊 SUMMARY REPORT")
    print("=" * 50)
    
    # Manager response summary
    print(f"🏢 MANAGER RESPONSES TO CONTEXT PROPOSAL:")
    if responses_found:
        print(f"   Found {len(responses_found)} potential responses")
        for response in responses_found:
            manager = response['manager']
            msg = response['message']
            print(f"   ✅ {manager}: {msg.get('id', 'N/A')}")
    else:
        print("   ❌ No manager responses found to the context proposal")
    
    # Context-related messages summary
    print(f"\n🧠 CONTEXT-RELATED MESSAGES:")
    if context_messages:
        print(f"   Found {len(context_messages)} context-related messages")
        manager_context_msgs = [msg for msg in context_messages if msg.get('from') in [
            "HEAD_OF_ENGINEERING", "HEAD_OF_RESEARCH", "HEAD_OF_SECURITY", "HEAD_OF_OPERATIONS"
        ]]
        if manager_context_msgs:
            print(f"   📋 {len(manager_context_msgs)} from managers")
    else:
        print("   ❌ No context-related messages found")
    
    # Overall status
    print(f"\n🎯 OVERALL STATUS:")
    if responses_found or context_messages:
        print("   ✅ Manager feedback detected - review findings above")
    else:
        print("   ⏳ No manager feedback found yet")
        print("   💡 Managers may still be reviewing the proposal")

def main():
    """Main function to run all checks"""
    print("🔍 CHECKING MANAGER FEEDBACK ON AGENT CONTEXT MEMORY PROPOSAL")
    print("=" * 70)
    print(f"Search Time: {datetime.now().isoformat()}")
    print(f"Target Message ID: msg_20250617_082842_context_proposal")
    print()
    
    # Check if original message exists
    original = check_original_message()
    
    # Check for manager responses
    responses = check_manager_responses()
    
    # Search for context-related messages
    context_messages = check_context_related_messages()
    
    # Check recent manager activity
    check_recent_manager_activity()
    
    # Generate summary
    generate_summary_report(responses, context_messages)
    
    print("\n🏁 ANALYSIS COMPLETE")

if __name__ == "__main__":
    main()