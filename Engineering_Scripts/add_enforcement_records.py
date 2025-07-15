#!/usr/bin/env python3
"""
Add verified statistics to enforcement records database
"""

import os
import json
import logging
from datetime import datetime
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EnforcementRecorder:
    """Manager for enforcement and compliance records"""
    
    def __init__(self):
        """Initialize with enforcement container"""
        self.endpoint = os.getenv('COSMOS_ENDPOINT')
        self.key = os.getenv('COSMOS_KEY')
        self.database_name = os.getenv('COSMOS_DATABASE', 'research-analytics-db')
        
        if not self.endpoint or not self.key:
            raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY must be set in .env file")
        
        # Initialize client
        self.client = CosmosClient(self.endpoint, self.key)
        self.database = self.client.get_database_client(self.database_name)
        self.container = self.database.get_container_client('enforcement')
        
        # Setup logging
        self.logger = logging.getLogger('EnforcementRecorder')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def add_enforcement_record(self, record_data):
        """Add an enforcement record to the database"""
        try:
            # Ensure required fields
            if 'id' not in record_data:
                record_data['id'] = f"enf_{datetime.now().isoformat()}_{hash(str(record_data)) % 10000:04d}"
            
            if 'partitionKey' not in record_data:
                record_data['partitionKey'] = datetime.now().strftime('%Y-%m')
            
            # Add metadata
            record_data['createdDate'] = datetime.now().isoformat() + 'Z'
            record_data['recordType'] = 'enforcement_statistic'
            
            # Store in database
            result = self.container.create_item(record_data)
            self.logger.info(f"Enforcement record stored: {result['id']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to store enforcement record: {str(e)}")
            raise

def main():
    """Add the verified statistics as enforcement records"""
    recorder = EnforcementRecorder()
    
    # Record 1: Message failure rate
    message_failure_record = {
        'statistic_name': 'Multi-box Architecture Message Failure Rate',
        'statistic_value': '40%',
        'numeric_value': 0.40,
        'category': 'system_failure',
        'source_document': 'SAM message 2025-06-20',
        'source_type': 'agent_message',
        'date_discovered': '2025-06-20',
        'context': 'Architecture bug causing 40% message failure rate in multi-box system',
        'explanation': 'SAM discovered that the multi-box architecture has a bug where 40% of messages fail delivery between system components',
        'current_status': 'bug_to_fix',
        'severity': 'critical',
        'evidence_trail': {
            'reported_by': 'SAM',
            'message_date': '2025-06-20',
            'discovery_context': 'System monitoring and analysis'
        },
        'tags': ['architecture', 'bug', 'message-delivery', 'critical-failure']
    }
    
    # Record 2: Governance methods adoption rate
    governance_adoption_record = {
        'statistic_name': 'Governance Methods Adoption Rate',
        'statistic_value': '6.7%',
        'numeric_value': 0.067,
        'category': 'compliance_failure',
        'source_document': 'COMPLIANCE_MANAGER Conference Analysis 2025-06-15',
        'source_type': 'conference_analysis',
        'date_discovered': '2025-06-15',
        'context': 'Only 6.7% of agents have adopted mandatory governance methods',
        'explanation': 'COMPLIANCE_MANAGER analyzed conference materials and discovered extremely low adoption rate of required governance patterns',
        'current_status': 'pattern_to_track',
        'severity': 'critical',
        'evidence_trail': {
            'reported_by': 'COMPLIANCE_MANAGER',
            'analysis_date': '2025-06-15',
            'data_source': 'Conference materials analysis',
            'methodology': 'Pattern recognition and adoption tracking'
        },
        'tags': ['governance', 'compliance', 'adoption-failure', 'critical']
    }
    
    # Record 3: Blocked value breakdown
    blocked_value_record = {
        'statistic_name': 'Blocked Enterprise Value',
        'statistic_value': '$2.5M',
        'numeric_value': 2500000,
        'category': 'value_at_risk',
        'source_document': 'COMPLIANCE_MANAGER Conference Analysis 2025-06-15',
        'source_type': 'conference_analysis',
        'date_discovered': '2025-06-15',
        'context': 'Total enterprise value blocked due to governance failures',
        'explanation': 'COMPLIANCE_MANAGER identified $2.5M in enterprise value blocked by governance adoption failures',
        'current_status': 'pattern_to_track',
        'severity': 'critical',
        'evidence_trail': {
            'reported_by': 'COMPLIANCE_MANAGER',
            'analysis_date': '2025-06-15',
            'calculation_method': 'Enterprise value assessment',
            'breakdown': 'Value blocked due to inability to deploy governance-compliant solutions'
        },
        'breakdown_details': {
            'deployment_failures': 'Projects unable to deploy due to governance violations',
            'rework_costs': 'Cost of fixing non-compliant implementations',
            'opportunity_cost': 'Lost value from delayed implementations'
        },
        'tags': ['value-at-risk', 'governance', 'financial-impact', 'critical']
    }
    
    # Add all records
    records = [
        message_failure_record,
        governance_adoption_record,
        blocked_value_record
    ]
    
    for record in records:
        try:
            result = recorder.add_enforcement_record(record)
            print(f"✓ Added enforcement record: {record['statistic_name']}")
            print(f"  - ID: {result['id']}")
            print(f"  - Value: {record['statistic_value']}")
            print(f"  - Source: {record['source_document']}")
            print()
        except Exception as e:
            print(f"✗ Failed to add record {record['statistic_name']}: {str(e)}")
            print()
    
    # Verify records were added
    print("\nVerifying enforcement records...")
    try:
        query = """
        SELECT * FROM c 
        WHERE c.recordType = 'enforcement_statistic' 
        AND c.date_discovered >= '2025-06-15'
        ORDER BY c.createdDate DESC
        """
        
        results = list(recorder.container.query_items(
            query,
            enable_cross_partition_query=True
        ))
        
        print(f"Found {len(results)} enforcement statistic records:")
        for rec in results:
            print(f"  - {rec['statistic_name']}: {rec['statistic_value']} (Status: {rec['current_status']})")
            
    except Exception as e:
        print(f"Error verifying records: {str(e)}")

if __name__ == "__main__":
    main()