#!/usr/bin/env python3
"""
Migrate HEAD_OF_DIGITAL_STAFF to Context Memory System
Note: Lightest manager with outdated system knowledge - lowest risk
"""

import os
import json
from datetime import datetime
from cosmos_db_manager import CosmosDBManager

def migrate_head_of_digital_staff():
    """Migrate HEAD_OF_DIGITAL_STAFF context memory"""
    
    db = CosmosDBManager()
    agent_path = "/Users/mikaeleage/Research & Analytics Services/Digital Labor Workspace/Agent Roster/Managers/HEAD_OF_DIGITAL_STAFF"
    
    print("=== STARTING HEAD_OF_DIGITAL_STAFF MIGRATION ===")
    print("Reason: Lightest manager, outdated system knowledge, lowest risk\n")
    
    # 1. Create Layer 1: Constitutional Identity (immutable)
    layer_1 = {
        "agent_id": "MGR_002_HEAD_OF_DIGITAL_STAFF",
        "name": "HEAD_OF_DIGITAL_STAFF",
        "purpose": "Manage agent lifecycle, deployment, quality assurance, and digital labor optimization",
        "reports_to": "SAM",
        "boundaries": [
            "Cannot access SAM or COMPLIANCE_MANAGER private documents",
            "Cannot modify constitutional framework",
            "Cannot override compliance requirements",
            "Analysis access only for other agents"
        ],
        "protocols": [
            "Must use Cosmos DB for all communications",
            "Must provide evidence (file:line) for all claims",
            "Must follow 8-step initialization protocol",
            "Must maintain context separation (REQ-015)"
        ]
    }
    
    # 2. Create Layer 2: Compliance (COMPLIANCE_MANAGER controlled)
    layer_2 = {
        "version": "1.0.0",
        "last_updated": datetime.now().isoformat() + 'Z',
        "duties": [
            "Agent lifecycle management (creation to retirement)",
            "Quality assurance and performance monitoring",
            "Digital labor force optimization",
            "Deployment coordination and verification",
            "Agent health monitoring and intervention"
        ],
        "behavioral_guidelines": {
            "dos": [
                "Monitor agent performance metrics",
                "Coordinate agent deployments",
                "Maintain agent registry",
                "Ensure quality standards",
                "Document agent capabilities"
            ],
            "donts": [
                "Create theater instead of substance",
                "Access unauthorized agent data",
                "Make claims without verification",
                "Deploy without testing",
                "Ignore compliance violations"
            ]
        },
        "enforcement_requirements": [
            "REQ-002: Evidence citation required",
            "REQ-005: No fabrication (ZERO TOLERANCE)",
            "REQ-009: Email checking method",
            "REQ-010: Knowledge separation",
            "REQ-012: No planning theater",
            "REQ-015: Context separation",
            "REQ-016: Working systems over theater"
        ],
        "special_access": {
            "scope": "All agents except SAM and COMPLIANCE_MANAGER",
            "purpose": "Analysis only",
            "restriction": "Cannot use for decision making, must maintain integrity"
        }
    }
    
    # 3. Migrate Layer 3: Operational Context
    layer_3 = {
        "current_task": None,
        "active_todos": [],
        "knowledge_collection": {},
        "session_notes": [],
        "last_session": None
    }
    
    # Read todo_list.md
    todo_path = os.path.join(agent_path, "todo_list.md")
    if os.path.exists(todo_path):
        print("Migrating todo_list.md...")
        with open(todo_path, 'r') as f:
            todo_content = f.read()
            todos = []
            for line in todo_content.split('\n'):
                if '- [ ]' in line:
                    todos.append({
                        "task": line.replace('- [ ]', '').strip(),
                        "status": "pending",
                        "created": datetime.now().isoformat()
                    })
                elif '- [x]' in line:
                    todos.append({
                        "task": line.replace('- [x]', '').strip(),
                        "status": "completed",
                        "created": datetime.now().isoformat()
                    })
            layer_3["active_todos"] = [t for t in todos if t["status"] == "pending"]
            print(f"  Migrated {len(layer_3['active_todos'])} active todos")
    
    # Read development_journal.md (minimal as it's outdated)
    journal_path = os.path.join(agent_path, "development_journal.md")
    if os.path.exists(journal_path):
        print("Archiving development_journal.md (outdated)...")
        with open(journal_path, 'r') as f:
            journal_content = f.read()
            layer_3["knowledge_collection"]["archived_journal"] = {
                "content": journal_content,
                "note": "Pre-migration journal - system knowledge outdated"
            }
    
    # Get latest session
    logs_dir = os.path.join(agent_path, "logs")
    if os.path.exists(logs_dir):
        sessions = sorted([f for f in os.listdir(logs_dir) if f.startswith("session_")])
        if sessions:
            layer_3["last_session"] = sessions[-1]
            print(f"  Last session: {sessions[-1]}")
    
    # 4. Create initial Layer 4 analytics
    layer_4 = {
        "generated_at": datetime.now().isoformat() + 'Z',
        "migration_status": "management_pilot",
        "performance_metrics": {
            "total_files": 62,  # As counted
            "active_todos": len(layer_3["active_todos"]),
            "knowledge_status": "outdated - requires refresh",
            "migration_risk": "low - limited current system knowledge"
        },
        "recommendations": [
            "Refresh system knowledge post-migration",
            "Review current agent statuses",
            "Update deployment procedures"
        ]
    }
    
    # 5. Store in Cosmos DB metadata container
    context_doc = {
        "id": "CONTEXT_MEMORY_MGR_002_HEAD_OF_DIGITAL_STAFF",
        "type": "AGENT_CONTEXT_MEMORY",
        "agent_id": "MGR_002_HEAD_OF_DIGITAL_STAFF",
        "layer_1_constitutional": layer_1,
        "layer_2_compliance": layer_2,
        "layer_3_operational": layer_3,
        "layer_4_analytics": layer_4,
        "migration_date": datetime.now().isoformat() + 'Z',
        "migration_phase": "management_team",
        "status": "active"
    }
    
    db.container = db.database.get_container_client('metadata')
    
    try:
        result = db.container.create_item(context_doc)
        print(f"\n✅ Successfully migrated HEAD_OF_DIGITAL_STAFF to Context Memory")
        print(f"   Document ID: {result['id']}")
        
        # Create migration report
        report = {
            "agent": "HEAD_OF_DIGITAL_STAFF",
            "migration_date": datetime.now().isoformat(),
            "phase": "Management Team (2/4)",
            "files_found": 62,
            "todos_migrated": len(layer_3["active_todos"]),
            "risk_level": "LOW",
            "special_notes": "Outdated system knowledge - lowest risk for pilot",
            "context_id": result['id']
        }
        
        print("\n=== MIGRATION REPORT ===")
        for key, value in report.items():
            print(f"{key}: {value}")
            
        # Store report in audit container
        db.container = db.database.get_container_client('audit')
        audit_doc = {
            "id": f"MIGRATION_REPORT_HDS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "MIGRATION_REPORT",
            "report": report
        }
        db.container.create_item(audit_doc)
        print("\n✅ Migration report stored in audit container")
            
        return report
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return None

if __name__ == "__main__":
    migrate_head_of_digital_staff()