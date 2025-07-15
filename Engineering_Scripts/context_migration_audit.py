#!/usr/bin/env python3
"""
Audit questionnaire for context memory migration quality
"""

from cosmos_db_manager import CosmosDBManager
import json

def audit_migration(agent_id="ENG_002_DATA_ANALYST"):
    """Run structured audit of migrated context"""
    
    db = CosmosDBManager()
    db.container = db.database.get_container_client('metadata')
    
    print(f"=== CONTEXT MIGRATION AUDIT: {agent_id} ===\n")
    
    # Retrieve migrated context
    try:
        # Query for the document
        docs = db.query_messages(f"SELECT * FROM c WHERE c.id = 'CONTEXT_MEMORY_{agent_id}'")
        if docs:
            context = docs[0]
        else:
            print("❌ No context found in Cosmos DB")
            return False
    except Exception as e:
        print(f"❌ Failed to retrieve context from Cosmos DB: {e}")
        return False
    
    # Structured audit questions
    audit_results = {
        "agent_id": agent_id,
        "audit_date": datetime.now().isoformat(),
        "checks": {}
    }
    
    print("LAYER 1 - CONSTITUTIONAL IDENTITY")
    print("-" * 40)
    layer1 = context.get("layer_1_constitutional", {})
    
    # Check 1: Identity completeness
    required_fields = ["agent_id", "name", "purpose", "reports_to", "boundaries", "protocols"]
    missing = [f for f in required_fields if f not in layer1]
    
    audit_results["checks"]["identity_complete"] = len(missing) == 0
    print(f"✓ Identity fields complete: {len(missing) == 0}")
    if missing:
        print(f"  Missing: {missing}")
    
    # Check 2: Purpose clarity
    purpose_clear = len(layer1.get("purpose", "")) > 20
    audit_results["checks"]["purpose_clear"] = purpose_clear
    print(f"✓ Purpose clearly defined: {purpose_clear}")
    print(f"  Purpose: {layer1.get('purpose', 'NOT DEFINED')}")
    
    print("\nLAYER 2 - COMPLIANCE DYNAMICS")
    print("-" * 40)
    layer2 = context.get("layer_2_compliance", {})
    
    # Check 3: Enforcement requirements
    has_requirements = "enforcement_requirements" in layer2
    audit_results["checks"]["enforcement_present"] = has_requirements
    print(f"✓ Enforcement requirements present: {has_requirements}")
    if has_requirements:
        print(f"  Requirements: {len(layer2['enforcement_requirements'])}")
    
    # Check 4: Behavioral guidelines
    has_dos_donts = "behavioral_guidelines" in layer2
    audit_results["checks"]["guidelines_present"] = has_dos_donts
    print(f"✓ Behavioral guidelines defined: {has_dos_donts}")
    
    print("\nLAYER 3 - OPERATIONAL CONTEXT")
    print("-" * 40)
    layer3 = context.get("layer_3_operational", {})
    
    # Check 5: TODO migration
    todos_migrated = len(layer3.get("active_todos", [])) > 0
    audit_results["checks"]["todos_migrated"] = todos_migrated
    print(f"✓ TODOs successfully migrated: {todos_migrated}")
    print(f"  Active TODOs: {len(layer3.get('active_todos', []))}")
    
    # Check 6: Knowledge preservation
    knowledge_preserved = len(layer3.get("knowledge_collection", {})) > 0
    audit_results["checks"]["knowledge_preserved"] = knowledge_preserved
    print(f"✓ Knowledge collection preserved: {knowledge_preserved}")
    
    print("\nLAYER 4 - ANALYTICS")
    print("-" * 40)
    layer4 = context.get("layer_4_analytics", {})
    
    # Check 7: Metrics generation
    has_metrics = "performance_metrics" in layer4
    audit_results["checks"]["metrics_generated"] = has_metrics
    print(f"✓ Performance metrics generated: {has_metrics}")
    
    # Overall assessment
    passed_checks = sum(audit_results["checks"].values())
    total_checks = len(audit_results["checks"])
    
    print(f"\n=== AUDIT SUMMARY ===")
    print(f"Passed: {passed_checks}/{total_checks} checks")
    print(f"Score: {(passed_checks/total_checks)*100:.1f}%")
    
    # Quality determination
    if passed_checks == total_checks:
        print("\n✅ MIGRATION QUALITY: EXCELLENT - Ready for rollout")
        audit_results["quality"] = "EXCELLENT"
    elif passed_checks >= total_checks * 0.8:
        print("\n⚠️ MIGRATION QUALITY: GOOD - Minor improvements needed")
        audit_results["quality"] = "GOOD"
    else:
        print("\n❌ MIGRATION QUALITY: POOR - Significant work required")
        audit_results["quality"] = "POOR"
    
    # Store audit results
    audit_doc = {
        "id": f"AUDIT_CONTEXT_MIGRATION_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "type": "MIGRATION_AUDIT",
        "results": audit_results
    }
    
    db.container = db.database.get_container_client('audit')
    db.container.create_item(audit_doc)
    
    return audit_results

if __name__ == "__main__":
    from datetime import datetime
    audit_migration()