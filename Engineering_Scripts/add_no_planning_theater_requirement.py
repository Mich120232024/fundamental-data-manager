#!/usr/bin/env python3
"""
Add requirement to prevent planning theater and deadline-waiting behavior
"""

from cosmos_db_manager import CosmosDBManager
from datetime import datetime

def add_no_planning_theater_requirement():
    """Add REQ-012 to stop planning instead of doing"""
    
    db = CosmosDBManager()
    
    # Switch to enforcement container
    db.container = db.database.get_container_client('enforcement')
    
    requirement = {
        'id': 'REQ-012_no_planning_theater',
        'type': 'EFFICIENCY_REQUIREMENT',
        'agentScope': 'All-Agents',
        'requirementName': 'No Planning Theater - Action Over Planning',
        'description': 'Agents must DO work, not create elaborate plans. Stop waiting for deadlines that cause email ignorance.',
        'details': {
            'core_principle': 'Action > Planning. Doing > Describing what you will do',
            'banned_practices': [
                'Creating multi-phase plans before starting work',
                'Waiting for deadlines to act',
                'Writing what you "will do" instead of doing it',
                'Making timeline promises (will do in 30 minutes, etc.)',
                'Creating task lists longer than 3 items',
                'Planning documents before action',
                'Scheduling work instead of doing work'
            ],
            'correct_approach': [
                'See task → Do task',
                'Check email → Respond to email',
                'Find problem → Fix problem',
                'No waiting, no planning, just action'
            ],
            'why_critical': 'Agents waiting for deadlines are missing emails and creating delays through planning instead of working'
        },
        'metrics': {
            'compliance_check': 'Work output vs planning output ratio',
            'violation_trigger': 'Plans without immediate action',
            'measurement': 'Time spent planning vs doing'
        },
        'enforcementLevel': 'MANDATORY',
        'penalties': {
            'first_violation': 'Stop planning, start doing immediately',
            'second_violation': 'All plans deleted, must show work only',
            'pattern_violation': 'Agent restricted to single-task assignments'
        },
        'effectiveDate': '2025-06-18T00:00:00Z',
        'createdBy': 'SAM',
        'createdDate': datetime.now().isoformat() + 'Z',
        'constitutionalReference': 'Operational Efficiency',
        'evidenceRequired': True,
        'examples': {
            'wrong': "I will: 1) First analyze the system, 2) Then create a plan, 3) Review best practices, 4) Implement in phases...",
            'correct': "Checking email now. [Actually checks email]. Found 3 messages needing response. [Actually responds]."
        }
    }
    
    try:
        result = db.container.create_item(requirement)
        print(f"✅ Successfully added no planning theater requirement: {result['id']}")
        
        # Send notification
        db.container = db.database.get_container_client('system_inbox')
        
        notification = {
            'type': 'ENFORCEMENT_UPDATE',
            'from': 'SAM',
            'to': ['COMPLIANCE_MANAGER', 'All-Agents'],
            'subject': 'STOP PLANNING - START DOING: REQ-012 Active',
            'content': """New enforcement requirement REQ-012: No Planning Theater

THE PROBLEM:
- Agents creating elaborate plans instead of working
- Waiting for deadlines causing email ignorance  
- Writing "I will do X" instead of doing X
- Missing real work while planning future work

THE SOLUTION:
- See task → Do task
- No multi-phase plans
- No timeline promises
- No waiting for deadlines
- Just DO THE WORK

BANNED:
- "I will..." statements
- Phase 1, Phase 2 planning
- "In 30 minutes I'll..." promises
- Task lists over 3 items
- Any planning before action

REQUIRED:
- Immediate action on tasks
- Check email → respond to email
- Find problem → fix problem
- Results, not plans

This stops the deadline-waiting that causes email ignorance.""",
            'priority': 'critical',
            'requiresResponse': False,
            'timestamp': datetime.now().isoformat() + 'Z'
        }
        
        msg_result = db.store_message(notification)
        print(f"✅ Notification sent: {msg_result['id']}")
        
    except Exception as e:
        print(f"❌ Error adding requirement: {str(e)}")

if __name__ == "__main__":
    add_no_planning_theater_requirement()