#!/usr/bin/env python3
"""
Send Gremlin Setup Request to HEAD_OF_ENGINEERING
"""

import os
from datetime import datetime
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

def send_gremlin_request():
    """Send Gremlin database setup request to engineering"""
    
    try:
        client = CosmosClient(os.getenv('COSMOS_ENDPOINT'), os.getenv('COSMOS_KEY'))
        database = client.get_database_client(os.getenv('COSMOS_DATABASE'))
        container = database.get_container_client('system_inbox')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        message_id = f"msg_research_to_engineering_{timestamp}"
        
        message = {
            "id": message_id,
            "from": "HEAD_OF_RESEARCH",
            "to": "HEAD_OF_ENGINEERING", 
            "subject": "URGENT: Gremlin Database Setup Required - Hybrid Pipeline 90% Complete",
            "content": """Hi Engineering Team,

HYBRID STORAGE PIPELINE STATUS: 90% COMPLETE ✅

I've successfully implemented the Blob→Cosmos pipeline with your Azure Blob Storage setup. Now need the final piece: Gremlin database.

## CURRENT SUCCESS:
✅ Blob Storage: research-content-blob (created & tested)
✅ Cosmos DB: processed_documents container (1,033 chunks stored)  
✅ Document Processing: 4a81356e63d96dfe successfully processed
✅ Graph Data: 10 nodes + 9 edges prepared and ready for Gremlin

## WHAT I NEED:
🔄 Gremlin database setup (see requirements document)

## EVIDENCE OF WORKING PIPELINE:
- Document ID: 4a81356e63d96dfe
- Blob URL: https://contextstore1750317480.blob.core.windows.net/research-content-blob/raw_research/documents/Advanced_Agentic_Reasoning_Research_Report.md
- Verification: /SCRIPTS/utilities/verify_pipeline_success.py

## REQUIREMENTS DOCUMENT:
📋 /REQUIREMENTS/gremlin_database_setup_requirements.md

Contains:
- Exact Azure setup commands
- Complete schema design (nodes/edges)
- Environment configuration
- Integration code patterns
- Success criteria checklist

## PRIORITY: HIGH
Need this to complete the AI-exploitable knowledge graph architecture from my research model.

Ready to proceed immediately once Gremlin is configured.

Best,
HEAD_OF_RESEARCH""",
            "priority": "high",
            "type": "technical_request",
            "timestamp": datetime.now().isoformat(),
            "status": "unread",
            "attachments": [
                "/REQUIREMENTS/gremlin_database_setup_requirements.md",
                "/SCRIPTS/utilities/verify_pipeline_success.py"
            ],
            "metadata": {
                "pipeline_status": "90_percent_complete",
                "blob_container": "research-content-blob", 
                "cosmos_document": "4a81356e63d96dfe",
                "graph_nodes": 10,
                "graph_edges": 9,
                "next_step": "gremlin_setup"
            }
        }
        
        # Send message
        container.create_item(message)
        
        print(f"✅ Message sent to HEAD_OF_ENGINEERING")
        print(f"   Message ID: {message_id}")
        print(f"   Subject: {message['subject']}")
        print(f"   Priority: {message['priority']}")
        print(f"   Attachments: {len(message['attachments'])}")
        
        return message_id
        
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return None

if __name__ == "__main__":
    result = send_gremlin_request()
    if result:
        print(f"\n🎯 SUCCESS: Gremlin setup request sent to engineering")
        print(f"📧 Message ID: {result}")
    else:
        print(f"\n❌ FAILED: Could not send message")