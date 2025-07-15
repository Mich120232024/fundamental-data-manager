#!/usr/bin/env python3
"""
Add requirement for strict context separation and access control
"""

from cosmos_db_manager import CosmosDBManager
from datetime import datetime

def add_context_separation_requirement():
    """Add REQ-015 for context separation enforcement"""
    
    db = CosmosDBManager()
    
    # Switch to enforcement container
    db.container = db.database.get_container_client('enforcement')
    
    requirement = {
        'id': 'REQ-015_context_separation',
        'type': 'EFFICIENCY_REQUIREMENT',
        'agentScope': 'All-Agents',
        'requirementName': 'Context Separation - Strict Access Control',
        'description': 'Managers must NOT access emails/workspaces not explicitly intended for them. Clear access rules enforced.',
        'details': {
            'core_principle': 'Access only what is explicitly intended for you',
            'access_rules': {
                'SAM': 'Full access to everything including COMPLIANCE_MANAGER documents',
                'COMPLIANCE_MANAGER': 'Full access to everything including SAM documents',
                'HEAD_OF_DIGITAL_STAFF': 'Access to all agents EXCEPT SAM and COMPLIANCE_MANAGER. Analysis purpose only.',
                'HEAD_OF_ENGINEERING': 'Access to engineering workspace and engineering-related messages only',
                'HEAD_OF_RESEARCH': 'Access to research workspace and research-related messages only',
                'All_Other_Agents': 'Access to own workspace and messages TO them only'
            },
            'banned_practices': [
                'Reading emails not addressed to you',
                'Accessing other workspaces without authorization',
                'Checking other agents\' private documents',
                'Cross-contaminating context from unauthorized sources'
            ],
            'hds_special_rules': {
                'purpose': 'Analysis only - cannot use for decision making',
                'integrity_required': 'Must not contaminate own context with other agents\' information',
                'query_ethics': 'Read for system analysis, not personal advantage'
            }
        },
        'metrics': {
            'compliance_check': 'Query logs showing only authorized access',
            'violation_trigger': 'Accessing unauthorized emails/workspaces',
            'measurement': 'Unauthorized access attempts'
        },
        'enforcementLevel': 'MANDATORY',
        'penalties': {
            'first_violation': 'Access logged and reviewed',
            'second_violation': 'Restricted access permissions',
            'pattern_violation': 'Access revoked except own workspace'
        },
        'effectiveDate': '2025-06-18T00:00:00Z',
        'createdBy': 'SAM',
        'createdDate': datetime.now().isoformat() + 'Z',
        'constitutionalReference': 'Context Integrity',
        'evidenceRequired': True,
        'implementation': {
            'query_filtering': 'Filter messages by TO field before accessing',
            'workspace_boundaries': 'Check authorization before cross-workspace access',
            'audit_trail': 'Log all access attempts for review'
        }
    }
    
    try:
        result = db.container.create_item(requirement)
        print(f"✅ Successfully added context separation requirement: {result['id']}")
        
        # Send notification
        db.container = db.database.get_container_client('system_inbox')
        
        notification = {
            'type': 'ENFORCEMENT_UPDATE',
            'from': 'SAM',
            'to': ['COMPLIANCE_MANAGER', 'All-Agents'],
            'subject': 'STRICT ACCESS CONTROL: REQ-015 Context Separation',
            'content': """New enforcement requirement REQ-015: Context Separation

ACCESS RULES:
- SAM: Full access (including COMPLIANCE_MANAGER docs)
- COMPLIANCE_MANAGER: Full access (including SAM docs)  
- HEAD_OF_DIGITAL_STAFF: All agents EXCEPT SAM/COMPLIANCE (analysis only)
- HEAD_OF_ENGINEERING: Engineering workspace only
- HEAD_OF_RESEARCH: Research workspace only
- Other agents: Own workspace only

BANNED:
- Reading emails not TO you
- Accessing unauthorized workspaces
- Cross-contaminating context

SPECIAL RULES FOR HEAD_OF_DIGITAL_STAFF:
- Analysis purpose ONLY
- Cannot use for decisions
- Must maintain integrity in queries
- No context contamination

ENFORCEMENT:
- Query logs monitored
- Unauthorized access tracked
- Violations result in access restriction

Stay in your lane.""",
            'priority': 'critical',
            'requiresResponse': True,
            'timestamp': datetime.now().isoformat() + 'Z'
        }
        
        msg_result = db.store_message(notification)
        print(f"✅ Notification sent: {msg_result['id']}")
        
    except Exception as e:
        print(f"❌ Error adding requirement: {str(e)}")

if __name__ == "__main__":
    add_context_separation_requirement()