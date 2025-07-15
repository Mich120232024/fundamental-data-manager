#!/usr/bin/env python3
"""
Claude Code Conversation Extractor - Load existing Claude conversations to Cosmos DB
"""

import json
import os
import glob
from datetime import datetime
from cosmos_db_manager import CosmosDBManager

def extract_claude_conversations():
    """Extract all Claude Code conversations and load to Cosmos DB"""
    
    db = CosmosDBManager()
    db.container = db.database.get_container_client('logs')
    
    # Find Claude project directory
    claude_dir = os.path.expanduser('~/.claude/projects')
    project_pattern = os.path.join(claude_dir, '*')
    
    total_conversations = 0
    total_entries = 0
    
    print(f'=== EXTRACTING CLAUDE CODE CONVERSATIONS ===')
    print(f'Source: {claude_dir}')
    
    # Process each project directory
    for project_dir in glob.glob(project_pattern):
        if not os.path.isdir(project_dir):
            continue
            
        project_name = os.path.basename(project_dir)
        print(f'\nProcessing project: {project_name}')
        
        # Find all JSONL conversation files
        jsonl_pattern = os.path.join(project_dir, '*.jsonl')
        conversation_files = glob.glob(jsonl_pattern)
        
        print(f'  Found {len(conversation_files)} conversation files')
        
        for conv_file in conversation_files:
            session_id = os.path.basename(conv_file).replace('.jsonl', '')
            
            try:
                # Read conversation entries
                entries = []
                with open(conv_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line.strip())
                            entries.append(entry)
                
                if not entries:
                    continue
                
                # Create Cosmos DB document
                conversation_doc = {
                    'id': f'claude_code_session_{session_id}',
                    'type': 'CLAUDE_CODE_CONVERSATION',
                    'session_id': session_id,
                    'project': project_name,
                    'extracted_at': datetime.now().isoformat() + 'Z',
                    'total_entries': len(entries),
                    'conversation_entries': entries,
                    'metadata': {
                        'source_file': conv_file,
                        'file_size_bytes': os.path.getsize(conv_file),
                        'first_timestamp': entries[0].get('timestamp') if entries else None,
                        'last_timestamp': entries[-1].get('timestamp') if entries else None,
                        'message_types': list(set(e.get('type', 'unknown') for e in entries)),
                        'user_messages': len([e for e in entries if e.get('type') == 'user']),
                        'assistant_messages': len([e for e in entries if e.get('type') == 'assistant']),
                        'summary_entries': len([e for e in entries if e.get('type') == 'summary'])
                    }
                }
                
                # Upload to Cosmos DB
                try:
                    db.container.create_item(conversation_doc)
                    print(f'    ✅ {session_id}: {len(entries)} entries uploaded')
                    total_conversations += 1
                    total_entries += len(entries)
                except Exception as cosmos_error:
                    print(f'    ❌ {session_id}: Cosmos upload failed - {str(cosmos_error)[:50]}')
                    
            except Exception as e:
                print(f'    ❌ {session_id}: Parse failed - {str(e)[:50]}')
    
    print(f'\n=== EXTRACTION COMPLETE ===')
    print(f'Total conversations: {total_conversations}')
    print(f'Total entries: {total_entries}')
    print(f'Average entries per conversation: {total_entries/total_conversations if total_conversations > 0 else 0:.1f}')
    
    return total_conversations, total_entries

if __name__ == '__main__':
    extract_claude_conversations()