#!/usr/bin/env python3
"""
Analyze message format issues across the system
"""

import json
from cosmos_db_manager import get_db_manager
from datetime import datetime

def analyze_content_vs_body_fields():
    """Check how many messages have content vs body fields"""
    print("\n🔍 ANALYZING CONTENT vs BODY FIELD USAGE")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Get recent messages
    query = """
    SELECT 
        messages.id,
        messages.type,
        messages.from,
        messages.subject,
        messages.content,
        messages.body
    FROM messages 
    WHERE messages.timestamp >= '2025-06-15T00:00:00Z'
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        
        print(f"\n📊 Analyzing {len(results)} recent messages")
        
        # Statistics
        has_content = 0
        has_body = 0
        has_both = 0
        has_neither = 0
        content_empty = 0
        body_empty = 0
        
        # Examples
        body_only_examples = []
        content_only_examples = []
        both_examples = []
        
        for msg in results:
            msg_id = msg.get('id', 'N/A')
            content = msg.get('content')
            body = msg.get('body')
            
            # Check content field
            if content is not None:
                has_content += 1
                if isinstance(content, str) and not content.strip():
                    content_empty += 1
            
            # Check body field
            if body is not None:
                has_body += 1
                if isinstance(body, str) and not body.strip():
                    body_empty += 1
            
            # Categorize
            if content and body:
                has_both += 1
                if len(both_examples) < 3:
                    both_examples.append(msg)
            elif body and not content:
                if len(body_only_examples) < 5:
                    body_only_examples.append(msg)
            elif content and not body:
                if len(content_only_examples) < 5:
                    content_only_examples.append(msg)
            elif not content and not body:
                has_neither += 1
        
        # Print statistics
        print(f"\n📊 FIELD USAGE STATISTICS:")
        print(f"   Messages with 'content' field: {has_content}")
        print(f"   Messages with 'body' field: {has_body}")
        print(f"   Messages with BOTH fields: {has_both}")
        print(f"   Messages with NEITHER field: {has_neither}")
        print(f"   Empty 'content' fields: {content_empty}")
        print(f"   Empty 'body' fields: {body_empty}")
        
        # Show examples of body-only messages (like our proposal)
        print(f"\n\n📝 MESSAGES WITH BODY BUT NO CONTENT (like the proposal):")
        print("-" * 60)
        for msg in body_only_examples:
            print(f"\nID: {msg.get('id', 'N/A')}")
            print(f"Type: {msg.get('type', 'N/A')}")
            print(f"From: {msg.get('from', 'N/A')}")
            print(f"Subject: {msg.get('subject', 'N/A')}")
            body_preview = str(msg.get('body', ''))[:100]
            print(f"Body preview: {body_preview}...")
        
        # Show examples of content-only messages (standard format)
        print(f"\n\n✅ MESSAGES WITH CONTENT (standard format):")
        print("-" * 60)
        for msg in content_only_examples:
            print(f"\nID: {msg.get('id', 'N/A')}")
            print(f"Type: {msg.get('type', 'N/A')}")
            print(f"From: {msg.get('from', 'N/A')}")
            print(f"Subject: {msg.get('subject', 'N/A')}")
            content_preview = str(msg.get('content', ''))[:100]
            print(f"Content preview: {content_preview}...")
        
        return body_only_examples, content_only_examples
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return [], []

def check_manager_reading_patterns():
    """Check which field managers read when responding"""
    print("\n\n🔍 ANALYZING MANAGER RESPONSE PATTERNS")
    print("=" * 70)
    
    db = get_db_manager()
    
    # Get manager responses and what they responded to
    query = """
    SELECT * FROM messages 
    WHERE messages.from IN ('HEAD_OF_ENGINEERING', 'HEAD_OF_RESEARCH', 'HEAD_OF_DIGITAL_STAFF', 'COMPLIANCE_MANAGER')
    AND messages.type = 'response'
    AND messages.timestamp >= '2025-06-15T00:00:00Z'
    ORDER BY messages.timestamp DESC
    """
    
    try:
        results = db.query_messages(query)
        
        print(f"\n📊 Found {len(results)} manager responses")
        
        # For each response, check what they were responding to
        responded_to_body = 0
        responded_to_content = 0
        
        for response in results[:10]:  # Check first 10
            print(f"\n📧 Manager response from: {response.get('from', 'N/A')}")
            print(f"   Subject: {response.get('subject', 'N/A')}")
            
            # Look for what they're responding to in their content
            response_text = response.get('content', '') or response.get('body', '')
            
            # Check for quotes or references
            if 'Re:' in response.get('subject', '') or 'RE:' in response.get('subject', ''):
                # Try to find the original message they're responding to
                # This is a simplified check - in reality we'd use metadata
                if 'content' in response_text.lower():
                    responded_to_content += 1
                elif 'body' in response_text.lower():
                    responded_to_body += 1
        
        print(f"\n\n📊 MANAGER READING PATTERNS:")
        print(f"   Responses referencing 'content': {responded_to_content}")
        print(f"   Responses referencing 'body': {responded_to_body}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main analysis"""
    print("🕵️ ANALYZING MESSAGE FORMAT ISSUES ACROSS SYSTEM")
    print("=" * 70)
    
    # Analyze field usage
    body_msgs, content_msgs = analyze_content_vs_body_fields()
    
    # Check manager patterns
    check_manager_reading_patterns()
    
    # Final diagnosis
    print("\n\n📊 ROOT CAUSE ANALYSIS")
    print("=" * 70)
    
    print("\n❌ THE PROBLEM:")
    print("   1. The proposal used 'body' field instead of 'content' field")
    print("   2. Most messages use 'content' field (standard)")
    print("   3. Managers likely have automated filters/readers that look for 'content'")
    print("   4. Messages with only 'body' field are effectively invisible!")
    
    print("\n\n💡 WHY IT HAPPENED:")
    print("   - Inconsistent field naming in the system")
    print("   - Some messages use 'body', others use 'content'")
    print("   - No validation to ensure critical fields are populated")
    print("   - The proposal creation script used the wrong field name")
    
    print("\n\n✅ THE FIX:")
    print("   1. Resend the proposal with content in the 'content' field")
    print("   2. Copy the body text to content field")
    print("   3. Mark as HIGH priority")
    print("   4. Add 'ACTION REQUIRED' to subject")
    print("   5. Ensure all future messages use 'content' not 'body'")
    
    print("\n\n🔧 IMMEDIATE ACTION:")
    print("   Create a script to resend the proposal with proper formatting")

if __name__ == "__main__":
    main()