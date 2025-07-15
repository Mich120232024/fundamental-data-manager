#!/usr/bin/env python3
"""
Message Schema Validator - Enforces Unified Constitutional Framework v2.0
Validates all messages against mandatory schema requirements
"""

from cosmos_db_manager import get_db_manager
from datetime import datetime, timedelta
import json
import uuid

class MessageSchemaValidator:
    """Validates messages against constitutional requirements"""
    
    REQUIRED_FIELDS = [
        'id', 'type', 'from', 'to', 'subject', 'content', 
        'priority', 'status', 'requires_response', 'metadata'
    ]
    
    VALID_TYPES = ['request', 'response', 'notification', 'escalation']
    VALID_PRIORITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    VALID_STATUSES = ['pending', 'acknowledged', 'in_progress', 'resolved', 'escalated']
    
    BANNED_PHRASES = [
        "it appears that",
        "approximately",
        "successfully deployed",
        "should be working",
        "i believe",
        "seems to be",
        "probably"
    ]
    
    def __init__(self):
        self.db = get_db_manager()
        self.enforcement_container = self.db.database.get_container_client('enforcement')
    
    def validate_message(self, message):
        """Validate a message against schema requirements"""
        violations = []
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in message:
                violations.append({
                    'type': 'missing_field',
                    'field': field,
                    'severity': 'HIGH'
                })
        
        # Validate specific fields if present
        if 'type' in message and message['type'] not in self.VALID_TYPES:
            violations.append({
                'type': 'invalid_value',
                'field': 'type',
                'value': message['type'],
                'valid_values': self.VALID_TYPES,
                'severity': 'MEDIUM'
            })
        
        if 'priority' in message and message['priority'] not in self.VALID_PRIORITIES:
            violations.append({
                'type': 'invalid_value',
                'field': 'priority',
                'value': message['priority'],
                'valid_values': self.VALID_PRIORITIES,
                'severity': 'MEDIUM'
            })
        
        if 'status' in message and message['status'] not in self.VALID_STATUSES:
            violations.append({
                'type': 'invalid_value',
                'field': 'status',
                'value': message['status'],
                'valid_values': self.VALID_STATUSES,
                'severity': 'MEDIUM'
            })
        
        # Check for wrong field names
        if 'body' in message:
            violations.append({
                'type': 'wrong_field_name',
                'field': 'body',
                'correct_field': 'content',
                'severity': 'CRITICAL',
                'description': 'Using "body" instead of "content" makes messages invisible!'
            })
        
        # Check content requirements
        if 'content' in message:
            content = str(message['content']).lower()
            
            # Check for banned phrases
            for phrase in self.BANNED_PHRASES:
                if phrase in content:
                    violations.append({
                        'type': 'banned_phrase',
                        'phrase': phrase,
                        'severity': 'HIGH',
                        'description': 'Claims without evidence detected'
                    })
            
            # Check for evidence when making claims
            if any(word in content for word in ['successfully', 'completed', 'fixed', 'deployed']):
                if 'evidence' not in message or not message['evidence']:
                    violations.append({
                        'type': 'missing_evidence',
                        'severity': 'CRITICAL',
                        'description': 'Success claims require evidence'
                    })
        
        # Check recipient array
        if 'to' in message:
            if not isinstance(message['to'], list):
                violations.append({
                    'type': 'invalid_format',
                    'field': 'to',
                    'severity': 'HIGH',
                    'description': 'Recipients must be an array'
                })
            elif len(message['to']) == 0:
                violations.append({
                    'type': 'empty_recipients',
                    'severity': 'CRITICAL',
                    'description': 'Message has no recipients'
                })
        
        # Check metadata structure
        if 'metadata' in message:
            required_metadata = ['created_at']
            for field in required_metadata:
                if field not in message['metadata']:
                    violations.append({
                        'type': 'missing_metadata',
                        'field': field,
                        'severity': 'MEDIUM'
                    })
        
        return violations
    
    def record_violation(self, agent_id, message_id, violations):
        """Record violations in enforcement container"""
        
        violation_record = {
            'id': f"VIO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{agent_id}",
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat() + 'Z',
            'violation_type': 'schema',
            'severity': self._calculate_severity(violations),
            'description': 'Message schema violations detected',
            'evidence': {
                'message_id': message_id,
                'container': 'messages',
                'violations': violations
            },
            'penalty_level': self._determine_penalty_level(agent_id),
            'corrective_action_required': 'Fix message schema and resubmit',
            'deadline': (datetime.now() + timedelta(hours=24)).isoformat() + 'Z',
            'status': 'active'
        }
        
        try:
            self.enforcement_container.create_item(body=violation_record)
            print(f"⚠️  Violation recorded: {violation_record['id']}")
            return violation_record
        except Exception as e:
            print(f"❌ Error recording violation: {e}")
            return None
    
    def _calculate_severity(self, violations):
        """Calculate overall severity from violations"""
        severities = [v['severity'] for v in violations]
        if 'CRITICAL' in severities:
            return 'CRITICAL'
        elif 'HIGH' in severities:
            return 'HIGH'
        elif 'MEDIUM' in severities:
            return 'MEDIUM'
        return 'LOW'
    
    def _determine_penalty_level(self, agent_id):
        """Determine penalty level based on violation history"""
        try:
            # Query agent's violation history
            query = f"SELECT * FROM c WHERE c.agent_id = '{agent_id}' AND c.status = 'active'"
            violations = list(self.enforcement_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            active_violations = len(violations)
            if active_violations == 0:
                return 1  # First offense
            elif active_violations == 1:
                return 2  # Second offense
            elif active_violations == 2:
                return 3  # Third offense
            else:
                return 4  # Fourth+ offense
                
        except:
            return 1  # Default to warning
    
    def validate_batch(self, limit=100):
        """Validate recent messages in batch"""
        
        print("\n🔍 MESSAGE SCHEMA VALIDATION")
        print("=" * 60)
        
        # Get recent messages
        query = f"""
        SELECT TOP {limit} * FROM messages 
        WHERE messages.timestamp >= '{(datetime.now() - timedelta(days=1)).isoformat()}Z'
        ORDER BY messages.timestamp DESC
        """
        
        results = self.db.query_messages(query)
        
        valid_count = 0
        invalid_count = 0
        violations_by_agent = {}
        
        for message in results:
            violations = self.validate_message(message)
            
            if violations:
                invalid_count += 1
                agent_id = message.get('from', 'UNKNOWN')
                
                if agent_id not in violations_by_agent:
                    violations_by_agent[agent_id] = []
                violations_by_agent[agent_id].extend(violations)
                
                print(f"\n❌ Invalid message: {message.get('id', 'NO_ID')}")
                print(f"   From: {agent_id}")
                print(f"   Violations: {len(violations)}")
                for v in violations:
                    print(f"   - {v['type']}: {v.get('description', v.get('field', ''))}")
            else:
                valid_count += 1
        
        # Summary
        print(f"\n📊 VALIDATION SUMMARY")
        print(f"   Total messages checked: {len(results)}")
        print(f"   Valid messages: {valid_count}")
        print(f"   Invalid messages: {invalid_count}")
        print(f"   Compliance rate: {(valid_count/len(results)*100):.1f}%" if results else "N/A")
        
        # Record violations
        if violations_by_agent:
            print(f"\n⚠️  RECORDING VIOLATIONS")
            for agent_id, agent_violations in violations_by_agent.items():
                self.record_violation(agent_id, "BATCH_VALIDATION", agent_violations)
        
        return valid_count, invalid_count

def main():
    """Run message schema validation"""
    
    validator = MessageSchemaValidator()
    
    # Validate recent messages
    valid, invalid = validator.validate_batch(limit=50)
    
    print("\n🏛️ CONSTITUTIONAL ENFORCEMENT ACTIVE")
    print("All future messages will be validated against schema requirements.")
    print("Violations will be automatically recorded and penalties applied.")

if __name__ == "__main__":
    main()