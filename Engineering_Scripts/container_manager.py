#!/usr/bin/env python3
"""
Container Management & Naming Schema Enforcement
Engineering-controlled container operations
"""

import re
from datetime import datetime
from cosmos_db_manager import get_db_manager

class ContainerManager:
    """Enforce container naming and management standards"""
    
    # Approved container patterns
    ALLOWED_CONTAINERS = {
        'messages': {'partition': '/partitionKey', 'purpose': 'System messaging'},
        'logs': {'partition': '/partitionKey', 'purpose': 'Terminal and system logs'},
        'audit': {'partition': '/category', 'purpose': 'Audit trail'},
        'documents': {'partition': '/type', 'purpose': 'Document storage'},
        'metadata': {'partition': '/entity_type', 'purpose': 'System metadata'},
        'agent_context_memory': {'partition': '/agentName', 'purpose': 'Agent memory'},
        'processes': {'partition': '/processType', 'purpose': 'Process tracking'},
        'enforcement': {'partition': '/enforcement_type', 'purpose': 'System enforcement'},
        'institutional-data-center': {'partition': '/category', 'purpose': 'Research data'},
    }
    
    def __init__(self):
        self.db = get_db_manager()
        
    def validate_container_name(self, name):
        """Validate container name against standards"""
        # Must be lowercase, alphanumeric with hyphens/underscores
        pattern = r'^[a-z][a-z0-9_-]*$'
        if not re.match(pattern, name):
            return False, "Container names must be lowercase alphanumeric with - or _"
        
        # Check against allowed list
        if name not in self.ALLOWED_CONTAINERS:
            return False, f"Container '{name}' not in approved list. Request approval from Engineering."
        
        return True, "Valid"
    
    def create_container(self, name, partition_key_path=None):
        """Create container with enforced standards"""
        # Validate name
        valid, message = self.validate_container_name(name)
        if not valid:
            raise ValueError(f"Invalid container name: {message}")
        
        # Use standard partition key if not specified
        if not partition_key_path:
            partition_key_path = self.ALLOWED_CONTAINERS[name]['partition']
        
        # Check if exists
        existing = [c['id'] for c in self.db.database.list_containers()]
        if name in existing:
            return {'status': 'exists', 'container': name}
        
        # Create with standards
        container = self.db.database.create_container(
            id=name,
            partition_key={'paths': [partition_key_path], 'kind': 'Hash'}
        )
        
        # Log creation
        self._log_container_operation('create', name, partition_key_path)
        
        return {'status': 'created', 'container': name, 'partition_key': partition_key_path}
    
    def list_containers(self):
        """List containers with health status"""
        containers = []
        for container in self.db.database.list_containers():
            container_client = self.db.database.get_container_client(container['id'])
            
            # Get basic stats
            try:
                count_query = "SELECT VALUE COUNT(1) FROM c"
                count = list(container_client.query_items(
                    query=count_query, 
                    enable_cross_partition_query=True
                ))[0]
            except:
                count = 0
            
            containers.append({
                'name': container['id'],
                'partition_key': container.get('partitionKey', {}).get('paths', []),
                'document_count': count,
                'approved': container['id'] in self.ALLOWED_CONTAINERS,
                'purpose': self.ALLOWED_CONTAINERS.get(container['id'], {}).get('purpose', 'Unknown')
            })
            
        return containers
    
    def enforce_naming_standards(self):
        """Check all containers against standards"""
        violations = []
        containers = self.list_containers()
        
        for container in containers:
            if not container['approved']:
                violations.append({
                    'container': container['name'],
                    'issue': 'Not in approved container list',
                    'action': 'Request approval or migrate data'
                })
        
        return violations
    
    def _log_container_operation(self, operation, container_name, details=None):
        """Log container operations"""
        log_entry = {
            'operation': operation,
            'container': container_name,
            'timestamp': datetime.now().isoformat() + 'Z',
            'operator': 'ENGINEERING',
            'details': details,
            'partitionKey': 'container_operations'
        }
        
        logs_container = self.db.database.get_container_client('logs')
        logs_container.create_item(body=log_entry)

# CLI interface
if __name__ == "__main__":
    import sys
    
    manager = ContainerManager()
    
    if len(sys.argv) < 2:
        print("Container Manager")
        print("Usage:")
        print("  container_manager.py list")
        print("  container_manager.py create <name> [partition_key]")
        print("  container_manager.py validate <name>")
        print("  container_manager.py enforce")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        containers = manager.list_containers()
        print(f"{'Container':<30} {'Documents':<10} {'Status':<15} {'Purpose'}")
        print("-" * 80)
        for c in containers:
            status = "✅ Approved" if c['approved'] else "⚠️  Unapproved"
            print(f"{c['name']:<30} {c['document_count']:<10} {status:<15} {c['purpose']}")
    
    elif cmd == "create" and len(sys.argv) >= 3:
        name = sys.argv[2]
        partition = sys.argv[3] if len(sys.argv) > 3 else None
        try:
            result = manager.create_container(name, partition)
            print(f"✅ Container {result['status']}: {result['container']}")
        except ValueError as e:
            print(f"❌ Error: {e}")
    
    elif cmd == "validate" and len(sys.argv) >= 3:
        name = sys.argv[2]
        valid, message = manager.validate_container_name(name)
        print(f"{'✅' if valid else '❌'} {name}: {message}")
    
    elif cmd == "enforce":
        violations = manager.enforce_naming_standards()
        if violations:
            print("⚠️  Naming Standard Violations:")
            for v in violations:
                print(f"  - {v['container']}: {v['issue']} → {v['action']}")
        else:
            print("✅ All containers comply with standards")