#!/usr/bin/env python3
"""
Query enforcement records from the database
"""

import os
import json
from datetime import datetime
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EnforcementQueryTool:
    """Tool for querying enforcement and compliance records"""
    
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
    
    def get_all_statistics(self):
        """Get all enforcement statistics"""
        query = """
        SELECT * FROM c 
        WHERE c.recordType = 'enforcement_statistic'
        ORDER BY c.numeric_value DESC
        """
        
        return list(self.container.query_items(
            query,
            enable_cross_partition_query=True
        ))
    
    def get_critical_statistics(self):
        """Get critical severity statistics"""
        query = """
        SELECT * FROM c 
        WHERE c.recordType = 'enforcement_statistic'
        AND c.severity = 'critical'
        ORDER BY c.numeric_value DESC
        """
        
        return list(self.container.query_items(
            query,
            enable_cross_partition_query=True
        ))
    
    def get_bugs_to_fix(self):
        """Get statistics that are bugs requiring fixes"""
        query = """
        SELECT * FROM c 
        WHERE c.recordType = 'enforcement_statistic'
        AND c.current_status = 'bug_to_fix'
        """
        
        return list(self.container.query_items(
            query,
            enable_cross_partition_query=True
        ))
    
    def get_patterns_to_track(self):
        """Get statistics that are patterns to monitor"""
        query = """
        SELECT * FROM c 
        WHERE c.recordType = 'enforcement_statistic'
        AND c.current_status = 'pattern_to_track'
        ORDER BY c.numeric_value DESC
        """
        
        return list(self.container.query_items(
            query,
            enable_cross_partition_query=True
        ))
    
    def get_by_category(self, category):
        """Get statistics by category"""
        query = """
        SELECT * FROM c 
        WHERE c.recordType = 'enforcement_statistic'
        AND c.category = @category
        """
        
        parameters = [{"name": "@category", "value": category}]
        
        return list(self.container.query_items(
            query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))

def format_record(record):
    """Format an enforcement record for display"""
    print(f"\n{'='*60}")
    print(f"Statistic: {record['statistic_name']}")
    print(f"Value: {record['statistic_value']} (Numeric: {record['numeric_value']})")
    print(f"Category: {record['category']}")
    print(f"Severity: {record['severity']}")
    print(f"Status: {record['current_status']}")
    print(f"Source: {record['source_document']}")
    print(f"Date Discovered: {record['date_discovered']}")
    print(f"\nContext: {record['context']}")
    print(f"Explanation: {record['explanation']}")
    
    if 'evidence_trail' in record:
        print(f"\nEvidence Trail:")
        for key, value in record['evidence_trail'].items():
            print(f"  - {key}: {value}")
    
    if 'breakdown_details' in record:
        print(f"\nBreakdown Details:")
        for key, value in record['breakdown_details'].items():
            print(f"  - {key}: {value}")
    
    if 'tags' in record:
        print(f"\nTags: {', '.join(record['tags'])}")

def main():
    """Run various queries to display enforcement records"""
    tool = EnforcementQueryTool()
    
    print("ENFORCEMENT RECORDS QUERY TOOL")
    print("=" * 60)
    
    # Show all statistics
    print("\n1. ALL ENFORCEMENT STATISTICS:")
    all_stats = tool.get_all_statistics()
    print(f"Found {len(all_stats)} enforcement statistics")
    
    for stat in all_stats:
        print(f"  - {stat['statistic_name']}: {stat['statistic_value']} [{stat['severity']}]")
    
    # Show critical issues
    print("\n2. CRITICAL SEVERITY ISSUES:")
    critical = tool.get_critical_statistics()
    for rec in critical:
        format_record(rec)
    
    # Show bugs to fix
    print("\n3. BUGS TO FIX:")
    bugs = tool.get_bugs_to_fix()
    print(f"Found {len(bugs)} bugs requiring fixes")
    for bug in bugs:
        print(f"  - {bug['statistic_name']}: {bug['statistic_value']}")
        print(f"    Context: {bug['context']}")
    
    # Show patterns to track
    print("\n4. PATTERNS TO TRACK:")
    patterns = tool.get_patterns_to_track()
    print(f"Found {len(patterns)} patterns to monitor")
    for pattern in patterns:
        print(f"  - {pattern['statistic_name']}: {pattern['statistic_value']}")
        print(f"    Source: {pattern['source_document']}")
    
    # Show by category
    print("\n5. STATISTICS BY CATEGORY:")
    categories = ['system_failure', 'compliance_failure', 'value_at_risk']
    for category in categories:
        cat_stats = tool.get_by_category(category)
        if cat_stats:
            print(f"\n  {category.upper()}:")
            for stat in cat_stats:
                print(f"    - {stat['statistic_name']}: {stat['statistic_value']}")

if __name__ == "__main__":
    main()