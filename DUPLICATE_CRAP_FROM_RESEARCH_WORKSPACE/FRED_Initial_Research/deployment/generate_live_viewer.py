#!/usr/bin/env python3
"""
Generate Live HTML Viewer - Creates an HTML file with current data from Cosmos DB
"""

import os
import json
from datetime import datetime
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_live_html():
    """Generate HTML with live data from Cosmos DB"""
    
    # Get credentials
    cosmos_url = os.getenv("COSMOS_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_KEY")
    
    if not cosmos_url or not cosmos_key:
        print("❌ Missing Cosmos DB credentials")
        return False
    
    try:
        # Connect to Cosmos DB and fetch live data
        print("🔄 Fetching live data from Cosmos DB...")
        client = CosmosClient(cosmos_url, cosmos_key)
        database = client.get_database_client("research-analytics-db")
        container = database.get_container_client("api_registry")
        
        # Get all documents
        all_docs = list(container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        
        # Separate system and API documents
        system_docs = [doc for doc in all_docs if doc.get('category') == 'system']
        api_docs = [doc for doc in all_docs if doc.get('category') != 'system']
        
        # Get unique categories
        categories = list(set(doc.get('category', 'unknown') for doc in all_docs))
        
        # Get schema requirements
        schema_req = None
        for doc in system_docs:
            if doc['id'] == 'schema_requirements_v1':
                schema_req = doc
                break
        
        print(f"✅ Found {len(all_docs)} documents")
        print(f"   • System docs: {len(system_docs)}")
        print(f"   • API docs: {len(api_docs)}")
        print(f"   • Categories: {categories}")
        
        # Generate HTML with live data
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>API Registry Database - LIVE DATA</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', monospace;
            background: white;
            color: black;
            padding: 20px;
            line-height: 1.6;
        }}
        
        h1 {{
            border-bottom: 3px solid black;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 24px;
            text-transform: uppercase;
        }}
        
        h2 {{
            border-bottom: 2px solid black;
            padding: 10px 0;
            margin: 30px 0 15px 0;
            font-size: 18px;
            text-transform: uppercase;
        }}
        
        .live-indicator {{
            background: black;
            color: white;
            padding: 5px 10px;
            display: inline-block;
            margin-left: 20px;
            font-size: 14px;
        }}
        
        .timestamp {{
            font-size: 12px;
            color: #666;
            margin-bottom: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .stats {{
            display: flex;
            gap: 30px;
            margin-bottom: 30px;
            padding: 20px;
            border: 3px solid black;
        }}
        
        .stat-box {{
            flex: 1;
            text-align: center;
            border-right: 1px solid black;
        }}
        
        .stat-box:last-child {{
            border-right: none;
        }}
        
        .stat-number {{
            font-size: 48px;
            font-weight: bold;
        }}
        
        .stat-label {{
            font-size: 14px;
            text-transform: uppercase;
        }}
        
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            border: 2px solid black;
        }}
        
        .table th, .table td {{
            border: 1px solid black;
            padding: 10px;
            text-align: left;
        }}
        
        .table th {{
            background: black;
            color: white;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .table tr:nth-child(even) {{
            background: #f5f5f5;
        }}
        
        .schema-box {{
            margin: 15px 0;
            padding: 15px;
            border: 2px solid black;
            background: white;
        }}
        
        .field-name {{
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        
        .field-requirement {{
            font-style: italic;
            padding-left: 20px;
            color: #333;
        }}
        
        .category-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }}
        
        .category-box {{
            border: 2px solid black;
            padding: 10px 20px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .raw-data {{
            background: #f5f5f5;
            border: 2px solid black;
            padding: 20px;
            overflow-x: auto;
            font-size: 12px;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        pre {{
            margin: 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>API Registry Database Viewer <span class="live-indicator">LIVE DATA</span></h1>
        <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{len(all_docs)}</div>
                <div class="stat-label">Total Documents</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{len(system_docs)}</div>
                <div class="stat-label">System Docs</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{len(api_docs)}</div>
                <div class="stat-label">API Docs</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{len(categories)}</div>
                <div class="stat-label">Categories</div>
            </div>
        </div>
'''

        # Add system documents section
        html_content += '''
        <h2>System Documents (Live)</h2>
        <div style="margin: 20px 0;">
'''
        
        for doc in system_docs:
            html_content += f'''
            <div class="schema-box">
                <div class="field-name">{doc['id']}</div>
                <div class="field-requirement">{doc.get('apiName', 'N/A')}</div>
            </div>
'''
        
        html_content += '</div>'
        
        # Add API documents table
        html_content += '''
        <h2>API Documents (Live)</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>API Name</th>
                    <th>Provider</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Auth Type</th>
                    <th>Protocol</th>
                </tr>
            </thead>
            <tbody>
'''
        
        if not api_docs:
            html_content += '''
                <tr>
                    <td colspan="7" style="text-align: center; padding: 20px;">
                        No API documents found - only system documents exist
                    </td>
                </tr>
'''
        else:
            for i, doc in enumerate(api_docs, 1):
                html_content += f'''
                <tr>
                    <td>{i}</td>
                    <td>{doc.get('apiName', doc.get('id', 'N/A'))}</td>
                    <td>{doc.get('provider', 'N/A')}</td>
                    <td>{doc.get('category', 'N/A')}</td>
                    <td>{doc.get('status', 'N/A')}</td>
                    <td>{doc.get('authType', 'N/A')}</td>
                    <td>{doc.get('protocol', 'N/A')}</td>
                </tr>
'''
        
        html_content += '''
            </tbody>
        </table>
'''

        # Add schema requirements if found
        if schema_req:
            html_content += '''
        <h2>Schema Requirements (Live)</h2>
        <div style="margin: 20px 0;">
'''
            key_fields = ['apiName', 'provider', 'baseUrl', 'authType', 'status', 'protocol']
            for field in key_fields:
                if field in schema_req:
                    html_content += f'''
            <div class="schema-box">
                <div class="field-name">{field}</div>
                <div class="field-requirement">{schema_req[field]}</div>
            </div>
'''
            html_content += '</div>'
        
        # Add categories
        html_content += '''
        <h2>Categories (Live)</h2>
        <div class="category-container">
'''
        for cat in sorted(categories):
            html_content += f'<div class="category-box">{cat}</div>'
        
        html_content += '</div>'
        
        # Add raw data view
        html_content += '''
        <h2>Raw Data (First 3 Documents)</h2>
        <div class="raw-data">
            <pre>
'''
        # Show first 3 documents as JSON
        sample_docs = all_docs[:3] if len(all_docs) > 3 else all_docs
        html_content += json.dumps(sample_docs, indent=2, default=str)
        
        html_content += '''
            </pre>
        </div>
        
        <div style="margin-top: 40px; text-align: center; padding: 20px; border: 3px solid black;">
            <strong>LIVE DATA STATUS:</strong> Connected to Cosmos DB successfully. 
            This is real-time data from your api_registry container.
        </div>
    </div>
</body>
</html>
'''
        
        # Save HTML file
        output_file = "api_registry_LIVE_viewer.html"
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"\n✅ Live HTML viewer generated: {output_file}")
        print(f"📄 Open this file in your browser to see LIVE data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating live viewer: {e}")
        return False

if __name__ == "__main__":
    generate_live_html()