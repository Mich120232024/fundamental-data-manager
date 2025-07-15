#!/usr/bin/env python3
"""
Claude Session Log Processor
Processes terminal logs and stores them in Cosmos DB
Engineering-focused, minimalistic approach
"""

import os
import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from cosmos_db_manager import get_db_manager

class ClaudeSessionProcessor:
    def __init__(self):
        self.db = get_db_manager()
        self.logs_container = self.db.database.get_container_client('logs')
        
    def process_log_file(self, log_file_path):
        """Process a Claude session log file"""
        if not os.path.exists(log_file_path):
            return None
            
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()
        
        # Clean terminal control characters
        clean_content = self._clean_terminal_output(raw_content)
        
        # Extract session data
        session_data = self._extract_session_data(clean_content, log_file_path)
        
        # Store in Cosmos DB
        return self._store_session(session_data)
    
    def _clean_terminal_output(self, content):
        """Remove terminal control sequences"""
        # Remove ANSI escape codes
        content = re.sub(r'\x1b\[[0-9;]*[mGKF]', '', content)
        # Remove backspaces
        content = re.sub(r'\x08+', '', content)
        # Clean other control chars
        content = re.sub(r'[\x00-\x1f]+', '\n', content)
        return content.strip()
    
    def _extract_session_data(self, content, file_path):
        """Extract structured data from session"""
        lines = content.split('\n')
        
        # Extract interactions
        interactions = []
        current_block = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_block:
                    interactions.append({
                        'content': '\n'.join(current_block),
                        'timestamp': datetime.now().isoformat()
                    })
                    current_block = []
            else:
                current_block.append(line)
        
        # Create session document
        session_id = Path(file_path).stem
        return {
            'id': session_id,
            'type': 'TERMINAL_SESSION',
            'logType': 'CLAUDE_SESSION',
            'timestamp': datetime.now().isoformat() + 'Z',
            'session_metadata': {
                'session_id': session_id,
                'file_path': str(file_path),
                'file_size': os.path.getsize(file_path),
                'interaction_count': len(interactions)
            },
            'conversation_flow': interactions[:100],  # Limit for size
            'content_hash': hashlib.md5(content.encode()).hexdigest(),
            'partitionKey': 'terminal_conversations'
        }
    
    def _store_session(self, session_data):
        """Store session in Cosmos DB"""
        try:
            self.logs_container.create_item(body=session_data)
            return session_data['id']
        except Exception as e:
            print(f"Error storing session: {e}")
            return None

def watch_and_process():
    """Watch for new Claude session logs"""
    log_dir = Path.home() / "Research & Analytics Services" / "Digital Labor Workspace" / "Agent Logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    processor = ClaudeSessionProcessor()
    
    # Process any existing unprocessed logs
    for log_file in log_dir.glob("claude_session_*.log"):
        json_file = log_file.with_suffix('.json')
        if not json_file.exists():  # Not processed yet
            print(f"Processing: {log_file}")
            session_id = processor.process_log_file(log_file)
            if session_id:
                # Mark as processed
                with open(json_file, 'w') as f:
                    json.dump({'processed': True, 'session_id': session_id}, f)
                print(f"✅ Stored session: {session_id}")

if __name__ == "__main__":
    watch_and_process()