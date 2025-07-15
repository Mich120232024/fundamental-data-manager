#!/usr/bin/env python3
"""
Unified Message Query System
Solves email finding difficulties by handling both string and array recipient types

Purpose: Address the root cause of why scripts have difficulty finding emails
in the message container by providing unified query functions that handle
both string recipients ("AGENT_NAME") and array recipients (["AGENT1", "AGENT2"])
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from cosmos_db_manager import get_db_manager

class MessageStatus(Enum):
    """Message status requirements per Constitutional Framework Article III Section 2.1"""
    NEW = "NEW"
    PENDING = "PENDING"
    ANSWERED = "ANSWERED"
    BEING_PROCESSED = "BEING_PROCESSED"
    POSTPONED = "POSTPONED"

class UnifiedMessageQuery:
    """Unified query system that handles both string and array recipient types"""
    
    def __init__(self):
        """Initialize unified query system"""
        self.db = get_db_manager()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for query operations"""
        logger = logging.getLogger('UnifiedMessageQuery')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def find_messages_for_agent(self, agent_name: str, direction: str = "to", 
                               limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find messages for an agent using unified query that handles both string and array recipients
        
        Args:
            agent_name: Name of the agent to find messages for
            direction: "to", "from", or "both"
            limit: Maximum number of results (None for all)
            
        Returns:
            List of messages for the agent
        """
        try:
            # Build unified query that handles both string and array recipient types
            if direction == "to":
                query = """
                SELECT * FROM messages 
                WHERE (messages['to'] = @agent_name OR ARRAY_CONTAINS(messages['to'], @agent_name))
                """
            elif direction == "from":
                query = """
                SELECT * FROM messages 
                WHERE (messages['from'] = @agent_name OR ARRAY_CONTAINS(messages['from'], @agent_name))
                """
            else:  # both
                query = """
                SELECT * FROM messages 
                WHERE (messages['from'] = @agent_name OR ARRAY_CONTAINS(messages['from'], @agent_name))
                   OR (messages['to'] = @agent_name OR ARRAY_CONTAINS(messages['to'], @agent_name))
                """
            
            # Add ordering and limit
            query += " ORDER BY messages.timestamp DESC"
            if limit:
                query += f" OFFSET 0 LIMIT {limit}"
            
            parameters = [{"name": "@agent_name", "value": agent_name}]
            results = self.db.query_messages(query, parameters)
            
            self.logger.info(f"✅ Found {len(results)} messages for {agent_name} (direction: {direction})")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to find messages for {agent_name}: {str(e)}")
            return []
    
    def find_messages_for_group(self, group_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find messages sent to a group (like Management_Team, All-Agents)
        
        Args:
            group_name: Name of the group to find messages for
            limit: Maximum number of results
            
        Returns:
            List of messages sent to the group
        """
        try:
            query = """
            SELECT * FROM messages 
            WHERE (messages['to'] = @group_name OR ARRAY_CONTAINS(messages['to'], @group_name))
            ORDER BY messages.timestamp DESC
            """
            
            if limit:
                query += f" OFFSET 0 LIMIT {limit}"
            
            parameters = [{"name": "@group_name", "value": group_name}]
            results = self.db.query_messages(query, parameters)
            
            self.logger.info(f"✅ Found {len(results)} messages for group {group_name}")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to find messages for group {group_name}: {str(e)}")
            return []
    
    def analyze_recipient_types(self, limit: int = 100) -> Dict[str, Any]:
        """
        Analyze the recipient type patterns in the message container
        
        Args:
            limit: Number of recent messages to analyze
            
        Returns:
            Analysis of recipient type patterns
        """
        try:
            # Get recent messages with recipient information
            query = f"""
            SELECT messages['to'] as to_field, messages.id, messages.subject
            FROM messages 
            ORDER BY messages.timestamp DESC 
            OFFSET 0 LIMIT {limit}
            """
            
            results = self.db.query_messages(query)
            
            analysis = {
                'total_analyzed': len(results),
                'string_recipients': 0,
                'array_recipients': 0,
                'null_recipients': 0,
                'examples': {
                    'string': [],
                    'array': [],
                    'null': []
                }
            }
            
            for msg in results:
                to_field = msg.get('to_field')
                example = {
                    'id': msg.get('id', 'N/A'),
                    'subject': msg.get('subject', 'N/A')[:50],
                    'to_value': to_field
                }
                
                if to_field is None:
                    analysis['null_recipients'] += 1
                    if len(analysis['examples']['null']) < 3:
                        analysis['examples']['null'].append(example)
                elif isinstance(to_field, list):
                    analysis['array_recipients'] += 1
                    if len(analysis['examples']['array']) < 3:
                        analysis['examples']['array'].append(example)
                else:
                    analysis['string_recipients'] += 1
                    if len(analysis['examples']['string']) < 3:
                        analysis['examples']['string'].append(example)
            
            # Calculate percentages
            total = analysis['total_analyzed']
            if total > 0:
                analysis['percentages'] = {
                    'string': (analysis['string_recipients'] / total) * 100,
                    'array': (analysis['array_recipients'] / total) * 100,
                    'null': (analysis['null_recipients'] / total) * 100
                }
            
            self.logger.info(f"✅ Analyzed {total} messages for recipient types")
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze recipient types: {str(e)}")
            return {'error': str(e)}
    
    def test_query_patterns(self, agent_name: str = "HEAD_OF_DIGITAL_STAFF") -> Dict[str, Any]:
        """
        Test different query patterns to verify they work correctly
        
        Args:
            agent_name: Agent name to test queries with
            
        Returns:
            Test results for different query patterns
        """
        try:
            test_results = {}
            
            # Test 1: String-only query
            query1 = "SELECT * FROM messages WHERE messages['to'] = @agent"
            params1 = [{"name": "@agent", "value": agent_name}]
            results1 = self.db.query_messages(query1, params1)
            test_results['string_only'] = len(results1)
            
            # Test 2: Array-only query
            query2 = "SELECT * FROM messages WHERE ARRAY_CONTAINS(messages['to'], @agent)"
            params2 = [{"name": "@agent", "value": agent_name}]
            results2 = self.db.query_messages(query2, params2)
            test_results['array_only'] = len(results2)
            
            # Test 3: Unified query (our solution)
            query3 = """
            SELECT * FROM messages 
            WHERE (messages['to'] = @agent OR ARRAY_CONTAINS(messages['to'], @agent))
            """
            params3 = [{"name": "@agent", "value": agent_name}]
            results3 = self.db.query_messages(query3, params3)
            test_results['unified'] = len(results3)
            
            # Test 4: Check for duplicates in unified query
            unique_ids = set()
            duplicates = 0
            for msg in results3:
                msg_id = msg.get('id')
                if msg_id in unique_ids:
                    duplicates += 1
                else:
                    unique_ids.add(msg_id)
            
            test_results['duplicates_found'] = duplicates
            test_results['unique_messages'] = len(unique_ids)
            
            # Verification: unified should equal or exceed individual queries
            test_results['verification'] = {
                'unified_ge_string': test_results['unified'] >= test_results['string_only'],
                'unified_ge_array': test_results['unified'] >= test_results['array_only'],
                'no_duplicates': test_results['duplicates_found'] == 0
            }
            
            self.logger.info(f"✅ Query pattern testing complete for {agent_name}")
            return test_results
            
        except Exception as e:
            self.logger.error(f"❌ Query pattern testing failed: {str(e)}")
            return {'error': str(e)}
    
    def update_message_status(self, message_id: str, partition_key: str, 
                            new_status: MessageStatus, reason: Optional[str] = None) -> bool:
        """
        Update message status per Constitutional requirement Article III Section 2.1
        
        Args:
            message_id: Message ID to update
            partition_key: Message partition key
            new_status: New status from MessageStatus enum
            reason: Required for POSTPONED status
            
        Returns:
            Success/failure boolean
        """
        try:
            # Get current message
            message = self.db.get_message(message_id, partition_key)
            if not message:
                self.logger.error(f"Message {message_id} not found")
                return False
            
            # Validate POSTPONED requires reason
            if new_status == MessageStatus.POSTPONED and not reason:
                self.logger.error("POSTPONED status requires reason per Constitutional requirement")
                return False
            
            # Build status update
            status_update = {
                'status': new_status.value,
                'timestamp': datetime.now().isoformat() + 'Z',
                'agent': 'HEAD_OF_DIGITAL_STAFF'
            }
            
            if reason:
                status_update['reason'] = reason
            
            # Update status history
            status_history = message.get('status_history', [])
            status_history.append(status_update)
            
            # Update message
            updates = {
                'status': new_status.value,
                'status_history': status_history,
                'last_status_update': datetime.now().isoformat() + 'Z'
            }
            
            self.db.update_message(message_id, partition_key, updates)
            self.logger.info(f"✅ Updated message {message_id} status to {new_status.value}")
            
            # TODO: Fire Event Hub notification for status change
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update status: {str(e)}")
            return False
    
    def find_messages_by_status(self, status: MessageStatus, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Find all messages with specific status
        
        Args:
            status: MessageStatus to search for
            limit: Maximum results
            
        Returns:
            List of messages with given status
        """
        try:
            query = f"""
            SELECT * FROM messages 
            WHERE messages.status = @status
            ORDER BY messages.timestamp DESC
            OFFSET 0 LIMIT {limit}
            """
            
            parameters = [{"name": "@status", "value": status.value}]
            results = self.db.query_messages(query, parameters)
            
            self.logger.info(f"✅ Found {len(results)} messages with status {status.value}")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to find messages by status: {str(e)}")
            return []
    
    def find_stale_messages(self, hours: int = 48) -> List[Dict[str, Any]]:
        """
        Find messages that haven't been updated in specified hours
        Per Constitutional requirement for stale message alerts
        
        Args:
            hours: Hours since last update (default 48)
            
        Returns:
            List of stale messages needing attention
        """
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            query = f"""
            SELECT * FROM messages 
            WHERE (messages.status = 'NEW' OR messages.status = 'PENDING')
            AND messages.timestamp < '{cutoff.isoformat()}Z'
            ORDER BY messages.timestamp ASC
            """
            
            results = self.db.query_messages(query)
            
            if results:
                self.logger.warning(f"⚠️ Found {len(results)} stale messages older than {hours} hours")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to find stale messages: {str(e)}")
            return []

def get_unified_query_manager() -> UnifiedMessageQuery:
    """Get a unified query manager instance"""
    return UnifiedMessageQuery()

def find_all_agent_messages(agent_name: str, direction: str = "to", limit: int = 20) -> List[Dict[str, Any]]:
    """
    Convenience function to find messages for an agent using unified query
    
    This is the main function agents should use instead of the old get_messages_by_agent
    """
    query_manager = get_unified_query_manager()
    return query_manager.find_messages_for_agent(agent_name, direction, limit)

def demonstrate_solution():
    """Demonstrate the unified query solution with Constitutional message status"""
    print("🔍 UNIFIED MESSAGE QUERY SOLUTION WITH CONSTITUTIONAL STATUS TRACKING")
    print("=" * 70)
    
    query_manager = UnifiedMessageQuery()
    
    # Analyze current recipient type patterns
    print("\n📊 ANALYZING RECIPIENT TYPE PATTERNS:")
    print("-" * 50)
    
    analysis = query_manager.analyze_recipient_types(50)
    if 'error' not in analysis:
        total = analysis['total_analyzed']
        print(f"📈 Analysis of {total} recent messages:")
        print(f"   String recipients: {analysis['string_recipients']} ({analysis.get('percentages', {}).get('string', 0):.1f}%)")
        print(f"   Array recipients: {analysis['array_recipients']} ({analysis.get('percentages', {}).get('array', 0):.1f}%)")
        print(f"   Null recipients: {analysis['null_recipients']} ({analysis.get('percentages', {}).get('null', 0):.1f}%)")
        
        print("\n📝 Examples:")
        for recipient_type, examples in analysis['examples'].items():
            if examples:
                print(f"   {recipient_type.upper()} recipients:")
                for example in examples:
                    print(f"      • {example['id']}: {example['subject']}")
    
    # Test query patterns
    print("\n🧪 TESTING QUERY PATTERNS:")
    print("-" * 50)
    
    test_results = query_manager.test_query_patterns("HEAD_OF_DIGITAL_STAFF")
    if 'error' not in test_results:
        print(f"📊 Query Results for HEAD_OF_DIGITAL_STAFF:")
        print(f"   String-only query: {test_results['string_only']} messages")
        print(f"   Array-only query: {test_results['array_only']} messages")
        print(f"   Unified query: {test_results['unified']} messages")
        print(f"   Duplicates found: {test_results['duplicates_found']}")
        
        print(f"\n✅ Verification:")
        for check, passed in test_results['verification'].items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}: {passed}")
    
    # Demonstrate group message finding
    print("\n📧 TESTING GROUP MESSAGE FINDING:")
    print("-" * 50)
    
    group_messages = query_manager.find_messages_for_group("Management_Team", 5)
    print(f"📬 Found {len(group_messages)} messages for Management_Team")
    
    for msg in group_messages[:3]:
        print(f"   • {msg.get('id', 'N/A')}: {msg.get('subject', 'N/A')[:50]}")
    
    # Show the solution
    # Demonstrate message status tracking
    print("\n📋 TESTING MESSAGE STATUS TRACKING (Constitutional Requirement):")
    print("-" * 50)
    
    # Find messages without status (Constitutional violation)
    print("\n🚨 Checking for messages without status (VIOLATION):")
    # Use a different approach due to Cosmos DB client limitations
    all_msgs_query = "SELECT messages.id, messages.status FROM messages OFFSET 0 LIMIT 100"
    all_results = query_manager.db.query_messages(all_msgs_query)
    no_status_count = sum(1 for msg in all_results if not msg.get('status'))
    print(f"   ⚠️ Found {no_status_count} messages without status out of 100 checked!")
    
    # Test status update functionality
    print("\n✅ Testing status update functionality:")
    recent_messages = query_manager.db.get_recent_messages(1)
    if recent_messages:
        test_msg = recent_messages[0]
        print(f"   Test message: {test_msg.get('id')}")
        print(f"   Current status: {test_msg.get('status', 'NONE')}")
        
        # Update to BEING_PROCESSED
        success = query_manager.update_message_status(
            test_msg['id'], 
            test_msg['partitionKey'],
            MessageStatus.BEING_PROCESSED
        )
        print(f"   Update to BEING_PROCESSED: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Check for stale messages
    print("\n⏰ Checking for stale messages (>48 hours):")
    stale_messages = query_manager.find_stale_messages(48)
    print(f"   Found {len(stale_messages)} stale messages requiring attention")
    
    print("\n💡 THE COMPLETE SOLUTION:")
    print("-" * 50)
    print("1. UNIFIED QUERY: Handles both string and array recipients")
    print("   ✅ WHERE (messages['to'] = @agent OR ARRAY_CONTAINS(messages['to'], @agent))")
    print()
    print("2. STATUS TRACKING: Constitutional Article III Section 2.1 compliance")
    print("   ✅ NEW, PENDING, ANSWERED, BEING_PROCESSED, POSTPONED")
    print("   ✅ Status history with timestamps and agent tracking")
    print("   ✅ Stale message detection after 48 hours")
    print()
    print("This solves both the invisible message problem AND ensures Constitutional compliance!")
    
    return True

if __name__ == "__main__":
    demonstrate_solution()