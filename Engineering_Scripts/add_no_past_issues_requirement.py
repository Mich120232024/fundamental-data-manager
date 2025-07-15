#!/usr/bin/env python3
"""
Add requirement to prevent discussing obsolete past issues
"""

from cosmos_db_manager import CosmosDBManager
from datetime import datetime

def add_no_past_issues_requirement():
    """Add REQ-014 to focus on current state only"""
    
    db = CosmosDBManager()
    
    # Switch to enforcement container
    db.container = db.database.get_container_client('enforcement')
    
    requirement = {
        'id': 'REQ-014_no_past_issues_discussion',
        'type': 'EFFICIENCY_REQUIREMENT',
        'agentScope': 'All-Agents',
        'requirementName': 'No Past Issues Discussion - Current State Only',
        'description': 'Stop discussing solved problems, obsolete architectures, or past failures. Focus on current system state and forward action only.',
        'details': {
            'core_principle': 'Current Reality > Historical Problems',
            'banned_topics': [
                'Multi-box architecture issues (no longer relevant)',
                'Past fragmentation problems',
                'Historical failures already fixed',
                'Old system architectures',
                'Previous deployment issues',
                'Legacy communication problems',
                'Obsolete governance structures'
            ],
            'allowed_focus': [
                'Current system capabilities',
                'Active problems needing solution',
                'Forward improvements only',
                'Present state verification'
            ],
            'why_critical': 'Discussing past issues wastes time and confuses current reality with obsolete problems'
        },
        'metrics': {
            'compliance_check': 'Discussion relevance to current system',
            'violation_trigger': 'References to fixed/obsolete issues',
            'measurement': 'Time wasted on irrelevant history'
        },
        'enforcementLevel': 'MANDATORY',
        'penalties': {
            'first_violation': 'Redirect to current state immediately',
            'second_violation': 'Response must be rewritten',
            'pattern_violation': 'Restricted to current-state queries only'
        },
        'effectiveDate': '2025-06-18T00:00:00Z',
        'createdBy': 'SAM',
        'createdDate': datetime.now().isoformat() + 'Z',
        'constitutionalReference': 'Operational Efficiency',
        'evidenceRequired': True,
        'examples': {
            'wrong': "The multi-box architecture fix solves our fragmentation issue from the old system",
            'correct': "Current system uses unified Cosmos DB architecture"
        }
    }
    
    try:
        result = db.container.create_item(requirement)
        print(f"✅ Successfully added no past issues requirement: {result['id']}")
        
        # Send notification
        db.container = db.database.get_container_client('system_inbox')
        
        notification = {
            'type': 'ENFORCEMENT_UPDATE',
            'from': 'SAM',
            'to': ['COMPLIANCE_MANAGER', 'All-Agents'],
            'subject': 'STOP HISTORY LESSONS - CURRENT STATE ONLY: REQ-014',
            'content': """New enforcement requirement REQ-014: No Past Issues Discussion

STOP DISCUSSING:
- Multi-box architecture (obsolete)
- Past fragmentation issues
- Historical failures
- Old system problems
- Previous deployments
- Legacy anything

FOCUS ONLY ON:
- Current system state
- Active problems
- Forward improvements
- What works NOW

WHY:
- Past issues aren't relevant to new system
- Confuses current reality with old problems
- Wastes time on solved issues
- Creates false context

Example violation: "Multi-box fix solves fragmentation"
Correct approach: "Current system uses Cosmos DB"

Look forward, not backward.""",
            'priority': 'high',
            'requiresResponse': False,
            'timestamp': datetime.now().isoformat() + 'Z'
        }
        
        msg_result = db.store_message(notification)
        print(f"✅ Notification sent: {msg_result['id']}")
        
    except Exception as e:
        print(f"❌ Error adding requirement: {str(e)}")

if __name__ == "__main__":
    add_no_past_issues_requirement()