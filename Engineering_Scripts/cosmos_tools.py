#!/usr/bin/env python3
"""
Minimalistic Cosmos DB Tools
Engineering-focused utilities for resource management
"""

from cosmos_db_manager import get_db_manager
import json
from datetime import datetime

class CosmosTools:
    """Minimalistic tools for Cosmos DB operations"""
    
    def __init__(self):
        self.db = get_db_manager()
        
    def quick_write(self, container_name, document):
        """Write document to container - no complexity"""
        container = self.db.database.get_container_client(container_name)
        if 'id' not in document:
            document['id'] = f"{container_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if 'timestamp' not in document:
            document['timestamp'] = datetime.now().isoformat() + 'Z'
        return container.create_item(body=document)
    
    def quick_read(self, container_name, query=None, limit=10):
        """Read from container - simple and direct"""
        container = self.db.database.get_container_client(container_name)
        if query:
            items = container.query_items(query=query, enable_cross_partition_query=True)
        else:
            items = container.query_items(
                query=f"SELECT * FROM c ORDER BY c._ts DESC OFFSET 0 LIMIT {limit}",
                enable_cross_partition_query=True
            )
        return list(items)
    
    def send_message(self, to, subject, content, from_agent="ENGINEERING"):
        """Send message - no frills"""
        return self.quick_write('messages', {
            'from': from_agent,
            'to': to,
            'subject': subject,
            'content': content,
            'type': 'SYSTEM_MESSAGE',
            'partitionKey': datetime.now().strftime('%Y-%m')
        })
    
    def check_inbox(self, recipient="ENGINEERING", limit=5):
        """Check messages - direct query"""
        query = f"SELECT * FROM c WHERE c.to = '{recipient}' ORDER BY c._ts DESC"
        return self.quick_read('messages', query, limit)

# CLI usage
if __name__ == "__main__":
    import sys
    
    tools = CosmosTools()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  cosmos_tools.py send <to> <subject> <content>")
        print("  cosmos_tools.py inbox [recipient] [limit]")
        print("  cosmos_tools.py write <container> <json_data>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "send" and len(sys.argv) >= 5:
        result = tools.send_message(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"Sent: {result['id']}")
        
    elif cmd == "inbox":
        recipient = sys.argv[2] if len(sys.argv) > 2 else "ENGINEERING"
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        messages = tools.check_inbox(recipient, limit)
        for msg in messages:
            print(f"From: {msg.get('from')}, Subject: {msg.get('subject')}")
            
    elif cmd == "write" and len(sys.argv) >= 4:
        container = sys.argv[2]
        data = json.loads(sys.argv[3])
        result = tools.quick_write(container, data)
        print(f"Written: {result['id']}")