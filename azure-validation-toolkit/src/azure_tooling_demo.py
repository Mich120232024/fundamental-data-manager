#!/usr/bin/env python3
"""
Azure Tooling Demo - Job-Based Toolboxes
HEAD_OF_ENGINEERING - June 14, 2025

Demo of what we have and your concept of job-based tooling
"""

import json
from typing import List, Dict, Set

class JobBasedToolbox:
    """
    Your concept: Bundle tools by job/task and return complete toolbox per query
    """
    
    def __init__(self, tools_json_path: str):
        with open(tools_json_path, 'r') as f:
            self.data = json.load(f)
        self.tools = self.data['tools']
        
        # Define job-based toolboxes
        self.job_toolboxes = {
            "vm_deployment": {
                "description": "Complete VM deployment workflow",
                "tools": ["azure-mgmt-compute", "azure-mgmt-network", "azure-mgmt-resource", "azure-identity"],
                "workflow": ["Create resource group", "Setup networking", "Deploy VM", "Configure monitoring"]
            },
            
            "data_pipeline": {
                "description": "FRED data collection and processing",
                "tools": ["azure-cosmos", "azure-eventhub", "azure-mgmt-synapse", "azure-monitor-query"],
                "workflow": ["Event ingestion", "Stream processing", "Data storage", "Monitoring"]
            },
            
            "web_application": {
                "description": "React + FastAPI web application deployment",
                "tools": ["azure-mgmt-containerservice", "azure-mgmt-appservice", "azure-mgmt-keyvault", "azure-mgmt-monitor"],
                "workflow": ["Container setup", "App deployment", "Secret management", "Monitoring setup"]
            },
            
            "database_management": {
                "description": "Database setup and maintenance",
                "tools": ["azure-mgmt-cosmosdb", "azure-cosmos", "azure-mgmt-sql", "azure-mgmt-postgresql"],
                "workflow": ["Database creation", "Schema setup", "Data operations", "Backup configuration"]
            },
            
            "security_compliance": {
                "description": "Security and compliance operations",
                "tools": ["azure-mgmt-keyvault", "azure-keyvault-secrets", "azure-mgmt-security", "azure-mgmt-authorization"],
                "workflow": ["Key management", "Access control", "Security monitoring", "Compliance reporting"]
            }
        }
    
    def get_toolbox_for_job(self, job: str) -> Dict:
        """Get complete toolbox for a specific job"""
        if job not in self.job_toolboxes:
            return {"error": f"Job '{job}' not found. Available: {list(self.job_toolboxes.keys())}"}
        
        toolbox = self.job_toolboxes[job]
        detailed_tools = []
        
        # Find detailed info for each tool in the job
        for tool_name in toolbox["tools"]:
            for tool in self.tools:
                if tool_name in tool["command"] or tool_name in tool["id"]:
                    detailed_tools.append({
                        "name": tool["command"],
                        "description": tool["description"],
                        "language": tool.get("language", "N/A"),
                        "authentication": tool.get("authentication", "N/A"),
                        "category": tool["category"]
                    })
                    break
        
        return {
            "job": job,
            "description": toolbox["description"],
            "workflow_steps": toolbox["workflow"],
            "tools": detailed_tools,
            "total_tools": len(detailed_tools)
        }
    
    def suggest_job_from_query(self, query: str) -> List[str]:
        """Suggest jobs based on query keywords"""
        query_lower = query.lower()
        suggestions = []
        
        keywords = {
            "vm_deployment": ["vm", "virtual machine", "compute", "deploy", "server"],
            "data_pipeline": ["data", "pipeline", "synapse", "eventhub", "cosmos", "fred"],
            "web_application": ["web", "app", "react", "fastapi", "container", "kubernetes"],
            "database_management": ["database", "sql", "cosmos", "postgresql", "data"],
            "security_compliance": ["security", "keyvault", "rbac", "auth", "compliance"]
        }
        
        for job, job_keywords in keywords.items():
            if any(keyword in query_lower for keyword in job_keywords):
                suggestions.append(job)
        
        return suggestions
    
    def get_current_scope(self) -> Dict:
        """Show what tools we actually have"""
        categories = {}
        languages = {}
        
        for tool in self.tools:
            # Count by category
            cat = tool["category"]
            categories[cat] = categories.get(cat, 0) + 1
            
            # Count by language
            lang = tool.get("language", "unknown")
            languages[lang] = languages.get(lang, 0) + 1
        
        return {
            "total_tools": len(self.tools),
            "categories": dict(sorted(categories.items())),
            "languages": dict(sorted(languages.items())),
            "sample_tools": [
                {
                    "name": tool["command"],
                    "desc": tool["description"][:60] + "..." if len(tool["description"]) > 60 else tool["description"],
                    "type": tool["category"]
                }
                for tool in self.tools[:10]
            ]
        }

def demo_job_based_tooling():
    """Demonstrate the job-based tooling concept"""
    
    print("=== AZURE TOOLING SYSTEM DEMO ===")
    print("Your concept: Job-based toolboxes\n")
    
    # Initialize with our current data
    toolbox = JobBasedToolbox("/Users/mikaeleage/Research & Analytics Services/azure_tools.json")
    
    # Show current scope
    print("1. CURRENT TOOLING SCOPE")
    print("-" * 40)
    scope = toolbox.get_current_scope()
    print(f"Total tools: {scope['total_tools']}")
    print(f"Categories: {list(scope['categories'].keys())}")
    print(f"Languages: {list(scope['languages'].keys())}")
    print()
    
    # Show available jobs
    print("2. AVAILABLE JOB TOOLBOXES")
    print("-" * 40)
    for job in toolbox.job_toolboxes:
        desc = toolbox.job_toolboxes[job]["description"]
        print(f"  {job}: {desc}")
    print()
    
    # Demo job-based queries
    test_queries = [
        "I need to deploy a VM",
        "Setting up FRED data pipeline", 
        "React application deployment",
        "Database management tasks"
    ]
    
    print("3. JOB-BASED QUERY EXAMPLES")
    print("-" * 40)
    
    for query in test_queries:
        print(f"Query: '{query}'")
        suggestions = toolbox.suggest_job_from_query(query)
        
        if suggestions:
            # Get first suggestion toolbox
            job_tools = toolbox.get_toolbox_for_job(suggestions[0])
            print(f"  → Suggested job: {suggestions[0]}")
            print(f"  → Tools needed: {job_tools['total_tools']}")
            print(f"  → Workflow: {' → '.join(job_tools['workflow_steps'])}")
            
            # Show first few tools
            for i, tool in enumerate(job_tools['tools'][:3]):
                print(f"    {i+1}. {tool['name']} ({tool['language']})")
        else:
            print("  → No specific job match found")
        print()
    
    # Show complete toolbox for one job
    print("4. COMPLETE TOOLBOX EXAMPLE")
    print("-" * 40)
    complete_toolbox = toolbox.get_toolbox_for_job("data_pipeline")
    print(f"Job: {complete_toolbox['job']}")
    print(f"Description: {complete_toolbox['description']}")
    print("Workflow:")
    for i, step in enumerate(complete_toolbox['workflow_steps'], 1):
        print(f"  {i}. {step}")
    print(f"\nTools ({complete_toolbox['total_tools']} total):")
    for tool in complete_toolbox['tools']:
        print(f"  • {tool['name']} - {tool['description'][:50]}...")

if __name__ == "__main__":
    demo_job_based_tooling()