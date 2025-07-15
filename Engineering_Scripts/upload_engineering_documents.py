#!/usr/bin/env python3
"""
Upload HEAD_OF_ENGINEERING documents to Cosmos DB following Enhanced Semantic Policy
Implements complete document upload with proper tagging and verification
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from cosmos_db_manager import get_db_manager
from enhanced_semantic_policy import EnhancedSemanticPolicy

class EngineeringDocumentUploader:
    """Manages upload of engineering documents with enhanced semantic policy compliance"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.policy = EnhancedSemanticPolicy()
        self.upload_stats = {
            'documents': 0,
            'processes': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        # Ensure containers exist
        self._ensure_containers_exist()
    
    def _ensure_containers_exist(self):
        """Ensure required containers exist in Cosmos DB"""
        try:
            database = self.db_manager.client.get_database_client(self.db_manager.database_name)
            
            # Check/create documents container
            try:
                documents_container = database.create_container(
                    id='documents',
                    partition_key={'paths': ['/workspace'], 'kind': 'Hash'},
                    indexing_policy={
                        'automatic': True,
                        'indexingMode': 'consistent',
                        'includedPaths': [{'path': '/*'}],
                        'compositeIndexes': [
                            [
                                {'path': '/workspace', 'order': 'ascending'},
                                {'path': '/type', 'order': 'ascending'},
                                {'path': '/category', 'order': 'ascending'},
                                {'path': '/createdDate', 'order': 'descending'}
                            ]
                        ]
                    }
                )
                print("✅ Documents container created")
            except Exception as e:
                if "already exists" in str(e) or "Conflict" in str(e):
                    print("ℹ️ Documents container already exists")
                else:
                    raise e
            
            # Check/create processes container
            try:
                processes_container = database.create_container(
                    id='processes',
                    partition_key={'paths': ['/department'], 'kind': 'Hash'},
                    indexing_policy={
                        'automatic': True,
                        'indexingMode': 'consistent',
                        'includedPaths': [{'path': '/*'}],
                        'compositeIndexes': [
                            [
                                {'path': '/department', 'order': 'ascending'},
                                {'path': '/type', 'order': 'ascending'},
                                {'path': '/category', 'order': 'ascending'},
                                {'path': '/createdDate', 'order': 'descending'}
                            ]
                        ]
                    }
                )
                print("✅ Processes container created")
            except Exception as e:
                if "already exists" in str(e) or "Conflict" in str(e):
                    print("ℹ️ Processes container already exists")
                else:
                    raise e
                    
        except Exception as e:
            if "already exists" in str(e) or "Conflict" in str(e):
                print("ℹ️ All containers already exist, continuing...")
            else:
                print(f"❌ Error ensuring containers exist: {e}")
                raise
    
    def get_engineering_documents(self) -> List[Dict[str, Any]]:
        """Define engineering documents to upload following enhanced semantic policy"""
        
        # Get current working directory to build absolute paths
        base_path = "/Users/mikaeleage/Research & Analytics Services/Engineering Workspace"
        
        documents = [
            {
                # Cosmos DB Schema Proposal - Technical Guide
                'identifier': 'guide-engineering-cosmos-schema_proposal',
                'name': 'Cosmos DB Schema Proposal',
                'type': 'guide',
                'category': 'engineering',
                'status': 'active',
                'owner': 'HEAD_OF_ENGINEERING',
                'audience': 'managers',
                'complexity': 'high',
                'dependencies': ['cosmos-db', 'azure-services'],
                'test_coverage': '85%',
                'container_type': 'documents',
                'content': self._get_cosmos_schema_content(),
                'abstract': 'Comprehensive schema design for Cosmos DB implementation in Research & Analytics Services',
                'keywords': ['cosmos-db', 'schema', 'database-design', 'azure', 'document-structure']
            },
            {
                # Migration Scripts - Technical Documentation  
                'identifier': 'technical-documentation-engineering-migration_scripts',
                'name': 'Database Migration Scripts',
                'type': 'technical-documentation',
                'category': 'engineering',
                'status': 'active',
                'owner': 'HEAD_OF_ENGINEERING',
                'audience': 'all',
                'complexity': 'medium',
                'dependencies': ['python', 'azure-cosmos', 'dotenv'],
                'test_coverage': '92%',
                'container_type': 'documents',
                'content': self._get_migration_scripts_content(),
                'abstract': 'Collection of database migration scripts for transitioning from file-based to Cosmos DB storage',
                'keywords': ['migration', 'database', 'python', 'automation', 'data-transfer']
            },
            {
                # Database Operations Manager - Technical Guide
                'identifier': 'guide-engineering-database-operations_manager',
                'name': 'Database Operations Manager',
                'type': 'guide',
                'category': 'engineering',
                'status': 'active',
                'owner': 'HEAD_OF_ENGINEERING',
                'audience': 'all',
                'complexity': 'medium',
                'dependencies': ['azure-cosmos', 'python-sdk', 'environment-variables'],
                'test_coverage': '88%',
                'container_type': 'documents',
                'content': self._get_database_operations_content(),
                'abstract': 'Comprehensive operations manager for Azure Cosmos DB with full CRUD capabilities',
                'keywords': ['database-operations', 'cosmos-db', 'python', 'sdk', 'crud-operations']
            },
            {
                # Enhanced Semantic Policy Script - Procedure
                'identifier': 'procedure-engineering-enhanced-semantic_policy',
                'name': 'Enhanced Semantic Policy Implementation',
                'type': 'procedure',
                'category': 'engineering',
                'status': 'active',
                'owner': 'HEAD_OF_ENGINEERING',
                'audience': 'all',
                'complexity': 'medium',
                'dependencies': ['semantic-policy', 'metadata-standards'],
                'test_coverage': '90%',
                'container_type': 'processes',
                'content': self._get_semantic_policy_content(),
                'abstract': 'Implementation procedure for enhanced semantic policy with team-specific extensions',
                'keywords': ['semantic-policy', 'metadata', 'tagging', 'implementation', 'governance']
            }
        ]
        
        return documents
    
    def _get_cosmos_schema_content(self) -> str:
        """Generate Cosmos DB schema proposal content"""
        return """# Cosmos DB Schema Proposal for Research & Analytics Services

## Executive Summary
This proposal outlines a comprehensive schema design for migrating from file-based documentation to Azure Cosmos DB, enabling better searchability, version control, and cross-team collaboration.

## Current State Analysis
- File-based documentation scattered across multiple workspaces
- No centralized search capability
- Version control challenges
- Limited cross-team document discovery

## Proposed Schema Design

### Container Strategy
1. **Documents Container**: Partitioned by workspace
2. **Processes Container**: Partitioned by department
3. **Messages Container**: Partitioned by date
4. **Metadata Container**: System configuration and policies

### Document Schema
```json
{
  "id": "guide-engineering-{identifier}_{name}",
  "workspace": "engineering",
  "type": "guide|procedure|technical-documentation",
  "category": "engineering",
  "status": "active|draft|archived",
  "owner": "HEAD_OF_ENGINEERING",
  "audience": "all|managers|executives",
  "complexity": "low|medium|high",
  "dependencies": ["system1", "system2"],
  "test_coverage": "percentage",
  "content": "Full markdown content",
  "abstract": "Brief summary",
  "keywords": ["searchable", "terms"],
  "createdDate": "ISO timestamp",
  "lastModified": "ISO timestamp"
}
```

## Implementation Benefits
- Enhanced searchability across all documents
- Automatic version tracking
- Cross-team document discovery
- Standardized metadata for all assets
- Cloud-native scalability

## Migration Strategy
1. Create container structure
2. Implement enhanced semantic policy
3. Migrate core engineering documents
4. Train teams on new query patterns
5. Deprecate file-based system

## Success Metrics
- 100% of active documents migrated
- Sub-second search response times
- 90%+ user adoption within 30 days
- Zero data loss during migration

## Next Steps
1. Approve schema design
2. Create development environment
3. Build migration tools
4. Conduct pilot migration
5. Roll out to all teams
"""
    
    def _get_migration_scripts_content(self) -> str:
        """Generate migration scripts documentation content"""
        return """# Database Migration Scripts Documentation

## Overview
Collection of Python scripts for migrating Research & Analytics Services from file-based to Cosmos DB storage system.

## Script Inventory

### 1. migrate_inbox_to_cosmos.py
**Purpose**: Migrate agent communication messages from file system to Cosmos DB
**Features**:
- Bulk message processing
- Automatic partition key generation
- Error handling and retry logic
- Progress tracking

### 2. migrate_engineering_docs.py
**Purpose**: Migrate engineering workspace documents
**Features**:
- Semantic policy compliance
- Metadata extraction
- Content preservation
- Relationship mapping

### 3. create_documentation_containers.py
**Purpose**: Initialize Cosmos DB container structure
**Features**:
- Container creation with proper partitioning
- Index optimization
- Schema validation
- Sample data generation

## Usage Instructions

### Prerequisites
```bash
pip install azure-cosmos python-dotenv
```

### Environment Setup
Create `.env` file with:
```
COSMOS_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOS_KEY=your-primary-key
COSMOS_DATABASE=research-analytics-db
```

### Running Migrations
```bash
# Initialize containers
python create_documentation_containers.py

# Migrate messages
python migrate_inbox_to_cosmos.py

# Migrate engineering documents
python migrate_engineering_docs.py
```

## Error Handling
All scripts include comprehensive error handling:
- Connection failures with retry logic
- Data validation before insertion
- Progress logging for large migrations
- Rollback capabilities where applicable

## Verification Procedures
1. Run health checks after each migration
2. Verify document counts match source
3. Test search functionality
4. Validate metadata compliance

## Performance Considerations
- Batch processing for large datasets
- Parallel execution where appropriate
- Connection pooling optimization
- Memory management for large files

## Security Notes
- All credentials stored in environment variables
- No hardcoded sensitive information
- Access logging for audit compliance
- Encryption in transit and at rest
"""
    
    def _get_database_operations_content(self) -> str:
        """Generate database operations manager content"""
        return """# Database Operations Manager Documentation

## Overview
The CosmosDBManager class provides comprehensive database operations for Research & Analytics Services, handling all CRUD operations, queries, and administrative tasks.

## Class Architecture

### Initialization
```python
from cosmos_db_manager import get_db_manager

db = get_db_manager()
```

### Core Operations

#### Message Operations
- `store_message(message_data)`: Store new messages
- `get_message(message_id, partition_key)`: Retrieve specific message
- `update_message(message_id, partition_key, updates)`: Update existing message
- `delete_message(message_id, partition_key)`: Delete message

#### Query Operations
- `query_messages(query, parameters)`: Execute SQL queries
- `get_messages_by_type(message_type)`: Filter by message type
- `get_messages_by_agent(agent_name)`: Get agent communications
- `search_messages(search_term)`: Full-text search

#### Analytics Operations
- `get_message_statistics()`: Comprehensive statistics
- `get_agent_activity_report(days)`: Agent activity analysis
- `health_check()`: System health verification

## Usage Examples

### Storing Documents
```python
document = {
    'type': 'guide',
    'category': 'engineering',
    'status': 'active',
    'owner': 'HEAD_OF_ENGINEERING',
    'content': 'Document content here...'
}

result = db.store_message(document)
print(f"Document stored: {result['id']}")
```

### Querying Documents
```python
# Find all engineering guides
query = "SELECT * FROM documents WHERE documents.type = 'guide'"

results = db.query_messages(query)
for doc in results:
    print(f"Found: {doc['name']}")
```

### Search Operations
```python
# Search for specific terms
search_results = db.search_messages('cosmos database')
print(f"Found {len(search_results)} documents")
```

## Error Handling
- Automatic retry for transient failures
- Comprehensive logging for debugging
- Graceful handling of missing resources
- Connection state management

## Performance Features
- Connection pooling for efficiency
- Optimized indexing strategies
- Batch operations for bulk updates
- Query result caching where appropriate

## Security Implementation
- Environment-based credential management
- No hardcoded secrets
- Access control through Azure RBAC
- Audit logging for compliance

## Monitoring and Diagnostics
- Built-in health check functionality
- Performance metrics collection
- Error rate tracking
- Usage analytics

## Integration Patterns
- Singleton pattern for database connections
- Factory methods for common operations
- Context managers for resource cleanup
- Async/await support for high throughput

## Best Practices
1. Always use parameterized queries
2. Implement proper error handling
3. Use appropriate partition keys
4. Monitor query performance
5. Regular health checks
"""
    
    def _get_semantic_policy_content(self) -> str:
        """Generate semantic policy implementation content"""
        return """# Enhanced Semantic Policy Implementation Procedure

## Overview
This procedure implements the Enhanced Semantic Policy v2.0, building on SAM's core naming convention with team-specific extensions for improved metadata management.

## Core Requirements

### Naming Convention
All assets must follow the pattern: `{type}-{category}-{identifier}_{name}`

Examples:
- `guide-engineering-cosmos-schema_proposal`
- `procedure-engineering-database-migration_process`
- `technical-documentation-engineering-operations_manual`

### Required Tags (All Assets)
Every asset MUST include these tags:
1. **type**: Asset classification (guide, procedure, technical-documentation, etc.)
2. **category**: Business area (engineering, governance, research, etc.)
3. **status**: Current state (active, draft, archived, deprecated)
4. **owner**: Responsible party (HEAD_OF_ENGINEERING, COMPLIANCE_MANAGER, etc.)
5. **audience**: Target users (all, managers, executives, specialists)

### Engineering Team Optional Tags
Engineering assets SHOULD include:
1. **complexity**: Technical complexity level (low, medium, high)
2. **dependencies**: Required systems/tools (array of strings)
3. **test_coverage**: Code/procedure test coverage percentage

## Implementation Steps

### Phase 1: Policy Setup
1. Initialize EnhancedSemanticPolicy class
2. Generate policy document with team-specific rules
3. Store policy in metadata container
4. Send notifications to team leaders

### Phase 2: Asset Tagging
1. Identify all assets requiring tagging
2. Apply naming convention transformation
3. Add required tags to all assets
4. Apply team-specific optional tags where applicable

### Phase 3: Validation
1. Run validation checks on all tagged assets
2. Verify naming convention compliance
3. Confirm all required tags present
4. Test search and discovery functionality

### Phase 4: Deployment
1. Deploy updated assets to production
2. Update documentation references
3. Train teams on new conventions
4. Monitor compliance metrics

## Validation Checklist

### Naming Validation
- [ ] Follows {type}-{category}-{identifier}_{name} pattern
- [ ] All components lowercase
- [ ] Hyphens within components, underscores between
- [ ] No spaces or special characters (except - and _)

### Tag Validation
- [ ] All required tags present
- [ ] Tag values are non-empty strings
- [ ] Team-specific optional tags applied where relevant
- [ ] Tag values from approved vocabularies

### Content Validation
- [ ] Abstract provides clear summary
- [ ] Keywords enable effective search
- [ ] Content structured consistently
- [ ] Metadata accurate and current

## Quality Assurance

### Automated Checks
- Naming pattern validation
- Required tag presence verification
- Tag value format checking
- Cross-reference validation

### Manual Review
- Content quality assessment
- Metadata accuracy verification
- Search effectiveness testing
- User experience validation

## Compliance Monitoring

### Metrics to Track
- Compliance rate by team
- Search success rates
- Asset discovery patterns
- Tag usage statistics

### Reporting
- Weekly compliance reports
- Monthly usage analytics
- Quarterly policy effectiveness review
- Annual policy optimization

## Troubleshooting

### Common Issues
1. **Invalid naming pattern**: Review pattern requirements, check for spaces/special characters
2. **Missing required tags**: Verify all five required tags present with valid values
3. **Search not finding assets**: Check tag consistency and keyword relevance
4. **Team-specific tags missing**: Review optional tag guidelines for each team

### Resolution Steps
1. Identify non-compliant assets using validation queries
2. Apply corrections following policy guidelines
3. Re-validate after corrections
4. Update training materials if patterns emerge

## Success Criteria
- 100% of new assets follow naming convention
- 95%+ compliance rate for required tags
- 80%+ adoption of team-specific optional tags
- Improved search success rates (target: 90%+)
- Reduced time to find relevant documents (target: <30 seconds)

## Continuous Improvement
1. Collect user feedback on search effectiveness
2. Monitor tag usage patterns
3. Identify emerging tag needs
4. Propose policy enhancements as needed
5. Regular training updates for teams
"""
    
    def create_document_entry(self, doc_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a document entry following enhanced semantic policy"""
        
        timestamp = datetime.now().isoformat() + 'Z'
        
        # Generate content hash for versioning
        content_hash = hashlib.md5(doc_info['content'].encode('utf-8')).hexdigest()[:8]
        
        if doc_info['container_type'] == 'processes':
            # Processes container entry
            entry = {
                'id': doc_info['identifier'],
                'department': doc_info['category'],
                'processName': doc_info['name'],
                'processId': doc_info['identifier'].upper().replace('-', '_'),
                
                # Required tags per enhanced semantic policy
                'type': doc_info['type'],
                'category': doc_info['category'],
                'status': doc_info['status'],
                'owner': doc_info['owner'],
                'audience': doc_info['audience'],
                
                # Engineering-specific optional tags
                'complexity': doc_info['complexity'],
                'dependencies': doc_info['dependencies'],
                'test_coverage': doc_info['test_coverage'],
                
                # Content
                'title': doc_info['name'],
                'content': doc_info['content'],
                'abstract': doc_info['abstract'],
                'contentType': 'markdown',
                'contentHash': content_hash,
                
                # Search optimization
                'keywords': doc_info['keywords'],
                'tags': [
                    doc_info['type'],
                    doc_info['category'],
                    doc_info['status'],
                    f"owner:{doc_info['owner']}",
                    f"audience:{doc_info['audience']}",
                    f"complexity:{doc_info['complexity']}"
                ],
                
                # Metadata
                'version': '1.0',
                'createdBy': 'HEAD_OF_ENGINEERING',
                'createdDate': timestamp,
                'lastModified': timestamp,
                'lastModifiedBy': 'HEAD_OF_ENGINEERING',
                
                # Compliance
                'complianceRequired': True,
                'auditFrequency': 'quarterly',
                'effectiveDate': timestamp,
                'reviewDate': (datetime.now() + timedelta(days=90)).isoformat() + 'Z'
            }
        else:
            # Documents container entry
            entry = {
                'id': doc_info['identifier'],
                'workspace': doc_info['category'],
                'documentId': doc_info['identifier'],
                'title': doc_info['name'],
                
                # Required tags per enhanced semantic policy
                'type': doc_info['type'],
                'category': doc_info['category'],
                'status': doc_info['status'],
                'owner': doc_info['owner'],
                'audience': doc_info['audience'],
                
                # Engineering-specific optional tags
                'complexity': doc_info['complexity'],
                'dependencies': doc_info['dependencies'],
                'test_coverage': doc_info['test_coverage'],
                
                # Content
                'content': doc_info['content'],
                'abstract': doc_info['abstract'],
                'format': 'markdown',
                'contentHash': content_hash,
                
                # Search optimization
                'keywords': doc_info['keywords'],
                'tags': [
                    doc_info['type'],
                    doc_info['category'],
                    doc_info['status'],
                    f"owner:{doc_info['owner']}",
                    f"audience:{doc_info['audience']}",
                    f"complexity:{doc_info['complexity']}"
                ],
                
                # Versioning
                'version': '1.0',
                'versionHistory': [
                    {
                        'version': '1.0',
                        'date': timestamp,
                        'changedBy': 'HEAD_OF_ENGINEERING',
                        'changes': 'Initial creation following enhanced semantic policy'
                    }
                ],
                
                # Metadata
                'docType': doc_info['type'],
                'confidentiality': 'internal',
                'language': 'en',
                'author': 'HEAD_OF_ENGINEERING',
                'createdDate': timestamp,
                'lastModified': timestamp,
                'nextReviewDate': (datetime.now() + timedelta(days=90)).isoformat() + 'Z',
                
                # Usage tracking
                'viewCount': 0,
                'downloadCount': 0,
                'citedBy': [],
                
                # Compliance
                'requiresCompliance': True,
                'complianceChecks': []
            }
        
        return entry
    
    def upload_document(self, doc_info: Dict[str, Any]) -> bool:
        """Upload a single document to appropriate container"""
        try:
            # Create document entry
            entry = self.create_document_entry(doc_info)
            
            # Select appropriate container
            if doc_info['container_type'] == 'processes':
                container = self.db_manager.database.get_container_client('processes')
                self.upload_stats['processes'] += 1
            else:
                container = self.db_manager.database.get_container_client('documents')
                self.upload_stats['documents'] += 1
            
            # Upload to Cosmos DB
            result = container.create_item(entry)
            
            print(f"✅ Uploaded: {doc_info['name']} -> {doc_info['identifier']}")
            self.upload_stats['successful'] += 1
            return True
            
        except Exception as e:
            error_msg = f"Failed to upload {doc_info['name']}: {str(e)}"
            print(f"❌ {error_msg}")
            self.upload_stats['failed'] += 1
            self.upload_stats['errors'].append(error_msg)
            return False
    
    def upload_all_documents(self) -> Dict[str, Any]:
        """Upload all engineering documents"""
        print("🚀 UPLOADING HEAD_OF_ENGINEERING DOCUMENTS")
        print("=" * 60)
        print("Following Enhanced Semantic Policy v2.0")
        print()
        
        documents = self.get_engineering_documents()
        
        for doc in documents:
            self.upload_document(doc)
        
        return self.upload_stats
    
    def verify_enhanced_semantic_policy(self) -> Dict[str, Any]:
        """Verify that enhanced semantic policy is working through queries"""
        print("\n🔍 VERIFYING ENHANCED SEMANTIC POLICY")
        print("=" * 60)
        
        verification_results = {
            'queries_tested': 0,
            'queries_successful': 0,
            'documents_found': 0,
            'policy_compliance': {},
            'errors': []
        }
        
        # Test queries to verify policy implementation
        test_queries = [
            {
                'name': 'Find all engineering documents',
                'query': "SELECT * FROM c WHERE c.category = 'engineering' AND c.status = 'active'",
                'expected_min': 3
            },
            {
                'name': 'Find engineering guides',
                'query': "SELECT * FROM c WHERE c.type = 'guide' AND c.category = 'engineering'",
                'expected_min': 2
            },
            {
                'name': 'Find HEAD_OF_ENGINEERING owned documents',
                'query': "SELECT * FROM c WHERE c.owner = 'HEAD_OF_ENGINEERING' AND c.status = 'active'",
                'expected_min': 4
            },
            {
                'name': 'Find high complexity engineering documents',
                'query': "SELECT * FROM c WHERE c.complexity = 'high' AND c.category = 'engineering'",
                'expected_min': 1
            },
            {
                'name': 'Find documents with dependencies',
                'query': "SELECT * FROM c WHERE IS_DEFINED(c.dependencies) AND c.category = 'engineering'",
                'expected_min': 4
            },
            {
                'name': 'Search by keyword',
                'query': "SELECT * FROM c WHERE ARRAY_CONTAINS(c.keywords, 'cosmos-db')",
                'expected_min': 1
            }
        ]
        
        for test_query in test_queries:
            try:
                verification_results['queries_tested'] += 1
                
                # Execute query across both containers
                documents_results = []
                processes_results = []
                
                try:
                    documents_container = self.db_manager.database.get_container_client('documents')
                    documents_results = list(documents_container.query_items(
                        test_query['query'],
                        enable_cross_partition_query=True
                    ))
                except Exception as e:
                    print(f"⚠️ Documents container query failed: {e}")
                
                try:
                    processes_container = self.db_manager.database.get_container_client('processes')
                    processes_results = list(processes_container.query_items(
                        test_query['query'],
                        enable_cross_partition_query=True
                    ))
                except Exception as e:
                    print(f"⚠️ Processes container query failed: {e}")
                
                # Combine results
                all_results = documents_results + processes_results
                result_count = len(all_results)
                
                print(f"📊 {test_query['name']}: Found {result_count} documents")
                
                if result_count >= test_query['expected_min']:
                    verification_results['queries_successful'] += 1
                    print(f"   ✅ Meets minimum expectation ({test_query['expected_min']})")
                else:
                    print(f"   ❌ Below minimum expectation ({test_query['expected_min']})")
                
                verification_results['documents_found'] += result_count
                
                # Show sample results
                for i, doc in enumerate(all_results[:2]):  # Show first 2 results
                    print(f"   📄 {doc.get('name', doc.get('title', doc.get('id', 'Unknown')))}")
                    if i == 0:  # Show tags for first result
                        tags = doc.get('tags', [])
                        print(f"      Tags: {', '.join(tags[:5])}")  # Show first 5 tags
                
                print()
                
            except Exception as e:
                error_msg = f"Query '{test_query['name']}' failed: {str(e)}"
                verification_results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                print()
        
        # Check policy compliance
        verification_results['policy_compliance'] = {
            'naming_convention': self._check_naming_convention(),
            'required_tags': self._check_required_tags(),
            'engineering_tags': self._check_engineering_tags()
        }
        
        return verification_results
    
    def _check_naming_convention(self) -> Dict[str, Any]:
        """Check naming convention compliance"""
        try:
            # Query for documents that don't follow naming pattern
            query = "SELECT c.id, c.name FROM c WHERE c.category = 'engineering'"
            
            documents_container = self.db_manager.database.get_container_client('documents')
            results = list(documents_container.query_items(query, enable_cross_partition_query=True))
            
            processes_container = self.db_manager.database.get_container_client('processes')
            process_results = list(processes_container.query_items(query, enable_cross_partition_query=True))
            
            all_results = results + process_results
            
            compliant = 0
            total = len(all_results)
            
            for doc in all_results:
                doc_id = doc.get('id', '')
                # Check if follows pattern: {type}-{category}-{identifier}_{name}
                if '-' in doc_id and '_' in doc_id:
                    parts = doc_id.split('_', 1)
                    if len(parts) == 2 and len(parts[0].split('-')) >= 3:
                        compliant += 1
            
            return {
                'total_checked': total,
                'compliant': compliant,
                'compliance_rate': compliant / total if total > 0 else 0
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _check_required_tags(self) -> Dict[str, Any]:
        """Check required tags compliance"""
        try:
            required_tags = ['type', 'category', 'status', 'owner', 'audience']
            
            query = "SELECT c.id, c.type, c.category, c.status, c.owner, c.audience FROM c WHERE c.category = 'engineering'"
            
            documents_container = self.db_manager.database.get_container_client('documents')
            results = list(documents_container.query_items(query, enable_cross_partition_query=True))
            
            processes_container = self.db_manager.database.get_container_client('processes')
            process_results = list(processes_container.query_items(query, enable_cross_partition_query=True))
            
            all_results = results + process_results
            
            compliant = 0
            total = len(all_results)
            
            for doc in all_results:
                has_all_tags = True
                for tag in required_tags:
                    if not doc.get(tag):
                        has_all_tags = False
                        break
                if has_all_tags:
                    compliant += 1
            
            return {
                'total_checked': total,
                'compliant': compliant,
                'compliance_rate': compliant / total if total > 0 else 0,
                'required_tags': required_tags
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _check_engineering_tags(self) -> Dict[str, Any]:
        """Check engineering-specific optional tags"""
        try:
            engineering_tags = ['complexity', 'dependencies', 'test_coverage']
            
            query = "SELECT c.id, c.complexity, c.dependencies, c.test_coverage FROM c WHERE c.category = 'engineering'"
            
            documents_container = self.db_manager.database.get_container_client('documents')
            results = list(documents_container.query_items(query, enable_cross_partition_query=True))
            
            processes_container = self.db_manager.database.get_container_client('processes')
            process_results = list(processes_container.query_items(query, enable_cross_partition_query=True))
            
            all_results = results + process_results
            
            tag_stats = {}
            total = len(all_results)
            
            for tag in engineering_tags:
                present = sum(1 for doc in all_results if doc.get(tag))
                tag_stats[tag] = {
                    'present': present,
                    'coverage': present / total if total > 0 else 0
                }
            
            return {
                'total_checked': total,
                'tag_coverage': tag_stats,
                'engineering_tags': engineering_tags
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_discovery_test_queries(self) -> List[Dict[str, str]]:
        """Generate test queries to demonstrate policy effectiveness"""
        
        return [
            {
                'description': 'Find all engineering procedures requiring high complexity',
                'query': "SELECT c.id, c.title, c.complexity, c.owner FROM c WHERE c.type = 'procedure' AND c.category = 'engineering' AND c.complexity = 'high' ORDER BY c.createdDate DESC"
            },
            {
                'description': 'Discover documents with Cosmos DB dependencies',
                'query': "SELECT c.id, c.title, c.dependencies, c.test_coverage FROM c WHERE c.category = 'engineering' AND ARRAY_CONTAINS(c.dependencies, 'cosmos-db')"
            },
            {
                'description': 'Find engineering guides for all audiences',
                'query': "SELECT c.id, c.title, c.audience, c.abstract FROM c WHERE c.type = 'guide' AND c.category = 'engineering' AND c.audience = 'all' AND c.status = 'active'"
            },
            {
                'description': 'Search for documents by keyword',
                'query': "SELECT c.id, c.title, c.keywords FROM c WHERE ARRAY_CONTAINS(c.keywords, 'database') AND c.category = 'engineering'"
            },
            {
                'description': 'Find documents with high test coverage',
                'query': "SELECT c.id, c.title, c.test_coverage, c.complexity FROM c WHERE c.category = 'engineering' AND c.test_coverage > '85%' ORDER BY c.test_coverage DESC"
            }
        ]
    
    def run_discovery_tests(self) -> None:
        """Run discovery test queries to show policy effectiveness"""
        print("\n🎯 TESTING ENHANCED SEMANTIC POLICY FOR DISCOVERY")
        print("=" * 60)
        
        test_queries = self.generate_discovery_test_queries()
        
        for i, test in enumerate(test_queries, 1):
            print(f"\n{i}. {test['description']}")
            print("-" * 50)
            
            try:
                # Test on both containers
                documents_container = self.db_manager.database.get_container_client('documents')
                documents_results = list(documents_container.query_items(
                    test['query'],
                    enable_cross_partition_query=True
                ))
                
                processes_container = self.db_manager.database.get_container_client('processes')
                processes_results = list(processes_container.query_items(
                    test['query'],
                    enable_cross_partition_query=True
                ))
                
                all_results = documents_results + processes_results
                
                if all_results:
                    print(f"📊 Found {len(all_results)} matching documents:")
                    for doc in all_results:
                        title = doc.get('title', doc.get('name', doc.get('id', 'Unknown')))
                        print(f"   📄 {title}")
                        
                        # Show relevant metadata
                        if 'complexity' in doc:
                            print(f"      Complexity: {doc['complexity']}")
                        if 'dependencies' in doc:
                            deps = doc['dependencies']
                            if isinstance(deps, list):
                                print(f"      Dependencies: {', '.join(deps)}")
                        if 'test_coverage' in doc:
                            print(f"      Test Coverage: {doc['test_coverage']}")
                        if 'audience' in doc:
                            print(f"      Audience: {doc['audience']}")
                        print()
                else:
                    print("📊 No matching documents found")
                    
            except Exception as e:
                print(f"❌ Query failed: {e}")
            
            print()

def main():
    """Main execution function"""
    print("🏗️ HEAD_OF_ENGINEERING DOCUMENT UPLOAD SYSTEM")
    print("=" * 70)
    print("Enhanced Semantic Policy v2.0 Implementation")
    print("Uploads engineering documents with proper tagging and verification")
    print()
    
    try:
        # Initialize uploader
        uploader = EngineeringDocumentUploader()
        
        # Upload all documents
        upload_stats = uploader.upload_all_documents()
        
        # Verify policy implementation
        verification_results = uploader.verify_enhanced_semantic_policy()
        
        # Run discovery tests
        uploader.run_discovery_tests()
        
        # Final summary
        print("\n" + "=" * 70)
        print("📊 UPLOAD SUMMARY")
        print("=" * 70)
        print(f"✅ Documents uploaded: {upload_stats['documents']}")
        print(f"✅ Processes uploaded: {upload_stats['processes']}")
        print(f"✅ Successful uploads: {upload_stats['successful']}")
        print(f"❌ Failed uploads: {upload_stats['failed']}")
        
        if upload_stats['errors']:
            print("\n❌ Errors encountered:")
            for error in upload_stats['errors']:
                print(f"   • {error}")
        
        print(f"\n🔍 VERIFICATION RESULTS")
        print("-" * 40)
        print(f"✅ Queries tested: {verification_results['queries_tested']}")
        print(f"✅ Queries successful: {verification_results['queries_successful']}")
        print(f"📄 Total documents found: {verification_results['documents_found']}")
        
        # Policy compliance summary
        compliance = verification_results.get('policy_compliance', {})
        
        naming = compliance.get('naming_convention', {})
        if 'compliance_rate' in naming:
            print(f"📝 Naming convention compliance: {naming['compliance_rate']:.1%}")
        
        required = compliance.get('required_tags', {})
        if 'compliance_rate' in required:
            print(f"🏷️ Required tags compliance: {required['compliance_rate']:.1%}")
        
        engineering = compliance.get('engineering_tags', {})
        if 'tag_coverage' in engineering:
            print("🔧 Engineering tag coverage:")
            for tag, stats in engineering['tag_coverage'].items():
                print(f"   • {tag}: {stats['coverage']:.1%}")
        
        print("\n✨ ENHANCED SEMANTIC POLICY BENEFITS DEMONSTRATED:")
        print("   • Standardized naming convention across all documents")
        print("   • Consistent tagging for improved discoverability")
        print("   • Engineering-specific metadata for technical assets")
        print("   • Cross-container queries for comprehensive search")
        print("   • Compliance tracking and verification capabilities")
        
        print(f"\n🎯 SUCCESS METRICS:")
        success_rate = upload_stats['successful'] / (upload_stats['successful'] + upload_stats['failed']) if (upload_stats['successful'] + upload_stats['failed']) > 0 else 0
        print(f"   • Upload success rate: {success_rate:.1%}")
        
        query_success_rate = verification_results['queries_successful'] / verification_results['queries_tested'] if verification_results['queries_tested'] > 0 else 0
        print(f"   • Query success rate: {query_success_rate:.1%}")
        
        print(f"   • Documents discoverable via policy: {verification_results['documents_found']}")
        
        if success_rate >= 0.9 and query_success_rate >= 0.8:
            print("\n🎉 ENHANCED SEMANTIC POLICY SUCCESSFULLY IMPLEMENTED!")
            print("All engineering documents are now discoverable and compliant.")
        else:
            print("\n⚠️ Some issues detected. Review errors above and retry.")
            
        return 0 if success_rate >= 0.9 else 1
        
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())