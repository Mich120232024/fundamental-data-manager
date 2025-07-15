#!/usr/bin/env python3
"""
Investigate why the Agent Context Memory proposal email was ignored by managers
"""

import json
from cosmos_db_manager import get_db_manager
from datetime import datetime

def find_context_proposal():
    """Find and examine the context proposal message"""
    print("\n🔍 SEARCHING FOR CONTEXT PROPOSAL MESSAGE")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Query for the specific message ID
    query = "SELECT * FROM messages WHERE messages.id = @message_id"
    parameters = [{"name": "@message_id", "value": "msg_20250617_082842_context_proposal"}]
    
    try:
        results = db.query_messages(query, parameters)
        
        if results:
            msg = results[0]
            print(f"✅ Found message: msg_20250617_082842_context_proposal")
            
            print(f"\n📄 Message Details:")
            print(f"   ID: {msg.get('id', 'N/A')}")
            print(f"   Timestamp: {msg.get('timestamp', 'N/A')}")
            print(f"   From: {msg.get('from', 'N/A')}")
            print(f"   To: {msg.get('to', 'N/A')}")
            print(f"   Type: {msg.get('type', 'N/A')}")
            print(f"   Priority: {msg.get('priority', 'N/A')}")
            print(f"   Subject: {msg.get('subject', 'N/A')}")
            
            # Check metadata
            metadata = msg.get('metadata', {})
            if metadata:
                print(f"\n📊 Metadata:")
                for key, value in metadata.items():
                    print(f"   {key}: {value}")
            
            # Full content
            content = msg.get('content', '')
            if content:
                print(f"\n📝 Full Content:")
                print("-" * 60)
                print(content)
                print("-" * 60)
                
                # Analyze content structure
                print(f"\n📏 Content Analysis:")
                print(f"   Length: {len(content)} characters")
                print(f"   Line count: {len(content.splitlines())}")
                
                # Check for common email formatting issues
                if not content.strip():
                    print("   ⚠️ WARNING: Content is empty or only whitespace!")
                if len(content) > 10000:
                    print("   ⚠️ WARNING: Very long content - might be ignored!")
                if not any(greeting in content.lower() for greeting in ['dear', 'hello', 'hi', 'greetings']):
                    print("   ⚠️ WARNING: No greeting found - might seem impersonal!")
                if 'urgent' in subject.lower() or 'asap' in subject.lower():
                    print("   ⚠️ WARNING: Urgent marking might cause managers to deprioritize!")
            else:
                print(f"\n❌ ERROR: No content found in message!")
            
            return msg
        else:
            print(f"❌ Message NOT FOUND: msg_20250617_082842_context_proposal")
            print("\nPossible reasons:")
            print("- Message was never created")
            print("- Message ID is incorrect")
            print("- Message was deleted")
            return None
            
    except Exception as e:
        print(f"❌ Error finding message: {e}")
        return None

def find_similar_proposals():
    """Find other proposals or similar messages to compare"""
    print("\n\n🔍 SEARCHING FOR OTHER PROPOSALS/SIMILAR MESSAGES")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Search for messages with similar subjects or content
    query = """
    SELECT * FROM messages 
    WHERE (
        CONTAINS(LOWER(messages.subject), 'proposal') OR 
        CONTAINS(LOWER(messages.subject), 'context') OR
        CONTAINS(LOWER(messages.subject), 'memory') OR
        CONTAINS(LOWER(messages.content), 'agent context memory')
    )
    AND messages.timestamp >= '2025-06-15T00:00:00Z'
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        
        print(f"\n📊 Found {len(results)} related messages")
        
        for msg in results[:10]:  # Show first 10
            print(f"\n📄 Message: {msg.get('id', 'N/A')}")
            print(f"   Timestamp: {msg.get('timestamp', 'N/A')}")
            print(f"   From: {msg.get('from', 'N/A')}")
            print(f"   To: {msg.get('to', 'N/A')}")
            print(f"   Subject: {msg.get('subject', 'N/A')}")
            
            # Check if this message got responses
            if 'response' in str(msg.get('type', '')).lower():
                print(f"   ✅ This is a response message!")
        
        return results
            
    except Exception as e:
        print(f"❌ Error searching for similar messages: {e}")
        return []

def find_manager_responses():
    """Find successful manager communications for comparison"""
    print("\n\n🔍 ANALYZING SUCCESSFUL MANAGER COMMUNICATIONS")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Find messages that managers actually responded to
    query = """
    SELECT * FROM messages 
    WHERE messages.type = 'response'
    AND (
        messages.from = 'head_of_engineering@company.com' OR
        messages.from = 'head_of_research@company.com' OR
        messages.from = 'head_of_ai@company.com'
    )
    AND messages.timestamp >= '2025-06-15T00:00:00Z'
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        
        print(f"\n📊 Found {len(results)} manager responses")
        
        responded_to_ids = []
        for msg in results[:5]:  # Analyze first 5
            print(f"\n✅ Manager Response:")
            print(f"   From: {msg.get('from', 'N/A')}")
            print(f"   Timestamp: {msg.get('timestamp', 'N/A')}")
            print(f"   Subject: {msg.get('subject', 'N/A')}")
            
            # Check metadata for what they responded to
            metadata = msg.get('metadata', {})
            if 'in_reply_to' in metadata:
                responded_to_ids.append(metadata['in_reply_to'])
                print(f"   In reply to: {metadata['in_reply_to']}")
        
        # Now check what messages got responses
        if responded_to_ids:
            print(f"\n\n📧 EXAMINING MESSAGES THAT GOT RESPONSES:")
            print("=" * 60)
            
            for msg_id in responded_to_ids[:3]:  # Check first 3
                query = "SELECT * FROM messages WHERE messages.id = @message_id"
                parameters = [{"name": "@message_id", "value": msg_id}]
                
                original_msgs = db.query_messages(query, parameters)
                if original_msgs:
                    orig = original_msgs[0]
                    print(f"\n📌 Original message that got response:")
                    print(f"   ID: {orig.get('id', 'N/A')}")
                    print(f"   Subject: {orig.get('subject', 'N/A')}")
                    print(f"   Type: {orig.get('type', 'N/A')}")
                    print(f"   Priority: {orig.get('priority', 'N/A')}")
                    print(f"   From: {orig.get('from', 'N/A')}")
                    
                    # Analyze what made it successful
                    subject = orig.get('subject', '')
                    if 'urgent' in subject.lower():
                        print("   ⚡ Had URGENT tag")
                    if 'action required' in subject.lower():
                        print("   ⚡ Had ACTION REQUIRED")
                    if orig.get('priority') == 'high':
                        print("   ⚡ Had HIGH priority")
        
        return results
            
    except Exception as e:
        print(f"❌ Error finding manager responses: {e}")
        return []

def check_delivery_issues():
    """Check for any delivery or technical issues"""
    print("\n\n🔍 CHECKING FOR DELIVERY/TECHNICAL ISSUES")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Check for any error messages around the same time
    query = """
    SELECT * FROM messages 
    WHERE (
        messages.type = 'error' OR 
        messages.type = 'system' OR
        CONTAINS(LOWER(messages.content), 'delivery failed') OR
        CONTAINS(LOWER(messages.content), 'error')
    )
    AND messages.timestamp >= '2025-06-17T08:00:00Z'
    AND messages.timestamp <= '2025-06-17T09:00:00Z'
    ORDER BY messages.timestamp
    """
    
    try:
        results = db.query_messages(query)
        
        if results:
            print(f"\n⚠️ Found {len(results)} potential delivery issues:")
            for msg in results:
                print(f"\n   Timestamp: {msg.get('timestamp', 'N/A')}")
                print(f"   Type: {msg.get('type', 'N/A')}")
                print(f"   Subject: {msg.get('subject', 'N/A')}")
                if 'error' in str(msg.get('content', '')).lower():
                    print(f"   ❌ Contains error message")
        else:
            print(f"\n✅ No delivery issues found around that time")
            
    except Exception as e:
        print(f"❌ Error checking delivery issues: {e}")

def main():
    """Main investigation function"""
    print("🕵️ INVESTIGATING IGNORED AGENT CONTEXT MEMORY PROPOSAL")
    print("=" * 70)
    print("Target message ID: msg_20250617_082842_context_proposal")
    
    # 1. Find the actual message
    proposal_msg = find_context_proposal()
    
    # 2. Find similar proposals
    similar_msgs = find_similar_proposals()
    
    # 3. Find successful manager communications
    manager_responses = find_manager_responses()
    
    # 4. Check for delivery issues
    check_delivery_issues()
    
    # Summary
    print("\n\n📊 INVESTIGATION SUMMARY")
    print("=" * 70)
    
    if proposal_msg:
        print("✅ Message exists in Cosmos DB")
        print(f"   Subject: {proposal_msg.get('subject', 'N/A')}")
        print(f"   To: {proposal_msg.get('to', 'N/A')}")
        print(f"   Priority: {proposal_msg.get('priority', 'N/A')}")
        
        # Potential issues
        print("\n🚨 POTENTIAL ISSUES:")
        
        subject = proposal_msg.get('subject', '').lower()
        content = proposal_msg.get('content', '').lower()
        priority = proposal_msg.get('priority', '').lower()
        
        issues = []
        
        if priority != 'high':
            issues.append("- Not marked as high priority")
        if 'urgent' not in subject and 'action required' not in subject:
            issues.append("- No urgency indicators in subject")
        if len(content) > 5000:
            issues.append("- Very long content (managers might skip)")
        if not proposal_msg.get('to'):
            issues.append("- No recipients specified!")
        
        if issues:
            for issue in issues:
                print(issue)
        else:
            print("   No obvious formatting issues found")
            
        print("\n💡 RECOMMENDATIONS:")
        print("1. Resend with HIGH priority and 'ACTION REQUIRED' in subject")
        print("2. Keep content concise (under 500 words)")
        print("3. Add clear call-to-action at the beginning")
        print("4. Follow up with direct message to specific manager")
        print("5. Consider breaking into smaller, actionable requests")
    else:
        print("❌ Message NOT FOUND in Cosmos DB!")
        print("   The message may never have been created or was deleted")

if __name__ == "__main__":
    main()