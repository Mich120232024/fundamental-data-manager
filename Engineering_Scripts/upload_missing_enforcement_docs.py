#!/usr/bin/env python3
"""
Upload missing enforcement documents from local governance to Cosmos DB
"""

import os
from cosmos_db_manager import CosmosDBManager
from datetime import datetime

def upload_missing_enforcement_docs():
    """Upload session log enforcement and other missing docs"""
    
    db = CosmosDBManager()
    db.container = db.database.get_container_client('documents')
    
    # Session log enforcement procedure
    session_log_path = "/Users/mikaeleage/Research & Analytics Services/Governance Workspace/Procedures/session_log_enforcement_procedure.md"
    
    if os.path.exists(session_log_path):
        with open(session_log_path, 'r') as f:
            content = f.read()
        
        doc = {
            'id': 'DOC-GOV-PRO-035_session_log_enforcement',
            'type': 'PROCEDURE',
            'pillar': 'Procedures',
            'title': 'Session Log Enforcement Procedure',
            'description': 'Mandatory session logging to prevent drift and enable auditing',
            'content': content,
            'status': 'active',
            'version': '1.0',
            'effectiveDate': '2025-06-18T00:00:00Z',
            'lastModified': datetime.now().isoformat() + 'Z',
            'createdBy': 'SAM',
            'tags': ['enforcement', 'session-logging', 'mandatory', 'audit-trail'],
            'enforcementLevel': 'MANDATORY',
            'constitutionalReference': 'Evidence Requirements'
        }
        
        try:
            result = db.container.create_item(doc)
            print(f"✅ Uploaded session log enforcement: {result['id']}")
        except Exception as e:
            print(f"❌ Failed to upload session log enforcement: {e}")
    
    # Check for other missing enforcement documents
    missing_docs = [
        ('compliance_manager_verification_loops.md', 'Compliance Manager Verification Loops'),
        ('handle_violations.md', 'Handle Violations Procedure'),
        ('emergency_agent_triage_protocol.md', 'Emergency Agent Triage Protocol')
    ]
    
    for filename, title in missing_docs:
        file_path = f"/Users/mikaeleage/Research & Analytics Services/Governance Workspace/Procedures/{filename}"
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Generate ID
            doc_id = f"DOC-GOV-PRO-{filename.replace('.md', '').replace('_', '-')}"
            
            doc = {
                'id': doc_id,
                'type': 'PROCEDURE',
                'pillar': 'Procedures',
                'title': title,
                'content': content,
                'status': 'active',
                'version': '1.0',
                'effectiveDate': '2025-06-18T00:00:00Z',
                'lastModified': datetime.now().isoformat() + 'Z',
                'createdBy': 'SAM',
                'tags': ['enforcement', 'procedure']
            }
            
            try:
                result = db.container.create_item(doc)
                print(f"✅ Uploaded {filename}: {result['id']}")
            except Exception as e:
                print(f"❌ Failed to upload {filename}: {e}")
        else:
            print(f"⚠️  File not found: {filename}")

if __name__ == "__main__":
    upload_missing_enforcement_docs()