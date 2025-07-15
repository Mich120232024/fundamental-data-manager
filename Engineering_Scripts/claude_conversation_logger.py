#!/usr/bin/env python3
"""
Claude Code Conversation Logger - Captures entire terminal conversation to Cosmos DB
"""

import json
import sys
import os
from datetime import datetime
import time
import threading
import queue
from cosmos_db_manager import CosmosDBManager

class ClaudeConversationLogger:
    def __init__(self):
        self.db = CosmosDBManager()
        self.db.container = self.db.database.get_container_client('logs')
        self.session_id = f"claude_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
        self.conversation_history = []
        self.start_time = datetime.now()
        self.message_queue = queue.Queue()
        self.is_running = True
        
        # Start background thread for periodic saves
        self.save_thread = threading.Thread(target=self._periodic_save)
        self.save_thread.daemon = True
        self.save_thread.start()
        
        print(f"[LOGGER] Started session: {self.session_id}")
        
    def log_user_input(self, content):
        """Log user input to conversation"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'user_input',
            'content': content,
            'length': len(content),
            'interaction_id': len(self.conversation_history) + 1
        }
        self.conversation_history.append(entry)
        self.message_queue.put(('save', None))
        
    def log_claude_response(self, content, tool_calls=None):
        """Log Claude's response"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'claude_response',
            'content': content,
            'length': len(content),
            'tool_calls': tool_calls or [],
            'interaction_id': len(self.conversation_history) + 1
        }
        self.conversation_history.append(entry)
        self.message_queue.put(('save', None))
        
    def log_tool_execution(self, tool_name, tool_input, tool_output, success=True):
        """Log tool execution details"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'tool_execution',
            'tool_name': tool_name,
            'tool_input': str(tool_input)[:500],  # Truncate large inputs
            'tool_output': str(tool_output)[:1000],  # Truncate large outputs
            'execution_success': success,
            'interaction_id': len(self.conversation_history) + 1
        }
        self.conversation_history.append(entry)
        self.message_queue.put(('save', None))
        
    def log_error(self, error_type, error_message, context=None):
        """Log errors that occur"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'error',
            'error_type': error_type,
            'error_message': str(error_message),
            'context': context,
            'interaction_id': len(self.conversation_history) + 1
        }
        self.conversation_history.append(entry)
        self.message_queue.put(('save', None))
        
    def _periodic_save(self):
        """Background thread to save conversation periodically"""
        while self.is_running:
            try:
                # Wait for save signal or timeout
                action, _ = self.message_queue.get(timeout=30)
                if action == 'save':
                    self._save_to_cosmos()
            except queue.Empty:
                # Save every 30 seconds even if no new messages
                self._save_to_cosmos()
            except Exception as e:
                print(f"[LOGGER ERROR] Failed to save: {e}")
                
    def _save_to_cosmos(self):
        """Save conversation to Cosmos DB"""
        try:
            document = {
                'id': self.session_id,
                'type': 'CLAUDE_CONVERSATION_LOG',
                'session_start': self.start_time.isoformat(),
                'last_updated': datetime.now().isoformat(),
                'agent': 'SAM',
                'workspace': os.getcwd(),
                'conversation_history': self.conversation_history,
                'total_interactions': len(self.conversation_history),
                'session_duration_seconds': (datetime.now() - self.start_time).total_seconds(),
                'metadata': {
                    'user_inputs': len([e for e in self.conversation_history if e['type'] == 'user_input']),
                    'claude_responses': len([e for e in self.conversation_history if e['type'] == 'claude_response']),
                    'tool_executions': len([e for e in self.conversation_history if e['type'] == 'tool_execution']),
                    'errors': len([e for e in self.conversation_history if e['type'] == 'error'])
                }
            }
            
            # Upsert to Cosmos DB
            self.db.container.upsert_item(document)
            print(f"[LOGGER] Saved {len(self.conversation_history)} entries to Cosmos DB")
            
        except Exception as e:
            print(f"[LOGGER ERROR] Failed to save to Cosmos: {e}")
            
    def finalize(self):
        """Final save and cleanup"""
        self.is_running = False
        self._save_to_cosmos()
        
        # Create final summary
        summary = {
            'id': f"{self.session_id}_summary",
            'type': 'CONVERSATION_SUMMARY',
            'session_id': self.session_id,
            'session_date': self.start_time.strftime('%Y-%m-%d'),
            'duration': str(datetime.now() - self.start_time),
            'total_interactions': len(self.conversation_history),
            'key_topics': self._extract_topics(),
            'tools_used': self._get_tools_used(),
            'completion_time': datetime.now().isoformat()
        }
        
        try:
            self.db.container.create_item(summary)
            print(f"[LOGGER] Session finalized: {self.session_id}")
        except:
            pass
            
    def _extract_topics(self):
        """Extract key topics from conversation"""
        # Simple keyword extraction
        topics = set()
        for entry in self.conversation_history:
            if entry['type'] in ['user_input', 'claude_response']:
                content = entry.get('content', '').lower()
                if 'migration' in content:
                    topics.add('migration')
                if 'log' in content:
                    topics.add('logging')
                if 'enforcement' in content:
                    topics.add('enforcement')
                if 'cosmos' in content:
                    topics.add('cosmos_db')
        return list(topics)
        
    def _get_tools_used(self):
        """Get list of tools used in session"""
        tools = set()
        for entry in self.conversation_history:
            if entry['type'] == 'tool_execution':
                tools.add(entry.get('tool_name', 'unknown'))
        return list(tools)

# Global logger instance
_logger = None

def get_logger():
    """Get or create logger instance"""
    global _logger
    if _logger is None:
        _logger = ClaudeConversationLogger()
    return _logger

def log_conversation(message_type, **kwargs):
    """Main API for logging conversation events"""
    logger = get_logger()
    
    if message_type == 'user':
        logger.log_user_input(kwargs.get('content', ''))
    elif message_type == 'claude':
        logger.log_claude_response(
            kwargs.get('content', ''),
            kwargs.get('tool_calls', [])
        )
    elif message_type == 'tool':
        logger.log_tool_execution(
            kwargs.get('tool_name', 'unknown'),
            kwargs.get('tool_input', ''),
            kwargs.get('tool_output', ''),
            kwargs.get('success', True)
        )
    elif message_type == 'error':
        logger.log_error(
            kwargs.get('error_type', 'unknown'),
            kwargs.get('error_message', ''),
            kwargs.get('context', None)
        )
    elif message_type == 'finalize':
        logger.finalize()

if __name__ == '__main__':
    # Test the logger
    print("Testing Claude Conversation Logger...")
    
    # Log test conversation
    log_conversation('user', content='Please help me understand the logging system')
    time.sleep(0.5)
    
    log_conversation('claude', content='I\'ll help you understand the logging system.', 
                    tool_calls=['Read', 'Bash'])
    time.sleep(0.5)
    
    log_conversation('tool', tool_name='Read', 
                    tool_input='logs/session_2025-06-18.md',
                    tool_output='File contents here...',
                    success=True)
    time.sleep(0.5)
    
    log_conversation('finalize')
    
    print("\nLogger test complete. Check Cosmos DB logs container.")
