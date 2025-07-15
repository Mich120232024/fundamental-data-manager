#!/usr/bin/env python3
"""
Comprehensive Cosmos DB Audit Script
Audits all containers against constitutional standards and enhanced semantic policy
"""

from cosmos_db_manager import get_db_manager
from datetime import datetime, timedelta
import json
import re
from typing import Dict, List, Any, Tuple
from pathlib import Path

class CosmosAuditFramework:
    """Comprehensive audit framework for constitutional compliance"""
    
    def __init__(self):
        self.db = get_db_manager()
        self.audit_timestamp = datetime.now().isoformat() + 'Z'
        self.report = {
            'audit_id': f"AUDIT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'timestamp': self.audit_timestamp,
            'compliance_status': 'UNKNOWN',
            'containers': {},
            'violations': [],
            'recommendations': [],
            'metrics': {},
            'summary': {}
        }
        
        # Constitutional standards
        self.constitutional_standards = {
            'messages': {
                'required_fields': ['id', 'type', 'from', 'to', 'subject', 'content', 'priority', 'status', 'requires_response', 'metadata'],
                'valid_types': ['request', 'response', 'notification', 'escalation'],
                'valid_priorities': ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
                'valid_statuses': ['pending', 'acknowledged', 'in_progress', 'resolved', 'escalated'],
                'banned_phrases': ["it appears that", "approximately", "successfully deployed", "should be working", "i believe", "seems to be", "probably"]
            },
            'documents': {
                'required_fields': ['id', 'documentId', 'title', 'workspace', 'docType', 'category', 'content'],
                'naming_pattern': r'^DOC-[A-Z]+-[A-Z0-9]+-\d+_[a-z_]+$',
                'required_metadata': ['author', 'owner', 'status', 'version']
            },
            'metadata': {
                'required_fields': ['id', 'type', 'name', 'description', 'schema_version'],
                'naming_pattern': r'^[a-z]+-[a-z]+-[a-z0-9]+_[a-z_]+$'
            },
            'audit': {
                'required_fields': ['id', 'audit_type', 'timestamp', 'auditor', 'findings'],
                'retention_days': 365
            },
            'enforcement': {
                'required_fields': ['id', 'agent_id', 'violation_type', 'severity', 'timestamp'],
                'valid_severities': ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
            },
            'processes': {
                'required_fields': ['id', 'process_name', 'version', 'status', 'definition'],
                'valid_statuses': ['draft', 'active', 'deprecated']
            }
        }
        
        # Enhanced semantic policy standards
        self.semantic_policy = {
            'naming_pattern': r'^[a-z]+-[a-z]+-[a-z0-9]+_[a-z_]+$',
            'required_tags': ['type', 'category', 'status', 'owner', 'audience'],
            'team_specific_tags': {
                'Engineering': ['complexity', 'dependencies', 'test_coverage'],
                'Governance': ['compliance_level', 'evidence_required', 'audit_frequency'],
                'Research': ['methodology', 'confidence_level', 'peer_reviewed'],
                'Business': ['roi_impact', 'stakeholders', 'market_segment'],
                'Executive': ['strategic_priority', 'decision_impact', 'board_visibility'],
                'Digital Labor': ['skill_level', 'utilization_rate', 'performance_tier']
            }
        }
    
    def audit_all_containers(self) -> Dict[str, Any]:
        """Main audit entry point - audits all containers"""
        
        print("🔍 COMPREHENSIVE COSMOS DB CONSTITUTIONAL AUDIT")
        print("=" * 80)
        print(f"Audit ID: {self.report['audit_id']}")
        print(f"Timestamp: {self.audit_timestamp}")
        print()
        
        # Discover containers
        containers = self.discover_containers()
        print(f"📊 Discovered {len(containers)} containers: {', '.join(containers)}")
        print()
        
        # Audit each container
        for container_name in containers:
            print(f"🔍 Auditing container: {container_name}")
            self.audit_container(container_name)
            print()
        
        # Cross-container analysis
        self.perform_cross_container_analysis()
        
        # Generate final compliance status
        self.calculate_final_compliance()
        
        # Save audit report
        self.save_audit_report()
        
        return self.report
    
    def discover_containers(self) -> List[str]:
        """Discover all containers in the database"""
        try:
            # Get database properties to list containers
            database_properties = self.db.database.read()
            
            # Known containers based on system structure
            known_containers = ['messages', 'audit', 'documents', 'metadata', 'enforcement', 'processes']
            
            # Test each container for existence
            existing_containers = []
            for container_name in known_containers:
                try:
                    container = self.db.database.get_container_client(container_name)
                    # Test if container exists by querying it
                    test_query = list(container.query_items('SELECT TOP 1 * FROM c', enable_cross_partition_query=True))
                    existing_containers.append(container_name)
                except Exception as e:
                    print(f"   Container '{container_name}' not accessible: {str(e)[:100]}")
            
            return existing_containers
            
        except Exception as e:
            print(f"❌ Error discovering containers: {e}")
            # Fall back to known containers
            return ['messages', 'audit', 'documents', 'metadata', 'enforcement', 'processes']
    
    def audit_container(self, container_name: str):
        """Audit a specific container against constitutional standards"""
        
        container_audit = {
            'name': container_name,
            'document_count': 0,
            'sample_documents': [],
            'schema_compliance': {'compliant': 0, 'violations': []},
            'semantic_compliance': {'compliant': 0, 'violations': []},
            'metadata_documentation': {'exists': False, 'compliant': False},
            'health_status': 'UNKNOWN'
        }
        
        try:
            container = self.db.database.get_container_client(container_name)
            
            # Get document count
            count_query = "SELECT VALUE COUNT(1) FROM c"
            count_result = list(container.query_items(count_query, enable_cross_partition_query=True))
            container_audit['document_count'] = count_result[0] if count_result else 0
            
            print(f"   📊 {container_audit['document_count']} documents found")
            
            # Sample documents for analysis (up to 10)
            sample_query = "SELECT TOP 10 * FROM c"
            samples = list(container.query_items(sample_query, enable_cross_partition_query=True))
            container_audit['sample_documents'] = samples
            
            print(f"   📝 Analyzing {len(samples)} sample documents")
            
            # Audit each sample document
            for doc in samples:
                self.audit_document_schema(container_name, doc, container_audit)
                self.audit_semantic_compliance(container_name, doc, container_audit)
            
            # Check for metadata documentation
            self.check_metadata_documentation(container_name, container_audit)
            
            # Calculate compliance rates
            total_samples = len(samples)
            if total_samples > 0:
                schema_rate = (total_samples - len(container_audit['schema_compliance']['violations'])) / total_samples * 100
                semantic_rate = (total_samples - len(container_audit['semantic_compliance']['violations'])) / total_samples * 100
                
                print(f"   ✅ Schema compliance: {schema_rate:.1f}%")
                print(f"   📋 Semantic compliance: {semantic_rate:.1f}%")
                
                container_audit['health_status'] = 'HEALTHY' if schema_rate >= 90 and semantic_rate >= 80 else 'NEEDS_ATTENTION'
            else:
                container_audit['health_status'] = 'EMPTY'
            
        except Exception as e:
            print(f"   ❌ Error auditing container: {e}")
            container_audit['health_status'] = 'ERROR'
            container_audit['error'] = str(e)
        
        self.report['containers'][container_name] = container_audit
    
    def audit_document_schema(self, container_name: str, document: Dict, container_audit: Dict):
        """Audit document against constitutional schema requirements"""
        
        if container_name not in self.constitutional_standards:
            return  # No standards defined for this container
        
        standards = self.constitutional_standards[container_name]
        violations = []
        
        # Check required fields
        for field in standards['required_fields']:
            if field not in document:
                violations.append({
                    'type': 'missing_required_field',
                    'field': field,
                    'document_id': document.get('id', 'UNKNOWN'),
                    'severity': 'HIGH'
                })
        
        # Check naming patterns
        if 'naming_pattern' in standards:
            doc_id = document.get('id', '')
            if not re.match(standards['naming_pattern'], doc_id):
                violations.append({
                    'type': 'invalid_naming_pattern',
                    'document_id': doc_id,
                    'expected_pattern': standards['naming_pattern'],
                    'severity': 'MEDIUM'
                })
        
        # Container-specific validations
        if container_name == 'messages':
            self.validate_message_specifics(document, violations)
        elif container_name == 'documents':
            self.validate_document_specifics(document, violations)
        elif container_name == 'enforcement':
            self.validate_enforcement_specifics(document, violations)
        
        if violations:
            container_audit['schema_compliance']['violations'].extend(violations)
    
    def validate_message_specifics(self, message: Dict, violations: List):
        """Validate message-specific requirements"""
        
        # Check message type
        msg_type = message.get('type', '')
        if msg_type not in self.constitutional_standards['messages']['valid_types']:
            violations.append({
                'type': 'invalid_message_type',
                'value': msg_type,
                'valid_values': self.constitutional_standards['messages']['valid_types'],
                'document_id': message.get('id', 'UNKNOWN'),
                'severity': 'MEDIUM'
            })
        
        # Check priority
        priority = message.get('priority', '')
        if priority not in self.constitutional_standards['messages']['valid_priorities']:
            violations.append({
                'type': 'invalid_priority',
                'value': priority,
                'valid_values': self.constitutional_standards['messages']['valid_priorities'],
                'document_id': message.get('id', 'UNKNOWN'),
                'severity': 'MEDIUM'
            })
        
        # Check for banned phrases
        content = str(message.get('content', '')).lower()
        for phrase in self.constitutional_standards['messages']['banned_phrases']:
            if phrase in content:
                violations.append({
                    'type': 'banned_phrase_detected',
                    'phrase': phrase,
                    'document_id': message.get('id', 'UNKNOWN'),
                    'severity': 'HIGH'
                })
        
        # Check recipient format
        recipients = message.get('to', '')
        if recipients and not isinstance(recipients, list):
            violations.append({
                'type': 'invalid_recipient_format',
                'expected': 'array',
                'actual': type(recipients).__name__,
                'document_id': message.get('id', 'UNKNOWN'),
                'severity': 'HIGH'
            })
        
        # Check for evidence when making success claims
        if any(word in content for word in ['successfully', 'completed', 'fixed', 'deployed']):
            if not message.get('evidence'):
                violations.append({
                    'type': 'missing_evidence',
                    'description': 'Success claims require evidence',
                    'document_id': message.get('id', 'UNKNOWN'),
                    'severity': 'CRITICAL'
                })
    
    def validate_document_specifics(self, document: Dict, violations: List):
        """Validate document-specific requirements"""
        
        # Check document ID format
        doc_id = document.get('documentId', '')
        if doc_id and not re.match(r'^DOC-[A-Z]+-[A-Z0-9]+-\d+$', doc_id):
            violations.append({
                'type': 'invalid_document_id_format',
                'value': doc_id,
                'expected_pattern': 'DOC-{WORKSPACE}-{TYPE}-{NUMBER}',
                'document_id': document.get('id', 'UNKNOWN'),
                'severity': 'MEDIUM'
            })
        
        # Check required metadata
        for field in self.constitutional_standards['documents']['required_metadata']:
            if field not in document:
                violations.append({
                    'type': 'missing_document_metadata',
                    'field': field,
                    'document_id': document.get('id', 'UNKNOWN'),
                    'severity': 'MEDIUM'
                })
    
    def validate_enforcement_specifics(self, enforcement: Dict, violations: List):
        """Validate enforcement record specifics"""
        
        severity = enforcement.get('severity', '')
        if severity not in self.constitutional_standards['enforcement']['valid_severities']:
            violations.append({
                'type': 'invalid_enforcement_severity',
                'value': severity,
                'valid_values': self.constitutional_standards['enforcement']['valid_severities'],
                'document_id': enforcement.get('id', 'UNKNOWN'),
                'severity': 'MEDIUM'
            })
    
    def audit_semantic_compliance(self, container_name: str, document: Dict, container_audit: Dict):
        """Audit document against enhanced semantic policy"""
        
        violations = []
        doc_id = document.get('id', '')
        
        # Check naming pattern compliance
        if not re.match(self.semantic_policy['naming_pattern'], doc_id):
            violations.append({
                'type': 'semantic_naming_violation',
                'document_id': doc_id,
                'expected_pattern': self.semantic_policy['naming_pattern'],
                'severity': 'MEDIUM'
            })
        
        # Check for required tags (if document has tagging system)
        tags = document.get('tags', [])
        metadata = document.get('metadata', {})
        
        if isinstance(tags, list) or isinstance(metadata, dict):
            # Look for semantic tags in either tags array or metadata fields
            available_tags = tags if isinstance(tags, list) else []
            if isinstance(metadata, dict):
                available_tags.extend(metadata.keys())
            
            missing_required = []
            for required_tag in self.semantic_policy['required_tags']:
                if required_tag not in available_tags:
                    missing_required.append(required_tag)
            
            if missing_required:
                violations.append({
                    'type': 'missing_semantic_tags',
                    'missing_tags': missing_required,
                    'document_id': doc_id,
                    'severity': 'LOW'
                })
        
        if violations:
            container_audit['semantic_compliance']['violations'].extend(violations)
    
    def check_metadata_documentation(self, container_name: str, container_audit: Dict):
        """Check if container is properly documented in metadata container"""
        
        try:
            metadata_container = self.db.database.get_container_client('metadata')
            
            # Look for container documentation
            query = f"SELECT * FROM c WHERE c.container_name = '{container_name}' OR c.name = '{container_name}'"
            docs = list(metadata_container.query_items(query, enable_cross_partition_query=True))
            
            if docs:
                container_audit['metadata_documentation']['exists'] = True
                
                # Check if documentation is comprehensive
                doc = docs[0]
                required_fields = ['description', 'schema_version', 'purpose']
                has_all_fields = all(field in doc for field in required_fields)
                
                container_audit['metadata_documentation']['compliant'] = has_all_fields
                container_audit['metadata_documentation']['document'] = doc
                
                print(f"   📚 Metadata documentation: {'COMPLIANT' if has_all_fields else 'INCOMPLETE'}")
            else:
                container_audit['metadata_documentation']['exists'] = False
                container_audit['metadata_documentation']['compliant'] = False
                print(f"   📚 Metadata documentation: MISSING")
                
                # Add violation
                self.report['violations'].append({
                    'type': 'missing_metadata_documentation',
                    'container': container_name,
                    'severity': 'MEDIUM',
                    'description': f'Container {container_name} is not documented in metadata container'
                })
                
        except Exception as e:
            print(f"   📚 Metadata documentation: ERROR - {str(e)[:50]}")
            container_audit['metadata_documentation']['error'] = str(e)
    
    def perform_cross_container_analysis(self):
        """Perform cross-container compliance analysis"""
        
        print("🔍 CROSS-CONTAINER ANALYSIS")
        print("-" * 40)
        
        # Check message-document relationships
        self.analyze_message_document_relationships()
        
        # Check enforcement effectiveness
        self.analyze_enforcement_effectiveness()
        
        # Check process compliance
        self.analyze_process_compliance()
        
        print()
    
    def analyze_message_document_relationships(self):
        """Analyze relationships between messages and documents"""
        
        try:
            # Look for governance messages that reference documents
            if 'messages' in self.report['containers'] and 'documents' in self.report['containers']:
                messages_container = self.db.database.get_container_client('system_inbox')
                
                # Find governance-related messages
                gov_query = "SELECT * FROM c WHERE CONTAINS(c.content, 'constitutional') OR CONTAINS(c.content, 'governance') OR CONTAINS(c.subject, 'governance')"
                gov_messages = list(messages_container.query_items(gov_query, enable_cross_partition_query=True))
                
                print(f"   📋 Found {len(gov_messages)} governance-related messages")
                
                # Check if these messages properly reference documents
                missing_references = 0
                for msg in gov_messages:
                    content = str(msg.get('content', '')) + str(msg.get('subject', ''))
                    if 'DOC-' not in content:
                        missing_references += 1
                
                if missing_references > 0:
                    self.report['violations'].append({
                        'type': 'governance_messages_missing_document_references',
                        'count': missing_references,
                        'total_gov_messages': len(gov_messages),
                        'severity': 'MEDIUM'
                    })
                    print(f"   ⚠️  {missing_references} governance messages lack document references")
                else:
                    print(f"   ✅ All governance messages properly reference documents")
                    
        except Exception as e:
            print(f"   ❌ Error analyzing message-document relationships: {e}")
    
    def analyze_enforcement_effectiveness(self):
        """Analyze enforcement container effectiveness"""
        
        try:
            if 'enforcement' in self.report['containers']:
                enforcement_container = self.db.database.get_container_client('enforcement')
                
                # Get recent violations
                cutoff = (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
                query = f"SELECT * FROM c WHERE c.timestamp >= '{cutoff}'"
                recent_violations = list(enforcement_container.query_items(query, enable_cross_partition_query=True))
                
                print(f"   ⚖️  {len(recent_violations)} violations in last 30 days")
                
                # Analyze violation trends
                agent_violations = {}
                for violation in recent_violations:
                    agent = violation.get('agent_id', 'UNKNOWN')
                    agent_violations[agent] = agent_violations.get(agent, 0) + 1
                
                repeat_offenders = {agent: count for agent, count in agent_violations.items() if count > 3}
                
                if repeat_offenders:
                    print(f"   ⚠️  {len(repeat_offenders)} agents with multiple violations")
                    self.report['violations'].append({
                        'type': 'repeat_violation_agents',
                        'agents': repeat_offenders,
                        'severity': 'HIGH'
                    })
                else:
                    print(f"   ✅ No repeat violation patterns detected")
                    
        except Exception as e:
            print(f"   ❌ Error analyzing enforcement effectiveness: {e}")
    
    def analyze_process_compliance(self):
        """Analyze process compliance across containers"""
        
        try:
            if 'processes' in self.report['containers']:
                processes_container = self.db.database.get_container_client('processes')
                
                # Get active processes
                query = "SELECT * FROM c WHERE c.status = 'active'"
                active_processes = list(processes_container.query_items(query, enable_cross_partition_query=True))
                
                print(f"   📋 {len(active_processes)} active processes")
                
                # Check if processes have recent usage in messages
                if 'messages' in self.report['containers']:
                    messages_container = self.db.database.get_container_client('system_inbox')
                    
                    unused_processes = []
                    for process in active_processes:
                        process_name = process.get('process_name', '')
                        if process_name:
                            # Look for mentions in recent messages
                            search_query = f"SELECT TOP 1 * FROM c WHERE CONTAINS(c.content, '{process_name}')"
                            mentions = list(messages_container.query_items(search_query, enable_cross_partition_query=True))
                            
                            if not mentions:
                                unused_processes.append(process_name)
                    
                    if unused_processes:
                        print(f"   ⚠️  {len(unused_processes)} processes not referenced in recent messages")
                        self.report['recommendations'].append({
                            'type': 'review_unused_processes',
                            'processes': unused_processes,
                            'action': 'Consider deprecating or promoting usage'
                        })
                    else:
                        print(f"   ✅ All processes actively referenced")
                        
        except Exception as e:
            print(f"   ❌ Error analyzing process compliance: {e}")
    
    def calculate_final_compliance(self):
        """Calculate overall compliance status"""
        
        print("📊 CALCULATING FINAL COMPLIANCE STATUS")
        print("-" * 40)
        
        total_containers = len(self.report['containers'])
        healthy_containers = sum(1 for container in self.report['containers'].values() 
                               if container['health_status'] == 'HEALTHY')
        
        container_health_rate = (healthy_containers / total_containers * 100) if total_containers > 0 else 0
        
        # Count violations by severity
        critical_violations = sum(1 for v in self.report['violations'] if v.get('severity') == 'CRITICAL')
        high_violations = sum(1 for v in self.report['violations'] if v.get('severity') == 'HIGH')
        medium_violations = sum(1 for v in self.report['violations'] if v.get('severity') == 'MEDIUM')
        low_violations = sum(1 for v in self.report['violations'] if v.get('severity') == 'LOW')
        
        total_violations = critical_violations + high_violations + medium_violations + low_violations
        
        # Determine overall compliance
        if critical_violations > 0:
            compliance_status = 'NON_COMPLIANT'
        elif high_violations > 5:
            compliance_status = 'NON_COMPLIANT'
        elif container_health_rate < 70:
            compliance_status = 'NEEDS_ATTENTION'
        elif medium_violations > 10:
            compliance_status = 'NEEDS_ATTENTION'
        else:
            compliance_status = 'COMPLIANT'
        
        self.report['compliance_status'] = compliance_status
        self.report['metrics'] = {
            'total_containers': total_containers,
            'healthy_containers': healthy_containers,
            'container_health_rate': container_health_rate,
            'total_violations': total_violations,
            'critical_violations': critical_violations,
            'high_violations': high_violations,
            'medium_violations': medium_violations,
            'low_violations': low_violations
        }
        
        print(f"   📊 Container health rate: {container_health_rate:.1f}%")
        print(f"   ⚠️  Total violations: {total_violations}")
        print(f"   🚨 Critical violations: {critical_violations}")
        print(f"   🔶 High violations: {high_violations}")
        print(f"   🔸 Medium violations: {medium_violations}")
        print(f"   🔹 Low violations: {low_violations}")
        print(f"   📋 Overall compliance: {compliance_status}")
    
    def save_audit_report(self):
        """Save comprehensive audit report"""
        
        # Generate summary
        self.report['summary'] = {
            'audit_completed_at': datetime.now().isoformat() + 'Z',
            'containers_audited': list(self.report['containers'].keys()),
            'compliance_status': self.report['compliance_status'],
            'key_findings': self.generate_key_findings(),
            'next_steps': self.generate_next_steps()
        }
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/scripts/cosmos_audit_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 AUDIT REPORT SAVED: {report_file}")
        
        # Save to audit container if available
        try:
            if 'audit' in self.report['containers']:
                audit_container = self.db.database.get_container_client('audit')
                
                audit_record = {
                    'id': self.report['audit_id'],
                    'audit_type': 'comprehensive_constitutional_compliance',
                    'timestamp': self.audit_timestamp,
                    'auditor': 'CosmosAuditFramework',
                    'scope': 'all_containers',
                    'compliance_status': self.report['compliance_status'],
                    'findings': self.report['violations'],
                    'metrics': self.report['metrics'],
                    'report_file': report_file,
                    'partitionKey': datetime.now().strftime('%Y-%m')
                }
                
                audit_container.create_item(audit_record)
                print(f"📊 Audit record stored in audit container: {self.report['audit_id']}")
                
        except Exception as e:
            print(f"⚠️  Could not store audit record: {e}")
    
    def generate_key_findings(self) -> List[str]:
        """Generate key findings summary"""
        
        findings = []
        
        metrics = self.report['metrics']
        
        if metrics['critical_violations'] > 0:
            findings.append(f"🚨 {metrics['critical_violations']} critical constitutional violations require immediate attention")
        
        if metrics['container_health_rate'] < 80:
            findings.append(f"📊 Container health rate of {metrics['container_health_rate']:.1f}% below optimal threshold")
        
        # Check for missing metadata documentation
        missing_metadata = sum(1 for container in self.report['containers'].values() 
                             if not container['metadata_documentation']['exists'])
        if missing_metadata > 0:
            findings.append(f"📚 {missing_metadata} containers lack proper metadata documentation")
        
        # Check for semantic policy violations
        semantic_violations = 0
        for container in self.report['containers'].values():
            semantic_violations += len(container['semantic_compliance']['violations'])
        
        if semantic_violations > 10:
            findings.append(f"📋 {semantic_violations} semantic policy violations detected across containers")
        
        if not findings:
            findings.append("✅ No major constitutional violations detected")
        
        return findings
    
    def generate_next_steps(self) -> List[str]:
        """Generate recommended next steps"""
        
        steps = []
        
        if self.report['compliance_status'] == 'NON_COMPLIANT':
            steps.append("🚨 Address all critical violations immediately")
            steps.append("📋 Implement constitutional enforcement measures")
        
        if self.report['metrics']['container_health_rate'] < 80:
            steps.append("🔧 Improve container schema compliance")
            steps.append("📊 Implement automated validation checks")
        
        # Check for specific issues
        missing_metadata = sum(1 for container in self.report['containers'].values() 
                             if not container['metadata_documentation']['exists'])
        if missing_metadata > 0:
            steps.append("📚 Create comprehensive metadata documentation for all containers")
        
        if len(self.report['violations']) > 20:
            steps.append("⚖️ Implement automated constitutional compliance monitoring")
        
        steps.append("📅 Schedule follow-up audit in 30 days")
        steps.append("📋 Share audit results with constitutional governance team")
        
        return steps

def main():
    """Run comprehensive Cosmos DB audit"""
    
    print("🏛️ CONSTITUTIONAL COSMOS DB AUDIT FRAMEWORK")
    print("=" * 80)
    print("Auditing all containers against constitutional standards...")
    print("Checking enhanced semantic policy compliance...")
    print("Validating metadata documentation...")
    print("Analyzing cross-container relationships...")
    print()
    
    # Initialize and run audit
    auditor = CosmosAuditFramework()
    report = auditor.audit_all_containers()
    
    # Print final summary
    print("\n" + "=" * 80)
    print("🏛️ CONSTITUTIONAL AUDIT COMPLETED")
    print("=" * 80)
    print(f"📋 Audit ID: {report['audit_id']}")
    print(f"📊 Compliance Status: {report['compliance_status']}")
    print(f"📦 Containers Audited: {report['metrics']['total_containers']}")
    print(f"✅ Healthy Containers: {report['metrics']['healthy_containers']}")
    print(f"⚠️  Total Violations: {report['metrics']['total_violations']}")
    
    print("\n🔍 KEY FINDINGS:")
    for finding in report['summary']['key_findings']:
        print(f"   {finding}")
    
    print("\n📋 NEXT STEPS:")
    for step in report['summary']['next_steps']:
        print(f"   {step}")
    
    print(f"\n📄 Detailed report saved with evidence and recommendations")
    print("🏛️ Constitutional compliance audit complete - evidence-based results only")

if __name__ == "__main__":
    main()