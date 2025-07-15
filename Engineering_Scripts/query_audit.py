#!/usr/bin/env python3
"""
Quick audit query tool for governance review
Helps navigate the governance mess systematically
"""

from cosmos_db_manager import get_db_manager
from datetime import datetime

def query_audits_by_status(status):
    """Find all audits with specific status"""
    
    db = get_db_manager()
    audit_container = db.database.get_container_client('audit')
    
    query = f"""
    SELECT * FROM audit 
    WHERE audit.review_status = '{status}'
    ORDER BY audit.priority DESC, audit.timestamp DESC
    """
    
    results = list(audit_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    print(f"\n📋 Audits with status '{status}': {len(results)}")
    for item in results:
        print(f"\n• {item['document']['name']}")
        print(f"  Findings: {item['findings']}")
        print(f"  Action: {item['action_required']}")
        print(f"  Owner: {item['responsible_agent']}")

def query_audits_by_agent(agent_name):
    """Find all audits assigned to specific agent"""
    
    db = get_db_manager()
    audit_container = db.database.get_container_client('audit')
    
    query = f"""
    SELECT * FROM audit 
    WHERE audit.responsible_agent = '{agent_name}'
    ORDER BY audit.priority DESC
    """
    
    results = list(audit_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    print(f"\n👤 {agent_name} Responsibilities: {len(results)} items")
    for item in results:
        priority_icon = "🔴" if item['priority'] == 'critical' else "🟡"
        print(f"\n{priority_icon} {item['document']['name']}")
        print(f"   Status: {item['review_status']}")
        print(f"   Action: {item['action_required']}")

def search_governance_issues(search_term):
    """Search for specific governance issues"""
    
    db = get_db_manager()
    audit_container = db.database.get_container_client('audit')
    
    query = f"""
    SELECT * FROM audit 
    WHERE CONTAINS(audit.findings, '{search_term}') 
    OR CONTAINS(audit.action_required, '{search_term}')
    ORDER BY audit.timestamp DESC
    """
    
    results = list(audit_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    print(f"\n🔍 Search results for '{search_term}': {len(results)} items")
    for item in results:
        print(f"\n• {item['document']['name']}")
        print(f"  Findings: {item['findings']}")

def get_low_compliance_items(threshold=0.5):
    """Find items with low compliance scores"""
    
    db = get_db_manager()
    audit_container = db.database.get_container_client('audit')
    
    query = f"""
    SELECT * FROM audit 
    WHERE audit.compliance_score < {threshold}
    AND audit.compliance_score != null
    ORDER BY audit.compliance_score ASC
    """
    
    results = list(audit_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    print(f"\n⚠️ LOW COMPLIANCE ITEMS (<{threshold*100}%):")
    for item in results:
        score = item['compliance_score'] * 100
        print(f"\n• {item['document']['name']} - {score:.1f}%")
        print(f"  Issue: {item['findings']}")
        print(f"  Fix: {item['action_required']}")

def generate_action_list():
    """Generate prioritized action list"""
    
    db = get_db_manager()
    audit_container = db.database.get_container_client('audit')
    
    query = """
    SELECT * FROM audit 
    WHERE audit.action_required != 'none'
    AND audit.action_required != 'Maintain current structure'
    ORDER BY 
        CASE audit.priority
            WHEN 'critical' THEN 0
            WHEN 'high' THEN 1
            WHEN 'medium' THEN 2
            ELSE 3
        END,
        audit.compliance_score ASC
    """
    
    results = list(audit_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    print("\n🎯 PRIORITIZED ACTION LIST")
    print("="*50)
    
    for i, item in enumerate(results, 1):
        priority_icon = {
            'critical': '🔴',
            'high': '🟡',
            'medium': '🟢'
        }.get(item['priority'], '⚪')
        
        print(f"\n{i}. {priority_icon} {item['action_required']}")
        print(f"   Document: {item['document']['name']}")
        print(f"   Owner: {item['responsible_agent']}")
        if item.get('compliance_score'):
            print(f"   Current compliance: {item['compliance_score']*100:.1f}%")

def main():
    """Interactive audit query tool"""
    
    print("🔍 GOVERNANCE AUDIT QUERY TOOL")
    print("="*40)
    
    while True:
        print("\nOptions:")
        print("1. View by status (critical_issues, action_required, etc)")
        print("2. View by responsible agent")
        print("3. Search for specific issues")
        print("4. Show low compliance items")
        print("5. Generate action list")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ")
        
        if choice == '1':
            status = input("Enter status: ")
            query_audits_by_status(status)
        elif choice == '2':
            agent = input("Enter agent name: ")
            query_audits_by_agent(agent)
        elif choice == '3':
            term = input("Search term: ")
            search_governance_issues(term)
        elif choice == '4':
            get_low_compliance_items()
        elif choice == '5':
            generate_action_list()
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    # Quick action list on startup
    generate_action_list()
    
    # Then interactive mode
    main()