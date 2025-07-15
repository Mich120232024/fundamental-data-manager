#!/usr/bin/env python3
"""
User Management Dashboard - Main Flask Application
Enhanced Cosmos DB viewer with formatted display and message composition
"""

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

from flask import Flask, jsonify, send_from_directory, request, render_template_string
from flask_cors import CORS
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Import cosmos manager from the scripts directory
scripts_dir = Path(__file__).parent.parent.parent / 'Engineering Workspace' / 'scripts'
sys.path.insert(0, str(scripts_dir))
from cosmos_db_manager import get_db_manager
import hashlib
from collections import defaultdict
import glob
import markdown

# Import memory layer API
try:
    from memory_layer_api import memory_api
    MEMORY_API_AVAILABLE = True
except ImportError:
    print("Memory layer API not available")
    MEMORY_API_AVAILABLE = False

# Import live data API
try:
    from live_data_api import live_data_api
    LIVE_DATA_API_AVAILABLE = True
except ImportError:
    print("Live data API not available")
    LIVE_DATA_API_AVAILABLE = False

# Import message status API
try:
    from message_status_api import message_status_api
    MESSAGE_STATUS_API_AVAILABLE = True
except ImportError:
    print("Message status API not available")
    MESSAGE_STATUS_API_AVAILABLE = False

# Import log collection API
try:
    from log_collection_api import log_collection_api
    LOG_COLLECTION_API_AVAILABLE = True
except ImportError:
    print("Log collection API not available")
    LOG_COLLECTION_API_AVAILABLE = False

# Import Gremlin API
try:
    from gremlin_api import gremlin_api
    GREMLIN_API_AVAILABLE = True
except ImportError:
    print("Gremlin API not available")
    GREMLIN_API_AVAILABLE = False

# Import System API
try:
    from system_api import system_api
    SYSTEM_API_AVAILABLE = True
except ImportError:
    print("System API not available")
    SYSTEM_API_AVAILABLE = False

# Import Graph Diagnostic API
try:
    from graph_diagnostic import graph_diagnostic
    GRAPH_DIAGNOSTIC_AVAILABLE = True
except ImportError:
    print("Graph diagnostic API not available")
    GRAPH_DIAGNOSTIC_AVAILABLE = False

# Import Graph Test API  
try:
    from graph_test_endpoint import graph_test
    GRAPH_TEST_AVAILABLE = True
except ImportError:
    print("Graph test API not available")
    GRAPH_TEST_AVAILABLE = False

# Import Static Cytoscape API
try:
    from static_cytoscape import static_cytoscape
    STATIC_CYTOSCAPE_AVAILABLE = True
except ImportError:
    print("Static Cytoscape API not available")
    STATIC_CYTOSCAPE_AVAILABLE = False
import mimetypes

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# Register memory layer API blueprint if available
if MEMORY_API_AVAILABLE:
    app.register_blueprint(memory_api)
    print("Memory layer API registered")

# Register live data API blueprint if available
if LIVE_DATA_API_AVAILABLE:
    app.register_blueprint(live_data_api)
    print("Live data API registered")

# Register message status API blueprint if available
if MESSAGE_STATUS_API_AVAILABLE:
    app.register_blueprint(message_status_api)
    print("Message status API registered")

# Register log collection API blueprint if available
if LOG_COLLECTION_API_AVAILABLE:
    app.register_blueprint(log_collection_api)
    print("Log collection API registered")

# Register Gremlin API blueprint if available
if GREMLIN_API_AVAILABLE:
    app.register_blueprint(gremlin_api)
    print("Gremlin API registered")

# Register System API blueprint if available
if SYSTEM_API_AVAILABLE:
    app.register_blueprint(system_api)
    print("System API registered")

# Register Graph Diagnostic API blueprint if available
if GRAPH_DIAGNOSTIC_AVAILABLE:
    app.register_blueprint(graph_diagnostic)
    print("Graph diagnostic API registered")

# Register Graph Test API blueprint if available
if GRAPH_TEST_AVAILABLE:
    app.register_blueprint(graph_test)
    print("Graph test API registered")

# Register Static Cytoscape API blueprint if available
if STATIC_CYTOSCAPE_AVAILABLE:
    app.register_blueprint(static_cytoscape)
    print("Static Cytoscape API registered")

# Global database connection
db = None

def init_db():
    """Initialize database connection"""
    global db
    try:
        db = get_db_manager()
        
        # Ensure required containers exist
        ensure_required_containers()
        
        return True
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return False

def ensure_required_containers():
    """Ensure all required containers exist in Cosmos DB"""
    if not db:
        return
        
    required_containers = [
        {'id': 'agent_session_logs', 'partition_key': '/agent_name'},
        {'id': 'agent_logs', 'partition_key': '/agent_name'},
        {'id': 'system_inbox', 'partition_key': '/to'},
        {'id': 'identity_cards', 'partition_key': '/agent_name'},
        {'id': 'working_contexts', 'partition_key': '/agent_name'},
        {'id': 'journal_entries', 'partition_key': '/agent_name'},
        {'id': 'memory_contexts', 'partition_key': '/agent_name'}
    ]
    
    try:
        database = db.client.get_database_client(db.database_name)
        existing_containers = [container['id'] for container in database.list_containers()]
        
        for container_info in required_containers:
            if container_info['id'] not in existing_containers:
                print(f"Creating missing container: {container_info['id']}")
                database.create_container_if_not_exists(
                    id=container_info['id'],
                    partition_key={'paths': [container_info['partition_key']], 'kind': 'Hash'}
                )
                print(f"Successfully created container: {container_info['id']}")
            else:
                print(f"Container already exists: {container_info['id']}")
                
    except Exception as e:
        print(f"Error ensuring containers exist: {e}")

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'User Management Dashboard',
        'version': '1.0.0',
        'database': 'connected' if db else 'disconnected'
    })

@app.route('/')
def index():
    """Serve the main dashboard"""
    return send_from_directory('../frontend', 'dashboard.html')

@app.route('/v1')
def index_v1():
    """Serve the legacy dashboard"""
    return send_from_directory('../frontend', 'dashboard-legacy.html')

@app.route('/fixed')
def index_fixed():
    """Serve the fixed minimal dashboard"""
    return send_from_directory('../frontend', 'dashboard-fixed.html')


@app.route('/debug')
def debug():
    """Serve the debug version"""
    return send_from_directory('../frontend', 'debug.html')

@app.route('/blob-test')
def blob_test():
    """Serve the blob storage test page"""
    return send_from_directory('../frontend', 'blob-test.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/css/<path:filename>')
def css_files(filename):
    """Serve CSS files"""
    return send_from_directory('../frontend/css', filename)

@app.route('/js/<path:filename>')
def js_files(filename):
    """Serve JavaScript files"""
    return send_from_directory('../frontend/js', filename)

@app.route('/graph-explorer-fixed')
def graph_explorer_fixed():
    """Serve the fixed graph explorer"""
    return send_from_directory('../frontend', 'graph-explorer-fixed.html')

@app.route('/graph-standalone')
def graph_standalone():
    """Serve the standalone graph test"""
    return send_from_directory('../frontend', 'graph-standalone.html')

@app.route('/cytoscape-test')
def cytoscape_test():
    """Serve the basic Cytoscape test"""
    return send_from_directory('../frontend', 'cytoscape-test.html')

@app.route('/graph-safari-fix')
def graph_safari_fix():
    """Serve the Safari-compatible graph visualization"""
    return send_from_directory('../frontend', 'graph-safari-fix.html')

@app.route('/minimal')
def index_minimal():
    """Serve the minimal test dashboard"""
    return send_from_directory('../frontend', 'dashboard-minimal.html')

@app.route('/safari-fetch-test.html')
def safari_fetch_test():
    """Serve the Safari fetch test page"""
    return send_from_directory('../frontend', 'safari-fetch-test.html')

@app.route('/test-fetch.html')
def test_fetch():
    """Serve the fetch test page"""
    return send_from_directory('../frontend', 'test-fetch.html')

@app.route('/simple-test.html')
def simple_test():
    """Serve the simple test page"""
    return send_from_directory('../frontend', 'simple-test.html')

@app.route('/api/containers')
def get_containers():
    """Get all containers with document counts - with Redis caching"""
    try:
        # Try to get from Redis cache first
        cache_key = "dashboard:containers"
        
        # Import redis at the top if not already
        import redis
        import json
        
        # Create Redis connection
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD'),
            ssl=os.getenv('REDIS_SSL', 'True').lower() == 'true',
            decode_responses=True,
            db=0  # Use DB 0 for general caching
        )
        
        # Try to get cached containers
        try:
            cached_containers = redis_client.get(cache_key)
            if cached_containers:
                containers_data = json.loads(cached_containers)
                return jsonify({
                    'success': True,
                    'containers': containers_data,
                    'cached': True
                })
        except:
            pass  # If Redis fails, continue to fetch from DB
        
        # Fetch from database
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
        
        sorted_containers = sorted(containers, key=lambda x: x['count'], reverse=True)
        
        # Cache the results for 5 minutes
        try:
            redis_client.setex(
                cache_key,
                300,  # 5 minutes TTL
                json.dumps(sorted_containers)
            )
        except:
            pass  # If Redis fails, still return the data
        
        return jsonify({
            'success': True,
            'containers': sorted_containers,
            'cached': False
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
        
        # Try to find document
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
            'count': len(results),
            'search_term': search_term
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/message', methods=['POST'])
def send_message():
    """Send a new message to the database"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['to', 'subject', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create message document
        timestamp = datetime.utcnow().isoformat() + 'Z'
        message_id = f"msg_{timestamp.replace(':', '').replace('-', '').replace('.', '_')}"
        
        message_doc = {
            'id': message_id,
            'from': data.get('from', 'USER_DASHBOARD'),
            'to': data['to'],
            'subject': data['subject'],
            'content': data['content'],
            'type': data.get('type', 'USER_MESSAGE'),
            'priority': data.get('priority', 'medium'),
            'timestamp': timestamp,
            'partitionKey': timestamp[:7],  # YYYY-MM format
            'requiresResponse': data.get('requiresResponse', False),
            'status': 'sent',
            'tags': data.get('tags', [])
        }
        
        # Store in messages container
        database = db.client.get_database_client(db.database_name)
        container = database.get_container_client('system_inbox')
        
        result = container.create_item(message_doc)
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully',
            'document_id': result['id'],
            'timestamp': timestamp
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """Get database statistics with Redis caching"""
    try:
        # Try to get from Redis cache first
        cache_key = "dashboard:stats"
        
        # Import redis at the top if not already
        import redis
        import json
        from datetime import datetime
        
        # Create Redis connection
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD'),
            ssl=os.getenv('REDIS_SSL', 'True').lower() == 'true',
            decode_responses=True,
            db=0  # Use DB 0 for general caching
        )
        
        # Try to get cached stats
        try:
            cached_stats = redis_client.get(cache_key)
            if cached_stats:
                stats_data = json.loads(cached_stats)
                # Add cache indicator
                stats_data['cached'] = True
                stats_data['cache_timestamp'] = redis_client.ttl(cache_key)
                return jsonify({
                    'success': True,
                    'stats': stats_data
                })
        except:
            pass  # If Redis fails, continue to fetch from DB
        
        # Fetch from database
        database = db.client.get_database_client(db.database_name)
        stats = {
            'database': db.database_name,
            'endpoint': db.endpoint,
            'containers': {},
            'totalDocuments': 0,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
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
        
        # Cache the results for 5 minutes
        try:
            redis_client.setex(
                cache_key,
                300,  # 5 minutes TTL
                json.dumps(stats)
            )
        except:
            pass  # If Redis fails, still return the data
        
        stats['cached'] = False
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/logs/analyze', methods=['GET'])
def analyze_logs():
    """Analyze logs for duplicates and terminal history"""
    try:
        if not db:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500
        
        container = db.database.get_container_client('logs')
        query = "SELECT * FROM c"
        all_logs = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        # Analyze duplicates
        seen_hashes = {}
        duplicates = []
        terminal_logs = []
        agent_logs = []
        log_stats = defaultdict(int)
        
        for log in all_logs:
            # Create hash
            content_hash = create_log_hash(log)
            
            if content_hash in seen_hashes:
                duplicates.append({
                    'original_id': seen_hashes[content_hash]['id'],
                    'duplicate_id': log.get('id', 'unknown'),
                    'type': log.get('logType', log.get('type', 'unknown'))
                })
            else:
                seen_hashes[content_hash] = log
            
            # Categorize
            if 'terminal' in str(log).lower() or 'conversation_flow' in log:
                terminal_logs.append(log)
            elif log.get('agentName'):
                agent_logs.append(log)
            
            # Stats
            log_type = log.get('logType', log.get('type', 'unknown'))
            log_stats[log_type] += 1
        
        # Verify terminal logs
        valid_terminal = 0
        for log in terminal_logs:
            if 'conversation_flow' in log:
                flow = log['conversation_flow']
                has_user = any(item.get('type') == 'user_input' for item in flow)
                has_claude = any(item.get('type') == 'claude_response' for item in flow)
                if has_user and has_claude:
                    valid_terminal += 1
            elif 'capture_completeness' in log:
                valid_terminal += 1
        
        return jsonify({
            'success': True,
            'analysis': {
                'total_logs': len(all_logs),
                'duplicates': len(duplicates),
                'duplicate_details': duplicates[:10],  # First 10
                'terminal_logs': len(terminal_logs),
                'valid_terminal_logs': valid_terminal,
                'agent_logs': len(agent_logs),
                'log_types': dict(log_stats)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logs/remove-duplicates', methods=['POST'])
def remove_duplicate_logs():
    """Remove duplicate logs from database"""
    try:
        if not db:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500
        
        container = db.database.get_container_client('logs')
        
        # Get duplicate IDs from request
        data = request.get_json()
        duplicate_ids = data.get('duplicate_ids', [])
        
        if not duplicate_ids:
            return jsonify({'success': False, 'error': 'No duplicate IDs provided'}), 400
        
        removed = 0
        errors = []
        
        for dup in duplicate_ids:
            try:
                container.delete_item(
                    item=dup['id'], 
                    partition_key=dup.get('partitionKey', dup.get('agentName', 'unknown'))
                )
                removed += 1
            except Exception as e:
                errors.append({'id': dup['id'], 'error': str(e)})
        
        return jsonify({
            'success': True,
            'removed': removed,
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/messages/analyze', methods=['GET'])
def analyze_messages():
    """Analyze messages for duplicates"""
    try:
        if not db:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500
        
        container = db.database.get_container_client('system_inbox')
        query = "SELECT * FROM c"
        all_messages = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        # Group by content hash
        content_groups = defaultdict(list)
        
        for msg in all_messages:
            key_content = f"{msg.get('subject', '')}-{msg.get('content', '')}-{msg.get('from', '')}-{msg.get('to', '')}"
            content_hash = hashlib.md5(key_content.encode()).hexdigest()
            content_groups[content_hash].append(msg)
        
        # Find duplicates
        duplicates = []
        total_duplicates = 0
        
        for group in content_groups.values():
            if len(group) > 1:
                total_duplicates += len(group) - 1
                duplicates.append({
                    'subject': group[0].get('subject', 'No subject'),
                    'copies': len(group),
                    'duplicate_ids': [msg['id'] for msg in group[1:]]  # All except first
                })
        
        return jsonify({
            'success': True,
            'analysis': {
                'total_messages': len(all_messages),
                'duplicate_groups': len(duplicates),
                'total_duplicates': total_duplicates,
                'duplicate_details': duplicates[:10]  # First 10 groups
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/messages/remove-duplicates', methods=['POST'])
def remove_duplicate_messages():
    """Remove duplicate messages"""
    try:
        if not db:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500
        
        container = db.database.get_container_client('system_inbox')
        data = request.get_json()
        duplicate_ids = data.get('duplicate_ids', [])
        
        if not duplicate_ids:
            return jsonify({'success': False, 'error': 'No duplicate IDs provided'}), 400
        
        removed = 0
        errors = []
        
        # Get the actual partition key values for each message
        for msg_id in duplicate_ids:
            try:
                # First get the message to find its partition key
                msg_query = f"SELECT * FROM c WHERE c.id = '{msg_id}'"
                msg_results = list(container.query_items(query=msg_query, enable_cross_partition_query=True))
                
                if msg_results:
                    msg = msg_results[0]
                    partition_key = msg.get('partitionKey', '2025-06')  # Default fallback
                    container.delete_item(item=msg_id, partition_key=partition_key)
                    removed += 1
                else:
                    errors.append({'id': msg_id, 'error': 'Message not found'})
            except Exception as e:
                errors.append({'id': msg_id, 'error': str(e)})
        
        return jsonify({
            'success': True,
            'removed': removed,
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def create_log_hash(log):
    """Create hash from log content to identify duplicates"""
    key_fields = []
    
    if 'conversation_flow' in log:
        key_fields.append(log.get('session_metadata', {}).get('session_id', ''))
        key_fields.append(str(log.get('conversation_flow', [])))
    elif log.get('agentName'):
        key_fields.append(log.get('agentName', ''))
        key_fields.append(log.get('action', ''))
        key_fields.append(log.get('timestamp', ''))
    else:
        key_fields.append(str(log.get('content', '')))
        key_fields.append(str(log.get('complete_conversation_flow', '')))
        
    content = '|'.join(key_fields)
    return hashlib.md5(content.encode()).hexdigest()

@app.route('/api/containers/<container_name>/documents', methods=['POST'])
def create_document(container_name):
    """Create a new document in specified container"""
    try:
        if not db:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500
        
        # Validate container exists
        containers = [c['id'] for c in db.database.list_containers()]
        if container_name not in containers:
            return jsonify({'success': False, 'error': f'Container {container_name} not found'}), 404
        
        container = db.database.get_container_client(container_name)
        data = request.get_json()
        
        # Check if this is a large session upload
        if 'raw_content' in data and len(data.get('raw_content', '')) > 1500000:  # ~1.5MB
            # Handle large uploads by chunking
            return handle_large_session_upload(container, data)
        
        # Ensure required fields
        if 'id' not in data:
            data['id'] = f"{container_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat() + 'Z'
        
        # Create item
        result = container.create_item(body=data)
        
        return jsonify({
            'success': True,
            'document_id': result['id'],
            'container': container_name
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def handle_large_session_upload(container, data):
    """Handle large session uploads by chunking"""
    try:
        raw_content = data.pop('raw_content', '')
        content_size = len(raw_content)
        chunk_size = 1000000  # 1MB chunks
        
        # Create master record
        master_id = data['id']
        master_doc = {
            **data,
            'id': master_id,
            'type': 'TERMINAL_SESSION_MASTER',
            'content_size': content_size,
            'chunk_count': (content_size // chunk_size) + 1,
            'chunks': []
        }
        
        # Split content into chunks
        chunk_ids = []
        for i in range(0, content_size, chunk_size):
            chunk_id = f"{master_id}_chunk_{i // chunk_size}"
            chunk_doc = {
                'id': chunk_id,
                'master_id': master_id,
                'chunk_index': i // chunk_size,
                'content': raw_content[i:i + chunk_size],
                'partitionKey': data.get('partitionKey', 'terminal_conversations')
            }
            container.create_item(body=chunk_doc)
            chunk_ids.append(chunk_id)
        
        # Update master with chunk references
        master_doc['chunks'] = chunk_ids
        container.create_item(body=master_doc)
        
        return jsonify({
            'success': True,
            'document_id': master_id,
            'message': f'Large session uploaded in {len(chunk_ids)} chunks',
            'total_size': f'{content_size / 1024 / 1024:.1f} MB'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Chunking error: {str(e)}'}), 500

@app.route('/api/docs/structure')
def get_docs_structure():
    """Get documentation structure from database_operations directory"""
    try:
        # Base path for documentation
        docs_base = Path(__file__).parent.parent.parent
        
        structure = {}
        stats = {
            'total_files': 0,
            'categories': 0,
            'examples': 0,
            'total_size': 0
        }
        
        # Define categories to scan
        categories = {
            'System Overview': docs_base / 'System Enforcement Workspace',
            'Engineering': docs_base / 'Engineering Workspace',
            'Analytics': docs_base / 'Analytics & Data Workspace',
            'Azure Infrastructure': docs_base / 'Azure Infrastructure Management',
            'Software Engineering': docs_base / 'Software Engineering Workspace',
            'Documentation': docs_base / 'System Enforcement Workspace' / 'agent_initialization',
            'Operational Tools': docs_base / 'System Enforcement Workspace' / 'Operational_Tools'
        }
        
        for category_name, category_path in categories.items():
            if category_path.exists():
                files = []
                
                # Get markdown files
                for md_file in category_path.glob('*.md'):
                    rel_path = str(md_file.relative_to(docs_base))
                    file_stat = md_file.stat()
                    files.append({
                        'name': md_file.name,
                        'path': rel_path,
                        'size': file_stat.st_size,
                        'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                    })
                    stats['total_files'] += 1
                    stats['total_size'] += file_stat.st_size
                    if category_name == 'examples':
                        stats['examples'] += 1
                
                # Get Python files for examples
                if category_name in ['examples', 'cosmos_operations', 'serverless', 'tests']:
                    for py_file in category_path.glob('*.py'):
                        if not py_file.name.startswith('__'):
                            rel_path = str(py_file.relative_to(docs_base))
                            file_stat = py_file.stat()
                            files.append({
                                'name': py_file.name,
                                'path': rel_path,
                                'size': file_stat.st_size,
                                'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                            })
                            stats['total_files'] += 1
                            stats['total_size'] += file_stat.st_size
                
                if files:
                    structure[category_name] = sorted(files, key=lambda x: x['name'])
                    stats['categories'] += 1
        
        return jsonify({
            'success': True,
            'structure': structure,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/docs/content')
def get_doc_content():
    """Get content of a specific documentation file"""
    try:
        file_path = request.args.get('path')
        if not file_path:
            return jsonify({'success': False, 'error': 'No path provided'}), 400
        
        # Security check - prevent directory traversal
        if '..' in file_path or file_path.startswith('/'):
            return jsonify({'success': False, 'error': 'Invalid path'}), 400
        
        # Base path
        docs_base = Path(__file__).parent.parent.parent
        full_path = docs_base / file_path
        
        if not full_path.exists():
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Read file content
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get file info
            file_stat = full_path.stat()
            
            return jsonify({
                'success': True,
                'content': content,
                'path': file_path,
                'size': file_stat.st_size,
                'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                'type': 'markdown' if file_path.endswith('.md') else 'python'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': f'Failed to read file: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/docs/search')
def search_docs():
    """Search documentation content"""
    try:
        search_term = request.args.get('q', '').lower()
        if not search_term:
            return jsonify({'success': False, 'error': 'Search term required'}), 400
        
        results = []
        docs_base = Path(__file__).parent.parent.parent
        
        # Search in all markdown and Python files
        for pattern in ['**/*.md', '**/*.py']:
            for file_path in docs_base.glob(pattern):
                if file_path.name.startswith('__'):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Search in content and filename
                    if search_term in content.lower() or search_term in file_path.name.lower():
                        # Find matching lines
                        matches = []
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if search_term in line.lower():
                                matches.append({
                                    'line': i + 1,
                                    'text': line.strip()[:100] + '...' if len(line.strip()) > 100 else line.strip()
                                })
                                if len(matches) >= 3:  # Limit matches per file
                                    break
                        
                        rel_path = str(file_path.relative_to(docs_base))
                        results.append({
                            'path': rel_path,
                            'name': file_path.name,
                            'matches': matches,
                            'match_count': content.lower().count(search_term)
                        })
                
                except Exception:
                    pass  # Skip files that can't be read
        
        # Sort by match count
        results.sort(key=lambda x: x['match_count'], reverse=True)
        
        return jsonify({
            'success': True,
            'results': results[:20],  # Limit to top 20 results
            'total': len(results),
            'search_term': search_term
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting User Management Dashboard...")
    
    if init_db():
        print("✅ Database connection established")
        print("\\n📋 Available endpoints:")
        print("   http://localhost:5001/ - Main dashboard")
        print("   http://localhost:5001/debug - Debug mode")
        print("   http://localhost:5001/api/containers - API endpoints")
        
        print("\\n🌐 User Management Dashboard running on http://localhost:5001")
        print("   Press Ctrl+C to stop")
        
        app.run(host='127.0.0.1', port=5001, debug=False)
    else:
        print("❌ Failed to initialize database connection")