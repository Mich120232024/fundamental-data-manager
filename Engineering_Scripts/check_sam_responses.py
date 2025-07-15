#!/usr/bin/env python3

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Import cosmos manager
sys.path.insert(0, str(Path(__file__).parent))
from cosmos_db_manager import get_db_manager

db = get_db_manager()

print("🔍 Checking for SAM's messages and my responses...\n")

# Get recent messages FROM SAM
sam_query = """
SELECT * FROM messages 
WHERE messages['from'] = 'SAM'
AND messages.timestamp > '2025-06-15'
ORDER BY messages.timestamp DESC
"""

sam_messages = list(db.query_messages(sam_query, []))
print(f"📧 Recent messages FROM SAM: {len(sam_messages)}")

# Show SAM's messages that might need responses
requires_response = []
for msg in sam_messages[:5]:
    print(f"\n- Time: {msg.get('timestamp', 'Unknown')}")
    print(f"  To: {msg.get('to', 'Unknown')}")
    print(f"  Subject: {msg.get('subject', 'No subject')[:60]}...")
    print(f"  ID: {msg.get('id', 'Unknown')}")
    
    if msg.get('requiresResponse'):
        print("  🔴 REQUIRES RESPONSE")
        requires_response.append(msg)
        
    # Check if it's the constitutional role review
    if 'constitutional' in str(msg.get('subject', '')).lower():
        print("  ⚠️  CONSTITUTIONAL ROLE REVIEW MESSAGE")

# Get my messages TO SAM
my_response_query = """
SELECT * FROM messages 
WHERE messages['from'] = 'HEAD_OF_ENGINEERING'
AND messages['to'] = 'SAM'
AND messages.timestamp > '2025-06-15'
ORDER BY messages.timestamp DESC
"""

my_responses = list(db.query_messages(my_response_query, []))
print(f"\n\n📧 My messages TO SAM: {len(my_responses)}")

for resp in my_responses[:5]:
    print(f"\n- Time: {resp.get('timestamp', 'Unknown')}")
    print(f"  Subject: {resp.get('subject', 'No subject')}")
    print(f"  ID: {resp.get('id', 'Unknown')}")
    
# Check if I responded to specific messages
print(f"\n\n🔍 Checking if I responded to SAM's messages requiring response...")

if requires_response:
    for sam_msg in requires_response:
        sam_time = sam_msg.get('timestamp', '')
        sam_subject = sam_msg.get('subject', 'No subject')
        
        # Look for my responses after SAM's message
        responded = False
        for my_msg in my_responses:
            if my_msg.get('timestamp', '') > sam_time:
                # Check if subjects are related
                if any(word in str(my_msg.get('subject', '')).lower() 
                      for word in ['constitutional', 'role', 'review'] 
                      if word in sam_subject.lower()):
                    responded = True
                    print(f"\n✅ RESPONDED to '{sam_subject[:40]}...'")
                    print(f"   My response: {my_msg.get('subject', 'No subject')}")
                    break
        
        if not responded:
            print(f"\n❌ NO RESPONSE found to: '{sam_subject[:40]}...'")
            print(f"   Sent: {sam_time}")
            print(f"   This message still needs a response!")

# Also check messages where I'm CC'd or in a group
print(f"\n\n🔍 Checking for group messages from SAM...")
group_query = """
SELECT * FROM messages 
WHERE messages['from'] = 'SAM'
AND (ARRAY_CONTAINS(messages['to'], 'HEAD_OF_ENGINEERING') OR 
     messages['to'] = 'HEAD_OF_ENGINEERING' OR
     messages['to'] = 'All-Agents' OR
     messages['to'] = 'Management_Team')
AND messages.timestamp > '2025-06-15'
ORDER BY messages.timestamp DESC
"""

group_messages = list(db.query_messages(group_query, []))
print(f"Found {len(group_messages)} messages where I might be included")

for msg in group_messages[:3]:
    if msg['id'] not in [m['id'] for m in sam_messages]:  # Don't duplicate
        print(f"\n- Time: {msg.get('timestamp', 'Unknown')}")
        print(f"  To: {msg.get('to', 'Unknown')}")
        print(f"  Subject: {msg.get('subject', 'No subject')[:60]}...")
        if msg.get('requiresResponse'):
            print("  🔴 REQUIRES RESPONSE")