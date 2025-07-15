#!/usr/bin/env python3
"""
Search for direct responses to the Agent Context Memory proposal
"""

import json
from cosmos_db_manager import get_db_manager

def search_direct_responses():
    """Search for messages that directly reference the context proposal"""
    print("🔍 SEARCHING FOR DIRECT RESPONSES TO CONTEXT PROPOSAL")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Get all messages after the proposal date
    cutoff_date = "2025-06-17T08:28:42Z"
    
    query = """
    SELECT * FROM messages 
    WHERE messages.timestamp >= @cutoff_date
    ORDER BY messages.timestamp ASC
    """
    
    parameters = [{"name": "@cutoff_date", "value": cutoff_date}]
    
    try:
        messages = db.query_messages(query, parameters)
        print(f"📊 Found {len(messages)} messages after proposal time")
        
        # Target managers from the original proposal
        target_managers = ["HEAD_OF_ENGINEERING", "HEAD_OF_RESEARCH", "HEAD_OF_DIGITAL_STAFF", "COMPLIANCE_MANAGER"]
        
        direct_responses = []
        
        for msg in messages:
            from_agent = msg.get('from', '')
            subject = str(msg.get('subject', ''))
            content = str(msg.get('content', ''))
            body = str(msg.get('body', ''))
            
            # Only check messages from target managers
            if from_agent not in target_managers:
                continue
            
            # Combine all text
            all_text = f"{subject} {content} {body}".lower()
            
            # Check for direct references to the proposal
            direct_references = [
                'msg_20250617_082842_context_proposal',
                'agent context memory',
                'consolidated agent context',
                'context memory system',
                'agent context memory system'
            ]
            
            # Check for indirect but likely references
            indirect_references = []
            if 'context' in all_text and 'memory' in all_text:
                indirect_references.append('context+memory')
            if 'context' in all_text and 'agent' in all_text:
                indirect_references.append('context+agent')
            if 'context' in all_text and 'proposal' in all_text:
                indirect_references.append('context+proposal')
            if 'memory' in all_text and 'system' in all_text:
                indirect_references.append('memory+system')
            
            found_direct = [ref for ref in direct_references if ref in all_text]
            
            if found_direct or indirect_references:
                direct_responses.append({
                    'message': msg,
                    'direct_refs': found_direct,
                    'indirect_refs': indirect_references
                })
        
        print(f"\n📋 DIRECT RESPONSES FOUND: {len(direct_responses)}")
        
        if direct_responses:
            for i, response in enumerate(direct_responses, 1):
                msg = response['message']
                direct_refs = response['direct_refs']
                indirect_refs = response['indirect_refs']
                
                print(f"\n{i}. 📝 RESPONSE FROM {msg.get('from', 'UNKNOWN')}")
                print(f"   ID: {msg.get('id', 'N/A')}")
                print(f"   Timestamp: {msg.get('timestamp', 'N/A')}")
                print(f"   To: {msg.get('to', 'N/A')}")
                print(f"   Subject: {msg.get('subject', 'N/A')}")
                
                if direct_refs:
                    print(f"   🎯 DIRECT REFERENCES: {', '.join(direct_refs)}")
                if indirect_refs:
                    print(f"   🔍 INDIRECT REFERENCES: {', '.join(indirect_refs)}")
                
                # Show content if available
                content = msg.get('content', '') or msg.get('body', '')
                if content:
                    content_snippet = content[:300] + "..." if len(content) > 300 else content
                    print(f"   📄 Content: {content_snippet}")
                else:
                    print(f"   📄 No content available")
        
        else:
            print("❌ No direct responses found to the Agent Context Memory proposal")
        
        return direct_responses
        
    except Exception as e:
        print(f"❌ Error searching for direct responses: {e}")
        return []

def check_proposal_status():
    """Check the status of the original proposal"""
    print("\n🔍 CHECKING PROPOSAL STATUS")
    print("=" * 50)
    
    db = get_db_manager()
    
    # Get the original proposal
    original_id = "msg_20250617_082842_context_proposal"
    query = "SELECT * FROM messages WHERE messages.id = @message_id"
    parameters = [{"name": "@message_id", "value": original_id}]
    
    try:
        results = db.query_messages(query, parameters)
        
        if results:
            proposal = results[0]
            
            print(f"📋 Original Proposal Details:")
            print(f"   ID: {proposal.get('id')}")
            print(f"   Sent: {proposal.get('timestamp')}")
            print(f"   From: {proposal.get('from')}")
            print(f"   To: {proposal.get('to')}")
            print(f"   Subject: {proposal.get('subject')}")
            print(f"   Requires Response: {proposal.get('requires_response')}")
            print(f"   Response Deadline: {proposal.get('response_deadline')}")
            print(f"   Status: {proposal.get('status')}")
            
            # Check if deadline has passed
            if proposal.get('response_deadline'):
                deadline = proposal.get('response_deadline')
                print(f"\n⏰ Response Deadline: {deadline}")
                print(f"   Status: DEADLINE HAS PASSED (2025-06-18 17:00)")
            
            return proposal
        else:
            print("❌ Original proposal not found")
            return None
            
    except Exception as e:
        print(f"❌ Error checking proposal status: {e}")
        return None

def main():
    """Main function"""
    print("🔍 DIRECT RESPONSE ANALYSIS FOR AGENT CONTEXT MEMORY PROPOSAL")
    print("=" * 80)
    
    # Check proposal status
    proposal = check_proposal_status()
    
    # Search for direct responses
    responses = search_direct_responses()
    
    # Summary
    print("\n📊 FINAL SUMMARY")
    print("=" * 50)
    
    if proposal:
        print("✅ Original proposal exists and was properly sent")
        recipients = proposal.get('to', [])
        if isinstance(recipients, list):
            print(f"📧 Sent to {len(recipients)} managers: {', '.join(recipients)}")
        else:
            print(f"📧 Sent to: {recipients}")
        
        deadline = proposal.get('response_deadline')
        if deadline:
            print(f"⏰ Response deadline was: {deadline}")
            print("⚠️  DEADLINE HAS PASSED - responses were due by 2025-06-18 17:00")
    
    if responses:
        print(f"\n🎯 Found {len(responses)} potential responses")
        
        # Count by manager
        manager_responses = {}
        for response in responses:
            manager = response['message'].get('from', 'UNKNOWN')
            if manager not in manager_responses:
                manager_responses[manager] = 0
            manager_responses[manager] += 1
        
        print("📋 Responses by manager:")
        for manager, count in manager_responses.items():
            print(f"   {manager}: {count} message(s)")
    else:
        print("❌ NO DIRECT RESPONSES FOUND")
        print("💡 This suggests managers have not yet responded to the context proposal")
        print("🔄 You may want to follow up with the managers")
    
    print("\n🏁 ANALYSIS COMPLETE")

if __name__ == "__main__":
    main()