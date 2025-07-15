#!/usr/bin/env python3
"""
Analyze patterns in missed messages to understand root causes

This script digs deeper into why certain messages are being missed
and provides specific examples and fixes.
"""

import json
from datetime import datetime
from collections import defaultdict, Counter
from cosmos_db_manager import get_db_manager

def analyze_missed_patterns():
    """Deep analysis of why messages are being missed"""
    print("🔍 ANALYZING MISSED MESSAGE PATTERNS")
    print("=" * 80)
    
    db = get_db_manager()
    
    # Test cases based on investigation findings
    test_cases = [
        {
            'name': 'Multiple recipients in string field',
            'example': 'BETA_DATA_ANALYST+Azure_Infrastructure_Agent',
            'agents': ['BETA_DATA_ANALYST', 'Azure_Infrastructure_Agent']
        },
        {
            'name': 'Space-separated recipients',
            'example': 'AzureEngineeringService Auditor',
            'agents': ['AzureEngineeringService', 'Auditor']
        },
        {
            'name': 'Comma-separated recipients',
            'example': 'HEAD_OF_ENGINEERING, HEAD_OF_RESEARCH',
            'agents': ['HEAD_OF_ENGINEERING', 'HEAD_OF_RESEARCH']
        }
    ]
    
    missed_patterns = defaultdict(list)
    
    print("\n📊 TESTING RECIPIENT PATTERNS:")
    print("-" * 50)
    
    for test in test_cases:
        print(f"\n🧪 Testing: {test['name']}")
        print(f"   Example: '{test['example']}'")
        
        # Query for messages with this pattern
        query = f"""
        SELECT * FROM messages 
        WHERE CONTAINS(messages['to'], '{test['example']}')
        ORDER BY messages.timestamp DESC
        LIMIT 5
        """
        
        try:
            results = db.query_messages(query)
            
            if results:
                print(f"   ✓ Found {len(results)} messages with this pattern")
                
                # Check if standard queries would find these for each agent
                for agent in test['agents']:
                    standard_query = "SELECT COUNT(1) as count FROM messages WHERE messages['to'] = @agent"
                    params = [{"name": "@agent", "value": agent}]
                    
                    standard_results = db.query_messages(standard_query, params)
                    count = standard_results[0]['count'] if standard_results else 0
                    
                    if count == 0:
                        print(f"   ❌ Agent '{agent}' would miss these messages with standard query")
                        missed_patterns[test['name']].append({
                            'agent': agent,
                            'pattern': test['example'],
                            'sample_messages': [r['id'] for r in results[:3]]
                        })
                    else:
                        print(f"   ✓ Agent '{agent}' can find messages with standard query")
                        
        except Exception as e:
            print(f"   ⚠️  Query failed: {str(e)}")
    
    # Analyze all recipient formats
    print("\n📊 ANALYZING ALL RECIPIENT FORMATS:")
    print("-" * 50)
    
    # Get sample of messages with various recipient formats
    sample_query = """
    SELECT messages.id, messages['to'] as recipient, messages['from'] as sender, messages.subject
    FROM messages
    ORDER BY messages.timestamp DESC
    OFFSET 0 LIMIT 200
    """
    
    all_messages = db.query_messages(sample_query)
    
    recipient_patterns = Counter()
    pattern_examples = defaultdict(list)
    
    for msg in all_messages:
        recipient = msg.get('recipient', '')
        
        # Classify the pattern
        if isinstance(recipient, list):
            pattern = 'array'
        elif not recipient:
            pattern = 'empty'
        elif '+' in recipient:
            pattern = 'plus_separated'
        elif ',' in recipient:
            pattern = 'comma_separated'
        elif ' ' in recipient and len(recipient.split()) > 1:
            pattern = 'space_separated'
        elif recipient.startswith('[') and recipient.endswith(']'):
            pattern = 'string_that_looks_like_array'
        else:
            pattern = 'standard_single'
        
        recipient_patterns[pattern] += 1
        
        if len(pattern_examples[pattern]) < 3:
            pattern_examples[pattern].append({
                'id': msg.get('id'),
                'recipient': recipient,
                'sender': msg.get('sender', 'Unknown')
            })
    
    print("\n📈 Recipient Pattern Distribution:")
    for pattern, count in recipient_patterns.most_common():
        percentage = (count / len(all_messages)) * 100
        print(f"   {pattern}: {count} ({percentage:.1f}%)")
    
    print("\n📋 Pattern Examples:")
    for pattern, examples in pattern_examples.items():
        if pattern != 'standard_single':  # Focus on problematic patterns
            print(f"\n   {pattern.upper()}:")
            for ex in examples:
                print(f"      ID: {ex['id']}")
                print(f"      Recipient: '{ex['recipient']}'")
                print(f"      From: {ex['sender']}")
    
    # Generate specific query solutions
    print("\n💡 QUERY SOLUTIONS FOR EACH PATTERN:")
    print("-" * 50)
    
    print("\n1. For plus-separated recipients (+):")
    print("   Query: WHERE CONTAINS(messages['to'], @agent)")
    
    print("\n2. For space-separated recipients:")
    print("   Query: WHERE CONTAINS(messages['to'], @agent)")
    
    print("\n3. For comma-separated recipients:")
    print("   Query: WHERE CONTAINS(messages['to'], @agent)")
    
    print("\n4. For array recipients:")
    print("   Query: WHERE ARRAY_CONTAINS(messages['to'], @agent)")
    
    print("\n5. UNIFIED SOLUTION (handles all cases):")
    print("   Query: WHERE (messages['to'] = @agent")
    print("          OR ARRAY_CONTAINS(messages['to'], @agent)")
    print("          OR CONTAINS(messages['to'], @agent))")
    
    # Test the comprehensive unified query
    print("\n🧪 TESTING COMPREHENSIVE UNIFIED QUERY:")
    print("-" * 50)
    
    test_agent = "BETA_DATA_ANALYST"
    
    queries_to_test = [
        ("Standard", "SELECT COUNT(1) as count FROM messages WHERE messages['to'] = @agent"),
        ("Array", "SELECT COUNT(1) as count FROM messages WHERE ARRAY_CONTAINS(messages['to'], @agent)"),
        ("Contains", "SELECT COUNT(1) as count FROM messages WHERE CONTAINS(messages['to'], @agent)"),
        ("Comprehensive", """
            SELECT COUNT(1) as count FROM messages 
            WHERE (messages['to'] = @agent 
                OR ARRAY_CONTAINS(messages['to'], @agent)
                OR CONTAINS(messages['to'], @agent))
        """)
    ]
    
    params = [{"name": "@agent", "value": test_agent}]
    
    for name, query in queries_to_test:
        try:
            results = db.query_messages(query, params)
            count = results[0]['count'] if results else 0
            print(f"   {name}: {count} messages found")
        except Exception as e:
            print(f"   {name}: FAILED - {str(e)}")
    
    # Final recommendations
    print("\n🎯 ROOT CAUSE ANALYSIS:")
    print("=" * 50)
    
    print("\n1. PRIMARY ISSUE: Multi-recipient string formats")
    print("   - Some agents/systems are storing multiple recipients in a single string")
    print("   - Using separators like '+', ',', or spaces")
    print("   - Standard equality queries miss these messages")
    
    print("\n2. SECONDARY ISSUE: Mixed type storage")
    print("   - Some messages use arrays for recipients")
    print("   - Some use strings")
    print("   - No consistent pattern")
    
    print("\n3. IMPACT:")
    print("   - Agents miss messages when they're part of multi-recipient strings")
    print("   - Inbox queries return incomplete results")
    print("   - Critical messages may go unnoticed")
    
    print("\n📋 IMMEDIATE FIXES:")
    print("=" * 50)
    
    print("\n1. SHORT-TERM (Deploy Today):")
    print("   ✓ Use the comprehensive unified query for ALL message searches")
    print("   ✓ Update all agents to use unified_message_query.py")
    print("   ✓ Add CONTAINS clause to catch multi-recipient strings")
    
    print("\n2. MEDIUM-TERM (This Week):")
    print("   ✓ Standardize message creation:")
    print("     - Single recipient: string (e.g., 'AGENT_NAME')")
    print("     - Multiple recipients: array (e.g., ['AGENT1', 'AGENT2'])")
    print("   ✓ Add validation to reject non-standard formats")
    print("   ✓ Create migration script to fix existing messages")
    
    print("\n3. LONG-TERM (Next Sprint):")
    print("   ✓ Implement proper message routing with dedicated fields:")
    print("     - 'to': primary recipient (string)")
    print("     - 'cc': carbon copy recipients (array)")
    print("     - 'groups': group recipients (array)")
    print("   ✓ Add database triggers to enforce schema")
    print("   ✓ Create monitoring for schema violations")
    
    return missed_patterns, pattern_examples

if __name__ == "__main__":
    analyze_missed_patterns()