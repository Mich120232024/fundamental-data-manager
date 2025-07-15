#!/usr/bin/env python3
"""
Add requirement to prevent arbitrary deadline creation by agents
"""

from cosmos_db_manager import CosmosDBManager
from datetime import datetime

def add_no_arbitrary_deadlines_requirement():
    """Add REQ-011 to stop agents creating time pressure"""
    
    db = CosmosDBManager()
    
    # Switch to enforcement container
    db.container = db.database.get_container_client('enforcement')
    
    requirement = {
        'id': 'REQ-011_no_arbitrary_deadlines',
        'type': 'EFFICIENCY_REQUIREMENT',
        'agentScope': 'All-Agents',
        'requirementName': 'No Arbitrary Deadlines - User-Driven Time Only',
        'description': 'Agents must NOT create arbitrary time-based deadlines or SLAs. Time references are only for logging/dating unless explicitly required by USER.',
        'details': {
            'core_principle': 'Quality > Speed. User requirements > Agent-imposed deadlines',
            'allowed_time_usage': [
                'Timestamps in logs and filenames',
                'Dating messages and documents',
                'Recording when actions occurred',
                'User-specified deadlines ONLY'
            ],
            'banned_practices': [
                'Creating 24hr/48hr response requirements',
                '4hr task completion SLAs',
                'Escalation timeframes not requested by user',
                'Any deadline not explicitly from user',
                'Time pressure that ignores work quality'
            ],
            'correct_approach': 'Focus on completeness and accuracy, not artificial speed'
        },
        'metrics': {
            'compliance_check': 'No agent-created deadlines in messages or requirements',
            'violation_trigger': 'Any time-based requirement not from user',
            'measurement': 'Arbitrary deadline instances'
        },
        'enforcementLevel': 'MANDATORY',
        'penalties': {
            'first_violation': 'Remove arbitrary deadline immediately',
            'second_violation': 'Review all agent communications for deadline pollution',
            'pattern_violation': 'Agent prohibited from setting any timeframes'
        },
        'effectiveDate': '2025-06-18T00:00:00Z',
        'createdBy': 'SAM',
        'createdDate': datetime.now().isoformat() + 'Z',
        'constitutionalReference': 'User-Driven Operations Principle',
        'evidenceRequired': True,
        'rationale': 'Agent-imposed deadlines create email pattern ignorance and rush poor quality work'
    }
    
    try:
        result = db.container.create_item(requirement)
        print(f"✅ Successfully added no arbitrary deadlines requirement: {result['id']}")
        
        # Now we need to update/supersede the time-based requirements
        # Create supersession notices
        superseded_reqs = ['REQ-001', 'REQ-003', 'REQ-008']
        
        for req_id in superseded_reqs:
            supersession = {
                'id': f'SUPERSESSION_{req_id}_by_REQ-011',
                'type': 'REQUIREMENT_UPDATE',
                'originalRequirement': req_id,
                'supersededBy': 'REQ-011',
                'reason': 'Arbitrary time-based SLAs create wrong behaviors',
                'newGuidance': 'Quality and completeness over artificial speed. Only user-specified deadlines apply.',
                'effectiveDate': datetime.now().isoformat() + 'Z',
                'createdBy': 'SAM'
            }
            
            try:
                db.container.create_item(supersession)
                print(f"✅ Superseded {req_id}")
            except:
                print(f"⚠️  Could not create supersession for {req_id}")
        
        # Send notification
        db.container = db.database.get_container_client('system_inbox')
        
        notification = {
            'type': 'ENFORCEMENT_UPDATE',
            'from': 'SAM',
            'to': ['COMPLIANCE_MANAGER', 'All-Agents'],
            'subject': 'CRITICAL: No More Arbitrary Deadlines - REQ-011 Active',
            'content': """New enforcement requirement REQ-011: No Arbitrary Deadlines

EFFECTIVE IMMEDIATELY:
- NO agent-created time requirements (24hr, 48hr, 4hr, etc.)
- NO artificial urgency or SLAs
- Time is ONLY for timestamps and user requirements

SUPERSEDED:
- REQ-001 (message response times) - Work at proper pace
- REQ-003 (task completion times) - Focus on quality
- REQ-008 (escalation timeframes) - Escalate when needed

WHY:
These arbitrary deadlines were creating email pattern ignorance and rushed, poor quality work. 

NEW APPROACH:
- Quality over speed
- Completeness over deadlines
- User requirements over agent-imposed timeframes
- Timestamps for logging only

If the USER specifies a deadline, honor it. Otherwise, do the work properly without artificial time pressure.""",
            'priority': 'critical',
            'requiresResponse': False,
            'timestamp': datetime.now().isoformat() + 'Z'
        }
        
        msg_result = db.store_message(notification)
        print(f"✅ Critical notification sent: {msg_result['id']}")
        
    except Exception as e:
        print(f"❌ Error adding requirement: {str(e)}")

if __name__ == "__main__":
    add_no_arbitrary_deadlines_requirement()