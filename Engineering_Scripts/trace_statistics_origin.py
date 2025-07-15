#!/usr/bin/env python3
"""Trace the origin of specific statistics"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cosmos_db_manager import CosmosDBManager
import json
from datetime import datetime

def trace_statistics_origin():
    """Find the earliest mentions of these statistics"""
    db = CosmosDBManager()
    
    print("Tracing the origin of statistics...")
    print("=" * 80)
    
    # Get all messages containing these stats
    stats_messages = []
    
    # Search for 40%
    try:
        results = db.search_messages("40%", field="content")
        for msg in results:
            msg['stat_found'] = '40%'
            stats_messages.append(msg)
    except:
        pass
    
    # Search for 6.7%
    try:
        results = db.search_messages("6.7%", field="content")
        for msg in results:
            msg['stat_found'] = '6.7%'
            stats_messages.append(msg)
    except:
        pass
    
    # Search for $2.5M
    try:
        results = db.search_messages("$2.5M", field="content")
        for msg in results:
            msg['stat_found'] = '$2.5M'
            stats_messages.append(msg)
    except:
        pass
    
    # Sort by timestamp to find earliest
    stats_messages.sort(key=lambda x: x.get('timestamp', ''))
    
    print(f"Found {len(stats_messages)} messages containing these statistics\n")
    
    # Show first appearance of each stat
    first_appearances = {}
    
    for msg in stats_messages:
        stat = msg['stat_found']
        if stat not in first_appearances:
            first_appearances[stat] = msg
            print(f"FIRST APPEARANCE OF {stat}:")
            print(f"  Date: {msg.get('timestamp', 'Unknown')}")
            print(f"  From: {msg.get('from', 'Unknown')}")
            print(f"  To: {msg.get('to', 'Unknown')}")
            print(f"  Subject: {msg.get('subject', 'No subject')}")
            
            # Extract relevant part of content
            content = msg.get('content', '')
            if stat in content:
                idx = content.find(stat)
                start = max(0, idx - 200)
                end = min(len(content), idx + 200)
                snippet = content[start:end]
                print(f"  Context:\n    {snippet}")
            print("\n" + "-" * 80 + "\n")
    
    # Now let's look at the COMPLIANCE_MANAGER message from June 15
    print("\nLooking for the COMPLIANCE_MANAGER message to Claude_Code from June 15...")
    try:
        # Get messages from COMPLIANCE_MANAGER
        cm_messages = db.get_messages_by_agent("COMPLIANCE_MANAGER", direction="from", limit=50)
        
        for msg in cm_messages:
            if (msg.get('to') == 'Claude_Code' and 
                'Deep Appreciation' in msg.get('subject', '') and
                '2025-06-15' in msg.get('timestamp', '')):
                
                print("Found the COMPLIANCE_MANAGER appreciation message:")
                print(f"  Full content:\n{msg.get('content', '')[:1000]}...")
                
                # Check if this references another document
                if "External Audit Analysis" in msg.get('content', ''):
                    print("\n  This message references an 'External Audit Analysis' - let's search for that...")
                
                break
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Search for any External Audit documents
    print("\nSearching for External Audit Analysis documents...")
    try:
        audit_results = db.search_messages("External Audit", field="subject")
        print(f"Found {len(audit_results)} messages with 'External Audit' in subject")
        
        for msg in audit_results[:3]:
            print(f"  - {msg.get('subject', 'No subject')}")
            print(f"    From: {msg.get('from', 'Unknown')}, Date: {msg.get('timestamp', 'Unknown')}")
    except:
        pass

if __name__ == "__main__":
    trace_statistics_origin()