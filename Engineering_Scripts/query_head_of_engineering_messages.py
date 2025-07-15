#!/usr/bin/env python3
"""
Query Cosmos DB for specific messages needed by HEAD_OF_ENGINEERING
Focuses on recent messages TO HEAD_OF_ENGINEERING and key organizational topics
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Import cosmos manager - properly handle imports
sys.path.insert(0, str(Path(__file__).parent))
from cosmos_db_manager import get_db_manager

def get_recent_cutoff_date(hours=48):
    """Get cutoff date for recent messages (48 hours ago)"""
    cutoff = datetime.now() - timedelta(hours=hours)
    return cutoff.isoformat() + 'Z'

def query_messages_to_head_of_engineering():
    """Get messages TO HEAD_OF_ENGINEERING from last 24-48 hours"""
    db = get_db_manager()
    cutoff_date = get_recent_cutoff_date(48)
    
    # Using unified query pattern to handle both string and array recipients
    query = """
    SELECT * FROM messages 
    WHERE (messages['to'] = 'HEAD_OF_ENGINEERING' OR ARRAY_CONTAINS(messages['to'], 'HEAD_OF_ENGINEERING'))
    AND messages.timestamp >= @cutoff_date
    ORDER BY messages.timestamp DESC
    """
    
    parameters = [{"name": "@cutoff_date", "value": cutoff_date}]
    
    try:
        results = db.query_messages(query, parameters)
        return results
    except Exception as e:
        print(f"Error querying messages to HEAD_OF_ENGINEERING: {e}")
        return []

def query_research_engineering_mentions():
    """Get messages mentioning research or engineering teams"""
    db = get_db_manager()
    cutoff_date = get_recent_cutoff_date(48)
    
    query = """
    SELECT * FROM messages 
    WHERE (
        CONTAINS(LOWER(messages.content), 'research team') OR
        CONTAINS(LOWER(messages.content), 'engineering team') OR
        CONTAINS(LOWER(messages.content), 'research & analytics') OR
        CONTAINS(LOWER(messages.subject), 'research') OR
        CONTAINS(LOWER(messages.subject), 'engineering')
    )
    AND messages.timestamp >= @cutoff_date
    ORDER BY messages.timestamp DESC
    """
    
    parameters = [{"name": "@cutoff_date", "value": cutoff_date}]
    
    try:
        results = db.query_messages(query, parameters)
        return results
    except Exception as e:
        print(f"Error querying research/engineering mentions: {e}")
        return []

def query_semantic_policy_messages():
    """Get messages about enhanced semantic policy responses"""
    db = get_db_manager()
    
    query = """
    SELECT * FROM messages 
    WHERE (
        CONTAINS(LOWER(messages.content), 'semantic policy') OR
        CONTAINS(LOWER(messages.content), 'policy response') OR
        CONTAINS(LOWER(messages.content), 'enhanced semantic') OR
        CONTAINS(LOWER(messages.subject), 'semantic') OR
        CONTAINS(LOWER(messages.subject), 'policy')
    )
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        return results
    except Exception as e:
        print(f"Error querying semantic policy messages: {e}")
        return []

def query_constitutional_role_messages():
    """Get constitutional role review messages from SAM"""
    db = get_db_manager()
    
    query = """
    SELECT * FROM messages 
    WHERE (
        messages['from'] = 'SAM' OR
        CONTAINS(LOWER(messages.content), 'constitutional') OR
        CONTAINS(LOWER(messages.content), 'role review') OR
        CONTAINS(LOWER(messages.subject), 'constitutional') OR
        CONTAINS(LOWER(messages.subject), 'role review')
    )
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        return results
    except Exception as e:
        print(f"Error querying constitutional role messages: {e}")
        return []

def query_azure_infrastructure_messages():
    """Get Azure infrastructure coordination messages"""
    db = get_db_manager()
    cutoff_date = get_recent_cutoff_date(72)  # 72 hours for infrastructure
    
    query = """
    SELECT * FROM messages 
    WHERE (
        CONTAINS(LOWER(messages.content), 'azure') OR
        CONTAINS(LOWER(messages.content), 'infrastructure') OR
        CONTAINS(LOWER(messages.content), 'cosmos') OR
        CONTAINS(LOWER(messages.content), 'deployment') OR
        CONTAINS(LOWER(messages.subject), 'azure') OR
        CONTAINS(LOWER(messages.subject), 'infrastructure')
    )
    AND messages.timestamp >= @cutoff_date
    ORDER BY messages.timestamp DESC
    """
    
    parameters = [{"name": "@cutoff_date", "value": cutoff_date}]
    
    try:
        results = db.query_messages(query, parameters)
        return results
    except Exception as e:
        print(f"Error querying Azure infrastructure messages: {e}")
        return []

def format_message_for_display(message):
    """Format message for readable display"""
    timestamp = message.get('timestamp', 'Unknown')
    from_agent = message.get('from', 'Unknown')
    to_agent = message.get('to', 'Unknown')
    subject = message.get('subject', 'No Subject')
    content = message.get('content', 'No Content')
    priority = message.get('priority', 'medium')
    msg_type = message.get('type', 'UNKNOWN')
    
    # Truncate long content for summary view
    if len(content) > 500:
        content_display = content[:500] + "...[TRUNCATED]"
    else:
        content_display = content
    
    return f"""
{'='*80}
🕒 {timestamp} | 🏷️  {msg_type} | ⚡ {priority.upper()}
📧 FROM: {from_agent} → TO: {to_agent}
📋 SUBJECT: {subject}
{'='*80}
📝 CONTENT:
{content_display}
{'='*80}
"""

def main():
    """Main execution function"""
    print("🔍 QUERYING COSMOS DB FOR HEAD_OF_ENGINEERING MESSAGES")
    print("=" * 60)
    
    try:
        # 1. Messages TO HEAD_OF_ENGINEERING (last 48 hours)
        print("\n📨 1. MESSAGES TO HEAD_OF_ENGINEERING (Last 48 Hours)")
        print("-" * 60)
        
        to_head_messages = query_messages_to_head_of_engineering()
        if to_head_messages:
            print(f"Found {len(to_head_messages)} messages to HEAD_OF_ENGINEERING")
            for msg in to_head_messages[:10]:  # Show top 10 most recent
                print(format_message_for_display(msg))
        else:
            print("❌ No recent messages found to HEAD_OF_ENGINEERING")
        
        # 2. Research/Engineering Team Mentions
        print("\n🔬 2. RESEARCH & ENGINEERING TEAM MENTIONS (Last 48 Hours)")
        print("-" * 60)
        
        research_messages = query_research_engineering_mentions()
        if research_messages:
            print(f"Found {len(research_messages)} messages mentioning research/engineering teams")
            for msg in research_messages[:5]:  # Show top 5
                print(format_message_for_display(msg))
        else:
            print("❌ No messages found mentioning research/engineering teams")
        
        # 3. Enhanced Semantic Policy Messages
        print("\n🧠 3. ENHANCED SEMANTIC POLICY RESPONSES")
        print("-" * 60)
        
        semantic_messages = query_semantic_policy_messages()
        if semantic_messages:
            print(f"Found {len(semantic_messages)} messages about semantic policy")
            for msg in semantic_messages[:3]:  # Show top 3
                print(format_message_for_display(msg))
        else:
            print("❌ No messages found about semantic policy responses")
        
        # 4. Constitutional Role Review from SAM
        print("\n⚖️ 4. CONSTITUTIONAL ROLE REVIEW DETAILS FROM SAM")
        print("-" * 60)
        
        constitutional_messages = query_constitutional_role_messages()
        if constitutional_messages:
            print(f"Found {len(constitutional_messages)} constitutional/role review messages")
            for msg in constitutional_messages[:3]:  # Show top 3
                print(format_message_for_display(msg))
        else:
            print("❌ No constitutional role review messages found")
        
        # 5. Azure Infrastructure Coordination
        print("\n☁️ 5. AZURE INFRASTRUCTURE COORDINATION (Last 72 Hours)")
        print("-" * 60)
        
        azure_messages = query_azure_infrastructure_messages()
        if azure_messages:
            print(f"Found {len(azure_messages)} Azure infrastructure messages")
            for msg in azure_messages[:5]:  # Show top 5
                print(format_message_for_display(msg))
        else:
            print("❌ No Azure infrastructure coordination messages found")
        
        # Summary
        total_messages = (
            len(to_head_messages) + 
            len(research_messages) + 
            len(semantic_messages) + 
            len(constitutional_messages) + 
            len(azure_messages)
        )
        
        print(f"\n📊 SUMMARY")
        print("=" * 60)
        print(f"📨 Messages to HEAD_OF_ENGINEERING: {len(to_head_messages)}")
        print(f"🔬 Research/Engineering mentions: {len(research_messages)}")
        print(f"🧠 Semantic policy messages: {len(semantic_messages)}")
        print(f"⚖️ Constitutional role messages: {len(constitutional_messages)}")
        print(f"☁️ Azure infrastructure messages: {len(azure_messages)}")
        print(f"📈 Total relevant messages: {total_messages}")
        
        if total_messages == 0:
            print("\n⚠️ WARNING: No relevant messages found!")
            print("This could indicate:")
            print("  - Messages haven't been migrated to Cosmos DB yet")
            print("  - Different field naming conventions")
            print("  - Messages are older than the query timeframes")
            
            # Let's do a sample query to see what's actually in the database
            print("\n🔍 SAMPLING DATABASE CONTENTS...")
            db = get_db_manager()
            
            sample_query = "SELECT TOP 5 * FROM messages ORDER BY messages.timestamp DESC"
            sample_results = db.query_messages(sample_query)
            
            if sample_results:
                print(f"Found {len(sample_results)} sample messages in database:")
                for i, msg in enumerate(sample_results, 1):
                    print(f"\n--- SAMPLE MESSAGE {i} ---")
                    print(f"ID: {msg.get('id', 'N/A')}")
                    print(f"From: {msg.get('from', 'N/A')}")
                    print(f"To: {msg.get('to', 'N/A')}")
                    print(f"Subject: {msg.get('subject', 'N/A')}")
                    print(f"Timestamp: {msg.get('timestamp', 'N/A')}")
                    print(f"Type: {msg.get('type', 'N/A')}")
                    if 'content' in msg:
                        content_preview = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                        print(f"Content Preview: {content_preview}")
            else:
                print("❌ No messages found in database at all!")
    
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)