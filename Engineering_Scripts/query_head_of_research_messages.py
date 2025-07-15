#!/usr/bin/env python3
"""
Query Cosmos DB for HEAD_OF_RESEARCH communications
Focuses on messages FROM/TO HEAD_OF_RESEARCH and research leadership communications
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Import cosmos manager - properly handle imports
sys.path.insert(0, str(Path(__file__).parent))
from cosmos_db_manager import get_db_manager

def get_recent_cutoff_date(days=7):
    """Get cutoff date for recent messages (default 7 days)"""
    cutoff = datetime.now() - timedelta(days=days)
    return cutoff.isoformat() + 'Z'

def query_messages_from_head_of_research():
    """Get all messages FROM HEAD_OF_RESEARCH"""
    db = get_db_manager()
    
    query = """
    SELECT * FROM messages 
    WHERE messages['from'] = 'HEAD_OF_RESEARCH'
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        return results
    except Exception as e:
        print(f"Error querying messages from HEAD_OF_RESEARCH: {e}")
        return []

def query_messages_to_head_of_engineering_from_research():
    """Get messages TO HEAD_OF_ENGINEERING FROM HEAD_OF_RESEARCH"""
    db = get_db_manager()
    
    # Using unified query pattern to handle both string and array recipients
    query = """
    SELECT * FROM messages 
    WHERE messages['from'] = 'HEAD_OF_RESEARCH'
    AND (messages['to'] = 'HEAD_OF_ENGINEERING' OR ARRAY_CONTAINS(messages['to'], 'HEAD_OF_ENGINEERING'))
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        return results
    except Exception as e:
        print(f"Error querying messages from HEAD_OF_RESEARCH to HEAD_OF_ENGINEERING: {e}")
        return []

def query_recent_research_leadership_communications():
    """Get recent communications from research leadership"""
    db = get_db_manager()
    cutoff_date = get_recent_cutoff_date(14)  # Last 14 days
    
    query = """
    SELECT * FROM messages 
    WHERE (
        messages['from'] = 'HEAD_OF_RESEARCH' OR
        CONTAINS(LOWER(messages['from']), 'research') OR
        CONTAINS(LOWER(messages.content), 'research leadership') OR
        CONTAINS(LOWER(messages.content), 'research team') OR
        CONTAINS(LOWER(messages.subject), 'research leadership')
    )
    AND messages.timestamp >= @cutoff_date
    ORDER BY messages.timestamp DESC
    """
    
    parameters = [{"name": "@cutoff_date", "value": cutoff_date}]
    
    try:
        results = db.query_messages(query, parameters)
        return results
    except Exception as e:
        print(f"Error querying recent research leadership communications: {e}")
        return []

def query_document_migration_messages():
    """Get messages about research team document migration"""
    db = get_db_manager()
    
    query = """
    SELECT * FROM messages 
    WHERE (
        CONTAINS(LOWER(messages.content), 'document migration') OR
        CONTAINS(LOWER(messages.content), 'migrate') OR
        CONTAINS(LOWER(messages.content), 'migration') OR
        CONTAINS(LOWER(messages.subject), 'migration') OR
        CONTAINS(LOWER(messages.subject), 'migrate') OR
        (CONTAINS(LOWER(messages.content), 'research') AND CONTAINS(LOWER(messages.content), 'document'))
    )
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        return results
    except Exception as e:
        print(f"Error querying document migration messages: {e}")
        return []

def query_semantic_policy_messages():
    """Get messages mentioning semantic policy"""
    db = get_db_manager()
    
    query = """
    SELECT * FROM messages 
    WHERE (
        CONTAINS(LOWER(messages.content), 'semantic policy') OR
        CONTAINS(LOWER(messages.content), 'semantic') OR
        CONTAINS(LOWER(messages.subject), 'semantic') OR
        CONTAINS(LOWER(messages.subject), 'policy') OR
        CONTAINS(LOWER(messages.content), 'policy')
    )
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        return results
    except Exception as e:
        print(f"Error querying semantic policy messages: {e}")
        return []

def format_message_for_display(message):
    """Format message for readable display with full content"""
    timestamp = message.get('timestamp', 'Unknown')
    from_agent = message.get('from', 'Unknown')
    to_agent = message.get('to', 'Unknown')
    subject = message.get('subject', 'No Subject')
    content = message.get('content', 'No Content')
    priority = message.get('priority', 'medium')
    msg_type = message.get('type', 'UNKNOWN')
    message_id = message.get('id', 'No ID')
    
    return f"""
{'='*100}
🆔 ID: {message_id}
🕒 TIMESTAMP: {timestamp} | 🏷️  TYPE: {msg_type} | ⚡ PRIORITY: {priority.upper()}
📧 FROM: {from_agent} → TO: {to_agent}
📋 SUBJECT: {subject}
{'='*100}
📝 FULL CONTENT:
{content}
{'='*100}
"""

def main():
    """Main execution function"""
    print("🔍 QUERYING COSMOS DB FOR HEAD_OF_RESEARCH COMMUNICATIONS")
    print("=" * 80)
    
    try:
        # 1. All messages FROM HEAD_OF_RESEARCH
        print("\n📤 1. ALL MESSAGES FROM HEAD_OF_RESEARCH")
        print("-" * 80)
        
        from_research_messages = query_messages_from_head_of_research()
        if from_research_messages:
            print(f"✅ Found {len(from_research_messages)} messages from HEAD_OF_RESEARCH")
            for i, msg in enumerate(from_research_messages, 1):
                print(f"\n--- MESSAGE {i} FROM HEAD_OF_RESEARCH ---")
                print(format_message_for_display(msg))
        else:
            print("❌ No messages found from HEAD_OF_RESEARCH")
        
        # 2. Messages TO HEAD_OF_ENGINEERING FROM HEAD_OF_RESEARCH
        print("\n📧 2. MESSAGES TO HEAD_OF_ENGINEERING FROM HEAD_OF_RESEARCH")
        print("-" * 80)
        
        to_engineering_messages = query_messages_to_head_of_engineering_from_research()
        if to_engineering_messages:
            print(f"✅ Found {len(to_engineering_messages)} messages from HEAD_OF_RESEARCH to HEAD_OF_ENGINEERING")
            for i, msg in enumerate(to_engineering_messages, 1):
                print(f"\n--- MESSAGE {i} TO HEAD_OF_ENGINEERING ---")
                print(format_message_for_display(msg))
        else:
            print("❌ No messages found from HEAD_OF_RESEARCH to HEAD_OF_ENGINEERING")
        
        # 3. Recent research leadership communications
        print("\n🔬 3. RECENT RESEARCH LEADERSHIP COMMUNICATIONS (Last 14 Days)")
        print("-" * 80)
        
        leadership_messages = query_recent_research_leadership_communications()
        if leadership_messages:
            print(f"✅ Found {len(leadership_messages)} recent research leadership communications")
            for i, msg in enumerate(leadership_messages, 1):
                print(f"\n--- LEADERSHIP MESSAGE {i} ---")
                print(format_message_for_display(msg))
        else:
            print("❌ No recent research leadership communications found")
        
        # 4. Document migration messages
        print("\n📄 4. RESEARCH TEAM DOCUMENT MIGRATION MESSAGES")
        print("-" * 80)
        
        migration_messages = query_document_migration_messages()
        if migration_messages:
            print(f"✅ Found {len(migration_messages)} document migration messages")
            for i, msg in enumerate(migration_messages, 1):
                print(f"\n--- MIGRATION MESSAGE {i} ---")
                print(format_message_for_display(msg))
        else:
            print("❌ No document migration messages found")
        
        # 5. Semantic policy messages
        print("\n🧠 5. SEMANTIC POLICY MESSAGES")
        print("-" * 80)
        
        semantic_messages = query_semantic_policy_messages()
        if semantic_messages:
            print(f"✅ Found {len(semantic_messages)} semantic policy messages")
            for i, msg in enumerate(semantic_messages, 1):
                print(f"\n--- SEMANTIC POLICY MESSAGE {i} ---")
                print(format_message_for_display(msg))
        else:
            print("❌ No semantic policy messages found")
        
        # Summary
        total_messages = (
            len(from_research_messages) + 
            len(to_engineering_messages) + 
            len(leadership_messages) + 
            len(migration_messages) + 
            len(semantic_messages)
        )
        
        print(f"\n📊 SUMMARY")
        print("=" * 80)
        print(f"📤 Messages FROM HEAD_OF_RESEARCH: {len(from_research_messages)}")
        print(f"📧 Messages TO HEAD_OF_ENGINEERING from research: {len(to_engineering_messages)}")
        print(f"🔬 Recent research leadership communications: {len(leadership_messages)}")
        print(f"📄 Document migration messages: {len(migration_messages)}")
        print(f"🧠 Semantic policy messages: {len(semantic_messages)}")
        print(f"📈 Total relevant messages: {total_messages}")
        
        if total_messages == 0:
            print("\n⚠️ WARNING: No HEAD_OF_RESEARCH messages found!")
            print("This could indicate:")
            print("  - HEAD_OF_RESEARCH hasn't sent messages yet")
            print("  - Messages use different agent naming conventions")
            print("  - Messages haven't been migrated to Cosmos DB yet")
            
            # Let's check what agents exist in the database
            print("\n🔍 CHECKING WHAT AGENTS EXIST IN DATABASE...")
            db = get_db_manager()
            
            agent_query = """
            SELECT DISTINCT messages['from'] as from_agent, messages['to'] as to_agent 
            FROM messages 
            WHERE IS_DEFINED(messages['from']) AND IS_DEFINED(messages['to'])
            """
            
            try:
                agent_results = db.query_messages(agent_query)
                
                from_agents = set()
                to_agents = set()
                
                for result in agent_results:
                    if result.get('from_agent'):
                        from_agents.add(result['from_agent'])
                    if result.get('to_agent'):
                        to_agents.add(result['to_agent'])
                
                print(f"\n📋 AGENTS SENDING MESSAGES:")
                for agent in sorted(from_agents):
                    print(f"  - {agent}")
                
                print(f"\n📋 AGENTS RECEIVING MESSAGES:")
                for agent in sorted(to_agents):
                    print(f"  - {agent}")
                    
                # Check for research-related agents
                research_agents = [agent for agent in (from_agents | to_agents) if 'research' in agent.lower()]
                if research_agents:
                    print(f"\n🔬 RESEARCH-RELATED AGENTS FOUND:")
                    for agent in research_agents:
                        print(f"  - {agent}")
                        
            except Exception as e:
                print(f"Error checking agents: {e}")
    
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)