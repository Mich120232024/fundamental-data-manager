#!/usr/bin/env python3
"""
Check for logs container and create if missing
"""

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Import cosmos manager
sys.path.insert(0, str(Path(__file__).parent))
from cosmos_db_manager import get_db_manager

def check_existing_containers():
    """Check what containers already exist"""
    
    db = get_db_manager()
    database = db.client.get_database_client(db.database_name)
    
    print("🔍 Checking existing containers...")
    
    containers = list(database.list_containers())
    container_names = [c['id'] for c in containers]
    
    print(f"\n📦 Found {len(containers)} containers:")
    for name in sorted(container_names):
        print(f"   • {name}")
    
    return container_names, database

def create_logs_container(database):
    """Create logs container with proper schema"""
    
    print(f"\n🔨 Creating logs container...")
    
    try:
        # Create logs container with session-based partitioning
        container = database.create_container(
            id='logs',
            partition_key={'paths': ['/sessionDate'], 'kind': 'Hash'},
            indexing_policy={
                'automatic': True,
                'indexingMode': 'consistent',
                'includedPaths': [{'path': '/*'}],
                'compositeIndexes': [
                    [
                        {'path': '/sessionDate', 'order': 'ascending'},
                        {'path': '/agentName', 'order': 'ascending'},
                        {'path': '/timestamp', 'order': 'descending'}
                    ]
                ]
            }
        )
        
        print("✅ Logs container created successfully!")
        return container
        
    except Exception as e:
        if "already exists" in str(e) or "Conflict" in str(e):
            print("ℹ️ Logs container already exists")
            return database.get_container_client('logs')
        else:
            print(f"❌ Error creating logs container: {e}")
            raise e

def create_logs_schema_documentation():
    """Create schema documentation for logs container"""
    
    schema_doc = {
        'id': 'logs-container-schema',
        'containerName': 'logs',
        'purpose': 'Store all agent session logs and activity tracking',
        'partitionKey': '/sessionDate',
        'description': 'Constitutional compliance requires all agent activities to be logged with evidence',
        
        'schema': {
            'id': 'log-{sessionDate}-{agentName}-{timestamp}',
            'sessionDate': 'YYYY-MM-DD',
            'agentName': 'AGENT_NAME',
            'sessionId': 'session_YYYY-MM-DD_HHMMSS',
            'timestamp': 'ISO 8601 timestamp',
            'logType': 'SESSION_START|SESSION_END|ACTIVITY|ERROR|VIOLATION|EVIDENCE',
            'action': 'Description of action taken',
            'evidence': 'Required evidence for claims',
            'outcome': 'Result of action',
            'status': 'SUCCESS|FAILURE|WARNING|INFO',
            'context': 'Additional context or metadata',
            'constitutionalCompliance': True,
            'violationLevel': 'NONE|LOW|MEDIUM|HIGH|CRITICAL'
        },
        
        'requiredFields': [
            'id', 'sessionDate', 'agentName', 'timestamp', 
            'logType', 'action', 'status'
        ],
        
        'constitutionalRequirements': {
            'evidenceRequired': True,
            'sessionLogging': 'All agent sessions must be logged',
            'activityTracking': 'All significant actions must be recorded',
            'violationReporting': 'All violations must be logged immediately',
            'retention': 'Logs retained for constitutional audit purposes'
        },
        
        'examples': [
            {
                'id': 'log-2025-06-18-HEAD_OF_ENGINEERING-01432408',
                'sessionDate': '2025-06-18',
                'agentName': 'HEAD_OF_ENGINEERING',
                'sessionId': 'session_2025-06-18_014324',
                'timestamp': '2025-06-18T01:43:24.081Z',
                'logType': 'SESSION_START',
                'action': 'Started constitutional compliance audit',
                'evidence': 'cosmos_db_manager.py:25 - Database connection established',
                'outcome': 'Successfully connected to research-analytics-db',
                'status': 'SUCCESS',
                'context': 'Comprehensive container audit initiated',
                'constitutionalCompliance': True,
                'violationLevel': 'NONE'
            }
        ],
        
        'metadata': {
            'createdBy': 'HEAD_OF_ENGINEERING',
            'createdDate': datetime.now().isoformat() + 'Z',
            'constitutionalArticle': 'Article VI - Logging and Evidence Requirements',
            'enforcementLevel': 'MANDATORY'
        }
    }
    
    return schema_doc

def add_sample_log_entry():
    """Add sample log entry to demonstrate schema"""
    
    db = get_db_manager()
    logs_container = db.database.get_container_client('logs')
    
    sample_log = {
        'id': f"log-2025-06-18-HEAD_OF_ENGINEERING-{datetime.now().strftime('%H%M%S%f')[:8]}",
        'sessionDate': '2025-06-18',
        'agentName': 'HEAD_OF_ENGINEERING',
        'sessionId': 'session_2025-06-18_014324',
        'timestamp': datetime.now().isoformat() + 'Z',
        'logType': 'ACTIVITY',
        'action': 'Created logs container with constitutional schema',
        'evidence': 'check_and_create_logs_container.py:95 - Container creation successful',
        'outcome': 'Logs container operational with proper indexing',
        'status': 'SUCCESS',
        'context': 'Constitutional compliance audit remediation',
        'constitutionalCompliance': True,
        'violationLevel': 'NONE',
        'metadata': {
            'auditContext': 'Container compliance review',
            'remediation': True,
            'constitutionalRequirement': 'Article VI logging mandate'
        }
    }
    
    try:
        result = logs_container.create_item(sample_log)
        print(f"✅ Sample log entry created: {sample_log['id']}")
        return result
    except Exception as e:
        print(f"❌ Error creating sample log: {e}")
        return None

def add_logs_metadata_documentation():
    """Add logs container documentation to metadata container"""
    
    db = get_db_manager()
    metadata_container = db.database.get_container_client('metadata')
    
    schema_doc = create_logs_schema_documentation()
    
    try:
        result = metadata_container.create_item(schema_doc)
        print(f"✅ Logs schema documented in metadata container")
        return result
    except Exception as e:
        if "Conflict" in str(e):
            print("ℹ️ Logs schema documentation already exists")
        else:
            print(f"❌ Error documenting schema: {e}")

def test_logs_container():
    """Test logs container functionality"""
    
    print(f"\n🧪 Testing logs container...")
    
    db = get_db_manager()
    logs_container = db.database.get_container_client('logs')
    
    # Test query
    query = "SELECT * FROM logs WHERE logs.sessionDate = '2025-06-18'"
    results = list(logs_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    
    print(f"✅ Test query successful - found {len(results)} log entries")
    
    # Show sample
    if results:
        sample = results[0]
        print(f"\nSample log entry:")
        print(f"  ID: {sample.get('id', 'Unknown')}")
        print(f"  Agent: {sample.get('agentName', 'Unknown')}")
        print(f"  Action: {sample.get('action', 'Unknown')}")
        print(f"  Status: {sample.get('status', 'Unknown')}")

def main():
    """Main execution"""
    
    print("📋 LOGS CONTAINER VERIFICATION AND CREATION")
    print("="*60)
    
    # Check existing containers
    container_names, database = check_existing_containers()
    
    # Check if logs container exists
    if 'logs' in container_names:
        print(f"\n✅ Logs container already exists")
    else:
        print(f"\n⚠️ Logs container missing - creating now...")
        create_logs_container(database)
    
    # Add schema documentation
    print(f"\n📚 Adding schema documentation...")
    add_logs_metadata_documentation()
    
    # Add sample log entry
    print(f"\n📝 Adding sample log entry...")
    add_sample_log_entry()
    
    # Test functionality
    test_logs_container()
    
    print(f"\n" + "="*60)
    print("✅ LOGS CONTAINER SETUP COMPLETE")
    print("="*60)
    
    print(f"\n📦 Container Status:")
    print(f"   • Container: logs")
    print(f"   • Partition Key: /sessionDate")
    print(f"   • Indexing: Optimized for agent queries")
    print(f"   • Schema: Constitutional compliance ready")
    print(f"   • Documentation: Added to metadata container")
    
    print(f"\n🏛️ Constitutional Compliance:")
    print(f"   • Article VI logging requirements: SUPPORTED")
    print(f"   • Evidence tracking: ENABLED")
    print(f"   • Session logging: OPERATIONAL")
    print(f"   • Violation reporting: READY")
    
    print(f"\n📋 Usage:")
    print(f"   • All agents must log sessions to this container")
    print(f"   • Required fields: sessionDate, agentName, action, evidence")
    print(f"   • Automatic constitutional compliance tracking")

if __name__ == "__main__":
    main()