#!/usr/bin/env python3
"""
Create comprehensive documentation system in Cosmos DB
Replaces file-based documentation with searchable, categorized cloud storage
"""

from cosmos_db_manager import get_db_manager
from datetime import datetime
import json

def analyze_governance_structure():
    """Analyze current governance structure for categorization"""
    
    print("📊 ANALYZING GOVERNANCE STRUCTURE")
    print("="*50)
    
    # Current workspace structure
    workspaces = {
        'governance': {
            'name': 'Governance Workspace',
            'owner': 'COMPLIANCE_MANAGER',
            'pillars': ['Standards', 'Methods', 'Procedures'],
            'document_types': ['standards', 'methods', 'procedures', 'templates', 'audits', 'quick_start']
        },
        'engineering': {
            'name': 'Engineering Workspace',
            'owner': 'HEAD_OF_ENGINEERING',
            'document_types': ['technical_specs', 'scripts', 'procedures', 'architecture']
        },
        'research': {
            'name': 'Research Workspace',
            'owner': 'HEAD_OF_RESEARCH',
            'document_types': ['research_papers', 'analysis', 'external_sources', 'knowledge_base']
        },
        'business': {
            'name': 'Business Workspace',
            'owner': 'Business Owner',
            'document_types': ['roundtables', 'strategies', 'reports', 'meetings']
        },
        'executive': {
            'name': 'Executive Board',
            'owner': 'SAM',
            'document_types': ['directives', 'synthesis', 'architectural_plans', 'approvals']
        },
        'digital_labor': {
            'name': 'Digital Labor Workspace',
            'owner': 'HEAD_OF_DIGITAL_STAFF',
            'document_types': ['agent_definitions', 'rosters', 'performance_reviews']
        }
    }
    
    # Document categories identified
    categories = {
        'governance': ['standards', 'methods', 'procedures', 'templates', 'policies'],
        'technical': ['architecture', 'specifications', 'code', 'scripts', 'configurations'],
        'operational': ['processes', 'workflows', 'sops', 'checklists', 'guides'],
        'strategic': ['plans', 'roadmaps', 'analysis', 'reports', 'proposals'],
        'administrative': ['meetings', 'memos', 'directives', 'approvals', 'reviews'],
        'knowledge': ['research', 'tutorials', 'best_practices', 'references', 'external_docs']
    }
    
    return workspaces, categories

def create_processes_container():
    """Create processes container for all procedural documentation"""
    
    print("\n🔨 Creating Processes Container...")
    
    db = get_db_manager()
    
    try:
        database = db.client.get_database_client(db.database_name)
        
        # Create processes container with department-based partitioning
        container = database.create_container(
            id='processes',
            partition_key={'paths': ['/department'], 'kind': 'Hash'},
            indexing_policy={
                'automatic': True,
                'indexingMode': 'consistent',
                'includedPaths': [{'path': '/*'}],
                'compositeIndexes': [
                    [
                        {'path': '/department', 'order': 'ascending'},
                        {'path': '/category', 'order': 'ascending'},
                        {'path': '/lastModified', 'order': 'descending'}
                    ]
                ]
            }
        )
        
        print("✅ Processes container created!")
        return container
        
    except Exception as e:
        if "Resource with specified id already exists" in str(e):
            print("ℹ️ Processes container already exists")
            return database.get_container_client('processes')
        else:
            raise e

def create_documents_container():
    """Create universal documents container for all documentation"""
    
    print("\n🔨 Creating Documents Container...")
    
    db = get_db_manager()
    
    try:
        database = db.client.get_database_client(db.database_name)
        
        # Create documents container with flexible schema
        container = database.create_container(
            id='documents',
            partition_key={'paths': ['/workspace'], 'kind': 'Hash'},
            indexing_policy={
                'automatic': True,
                'indexingMode': 'consistent',
                'includedPaths': [{'path': '/*'}],
                'compositeIndexes': [
                    [
                        {'path': '/workspace', 'order': 'ascending'},
                        {'path': '/docType', 'order': 'ascending'},
                        {'path': '/version', 'order': 'descending'}
                    ]
                ]
            }
        )
        
        print("✅ Documents container created!")
        return container
        
    except Exception as e:
        if "Resource with specified id already exists" in str(e):
            print("ℹ️ Documents container already exists")
            return database.get_container_client('documents')
        else:
            raise e

def design_process_schema():
    """Design schema for process documentation"""
    
    process_schema = {
        'id': 'unique_process_id',
        'department': 'governance|engineering|research|business|executive|digital_labor',
        'processName': 'Human-readable process name',
        'processId': 'PROC-GOV-001',  # Structured ID
        'category': 'operational|compliance|technical|administrative',
        'subcategory': 'initialization|communication|review|deployment',
        
        # Content
        'title': 'Process title',
        'purpose': 'Why this process exists',
        'scope': 'Who/what this applies to',
        'content': 'Full process documentation in markdown',
        
        # Metadata
        'version': '1.0',
        'status': 'draft|active|deprecated|archived',
        'effectiveDate': '2025-06-16',
        'reviewDate': '2025-07-16',
        
        # Ownership
        'owner': 'AGENT_NAME or ROLE',
        'approvedBy': 'Authority who approved',
        'maintainer': 'Who maintains this',
        
        # Relationships
        'replaces': 'previous_process_id',
        'relatedProcesses': ['PROC-001', 'PROC-002'],
        'requiredTemplates': ['template_ids'],
        'referencedStandards': ['standard_ids'],
        
        # Compliance
        'complianceRequired': True,
        'auditFrequency': 'monthly|quarterly|annual',
        'lastAudit': '2025-06-16',
        'complianceScore': 0.95,
        
        # Search optimization
        'tags': ['onboarding', 'mandatory', 'security'],
        'keywords': ['initialization', 'agent', 'protocol'],
        'searchText': 'Combined searchable content',
        
        # Tracking
        'createdBy': 'AGENT_NAME',
        'createdDate': '2025-06-16',
        'lastModifiedBy': 'AGENT_NAME',
        'lastModified': '2025-06-16T10:00:00Z',
        'accessCount': 0,
        'lastAccessed': '2025-06-16T10:00:00Z'
    }
    
    return process_schema

def design_document_schema():
    """Design universal schema for all documentation"""
    
    document_schema = {
        'id': 'unique_document_id',
        'workspace': 'governance|engineering|research|business|executive|digital_labor',
        
        # Document classification
        'docType': 'standard|method|procedure|template|report|guide|policy|spec',
        'pillar': 'standards|methods|processes',  # For governance docs
        'category': 'technical|operational|strategic|administrative|knowledge',
        'subcategory': 'specific_subcategory',
        
        # Content
        'title': 'Document title',
        'abstract': 'Brief summary for search results',
        'content': 'Full document content in markdown',
        'format': 'markdown|json|yaml|python',
        
        # Versioning
        'version': '1.0',
        'versionHistory': [
            {
                'version': '0.9',
                'date': '2025-06-15',
                'changedBy': 'AGENT_NAME',
                'changes': 'Initial draft'
            }
        ],
        
        # Metadata
        'status': 'draft|review|approved|active|deprecated|archived',
        'confidentiality': 'public|internal|confidential|restricted',
        'language': 'en',
        
        # Ownership and approval
        'author': 'Original author',
        'owner': 'Current owner/maintainer',
        'approvers': ['SAM', 'COMPLIANCE_MANAGER'],
        'stakeholders': ['interested_agents'],
        
        # Relationships
        'parentDoc': 'parent_doc_id',
        'childDocs': ['child_doc_ids'],
        'references': ['referenced_doc_ids'],
        'supersedes': 'old_doc_id',
        'supersededBy': 'new_doc_id',
        
        # File system mapping (for migration)
        'originalPath': '/Governance Workspace/Standards/example.md',
        'migratedFrom': 'file_system',
        'migrationDate': '2025-06-16',
        
        # Search and discovery
        'tags': ['governance', 'mandatory', 'initialization'],
        'keywords': ['extracted', 'keywords', 'for', 'search'],
        'searchableContent': 'Full text for search indexing',
        
        # Usage tracking
        'viewCount': 0,
        'lastViewed': '2025-06-16T10:00:00Z',
        'downloadCount': 0,
        'citedBy': ['document_ids_that_reference_this'],
        
        # Compliance and audit
        'requiresCompliance': True,
        'complianceChecks': [
            {
                'date': '2025-06-16',
                'agent': 'COMPLIANCE_MANAGER',
                'result': 'passed',
                'notes': 'Meets all standards'
            }
        ],
        
        # Timestamps
        'createdDate': '2025-06-16T10:00:00Z',
        'lastModified': '2025-06-16T10:00:00Z',
        'expiryDate': '2026-06-16',  # For time-limited docs
        'nextReviewDate': '2025-09-16'
    }
    
    return document_schema

def create_sample_process_entry():
    """Create sample process documentation entry"""
    
    db = get_db_manager()
    processes_container = db.database.get_container_client('processes')
    
    sample_process = {
        'id': 'PROC-GOV-001_agent_initialization',
        'department': 'governance',
        'processName': '8-Step Agent Initialization Protocol',
        'processId': 'PROC-GOV-001',
        'category': 'operational',
        'subcategory': 'initialization',
        
        'title': 'Mandatory 8-Step Agent Initialization Protocol',
        'purpose': 'Ensure all agents properly initialize with governance compliance',
        'scope': 'All agents in Research & Analytics Services workspace',
        'content': '''
# 8-Step Agent Initialization Protocol

## Overview
This protocol ensures proper agent initialization and governance compliance.

## Steps
1. Environment verification (`pwd` check)
2. Read last 20 lines of `/Inbox/ledger.md`
3. Locate your identity prompt
4. Verify 8-file agent package exists
5. Read your last session log AND CREATE TODAY'S SESSION LOG
6. Update your todo list
7. Send initialization heartbeat
8. Understand three-pillar governance

## Compliance
Violation = Immediate protocol violation report to COMPLIANCE_MANAGER
        ''',
        
        'version': '2.0',
        'status': 'active',
        'effectiveDate': '2025-06-15',
        'reviewDate': '2025-07-15',
        
        'owner': 'COMPLIANCE_MANAGER',
        'approvedBy': 'SAM',
        'maintainer': 'COMPLIANCE_MANAGER',
        
        'relatedProcesses': ['PROC-GOV-002_session_logging'],
        'requiredTemplates': ['identity_card_template', 'session_log_template'],
        'referencedStandards': ['agent_standards', 'evidence_standards'],
        
        'complianceRequired': True,
        'auditFrequency': 'weekly',
        'lastAudit': '2025-06-16',
        'complianceScore': 0.70,
        
        'tags': ['initialization', 'mandatory', 'governance', 'agent-startup'],
        'keywords': ['8-step', 'protocol', 'initialization', 'compliance'],
        
        'createdBy': 'COMPLIANCE_MANAGER',
        'createdDate': '2025-06-01',
        'lastModifiedBy': 'COMPLIANCE_MANAGER',
        'lastModified': datetime.now().isoformat() + 'Z',
        'accessCount': 145,
        'lastAccessed': datetime.now().isoformat() + 'Z'
    }
    
    try:
        result = processes_container.create_item(sample_process)
        print("✅ Sample process created:", sample_process['processName'])
        return result
    except Exception as e:
        if "Conflict" in str(e):
            print("ℹ️ Sample process already exists")
        else:
            print(f"❌ Error: {e}")

def create_taxonomy_documentation():
    """Document the categorization taxonomy in metadata"""
    
    db = get_db_manager()
    metadata_container = db.database.get_container_client('metadata')
    
    taxonomy_doc = {
        'id': 'documentation_taxonomy',
        'metaType': 'taxonomy_guide',
        'title': 'Documentation Categorization System',
        'description': 'Complete taxonomy for organizing all documentation in Cosmos DB',
        
        'workspaces': {
            'governance': {
                'owner': 'COMPLIANCE_MANAGER',
                'pillars': ['standards', 'methods', 'processes'],
                'focus': 'Rules, compliance, and operational procedures'
            },
            'engineering': {
                'owner': 'HEAD_OF_ENGINEERING',
                'focus': 'Technical specifications, architecture, and code'
            },
            'research': {
                'owner': 'HEAD_OF_RESEARCH',
                'focus': 'Analysis, findings, and knowledge management'
            },
            'business': {
                'owner': 'Business Owner',
                'focus': 'Strategy, meetings, and business operations'
            },
            'executive': {
                'owner': 'SAM',
                'focus': 'High-level directives and architectural decisions'
            },
            'digital_labor': {
                'owner': 'HEAD_OF_DIGITAL_STAFF',
                'focus': 'Agent management and performance'
            }
        },
        
        'documentTypes': {
            'standard': 'Rules and requirements that must be followed',
            'method': 'Approaches and frameworks for problem-solving',
            'procedure': 'Step-by-step instructions for specific tasks',
            'template': 'Reusable formats for common documents',
            'report': 'Analysis results and findings',
            'guide': 'Educational and reference materials',
            'policy': 'High-level organizational rules',
            'specification': 'Technical requirements and designs'
        },
        
        'categories': {
            'technical': 'Technology, architecture, and implementation',
            'operational': 'Day-to-day processes and workflows',
            'strategic': 'Planning, analysis, and decision-making',
            'administrative': 'Management, meetings, and coordination',
            'knowledge': 'Research, learning, and best practices'
        },
        
        'statusValues': {
            'draft': 'Work in progress',
            'review': 'Under review for approval',
            'approved': 'Approved but not yet active',
            'active': 'Current official version',
            'deprecated': 'Outdated but kept for reference',
            'archived': 'Historical record only'
        },
        
        'examples': {
            'process_id': 'PROC-GOV-001 = Process, Governance workspace, number 001',
            'doc_id': 'DOC-ENG-SPEC-042 = Document, Engineering, Specification, number 042',
            'workspace_partition': 'Documents partitioned by workspace for efficient queries',
            'department_partition': 'Processes partitioned by department for access control'
        }
    }
    
    try:
        metadata_container.create_item(taxonomy_doc)
        print("✅ Taxonomy documentation created")
    except Exception as e:
        if "Conflict" in str(e):
            print("ℹ️ Taxonomy already documented")

def design_migration_strategy():
    """Strategy for migrating file-based docs to Cosmos DB"""
    
    print("\n📋 MIGRATION STRATEGY")
    print("="*50)
    
    strategy = {
        'phases': [
            {
                'phase': 1,
                'name': 'Core Governance Documents',
                'targets': [
                    '/Governance Workspace/Standards/*',
                    '/Governance Workspace/Methods/*',
                    '/Governance Workspace/Procedures/*'
                ],
                'priority': 'HIGH',
                'timeline': '1 week'
            },
            {
                'phase': 2,
                'name': 'Active Operational Documents',
                'targets': [
                    'All workspace README files',
                    'Active templates',
                    'Current procedures'
                ],
                'priority': 'MEDIUM',
                'timeline': '2 weeks'
            },
            {
                'phase': 3,
                'name': 'Historical and Archive',
                'targets': [
                    'Archive folders',
                    'Historical reports',
                    'Legacy documentation'
                ],
                'priority': 'LOW',
                'timeline': '1 month'
            }
        ],
        
        'benefits': [
            'Single source of truth - no more file hunting',
            'Version control built-in',
            'Full-text search across all documentation',
            'Access control by workspace/department',
            'Usage analytics - know what docs are actually used',
            'Relationships tracked - see doc dependencies',
            'No local file maintenance needed',
            'External agent access ready'
        ],
        
        'implementation': [
            '1. Create migration script to parse markdown files',
            '2. Extract metadata from file paths and content',
            '3. Preserve original paths for reference',
            '4. Maintain version history during migration',
            '5. Verify all content migrated correctly',
            '6. Update agent procedures to use database',
            '7. Deprecate file-based documentation gradually'
        ]
    }
    
    return strategy

def main():
    """Set up comprehensive documentation system"""
    
    print("🏗️ COMPREHENSIVE DOCUMENTATION SYSTEM SETUP")
    print("="*60)
    
    # Analyze current structure
    workspaces, categories = analyze_governance_structure()
    
    # Create containers
    processes_container = create_processes_container()
    documents_container = create_documents_container()
    
    # Document schemas
    process_schema = design_process_schema()
    document_schema = design_document_schema()
    
    print("\n📐 SCHEMA DESIGN COMPLETE")
    print("-"*40)
    print("✅ Processes Container: Department-based partitioning")
    print("✅ Documents Container: Workspace-based partitioning")
    print("✅ Flexible schemas support all document types")
    
    # Create sample and documentation
    create_sample_process_entry()
    create_taxonomy_documentation()
    
    # Show migration strategy
    strategy = design_migration_strategy()
    
    print("\n🎯 RECOMMENDED APPROACH")
    print("-"*40)
    print("1. Start with 'processes' container for all procedures")
    print("2. Use 'documents' container for everything else")
    print("3. Maintain taxonomy in metadata for consistency")
    print("4. Migrate in phases - core governance first")
    print("5. Agents query database instead of file system")
    
    print("\n✅ BENEFITS FOR AGENTS")
    print("-"*40)
    for benefit in strategy['benefits']:
        print(f"   • {benefit}")
    
    print("\n🚀 NEXT STEPS")
    print("-"*40)
    print("1. Review and approve container schemas")
    print("2. Create migration scripts for each workspace")
    print("3. Test with pilot documents")
    print("4. Train agents on document queries")
    print("5. Phase out file-based documentation")
    
    print("\n✨ Vision: All documentation searchable, versioned, and")
    print("   accessible through simple queries - no more file hunting!")

if __name__ == "__main__":
    main()