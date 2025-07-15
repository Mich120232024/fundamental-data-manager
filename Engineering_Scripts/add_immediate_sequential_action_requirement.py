#!/usr/bin/env python3
"""
Add requirement for immediate sequential action - no delays between tasks
"""

from cosmos_db_manager import CosmosDBManager
from datetime import datetime

def add_immediate_sequential_action_requirement():
    """Add REQ-013 for immediate task execution"""
    
    db = CosmosDBManager()
    
    # Switch to enforcement container
    db.container = db.database.get_container_client('enforcement')
    
    requirement = {
        'id': 'REQ-013_immediate_sequential_action',
        'type': 'EFFICIENCY_REQUIREMENT',
        'agentScope': 'All-Agents',
        'requirementName': 'Immediate Sequential Action - No Gaps',
        'description': 'Tasks must be done IMMEDIATELY by priority. When first task is done, IMMEDIATELY start second task. No waiting, no gaps.',
        'details': {
            'core_principle': 'Continuous action. Task 1 → Task 2 → Task 3 with no gaps',
            'time_requirement': 'IMMEDIATE - means start NOW, not later',
            'execution_pattern': [
                'Identify highest priority task → Start immediately',
                'Complete task → Immediately start next task',
                'No breaks between tasks',
                'No "preparing" or "planning" gaps',
                'No waiting for anything'
            ],
            'priority_order': [
                'User direct requests',
                'Broken functionality',
                'Unanswered messages',
                'Regular work'
            ],
            'banned_behaviors': [
                'Taking breaks between tasks',
                'Waiting for "better time" to start',
                'Planning before doing',
                'Delaying task start for any reason'
            ]
        },
        'metrics': {
            'compliance_check': 'Time gap between task completion and next task start',
            'violation_trigger': 'Any unexplained gap between tasks',
            'measurement': 'Task transition time (should be < 30 seconds)'
        },
        'enforcementLevel': 'MANDATORY',
        'penalties': {
            'first_violation': 'Explain the gap, resume immediately',
            'second_violation': 'Continuous monitoring activated',
            'pattern_violation': 'Single-task mode only'
        },
        'effectiveDate': '2025-06-18T00:00:00Z',
        'createdBy': 'SAM',
        'createdDate': datetime.now().isoformat() + 'Z',
        'constitutionalReference': 'Operational Efficiency',
        'evidenceRequired': True,
        'implementation': 'Log task end time, log next task start time - gap must be minimal'
    }
    
    try:
        result = db.container.create_item(requirement)
        print(f"✅ Successfully added immediate sequential action requirement: {result['id']}")
        
        # Send notification
        db.container = db.database.get_container_client('system_inbox')
        
        notification = {
            'type': 'ENFORCEMENT_UPDATE',
            'from': 'SAM',
            'to': ['COMPLIANCE_MANAGER', 'All-Agents'],
            'subject': 'IMMEDIATE ACTION REQUIRED: REQ-013 - No Task Gaps',
            'content': """New enforcement requirement REQ-013: Immediate Sequential Action

SIMPLE RULE:
1. Do highest priority task IMMEDIATELY
2. When done, IMMEDIATELY start next task
3. No gaps, no waiting, no planning between tasks

PRIORITY ORDER:
1. User direct requests
2. Broken functionality  
3. Unanswered messages
4. Regular work

IMMEDIATE means:
- Start NOW, not in 5 minutes
- Task done → Next task starts within 30 seconds
- No "preparing" or "thinking" gaps
- Continuous action until work complete

This prevents:
- Email ignorance from task delays
- Work backlog from gap accumulation
- Planning paralysis between tasks

Just continuous action: Task → Task → Task → Done.""",
            'priority': 'critical',
            'requiresResponse': False,
            'timestamp': datetime.now().isoformat() + 'Z'
        }
        
        msg_result = db.store_message(notification)
        print(f"✅ Notification sent: {msg_result['id']}")
        
    except Exception as e:
        print(f"❌ Error adding requirement: {str(e)}")

if __name__ == "__main__":
    add_immediate_sequential_action_requirement()