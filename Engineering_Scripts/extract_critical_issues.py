#!/usr/bin/env python3
"""
Extract detailed information about critical issues from messages container
"""

import os
import json
from datetime import datetime
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_critical_issues():
    """Extract messages related to SAM's critical issues"""
    endpoint = os.getenv('COSMOS_ENDPOINT')
    key = os.getenv('COSMOS_KEY')
    database_name = os.getenv('COSMOS_DATABASE', 'research-analytics-db')
    
    client = CosmosClient(endpoint, key)
    database = client.get_database_client(database_name)
    container = database.get_container_client('system_inbox')
    
    # Define search queries for critical issues
    searches = [
        {
            "name": "Multi-box Architecture Issues",
            "query": """SELECT * FROM c WHERE 
                       (CONTAINS(LOWER(c.content), 'multi-box') OR 
                        CONTAINS(LOWER(c.content), 'multibox') OR
                        CONTAINS(LOWER(c.content), 'multi box'))
                       ORDER BY c.timestamp DESC"""
        },
        {
            "name": "SAM's Critical Messages",
            "query": """SELECT * FROM c WHERE 
                       (CONTAINS(LOWER(c.content), 'sam') AND 
                        (CONTAINS(LOWER(c.content), 'critical') OR 
                         CONTAINS(LOWER(c.content), 'urgent') OR
                         CONTAINS(LOWER(c.content), 'issue')))
                       ORDER BY c.timestamp DESC"""
        },
        {
            "name": "Governance Adoption Issues",
            "query": """SELECT * FROM c WHERE 
                       CONTAINS(LOWER(c.content), 'governance') AND 
                       (CONTAINS(LOWER(c.content), 'adoption') OR 
                        CONTAINS(LOWER(c.content), 'theater') OR
                        CONTAINS(LOWER(c.content), 'failure'))
                       ORDER BY c.timestamp DESC"""
        },
        {
            "name": "Architecture Bugs and Issues",
            "query": """SELECT * FROM c WHERE 
                       CONTAINS(LOWER(c.content), 'architecture') AND 
                       (CONTAINS(LOWER(c.content), 'bug') OR 
                        CONTAINS(LOWER(c.content), 'issue') OR
                        CONTAINS(LOWER(c.content), 'failure'))
                       ORDER BY c.timestamp DESC"""
        },
        {
            "name": "Message Delivery Failures",
            "query": """SELECT * FROM c WHERE 
                       (CONTAINS(LOWER(c.content), 'message') OR 
                        CONTAINS(LOWER(c.content), 'delivery')) AND
                       (CONTAINS(LOWER(c.content), 'fail') OR 
                        CONTAINS(LOWER(c.content), 'error'))
                       ORDER BY c.timestamp DESC"""
        }
    ]
    
    print("🔍 EXTRACTING CRITICAL ISSUES FROM MESSAGES")
    print("="*80)
    
    all_findings = []
    
    for search in searches:
        print(f"\n📋 {search['name']}:")
        print("-"*60)
        
        try:
            results = list(container.query_items(search['query'], enable_cross_partition_query=True))
            print(f"Found {len(results)} relevant messages")
            
            # Show details of most relevant messages
            for i, msg in enumerate(results[:3], 1):  # Top 3 per category
                finding = {
                    'category': search['name'],
                    'id': msg.get('id'),
                    'from': msg.get('from'),
                    'to': msg.get('to'),
                    'subject': msg.get('subject'),
                    'timestamp': msg.get('timestamp'),
                    'content': msg.get('content')
                }
                all_findings.append(finding)
                
                print(f"\n{i}. Message ID: {msg.get('id', 'N/A')}")
                print(f"   From: {msg.get('from', 'N/A')}")
                print(f"   To: {msg.get('to', 'N/A')}")
                print(f"   Subject: {msg.get('subject', 'N/A')}")
                print(f"   Date: {msg.get('timestamp', 'N/A')}")
                print(f"   Type: {msg.get('type', 'N/A')}")
                
                # Extract key content
                content = msg.get('content', '')
                if isinstance(content, dict):
                    # Handle structured content
                    print("   Key Points:")
                    for key, value in content.items():
                        if isinstance(value, (str, int, float, bool)):
                            print(f"     - {key}: {str(value)[:100]}...")
                        elif isinstance(value, list) and len(value) > 0:
                            print(f"     - {key}: {len(value)} items")
                        elif isinstance(value, dict):
                            print(f"     - {key}: {len(value)} fields")
                else:
                    # Handle text content
                    lines = str(content).split('\n')
                    important_lines = []
                    for line in lines:
                        line_lower = line.lower()
                        if any(term in line_lower for term in ['critical', 'urgent', 'fail', 'issue', 'bug', 'adoption', 'multi-box', 'sam']):
                            important_lines.append(line.strip())
                    
                    if important_lines:
                        print("   Key Content:")
                        for line in important_lines[:5]:  # First 5 important lines
                            print(f"     > {line[:150]}...")
                    else:
                        # Show preview if no key lines found
                        preview = content[:300] + "..." if len(content) > 300 else content
                        print(f"   Content Preview: {preview}")
                        
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    # Save findings to file
    output_file = "critical_issues_findings.json"
    with open(output_file, 'w') as f:
        json.dump(all_findings, f, indent=2)
    
    print(f"\n\n💾 Full findings saved to: {output_file}")
    print(f"Total findings extracted: {len(all_findings)}")
    
    # Summary of key patterns
    print("\n\n🎯 KEY PATTERNS IDENTIFIED:")
    print("="*60)
    
    # Count mentions of key terms across all findings
    term_counts = {
        'multi-box': 0,
        'SAM': 0,
        'governance': 0,
        'adoption': 0,
        'architecture': 0,
        'bug': 0,
        'failure': 0,
        'critical': 0
    }
    
    for finding in all_findings:
        content_str = str(finding.get('content', '')).lower()
        for term in term_counts:
            if term.lower() in content_str:
                term_counts[term] += 1
    
    for term, count in sorted(term_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  - {term}: mentioned in {count} messages")

if __name__ == "__main__":
    extract_critical_issues()