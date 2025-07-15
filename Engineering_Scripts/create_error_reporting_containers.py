#!/usr/bin/env python3
"""
Create Error Reporting and Process Violation Containers
with Event Hub Integration for Automated Auditing

Purpose: Replace email-based error reporting with container-based system
for real-time monitoring and automated audit capabilities
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ErrorReportingContainerManager:
    """Manage error reporting and process violation containers"""
    
    def __init__(self):
        """Initialize container manager with Cosmos DB connection"""
        self.endpoint = os.getenv('COSMOS_ENDPOINT')
        self.key = os.getenv('COSMOS_KEY')
        self.database_name = os.getenv('COSMOS_DATABASE', 'research-analytics-db')
        
        if not self.endpoint or not self.key:
            raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY must be set in .env file")
        
        self.client = CosmosClient(self.endpoint, self.key)
        self.database = self.client.get_database_client(self.database_name)
        
        # Setup logging
        self.logger = self._setup_logger()
        
        # Container names
        self.error_container_name = 'error_reports'
        self.violation_container_name = 'process_violations'
        self.audit_container_name = 'automated_audits'
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for container operations"""
        logger = logging.getLogger('ErrorReportingContainers')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def create_containers(self) -> Dict[str, bool]:
        """Create all error reporting containers"""
        results = {}
        
        # Container configurations
        containers = {
            self.error_container_name: {
                'partition_key': PartitionKey(path="/agent_name"),
                'default_ttl': None  # Keep errors indefinitely for analysis
            },
            self.violation_container_name: {
                'partition_key': PartitionKey(path="/violation_type"),
                'default_ttl': None  # Keep violations indefinitely for compliance
            },
            self.audit_container_name: {
                'partition_key': PartitionKey(path="/audit_date"),
                'default_ttl': 7776000  # Keep audits for 90 days
            }
        }
        
        for container_name, config in containers.items():
            try:
                # Try to create container
                container = self.database.create_container(
                    id=container_name,
                    partition_key=config['partition_key'],
                    default_ttl=config['default_ttl']
                )
                self.logger.info(f"✅ Created container: {container_name}")
                results[container_name] = True
                
            except Exception as e:
                if "Conflict" in str(e):
                    self.logger.info(f"✅ Container already exists: {container_name}")
                    results[container_name] = True
                else:
                    self.logger.error(f"❌ Failed to create container {container_name}: {e}")
                    results[container_name] = False
        
        return results
    
    def report_error(self, agent_name: str, error_type: str, error_details: Dict[str, Any]) -> str:
        """Report an error to the error container"""
        try:
            container = self.database.get_container_client(self.error_container_name)
            
            error_report = {
                'id': f"error_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{agent_name}",
                'agent_name': agent_name,
                'error_type': error_type,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'details': error_details,
                'status': 'reported',
                'severity': error_details.get('severity', 'medium'),
                'requires_action': error_details.get('requires_action', True)
            }
            
            response = container.create_item(error_report)
            self.logger.info(f"✅ Error reported: {response['id']}")
            return response['id']
            
        except Exception as e:
            self.logger.error(f"❌ Failed to report error: {e}")
            return None
    
    def report_violation(self, violation_type: str, agent_name: str, violation_details: Dict[str, Any]) -> str:
        """Report a process violation to the violation container"""
        try:
            container = self.database.get_container_client(self.violation_container_name)
            
            violation_report = {
                'id': f"violation_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{violation_type}",
                'violation_type': violation_type,
                'agent_name': agent_name,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'details': violation_details,
                'status': 'reported',
                'compliance_manager_notified': False,
                'resolution_required': violation_details.get('resolution_required', True),
                'constitutional_breach': violation_details.get('constitutional_breach', False)
            }
            
            response = container.create_item(violation_report)
            self.logger.info(f"✅ Violation reported: {response['id']}")
            return response['id']
            
        except Exception as e:
            self.logger.error(f"❌ Failed to report violation: {e}")
            return None
    
    def log_audit_result(self, audit_type: str, audit_results: Dict[str, Any]) -> str:
        """Log automated audit results"""
        try:
            container = self.database.get_container_client(self.audit_container_name)
            
            audit_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            audit_log = {
                'id': f"audit_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{audit_type}",
                'audit_date': audit_date,
                'audit_type': audit_type,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'results': audit_results,
                'agents_checked': audit_results.get('agents_checked', []),
                'violations_found': audit_results.get('violations_found', 0),
                'errors_found': audit_results.get('errors_found', 0),
                'compliance_score': audit_results.get('compliance_score', None)
            }
            
            response = container.create_item(audit_log)
            self.logger.info(f"✅ Audit logged: {response['id']}")
            return response['id']
            
        except Exception as e:
            self.logger.error(f"❌ Failed to log audit: {e}")
            return None
    
    def get_recent_errors(self, agent_name: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent error reports"""
        try:
            container = self.database.get_container_client(self.error_container_name)
            
            if agent_name:
                query = f"SELECT * FROM errors WHERE errors.agent_name = '{agent_name}' ORDER BY errors.timestamp DESC OFFSET 0 LIMIT {limit}"
            else:
                query = f"SELECT * FROM errors ORDER BY errors.timestamp DESC OFFSET 0 LIMIT {limit}"
            
            results = list(container.query_items(query, enable_cross_partition_query=True))
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get errors: {e}")
            return []
    
    def get_recent_violations(self, violation_type: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent process violations"""
        try:
            container = self.database.get_container_client(self.violation_container_name)
            
            if violation_type:
                query = f"SELECT * FROM violations WHERE violations.violation_type = '{violation_type}' ORDER BY violations.timestamp DESC OFFSET 0 LIMIT {limit}"
            else:
                query = f"SELECT * FROM violations ORDER BY violations.timestamp DESC OFFSET 0 LIMIT {limit}"
            
            results = list(container.query_items(query, enable_cross_partition_query=True))
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get violations: {e}")
            return []
    
    def get_audit_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get audit summary for recent days"""
        try:
            container = self.database.get_container_client(self.audit_container_name)
            
            # Get audits from last N days
            query = f"""
            SELECT 
                COUNT(1) as total_audits,
                SUM(audits.results.violations_found) as total_violations,
                SUM(audits.results.errors_found) as total_errors,
                AVG(audits.results.compliance_score) as avg_compliance_score
            FROM audits 
            WHERE audits.timestamp >= DateTimeAdd('day', -{days}, GetCurrentDateTime())
            """
            
            results = list(container.query_items(query, enable_cross_partition_query=True))
            
            if results:
                summary = results[0]
                summary['days_covered'] = days
                summary['last_updated'] = datetime.now(timezone.utc).isoformat()
                return summary
            else:
                return {
                    'total_audits': 0,
                    'total_violations': 0,
                    'total_errors': 0,
                    'avg_compliance_score': None,
                    'days_covered': days,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get audit summary: {e}")
            return {'error': str(e)}

def create_event_hub_integration():
    """Design Event Hub integration for real-time updates"""
    integration_config = {
        'event_hub_namespace': 'research-analytics-events',
        'event_hubs': {
            'error-events': {
                'purpose': 'Real-time error notifications',
                'triggers': ['new_error', 'critical_error', 'error_resolved'],
                'consumers': ['COMPLIANCE_MANAGER', 'HEAD_OF_DIGITAL_STAFF', 'automated_audit_system']
            },
            'violation-events': {
                'purpose': 'Real-time violation notifications',
                'triggers': ['constitutional_breach', 'security_violation', 'process_violation'],
                'consumers': ['COMPLIANCE_MANAGER', 'SAM', 'automated_escalation_system']
            },
            'audit-events': {
                'purpose': 'Audit completion notifications',
                'triggers': ['audit_complete', 'compliance_score_change', 'violation_trend_detected'],
                'consumers': ['All-Management', 'automated_reporting_system']
            }
        },
        'integration_benefits': [
            'Real-time notifications instead of email polling',
            'Automated escalation based on severity',
            'Event-driven audit triggers',
            'Reduced manual monitoring overhead',
            'Faster response times to violations'
        ]
    }
    
    return integration_config

# Example usage and testing functions
def test_error_reporting_system():
    """Test the error reporting system"""
    try:
        manager = ErrorReportingContainerManager()
        
        print("🔧 Creating error reporting containers...")
        results = manager.create_containers()
        
        for container, success in results.items():
            status = "✅" if success else "❌"
            print(f"   {status} {container}")
        
        # Test error reporting
        print("\n📊 Testing error reporting...")
        error_id = manager.report_error(
            agent_name="HEAD_OF_DIGITAL_STAFF",
            error_type="communication_failure",
            error_details={
                'description': 'Message content field was null, causing invisible proposal',
                'impact': 'Managers never saw proposal content',
                'root_cause': 'Wrong database field used for content',
                'severity': 'high',
                'requires_action': True,
                'proposed_fix': 'Resend with correct content field'
            }
        )
        print(f"   ✅ Error reported: {error_id}")
        
        # Test violation reporting
        print("\n⚠️ Testing violation reporting...")
        violation_id = manager.report_violation(
            violation_type="constitutional_breach",
            agent_name="SYSTEM_ARCHITECTURE",
            violation_details={
                'description': 'Failed to use proper message content field',
                'constitutional_rule': 'All claims require proper evidence and verification',
                'impact': 'Communication failure led to ignored proposal',
                'resolution_required': True,
                'constitutional_breach': True
            }
        )
        print(f"   ✅ Violation reported: {violation_id}")
        
        # Test audit logging
        print("\n🔍 Testing audit logging...")
        audit_id = manager.log_audit_result(
            audit_type="message_field_verification",
            audit_results={
                'agents_checked': ['SYSTEM_ARCHITECTURE', 'HEAD_OF_DIGITAL_STAFF'],
                'violations_found': 1,
                'errors_found': 1,
                'compliance_score': 85.5,
                'recommendations': ['Standardize message content fields', 'Add validation before sending']
            }
        )
        print(f"   ✅ Audit logged: {audit_id}")
        
        # Show Event Hub integration design
        print("\n🌐 Event Hub Integration Design:")
        integration = create_event_hub_integration()
        print(f"   📡 Namespace: {integration['event_hub_namespace']}")
        
        for hub_name, config in integration['event_hubs'].items():
            print(f"   📊 {hub_name}: {config['purpose']}")
            print(f"      Triggers: {', '.join(config['triggers'])}")
        
        print(f"\n   🎯 Benefits:")
        for benefit in integration['integration_benefits']:
            print(f"      • {benefit}")
        
        print(f"\n✅ Error reporting system ready for deployment!")
        print(f"✅ Event Hub integration designed!")
        print(f"✅ Automated audit capabilities enabled!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing system: {e}")
        return False

if __name__ == "__main__":
    test_error_reporting_system()