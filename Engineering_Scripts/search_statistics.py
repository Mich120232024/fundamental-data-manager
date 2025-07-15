#!/usr/bin/env python3
"""Search for specific statistics in messages"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cosmos_db_manager import CosmosDBManager
import json

def search_for_statistics():
    """Search for the specific statistics mentioned"""
    db = CosmosDBManager()
    
    # Statistics to search for
    search_terms = [
        "40%",
        "40 percent",
        "forty percent",
        "message failures",
        "6.7%",
        "6.7 percent",
        "adoption",
        "2.5M",
        "$2.5M",
        "2.5 million",
        "blocked value"
    ]
    
    print("Searching for statistics in all messages...")
    print("=" * 80)
    
    results = {}
    
    # Search each term
    for term in search_terms:
        print(f"\nSearching for: '{term}'")
        try:
            # Search in content
            content_results = db.search_messages(term, field="content")
            
            # Search in subject
            subject_results = db.search_messages(term, field="subject")
            
            # Combine and deduplicate
            all_results = content_results + subject_results
            unique_results = []
            seen_ids = set()
            
            for msg in all_results:
                if msg['id'] not in seen_ids:
                    seen_ids.add(msg['id'])
                    unique_results.append(msg)
            
            if unique_results:
                print(f"Found {len(unique_results)} message(s) containing '{term}':")
                for msg in unique_results[:3]:  # Show first 3
                    print(f"  - From: {msg.get('from', 'Unknown')}")
                    print(f"    To: {msg.get('to', 'Unknown')}")
                    print(f"    Subject: {msg.get('subject', 'No subject')}")
                    print(f"    Date: {msg.get('timestamp', 'Unknown date')}")
                    
                    # Show context where term appears
                    content = msg.get('content', '')
                    if term.lower() in content.lower():
                        # Find and show snippet
                        idx = content.lower().find(term.lower())
                        start = max(0, idx - 50)
                        end = min(len(content), idx + len(term) + 50)
                        snippet = content[start:end].replace('\n', ' ')
                        if start > 0:
                            snippet = "..." + snippet
                        if end < len(content):
                            snippet = snippet + "..."
                        print(f"    Context: {snippet}")
                    print()
            else:
                print(f"  No messages found containing '{term}'")
                
            results[term] = unique_results
            
        except Exception as e:
            print(f"  Error searching for '{term}': {str(e)}")
    
    # Also do a broader query for messages from SAM
    print("\n" + "=" * 80)
    print("Checking all messages from SAM for these statistics...")
    try:
        sam_messages = db.get_messages_by_agent("Strategic Architecture Manager (SAM)", direction="from", limit=50)
        print(f"Found {len(sam_messages)} messages from SAM")
        
        stats_found = False
        for msg in sam_messages:
            content = msg.get('content', '').lower()
            subject = msg.get('subject', '').lower()
            full_text = content + " " + subject
            
            # Check if any of our stats appear
            for stat in ["40%", "6.7%", "2.5m", "$2.5m"]:
                if stat in full_text:
                    stats_found = True
                    print(f"\nFound '{stat}' in message:")
                    print(f"  Subject: {msg.get('subject', 'No subject')}")
                    print(f"  Date: {msg.get('timestamp', 'Unknown date')}")
                    
                    # Show snippet
                    idx = full_text.find(stat)
                    start = max(0, idx - 100)
                    end = min(len(content), idx + 100)
                    snippet = content[start:end].replace('\n', ' ')
                    print(f"  Context: ...{snippet}...")
        
        if not stats_found:
            print("None of the specific statistics (40%, 6.7%, $2.5M) were found in SAM's messages")
            
    except Exception as e:
        print(f"Error checking SAM messages: {str(e)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    found_any = False
    for term, msgs in results.items():
        if msgs:
            found_any = True
            print(f"- '{term}': Found in {len(msgs)} message(s)")
    
    if not found_any:
        print("None of the specific statistics were found in any messages.")
        print("This suggests these numbers may be hallucinated or from a different source.")

if __name__ == "__main__":
    search_for_statistics()