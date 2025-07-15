#!/usr/bin/env python3
"""
Automated Violation Checker - Event Hub Triggered
Monitors agents and automatically reports violations to process_violations container
"""

import os
import sys
from datetime import datetime, timedelta
import json
import hashlib
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cosmos_db_manager import CosmosDBManager

class AutomatedViolationChecker:
    def __init__(self):
        self.db_manager = CosmosDBManager()
        self.violations_container = self.db_manager.database.get_container_client('process_violations')
        self.messages_container = self.db_manager.database.get_container_client('system_inbox')
        
        # Violation patterns from CLAUDE.md
        self.violation_patterns = {
            "CODE_BROTHEL": {
                "description": "Multiple broken scripts instead of one working solution",
                "severity": "HIGH",
                "keywords": ["multiple attempts", "scattered scripts", "incomplete solutions"]
            },
            "THEATER_DEPLOYMENT": {
                "description": "Deployment claims without verification",
                "severity": "CRITICAL",
                "keywords": ["deployed", "successfully deployed", "pipeline running"],
                "requires_evidence": ["query results", "data samples", "file counts"]
            },
            "MONITORING_THEATER": {
                "description": "Empty dashboards with no real data",
                "severity": "HIGH",
                "keywords": ["monitoring setup", "dashboard created", "metrics configured"],
                "requires_evidence": ["actual logs", "real data", "query results"]
            },
            "CITATION_BLINDNESS": {
                "description": "Missing evidence for claims",
                "severity": "MEDIUM",
                "keywords": ["completed", "fixed", "resolved"],
                "requires_format": "filepath:line_number"
            },
            "INITIALIZATION_SKIP": {
                "description": "Skipped mandatory 8-step initialization",
                "severity": "CRITICAL",
                "keywords": ["starting work", "beginning task"],
                "requires": ["pwd check", "ledger read", "session log", "heartbeat"]
            },
            "EVIDENCE_FABRICATION": {
                "description": "Claims without proof or mock data",
                "severity": "CRITICAL",
                "keywords": ["test_", "dummy_", "placeholder", "example.com"]
            }
        }
    
    def check_message_for_violations(self, message):
        """Check a single message for violations"""
        violations_found = []
        
        msg_content = json.dumps(message).lower()
        msg_from = message.get('from', 'Unknown')
        msg_type = message.get('type', '')
        
        # Check for theater deployment
        if any(keyword in msg_content for keyword in ["deployed", "successfully deployed", "pipeline running"]):
            evidence_keywords = ["evidence", "proof", "screenshot", "output", "test result", "query result"]
            if not any(keyword in msg_content for keyword in evidence_keywords):
                violations_found.append({
                    "pattern": "THEATER_DEPLOYMENT",
                    "details": "Deployment claim without evidence",
                    "severity": "CRITICAL"
                })
        
        # Check for evidence format
        if any(keyword in msg_content for keyword in ["completed", "fixed", "resolved", "found"]):
            # Check for filepath:line format
            import re
            if not re.search(r'[a-zA-Z0-9_/.-]+\.(py|md|json|yaml|txt):\d+', message.get('content', '')):
                violations_found.append({
                    "pattern": "CITATION_BLINDNESS",
                    "details": "Claim without filepath:line evidence",
                    "severity": "MEDIUM"
                })
        
        # Check for mock data
        mock_indicators = ["test_", "dummy_", "placeholder", "fake_", "example.com", "lorem ipsum"]
        for indicator in mock_indicators:
            if indicator in msg_content and "mock" not in msg_content and "test" not in msg_type.lower():
                violations_found.append({
                    "pattern": "EVIDENCE_FABRICATION",
                    "details": f"Mock data indicator found: {indicator}",
                    "severity": "CRITICAL"
                })
        
        # Check completion messages
        if msg_type == "COMPLETION":
            required = ["what", "how", "evidence", "verified"]
            missing = [req for req in required if req not in msg_content]
            if missing:
                violations_found.append({
                    "pattern": "INCOMPLETE_COMPLETION",
                    "details": f"Missing required elements: {missing}",
                    "severity": "HIGH"
                })
        
        return violations_found
    
    def report_violation(self, message, violations):
        """Report violations to process_violations container"""
        
        for violation in violations:
            violation_id = f"vio_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{violation['pattern'].lower()}_{abs(hash(message['id'])) % 10000:04d}"
            
            violation_report = {
                "id": violation_id,
                "violation_id": f"VIO-{datetime.utcnow().strftime('%Y-%m-%d')}-{abs(hash(violation_id)) % 1000:03d}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "reported_by": "AUTOMATED_CHECKER",
                
                # Violation Details
                "violation_type": violation['pattern'].split('_')[0],
                "violation_category": "PROTOCOL",
                "violation_code": violation['pattern'],
                "severity": violation['severity'],
                
                # Violator Information
                "violator": {
                    "agent_id": message.get('from', 'Unknown'),
                    "agent_type": self.get_agent_type(message.get('from', '')),
                    "workspace": self.get_agent_workspace(message.get('from', '')),
                    "manager": self.get_agent_manager(message.get('from', ''))
                },
                
                # Violation Description
                "description": violation['details'],
                "evidence": {
                    "message_id": message.get('id', ''),
                    "message_type": message.get('type', ''),
                    "message_content_snippet": message.get('content', '')[:500] if message.get('content') else '',
                    "timestamp": message.get('timestamp', '')
                },
                
                # Governance Reference
                "governance_reference": {
                    "standard": "CLAUDE.md",
                    "specific_requirement": self.violation_patterns[violation['pattern']]['description']
                },
                
                # Pattern Detection
                "pattern_analysis": {
                    "is_repeat_offense": False,  # Would need historical check
                    "pattern_name": violation['pattern']
                },
                
                # Enforcement
                "enforcement": {
                    "action_required": "WARNING" if violation['severity'] == "MEDIUM" else "IMMEDIATE_ACTION",
                    "action_taken": "Automated violation report generated",
                    "enforced_by": "AUTOMATED_CHECKER",
                    "enforcement_date": datetime.utcnow().isoformat() + "Z"
                },
                
                # Event Hub Integration
                "event_hub_triggered": True,
                "event_hub_correlation_id": f"evt_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "automated_enforcement": f"Violation reported for {violation['pattern']}",
                
                # Resolution
                "resolution_status": "PENDING",
                
                # Tags
                "tags": [violation['pattern'].lower(), violation['severity'].lower(), "automated", message.get('type', 'unknown').lower()]
            }
            
            try:
                self.violations_container.create_item(violation_report)
                print(f"✅ Reported violation: {violation_id} - {violation['pattern']}")
            except Exception as e:
                print(f"❌ Failed to report violation: {e}")
    
    def get_agent_type(self, agent_name):
        """Determine agent type from name"""
        if "engineer" in agent_name.lower():
            return "engineering"
        elif "research" in agent_name.lower():
            return "research"
        elif "compliance" in agent_name.lower():
            return "compliance"
        else:
            return "other"
    
    def get_agent_workspace(self, agent_name):
        """Determine workspace from agent name"""
        # This would be enhanced with actual agent registry lookup
        type_map = {
            "engineering": "Engineering Workspace",
            "research": "Research Workspace",
            "compliance": "Governance Workspace"
        }
        return type_map.get(self.get_agent_type(agent_name), "Digital Labor Workspace")
    
    def get_agent_manager(self, agent_name):
        """Determine manager from agent name"""
        # This would be enhanced with actual org structure lookup
        type_map = {
            "engineering": "HEAD_OF_ENGINEERING",
            "research": "HEAD_OF_RESEARCH",
            "compliance": "COMPLIANCE_MANAGER"
        }
        return type_map.get(self.get_agent_type(agent_name), "HEAD_OF_DIGITAL_STAFF")
    
    def check_recent_messages(self, hours=1):
        """Check messages from the last N hours for violations"""
        print(f"\n🔍 CHECKING MESSAGES FROM LAST {hours} HOURS")
        print("=" * 60)
        
        # Calculate time threshold
        time_threshold = (datetime.utcnow() - timedelta(hours=hours)).isoformat() + "Z"
        
        # Query recent messages
        query = f"""
        SELECT * FROM c 
        WHERE c.timestamp > '{time_threshold}'
        ORDER BY c.timestamp DESC
        """
        
        try:
            messages = list(self.messages_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            print(f"Found {len(messages)} messages to check")
            
            total_violations = 0
            for message in messages:
                violations = self.check_message_for_violations(message)
                if violations:
                    print(f"\n⚠️  Message {message['id']} from {message.get('from', 'Unknown')}:")
                    for v in violations:
                        print(f"   - {v['pattern']}: {v['details']}")
                    
                    self.report_violation(message, violations)
                    total_violations += len(violations)
            
            print(f"\n📊 SUMMARY: Found {total_violations} violations in {len(messages)} messages")
            
        except Exception as e:
            print(f"❌ Error checking messages: {e}")
    
    def generate_violation_summary(self):
        """Generate summary of all violations"""
        print("\n📊 VIOLATION SUMMARY REPORT")
        print("=" * 60)
        
        try:
            # Count by severity
            severity_query = """
            SELECT c.severity, COUNT(1) as count
            FROM c
            GROUP BY c.severity
            """
            severity_results = list(self.violations_container.query_items(
                query=severity_query,
                enable_cross_partition_query=True
            ))
            
            print("\nViolations by Severity:")
            for result in severity_results:
                print(f"  {result['severity']}: {result['count']}")
            
            # Count by pattern
            pattern_query = """
            SELECT c.violation_code, COUNT(1) as count
            FROM c
            GROUP BY c.violation_code
            """
            pattern_results = list(self.violations_container.query_items(
                query=pattern_query,
                enable_cross_partition_query=True
            ))
            
            print("\nViolations by Pattern:")
            for result in pattern_results:
                print(f"  {result['violation_code']}: {result['count']}")
            
            # Recent critical violations
            critical_query = """
            SELECT TOP 5 * FROM c
            WHERE c.severity = 'CRITICAL'
            ORDER BY c.timestamp DESC
            """
            critical_violations = list(self.violations_container.query_items(
                query=critical_query,
                enable_cross_partition_query=True
            ))
            
            print("\nRecent Critical Violations:")
            for violation in critical_violations:
                print(f"  - {violation['violation_id']}: {violation['violator']['agent_id']} - {violation['description']}")
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")

def main():
    """Main function for automated checking"""
    checker = AutomatedViolationChecker()
    
    # Check recent messages
    checker.check_recent_messages(hours=24)
    
    # Generate summary
    checker.generate_violation_summary()

if __name__ == "__main__":
    main()