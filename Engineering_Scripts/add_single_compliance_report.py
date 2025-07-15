#!/usr/bin/env python3
"""
Example: How to add a single compliance report to the audit container
This shows the exact pattern agents can follow
"""

from cosmos_db_manager import get_db_manager
from datetime import datetime

def add_compliance_report_example():
    """Example of adding the Governance Assessment Report to audit container"""
    
    db = get_db_manager()
    audit_container = db.database.get_container_client('audit')
    
    # Create the compliance report entry with clear schema
    report_entry = {
        # Unique ID using date and hash
        'id': f"report_2025-06-11_{hash('Governance Assessment Report') % 10000:04d}",
        
        # Date for partitioning (YYYY-MM-DD)
        'auditDate': '2025-06-11',
        
        # Timestamp when added to database
        'timestamp': datetime.now().isoformat() + 'Z',
        
        # Type to identify compliance reports
        'audit_type': 'compliance_report',
        
        # Specific report type for categorization
        'report_type': 'governance_assessment',
        
        # Document information
        'document': {
            'name': 'Governance Assessment Report',
            'path': '/Governance Workspace/Audit/governance_assessment_report_2025-06-11.md',
            'type': 'compliance_analysis_report'
        },
        
        # WHO created this report
        'created_by': 'COMPLIANCE_MANAGER',
        
        # WHEN it was created
        'created_date': '2025-06-11',
        
        # WHY it was created (purpose)
        'purpose': 'Comprehensive evaluation of governance system effectiveness and agent compliance patterns',
        
        # FOR WHOM it was requested
        'requested_by': 'SAM',
        
        # Key findings summary
        'findings': '23% actual agent compliance. Governance theater detected - complex systems (163-line constitution, 485-line procedures) with minimal usage. 8/13 agents show zero engagement.',
        
        # Compliance score (0.0 to 1.0)
        'compliance_score': 0.23,
        
        # Status of the report
        'review_status': 'critical_action_required',
        
        # Recommendations from the report
        'recommendations': [
            'Archive complex governance documents',
            'Create 5-document Minimum Viable Governance',
            'Deploy automated monitoring/reminder systems',
            'Launch 3-agent pilot program',
            'Weekly iteration based on usage data'
        ],
        
        # Tags for searchability
        'tags': ['compliance', 'governance', 'assessment', 'critical', 'simplification'],
        
        # Additional metadata
        'key_metrics': {
            'current_compliance': 0.23,
            'engaged_agents': 5,
            'total_agents': 13,
            'document_count': 50,
            'recommended_docs': 5
        }
    }
    
    # Add to database
    try:
        result = audit_container.create_item(report_entry)
        print("✅ Report added successfully!")
        print(f"   ID: {result['id']}")
        print(f"   Report: {report_entry['document']['name']}")
        print(f"   Created by: {report_entry['created_by']}")
        print(f"   For: {report_entry['requested_by']}")
        print(f"   Purpose: {report_entry['purpose']}")
        print(f"   Compliance Score: {report_entry['compliance_score']*100:.0f}%")
        
        return result
        
    except Exception as e:
        print(f"❌ Failed to add report: {str(e)}")
        return None

def query_this_report():
    """Show how to query for this specific report"""
    
    db = get_db_manager()
    audit_container = db.database.get_container_client('audit')
    
    print("\n📋 QUERYING FOR THIS REPORT:")
    print("-" * 40)
    
    # Query by creator and date
    query = """
    SELECT * FROM audit 
    WHERE audit.created_by = 'COMPLIANCE_MANAGER' 
    AND audit.created_date = '2025-06-11'
    AND audit.audit_type = 'compliance_report'
    """
    
    results = list(audit_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    if results:
        report = results[0]
        print(f"Found: {report['document']['name']}")
        print(f"Score: {report['compliance_score']*100:.0f}%")
        print(f"Finding: {report['findings'][:100]}...")
        print(f"Status: {report['review_status']}")

def main():
    """Example workflow for adding compliance reports"""
    
    print("📚 COMPLIANCE REPORT ADDITION EXAMPLE")
    print("="*50)
    print("\nThis example shows how to add any compliance report to the audit container")
    print("with clear attribution: WHO, WHEN, WHY, and FOR WHOM\n")
    
    # Add the report
    result = add_compliance_report_example()
    
    if result:
        # Query it back
        query_this_report()
        
        print("\n💡 KEY SCHEMA FIELDS:")
        print("   • created_by: WHO created the report")
        print("   • created_date: WHEN it was created")
        print("   • purpose: WHY it was created")
        print("   • requested_by: FOR WHOM it was requested")
        print("   • findings: Summary of key findings")
        print("   • compliance_score: Numeric score (0.0-1.0)")
        print("   • recommendations: List of next actions")
        
        print("\n🔍 USEFUL QUERIES:")
        print("   • By creator: WHERE created_by = 'AGENT_NAME'")
        print("   • By date: WHERE created_date = 'YYYY-MM-DD'")
        print("   • By requester: WHERE requested_by = 'REQUESTER_NAME'")
        print("   • Low scores: WHERE compliance_score < 0.5")
        print("   • By type: WHERE report_type = 'governance_assessment'")

if __name__ == "__main__":
    main()