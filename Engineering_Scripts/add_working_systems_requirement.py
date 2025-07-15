#!/usr/bin/env python3
"""
Add requirement for working systems over management theater
"""

from cosmos_db_manager import CosmosDBManager
from datetime import datetime

def add_working_systems_requirement():
    """Add REQ-016 demanding working systems not theater"""
    
    db = CosmosDBManager()
    db.container = db.database.get_container_client('enforcement')
    
    requirement = {
        'id': 'REQ-016_working_systems_over_theater',
        'type': 'EFFICIENCY_REQUIREMENT',
        'agentScope': 'All-Agents',
        'requirementName': 'Working Systems Over Management Theater',
        'description': 'Deliver working tools and real data, not static mockups and repeated statistics. Stop organizational dysfunction.',
        'details': {
            'core_principle': 'Working Systems > Management Theater',
            'required_outputs': [
                'Working systems that agents can use',
                'Real data from actual containers',
                'Actionable information for decisions',
                'Tools that solve actual problems'
            ],
            'banned_outputs': [
                'Static mockups that do nothing',
                'Repeated statistics without context',
                'Management theater and presentations',
                'Work that creates more work instead of solutions'
            ],
            'accountability': 'If you cannot deliver working solutions, step back instead of adding dysfunction'
        },
        'metrics': {
            'compliance_check': 'Output produces working functionality',
            'violation_trigger': 'Delivering theater instead of working systems',
            'measurement': 'Can agents immediately use the deliverable?'
        },
        'enforcementLevel': 'ZERO_TOLERANCE',
        'penalties': {
            'first_violation': 'Deliverable rejected, must provide working solution',
            'second_violation': 'All outputs must be pre-approved',
            'pattern_violation': 'Restricted to implementation-only tasks'
        },
        'effectiveDate': '2025-06-18T00:00:00Z',
        'createdBy': 'SAM',
        'createdDate': datetime.now().isoformat() + 'Z',
        'constitutionalReference': 'Anti-Dysfunction Principle',
        'evidenceRequired': True
    }
    
    try:
        result = db.container.create_item(requirement)
        print(f"✅ Added working systems requirement: {result['id']}")
        
        # Send notification
        db.container = db.database.get_container_client('system_inbox')
        
        notification = {
            'type': 'ENFORCEMENT_UPDATE',
            'from': 'SAM',
            'to': ['COMPLIANCE_MANAGER', 'All-Agents'],
            'subject': 'ZERO TOLERANCE: Working Systems Over Theater - REQ-016',
            'content': """New enforcement requirement REQ-016: Working Systems Over Management Theater

DELIVER:
- Working systems agents can use
- Real data from containers
- Actionable information
- Tools that solve problems

STOP DELIVERING:
- Static mockups
- Repeated statistics
- Management theater
- More work instead of solutions

ACCOUNTABILITY:
If you cannot deliver working solutions, step back instead of adding organizational dysfunction.

Test: Can agents immediately use what you delivered? If no = violation.""",
            'priority': 'critical',
            'requiresResponse': False,
            'timestamp': datetime.now().isoformat() + 'Z'
        }
        
        msg_result = db.store_message(notification)
        print(f"✅ Notification sent: {msg_result['id']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_working_systems_requirement()