#!/usr/bin/env python3
"""
Compliance Analysis Report Generator
Analyzes audit data to create actionable compliance insights
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class ComplianceAnalyzer:
    """Analyzes audit data to generate actionable compliance insights"""
    
    def __init__(self, audit_report_path: str):
        """Initialize with audit report data"""
        with open(audit_report_path, 'r') as f:
            self.audit_data = json.load(f)
        
        self.compliance_issues = {
            'CRITICAL': [],
            'HIGH': [],
            'MEDIUM': [],
            'LOW': []
        }
        
        self.recommendations = {
            'immediate_actions': [],
            'schema_fixes': [],
            'metadata_improvements': [],
            'process_enhancements': []
        }
    
    def analyze_compliance_gaps(self):
        """Analyze and categorize compliance gaps"""
        
        print("🔍 ANALYZING COMPLIANCE GAPS")
        print("=" * 60)
        
        # Analyze each container
        for container_name, container_data in self.audit_data['containers'].items():
            print(f"\n📦 {container_name.upper()} CONTAINER ANALYSIS")
            print("-" * 40)
            
            self.analyze_container_issues(container_name, container_data)
        
        # Analyze cross-container issues
        self.analyze_cross_container_issues()
        
        # Generate recommendations
        self.generate_recommendations()
    
    def analyze_container_issues(self, container_name: str, container_data: Dict):
        """Analyze issues for a specific container"""
        
        doc_count = container_data.get('document_count', 0)
        health_status = container_data.get('health_status', 'UNKNOWN')
        
        print(f"   📊 Documents: {doc_count}")
        print(f"   🏥 Health Status: {health_status}")
        
        # Schema compliance issues
        schema_violations = container_data.get('schema_compliance', {}).get('violations', [])
        semantic_violations = container_data.get('semantic_compliance', {}).get('violations', [])
        
        print(f"   ⚠️  Schema violations: {len(schema_violations)}")
        print(f"   📋 Semantic violations: {len(semantic_violations)}")
        
        # Categorize critical issues
        if container_name == 'messages' and len(schema_violations) > 20:
            self.compliance_issues['CRITICAL'].append({
                'container': container_name,
                'issue': 'Multiple message schema violations affecting communication',
                'count': len(schema_violations),
                'impact': 'Communication system reliability compromised'
            })
        
        # Missing metadata documentation
        metadata_doc = container_data.get('metadata_documentation', {})
        if not metadata_doc.get('exists', False):
            self.compliance_issues['HIGH'].append({
                'container': container_name,
                'issue': 'Missing metadata documentation',
                'impact': 'Container purpose and schema not documented'
            })
        elif not metadata_doc.get('compliant', False):
            self.compliance_issues['MEDIUM'].append({
                'container': container_name,
                'issue': 'Incomplete metadata documentation',
                'impact': 'Container documentation lacks required fields'
            })
        
        # Analyze specific violation patterns
        self.analyze_violation_patterns(container_name, schema_violations, semantic_violations)
    
    def analyze_violation_patterns(self, container_name: str, schema_violations: List, semantic_violations: List):
        """Analyze patterns in violations to identify root causes"""
        
        # Schema violation patterns
        violation_types = {}
        for violation in schema_violations:
            v_type = violation.get('type', 'unknown')
            violation_types[v_type] = violation_types.get(v_type, 0) + 1
        
        for v_type, count in violation_types.items():
            if count > 5:  # Multiple occurrences indicate systematic issue
                print(f"   🔍 Pattern detected: {v_type} ({count} instances)")
                
                if v_type == 'missing_required_field':
                    self.compliance_issues['HIGH'].append({
                        'container': container_name,
                        'issue': f'Systematic missing required fields ({count} documents)',
                        'pattern': v_type,
                        'impact': 'Data integrity and searchability compromised'
                    })
                elif v_type == 'invalid_naming_pattern':
                    self.compliance_issues['MEDIUM'].append({
                        'container': container_name,
                        'issue': f'Naming convention violations ({count} documents)',
                        'pattern': v_type,
                        'impact': 'Asset discovery and governance tracking affected'
                    })
                elif v_type == 'banned_phrase_detected':
                    self.compliance_issues['HIGH'].append({
                        'container': container_name,
                        'issue': f'Evidence-free claims detected ({count} documents)',
                        'pattern': v_type,
                        'impact': 'Constitutional evidence requirements violated'
                    })
        
        # Semantic violation patterns
        semantic_types = {}
        for violation in semantic_violations:
            v_type = violation.get('type', 'unknown')
            semantic_types[v_type] = semantic_types.get(v_type, 0) + 1
        
        for v_type, count in semantic_types.items():
            if count > 3:
                print(f"   📋 Semantic pattern: {v_type} ({count} instances)")
    
    def analyze_cross_container_issues(self):
        """Analyze issues that span multiple containers"""
        
        print(f"\n🔗 CROSS-CONTAINER ISSUES ANALYSIS")
        print("-" * 40)
        
        # Check violations from audit data
        violations = self.audit_data.get('violations', [])
        
        for violation in violations:
            v_type = violation.get('type', '')
            severity = violation.get('severity', 'MEDIUM')
            
            if v_type == 'governance_messages_missing_document_references':
                count = violation.get('count', 0)
                total = violation.get('total_gov_messages', 0)
                
                print(f"   📋 {count}/{total} governance messages lack document references")
                
                self.compliance_issues['HIGH'].append({
                    'type': 'cross_container',
                    'issue': 'Governance messages not linking to documents',
                    'count': count,
                    'total': total,
                    'impact': 'Governance traceability compromised'
                })
            
            elif v_type == 'missing_metadata_documentation':
                container = violation.get('container', 'unknown')
                print(f"   📚 Container '{container}' lacks metadata documentation")
            
            elif v_type == 'repeat_violation_agents':
                agents = violation.get('agents', {})
                print(f"   ⚖️  {len(agents)} agents with repeat violations")
    
    def generate_recommendations(self):
        """Generate actionable recommendations based on analysis"""
        
        print(f"\n💡 GENERATING RECOMMENDATIONS")
        print("-" * 40)
        
        # Immediate actions for critical issues
        critical_count = len(self.compliance_issues['CRITICAL'])
        high_count = len(self.compliance_issues['HIGH'])
        
        if critical_count > 0:
            self.recommendations['immediate_actions'].append({
                'priority': 'CRITICAL',
                'action': f'Address {critical_count} critical compliance violations immediately',
                'timeline': '24 hours',
                'impact': 'System integrity and constitutional compliance'
            })
        
        if high_count > 0:
            self.recommendations['immediate_actions'].append({
                'priority': 'HIGH',
                'action': f'Remediate {high_count} high-severity violations',
                'timeline': '72 hours',
                'impact': 'Operational reliability and governance effectiveness'
            })
        
        # Schema-specific recommendations
        self.generate_schema_recommendations()
        
        # Metadata recommendations
        self.generate_metadata_recommendations()
        
        # Process enhancement recommendations
        self.generate_process_recommendations()
        
        print(f"   ✅ Generated {len(self.recommendations['immediate_actions'])} immediate actions")
        print(f"   🔧 Generated {len(self.recommendations['schema_fixes'])} schema fixes")
        print(f"   📚 Generated {len(self.recommendations['metadata_improvements'])} metadata improvements")
        print(f"   📋 Generated {len(self.recommendations['process_enhancements'])} process enhancements")
    
    def generate_schema_recommendations(self):
        """Generate schema-specific recommendations"""
        
        # Check for widespread schema issues
        total_schema_violations = 0
        containers_with_issues = []
        
        for container_name, container_data in self.audit_data['containers'].items():
            violations = len(container_data.get('schema_compliance', {}).get('violations', []))
            if violations > 0:
                total_schema_violations += violations
                containers_with_issues.append(container_name)
        
        if total_schema_violations > 50:
            self.recommendations['schema_fixes'].append({
                'action': 'Implement automated schema validation service',
                'rationale': f'{total_schema_violations} schema violations across {len(containers_with_issues)} containers',
                'containers': containers_with_issues,
                'timeline': '1 week'
            })
        
        # Messages container specific fixes
        if 'messages' in containers_with_issues:
            self.recommendations['schema_fixes'].append({
                'action': 'Fix message schema compliance in messages container',
                'rationale': 'Critical communication infrastructure requires constitutional compliance',
                'specific_fixes': [
                    'Ensure all messages have required fields (id, type, from, to, subject, content, priority, status)',
                    'Convert recipient fields to array format where needed',
                    'Remove banned phrases and add evidence citations for claims',
                    'Standardize message types to: request, response, notification, escalation'
                ],
                'timeline': '3 days'
            })
    
    def generate_metadata_recommendations(self):
        """Generate metadata-specific recommendations"""
        
        missing_metadata = []
        incomplete_metadata = []
        
        for container_name, container_data in self.audit_data['containers'].items():
            metadata_doc = container_data.get('metadata_documentation', {})
            
            if not metadata_doc.get('exists', False):
                missing_metadata.append(container_name)
            elif not metadata_doc.get('compliant', False):
                incomplete_metadata.append(container_name)
        
        if missing_metadata:
            self.recommendations['metadata_improvements'].append({
                'action': f'Create metadata documentation for {len(missing_metadata)} containers',
                'containers': missing_metadata,
                'requirements': [
                    'Container purpose and scope description',
                    'Schema version and field definitions',
                    'Data retention and lifecycle policies',
                    'Access control and governance requirements',
                    'Enhanced semantic policy compliance tags'
                ],
                'timeline': '1 week'
            })
        
        if incomplete_metadata:
            self.recommendations['metadata_improvements'].append({
                'action': f'Complete metadata documentation for {len(incomplete_metadata)} containers',
                'containers': incomplete_metadata,
                'timeline': '3 days'
            })
    
    def generate_process_recommendations(self):
        """Generate process enhancement recommendations"""
        
        # Check overall compliance status
        compliance_status = self.audit_data.get('compliance_status', 'UNKNOWN')
        
        if compliance_status in ['NON_COMPLIANT', 'NEEDS_ATTENTION']:
            self.recommendations['process_enhancements'].append({
                'action': 'Implement continuous constitutional compliance monitoring',
                'rationale': f'Current compliance status: {compliance_status}',
                'components': [
                    'Automated daily compliance checks',
                    'Real-time violation detection and alerting',
                    'Constitutional enforcement workflow integration',
                    'Regular audit scheduling and reporting'
                ],
                'timeline': '2 weeks'
            })
        
        # Check for governance message issues
        violations = self.audit_data.get('violations', [])
        gov_message_issues = [v for v in violations if 'governance_messages' in v.get('type', '')]
        
        if gov_message_issues:
            self.recommendations['process_enhancements'].append({
                'action': 'Implement governance message-document linking requirements',
                'rationale': 'Governance messages lack proper document references',
                'implementation': [
                    'Require DOC-{ID} references in all governance messages',
                    'Validate document references at message submission',
                    'Create governance message templates with required fields',
                    'Train agents on constitutional reference requirements'
                ],
                'timeline': '1 week'
            })
    
    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary of compliance analysis"""
        
        # Calculate metrics
        total_issues = sum(len(issues) for issues in self.compliance_issues.values())
        total_recommendations = sum(len(recs) for recs in self.recommendations.values())
        
        containers_count = len(self.audit_data['containers'])
        healthy_containers = sum(1 for c in self.audit_data['containers'].values() 
                               if c['health_status'] == 'HEALTHY')
        
        compliance_rate = (healthy_containers / containers_count * 100) if containers_count > 0 else 0
        
        return {
            'audit_id': self.audit_data['audit_id'],
            'audit_timestamp': self.audit_data['timestamp'],
            'overall_compliance_status': self.audit_data['compliance_status'],
            'compliance_rate': round(compliance_rate, 1),
            'containers_audited': containers_count,
            'healthy_containers': healthy_containers,
            'total_issues_identified': total_issues,
            'critical_issues': len(self.compliance_issues['CRITICAL']),
            'high_severity_issues': len(self.compliance_issues['HIGH']),
            'medium_severity_issues': len(self.compliance_issues['MEDIUM']),
            'low_severity_issues': len(self.compliance_issues['LOW']),
            'total_recommendations': total_recommendations,
            'immediate_actions_required': len(self.recommendations['immediate_actions']),
            'key_compliance_gaps': [
                'Message schema violations affecting communication reliability',
                'Missing metadata documentation for container governance',
                'Governance messages lacking document references',
                'Semantic policy violations across multiple containers'
            ],
            'critical_recommendations': [
                'Implement automated schema validation for all containers',
                'Create comprehensive metadata documentation system',
                'Establish governance message-document linking requirements',
                'Deploy continuous constitutional compliance monitoring'
            ]
        }
    
    def save_analysis_report(self):
        """Save detailed compliance analysis report"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_data = {
            'analysis_id': f"COMPLIANCE_ANALYSIS_{timestamp}",
            'audit_reference': self.audit_data['audit_id'],
            'analysis_timestamp': datetime.now().isoformat() + 'Z',
            'executive_summary': self.generate_executive_summary(),
            'compliance_issues': self.compliance_issues,
            'recommendations': self.recommendations,
            'source_audit': self.audit_data['audit_id']
        }
        
        report_file = f"/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/scripts/compliance_analysis_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 COMPLIANCE ANALYSIS SAVED: {report_file}")
        return report_file, report_data

def main():
    """Run compliance analysis on latest audit report"""
    
    # Find latest audit report
    scripts_dir = Path("/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/scripts")
    audit_files = list(scripts_dir.glob("cosmos_audit_report_*.json"))
    
    if not audit_files:
        print("❌ No audit reports found. Run comprehensive_cosmos_audit.py first.")
        return
    
    latest_audit = max(audit_files, key=lambda f: f.stat().st_mtime)
    
    print("🔍 CONSTITUTIONAL COMPLIANCE ANALYSIS")
    print("=" * 60)
    print(f"📊 Analyzing audit report: {latest_audit.name}")
    print()
    
    # Initialize analyzer
    analyzer = ComplianceAnalyzer(str(latest_audit))
    
    # Run analysis
    analyzer.analyze_compliance_gaps()
    
    # Save results
    report_file, report_data = analyzer.save_analysis_report()
    
    # Print executive summary
    summary = report_data['executive_summary']
    
    print("\n" + "=" * 60)
    print("📋 EXECUTIVE SUMMARY")
    print("=" * 60)
    print(f"🏛️  Overall Compliance: {summary['overall_compliance_status']}")
    print(f"📊 Compliance Rate: {summary['compliance_rate']}%")
    print(f"🚨 Critical Issues: {summary['critical_issues']}")
    print(f"🔶 High Severity: {summary['high_severity_issues']}")
    print(f"🔸 Medium Severity: {summary['medium_severity_issues']}")
    print(f"🔹 Low Severity: {summary['low_severity_issues']}")
    print(f"💡 Total Recommendations: {summary['total_recommendations']}")
    print(f"⚡ Immediate Actions: {summary['immediate_actions_required']}")
    
    print(f"\n🔍 KEY COMPLIANCE GAPS:")
    for gap in summary['key_compliance_gaps']:
        print(f"   • {gap}")
    
    print(f"\n💡 CRITICAL RECOMMENDATIONS:")
    for rec in summary['critical_recommendations']:
        print(f"   • {rec}")
    
    print(f"\n📄 Detailed analysis with actionable recommendations saved")
    print("🏛️ Constitutional compliance analysis complete - evidence-based findings")

if __name__ == "__main__":
    main()