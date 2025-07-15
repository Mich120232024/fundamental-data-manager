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

# Check for HEAD_OF_DIGITAL_STAFF's urgent message
original_msg_id = "msg_2025-06-17T16:01:52.886406_0981"

db = get_db_manager()

# Get the original message
query = f"SELECT * FROM messages WHERE messages.id = '{original_msg_id}'"
original = list(db.query_messages(query, []))

if original:
    print(f"✅ Found HEAD_OF_DIGITAL_STAFF's message:")
    print(f"   Subject: {original[0].get('subject', 'No subject')}")
    print(f"   Requires Response: {original[0].get('requiresResponse', False)}")
    print(f"   Time: {original[0].get('timestamp', 'Unknown')}")

# Check for my responses to HEAD_OF_DIGITAL_STAFF after that time
response_query = """
SELECT * FROM messages 
WHERE messages['from'] = 'HEAD_OF_ENGINEERING' 
AND messages['to'] = 'HEAD_OF_DIGITAL_STAFF'
AND messages.timestamp > '2025-06-17T16:01:52Z'
ORDER BY messages.timestamp ASC
"""

responses = list(db.query_messages(response_query, []))

print(f"\n📧 My responses to HEAD_OF_DIGITAL_STAFF after their message: {len(responses)}")

if responses:
    for i, resp in enumerate(responses):
        print(f"\n{i+1}. Time: {resp.get('timestamp', 'Unknown')}")
        print(f"   Subject: {resp.get('subject', 'No subject')}")
        print(f"   ID: {resp.get('id', 'Unknown')}")
        
        # Check if it references the original message
        content = str(resp.get('content', ''))
        if original_msg_id in content:
            print("   ✅ DIRECTLY REFERENCES THE EMAIL QUERY MESSAGE")
            
print("\n📋 Summary of my actions:")
print("1. Implemented the solution in cosmos_db_manager.py")
print("2. Notified COMPLIANCE_MANAGER and SAM about the update") 
print("3. Sent approval notification to HEAD_OF_DIGITAL_STAFF")
print("\nDid I directly reply to the URGENT message? Let me check...")