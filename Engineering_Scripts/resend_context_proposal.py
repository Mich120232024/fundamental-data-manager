#!/usr/bin/env python3
"""
Resend the Agent Context Memory proposal with correct formatting
"""

import json
from datetime import datetime
from cosmos_db_manager import get_db_manager

def get_original_proposal():
    """Retrieve the original proposal content from the body field"""
    print("\n📥 RETRIEVING ORIGINAL PROPOSAL")
    print("=" * 60)
    
    db = get_db_manager()
    
    query = "SELECT * FROM messages WHERE messages.id = @message_id"
    parameters = [{"name": "@message_id", "value": "msg_20250617_082842_context_proposal"}]
    
    try:
        results = db.query_messages(query, parameters)
        if results:
            return results[0]
        else:
            print("❌ Original proposal not found!")
            return None
    except Exception as e:
        print(f"❌ Error retrieving proposal: {e}")
        return None

def create_corrected_proposal(original):
    """Create a new proposal with correct formatting"""
    print("\n📝 CREATING CORRECTED PROPOSAL")
    print("=" * 60)
    
    # Extract the body content (which has the actual proposal)
    body_content = original.get('body', '')
    
    if not body_content:
        print("❌ No body content found in original!")
        return None
    
    # Create new message with proper structure
    new_message = {
        "id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_context_proposal_v2",
        "timestamp": datetime.now().isoformat(),
        "type": "PROPOSAL",
        "from": "SYSTEM_ARCHITECTURE",
        "to": [
            "HEAD_OF_ENGINEERING",
            "HEAD_OF_RESEARCH", 
            "HEAD_OF_DIGITAL_STAFF",
            "COMPLIANCE_MANAGER"
        ],
        "cc": ["SAM"],
        "subject": "ACTION REQUIRED: Agent Context Memory System Proposal - Response Needed by EOD",
        "content": body_content,  # PUT THE CONTENT IN THE RIGHT FIELD!
        "priority": "high",  # HIGH PRIORITY
        "requires_response": True,
        "response_deadline": datetime.now().replace(hour=17, minute=0, second=0).isoformat(),
        "status": "sent",
        "metadata": {
            "original_message_id": "msg_20250617_082842_context_proposal",
            "resent_reason": "Original had content in 'body' field instead of 'content' field",
            "resent_date": datetime.now().isoformat()
        }
    }
    
    # Add urgency indicators to content
    urgent_prefix = """**🚨 ACTION REQUIRED - RESPONSE NEEDED BY EOD 🚨**

**This is a resend of the proposal from 2025-06-17 which was not delivered correctly due to a technical issue.**

---

"""
    
    new_message["content"] = urgent_prefix + new_message["content"]
    
    return new_message

def send_individual_messages(proposal_content):
    """Send individual messages to each manager for better visibility"""
    print("\n📨 CREATING INDIVIDUAL MANAGER MESSAGES")
    print("=" * 60)
    
    managers = [
        {
            "to": "HEAD_OF_ENGINEERING",
            "name": "Head of Engineering",
            "focus": "technical implementation and resource requirements"
        },
        {
            "to": "HEAD_OF_RESEARCH",
            "name": "Head of Research",
            "focus": "research impact and data management"
        },
        {
            "to": "HEAD_OF_DIGITAL_STAFF",
            "name": "Head of Digital Staff",
            "focus": "digital agent coordination and monitoring"
        },
        {
            "to": "COMPLIANCE_MANAGER",
            "name": "Compliance Manager",
            "focus": "governance and compliance automation"
        }
    ]
    
    individual_messages = []
    
    for manager in managers:
        # Personalize the message
        personalized_content = f"""**Direct Message for {manager['name']}**

**🚨 YOUR IMMEDIATE INPUT NEEDED on Agent Context Memory Proposal 🚨**

I need your specific feedback on the {manager['focus']} aspects of this proposal.

---

{proposal_content}

---

**SPECIFIC QUESTIONS FOR YOU:**

1. Does this meet your {manager['focus']} requirements?
2. What modifications would you need for your team?
3. Can you approve moving forward with implementation?

**Please respond by EOD today.**

Thank you,
System Architecture Team"""
        
        message = {
            "id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_context_proposal_{manager['to'].lower()}",
            "timestamp": datetime.now().isoformat(),
            "type": "PROPOSAL",
            "from": "SYSTEM_ARCHITECTURE",
            "to": [manager['to']],  # Single recipient
            "subject": f"URGENT - {manager['name']}: Action Required on Context Memory Proposal",
            "content": personalized_content,
            "priority": "high",
            "requires_response": True,
            "response_deadline": datetime.now().replace(hour=17, minute=0, second=0).isoformat(),
            "status": "sent",
            "metadata": {
                "personalized_for": manager['to'],
                "original_proposal": "msg_20250617_082842_context_proposal"
            }
        }
        
        individual_messages.append(message)
    
    return individual_messages

def send_messages(messages):
    """Send the corrected messages to Cosmos DB"""
    print("\n📤 SENDING CORRECTED MESSAGES")
    print("=" * 60)
    
    db = get_db_manager()
    sent_count = 0
    
    for message in messages:
        try:
            # Create the message
            result = db.create_message(message)
            if result:
                print(f"✅ Sent to: {', '.join(message['to'])}")
                print(f"   ID: {message['id']}")
                print(f"   Subject: {message['subject']}")
                sent_count += 1
            else:
                print(f"❌ Failed to send to: {', '.join(message['to'])}")
        except Exception as e:
            print(f"❌ Error sending message: {e}")
    
    return sent_count

def main():
    """Main execution"""
    print("🚀 RESENDING AGENT CONTEXT MEMORY PROPOSAL")
    print("=" * 70)
    
    # Get original proposal
    original = get_original_proposal()
    if not original:
        return
    
    print(f"\n✅ Found original proposal")
    print(f"   Original subject: {original.get('subject')}")
    print(f"   Original recipients: {', '.join(original.get('to', []))}")
    
    # Create corrected version
    corrected = create_corrected_proposal(original)
    if not corrected:
        return
    
    print(f"\n✅ Created corrected proposal")
    print(f"   New ID: {corrected['id']}")
    print(f"   Priority: {corrected['priority']} (was: {original.get('priority')})")
    print(f"   Content field: {'✅ POPULATED' if corrected.get('content') else '❌ EMPTY'}")
    
    # Create individual messages
    individual_msgs = send_individual_messages(original.get('body', ''))
    
    # Prepare all messages to send
    all_messages = [corrected] + individual_msgs
    
    print(f"\n📋 MESSAGES TO SEND:")
    print(f"   1 group message to all managers")
    print(f"   {len(individual_msgs)} individual personalized messages")
    print(f"   Total: {len(all_messages)} messages")
    
    # Send messages
    input("\n⏸️  Press Enter to send messages...")
    
    sent = send_messages(all_messages)
    
    # Summary
    print(f"\n\n📊 SENDING COMPLETE")
    print("=" * 60)
    print(f"✅ Successfully sent: {sent}/{len(all_messages)} messages")
    
    if sent > 0:
        print("\n✅ NEXT STEPS:")
        print("   1. Monitor for manager responses")
        print("   2. Follow up if no response by 3 PM")
        print("   3. Consider scheduling a meeting if still no response")
        print("   4. Document any feedback received")
    
    print("\n💡 LESSONS LEARNED:")
    print("   - Always use 'content' field, not 'body'")
    print("   - Mark important proposals as HIGH priority")
    print("   - Include 'ACTION REQUIRED' in subject")
    print("   - Consider sending individual messages for critical items")
    print("   - Validate message structure before sending")

if __name__ == "__main__":
    main()