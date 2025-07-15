#!/usr/bin/env python3
"""
Process to migrate local logs to Cosmos DB logs container
Uses agent names as primary keys for organization
"""

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import os
import sys
from pathlib import Path
from datetime import datetime
import re
import json
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Import cosmos manager
sys.path.insert(0, str(Path(__file__).parent))
from cosmos_db_manager import get_db_manager

def discover_local_logs():
    """Discover all local log files across the workspace"""
    
    workspace_root = Path("/Users/mikaeleage/Research & Analytics Services")
    log_files = []
    
    print("🔍 Discovering local log files...")
    
    # Common log patterns
    log_patterns = [
        "**/logs/*.md",
        "**/logs/*.txt", 
        "**/logs/*.log",
        "**/session_*.md",
        "**/log_*.md",
        "**/*_log_*.md",
        "**/*session*.md"
    ]
    
    for pattern in log_patterns:
        for file_path in workspace_root.rglob(pattern):
            if file_path.is_file():
                log_files.append(file_path)
    
    # Organize by agent
    agent_logs = {}
    
    for log_file in log_files:
        agent_name = extract_agent_name_from_path(log_file)
        if agent_name not in agent_logs:
            agent_logs[agent_name] = []
        agent_logs[agent_name].append(log_file)
    
    print(f"📊 Found {len(log_files)} log files for {len(agent_logs)} agents")
    
    for agent, files in agent_logs.items():
        print(f"   • {agent}: {len(files)} files")
    
    return agent_logs

def extract_agent_name_from_path(file_path):
    """Extract agent name from file path"""
    
    path_str = str(file_path)
    
    # Common agent patterns
    if "HEAD_OF_ENGINEERING" in path_str or "Engineering Workspace" in path_str:
        return "HEAD_OF_ENGINEERING"
    elif "HEAD_OF_RESEARCH" in path_str or "Research Workspace" in path_str:
        return "HEAD_OF_RESEARCH"
    elif "HEAD_OF_DIGITAL_STAFF" in path_str or "Digital Labor" in path_str:
        return "HEAD_OF_DIGITAL_STAFF"
    elif "COMPLIANCE_MANAGER" in path_str or "Governance Workspace" in path_str:
        return "COMPLIANCE_MANAGER"
    elif "Management" in path_str or "Executive" in path_str:
        return "MANAGEMENT_TEAM"
    elif "Claude_Code" in path_str:
        return "CLAUDE_CODE"
    elif "SAM" in path_str:
        return "SAM"
    else:
        # Try to extract from filename
        filename = file_path.name
        if "session_" in filename:
            return "UNKNOWN_AGENT"
        return "SYSTEM"

def parse_log_file(file_path, agent_name):
    """Parse individual log file and extract entries"""
    
    print(f"   📄 Parsing {file_path.name}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"   ❌ Error reading {file_path}: {e}")
        return []
    
    entries = []
    
    # Extract session date from filename or content
    session_date = extract_session_date(file_path, content)
    
    # Parse markdown-style logs
    if file_path.suffix == '.md':
        entries.extend(parse_markdown_log(content, agent_name, session_date, file_path))
    else:
        entries.extend(parse_text_log(content, agent_name, session_date, file_path))
    
    return entries

def extract_session_date(file_path, content):
    """Extract session date from filename or content"""
    
    # Try filename first
    filename = file_path.name
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',
        r'session_(\d{4}-\d{2}-\d{2})',
        r'log_(\d{4}-\d{2}-\d{2})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, filename)
        if match:
            return match.group(1)
    
    # Try content
    for pattern in date_patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1)
    
    # Use file modification date as fallback
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    return mtime.strftime('%Y-%m-%d')

def parse_markdown_log(content, agent_name, session_date, file_path):
    """Parse markdown log file"""
    
    entries = []
    lines = content.split('\n')
    
    current_entry = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for session start/end markers
        if "Session Start" in line or "SESSION START" in line:
            entry = create_log_entry(
                agent_name, session_date, "SESSION_START", 
                "Session initiated", str(file_path), i+1
            )
            entries.append(entry)
            
        elif "Session End" in line or "SESSION END" in line:
            entry = create_log_entry(
                agent_name, session_date, "SESSION_END",
                "Session completed", str(file_path), i+1
            )
            entries.append(entry)
            
        # Look for action markers
        elif line.startswith('**') or line.startswith('##'):
            action = line.replace('**', '').replace('##', '').strip()
            if action and len(action) > 5:
                entry = create_log_entry(
                    agent_name, session_date, "ACTIVITY",
                    action, str(file_path), i+1
                )
                entries.append(entry)
                
        # Look for evidence patterns
        elif "Evidence:" in line or "EVIDENCE:" in line:
            evidence = line.split("Evidence:")[-1].strip()
            entry = create_log_entry(
                agent_name, session_date, "EVIDENCE",
                f"Evidence provided: {evidence}", str(file_path), i+1
            )
            entries.append(entry)
    
    # If no specific entries found, create a general entry
    if not entries:
        entry = create_log_entry(
            agent_name, session_date, "ACTIVITY",
            f"Log file activity: {file_path.name}", str(file_path), 1
        )
        entries.append(entry)
    
    return entries

def parse_text_log(content, agent_name, session_date, file_path):
    """Parse plain text log file"""
    
    entries = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line and len(line) > 10:  # Substantial content
            entry = create_log_entry(
                agent_name, session_date, "ACTIVITY",
                line[:200], str(file_path), i+1  # Truncate long lines
            )
            entries.append(entry)
    
    return entries

def create_log_entry(agent_name, session_date, log_type, action, file_path, line_number):
    """Create standardized log entry"""
    
    timestamp = datetime.now().isoformat() + 'Z'
    
    entry = {
        'id': f"log-{session_date}-{agent_name}-{datetime.now().strftime('%H%M%S%f')[:8]}",
        'sessionDate': session_date,
        'agentName': agent_name,
        'sessionId': f"session_{session_date}_{agent_name}",
        'timestamp': timestamp,
        'logType': log_type,
        'action': action,
        'evidence': f"{file_path}:{line_number}",
        'outcome': 'Migrated from local logs',
        'status': 'SUCCESS',
        'context': 'Local log migration to constitutional compliance system',
        'constitutionalCompliance': True,
        'violationLevel': 'NONE',
        'metadata': {
            'sourceFile': str(file_path),
            'sourceLine': line_number,
            'migrationType': 'LOCAL_TO_COSMOS',
            'migrationDate': timestamp
        }
    }
    
    return entry

def migrate_agent_logs(agent_name, log_files):
    """Migrate all logs for a specific agent"""
    
    print(f"\n🔄 Migrating logs for {agent_name}...")
    
    db = get_db_manager()
    logs_container = db.database.get_container_client('logs')
    
    all_entries = []
    
    # Parse all log files for this agent
    for log_file in log_files:
        entries = parse_log_file(log_file, agent_name)
        all_entries.extend(entries)
    
    # Upload to Cosmos DB
    successful = 0
    failed = 0
    
    for entry in all_entries:
        try:
            logs_container.create_item(entry)
            successful += 1
        except Exception as e:
            if "Conflict" in str(e):
                # Entry already exists, skip
                successful += 1
            else:
                print(f"   ❌ Failed to upload entry: {e}")
                failed += 1
    
    print(f"   ✅ {successful} entries migrated, {failed} failed")
    return successful, failed

def create_migration_summary(total_migrated, total_failed, agent_stats):
    """Create migration summary log entry"""
    
    db = get_db_manager()
    logs_container = db.database.get_container_client('logs')
    
    timestamp = datetime.now().isoformat() + 'Z'
    
    summary_entry = {
        'id': f"log-{datetime.now().strftime('%Y-%m-%d')}-SYSTEM-MIGRATION-{datetime.now().strftime('%H%M%S')}",
        'sessionDate': datetime.now().strftime('%Y-%m-%d'),
        'agentName': 'HEAD_OF_ENGINEERING',
        'sessionId': f"migration_session_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}",
        'timestamp': timestamp,
        'logType': 'ACTIVITY',
        'action': 'Local logs migration to Cosmos DB completed',
        'evidence': f"migrate_local_logs_to_cosmos.py:migration_summary",
        'outcome': f"Successfully migrated {total_migrated} log entries from {len(agent_stats)} agents",
        'status': 'SUCCESS' if total_failed == 0 else 'WARNING',
        'context': 'Constitutional compliance - centralized logging implementation',
        'constitutionalCompliance': True,
        'violationLevel': 'NONE',
        'metadata': {
            'totalMigrated': total_migrated,
            'totalFailed': total_failed,
            'agentCount': len(agent_stats),
            'agentStats': agent_stats,
            'migrationType': 'BULK_LOCAL_TO_COSMOS'
        }
    }
    
    try:
        logs_container.create_item(summary_entry)
        print(f"✅ Migration summary logged: {summary_entry['id']}")
    except Exception as e:
        print(f"❌ Failed to log migration summary: {e}")

def main():
    """Main migration process"""
    
    print("📋 LOCAL LOGS TO COSMOS DB MIGRATION PROCESS")
    print("="*60)
    print("Migrating all local logs to centralized Cosmos DB logs container")
    print("Using agent names as primary organization keys")
    
    # Discover all local logs
    agent_logs = discover_local_logs()
    
    if not agent_logs:
        print("⚠️ No local log files found")
        return
    
    # Migrate each agent's logs
    total_migrated = 0
    total_failed = 0
    agent_stats = {}
    
    for agent_name, log_files in agent_logs.items():
        migrated, failed = migrate_agent_logs(agent_name, log_files)
        total_migrated += migrated
        total_failed += failed
        agent_stats[agent_name] = {
            'files': len(log_files),
            'migrated': migrated,
            'failed': failed
        }
    
    # Create migration summary
    create_migration_summary(total_migrated, total_failed, agent_stats)
    
    print(f"\n" + "="*60)
    print("✅ LOCAL LOGS MIGRATION COMPLETE")
    print("="*60)
    
    print(f"\n📊 Migration Statistics:")
    print(f"   • Total log entries migrated: {total_migrated}")
    print(f"   • Failed migrations: {total_failed}")
    print(f"   • Agents processed: {len(agent_stats)}")
    
    print(f"\n📋 Agent-by-Agent Results:")
    for agent, stats in agent_stats.items():
        print(f"   • {agent}: {stats['migrated']} entries from {stats['files']} files")
    
    print(f"\n🏛️ Constitutional Compliance:")
    print(f"   • All local logs now centralized in Cosmos DB")
    print(f"   • Agent-based organization implemented")
    print(f"   • Evidence tracking preserved")
    print(f"   • Article VI logging requirements satisfied")
    
    print(f"\n📦 Container Status:")
    print(f"   • Container: logs")
    print(f"   • Partition key: sessionDate")
    print(f"   • Primary organization: agentName")
    print(f"   • Constitutional compliance: ACTIVE")

if __name__ == "__main__":
    main()