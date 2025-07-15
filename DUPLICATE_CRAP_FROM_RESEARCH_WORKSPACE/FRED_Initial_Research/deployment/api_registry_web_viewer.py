#!/usr/bin/env python3
"""
API Registry Web Viewer - Simple black and white web interface to visualize the database

Run this script to start a local web server that displays the API Registry contents.
"""

import os
import json
from datetime import datetime
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Load environment variables
load_dotenv()

# Get Cosmos DB credentials
COSMOS_URL = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")

class APIRegistryHandler(BaseHTTPRequestHandler):
    """HTTP request handler for API Registry viewer"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_main_page().encode())
        elif self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            data = self.get_registry_data()
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_error(404)
    
    def get_main_page(self):
        """Generate the main HTML page"""
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>API Registry Database Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: white;
            color: black;
            padding: 20px;
            line-height: 1.6;
        }
        
        h1 {
            border-bottom: 3px solid black;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 24px;
        }
        
        h2 {
            border-bottom: 2px solid black;
            padding: 10px 0;
            margin: 20px 0 10px 0;
            font-size: 18px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .stats {
            display: flex;
            gap: 30px;
            margin-bottom: 30px;
            padding: 15px;
            border: 2px solid black;
        }
        
        .stat-box {
            text-align: center;
        }
        
        .stat-number {
            font-size: 36px;
            font-weight: bold;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }
        
        .table th, .table td {
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }
        
        .table th {
            background: black;
            color: white;
            font-weight: bold;
        }
        
        .table tr:hover {
            background: #f0f0f0;
        }
        
        .schema-field {
            margin: 10px 0;
            padding: 10px;
            border: 1px solid black;
        }
        
        .field-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .field-requirement {
            font-style: italic;
            color: #333;
        }
        
        .category-box {
            display: inline-block;
            border: 2px solid black;
            padding: 10px 20px;
            margin: 5px;
            font-weight: bold;
        }
        
        .loading {
            text-align: center;
            font-size: 24px;
            padding: 50px;
        }
        
        .error {
            color: red;
            border: 2px solid red;
            padding: 20px;
            margin: 20px 0;
        }
        
        pre {
            background: #f5f5f5;
            border: 1px solid black;
            padding: 10px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>API REGISTRY DATABASE VIEWER</h1>
        
        <div id="loading" class="loading">Loading database...</div>
        <div id="content" style="display: none;">
            
            <div class="stats" id="stats">
                <!-- Stats will be inserted here -->
            </div>
            
            <h2>SYSTEM DOCUMENTS</h2>
            <div id="system-docs">
                <!-- System documents will be inserted here -->
            </div>
            
            <h2>API CATALOG</h2>
            <table class="table" id="api-table">
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
                <tbody id="api-tbody">
                    <!-- API rows will be inserted here -->
                </tbody>
            </table>
            
            <h2>SCHEMA REQUIREMENTS</h2>
            <div id="schema-requirements">
                <!-- Schema requirements will be inserted here -->
            </div>
            
            <h2>CATEGORIES</h2>
            <div id="categories">
                <!-- Categories will be inserted here -->
            </div>
            
            <h2>RAW DATA VIEW</h2>
            <pre id="raw-data">
                <!-- Raw JSON will be inserted here -->
            </pre>
        </div>
        
        <div id="error" class="error" style="display: none;">
            <!-- Errors will be shown here -->
        </div>
    </div>
    
    <script>
        // Fetch and display data
        fetch('/api/data')
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('content').style.display = 'block';
                
                // Display statistics
                const stats = document.getElementById('stats');
                stats.innerHTML = `
                    <div class="stat-box">
                        <div class="stat-number">${data.total_docs}</div>
                        <div>Total Documents</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">${data.system_docs}</div>
                        <div>System Documents</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">${data.api_docs}</div>
                        <div>API Documents</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">${data.categories.length}</div>
                        <div>Categories</div>
                    </div>
                `;
                
                // Display system documents
                const systemDocs = document.getElementById('system-docs');
                data.system_documents.forEach(doc => {
                    systemDocs.innerHTML += `
                        <div class="schema-field">
                            <div class="field-name">${doc.id}</div>
                            <div class="field-requirement">${doc.apiName}</div>
                        </div>
                    `;
                });
                
                // Display API table
                const tbody = document.getElementById('api-tbody');
                data.api_documents.forEach((api, index) => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${index + 1}</td>
                            <td>${api.apiName || api.id}</td>
                            <td>${api.provider || 'N/A'}</td>
                            <td>${api.category || 'N/A'}</td>
                            <td>${api.status || 'N/A'}</td>
                            <td>${api.authType || 'N/A'}</td>
                            <td>${api.protocol || 'N/A'}</td>
                        </tr>
                    `;
                });
                
                // Display schema requirements
                const schemaDiv = document.getElementById('schema-requirements');
                if (data.schema_requirements) {
                    Object.entries(data.schema_requirements).forEach(([field, requirement]) => {
                        if (typeof requirement === 'string' && field !== 'id' && 
                            field !== 'category' && field !== '_etag' && field !== '_ts' &&
                            field !== 'createdAt' && field !== 'updatedAt' && 
                            field !== 'createdBy' && field !== 'lastModifiedBy') {
                            schemaDiv.innerHTML += `
                                <div class="schema-field">
                                    <div class="field-name">${field}:</div>
                                    <div class="field-requirement">${requirement}</div>
                                </div>
                            `;
                        }
                    });
                }
                
                // Display categories
                const categoriesDiv = document.getElementById('categories');
                data.categories.forEach(cat => {
                    categoriesDiv.innerHTML += `<div class="category-box">${cat}</div>`;
                });
                
                // Display raw data
                document.getElementById('raw-data').textContent = JSON.stringify(data, null, 2);
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'block';
                document.getElementById('error').textContent = 'Error loading data: ' + error.message;
            });
    </script>
</body>
</html>
        '''
    
    def get_registry_data(self):
        """Fetch data from Cosmos DB"""
        try:
            client = CosmosClient(COSMOS_URL, COSMOS_KEY)
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
            
            return {
                'total_docs': len(all_docs),
                'system_docs': len(system_docs),
                'api_docs': len(api_docs),
                'categories': sorted(categories),
                'system_documents': system_docs,
                'api_documents': api_docs,
                'schema_requirements': schema_req,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}

def main():
    """Start the web server"""
    if not COSMOS_URL or not COSMOS_KEY:
        print("❌ Missing Cosmos DB credentials in .env file")
        return
    
    port = 8888
    server = HTTPServer(('localhost', port), APIRegistryHandler)
    
    print(f"\n🌐 API Registry Web Viewer Started!")
    print(f"📍 Open your browser to: http://localhost:{port}")
    print(f"🛑 Press Ctrl+C to stop the server\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.server_close()

if __name__ == "__main__":
    main()