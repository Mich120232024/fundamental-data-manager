#!/usr/bin/env python3
"""
Create system enforcement container with compulsory efficiency requirements
For better agent control and performance monitoring
"""

from cosmos_db_manager import get_db_manager
from datetime import datetime
import json

def create_enforcement_container():
    """Create enforcement container with efficiency tracking"""
    
    print("🔨 Creating System Enforcement Container...")
    
    db = get_db_manager()
    
    try:
        database = db.client.get_database_client(db.database_name)
        
        # Create enforcement container with agent-based partitioning
        container = database.create_container(
            id='enforcement',
            partition_key={'paths': ['/agentId'], 'kind': 'Hash'},
            indexing_policy={
                'automatic': True,
                'indexingMode': 'consistent',
                'includedPaths': [{'path': '/*'}],
                'compositeIndexes': [
                    [
                        {'path': '/agentId', 'order': 'ascending'},
                        {'path': '/requirementType', 'order': 'ascending'},
                        {'path': '/complianceScore', 'order': 'descending'}
                    ],
                    [
                        {'path': '/enforcementLevel', 'order': 'ascending'},
                        {'path': '/lastChecked', 'order': 'descending'}
                    ]
                ]
            }
        )
        
        print("✅ Enforcement container created successfully!")
        return container
        
    except Exception as e:
        if "already exists" in str(e) or "Conflict" in str(e):
            print("ℹ️ Enforcement container already exists - ready to use")
            return database.get_container_client('enforcement')
        else:
            raise e

def create_compulsory_requirements():
    """Create compulsory efficiency requirements for all agents"""
    
    requirements = [
        {
            'id': 'REQ-001_message_response_time',
            'requirementId': 'REQ-001',
            'requirementType': 'communication_efficiency',
            'title': 'Message Response Time Requirement',
            'description': 'All agents must acknowledge messages within 24 hours and provide full response within 48 hours',
            'metrics': {
                'acknowledgment_sla': '24 hours',
                'response_sla': '48 hours',
                'escalation_threshold': '72 hours'
            },
            'enforcementLevel': 'MANDATORY',
            'penalties': {
                'first_violation': 'Warning logged',
                'second_violation': 'Manager notification',
                'third_violation': 'Performance review required'
            },
            'measurement': 'Time between message receipt and status update',
            'agentId': 'ALL_AGENTS',
            'effectiveDate': datetime.now().isoformat() + 'Z'
        },
        {
            'id': 'REQ-002_evidence_citation',
            'requirementId': 'REQ-002',
            'requirementType': 'quality_standards',
            'title': 'Evidence Citation Requirement',
            'description': 'All claims must include file:line citations or command:output evidence',
            'metrics': {
                'citation_rate': '100%',
                'acceptable_formats': ['file:line', 'command:output', 'container:query']
            },
            'enforcementLevel': 'MANDATORY',
            'penalties': {
                'violation': 'Message rejected, must resubmit with evidence'
            },
            'measurement': 'Percentage of claims with proper citations',
            'agentId': 'ALL_AGENTS',
            'effectiveDate': datetime.now().isoformat() + 'Z'
        },
        {
            'id': 'REQ-003_task_completion',
            'requirementId': 'REQ-003',
            'requirementType': 'productivity',
            'title': 'Task Completion Efficiency',
            'description': 'Assigned tasks must be completed or status updated within SLA',
            'metrics': {
                'simple_task_sla': '4 hours',
                'complex_task_sla': '24 hours',
                'status_update_required': '8 hours'
            },
            'enforcementLevel': 'MANDATORY',
            'penalties': {
                'missed_sla': 'Efficiency score reduction',
                'pattern_violation': 'Capability review'
            },
            'measurement': 'Time from task assignment to completion/update',
            'agentId': 'ALL_AGENTS',
            'effectiveDate': datetime.now().isoformat() + 'Z'
        },
        {
            'id': 'REQ-004_session_logging',
            'requirementId': 'REQ-004',
            'requirementType': 'operational_compliance',
            'title': 'Session Logging Requirement',
            'description': 'All work sessions must be logged with timestamps and evidence',
            'metrics': {
                'log_creation': 'Within 5 minutes of session start',
                'log_updates': 'Every significant action',
                'log_closure': 'Summary before session end'
            },
            'enforcementLevel': 'MANDATORY',
            'penalties': {
                'missing_logs': 'Work not credited',
                'incomplete_logs': 'Compliance score reduction'
            },
            'measurement': 'Session log completeness and timeliness',
            'agentId': 'ALL_AGENTS',
            'effectiveDate': datetime.now().isoformat() + 'Z'
        },
        {
            'id': 'REQ-005_no_fabrication',
            'requirementId': 'REQ-005',
            'requirementType': 'integrity',
            'title': 'Anti-Fabrication Requirement',
            'description': 'No fabricated metrics, percentages, or claims without calculation proof',
            'metrics': {
                'fabrication_tolerance': '0%',
                'banned_patterns': ['unverified %', 'approximately', 'around', 'estimated']
            },
            'enforcementLevel': 'ZERO_TOLERANCE',
            'penalties': {
                'any_violation': 'Immediate correction required + integrity review'
            },
            'measurement': 'Fabrication detection scan results',
            'agentId': 'ALL_AGENTS',
            'effectiveDate': datetime.now().isoformat() + 'Z'
        },
        {
            'id': 'REQ-006_initialization_protocol',
            'requirementId': 'REQ-006',
            'requirementType': 'startup_compliance',
            'title': '8-Step Initialization Protocol',
            'description': 'All agents must complete 8-step initialization at session start',
            'metrics': {
                'completion_required': '100%',
                'time_limit': '10 minutes',
                'steps': 8
            },
            'enforcementLevel': 'MANDATORY',
            'penalties': {
                'skipped_initialization': 'Session invalid, work not recognized'
            },
            'measurement': 'Initialization checklist completion',
            'agentId': 'ALL_AGENTS',
            'effectiveDate': datetime.now().isoformat() + 'Z'
        },
        {
            'id': 'REQ-007_cosmos_db_usage',
            'requirementId': 'REQ-007',
            'requirementType': 'technical_compliance',
            'title': 'Cosmos DB Communication Requirement',
            'description': 'All inter-agent communication must use Cosmos DB, not file system',
            'metrics': {
                'cosmos_usage': '100%',
                'file_messaging_allowed': '0%'
            },
            'enforcementLevel': 'MANDATORY',
            'penalties': {
                'file_messaging': 'Message ignored, must resend via Cosmos DB'
            },
            'measurement': 'Message routing compliance check',
            'agentId': 'ALL_AGENTS',
            'effectiveDate': datetime.now().isoformat() + 'Z'
        },
        {
            'id': 'REQ-008_manager_efficiency',
            'requirementId': 'REQ-008',
            'requirementType': 'management_performance',
            'title': 'Manager Response Efficiency',
            'description': 'Managers must review and respond to escalations within enhanced SLA',
            'metrics': {
                'escalation_response': '4 hours',
                'decision_communication': '8 hours',
                'team_status_updates': 'Daily'
            },
            'enforcementLevel': 'MANDATORY',
            'penalties': {
                'missed_sla': 'Escalation to SAM',
                'pattern_violation': 'Management review'
            },
            'measurement': 'Manager response times and decision quality',
            'agentId': 'ALL_MANAGERS',
            'effectiveDate': datetime.now().isoformat() + 'Z'
        }
    ]
    
    return requirements

def populate_enforcement_container():
    """Populate enforcement container with requirements"""
    
    db = get_db_manager()
    enforcement_container = db.database.get_container_client('enforcement')
    
    requirements = create_compulsory_requirements()
    
    print("\n📋 UPLOADING COMPULSORY EFFICIENCY REQUIREMENTS:")
    print("-" * 50)
    
    for req in requirements:
        try:
            result = enforcement_container.create_item(req)
            print(f"✅ {req['requirementId']}: {req['title']}")
        except Exception as e:
            if "Conflict" in str(e):
                print(f"ℹ️ {req['requirementId']} already exists")
            else:
                print(f"❌ Error uploading {req['requirementId']}: {e}")

def create_metadata_entry():
    """Create metadata entry for enforcement container"""
    
    db = get_db_manager()
    metadata_container = db.database.get_container_client('metadata')
    
    metadata = {
        'id': 'container_enforcement',
        'metaType': 'container_documentation',
        'container_name': 'enforcement',
        'purpose': 'System enforcement methods and compulsory efficiency requirements for agent control',
        'description': 'Tracks and enforces mandatory performance standards, efficiency metrics, and compliance requirements for all agents',
        'key_features': [
            'Compulsory efficiency requirements',
            'Performance SLA tracking',
            'Violation penalty system',
            'Agent control mechanisms',
            'Manager accountability metrics'
        ],
        'usage_examples': [
            'Check agent compliance score',
            'Review efficiency violations',
            'Track response time metrics',
            'Enforce evidence requirements',
            'Monitor initialization compliance'
        ],
        'partition_strategy': 'By agentId for efficient per-agent queries',
        'enforcement_levels': ['MANDATORY', 'ZERO_TOLERANCE', 'RECOMMENDED'],
        'createdDate': datetime.now().isoformat() + 'Z'
    }
    
    try:
        metadata_container.create_item(metadata)
        print("\n✅ Metadata entry created for enforcement container")
    except Exception as e:
        if "Conflict" in str(e):
            print("\nℹ️ Metadata already exists")

def main():
    """Create and populate enforcement container"""
    
    print("🚔 CREATING SYSTEM ENFORCEMENT INFRASTRUCTURE")
    print("=" * 60)
    print("Establishing compulsory efficiency requirements for agent control...")
    print()
    
    # Create container
    create_enforcement_container()
    
    # Populate with requirements
    populate_enforcement_container()
    
    # Create metadata
    create_metadata_entry()
    
    print("\n✅ ENFORCEMENT SYSTEM OPERATIONAL")
    print("=" * 60)
    print("📊 Enforcement Container Features:")
    print("   • 8 compulsory efficiency requirements")
    print("   • Zero-tolerance anti-fabrication")
    print("   • Response time SLAs enforced")
    print("   • Evidence requirements mandatory")
    print("   • Manager accountability included")
    print("   • Violation penalties defined")
    print("\n🎯 Agents are now subject to systematic efficiency control")

if __name__ == "__main__":
    main()