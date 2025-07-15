#!/usr/bin/env python3
"""
Comprehensive Message Schema Investigation Script

Purpose: Identify and analyze all schema inconsistencies in the Cosmos DB message container
that might cause agents to miss their inbox messages.

This script will:
1. Analyze the current message schema variations
2. Check for all field variations (to, to_agent, recipient, etc.)
3. Test different query patterns to see what works and what fails
4. Identify schema inconsistencies that might cause discovery issues
5. Check if agents are using correct field names
6. Provide specific examples of messages that might be missed
7. Recommend schema standardization if needed
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict, Counter
from cosmos_db_manager import get_db_manager

class MessageSchemaInvestigator:
    """Comprehensive investigation of message schema issues"""
    
    def __init__(self):
        """Initialize the investigator"""
        self.db = get_db_manager()
        self.logger = self._setup_logger()
        self.findings = {
            'schema_variations': {},
            'field_inconsistencies': {},
            'query_failures': [],
            'missed_messages': [],
            'recommendations': []
        }
        
    def _setup_logger(self) -> logging.Logger:
        """Setup detailed logging"""
        logger = logging.getLogger('MessageSchemaInvestigator')
        logger.setLevel(logging.DEBUG)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def investigate_all_issues(self):
        """Run complete investigation"""
        self.logger.info("🔍 Starting Comprehensive Message Schema Investigation")
        self.logger.info("=" * 80)
        
        # Step 1: Analyze schema variations
        self._analyze_schema_variations()
        
        # Step 2: Check field name variations
        self._check_field_variations()
        
        # Step 3: Test query patterns
        self._test_query_patterns()
        
        # Step 4: Identify potential missed messages
        self._identify_missed_messages()
        
        # Step 5: Check agent usage patterns
        self._check_agent_usage_patterns()
        
        # Step 6: Generate recommendations
        self._generate_recommendations()
        
        # Step 7: Create detailed report
        self._create_investigation_report()
        
        return self.findings
    
    def _analyze_schema_variations(self):
        """Analyze all schema variations in the message container"""
        self.logger.info("\n📊 ANALYZING SCHEMA VARIATIONS")
        self.logger.info("-" * 50)
        
        try:
            # Get sample of messages to analyze schemas
            query = "SELECT * FROM messages ORDER BY messages.timestamp DESC OFFSET 0 LIMIT 500"
            messages = self.db.query_messages(query)
            
            self.logger.info(f"Analyzing {len(messages)} messages for schema patterns...")
            
            # Track all unique field combinations
            schema_patterns = defaultdict(list)
            field_frequency = Counter()
            field_type_variations = defaultdict(lambda: defaultdict(int))
            
            for msg in messages:
                # Get all fields in this message
                fields = set(msg.keys())
                field_pattern = tuple(sorted(fields))
                schema_patterns[field_pattern].append(msg['id'])
                
                # Track field frequency and types
                for field, value in msg.items():
                    field_frequency[field] += 1
                    value_type = type(value).__name__
                    field_type_variations[field][value_type] += 1
            
            # Analyze results
            self.findings['schema_variations'] = {
                'total_messages_analyzed': len(messages),
                'unique_schemas': len(schema_patterns),
                'schema_patterns': {},
                'field_frequency': dict(field_frequency),
                'field_type_variations': dict(field_type_variations)
            }
            
            # Detail each schema pattern
            for i, (pattern, msg_ids) in enumerate(schema_patterns.items(), 1):
                self.findings['schema_variations']['schema_patterns'][f'pattern_{i}'] = {
                    'fields': list(pattern),
                    'count': len(msg_ids),
                    'example_ids': msg_ids[:3]
                }
            
            # Log findings
            self.logger.info(f"Found {len(schema_patterns)} unique schema patterns")
            self.logger.info("\nMost common fields:")
            for field, count in field_frequency.most_common(10):
                percentage = (count / len(messages)) * 100
                self.logger.info(f"  - {field}: {count} ({percentage:.1f}%)")
            
            # Check for critical field variations
            critical_fields = ['to', 'from', 'subject', 'content', 'body', 'timestamp']
            missing_critical = []
            
            for field in critical_fields:
                if field_frequency[field] < len(messages):
                    missing_count = len(messages) - field_frequency[field]
                    missing_critical.append({
                        'field': field,
                        'missing_count': missing_count,
                        'missing_percentage': (missing_count / len(messages)) * 100
                    })
            
            if missing_critical:
                self.findings['schema_variations']['missing_critical_fields'] = missing_critical
                self.logger.warning(f"\n⚠️  Critical fields missing in some messages:")
                for item in missing_critical:
                    self.logger.warning(f"  - {item['field']}: missing in {item['missing_count']} messages ({item['missing_percentage']:.1f}%)")
            
        except Exception as e:
            self.logger.error(f"❌ Schema variation analysis failed: {str(e)}")
            self.findings['schema_variations']['error'] = str(e)
    
    def _check_field_variations(self):
        """Check for variations in recipient field names"""
        self.logger.info("\n🔍 CHECKING FIELD NAME VARIATIONS")
        self.logger.info("-" * 50)
        
        try:
            # Look for different recipient field names
            recipient_fields = ['to', 'to_agent', 'recipient', 'recipients', 'receiver', 'target']
            sender_fields = ['from', 'from_agent', 'sender', 'author', 'source']
            
            field_variations = {
                'recipient_fields': {},
                'sender_fields': {}
            }
            
            # Check each potential recipient field
            for field in recipient_fields:
                query = f"SELECT COUNT(1) as count FROM messages WHERE IS_DEFINED(messages.{field})"
                try:
                    result = list(self.db.messages_container.query_items(
                        query=query,
                        enable_cross_partition_query=True
                    ))
                    count = result[0]['count'] if result else 0
                    
                    if count > 0:
                        field_variations['recipient_fields'][field] = count
                        self.logger.info(f"  ✓ Found '{field}' field in {count} messages")
                        
                        # Get examples
                        example_query = f"SELECT messages.id, messages.{field}, messages.subject FROM messages WHERE IS_DEFINED(messages.{field}) OFFSET 0 LIMIT 3"
                        examples = self.db.query_messages(example_query)
                        if examples:
                            field_variations['recipient_fields'][f'{field}_examples'] = examples
                            
                except Exception as e:
                    self.logger.debug(f"  ✗ Field '{field}' check failed: {str(e)}")
            
            # Check sender fields
            for field in sender_fields:
                query = f"SELECT COUNT(1) as count FROM messages WHERE IS_DEFINED(messages.{field})"
                try:
                    result = list(self.db.messages_container.query_items(
                        query=query,
                        enable_cross_partition_query=True
                    ))
                    count = result[0]['count'] if result else 0
                    
                    if count > 0:
                        field_variations['sender_fields'][field] = count
                        self.logger.info(f"  ✓ Found '{field}' field in {count} messages")
                        
                except Exception as e:
                    self.logger.debug(f"  ✗ Field '{field}' check failed: {str(e)}")
            
            self.findings['field_inconsistencies'] = field_variations
            
            # Check for messages using non-standard fields
            if len(field_variations['recipient_fields']) > 1:
                self.logger.warning("\n⚠️  Multiple recipient field names detected!")
                self.logger.warning("This will cause messages to be missed by standard queries.")
            
        except Exception as e:
            self.logger.error(f"❌ Field variation check failed: {str(e)}")
            self.findings['field_inconsistencies']['error'] = str(e)
    
    def _test_query_patterns(self):
        """Test different query patterns to identify what works and what fails"""
        self.logger.info("\n🧪 TESTING QUERY PATTERNS")
        self.logger.info("-" * 50)
        
        test_agent = "HEAD_OF_ENGINEERING"
        query_tests = []
        
        # Define test queries
        test_queries = [
            {
                'name': 'Standard string match',
                'query': "SELECT * FROM messages WHERE messages['to'] = @agent",
                'params': [{"name": "@agent", "value": test_agent}]
            },
            {
                'name': 'Array contains',
                'query': "SELECT * FROM messages WHERE ARRAY_CONTAINS(messages['to'], @agent)",
                'params': [{"name": "@agent", "value": test_agent}]
            },
            {
                'name': 'Unified (string OR array)',
                'query': "SELECT * FROM messages WHERE (messages['to'] = @agent OR ARRAY_CONTAINS(messages['to'], @agent))",
                'params': [{"name": "@agent", "value": test_agent}]
            },
            {
                'name': 'Alternative field: to_agent',
                'query': "SELECT * FROM messages WHERE messages.to_agent = @agent",
                'params': [{"name": "@agent", "value": test_agent}]
            },
            {
                'name': 'Alternative field: recipient',
                'query': "SELECT * FROM messages WHERE messages.recipient = @agent",
                'params': [{"name": "@agent", "value": test_agent}]
            },
            {
                'name': 'Case-insensitive string',
                'query': "SELECT * FROM messages WHERE LOWER(messages['to']) = LOWER(@agent)",
                'params': [{"name": "@agent", "value": test_agent}]
            },
            {
                'name': 'Partial string match',
                'query': "SELECT * FROM messages WHERE CONTAINS(messages['to'], @agent)",
                'params': [{"name": "@agent", "value": test_agent}]
            }
        ]
        
        # Test each query pattern
        for test in test_queries:
            try:
                start_time = datetime.now()
                results = self.db.query_messages(test['query'], test['params'])
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                query_tests.append({
                    'pattern': test['name'],
                    'query': test['query'],
                    'status': 'success',
                    'results_count': len(results),
                    'duration_seconds': duration,
                    'example_ids': [r['id'] for r in results[:3]] if results else []
                })
                
                self.logger.info(f"  ✓ {test['name']}: {len(results)} results in {duration:.3f}s")
                
            except Exception as e:
                query_tests.append({
                    'pattern': test['name'],
                    'query': test['query'],
                    'status': 'failed',
                    'error': str(e)
                })
                
                self.logger.error(f"  ✗ {test['name']}: FAILED - {str(e)}")
        
        self.findings['query_failures'] = query_tests
        
        # Analyze query results
        successful_queries = [q for q in query_tests if q['status'] == 'success']
        if successful_queries:
            max_results = max(q['results_count'] for q in successful_queries)
            optimal_queries = [q for q in successful_queries if q['results_count'] == max_results]
            
            self.logger.info(f"\n📊 Query Analysis:")
            self.logger.info(f"  - Maximum results found: {max_results}")
            self.logger.info(f"  - Optimal query patterns: {', '.join(q['pattern'] for q in optimal_queries)}")
    
    def _identify_missed_messages(self):
        """Identify specific messages that might be missed by standard queries"""
        self.logger.info("\n🎯 IDENTIFYING POTENTIALLY MISSED MESSAGES")
        self.logger.info("-" * 50)
        
        try:
            # Get all unique agents mentioned in messages
            agents_query = """
            SELECT DISTINCT VALUE messages['from'] FROM messages WHERE IS_DEFINED(messages['from'])
            """
            all_agents = self.db.query_messages(agents_query)
            
            self.logger.info(f"Found {len(all_agents)} unique agents to check")
            
            missed_messages = []
            
            # For each agent, compare different query methods
            for agent in all_agents[:10]:  # Limit to first 10 for performance
                if not agent or not isinstance(agent, str):
                    continue
                
                # Standard query
                standard_query = "SELECT messages.id FROM messages WHERE messages['to'] = @agent"
                params = [{"name": "@agent", "value": agent}]
                standard_results = set(r['id'] for r in self.db.query_messages(standard_query, params))
                
                # Comprehensive query (check multiple fields)
                comprehensive_query = """
                SELECT messages.id FROM messages 
                WHERE messages['to'] = @agent 
                   OR ARRAY_CONTAINS(messages['to'], @agent)
                   OR messages.to_agent = @agent
                   OR messages.recipient = @agent
                   OR CONTAINS(LOWER(messages['to']), LOWER(@agent))
                """
                comprehensive_results = set(r['id'] for r in self.db.query_messages(comprehensive_query, params))
                
                # Find missed messages
                missed = comprehensive_results - standard_results
                
                if missed:
                    missed_messages.append({
                        'agent': agent,
                        'standard_count': len(standard_results),
                        'comprehensive_count': len(comprehensive_results),
                        'missed_count': len(missed),
                        'missed_ids': list(missed)[:5]  # First 5 examples
                    })
                    
                    self.logger.warning(f"  ⚠️  {agent}: {len(missed)} messages missed by standard query")
            
            self.findings['missed_messages'] = missed_messages
            
            if missed_messages:
                total_missed = sum(m['missed_count'] for m in missed_messages)
                self.logger.warning(f"\n❌ Total potentially missed messages: {total_missed}")
                
                # Analyze why messages were missed
                self.logger.info("\n📋 Analyzing missed message patterns...")
                for item in missed_messages[:3]:  # First 3 agents
                    agent = item['agent']
                    for msg_id in item['missed_ids'][:2]:  # First 2 examples
                        msg_query = "SELECT * FROM messages WHERE messages.id = @id"
                        msg_params = [{"name": "@id", "value": msg_id}]
                        msg_results = self.db.query_messages(msg_query, msg_params)
                        
                        if msg_results:
                            msg = msg_results[0]
                            self.logger.info(f"\n  Example: {msg_id}")
                            self.logger.info(f"    Expected recipient: {agent}")
                            self.logger.info(f"    'to' field value: {msg.get('to', 'MISSING')}")
                            self.logger.info(f"    'to' field type: {type(msg.get('to')).__name__}")
                            
                            # Check other potential fields
                            for field in ['to_agent', 'recipient', 'recipients']:
                                if field in msg:
                                    self.logger.info(f"    '{field}' field: {msg[field]}")
            
        except Exception as e:
            self.logger.error(f"❌ Missed message identification failed: {str(e)}")
            self.findings['missed_messages'] = {'error': str(e)}
    
    def _check_agent_usage_patterns(self):
        """Check how agents are creating and querying messages"""
        self.logger.info("\n🤖 CHECKING AGENT USAGE PATTERNS")
        self.logger.info("-" * 50)
        
        try:
            # Analyze message creation patterns by agent
            recent_messages_query = """
            SELECT messages['from'] as sender, messages['to'] as recipient, messages.id, messages.timestamp
            FROM messages 
            ORDER BY messages.timestamp DESC 
            OFFSET 0 LIMIT 200
            """
            
            recent_messages = self.db.query_messages(recent_messages_query)
            
            agent_patterns = defaultdict(lambda: {
                'messages_sent': 0,
                'recipient_types': Counter(),
                'uses_arrays': False,
                'uses_strings': False,
                'inconsistent': False
            })
            
            for msg in recent_messages:
                sender = msg.get('sender')
                recipient = msg.get('recipient')
                
                if sender:
                    agent_patterns[sender]['messages_sent'] += 1
                    
                    if recipient is not None:
                        recipient_type = 'array' if isinstance(recipient, list) else 'string'
                        agent_patterns[sender]['recipient_types'][recipient_type] += 1
                        
                        if recipient_type == 'array':
                            agent_patterns[sender]['uses_arrays'] = True
                        else:
                            agent_patterns[sender]['uses_strings'] = True
            
            # Check for inconsistent agents
            for agent, data in agent_patterns.items():
                if data['uses_arrays'] and data['uses_strings']:
                    data['inconsistent'] = True
                    self.logger.warning(f"  ⚠️  {agent} uses BOTH array and string recipients (inconsistent)")
                elif data['uses_arrays']:
                    self.logger.info(f"  📋 {agent} uses array recipients")
                elif data['uses_strings']:
                    self.logger.info(f"  ✓ {agent} uses string recipients (standard)")
            
            self.findings['agent_patterns'] = dict(agent_patterns)
            
        except Exception as e:
            self.logger.error(f"❌ Agent usage pattern check failed: {str(e)}")
            self.findings['agent_patterns'] = {'error': str(e)}
    
    def _generate_recommendations(self):
        """Generate specific recommendations based on findings"""
        self.logger.info("\n💡 GENERATING RECOMMENDATIONS")
        self.logger.info("-" * 50)
        
        recommendations = []
        
        # Check for schema inconsistencies
        if self.findings.get('schema_variations', {}).get('unique_schemas', 0) > 3:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Schema Standardization',
                'issue': 'Multiple schema variations detected',
                'recommendation': 'Implement strict schema validation in message creation',
                'action_items': [
                    'Define canonical message schema with required fields',
                    'Add validation in CosmosDBManager.store_message()',
                    'Create migration script to standardize existing messages'
                ]
            })
        
        # Check for field inconsistencies
        if len(self.findings.get('field_inconsistencies', {}).get('recipient_fields', {})) > 1:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Field Naming',
                'issue': 'Multiple recipient field names in use',
                'recommendation': 'Standardize on "to" field for all recipients',
                'action_items': [
                    'Update all agent code to use "to" field exclusively',
                    'Migrate messages using alternative fields',
                    'Add deprecation warnings for non-standard fields'
                ]
            })
        
        # Check for type inconsistencies
        field_variations = self.findings.get('schema_variations', {}).get('field_type_variations', {})
        if 'to' in field_variations and len(field_variations['to']) > 1:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Type Consistency',
                'issue': '"to" field has multiple types (string vs array)',
                'recommendation': 'Standardize recipient field types',
                'action_items': [
                    'Use string for single recipients',
                    'Use dedicated "cc" or "recipients" array field for multiple',
                    'Convert single-element arrays to strings',
                    'Update unified query to handle both during transition'
                ]
            })
        
        # Check for missed messages
        if self.findings.get('missed_messages'):
            total_missed = sum(m['missed_count'] for m in self.findings['missed_messages'])
            if total_missed > 0:
                recommendations.append({
                    'priority': 'CRITICAL',
                    'category': 'Query Reliability',
                    'issue': f'{total_missed} messages potentially missed by standard queries',
                    'recommendation': 'Implement unified query system immediately',
                    'action_items': [
                        'Deploy unified_message_query.py to all agents',
                        'Replace all direct queries with unified query functions',
                        'Add query result validation to detect missed messages'
                    ]
                })
        
        # Check for agent inconsistencies
        inconsistent_agents = [
            agent for agent, data in self.findings.get('agent_patterns', {}).items()
            if isinstance(data, dict) and data.get('inconsistent')
        ]
        if inconsistent_agents:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Agent Behavior',
                'issue': f'{len(inconsistent_agents)} agents use inconsistent message formats',
                'recommendation': 'Standardize agent message creation',
                'action_items': [
                    'Review and update agent code for: ' + ', '.join(inconsistent_agents[:3]),
                    'Create unit tests for message format validation',
                    'Add logging to track format violations'
                ]
            })
        
        # Add query optimization recommendation
        query_results = self.findings.get('query_failures', [])
        failed_queries = [q for q in query_results if q.get('status') == 'failed']
        if failed_queries:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Query Optimization',
                'issue': f'{len(failed_queries)} query patterns failed',
                'recommendation': 'Fix or remove problematic query patterns',
                'action_items': [
                    'Review failed queries and fix syntax errors',
                    'Test all query patterns in development environment',
                    'Document supported query patterns'
                ]
            })
        
        self.findings['recommendations'] = recommendations
        
        # Log recommendations
        for rec in recommendations:
            self.logger.info(f"\n{rec['priority']} Priority: {rec['category']}")
            self.logger.info(f"Issue: {rec['issue']}")
            self.logger.info(f"Recommendation: {rec['recommendation']}")
            self.logger.info("Action items:")
            for item in rec['action_items']:
                self.logger.info(f"  - {item}")
    
    def _create_investigation_report(self):
        """Create a detailed investigation report"""
        self.logger.info("\n📄 CREATING INVESTIGATION REPORT")
        self.logger.info("-" * 50)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"message_schema_investigation_{timestamp}.json"
        
        # Save detailed findings
        with open(report_file, 'w') as f:
            json.dump(self.findings, f, indent=2, default=str)
        
        self.logger.info(f"✅ Detailed findings saved to: {report_file}")
        
        # Create summary report
        summary = {
            'investigation_timestamp': timestamp,
            'summary': {
                'schema_variations': self.findings.get('schema_variations', {}).get('unique_schemas', 'Unknown'),
                'field_inconsistencies': len(self.findings.get('field_inconsistencies', {}).get('recipient_fields', {})),
                'potentially_missed_messages': sum(
                    m['missed_count'] for m in self.findings.get('missed_messages', [])
                    if isinstance(m, dict) and 'missed_count' in m
                ),
                'critical_recommendations': len([
                    r for r in self.findings.get('recommendations', [])
                    if r.get('priority') == 'CRITICAL'
                ]),
                'total_recommendations': len(self.findings.get('recommendations', []))
            },
            'immediate_actions': [
                r for r in self.findings.get('recommendations', [])
                if r.get('priority') in ['CRITICAL', 'HIGH']
            ]
        }
        
        summary_file = f"message_schema_investigation_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"✅ Summary report saved to: {summary_file}")
        
        # Print executive summary
        self.logger.info("\n📊 EXECUTIVE SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Schema Variations Found: {summary['summary']['schema_variations']}")
        self.logger.info(f"Field Naming Issues: {summary['summary']['field_inconsistencies']}")
        self.logger.info(f"Messages Potentially Missed: {summary['summary']['potentially_missed_messages']}")
        self.logger.info(f"Critical Issues: {summary['summary']['critical_recommendations']}")
        self.logger.info(f"Total Recommendations: {summary['summary']['total_recommendations']}")
        
        if summary['immediate_actions']:
            self.logger.info("\n🚨 IMMEDIATE ACTIONS REQUIRED:")
            for action in summary['immediate_actions']:
                self.logger.info(f"\n- {action['category']}: {action['issue']}")
                self.logger.info(f"  Action: {action['recommendation']}")
        
        return report_file, summary_file

def main():
    """Run the comprehensive investigation"""
    print("🔍 COMPREHENSIVE MESSAGE SCHEMA INVESTIGATION")
    print("=" * 80)
    print("This investigation will identify why agents are having trouble finding their messages")
    print()
    
    investigator = MessageSchemaInvestigator()
    findings = investigator.investigate_all_issues()
    
    print("\n✅ Investigation complete!")
    print("Review the generated reports for detailed findings and recommendations.")

if __name__ == "__main__":
    main()