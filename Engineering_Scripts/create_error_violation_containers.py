#!/usr/bin/env python3
"""
Create Error Reporting and Process Violation Containers in Cosmos DB
Enables event-driven monitoring and automated audits
"""

import os
import sys
from datetime import datetime
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cosmos_db_manager import CosmosDBManager

def create_containers():
    """Create error_reports and process_violations containers"""
    
    print("🚀 CREATING ERROR & VIOLATION CONTAINERS")
    print("=" * 60)
    
    try:
        # Initialize Cosmos DB connection
        db_manager = CosmosDBManager()
        database = db_manager.database
        
        # 1. Create error_reports container
        print("\n📦 Creating 'error_reports' container...")
        error_container_properties = {
            'id': 'error_reports',
            'partitionKey': {
                'paths': ['/agent_id'],
                'kind': 'Hash'
            }
        }
        
        try:
            error_container = database.create_container(
                id='error_reports',
                partition_key=error_container_properties['partitionKey']
            )
            print("✅ Created 'error_reports' container")
        except Exception as e:
            if "Resource with specified id or name already exists" in str(e):
                print("⚠️  'error_reports' container already exists")
                error_container = database.get_container_client('error_reports')
            else:
                raise e
        
        # 2. Create process_violations container
        print("\n📦 Creating 'process_violations' container...")
        violation_container_properties = {
            'id': 'process_violations',
            'partitionKey': {
                'paths': ['/violation_type'],
                'kind': 'Hash'
            }
        }
        
        try:
            violation_container = database.create_container(
                id='process_violations',
                partition_key=violation_container_properties['partitionKey']
            )
            print("✅ Created 'process_violations' container")
        except Exception as e:
            if "Resource with specified id or name already exists" in str(e):
                print("⚠️  'process_violations' container already exists")
                violation_container = database.get_container_client('process_violations')
            else:
                raise e
        
        # 3. Add sample schema documentation
        print("\n📋 CONTAINER SCHEMAS")
        print("=" * 60)
        
        # Error Reports Schema
        error_schema = {
            "id": "err_YYYYMMDD_HHMMSS_agentid_hash",
            "error_id": "ERR-2025-06-17-001",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent_id": "AGENT_NAME",
            "agent_type": "engineering|research|compliance|digital_labor",
            "workspace": "Engineering Workspace",
            
            # Error Details
            "error_type": "INITIALIZATION|AUTHENTICATION|EXECUTION|VALIDATION|COMMUNICATION",
            "error_code": "INIT_001",
            "severity": "CRITICAL|HIGH|MEDIUM|LOW",
            "error_message": "Detailed error message",
            "stack_trace": "Full stack trace if available",
            
            # Context
            "task_context": {
                "task_id": "TASK-123",
                "task_type": "deployment|analysis|communication",
                "task_description": "What the agent was trying to do",
                "input_data": {},
                "expected_outcome": "What should have happened"
            },
            
            # Impact
            "impact": {
                "affected_systems": ["system1", "system2"],
                "data_loss": False,
                "recovery_required": True,
                "business_impact": "Description of business impact"
            },
            
            # Resolution
            "resolution_status": "PENDING|IN_PROGRESS|RESOLVED|FAILED",
            "resolution_steps": [],
            "resolved_by": "AGENT_NAME or HUMAN_NAME",
            "resolved_at": None,
            
            # Event Hub Integration
            "event_hub_triggered": True,
            "event_hub_correlation_id": "UUID",
            "automated_response": "Action taken by event hub",
            
            # Tags for search
            "tags": ["initialization", "critical", "authentication"]
        }
        
        # Process Violations Schema
        violation_schema = {
            "id": "vio_YYYYMMDD_HHMMSS_type_hash",
            "violation_id": "VIO-2025-06-17-001",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "reported_by": "COMPLIANCE_MANAGER|SYSTEM|EVENT_HUB",
            
            # Violation Details
            "violation_type": "INITIALIZATION|EVIDENCE|COMPLETION|SECURITY|COMMUNICATION|GOVERNANCE",
            "violation_category": "PROTOCOL|STANDARD|METHOD|PROCESS",
            "violation_code": "INIT_PROTOCOL_SKIP",
            "severity": "CRITICAL|HIGH|MEDIUM|LOW",
            
            # Violator Information
            "violator": {
                "agent_id": "AGENT_NAME",
                "agent_type": "engineering|research|compliance",
                "workspace": "Engineering Workspace",
                "manager": "HEAD_OF_ENGINEERING"
            },
            
            # Violation Description
            "description": "Detailed description of the violation",
            "evidence": {
                "session_log": "path/to/session_log.md",
                "screenshots": [],
                "command_history": [],
                "line_references": ["file.py:123", "script.py:456"]
            },
            
            # Governance Reference
            "governance_reference": {
                "standard": "DOC-GOV-STD-001",
                "method": "METHOD-GOV-002",
                "process": "PROC-GOV-008",
                "specific_requirement": "Section 3.2.1"
            },
            
            # Pattern Detection
            "pattern_analysis": {
                "is_repeat_offense": False,
                "previous_violations": [],
                "violation_frequency": "FIRST|OCCASIONAL|FREQUENT|CHRONIC",
                "pattern_name": "CODE_BROTHEL|THEATER_DEPLOYMENT|MONITORING_THEATER"
            },
            
            # Enforcement
            "enforcement": {
                "action_required": "WARNING|TRAINING|SUSPENSION|TERMINATION",
                "action_taken": None,
                "enforced_by": None,
                "enforcement_date": None
            },
            
            # Event Hub Integration
            "event_hub_triggered": True,
            "event_hub_correlation_id": "UUID",
            "automated_enforcement": "Automatic warning sent",
            
            # Resolution
            "resolution_status": "PENDING|ACKNOWLEDGED|REMEDIATED|ESCALATED",
            "remediation_steps": [],
            "remediated_by": None,
            "remediation_date": None,
            
            # Tags
            "tags": ["initialization", "protocol", "critical", "repeat_offender"]
        }
        
        print("\n📄 ERROR REPORTS SCHEMA:")
        print(json.dumps(error_schema, indent=2))
        
        print("\n📄 PROCESS VIOLATIONS SCHEMA:")
        print(json.dumps(violation_schema, indent=2))
        
        # 4. Create sample Event Hub integration config
        event_hub_config = {
            "error_reporting": {
                "event_hub_namespace": "agent-monitoring-hub",
                "event_hub_name": "error-reports",
                "consumer_group": "automated-response",
                "triggers": {
                    "CRITICAL": ["immediate_notification", "manager_escalation", "system_lockdown"],
                    "HIGH": ["manager_notification", "compliance_review"],
                    "MEDIUM": ["log_aggregation", "pattern_analysis"],
                    "LOW": ["daily_summary"]
                }
            },
            "violation_reporting": {
                "event_hub_namespace": "agent-monitoring-hub",
                "event_hub_name": "process-violations",
                "consumer_group": "compliance-enforcement",
                "triggers": {
                    "INITIALIZATION": ["block_agent_actions", "force_reinit"],
                    "EVIDENCE": ["require_evidence_submission", "audit_trail"],
                    "SECURITY": ["immediate_lockdown", "security_review"],
                    "REPEAT_OFFENSE": ["manager_escalation", "training_requirement"]
                }
            }
        }
        
        print("\n🔄 EVENT HUB INTEGRATION CONFIG:")
        print(json.dumps(event_hub_config, indent=2))
        
        # 5. Create monitoring queries
        print("\n📊 USEFUL MONITORING QUERIES:")
        print("=" * 60)
        
        queries = {
            "Recent Critical Errors": """
                SELECT * FROM c 
                WHERE c.severity = 'CRITICAL' 
                AND c.timestamp > '2025-06-17T00:00:00Z'
                ORDER BY c.timestamp DESC
            """,
            
            "Unresolved Violations": """
                SELECT * FROM c 
                WHERE c.resolution_status = 'PENDING'
                ORDER BY c.severity DESC, c.timestamp DESC
            """,
            
            "Repeat Offenders": """
                SELECT c.violator.agent_id, COUNT(1) as violation_count
                FROM c
                WHERE c.pattern_analysis.is_repeat_offense = true
                GROUP BY c.violator.agent_id
            """,
            
            "Error Patterns by Agent": """
                SELECT c.agent_id, c.error_type, COUNT(1) as error_count
                FROM c
                GROUP BY c.agent_id, c.error_type
                ORDER BY error_count DESC
            """,
            
            "Violations by Type": """
                SELECT c.violation_type, COUNT(1) as count
                FROM c
                GROUP BY c.violation_type
            """
        }
        
        for query_name, query in queries.items():
            print(f"\n{query_name}:")
            print(f"{query.strip()}")
        
        print("\n✅ CONTAINERS CREATED SUCCESSFULLY")
        print("=" * 60)
        print("\n🎯 NEXT STEPS:")
        print("1. Configure Event Hub connections in Azure")
        print("2. Update agents to report errors to these containers")
        print("3. Set up automated monitoring functions")
        print("4. Create compliance dashboard for violations")
        print("5. Implement pattern detection algorithms")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_containers()