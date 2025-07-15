#!/usr/bin/env python3
"""
Find ALL manager responses to recent messages with comprehensive search patterns
Focus on:
1. Responses to constitutional review request (msg_2025-06-17T16:26:22.018696_3271)
2. Responses to rebranding coordination (msg_2025-06-17T16:33:09.062903_3254)
3. Any other manager responses from the last 24-48 hours
"""

import json
from datetime import datetime, timedelta
from cosmos_db_manager import get_db_manager
from typing import Dict, List, Any

def format_message(msg: Dict[str, Any]) -> str:
    """Format a message for display"""
    return f"""
{'='*80}
ID: {msg.get('id', 'N/A')}
From: {msg.get('from', 'N/A')}
To: {msg.get('to', 'N/A')}
Subject: {msg.get('subject', 'N/A')}
Timestamp: {msg.get('timestamp', 'N/A')}
Type: {msg.get('type', 'N/A')}
Priority: {msg.get('priority', 'N/A')}
Content Preview: {str(msg.get('content', ''))[:200]}...
{'='*80}
"""

def find_responses_to_message(db, message_id: str, message_subject: str) -> List[Dict[str, Any]]:
    """Find all responses to a specific message"""
    print(f"\n🔍 Searching for responses to: {message_id}")
    print(f"   Subject: {message_subject}")
    
    responses = []
    
    # Query 1: Look for message ID in content
    query1 = """
    SELECT * FROM messages 
    WHERE CONTAINS(messages.content, @message_id)
    ORDER BY messages.timestamp DESC
    """
    params1 = [{"name": "@message_id", "value": message_id}]
    
    try:
        results1 = db.query_messages(query1, params1)
        print(f"   Found {len(results1)} messages referencing ID in content")
        responses.extend(results1)
    except Exception as e:
        print(f"   Error in content search: {str(e)}")
    
    # Query 2: Look for message ID in subject
    query2 = """
    SELECT * FROM messages 
    WHERE CONTAINS(messages.subject, @message_id)
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results2 = db.query_messages(query2, params1)
        print(f"   Found {len(results2)} messages referencing ID in subject")
        responses.extend(results2)
    except Exception as e:
        print(f"   Error in subject search: {str(e)}")
    
    # Query 3: Look for Re: pattern in subject
    if message_subject:
        query3 = """
        SELECT * FROM messages 
        WHERE CONTAINS(messages.subject, @subject_pattern)
        ORDER BY messages.timestamp DESC
        """
        params3 = [{"name": "@subject_pattern", "value": f"Re: {message_subject[:30]}"}]
        
        try:
            results3 = db.query_messages(query3, params3)
            print(f"   Found {len(results3)} messages with Re: pattern")
            responses.extend(results3)
        except Exception as e:
            print(f"   Error in Re: pattern search: {str(e)}")
    
    # Deduplicate responses
    unique_responses = {msg['id']: msg for msg in responses}
    return list(unique_responses.values())

def find_manager_responses(db) -> Dict[str, Any]:
    """Find all manager responses with comprehensive search"""
    print("\n🔎 COMPREHENSIVE MANAGER RESPONSE SEARCH")
    print("="*80)
    
    all_responses = {
        'constitutional_review_responses': [],
        'rebranding_responses': [],
        'recent_manager_messages': [],
        'summary': {}
    }
    
    # Known manager agents
    managers = [
        'Head of Research',
        'Head of Engineering', 
        'Head of Staff',
        'Head of Finance',
        'Chief of Staff',
        'Director of Operations'
    ]
    
    # 1. Find responses to constitutional review
    constitutional_responses = find_responses_to_message(
        db,
        'msg_2025-06-17T16:26:22.018696_3271',
        'Constitutional Role Review Required'
    )
    all_responses['constitutional_review_responses'] = constitutional_responses
    
    # 2. Find responses to rebranding coordination
    rebranding_responses = find_responses_to_message(
        db,
        'msg_2025-06-17T16:33:09.062903_3254',
        'Rebranding Coordination Required'
    )
    all_responses['rebranding_responses'] = rebranding_responses
    
    # 3. Find all recent messages FROM managers (last 48 hours)
    cutoff_date = (datetime.now() - timedelta(hours=48)).isoformat() + 'Z'
    
    print(f"\n📅 Searching for messages from managers since: {cutoff_date}")
    
    for manager in managers:
        query = """
        SELECT * FROM messages 
        WHERE messages['from'] = @manager 
        AND messages.timestamp >= @cutoff_date
        ORDER BY messages.timestamp DESC
        """
        params = [
            {"name": "@manager", "value": manager},
            {"name": "@cutoff_date", "value": cutoff_date}
        ]
        
        try:
            results = db.query_messages(query, params)
            if results:
                print(f"\n✅ Found {len(results)} messages from {manager}")
                all_responses['recent_manager_messages'].extend(results)
                
                # Show preview of each message
                for msg in results:
                    print(f"   - {msg.get('timestamp', 'N/A')}: {msg.get('subject', 'N/A')[:60]}...")
        except Exception as e:
            print(f"❌ Error querying {manager}: {str(e)}")
    
    # 4. Search for specific response patterns
    print("\n🔍 Searching for response patterns...")
    
    response_patterns = [
        'response to your',
        'regarding your message',
        'in response to',
        're: constitutional',
        're: rebranding',
        'acknowledged'
    ]
    
    for pattern in response_patterns:
        query = """
        SELECT * FROM messages 
        WHERE CONTAINS(LOWER(messages.content), @pattern)
        AND messages.timestamp >= @cutoff_date
        ORDER BY messages.timestamp DESC
        """
        params = [
            {"name": "@pattern", "value": pattern.lower()},
            {"name": "@cutoff_date", "value": cutoff_date}
        ]
        
        try:
            results = db.query_messages(query, params)
            if results:
                print(f"   Found {len(results)} messages with pattern '{pattern}'")
                
                # Filter for manager messages
                manager_results = [msg for msg in results if msg.get('from') in managers]
                if manager_results:
                    print(f"      → {len(manager_results)} from managers")
                    all_responses['recent_manager_messages'].extend(manager_results)
        except Exception as e:
            print(f"   Error searching pattern '{pattern}': {str(e)}")
    
    # Deduplicate all manager messages
    unique_manager_messages = {}
    for msg in all_responses['recent_manager_messages']:
        unique_manager_messages[msg['id']] = msg
    all_responses['recent_manager_messages'] = list(unique_manager_messages.values())
    
    # Generate summary
    all_responses['summary'] = {
        'constitutional_review_responses': len(all_responses['constitutional_review_responses']),
        'rebranding_responses': len(all_responses['rebranding_responses']),
        'total_recent_manager_messages': len(all_responses['recent_manager_messages']),
        'search_cutoff': cutoff_date,
        'managers_searched': managers
    }
    
    return all_responses

def main():
    """Main execution"""
    print("🚀 Manager Response Finder - Following SAM Protocol")
    print("=" * 80)
    
    try:
        # Get database manager
        db = get_db_manager()
        
        # Find all manager responses
        results = find_manager_responses(db)
        
        # Display results
        print("\n📊 RESULTS SUMMARY")
        print("=" * 80)
        print(f"Constitutional Review Responses: {results['summary']['constitutional_review_responses']}")
        print(f"Rebranding Responses: {results['summary']['rebranding_responses']}")
        print(f"Total Recent Manager Messages: {results['summary']['total_recent_manager_messages']}")
        
        # Show constitutional review responses
        if results['constitutional_review_responses']:
            print("\n📋 CONSTITUTIONAL REVIEW RESPONSES:")
            for msg in results['constitutional_review_responses']:
                print(format_message(msg))
        else:
            print("\n❌ No responses found to constitutional review request")
        
        # Show rebranding responses
        if results['rebranding_responses']:
            print("\n🏷️ REBRANDING RESPONSES:")
            for msg in results['rebranding_responses']:
                print(format_message(msg))
        else:
            print("\n❌ No responses found to rebranding coordination request")
        
        # Show recent manager messages
        if results['recent_manager_messages']:
            print(f"\n💼 RECENT MANAGER MESSAGES ({len(results['recent_manager_messages'])} total):")
            
            # Sort by timestamp
            sorted_messages = sorted(
                results['recent_manager_messages'], 
                key=lambda x: x.get('timestamp', ''), 
                reverse=True
            )
            
            for msg in sorted_messages[:10]:  # Show top 10
                print(format_message(msg))
                
            if len(sorted_messages) > 10:
                print(f"\n... and {len(sorted_messages) - 10} more messages")
        
        # Save full results
        output_file = f'manager_responses_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Full results saved to: {output_file}")
        
        # Additional analysis
        print("\n🔍 VERIFICATION QUERIES:")
        print("=" * 80)
        
        # Query for any message mentioning the specific IDs
        verification_ids = [
            'msg_2025-06-17T16:26:22.018696_3271',
            'msg_2025-06-17T16:33:09.062903_3254'
        ]
        
        for msg_id in verification_ids:
            print(f"\nVerifying references to {msg_id}:")
            
            # Count references
            query = """
            SELECT COUNT(1) as count FROM messages 
            WHERE CONTAINS(messages.content, @msg_id) 
            OR CONTAINS(messages.subject, @msg_id)
            """
            params = [{"name": "@msg_id", "value": msg_id}]
            
            try:
                count_result = db.query_messages(query, params)
                if count_result:
                    print(f"   Total references found: {count_result[0].get('count', 0)}")
            except Exception as e:
                print(f"   Error counting references: {str(e)}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()