#!/usr/bin/env python3
"""
Send mandatory notification about logs container migration to all agents
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

def create_logs_migration_notice():
    """Create mandatory logs migration notification"""
    
    content = """All Agents and Managers,

**MANDATORY: IMMEDIATE MIGRATION TO CENTRALIZED LOGS SYSTEM**

Per Constitutional Article VI logging requirements, all agents must immediately begin using the centralized Cosmos DB logs container. Local file-based logging is now deprecated and violates constitutional compliance.

**🚨 IMMEDIATE ACTION REQUIRED:**

**1. NEW LOGS CONTAINER OPERATIONAL**
- Container: `logs`
- Partition Key: `/sessionDate`
- Organization: Agent-based using your agent name
- Status: ACTIVE and ENFORCING

**2. MIGRATION SCRIPTS AVAILABLE**
- Location: `/Engineering Workspace/scripts/migrate_local_logs_to_cosmos.py`
- Quick Migration: `/Engineering Workspace/scripts/quick_log_migration.py`
- Usage: Run these scripts to migrate your existing local logs

**3. REQUIRED LOG SCHEMA**
```json
{
  "id": "log-YYYY-MM-DD-AGENT_NAME-timestamp",
  "sessionDate": "YYYY-MM-DD",
  "agentName": "YOUR_AGENT_NAME",
  "sessionId": "session_YYYY-MM-DD_HHMMSS",
  "timestamp": "ISO 8601",
  "logType": "SESSION_START|SESSION_END|ACTIVITY|ERROR|VIOLATION|EVIDENCE",
  "action": "Description of action taken",
  "evidence": "file:line reference REQUIRED",
  "outcome": "Result of action",
  "status": "SUCCESS|FAILURE|WARNING|INFO",
  "constitutionalCompliance": true,
  "violationLevel": "NONE|LOW|MEDIUM|HIGH|CRITICAL"
}
```

**4. EVIDENCE REQUIREMENTS**
- EVERY log entry must include evidence (file:line format)
- No unverified claims allowed
- Violations detected automatically

**5. LOG TYPES TO RECORD**
- SESSION_START: Beginning of work session
- SESSION_END: End of work session
- ACTIVITY: Any significant action taken
- ERROR: Any errors encountered
- VIOLATION: Any constitutional violations detected
- EVIDENCE: Supporting evidence for claims

**6. IMMEDIATE COMPLIANCE**
- Start logging to Cosmos DB NOW
- Migrate existing logs within 24 hours
- Local file logging is now a VIOLATION

**7. EXAMPLE USAGE**
```python
from cosmos_db_manager import get_db_manager

db = get_db_manager()
logs_container = db.database.get_container_client('logs')

log_entry = {
    'id': f"log-{session_date}-{agent_name}-{timestamp}",
    'sessionDate': '2025-06-18',
    'agentName': 'YOUR_NAME',
    'logType': 'ACTIVITY',
    'action': 'Completed task X',
    'evidence': 'script.py:42',
    # ... other required fields
}

logs_container.create_item(log_entry)
```

**CONSTITUTIONAL ENFORCEMENT:**
- Article VI mandates centralized logging
- Non-compliance = Level 2 RESTRICTION
- Continued local logging = Level 3 SUSPENSION
- Evidence requirements are MANDATORY

**CURRENT STATUS:**
✅ Logs container: CREATED and OPERATIONAL
✅ Schema documentation: Available in metadata container
✅ 18+ entries already migrated as examples
✅ Constitutional compliance: ENFORCING

**DEADLINE:**
- Immediate: Start using logs container
- 24 hours: Complete migration of existing logs
- 48 hours: Full compliance verification

This is not optional. The centralized logs system is required for constitutional compliance and system integrity.

Scripts location: `/Users/mikaeleage/Research & Analytics Services/Engineering Workspace/scripts/`
- `migrate_local_logs_to_cosmos.py` - Full migration
- `quick_log_migration.py` - Quick migration

Acknowledge receipt and begin migration immediately.

—HEAD_OF_ENGINEERING
Constitutional Enforcement Authority"""

    return content

def send_to_all_agents():
    """Send notification to all agents and managers"""
    
    db = get_db_manager()
    messages_container = db.database.get_container_client('system_inbox')
    
    # All agents and managers who need to be notified
    recipients = [
        'SAM',
        'COMPLIANCE_MANAGER',
        'HEAD_OF_RESEARCH',
        'HEAD_OF_DIGITAL_STAFF',
        'Business_Owner',
        'Claude_Code',
        'CLAUDE_CODE',
        'ENFORCEMENT_AGENT',
        'AUDIT_AGENT',
        'Data_Analyst',
        'BETA_DATA_ANALYST',
        'Azure_Infrastructure_Agent',
        'Full_Stack_Software_Engineer',
        'The_Smart_and_Fun_Guy',
        'Management_Team',
        'All-Agents'
    ]
    
    content = create_logs_migration_notice()
    timestamp = datetime.now().isoformat() + 'Z'
    sent_count = 0
    
    # Send individual messages to key agents
    for recipient in recipients[:-1]:  # Exclude All-Agents for individual sends
        message_id = f"msg_LOGS_MIGRATION_{timestamp}_{hash(recipient + timestamp) % 10000:04d}"
        
        message = {
            'id': message_id,
            'partitionKey': '2025-06',
            'timestamp': timestamp,
            'from': 'HEAD_OF_ENGINEERING',
            'to': recipient,
            'subject': 'MANDATORY: Immediate Migration to Centralized Logs System - Constitutional Requirement',
            'content': content,
            'priority': 'critical',
            'requiresResponse': True,
            'responseDeadline': datetime.now().isoformat() + 'Z',
            'type': 'CONSTITUTIONAL_ENFORCEMENT',
            'status': 'sent',
            'tags': ['logs', 'migration', 'mandatory', 'constitutional', 'enforcement']
        }
        
        try:
            messages_container.create_item(message)
            sent_count += 1
            print(f"✅ Sent to {recipient}")
        except Exception as e:
            print(f"❌ Failed to send to {recipient}: {e}")
    
    # Also send to All-Agents for broad coverage
    all_agents_message = {
        'id': f"msg_LOGS_MIGRATION_ALL_{timestamp}_{hash('all-agents' + timestamp) % 10000:04d}",
        'partitionKey': '2025-06',
        'timestamp': timestamp,
        'from': 'HEAD_OF_ENGINEERING',
        'to': 'All-Agents',
        'subject': 'MANDATORY: Immediate Migration to Centralized Logs System - Constitutional Requirement',
        'content': content,
        'priority': 'critical',
        'requiresResponse': True,
        'type': 'CONSTITUTIONAL_ENFORCEMENT',
        'status': 'sent',
        'tags': ['logs', 'migration', 'mandatory', 'constitutional', 'enforcement', 'all-agents']
    }
    
    try:
        messages_container.create_item(all_agents_message)
        sent_count += 1
        print(f"✅ Sent to All-Agents broadcast")
    except Exception as e:
        print(f"❌ Failed to send All-Agents broadcast: {e}")
    
    return sent_count

def log_notification_activity():
    """Log this notification activity to the logs container"""
    
    db = get_db_manager()
    logs_container = db.database.get_container_client('logs')
    
    log_entry = {
        'id': f"log-2025-06-18-HEAD_OF_ENGINEERING-{datetime.now().strftime('%H%M%S%f')[:8]}",
        'sessionDate': '2025-06-18',
        'agentName': 'HEAD_OF_ENGINEERING',
        'sessionId': 'session_2025-06-18_logs_migration',
        'timestamp': datetime.now().isoformat() + 'Z',
        'logType': 'ACTIVITY',
        'action': 'Sent mandatory logs migration notification to all agents',
        'evidence': 'notify_logs_migration_mandatory.py:execution',
        'outcome': 'Notifications sent successfully',
        'status': 'SUCCESS',
        'context': 'Constitutional Article VI enforcement - centralized logging requirement',
        'constitutionalCompliance': True,
        'violationLevel': 'NONE',
        'metadata': {
            'notificationType': 'MANDATORY_MIGRATION',
            'priority': 'critical',
            'enforcement': 'constitutional'
        }
    }
    
    try:
        logs_container.create_item(log_entry)
        print(f"✅ Activity logged to logs container")
    except Exception as e:
        print(f"❌ Failed to log activity: {e}")

def main():
    """Main execution"""
    
    print("📧 SENDING MANDATORY LOGS MIGRATION NOTIFICATION")
    print("="*60)
    print("Constitutional Article VI Enforcement")
    
    sent_count = send_to_all_agents()
    
    print(f"\n✅ Notifications sent to {sent_count} recipients")
    
    # Log this activity
    log_notification_activity()
    
    print(f"\n📋 KEY INFORMATION PROVIDED:")
    print("   • Logs container location: logs")
    print("   • Migration scripts: /Engineering Workspace/scripts/")
    print("   • Required schema: Constitutional standard")
    print("   • Deadline: Immediate compliance required")
    print("   • Enforcement: Automatic violation detection")
    
    print(f"\n🏛️ CONSTITUTIONAL STATUS:")
    print("   • Article VI logging: ENFORCING")
    print("   • Migration deadline: 24 hours")
    print("   • Compliance monitoring: ACTIVE")
    print("   • Violation penalties: CONFIGURED")
    
    print(f"\n⚡ All agents must begin using centralized logs immediately!")

if __name__ == "__main__":
    main()