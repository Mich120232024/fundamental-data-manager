#!/usr/bin/env python3
"""
Mark Engineering Message as Read
"""

import os
from pathlib import Path
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment
env_paths = [
    Path(__file__).parent.parent / '.env',
    Path(__file__).parent.parent.parent / '.env',
    Path.cwd() / '.env'
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break

def mark_message_read():
    """Mark the engineering message as read"""
    
    try:
        client = CosmosClient(os.getenv('COSMOS_ENDPOINT'), os.getenv('COSMOS_KEY'))
        database = client.get_database_client(os.getenv('COSMOS_DATABASE'))
        container = database.get_container_client('system_inbox')
        
        message_id = "msg_engineering_to_research_20250620_053541"
        
        # Read the message
        message = container.read_item(
            item=message_id,
            partition_key=message_id
        )
        
        # Update status to read
        message['status'] = 'read'
        
        # Replace the item
        container.replace_item(
            item=message_id,
            body=message
        )
        
        print(f"✅ Marked message as read: {message_id}")
        print(f"   Subject: {message['subject']}")
        print(f"   Status: {message['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error marking message as read: {e}")
        return False

if __name__ == "__main__":
    mark_message_read()