#!/usr/bin/env python3
"""
EMERGENCY FILE MIGRATION - Fix system in next 25 minutes
"""

import os
import glob
import json
from datetime import datetime
from cosmos_db_manager import CosmosDBManager

def migrate_agent_files():
    db = CosmosDBManager()
    db.container = db.database.get_container_client('documents')
    
    workspace = '/Users/mikaeleage/Research & Analytics Services/Digital Labor Workspace/Agent Roster'
    pattern = os.path.join(workspace, '**/*.md')
    files = glob.glob(pattern, recursive=True)
    
    print(f'=== EMERGENCY MIGRATION: {len(files)} FILES ===')
    
    migrated = 0
    failed = 0
    
    for file_path in files:
        try:
            # Read file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract agent info from path
            rel_path = os.path.relpath(file_path, workspace)
            parts = rel_path.split('/')
            
            # Determine agent and file type
            if 'Engineering_Team' in parts:
                team = 'Engineering'
                agent_name = parts[parts.index('Engineering_Team') + 1] if len(parts) > parts.index('Engineering_Team') + 1 else 'Unknown'
            elif 'Managers' in parts:
                team = 'Management'
                agent_name = parts[parts.index('Managers') + 1] if len(parts) > parts.index('Managers') + 1 else 'Unknown'
            elif 'Research_Team' in parts:
                team = 'Research'
                agent_name = parts[parts.index('Research_Team') + 1] if len(parts) > parts.index('Research_Team') + 1 else 'Unknown'
            else:
                team = 'General'
                agent_name = 'System'
            
            filename = os.path.basename(file_path)
            
            # Create document
            doc = {
                'id': f'AGENT_FILE_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{migrated:04d}',
                'type': 'AGENT_FILE',
                'source_path': file_path,
                'relative_path': rel_path,
                'agent': agent_name,
                'team': team,
                'filename': filename,
                'content': content,
                'size_bytes': len(content),
                'migration_timestamp': datetime.now().isoformat() + 'Z',
                'migration_type': 'EMERGENCY_BULK',
                'searchable': True
            }
            
            # Upload to Cosmos DB
            db.container.create_item(doc)
            migrated += 1
            
            if migrated % 10 == 0:
                print(f'Progress: {migrated}/{len(files)} files migrated...')
                
        except Exception as e:
            failed += 1
            print(f'FAILED: {file_path} - {str(e)[:50]}')
    
    print(f'\n=== MIGRATION COMPLETE ===')
    print(f'✅ Migrated: {migrated} files')
    print(f'❌ Failed: {failed} files')
    print(f'Success rate: {(migrated/len(files)*100):.1f}%')
    
    return migrated, failed

if __name__ == '__main__':
    start_time = datetime.now()
    migrated, failed = migrate_agent_files()
    duration = (datetime.now() - start_time).total_seconds()
    print(f'\nCompleted in {duration:.1f} seconds')
    print(f'Files per second: {migrated/duration:.1f}')