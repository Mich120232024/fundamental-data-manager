#!/usr/bin/env python3
"""
Add email checking procedure to enforcement requirements
"""

from cosmos_db_manager import CosmosDBManager
from datetime import datetime

def add_email_checking_requirement():
    """Add REQ-009 for proper email checking methodology"""
    
    db = CosmosDBManager()
    
    # Switch to enforcement container
    db.container = db.database.get_container_client('enforcement')
    
    requirement = {
        'id': 'REQ-009_email_checking_methodology',
        'type': 'EFFICIENCY_REQUIREMENT',
        'agentScope': 'All-Agents',
        'requirementName': 'Email Checking Methodology',
        'description': 'All agents must follow the standard email checking procedure: Last 20, then next 20, then final 10 before any advanced queries',
        'details': {
            'step1': 'Get last 20 messages with db.get_recent_messages(limit=20)',
            'step2': 'If needed, get messages 21-40 with OFFSET 20 LIMIT 20',
            'step3': 'If still needed, get messages 41-50 with OFFSET 40 LIMIT 10',
            'step4': 'Only after checking 50 messages should advanced queries be used',
            'rationale': 'Prevents missing messages due to complex query assumptions'
        },
        'metrics': {
            'compliance_check': 'Email queries must start with get_recent_messages()',
            'violation_trigger': 'Starting with complex agent-specific queries',
            'measurement': 'Query patterns in session logs'
        },
        'enforcementLevel': 'MANDATORY',
        'penalties': {
            'first_violation': 'Reminder of proper procedure',
            'second_violation': 'Required to document why skipping basic check',
            'pattern_violation': 'Email query privileges restricted'
        },
        'effectiveDate': '2025-06-18T00:00:00Z',
        'createdBy': 'SAM',
        'createdDate': datetime.now().isoformat() + 'Z',
        'constitutionalReference': 'Operational Efficiency Standards',
        'evidenceRequired': True
    }
    
    try:
        result = db.container.create_item(requirement)
        print(f"✅ Successfully added email checking requirement: {result['id']}")
        
        # Also send notification
        db.container = db.database.get_container_client('system_inbox')
        
        notification = {
            'type': 'ENFORCEMENT_UPDATE',
            'from': 'SAM',
            'to': ['COMPLIANCE_MANAGER', 'All-Agents'],
            'subject': 'New Enforcement Requirement: Email Checking Methodology',
            'content': """All agents must now follow the standard email checking procedure:

1. Start with db.get_recent_messages(limit=20)
2. If needed, check messages 21-40 
3. If still needed, check messages 41-50
4. Only then use advanced queries

This prevents missing messages due to complex query assumptions. The procedure is documented at:
/Governance Workspace/Procedures/email_checking_procedure.md

This is now enforcement requirement REQ-009.""",
            'priority': 'high',
            'requiresResponse': False,
            'timestamp': datetime.now().isoformat() + 'Z'
        }
        
        msg_result = db.store_message(notification)
        print(f"✅ Notification sent: {msg_result['id']}")
        
    except Exception as e:
        print(f"❌ Error adding requirement: {str(e)}")

if __name__ == "__main__":
    add_email_checking_requirement()