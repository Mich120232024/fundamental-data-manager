#!/usr/bin/env python3
"""
Resource Discovery for Agents
Help agents find what they need quickly
"""

import os
import json
from pathlib import Path

class ResourceDiscovery:
    """Simple resource discovery for agents"""
    
    @staticmethod
    def get_workspace_map():
        """Return workspace structure for agents"""
        base = Path.home() / "Research & Analytics Services"
        
        return {
            "workspaces": {
                "engineering": str(base / "Engineering Workspace"),
                "research": str(base / "Research Workspace"),
                "system_enforcement": str(base / "System Enforcement Workspace")
            },
            "scripts": {
                "cosmos_tools": str(base / "Engineering Workspace/scripts/cosmos_tools.py"),
                "container_manager": str(base / "Engineering Workspace/scripts/container_manager.py"),
                "inbox_manager": str(base / "Engineering Workspace/scripts/inbox_manager.py"),
                "log_processor": str(base / "Engineering Workspace/scripts/claude_session_processor.py")
            },
            "system_operations": {
                "log_capture": str(base / "Engineering Workspace/system_operations/log_capture.sh"),
                "dashboard": str(base / "user-management-dashboard/backend/app.py")
            },
            "data_locations": {
                "agent_logs": str(base / "Digital Labor Workspace/Agent Logs"),
                "agent_memory": str(base / "Digital Labor Workspace/Agent Roster")
            }
        }
    
    @staticmethod
    def get_cosmos_containers():
        """Return Cosmos DB container reference"""
        return {
            "messages": "System messaging between agents",
            "logs": "Terminal sessions and system logs",
            "audit": "Audit trail for all operations",
            "documents": "Document storage",
            "metadata": "System metadata and configuration",
            "agent_context_memory": "Agent memory storage",
            "processes": "Process tracking",
            "enforcement": "System enforcement records",
            "institutional-data-center": "Research data storage"
        }
    
    @staticmethod
    def get_quick_commands():
        """Return quick command reference"""
        return {
            "send_message": "python3 cosmos_tools.py send <to> <subject> <content>",
            "check_inbox": "python3 inbox_manager.py check <recipient>",
            "list_containers": "python3 container_manager.py list",
            "capture_session": "./log_capture.sh claude",
            "process_logs": "./log_capture.sh process",
            "view_dashboard": "http://localhost:5001"
        }
    
    @staticmethod
    def save_reference():
        """Save reference file for agents"""
        reference = {
            "workspace_map": ResourceDiscovery.get_workspace_map(),
            "cosmos_containers": ResourceDiscovery.get_cosmos_containers(),
            "quick_commands": ResourceDiscovery.get_quick_commands(),
            "updated": datetime.now().isoformat()
        }
        
        ref_file = Path.home() / "Research & Analytics Services/RESOURCE_REFERENCE.json"
        with open(ref_file, 'w') as f:
            json.dump(reference, f, indent=2)
        
        return str(ref_file)

# CLI usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Resource Discovery")
        print("Usage:")
        print("  resource_discovery.py map      # Show workspace map")
        print("  resource_discovery.py cosmos   # Show Cosmos containers")
        print("  resource_discovery.py commands # Show quick commands")
        print("  resource_discovery.py save     # Save reference file")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "map":
        print("📁 WORKSPACE MAP:")
        for category, paths in ResourceDiscovery.get_workspace_map().items():
            print(f"\n{category.upper()}:")
            if isinstance(paths, dict):
                for name, path in paths.items():
                    print(f"  {name}: {path}")
            else:
                print(f"  {paths}")
    
    elif cmd == "cosmos":
        print("🗄️  COSMOS DB CONTAINERS:")
        for container, purpose in ResourceDiscovery.get_cosmos_containers().items():
            print(f"  {container:<25} - {purpose}")
    
    elif cmd == "commands":
        print("⚡ QUICK COMMANDS:")
        for action, command in ResourceDiscovery.get_quick_commands().items():
            print(f"  {action:<20} → {command}")
    
    elif cmd == "save":
        from datetime import datetime
        ref_file = ResourceDiscovery.save_reference()
        print(f"✅ Reference saved to: {ref_file}")