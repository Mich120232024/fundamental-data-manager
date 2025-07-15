#!/usr/bin/env python3
"""Generate Constitutional Documents HTML from Cosmos DB"""

import json
from datetime import datetime
from cosmos_db_manager import get_db_manager

def fetch_documents():
    db = get_db_manager()
    
    # Fetch constitutional messages
    query = """
    SELECT * FROM c 
    WHERE CONTAINS(LOWER(c.subject), 'constitutional') 
    OR CONTAINS(LOWER(c.content), 'governance')
    ORDER BY c.timestamp DESC
    """
    
    messages = db.query_messages(query)
    return messages[:20]  # Latest 20

def generate_html(documents):
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Constitutional Documents - New Governance Framework</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a2e;
            color: #e8e8e8;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #ff6b6b;
            border-bottom: 3px solid #ff6b6b;
            padding-bottom: 10px;
        }
        h2 {
            color: #4ecdc4;
            margin-top: 30px;
        }
        .stat-box {
            background: #16213e;
            border: 1px solid #2a2a4e;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #e94560;
        }
        .stat-value {
            font-size: 2.5em;
            color: #f7b731;
            font-weight: bold;
        }
        .stat-label {
            color: #a8a8a8;
            margin-bottom: 10px;
        }
        .document {
            background: #16213e;
            border: 1px solid #2a2a4e;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .doc-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #2a2a4e;
        }
        .doc-title {
            color: #ff6b6b;
            font-weight: bold;
            font-size: 1.2em;
        }
        .doc-meta {
            color: #a8a8a8;
            font-size: 0.9em;
        }
        .doc-content {
            white-space: pre-wrap;
            background: #0f3460;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .tag {
            display: inline-block;
            background: #e94560;
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            margin-right: 5px;
        }
        .search {
            background: #16213e;
            border: 1px solid #2a2a4e;
            padding: 10px;
            width: 100%;
            color: #e8e8e8;
            margin-bottom: 20px;
            border-radius: 5px;
        }
    </style>
    <script>
        function search() {
            var input = document.getElementById('searchBox').value.toLowerCase();
            var docs = document.getElementsByClassName('document');
            for (var i = 0; i < docs.length; i++) {
                var text = docs[i].textContent.toLowerCase();
                docs[i].style.display = text.includes(input) ? '' : 'none';
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Constitutional Documents - New Governance Framework</h1>
        <p>Generated from Cosmos DB containers on """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        
        <input type="text" id="searchBox" class="search" placeholder="Search documents..." onkeyup="search()">
        
        <h2>Critical Enforcement Statistics</h2>
        
        <div class="stat-box">
            <div class="stat-label">Multi-Box Architecture Message Failure Rate</div>
            <div class="stat-value">40%</div>
            <p>Source: SAM (2025-06-20) - Identified as BUG to fix, not pattern to enable</p>
        </div>
        
        <div class="stat-box">
            <div class="stat-label">Governance Methods Adoption Rate</div>
            <div class="stat-value">6.7%</div>
            <p>Source: COMPLIANCE_MANAGER Conference Analysis (2025-06-15)<br>
            Only 1 out of 15 agents uses governance methods</p>
        </div>
        
        <div class="stat-box">
            <div class="stat-label">Blocked Enterprise Value</div>
            <div class="stat-value">$2.5M</div>
            <p>Source: COMPLIANCE_MANAGER Conference Analysis (2025-06-15)<br>
            • Full_Stack_Software_Engineer: $830,000<br>
            • Azure Infrastructure: $500,000<br>
            • Research Team: $250,000<br>
            • Opportunity Cost: $1,000,000+</p>
        </div>
        
        <h2>Constitutional Framework Documents</h2>
    """
    
    # Add documents
    for doc in documents:
        subject = doc.get('subject', 'No subject')
        from_agent = doc.get('from', 'Unknown')
        to_agent = doc.get('to', 'Unknown')
        timestamp = doc.get('timestamp', '')[:19]
        priority = doc.get('priority', 'normal')
        msg_type = doc.get('type', 'MESSAGE')
        
        # Get content
        content = doc.get('content', {})
        if isinstance(content, dict):
            content_str = json.dumps(content, indent=2)
        else:
            content_str = str(content)
        
        html += f"""
        <div class="document">
            <div class="doc-header">
                <div class="doc-title">{subject}</div>
                <div class="doc-meta">
                    <span class="tag">{priority}</span>
                    <span class="tag">{msg_type}</span>
                    {timestamp}
                </div>
            </div>
            <div>
                <p><strong>From:</strong> {from_agent} → <strong>To:</strong> {to_agent}</p>
            </div>
            <div class="doc-content">{content_str}</div>
        </div>
        """
    
    html += """
    </div>
</body>
</html>"""
    
    return html

def main():
    print("Fetching constitutional documents from Cosmos DB...")
    documents = fetch_documents()
    print(f"Found {len(documents)} documents")
    
    print("Generating HTML...")
    html = generate_html(documents)
    
    filename = "constitutional_documents_2025-06-20.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Created: {filename}")
    print(f"   Size: {len(html):,} bytes")
    print("\nOpen this file in your browser to view the constitutional documents.")

if __name__ == "__main__":
    main()