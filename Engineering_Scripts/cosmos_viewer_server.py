#!/usr/bin/env python3
"""
Simple web server for Cosmos DB viewer
Provides REST API for frontend to access Cosmos DB data
"""

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Import cosmos manager
sys.path.insert(0, str(Path(__file__).parent))
from cosmos_db_manager import get_db_manager

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global database connection
db = None

def init_db():
    """Initialize database connection"""
    global db
    try:
        db = get_db_manager()
        return True
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return False

@app.route('/')
def index():
    """Serve the HTML viewer"""
    # Serve the debug version
    html_path = Path(__file__).parent / 'cosmos_db_viewer_debug.html'
    if html_path.exists():
        return send_file(str(html_path))
    else:
        # Fall back to original if debug doesn't exist
        html_path = Path(__file__).parent / 'cosmos_db_viewer.html'
        if html_path.exists():
            return send_file(str(html_path))
        else:
            return "Viewer HTML not found", 404

@app.route('/api/containers')
def get_containers():
    """Get all containers with document counts"""
    try:
        database = db.client.get_database_client(db.database_name)
        containers = []
        
        for container in database.list_containers():
            container_client = database.get_container_client(container['id'])
            
            # Get document count
            count_query = "SELECT VALUE COUNT(1) FROM c"
            count = list(container_client.query_items(
                query=count_query,
                enable_cross_partition_query=True
            ))[0]
            
            containers.append({
                'id': container['id'],
                'count': count,
                'partitionKey': container.get('partitionKey', {}).get('paths', [''])[0]
            })
        
        return jsonify({
            'success': True,
            'containers': sorted(containers, key=lambda x: x['id'])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/containers/<container_id>/documents')
def get_documents(container_id):
    """Get documents from a specific container"""
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        database = db.client.get_database_client(db.database_name)
        container = database.get_container_client(container_id)
        
        # Get documents with pagination
        query = f"SELECT * FROM c ORDER BY c._ts DESC OFFSET {offset} LIMIT {limit}"
        documents = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        return jsonify({
            'success': True,
            'container': container_id,
            'documents': documents,
            'count': len(documents),
            'offset': offset,
            'limit': limit
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/containers/<container_id>/documents/<document_id>')
def get_document(container_id, document_id):
    """Get a specific document"""
    try:
        database = db.client.get_database_client(db.database_name)
        container = database.get_container_client(container_id)
        
        # Try to find document - may need partition key
        query = "SELECT * FROM c WHERE c.id = @id"
        parameters = [{"name": "@id", "value": document_id}]
        
        documents = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        
        if documents:
            return jsonify({
                'success': True,
                'document': documents[0]
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search')
def search_documents():
    """Search across all containers"""
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify({
                'success': False,
                'error': 'Search term required'
            }), 400
            
        results = []
        database = db.client.get_database_client(db.database_name)
        
        # Search in each container
        for container_info in database.list_containers():
            container = database.get_container_client(container_info['id'])
            
            # Search in common text fields
            query = """
            SELECT * FROM c 
            WHERE CONTAINS(LOWER(c.content), LOWER(@search))
               OR CONTAINS(LOWER(c.subject), LOWER(@search))
               OR CONTAINS(LOWER(c.action), LOWER(@search))
               OR CONTAINS(LOWER(c.id), LOWER(@search))
            """
            
            parameters = [{"name": "@search", "value": search_term}]
            
            try:
                docs = list(container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True,
                    max_item_count=10
                ))
                
                for doc in docs:
                    results.append({
                        'container': container_info['id'],
                        'document': doc
                    })
                    
            except:
                # Skip containers where query fails
                pass
        
        return jsonify({
            'success': True,
            'results': results[:50],  # Limit total results
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    try:
        database = db.client.get_database_client(db.database_name)
        stats = {
            'database': db.database_name,
            'endpoint': db.endpoint,
            'containers': {},
            'totalDocuments': 0
        }
        
        for container_info in database.list_containers():
            container = database.get_container_client(container_info['id'])
            
            # Get count
            count_query = "SELECT VALUE COUNT(1) FROM c"
            count = list(container.query_items(
                query=count_query,
                enable_cross_partition_query=True
            ))[0]
            
            stats['containers'][container_info['id']] = count
            stats['totalDocuments'] += count
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/viewer')
def viewer():
    """Serve the enhanced HTML viewer"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cosmos DB Viewer</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #0078d4; color: white; padding: 1rem 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
        .container { display: flex; height: calc(100vh - 60px); }
        .sidebar { width: 300px; background: white; border-right: 1px solid #ddd; overflow-y: auto; }
        .main { flex: 1; padding: 2rem; overflow-y: auto; }
        .container-item { padding: 1rem; border-bottom: 1px solid #eee; cursor: pointer; transition: background 0.2s; }
        .container-item:hover { background: #f0f0f0; }
        .container-item.active { background: #e3f2fd; border-left: 4px solid #0078d4; }
        .container-name { font-weight: 600; color: #0078d4; }
        .container-count { color: #666; font-size: 0.9rem; margin-top: 0.25rem; }
        .document-list { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .document-item { padding: 1rem; border-bottom: 1px solid #eee; cursor: pointer; transition: background 0.2s; }
        .document-item:hover { background: #f8f8f8; }
        .document-id { font-weight: 600; color: #333; margin-bottom: 0.25rem; font-size: 0.9rem; word-break: break-all; }
        .document-meta { font-size: 0.85rem; color: #666; }
        .document-detail { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 2rem; }
        .json-viewer { background: #f8f8f8; border: 1px solid #ddd; border-radius: 4px; padding: 1rem; overflow-x: auto; font-family: 'Consolas', 'Monaco', monospace; font-size: 0.9rem; white-space: pre-wrap; word-wrap: break-word; max-height: 600px; overflow-y: auto; }
        
        /* Popup Modal Styles */
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 1000; }
        .modal-content { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; width: 90%; max-width: 800px; height: 80%; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); display: flex; flex-direction: column; }
        .modal-header { padding: 1rem 1.5rem; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; background: #f8f8f8; border-radius: 8px 8px 0 0; }
        .modal-title { font-weight: 600; color: #333; }
        .modal-close { background: #dc3545; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; font-size: 0.9rem; }
        .modal-close:hover { background: #c82333; }
        .modal-body { flex: 1; overflow-y: auto; padding: 1.5rem; background: white; }
        .formatted-content { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }
        .formatted-content h3 { color: #0078d4; margin: 1rem 0 0.5rem 0; }
        .formatted-content .field { margin-bottom: 1rem; padding: 0.75rem; background: #f5f5f5; border-radius: 4px; }
        .formatted-content .field-label { font-weight: 600; color: #555; margin-bottom: 0.25rem; }
        .formatted-content .field-value { color: #333; white-space: pre-wrap; }
        .formatted-content .timestamp { color: #666; font-size: 0.9rem; }
        .formatted-content .tags { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
        .formatted-content .tag { background: #e3f2fd; color: #0078d4; padding: 0.25rem 0.75rem; border-radius: 16px; font-size: 0.85rem; }
        .formatted-content .content-box { background: #f8f9fa; border-left: 4px solid #0078d4; padding: 1rem; margin: 1rem 0; border-radius: 4px; }
        .btn-view-formatted { background: #28a745; color: white; margin-left: 0.5rem; }
        .loading { text-align: center; padding: 2rem; color: #666; }
        .error { background: #fee; color: #c00; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
        .search-box { padding: 1rem; border-bottom: 1px solid #ddd; }
        .search-input { width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem; }
        .stats { background: #f0f7ff; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; font-size: 0.9rem; display: flex; justify-content: space-between; align-items: center; }
        .btn { border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; font-size: 0.9rem; }
        .btn-primary { background: #0078d4; color: white; }
        .btn-primary:hover { background: #005a9e; }
        .btn-success { background: #40a040; color: white; }
        .btn-success:hover { background: #308030; }
        .btn-secondary { background: #666; color: white; }
        .btn-secondary:hover { background: #555; }
        .document-actions { margin-bottom: 1rem; display: flex; gap: 1rem; }
        .stats-total { font-size: 0.8rem; color: #666; }
        .json-key { color: #881391; }
        .json-string { color: #1a1aa6; }
        .json-number { color: #098658; }
        .json-boolean { color: #ff6b00; }
        .json-null { color: #808080; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Cosmos DB Document Viewer</h1>
        <div class="stats-total" id="totalStats">Loading...</div>
    </div>
    
    <div class="container">
        <div class="sidebar">
            <div class="search-box">
                <input type="text" class="search-input" id="searchInput" placeholder="Search containers...">
            </div>
            <div id="containerList"></div>
        </div>
        
        <div class="main">
            <div id="content">
                <div class="loading">Select a container to view documents</div>
            </div>
        </div>
    </div>
    
    <!-- Modal for formatted view -->
    <div id="formattedModal" class="modal-overlay" onclick="closeModalOnOverlay(event)">
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title" id="modalTitle">Document View</h3>
                <button class="modal-close" onclick="closeModal()">Close</button>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- Formatted content will be inserted here -->
            </div>
        </div>
    </div>
    
    <script>
        const API_BASE = window.location.origin;
        let currentContainer = null;
        let allContainers = [];
        let allDocuments = [];
        
        async function init() {
            try {
                await loadContainers();
                await loadStats();
            } catch (error) {
                showError('Failed to initialize: ' + error.message);
            }
        }
        
        async function loadStats() {
            try {
                const response = await fetch(API_BASE + '/api/stats');
                const data = await response.json();
                if (data.success) {
                    document.getElementById('totalStats').textContent = 
                        `Total: ${data.stats.totalDocuments} documents across ${Object.keys(data.stats.containers).length} containers`;
                }
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }
        
        async function loadContainers() {
            const containerList = document.getElementById('containerList');
            containerList.innerHTML = '<div class="loading">Loading containers...</div>';
            
            try {
                const response = await fetch(API_BASE + '/api/containers');
                const data = await response.json();
                
                if (data.success) {
                    allContainers = data.containers;
                    displayContainers(data.containers);
                } else {
                    throw new Error(data.error);
                }
            } catch (error) {
                containerList.innerHTML = `<div class="error">Failed to load containers: ${error.message}</div>`;
            }
        }
        
        function displayContainers(containers) {
            const containerList = document.getElementById('containerList');
            containerList.innerHTML = '';
            
            containers.forEach(container => {
                const item = document.createElement('div');
                item.className = 'container-item';
                item.innerHTML = `
                    <div class="container-name">${container.id}</div>
                    <div class="container-count">${container.count} documents</div>
                `;
                item.onclick = () => selectContainer(container.id);
                containerList.appendChild(item);
            });
        }
        
        async function selectContainer(containerId) {
            currentContainer = containerId;
            
            document.querySelectorAll('.container-item').forEach(item => {
                item.classList.remove('active');
                if (item.querySelector('.container-name').textContent === containerId) {
                    item.classList.add('active');
                }
            });
            
            await loadDocuments(containerId);
        }
        
        async function loadDocuments(containerId, offset = 0) {
            const content = document.getElementById('content');
            content.innerHTML = `
                <div class="stats">
                    <strong>Container:</strong> ${containerId}
                    <button class="btn btn-primary" onclick="loadDocuments('${containerId}')">Refresh</button>
                </div>
                <div class="loading">Loading documents...</div>
            `;
            
            try {
                const response = await fetch(`${API_BASE}/api/containers/${containerId}/documents?limit=50&offset=${offset}`);
                const data = await response.json();
                
                if (data.success) {
                    allDocuments = data.documents;
                    displayDocuments(data.documents);
                } else {
                    throw new Error(data.error);
                }
            } catch (error) {
                content.innerHTML = `<div class="error">Failed to load documents: ${error.message}</div>`;
            }
        }
        
        function displayDocuments(documents) {
            const content = document.getElementById('content');
            const stats = content.querySelector('.stats');
            
            const listHtml = `
                <div class="document-list">
                    ${documents.map(doc => {
                        const timestamp = doc.timestamp || doc.createdDate || doc._ts || 'No timestamp';
                        const type = doc.type || doc.logType || doc.audit_type || 'document';
                        const from = doc.from || doc.agentName || doc.from_agent || '';
                        
                        return `
                        <div class="document-item" onclick="viewDocument('${doc.id}')">
                            <div class="document-id">${doc.id}</div>
                            <div class="document-meta">
                                ${timestamp} | ${type}${from ? ' | ' + from : ''}
                            </div>
                        </div>`;
                    }).join('')}
                </div>
            `;
            
            content.innerHTML = stats.outerHTML + listHtml;
        }
        
        function viewDocument(documentId) {
            const doc = allDocuments.find(d => d.id === documentId);
            if (!doc) return;
            
            const content = document.getElementById('content');
            content.innerHTML = `
                <div class="document-detail">
                    <div class="document-actions">
                        <button class="btn btn-secondary" onclick="loadDocuments('${currentContainer}')">← Back to List</button>
                        <button class="btn btn-success" onclick="copyDocument('${documentId}')">Copy JSON</button>
                        <button class="btn btn-success btn-view-formatted" onclick="viewFormatted('${documentId}')">View Formatted</button>
                    </div>
                    <h2 style="font-size: 1.2rem; margin-bottom: 1rem; word-break: break-all;">${documentId}</h2>
                    <div class="json-viewer" id="jsonContent">${syntaxHighlight(JSON.stringify(doc, null, 2))}</div>
                </div>
            `;
        }
        
        function syntaxHighlight(json) {
            return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
                let cls = 'json-number';
                if (/^"/.test(match)) {
                    if (/:$/.test(match)) {
                        cls = 'json-key';
                    } else {
                        cls = 'json-string';
                    }
                } else if (/true|false/.test(match)) {
                    cls = 'json-boolean';
                } else if (/null/.test(match)) {
                    cls = 'json-null';
                }
                return '<span class="' + cls + '">' + match + '</span>';
            });
        }
        
        function copyDocument(documentId) {
            const doc = allDocuments.find(d => d.id === documentId);
            if (!doc) return;
            
            navigator.clipboard.writeText(JSON.stringify(doc, null, 2))
                .then(() => alert('Document copied to clipboard!'))
                .catch(err => alert('Failed to copy: ' + err));
        }
        
        document.getElementById('searchInput').addEventListener('input', (e) => {
            const search = e.target.value.toLowerCase();
            const filtered = allContainers.filter(c => 
                c.id.toLowerCase().includes(search)
            );
            displayContainers(filtered);
        });
        
        function showError(message) {
            document.getElementById('content').innerHTML = `
                <div class="error">${message}</div>
            `;
        }
        
        function viewFormatted(documentId) {
            const doc = allDocuments.find(d => d.id === documentId);
            if (!doc) return;
            
            const modal = document.getElementById('formattedModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalBody = document.getElementById('modalBody');
            
            // Set title
            modalTitle.textContent = doc.id || 'Document View';
            
            // Format the document based on its type/container
            let formattedHtml = '<div class="formatted-content">';
            
            // Handle different document types
            if (currentContainer === 'messages') {
                formattedHtml += formatMessage(doc);
            } else if (currentContainer === 'audit') {
                formattedHtml += formatAudit(doc);
            } else if (currentContainer === 'documents') {
                formattedHtml += formatDocument(doc);
            } else if (currentContainer === 'logs') {
                formattedHtml += formatLog(doc);
            } else {
                formattedHtml += formatGeneric(doc);
            }
            
            formattedHtml += '</div>';
            modalBody.innerHTML = formattedHtml;
            modal.style.display = 'block';
        }
        
        function formatMessage(doc) {
            let html = '<h3>Message Details</h3>';
            
            if (doc.from) html += `<div class="field"><div class="field-label">From:</div><div class="field-value">${doc.from}</div></div>`;
            if (doc.to) html += `<div class="field"><div class="field-label">To:</div><div class="field-value">${doc.to}</div></div>`;
            if (doc.subject) html += `<div class="field"><div class="field-label">Subject:</div><div class="field-value">${doc.subject}</div></div>`;
            if (doc.timestamp) html += `<div class="field"><div class="field-label">Time:</div><div class="field-value timestamp">${new Date(doc.timestamp).toLocaleString()}</div></div>`;
            if (doc.type) html += `<div class="field"><div class="field-label">Type:</div><div class="field-value">${doc.type}</div></div>`;
            if (doc.priority) html += `<div class="field"><div class="field-label">Priority:</div><div class="field-value">${doc.priority}</div></div>`;
            
            if (doc.content) {
                html += '<h3>Content</h3>';
                html += `<div class="content-box">${doc.content.replace(/\n/g, '<br>')}</div>`;
            }
            
            if (doc.tags && doc.tags.length > 0) {
                html += '<h3>Tags</h3><div class="tags">';
                doc.tags.forEach(tag => {
                    html += `<span class="tag">${tag}</span>`;
                });
                html += '</div>';
            }
            
            return html;
        }
        
        function formatAudit(doc) {
            let html = '<h3>Audit Record</h3>';
            
            if (doc.audit_type) html += `<div class="field"><div class="field-label">Audit Type:</div><div class="field-value">${doc.audit_type}</div></div>`;
            if (doc.document_name) html += `<div class="field"><div class="field-label">Document:</div><div class="field-value">${doc.document_name}</div></div>`;
            if (doc.status) html += `<div class="field"><div class="field-label">Status:</div><div class="field-value">${doc.status}</div></div>`;
            if (doc.compliance_score) html += `<div class="field"><div class="field-label">Compliance Score:</div><div class="field-value">${doc.compliance_score}%</div></div>`;
            if (doc.responsible_agent) html += `<div class="field"><div class="field-label">Responsible Agent:</div><div class="field-value">${doc.responsible_agent}</div></div>`;
            
            if (doc.findings) {
                html += '<h3>Findings</h3>';
                html += `<div class="content-box">${doc.findings.replace(/\n/g, '<br>')}</div>`;
            }
            
            if (doc.action_required) {
                html += '<h3>Action Required</h3>';
                html += `<div class="content-box">${doc.action_required.replace(/\n/g, '<br>')}</div>`;
            }
            
            return html;
        }
        
        function formatDocument(doc) {
            let html = '<h3>Document Information</h3>';
            
            if (doc.type) html += `<div class="field"><div class="field-label">Type:</div><div class="field-value">${doc.type}</div></div>`;
            if (doc.category) html += `<div class="field"><div class="field-label">Category:</div><div class="field-value">${doc.category}</div></div>`;
            if (doc.status) html += `<div class="field"><div class="field-label">Status:</div><div class="field-value">${doc.status}</div></div>`;
            if (doc.owner) html += `<div class="field"><div class="field-label">Owner:</div><div class="field-value">${doc.owner}</div></div>`;
            if (doc.audience) html += `<div class="field"><div class="field-label">Audience:</div><div class="field-value">${doc.audience}</div></div>`;
            
            if (doc.content) {
                html += '<h3>Content</h3>';
                html += `<div class="content-box">${doc.content.replace(/\n/g, '<br>')}</div>`;
            }
            
            if (doc.tags && doc.tags.length > 0) {
                html += '<h3>Tags</h3><div class="tags">';
                doc.tags.forEach(tag => {
                    html += `<span class="tag">${tag}</span>`;
                });
                html += '</div>';
            }
            
            return html;
        }
        
        function formatLog(doc) {
            let html = '<h3>Log Entry</h3>';
            
            if (doc.logType) html += `<div class="field"><div class="field-label">Log Type:</div><div class="field-value">${doc.logType}</div></div>`;
            if (doc.agentName) html += `<div class="field"><div class="field-label">Agent:</div><div class="field-value">${doc.agentName}</div></div>`;
            if (doc.timestamp) html += `<div class="field"><div class="field-label">Time:</div><div class="field-value timestamp">${new Date(doc.timestamp).toLocaleString()}</div></div>`;
            if (doc.sessionId) html += `<div class="field"><div class="field-label">Session ID:</div><div class="field-value">${doc.sessionId}</div></div>`;
            
            if (doc.action) {
                html += '<h3>Action</h3>';
                html += `<div class="content-box">${doc.action.replace(/\n/g, '<br>')}</div>`;
            }
            
            if (doc.details) {
                html += '<h3>Details</h3>';
                html += `<div class="content-box">${JSON.stringify(doc.details, null, 2).replace(/\n/g, '<br>').replace(/ /g, '&nbsp;')}</div>`;
            }
            
            return html;
        }
        
        function formatGeneric(doc) {
            let html = '<h3>Document Details</h3>';
            
            // Show all fields in a generic way
            Object.keys(doc).forEach(key => {
                if (key.startsWith('_')) return; // Skip internal fields
                
                const value = doc[key];
                if (value === null || value === undefined) return;
                
                if (typeof value === 'object') {
                    html += `<div class="field"><div class="field-label">${key}:</div><div class="field-value">${JSON.stringify(value, null, 2).replace(/\n/g, '<br>').replace(/ /g, '&nbsp;')}</div></div>`;
                } else {
                    html += `<div class="field"><div class="field-label">${key}:</div><div class="field-value">${value}</div></div>`;
                }
            });
            
            return html;
        }
        
        function closeModal() {
            document.getElementById('formattedModal').style.display = 'none';
        }
        
        function closeModalOnOverlay(event) {
            if (event.target.classList.contains('modal-overlay')) {
                closeModal();
            }
        }
        
        // Add keyboard support for closing modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeModal();
            }
        });
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            // DOM is already ready
            init();
        }
    </script>
</body>
</html>'''
    
    return html_content

if __name__ == '__main__':
    print("🌐 Starting Cosmos DB Viewer Server...")
    
    if init_db():
        print("✅ Database connection established")
        print("\n📋 Available endpoints:")
        print("   http://localhost:5001/viewer - Web viewer interface")
        print("   http://localhost:5001/api/containers - List all containers")
        print("   http://localhost:5001/api/stats - Database statistics")
        print("\n🚀 Server running on http://localhost:5001")
        print("   Press Ctrl+C to stop")
        
        app.run(host='0.0.0.0', port=5001, debug=False)
    else:
        print("❌ Failed to initialize database connection")