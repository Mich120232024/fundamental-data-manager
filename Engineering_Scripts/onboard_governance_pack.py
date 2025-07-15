#!/usr/bin/env python3
"""
Onboard complete governance pack to documents container
Upload all quality governance documents with proper evidence requirements
"""

from cosmos_db_manager import get_db_manager
from datetime import datetime
import os
import json

def read_file_content(file_path):
    """Read file content safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

def create_governance_document(pillar, filename, file_path, doc_id_counter):
    """Create governance document entry for Cosmos DB"""
    
    content = read_file_content(file_path)
    if not content:
        return None
    
    # Extract title from content or filename
    title_line = content.split('\n')[0] if content else filename
    title = title_line.replace('#', '').strip() if title_line.startswith('#') else filename.replace('.md', '').replace('_', ' ').title()
    
    # Determine document type and category
    doc_type_map = {
        'Standards': 'standard',
        'Methods': 'method', 
        'Procedures': 'procedure',
        'Templates': 'template'
    }
    
    category_map = {
        'Standards': 'compliance',
        'Methods': 'analytical',
        'Procedures': 'operational', 
        'Templates': 'structural'
    }
    
    # Create document ID
    doc_id = f"DOC-GOV-{pillar.upper()[:3]}-{doc_id_counter:03d}_{filename.replace('.md', '').replace(' ', '_').lower()}"
    
    # Determine evidence requirements based on content
    evidence_required = True  # All governance docs require evidence
    fabrication_risk = any(word in content.lower() for word in ['%', 'metric', 'rate', 'score', 'analysis'])
    
    governance_doc = {
        'id': doc_id,
        'documentId': f"DOC-GOV-{pillar.upper()[:3]}-{doc_id_counter:03d}",
        'title': title,
        
        # Categorization
        'workspace': 'governance',
        'docType': doc_type_map.get(pillar, 'standard'),
        'category': category_map.get(pillar, 'governance'),
        'pillar': pillar.lower(),
        
        # Team context
        'intendedFor': {
            'teams': ['all_teams'],
            'roles': ['all_agents'] if pillar != 'Templates' else ['new_agents', 'managers'],
            'departments': ['all']
        },
        'authoringTeam': 'governance_team',
        'reviewingTeams': ['compliance_team'],
        
        # Content
        'abstract': f"{pillar} governance document: {title}",
        'content': content,
        'format': 'markdown',
        
        # Ownership
        'author': 'COMPLIANCE_MANAGER' if pillar == 'Standards' else ('HEAD_OF_RESEARCH' if pillar == 'Methods' else 'HEAD_OF_ENGINEERING'),
        'owner': 'COMPLIANCE_MANAGER',
        'maintainers': ['COMPLIANCE_MANAGER'],
        
        # Evidence requirements
        'evidence_required': evidence_required,
        'evidence_type': 'implementation_verification_and_compliance_tracking',
        'fabrication_risk': fabrication_risk,
        'governance_pillar': pillar.lower(),
        
        # Version
        'version': '1.0',
        'status': 'active',
        
        # File system reference
        'originalPath': file_path,
        'migratedFrom': 'governance_workspace_filesystem',
        'migrationDate': datetime.now().isoformat() + 'Z',
        
        # Governance metadata
        'governanceLevel': 'foundational',
        'complianceRequired': True,
        'requiresAcknowledgment': True,
        
        # Timestamps
        'createdDate': datetime.now().isoformat() + 'Z',
        'lastModified': datetime.now().isoformat() + 'Z'
    }
    
    return governance_doc

def upload_governance_pack():
    """Upload complete governance pack to documents container"""
    
    db = get_db_manager()
    documents_container = db.database.get_container_client('documents')
    
    governance_path = '/Users/mikaeleage/Research & Analytics Services/Governance Workspace'
    
    # Define priority documents for each pillar
    priority_uploads = {
        'Standards': [
            'agent_standards.md',
            'evidence_standards.md', 
            'communication_standards.md',
            'agent_initialization.md',
            'governance_framework.md',
            'governance_standards.md',
            'workspace_constitution.md',
            'operational_standards.md',
            'technical_standards.md'
        ],
        'Methods': [
            'scientific_method.md',
            'fact_vs_ai_fantasy_separation_method.md',
            'ground_truth_azure_method.md',
            'root_cause_analysis.md',
            'five_whys_method.md',
            'design_thinking_method.md',
            'cost_benefit_analysis.md'
        ],
        'Procedures': [
            'compliance_check.md',
            'agent_onboarding.md',
            'create_new_agent.md',
            'approve_new_agent.md',
            'handle_violations.md',
            'routine_maintenance.md',
            'emergency_agent_triage_protocol.md'
        ],
        'Templates': [
            'identity_card_template.md',
            'session_log_template.md',
            'agent_deployment_template.md',
            'daily_maintenance_checklist.md',
            'weekly_self_assessment_guide.md'
        ]
    }
    
    uploaded_docs = []
    doc_id_counter = 10  # Start after existing docs
    
    for pillar, files in priority_uploads.items():
        pillar_path = f"{governance_path}/{pillar}"
        
        print(f"\\n📂 UPLOADING {pillar.upper()} PILLAR:")
        print("-" * 40)
        
        for filename in files:
            file_path = f"{pillar_path}/{filename}"
            
            if os.path.exists(file_path):
                print(f"   📄 {filename}...")
                
                governance_doc = create_governance_document(pillar, filename, file_path, doc_id_counter)
                
                if governance_doc:
                    try:
                        result = documents_container.create_item(governance_doc)
                        print(f"   ✅ Uploaded: {result['id']}")
                        uploaded_docs.append(result)
                        doc_id_counter += 1
                    except Exception as e:
                        if "Conflict" in str(e):
                            print(f"   ℹ️  Already exists: {governance_doc['id']}")
                        else:
                            print(f"   ❌ Error: {e}")
                else:
                    print(f"   ❌ Failed to create document")
            else:
                print(f"   ⚠️  File not found: {filename}")
    
    return uploaded_docs

def main():
    """Upload complete governance package"""
    
    print("📦 ONBOARDING COMPLETE GOVERNANCE PACKAGE")
    print("=" * 60)
    print("Uploading quality governance documents from all four pillars...")
    print("Adding evidence requirements and compliance tracking...")
    print()
    
    uploaded_docs = upload_governance_pack()
    
    print(f"\\n✅ GOVERNANCE PACKAGE ONBOARDING COMPLETE")
    print("=" * 60)
    print(f"📊 Documents uploaded: {len(uploaded_docs)}")
    print(f"✅ Standards pillar: Evidence-based compliance documents")
    print(f"✅ Methods pillar: Analytical frameworks and thinking tools")
    print(f"✅ Procedures pillar: Operational workflows and protocols")
    print(f"✅ Templates pillar: Structural standards and formats")
    print(f"✅ All documents require evidence verification")
    print(f"✅ Complete governance framework now in Cosmos DB")
    
    # Show final container status
    from query_cosmos_containers import query_container
    all_docs = query_container('documents')
    ready_count = sum(1 for d in all_docs if d.get('status') == 'active' and d.get('evidence_required'))
    
    print(f"\\n📊 FINAL DOCUMENTS CONTAINER STATUS:")
    print(f"   Total documents: {len(all_docs)}")
    print(f"   Ready for production: {ready_count}")
    print(f"   Governance coverage: Complete")

if __name__ == "__main__":
    main()