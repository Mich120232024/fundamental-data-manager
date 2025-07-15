#!/usr/bin/env python3
"""
Migrate Engineering Workspace documents according to SAM's semantic policy
Manual migration helper for HEAD_OF_ENGINEERING workspace
"""

from cosmos_db_manager import get_db_manager
from datetime import datetime
import os

def get_engineering_documents():
    """List key Engineering Workspace documents for migration"""
    
    documents = [
        {
            'local_path': '/Engineering Workspace/documentation/cosmos_db_schema_proposal.md',
            'doc_id': 'GUIDE-ENG-001_cosmos_db_schema_proposal',
            'name': 'Cosmos DB Schema Proposal',
            'type': 'guide',
            'category': 'engineering',
            'status': 'active',
            'owner': 'HEAD_OF_ENGINEERING',
            'audience': 'managers',
            'complexity': 'advanced',
            'compliance': 'recommended',
            'evidence': 'none',
            'container': 'documents'
        },
        {
            'local_path': '/Engineering Workspace/scripts/cosmos_db_manager.py',
            'doc_id': 'GUIDE-ENG-002_cosmos_db_operations',
            'name': 'Cosmos DB Operations Manager',
            'type': 'guide',
            'category': 'engineering',
            'status': 'active',
            'owner': 'HEAD_OF_ENGINEERING',
            'audience': 'all',
            'complexity': 'intermediate',
            'compliance': 'mandatory',
            'evidence': 'none',
            'container': 'documents'
        },
        {
            'local_path': '/Governance Workspace/Procedures/cosmos_db_operations_procedure.md',
            'doc_id': 'PROC-ENG-001_cosmos_db_operations',
            'name': 'Cosmos DB Operations Procedure',
            'type': 'procedure',
            'category': 'engineering',
            'status': 'active',
            'owner': 'HEAD_OF_ENGINEERING',
            'audience': 'all',
            'complexity': 'intermediate',
            'compliance': 'mandatory',
            'frequency': 'as-needed',
            'evidence': 'optional',
            'container': 'processes'
        },
        {
            'local_path': '/Governance Workspace/Operational Processes/cosmos_db_agent_connection_process.md',
            'doc_id': 'PROC-ENG-002_agent_connection',
            'name': 'Agent Connection Process',
            'type': 'procedure',
            'category': 'engineering',
            'status': 'active',
            'owner': 'HEAD_OF_ENGINEERING',
            'audience': 'all',
            'complexity': 'basic',
            'compliance': 'mandatory',
            'frequency': 'as-needed',
            'evidence': 'required',
            'container': 'processes'
        },
        {
            'local_path': '/Research Workspace/Knowledge Base/cosmos_db_evolution_research.md',
            'doc_id': 'GUIDE-ENG-003_cosmos_evolution',
            'name': 'Cosmos DB Evolution Research',
            'type': 'guide',
            'category': 'engineering',
            'status': 'active',
            'owner': 'HEAD_OF_ENGINEERING',
            'audience': 'managers',
            'complexity': 'advanced',
            'compliance': 'optional',
            'evidence': 'none',
            'container': 'documents'
        }
    ]
    
    return documents

def create_migration_entry(doc_info):
    """Create a migration entry following SAM's semantic policy"""
    
    if doc_info['container'] == 'processes':
        return {
            'id': doc_info['doc_id'],
            'processId': doc_info['doc_id'],
            'processName': doc_info['name'],
            
            # Categorization per semantic policy
            'department': doc_info['category'],
            'category': 'operational' if doc_info['type'] == 'procedure' else 'technical',
            
            # Required tags
            'type': doc_info['type'],
            'status': doc_info['status'],
            'owner': doc_info['owner'],
            'audience': doc_info['audience'],
            
            # Optional tags
            'complexity': doc_info.get('complexity', 'intermediate'),
            'compliance': doc_info.get('compliance', 'recommended'),
            'frequency': doc_info.get('frequency', 'as-needed'),
            'evidence': doc_info.get('evidence', 'optional'),
            
            # Metadata
            'originalPath': doc_info['local_path'],
            'migratedDate': datetime.now().isoformat() + 'Z',
            'migratedBy': 'HEAD_OF_ENGINEERING',
            
            # Semantic tags for discovery
            'tags': [
                doc_info['type'],
                doc_info['category'],
                doc_info['status'],
                f"owner:{doc_info['owner']}",
                f"audience:{doc_info['audience']}",
                f"compliance:{doc_info['compliance']}"
            ],
            
            # Placeholder content - manual migration will add full content
            'content': f"See {doc_info['local_path']} for full content",
            'contentType': 'link',
            
            # Tracking
            'createdBy': 'HEAD_OF_ENGINEERING',
            'createdDate': datetime.now().isoformat() + 'Z'
        }
    else:  # documents container
        return {
            'id': doc_info['doc_id'],
            'documentId': doc_info['doc_id'],
            'title': doc_info['name'],
            
            # Categorization
            'workspace': 'engineering',
            'docType': doc_info['type'],
            'category': 'technical',
            
            # Required tags
            'type': doc_info['type'],
            'status': doc_info['status'],
            'owner': doc_info['owner'],
            'audience': doc_info['audience'],
            
            # Optional tags
            'complexity': doc_info.get('complexity', 'intermediate'),
            'compliance': doc_info.get('compliance', 'recommended'),
            'evidence': doc_info.get('evidence', 'none'),
            
            # Metadata
            'originalPath': doc_info['local_path'],
            'migratedDate': datetime.now().isoformat() + 'Z',
            'migratedBy': 'HEAD_OF_ENGINEERING',
            
            # Semantic tags
            'tags': [
                doc_info['type'],
                doc_info['category'],
                doc_info['status'],
                f"owner:{doc_info['owner']}",
                f"audience:{doc_info['audience']}"
            ],
            
            # Content placeholder
            'abstract': f"{doc_info['name']} - Engineering documentation",
            'content': f"See {doc_info['local_path']} for full content",
            'contentType': 'link',
            'format': 'markdown',
            
            # Version
            'version': '1.0',
            
            # Tracking
            'createdBy': 'HEAD_OF_ENGINEERING',
            'createdDate': datetime.now().isoformat() + 'Z'
        }

def display_migration_plan():
    """Display migration plan for manual execution"""
    
    print("📋 ENGINEERING WORKSPACE MIGRATION PLAN")
    print("="*60)
    print("Following SAM's Semantic Policy for Document Migration\n")
    
    documents = get_engineering_documents()
    
    processes = [d for d in documents if d['container'] == 'processes']
    docs = [d for d in documents if d['container'] == 'documents']
    
    print("🔧 PROCESSES TO MIGRATE:")
    print("-"*40)
    for proc in processes:
        print(f"• {proc['doc_id']}")
        print(f"  Name: {proc['name']}")
        print(f"  Tags: type:{proc['type']}, compliance:{proc['compliance']}, evidence:{proc['evidence']}")
        print(f"  Path: {proc['local_path']}")
        print()
    
    print("\n📄 DOCUMENTS TO MIGRATE:")
    print("-"*40)
    for doc in docs:
        print(f"• {doc['doc_id']}")
        print(f"  Name: {doc['name']}")
        print(f"  Tags: type:{doc['type']}, audience:{doc['audience']}, complexity:{doc['complexity']}")
        print(f"  Path: {doc['local_path']}")
        print()
    
    print("\n🏷️ SEMANTIC TAG SUMMARY:")
    print("-"*40)
    print("All documents tagged with:")
    print("• type (procedure|guide)")
    print("• category (engineering)")
    print("• status (active)")
    print("• owner (HEAD_OF_ENGINEERING)")
    print("• audience (all|managers)")
    print("\nOptional tags applied where relevant:")
    print("• complexity, compliance, frequency, evidence")
    
    print("\n📊 MIGRATION BENEFITS:")
    print("-"*40)
    print('• Query: "Show all mandatory engineering procedures"')
    print('• Query: "Find engineering guides for managers"')
    print('• Query: "What documents does HEAD_OF_ENGINEERING own?"')
    print('• Query: "Show all procedures requiring evidence"')
    
    print("\n✅ NEXT STEPS:")
    print("-"*40)
    print("1. Review document list above")
    print("2. Manually copy content to Cosmos DB entries")
    print("3. Update status in local tracking")
    print("4. Notify team of migrated documents")
    print("\n(Agent logs remain local for privacy as per SAM's policy)")

def generate_sample_queries():
    """Generate sample queries for migrated documents"""
    
    print("\n🔍 SAMPLE QUERIES FOR MIGRATED DOCUMENTS:")
    print("="*60)
    
    queries = [
        {
            'description': 'Find all mandatory engineering procedures',
            'query': '''
SELECT * FROM processes 
WHERE processes.category = 'engineering' 
AND processes.compliance = 'mandatory'
AND processes.type = 'procedure'
'''
        },
        {
            'description': 'Get engineering guides for advanced users',
            'query': '''
SELECT * FROM documents 
WHERE documents.category = 'engineering'
AND documents.type = 'guide'
AND documents.complexity = 'advanced'
'''
        },
        {
            'description': 'Show all HEAD_OF_ENGINEERING owned docs',
            'query': '''
SELECT * FROM c 
WHERE c.owner = 'HEAD_OF_ENGINEERING'
AND c.status = 'active'
'''
        },
        {
            'description': 'Find procedures requiring evidence',
            'query': '''
SELECT * FROM processes 
WHERE processes.evidence = 'required'
ORDER BY processes.compliance DESC
'''
        }
    ]
    
    for q in queries:
        print(f"\n📌 {q['description']}:")
        print(q['query'])

def main():
    """Display migration plan for HEAD_OF_ENGINEERING workspace"""
    
    display_migration_plan()
    generate_sample_queries()
    
    print("\n" + "="*60)
    print("🚀 READY FOR MANUAL MIGRATION")
    print("="*60)
    print("\nThis plan follows SAM's semantic policy:")
    print("• Clear naming convention: {type}-{category}-{identifier}_{name}")
    print("• Consistent tagging for instant discovery")
    print("• Privacy preserved (agent logs stay local)")
    print("• Lightweight structure with Cosmos DB for search")

if __name__ == "__main__":
    main()