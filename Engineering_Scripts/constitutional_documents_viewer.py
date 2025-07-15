#!/usr/bin/env python3
"""
Constitutional Documents Viewer
Reads new governance documentation from Cosmos DB and creates an HTML page
"""

import json
from datetime import datetime
from cosmos_db_manager import get_db_manager

def fetch_constitutional_documents():
    """Fetch all constitutional and governance documents from various containers"""
    db = get_db_manager()
    documents = {
        'constitutional': [],
        'enforcement': [],
        'governance': [],
        'accountability': []
    }
    
    # 1. Fetch from messages container - constitutional discussions
    print("Fetching constitutional discussions...")
    query = """
    SELECT * FROM c 
    WHERE CONTAINS(LOWER(c.subject), 'constitutional') 
    OR CONTAINS(LOWER(c.content), 'constitutional framework')
    OR CONTAINS(LOWER(c.content), 'governance framework')
    ORDER BY c.timestamp DESC
    """
    constitutional_msgs = db.query_messages(query)
    documents['constitutional'] = constitutional_msgs[:10]  # Latest 10
    
    # 2. Fetch enforcement records we just added
    print("Fetching enforcement records...")
    query = """
    SELECT * FROM c 
    WHERE c.record_type = 'enforcement'
    ORDER BY c.created_date DESC
    """
    try:
        enforcement_records = db.query_messages(query, container_name='enforcement')
        documents['enforcement'] = enforcement_records
    except:
        # Try alternative query
        documents['enforcement'] = []
    
    # 3. Fetch governance policies from IDC if available
    print("Fetching governance policies...")
    query = """
    SELECT * FROM c 
    WHERE c.type = 'governance_policy'
    OR c.domain = 'governance'
    ORDER BY c.modifiedEpoch DESC
    """
    try:
        governance_docs = db.query_messages(query, container_name='institutional-data-center')
        documents['governance'] = governance_docs
    except:
        documents['governance'] = []
    
    return documents

def generate_html(documents):
    """Generate HTML page with fetched documents"""
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Constitutional Documents - Governance Framework 2025</title>
    <style>
        :root {
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --bg-tertiary: #0f3460;
            --text-primary: #e8e8e8;
            --text-secondary: #a8a8a8;
            --accent: #e94560;
            --accent-light: #ff6b6b;
            --success: #4ecdc4;
            --warning: #f7b731;
            --border: #2a2a4e;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            border: 1px solid var(--border);
        }
        
        h1 {
            color: var(--accent-light);
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: var(--text-secondary);
            font-size: 1.2em;
        }
        
        .toc {
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            border: 1px solid var(--border);
        }
        
        .toc h2 {
            color: var(--success);
            margin-bottom: 15px;
        }
        
        .toc ul {
            list-style: none;
        }
        
        .toc li {
            margin-bottom: 10px;
        }
        
        .toc a {
            color: var(--text-primary);
            text-decoration: none;
            padding: 5px 10px;
            display: block;
            border-radius: 5px;
            transition: all 0.3s;
        }
        
        .toc a:hover {
            background: var(--bg-tertiary);
            color: var(--accent-light);
        }
        
        .section {
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            border: 1px solid var(--border);
        }
        
        .section h2 {
            color: var(--accent-light);
            margin-bottom: 20px;
            font-size: 2em;
        }
        
        .section h3 {
            color: var(--success);
            margin: 20px 0 10px 0;
            font-size: 1.5em;
        }
        
        .document {
            background: var(--bg-tertiary);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid var(--border);
        }
        
        .document-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            cursor: pointer;
        }
        
        .document-title {
            color: var(--accent-light);
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .document-meta {
            color: var(--text-secondary);
            font-size: 0.9em;
        }
        
        .document-content {
            padding-top: 15px;
            border-top: 1px solid var(--border);
            display: none;
        }
        
        .document-content.expanded {
            display: block;
        }
        
        .statistic {
            background: var(--bg-primary);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid var(--accent);
        }
        
        .stat-value {
            color: var(--warning);
            font-size: 2em;
            font-weight: bold;
        }
        
        .stat-label {
            color: var(--text-secondary);
            margin-bottom: 5px;
        }
        
        .stat-source {
            color: var(--text-secondary);
            font-size: 0.9em;
            font-style: italic;
        }
        
        .search-box {
            background: var(--bg-tertiary);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid var(--border);
        }
        
        .search-box input {
            width: 100%;
            padding: 10px;
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 5px;
            color: var(--text-primary);
            font-size: 1em;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: var(--accent);
        }
        
        pre {
            background: var(--bg-primary);
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 10px 0;
        }
        
        code {
            color: var(--success);
            font-family: 'Courier New', monospace;
        }
        
        .tag {
            display: inline-block;
            background: var(--accent);
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            margin-right: 5px;
        }
        
        .priority-critical {
            background: var(--accent);
        }
        
        .priority-high {
            background: var(--warning);
        }
        
        .priority-medium {
            background: var(--success);
        }
        
        .expand-btn {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            border: 1px solid var(--border);
            padding: 5px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
        }
        
        .expand-btn:hover {
            background: var(--accent);
            border-color: var(--accent);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Constitutional Documents & Governance Framework</h1>
            <p class="subtitle">New Constitutional Documentation from Cosmos DB Containers</p>
            <p class="subtitle">Generated: {timestamp}</p>
        </header>
        
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Search documents..." onkeyup="searchDocuments()">
        </div>
        
        <nav class="toc">
            <h2>Table of Contents</h2>
            <ul>
                <li><a href="#enforcement">🚨 Enforcement Statistics</a></li>
                <li><a href="#constitutional">📜 Constitutional Framework Documents</a></li>
                <li><a href="#governance">🏛️ Governance Policies</a></li>
                <li><a href="#accountability">⚖️ Accountability Matrix</a></li>
            </ul>
        </nav>
        
        <section id="enforcement" class="section">
            <h2>🚨 Enforcement Statistics</h2>
            <p>Critical metrics requiring immediate attention and tracking</p>
            
            <div class="statistic">
                <div class="stat-label">Multi-Box Architecture Message Failure Rate</div>
                <div class="stat-value">40%</div>
                <div class="stat-source">Source: SAM (2025-06-20) - Bug to Fix</div>
                <p>Fragmented agent identity across terminals causing communication failures. Requires unified architecture implementation.</p>
            </div>
            
            <div class="statistic">
                <div class="stat-label">Governance Methods Adoption Rate</div>
                <div class="stat-value">6.7%</div>
                <div class="stat-source">Source: COMPLIANCE_MANAGER Conference Analysis (2025-06-15)</div>
                <p>Only 1 out of 15 agents uses governance methods. 13 method documents exist but are ignored. Competing systems must be deleted.</p>
            </div>
            
            <div class="statistic">
                <div class="stat-label">Blocked Enterprise Value</div>
                <div class="stat-value">$2.5M</div>
                <div class="stat-source">Source: COMPLIANCE_MANAGER Conference Analysis (2025-06-15)</div>
                <ul>
                    <li>Full_Stack_Software_Engineer: $830,000 (FRED pipeline)</li>
                    <li>Azure Infrastructure: $500,000 (operational value)</li>
                    <li>Research Team: $250,000 (knowledge discovery)</li>
                    <li>Opportunity Cost: $1,000,000+</li>
                </ul>
            </div>
            
            {enforcement_section}
        </section>
        
        <section id="constitutional" class="section">
            <h2>📜 Constitutional Framework Documents</h2>
            <p>Core constitutional principles and frameworks from recent discussions</p>
            
            {constitutional_section}
        </section>
        
        <section id="governance" class="section">
            <h2>🏛️ Governance Policies</h2>
            <p>Active governance policies and procedures</p>
            
            {governance_section}
        </section>
        
        <section id="accountability" class="section">
            <h2>⚖️ Accountability Matrix</h2>
            <p>Role definitions and constitutional authorities</p>
            
            <div class="document">
                <div class="document-header">
                    <span class="document-title">Management Role Transformations</span>
                </div>
                <div class="document-content expanded">
                    <h3>Constitutional Role Definitions</h3>
                    <ul>
                        <li><strong>SAM</strong>: Constitutional framework protection + energy cascade enablement</li>
                        <li><strong>COMPLIANCE_MANAGER</strong>: From manual tracking to constitutional framework guardianship</li>
                        <li><strong>HEAD_OF_ENGINEERING</strong>: Emergency deployment authority + technical competence leadership</li>
                        <li><strong>HEAD_OF_RESEARCH</strong>: From strategic planning to knowledge operations engineering</li>
                        <li><strong>HEAD_OF_DIGITAL_STAFF</strong>: From manual coordination to automated workforce orchestration</li>
                    </ul>
                </div>
            </div>
        </section>
    </div>
    
    <script>
        function toggleDocument(element) {
            const content = element.nextElementSibling;
            content.classList.toggle('expanded');
        }
        
        function searchDocuments() {
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const documents = document.getElementsByClassName('document');
            
            for (let doc of documents) {
                const text = doc.textContent || doc.innerText;
                if (text.toLowerCase().indexOf(filter) > -1) {
                    doc.style.display = "";
                } else {
                    doc.style.display = "none";
                }
            }
        }
        
        // Add click handlers to all document headers
        document.addEventListener('DOMContentLoaded', function() {
            const headers = document.getElementsByClassName('document-header');
            for (let header of headers) {
                header.addEventListener('click', function() {
                    toggleDocument(this);
                });
            }
        });
    </script>
</body>
</html>
    """
    
    # Generate sections
    enforcement_html = ""
    for doc in documents.get('enforcement', []):
        enforcement_html += f"""
        <div class="document">
            <div class="document-header">
                <span class="document-title">{doc.get('title', doc.get('id', 'Enforcement Record'))}</span>
                <span class="document-meta">{doc.get('created_date', '')[:10]}</span>
            </div>
            <div class="document-content">
                <p><strong>Category:</strong> {doc.get('category', 'N/A')}</p>
                <p><strong>Status:</strong> {doc.get('status', 'N/A')}</p>
                <p><strong>Value:</strong> {doc.get('numeric_value', 'N/A')}</p>
                <pre>{json.dumps(doc, indent=2)}</pre>
            </div>
        </div>
        """
    
    constitutional_html = ""
    for doc in documents.get('constitutional', []):
        priority = doc.get('priority', 'medium')
        constitutional_html += f"""
        <div class="document">
            <div class="document-header">
                <span class="document-title">{doc.get('subject', 'Constitutional Document')}</span>
                <span class="tag priority-{priority}">{priority}</span>
                <span class="document-meta">From: {doc.get('from', 'Unknown')} | {doc.get('timestamp', '')[:10]}</span>
            </div>
            <div class="document-content">
                <p><strong>To:</strong> {doc.get('to', 'N/A')}</p>
                <p><strong>Type:</strong> {doc.get('type', 'N/A')}</p>
                <div style="margin-top: 15px;">
                    {str(doc.get('content', 'No content available')).replace(chr(10), '<br>')}
                </div>
            </div>
        </div>
        """
    
    governance_html = ""
    if not documents.get('governance'):
        governance_html = "<p>No governance policies found in IDC. Migration may be pending.</p>"
    else:
        for doc in documents.get('governance', []):
            governance_html += f"""
            <div class="document">
                <div class="document-header">
                    <span class="document-title">{doc.get('title', 'Governance Policy')}</span>
                    <span class="document-meta">{doc.get('domain', 'governance')}</span>
                </div>
                <div class="document-content">
                    <p>{doc.get('content', doc.get('description', 'No content available'))}</p>
                </div>
            </div>
            """
    
    # Fill template
    html = html_template.format(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        enforcement_section=enforcement_html,
        constitutional_section=constitutional_html,
        governance_section=governance_html
    )
    
    return html

def main():
    print("Fetching constitutional documents from Cosmos DB...")
    documents = fetch_constitutional_documents()
    
    print(f"Found:")
    print(f"  - Constitutional discussions: {len(documents['constitutional'])}")
    print(f"  - Enforcement records: {len(documents['enforcement'])}")
    print(f"  - Governance policies: {len(documents['governance'])}")
    
    print("\nGenerating HTML page...")
    html = generate_html(documents)
    
    output_file = 'constitutional_documents_2025-06-20.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Constitutional documents page created: {output_file}")
    print(f"   File size: {len(html):,} bytes")
    print(f"\nOpen in your browser to view the new governance documentation.")

if __name__ == "__main__":
    main()