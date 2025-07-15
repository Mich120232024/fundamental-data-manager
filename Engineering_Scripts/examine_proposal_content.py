#!/usr/bin/env python3
"""
Deep dive into the context proposal message to understand the content issue
"""

import json
from cosmos_db_manager import get_db_manager

def examine_proposal_in_detail():
    """Examine the proposal message with all fields"""
    print("\n🔍 DEEP EXAMINATION OF CONTEXT PROPOSAL MESSAGE")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Get the raw message
    query = "SELECT * FROM messages WHERE messages.id = @message_id"
    parameters = [{"name": "@message_id", "value": "msg_20250617_082842_context_proposal"}]
    
    try:
        results = db.query_messages(query, parameters)
        
        if results:
            msg = results[0]
            
            print("\n📄 RAW MESSAGE STRUCTURE:")
            print(json.dumps(msg, indent=2))
            
            # Check every field
            print("\n\n🔍 FIELD-BY-FIELD ANALYSIS:")
            print("-" * 50)
            
            for key, value in msg.items():
                print(f"\n{key}:")
                if value is None:
                    print("   ❌ NULL/None value!")
                elif isinstance(value, str) and not value.strip():
                    print("   ❌ Empty string!")
                elif isinstance(value, list) and not value:
                    print("   ❌ Empty list!")
                elif isinstance(value, dict) and not value:
                    print("   ❌ Empty dictionary!")
                else:
                    if isinstance(value, str) and len(value) > 100:
                        print(f"   Value: {value[:100]}... (truncated)")
                    else:
                        print(f"   Value: {value}")
                    print(f"   Type: {type(value).__name__}")
            
            # Specific content check
            print("\n\n📝 CONTENT ANALYSIS:")
            print("-" * 50)
            
            content = msg.get('content')
            if content is None:
                print("❌ CRITICAL: Content field is NULL/None!")
                print("   This explains why managers ignored it - there's no actual proposal content!")
            elif isinstance(content, str) and not content.strip():
                print("❌ CRITICAL: Content field is empty string!")
            elif not content:
                print("❌ CRITICAL: Content field is falsy/empty!")
            else:
                print(f"✅ Content exists: {len(content)} characters")
                print("\nFirst 500 characters of content:")
                print(content[:500])
            
            # Check related fields that might contain the actual proposal
            print("\n\n🔍 CHECKING OTHER FIELDS FOR PROPOSAL CONTENT:")
            for field in ['body', 'message', 'text', 'description', 'proposal', 'details']:
                if field in msg and msg[field]:
                    print(f"\n✅ Found content in '{field}' field:")
                    print(f"   Length: {len(str(msg[field]))} characters")
                    print(f"   Preview: {str(msg[field])[:200]}...")
            
            # Check metadata
            metadata = msg.get('metadata', {})
            if metadata:
                print("\n\n📊 METADATA CONTENTS:")
                print(json.dumps(metadata, indent=2))
                
                # Check if proposal is in metadata
                for key, value in metadata.items():
                    if 'proposal' in key.lower() or 'content' in key.lower():
                        print(f"\n⚠️ Found '{key}' in metadata - content might be misplaced!")
            
            return msg
        else:
            print("❌ Message not found!")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def find_other_proposals_structure():
    """Compare with other successful proposals"""
    print("\n\n🔍 COMPARING WITH OTHER PROPOSALS")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Find other proposals that got responses
    query = """
    SELECT * FROM messages 
    WHERE messages.type = 'PROPOSAL'
    AND messages.timestamp >= '2025-06-15T00:00:00Z'
    AND messages.id != 'msg_20250617_082842_context_proposal'
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        
        print(f"\n📊 Found {len(results)} other proposals")
        
        # Analyze first few
        for i, msg in enumerate(results[:3]):
            print(f"\n\n📄 Proposal {i+1}: {msg.get('id', 'N/A')}")
            print(f"   Subject: {msg.get('subject', 'N/A')}")
            print(f"   From: {msg.get('from', 'N/A')}")
            
            content = msg.get('content')
            if content:
                print(f"   ✅ Has content: {len(content)} characters")
            else:
                print(f"   ❌ No content!")
            
            # Check if this proposal got a response
            proposal_id = msg.get('id')
            response_query = """
            SELECT COUNT(1) as response_count FROM messages 
            WHERE messages.type = 'response' 
            AND CONTAINS(messages.content, @proposal_id)
            """
            response_params = [{"name": "@proposal_id", "value": proposal_id}]
            
            response_results = db.query_messages(response_query, response_params)
            if response_results and response_results[0].get('response_count', 0) > 0:
                print(f"   ✅ Got {response_results[0]['response_count']} responses!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main examination"""
    print("🕵️ EXAMINING CONTEXT PROPOSAL MESSAGE CONTENT ISSUE")
    print("=" * 70)
    
    # Detailed examination
    proposal = examine_proposal_in_detail()
    
    # Compare with others
    find_other_proposals_structure()
    
    # Summary
    print("\n\n📊 FINAL DIAGNOSIS")
    print("=" * 70)
    
    if proposal:
        content = proposal.get('content')
        if not content:
            print("\n❌ ROOT CAUSE IDENTIFIED:")
            print("   The proposal message has NO CONTENT!")
            print("   - Message was created with proper metadata")
            print("   - Recipients were correctly specified")
            print("   - Subject line was set")
            print("   - BUT the actual proposal content is missing/empty")
            print("\n   This is why managers ignored it - there was literally nothing to read!")
            
            print("\n\n💡 SOLUTION:")
            print("   1. Create a new proposal message WITH actual content")
            print("   2. Include the proposal details in the 'content' field")
            print("   3. Mark as HIGH priority")
            print("   4. Add 'ACTION REQUIRED' to subject")
            print("   5. Send to specific managers individually if needed")

if __name__ == "__main__":
    main()