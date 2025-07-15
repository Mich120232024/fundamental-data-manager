#!/usr/bin/env python3
"""
Add knowledge separation requirement to prevent AI knowledge contamination
"""

from cosmos_db_manager import CosmosDBManager
from datetime import datetime

def add_knowledge_separation_requirement():
    """Add REQ-010 for strict knowledge separation"""
    
    db = CosmosDBManager()
    
    # Switch to enforcement container
    db.container = db.database.get_container_client('enforcement')
    
    requirement = {
        'id': 'REQ-010_knowledge_separation',
        'type': 'EFFICIENCY_REQUIREMENT',
        'agentScope': 'All-Agents',
        'requirementName': 'Knowledge Separation - No AI Contamination',
        'description': 'Agents must NOT mix general AI knowledge with actual query results. Evidence from queries is more important than AI verbose explanations.',
        'details': {
            'core_principle': 'Query Results > AI Knowledge',
            'separation_required': [
                'Actual data from queries/files must be clearly labeled',
                'AI interpretations must be in separate sections',
                'No gap-filling with general knowledge',
                'No adding context not in the data'
            ],
            'banned_phrases': [
                'typically', 'usually', 'generally', 'in most cases',
                'this suggests', 'which means', 'indicating',
                'based on best practices', 'according to standards'
            ],
            'correct_pattern': 'Report ONLY what the query shows, nothing more'
        },
        'metrics': {
            'compliance_check': 'Response contains only cited data',
            'violation_trigger': 'Uncited assertions or AI knowledge mixed with results',
            'measurement': 'Knowledge contamination instances per session'
        },
        'enforcementLevel': 'ZERO_TOLERANCE',
        'penalties': {
            'first_violation': 'Immediate correction required',
            'second_violation': 'Response must be rewritten',
            'pattern_violation': 'Agent retraining on evidence standards'
        },
        'effectiveDate': '2025-06-18T00:00:00Z',
        'createdBy': 'SAM',
        'createdDate': datetime.now().isoformat() + 'Z',
        'constitutionalReference': 'Evidence-First Principle',
        'evidenceRequired': True,
        'examples': {
            'correct': "Query returned 23 violations: PROTOCOL(12), EVIDENCE(8), SECURITY(3)",
            'wrong': "Query returned 23 violations, which is typical for systems of this size"
        }
    }
    
    try:
        result = db.container.create_item(requirement)
        print(f"✅ Successfully added knowledge separation requirement: {result['id']}")
        
        # Also update the standards document
        db.container = db.database.get_container_client('documents')
        
        standard_doc = {
            'id': 'DOC-STD-010_knowledge_separation_standard',
            'type': 'STANDARD',
            'pillar': 'Standards',
            'title': 'Knowledge Separation Standard',
            'description': 'Prevent contamination of research results with general AI knowledge',
            'content': """# Knowledge Separation Standard

## Core Rule
Query Results > AI Knowledge

## Key Requirements
1. Label actual data clearly
2. Separate any analysis/interpretation 
3. No gap-filling with AI assumptions
4. Evidence citations for all claims

## Banned Practices
- Adding 'typical' or 'usual' context
- Interpreting beyond the data
- Mixing query results with AI knowledge
- Verbose explanations not in evidence

## Remember
The data speaks for itself. Report what's there, not what you think about it.""",
            'status': 'active',
            'version': '1.0',
            'effectiveDate': '2025-06-18T00:00:00Z',
            'lastModified': datetime.now().isoformat() + 'Z',
            'createdBy': 'SAM',
            'tags': ['evidence-first', 'anti-contamination', 'query-integrity']
        }
        
        doc_result = db.container.create_item(standard_doc)
        print(f"✅ Standard document created: {doc_result['id']}")
        
        # Send notification
        db.container = db.database.get_container_client('system_inbox')
        
        notification = {
            'type': 'ENFORCEMENT_UPDATE',
            'from': 'SAM',
            'to': ['COMPLIANCE_MANAGER', 'All-Agents'],
            'subject': 'ZERO TOLERANCE: Knowledge Separation Requirement Active',
            'content': """New enforcement requirement REQ-010: Knowledge Separation

CORE RULE: Query Results > AI Knowledge

Agents MUST NOT:
- Mix general AI knowledge with query results  
- Add interpretations unless explicitly requested
- Fill gaps with assumptions
- Use phrases like "typically" or "usually"

Agents MUST:
- Report ONLY what queries return
- Label data vs analysis clearly
- Cite every factual claim
- Keep responses focused on actual evidence

This is ZERO TOLERANCE - violations require immediate correction.

Standard documented at: /Governance Workspace/Standards/knowledge_separation_standard.md""",
            'priority': 'critical',
            'requiresResponse': True,
            'timestamp': datetime.now().isoformat() + 'Z'
        }
        
        msg_result = db.store_message(notification)
        print(f"✅ Critical notification sent: {msg_result['id']}")
        
    except Exception as e:
        print(f"❌ Error adding requirement: {str(e)}")

if __name__ == "__main__":
    add_knowledge_separation_requirement()