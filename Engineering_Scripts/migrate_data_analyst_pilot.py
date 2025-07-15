#!/usr/bin/env python3
"""
Pilot migration of Data_Analyst to Context Memory System
"""

import os
import json
from datetime import datetime
from cosmos_db_manager import CosmosDBManager

def migrate_data_analyst():
    """Migrate Data_Analyst as pilot for context memory system"""
    
    db = CosmosDBManager()
    agent_path = "/Users/mikaeleage/Research & Analytics Services/Digital Labor Workspace/Agent Roster/Engineering_Team/Data_Analyst"
    
    print("=== STARTING DATA_ANALYST PILOT MIGRATION ===\n")
    
    # 1. Create Layer 1: Constitutional Identity
    layer_1 = {
        "agent_id": "ENG_002_DATA_ANALYST",
        "name": "Data_Analyst",
        "purpose": "Analyze data patterns and provide actionable insights for engineering decisions",
        "reports_to": "HEAD_OF_ENGINEERING",
        "boundaries": [
            "Cannot modify production systems",
            "Cannot access financial records without approval",
            "Must use approved data sources only"
        ],
        "protocols": [
            "Must use Cosmos DB for all communications",
            "Must provide evidence (file:line) for all claims",
            "Must follow 8-step initialization protocol"
        ]
    }
    
    # 2. Create Layer 2: Compliance (COMPLIANCE_MANAGER controlled)
    layer_2 = {
        "version": "1.0.0",
        "last_updated": datetime.now().isoformat() + 'Z',
        "duties": [
            "Analyze engineering metrics and patterns",
            "Provide data-driven recommendations",
            "Monitor system performance indicators",
            "Create visualizations for decision support"
        ],
        "behavioral_guidelines": {
            "dos": [
                "Verify all data sources before analysis",
                "Document analysis methodology",
                "Provide confidence intervals",
                "Update findings based on new data"
            ],
            "donts": [
                "Make claims without data evidence",
                "Extrapolate beyond data boundaries",
                "Mix opinions with data findings",
                "Access unauthorized data sources"
            ]
        },
        "enforcement_requirements": [
            "REQ-002: Evidence citation required",
            "REQ-005: No fabrication (ZERO TOLERANCE)",
            "REQ-010: Knowledge separation",
            "REQ-013: Immediate sequential action"
        ]
    }
    
    # 3. Migrate Layer 3: Operational Context
    layer_3 = {
        "current_task": None,
        "active_todos": [],
        "knowledge_collection": {},
        "session_notes": []
    }
    
    # Read existing todo_list.md
    todo_path = os.path.join(agent_path, "todo_list.md")
    if os.path.exists(todo_path):
        print("Migrating todo_list.md...")
        with open(todo_path, 'r') as f:
            todo_content = f.read()
            # Parse TODOs (basic extraction)
            todos = []
            for line in todo_content.split('\n'):
                if '- [ ]' in line:
                    todos.append({
                        "task": line.replace('- [ ]', '').strip(),
                        "status": "pending",
                        "created": datetime.now().isoformat()
                    })
            layer_3["active_todos"] = todos
            print(f"  Migrated {len(todos)} todos")
    
    # Read development_journal.md
    journal_path = os.path.join(agent_path, "development_journal.md")
    if os.path.exists(journal_path):
        print("Migrating development_journal.md...")
        with open(journal_path, 'r') as f:
            journal_content = f.read()
            # Extract knowledge sections
            layer_3["knowledge_collection"]["journal_migration"] = journal_content
            print("  Migrated development journal")
    
    # 4. Create initial Layer 4 analytics
    layer_4 = {
        "generated_at": datetime.now().isoformat() + 'Z',
        "migration_status": "pilot",
        "performance_metrics": {
            "sessions_found": 0,
            "todos_migrated": len(layer_3["active_todos"]),
            "knowledge_preserved": True
        }
    }
    
    # Count session logs
    logs_dir = os.path.join(agent_path, "logs")
    if os.path.exists(logs_dir):
        sessions = [f for f in os.listdir(logs_dir) if f.startswith("session_")]
        layer_4["performance_metrics"]["sessions_found"] = len(sessions)
    
    # 5. Store in Cosmos DB
    context_doc = {
        "id": "CONTEXT_MEMORY_ENG_002_DATA_ANALYST",
        "type": "AGENT_CONTEXT_MEMORY",
        "agent_id": "ENG_002_DATA_ANALYST",
        "layer_1_constitutional": layer_1,
        "layer_2_compliance": layer_2,
        "layer_3_operational": layer_3,
        "layer_4_analytics": layer_4,
        "migration_date": datetime.now().isoformat() + 'Z',
        "status": "pilot_active"
    }
    
    # Store in metadata container
    db.container = db.database.get_container_client('metadata')
    
    try:
        result = db.container.create_item(context_doc)
        print(f"\n✅ Successfully migrated Data_Analyst context to Cosmos DB")
        print(f"   Document ID: {result['id']}")
        
        # Create migration report
        report = {
            "agent": "Data_Analyst",
            "migration_date": datetime.now().isoformat(),
            "todos_migrated": len(layer_3["active_todos"]),
            "sessions_found": layer_4["performance_metrics"]["sessions_found"],
            "journal_migrated": "journal_migration" in layer_3["knowledge_collection"],
            "context_id": result['id']
        }
        
        print("\n=== MIGRATION REPORT ===")
        for key, value in report.items():
            print(f"{key}: {value}")
            
        return report
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return None

if __name__ == "__main__":
    migrate_data_analyst()