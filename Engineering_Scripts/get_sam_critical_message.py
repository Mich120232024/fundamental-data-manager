#!/usr/bin/env python3
"""
Retrieve the full content of SAM's CRITICAL priority message ID: 2025-06-20T15:45:00Z_0579
"""

import json
from cosmos_db_manager import CosmosDBManager

def get_specific_message():
    """Retrieve specific message by ID"""
    try:
        db = CosmosDBManager()
        
        message_id = "2025-06-20T15:45:00Z_0579"
        
        print(f"Retrieving full content of message ID: {message_id}")
        print("=" * 80)
        
        # Query for the specific message
        query = f"""
        SELECT * FROM messages 
        WHERE messages.id = '{message_id}'
        """
        
        results = db.query_messages(query)
        
        if results:
            msg = results[0]
            print(f"\nFROM: {msg.get('from')}")
            print(f"TO: {msg.get('to')}")
            print(f"TYPE: {msg.get('type')}")
            print(f"SUBJECT: {msg.get('subject')}")
            print(f"TIMESTAMP: {msg.get('timestamp')}")
            print(f"PRIORITY: {msg.get('priority', 'medium')}")
            print(f"REQUIRES RESPONSE: {msg.get('requiresResponse', False)}")
            print("\n" + "=" * 80)
            print("FULL MESSAGE CONTENT:")
            print("=" * 80)
            print(msg.get('content', 'No content'))
            print("\n" + "=" * 80)
            
            # Save to file for reference
            with open('sam_critical_message_2025-06-20.txt', 'w') as f:
                f.write(f"MESSAGE ID: {message_id}\n")
                f.write(f"FROM: {msg.get('from')}\n")
                f.write(f"TO: {msg.get('to')}\n")
                f.write(f"TYPE: {msg.get('type')}\n")
                f.write(f"SUBJECT: {msg.get('subject')}\n")
                f.write(f"TIMESTAMP: {msg.get('timestamp')}\n")
                f.write(f"PRIORITY: {msg.get('priority', 'medium')}\n")
                f.write(f"REQUIRES RESPONSE: {msg.get('requiresResponse', False)}\n")
                f.write("\n" + "=" * 80 + "\n")
                f.write("FULL MESSAGE CONTENT:\n")
                f.write("=" * 80 + "\n")
                f.write(msg.get('content', 'No content'))
            
            print("\nMessage saved to: sam_critical_message_2025-06-20.txt")
            
        else:
            print("Message not found!")
        
    except Exception as e:
        print(f"Error retrieving message: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_specific_message()