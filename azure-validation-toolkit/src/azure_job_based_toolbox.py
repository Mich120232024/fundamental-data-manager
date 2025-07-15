#!/usr/bin/env python3
"""
Azure Job-Based Toolbox System
HEAD_OF_ENGINEERING - June 14, 2025

Exploitable toolbox system using comprehensive Azure tools JSON
Returns complete toolkits for specific engineering jobs
"""

import json
import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

@dataclass
class JobToolbox:
    """Complete toolkit for a specific engineering job"""
    job_name: str
    description: str
    workflow_steps: List[str]
    cli_tools: List[Dict[str, Any]]
    mcp_tools: List[Dict[str, Any]]
    sdk_tools: List[Dict[str, Any]]
    total_tools: int
    estimated_time: str
    complexity: str
    prerequisites: List[str]
    common_patterns: List[str]

class AzureJobBasedToolbox:
    """Production-ready job-based toolbox system"""
    
    def __init__(self, comprehensive_json_path: str):
        with open(comprehensive_json_path, 'r') as f:
            self.data = json.load(f)
        
        self.tools = {tool['id']: tool for tool in self.data['tools']}
        self.categories = self.data['indexes']['categories']
        self.languages = self.data['indexes']['languages']
        
        # Define comprehensive job templates
        self.job_definitions = {
            
            "vm_deployment_production": {
                "description": "Production VM deployment with monitoring and security",
                "workflow": [
                    "Create resource group with proper naming",
                    "Setup virtual network and subnets", 
                    "Configure NSG and security rules",
                    "Deploy VM with managed identity",
                    "Setup monitoring and alerting",
                    "Configure backup and disaster recovery"
                ],
                "categories": ["compute", "networking", "security", "monitoring"],
                "tools_needed": [
                    "resource group creation", "vm creation", "network setup", 
                    "monitoring", "security", "identity management"
                ],
                "complexity": "medium",
                "estimated_time": "2-3 hours",
                "prerequisites": ["Azure subscription", "RBAC permissions", "Network planning"]
            },
            
            "fred_data_pipeline": {
                "description": "Complete FRED data collection and processing pipeline",
                "workflow": [
                    "Setup Event Hub for data ingestion",
                    "Configure Cosmos DB for data storage",
                    "Deploy Synapse for data processing",
                    "Setup monitoring and alerting",
                    "Configure data validation and quality checks",
                    "Implement rate limiting and error handling"
                ],
                "categories": ["messaging", "database", "analytics", "monitoring"],
                "tools_needed": [
                    "event streaming", "data storage", "data processing",
                    "monitoring", "authentication"
                ],
                "complexity": "high",
                "estimated_time": "4-6 hours",
                "prerequisites": ["Data architecture design", "Rate limiting strategy", "Error handling plan"]
            },
            
            "react_fastapi_deployment": {
                "description": "Full-stack React + FastAPI application deployment",
                "workflow": [
                    "Setup container registry",
                    "Create AKS cluster",
                    "Configure ingress and load balancing",
                    "Deploy FastAPI backend services",
                    "Deploy React frontend",
                    "Setup CI/CD pipeline",
                    "Configure monitoring and logging"
                ],
                "categories": ["containers", "networking", "monitoring", "security"],
                "tools_needed": [
                    "container orchestration", "networking", "load balancing",
                    "monitoring", "cicd", "security"
                ],
                "complexity": "high",
                "estimated_time": "6-8 hours",
                "prerequisites": ["Kubernetes knowledge", "Container expertise", "Application architecture"]
            },
            
            "database_setup_production": {
                "description": "Production database setup with security and backups",
                "workflow": [
                    "Create database server with encryption",
                    "Configure networking and firewall",
                    "Setup authentication and authorization",
                    "Create databases and schemas",
                    "Configure automated backups",
                    "Setup monitoring and alerting",
                    "Implement security compliance"
                ],
                "categories": ["database", "security", "monitoring", "networking"],
                "tools_needed": [
                    "database management", "security", "backup",
                    "monitoring", "networking"
                ],
                "complexity": "medium",
                "estimated_time": "3-4 hours",
                "prerequisites": ["Database design", "Security requirements", "Backup strategy"]
            },
            
            "security_hardening": {
                "description": "Comprehensive security hardening and compliance setup",
                "workflow": [
                    "Setup Key Vault for secrets management",
                    "Configure managed identities",
                    "Implement RBAC and least privilege",
                    "Setup security monitoring",
                    "Configure compliance reporting",
                    "Implement audit logging",
                    "Setup threat detection"
                ],
                "categories": ["security", "monitoring", "management"],
                "tools_needed": [
                    "key management", "identity", "rbac",
                    "security monitoring", "compliance"
                ],
                "complexity": "high",
                "estimated_time": "4-5 hours",
                "prerequisites": ["Security architecture", "Compliance requirements", "Identity design"]
            },
            
            "monitoring_observability": {
                "description": "Complete monitoring and observability setup",
                "workflow": [
                    "Setup Application Insights",
                    "Configure Log Analytics workspace",
                    "Create custom dashboards",
                    "Setup alerting rules",
                    "Configure automated responses",
                    "Implement performance monitoring",
                    "Setup cost monitoring"
                ],
                "categories": ["monitoring", "analytics"],
                "tools_needed": [
                    "application monitoring", "log analytics", "alerting",
                    "dashboards", "performance monitoring"
                ],
                "complexity": "medium",
                "estimated_time": "3-4 hours",
                "prerequisites": ["Monitoring strategy", "Alert definitions", "Dashboard requirements"]
            },
            
            "disaster_recovery": {
                "description": "Disaster recovery and business continuity setup",
                "workflow": [
                    "Setup geo-redundant storage",
                    "Configure database replication",
                    "Implement automated backups",
                    "Setup recovery testing",
                    "Configure failover procedures",
                    "Document recovery processes",
                    "Test recovery scenarios"
                ],
                "categories": ["storage", "database", "management", "monitoring"],
                "tools_needed": [
                    "backup management", "replication", "storage",
                    "automation", "testing"
                ],
                "complexity": "high",
                "estimated_time": "5-7 hours",
                "prerequisites": ["RTO/RPO requirements", "Business continuity plan", "Testing schedule"]
            }
        }
    
    def get_toolbox_for_job(self, job_name: str) -> Optional[JobToolbox]:
        """Get complete toolbox for a specific job"""
        if job_name not in self.job_definitions:
            return None
        
        job_def = self.job_definitions[job_name]
        
        # Find relevant tools for this job
        cli_tools = []
        mcp_tools = []
        sdk_tools = []
        
        # Get tools by categories needed for this job
        for category in job_def["categories"]:
            if category in self.categories:
                for tool_id in self.categories[category]:
                    tool = self.tools[tool_id]
                    
                    if tool["tool_type"] == "cli":
                        cli_tools.append(tool)
                    elif tool["tool_type"] == "mcp":
                        mcp_tools.append(tool)
                    elif tool["tool_type"] == "sdk":
                        sdk_tools.append(tool)
        
        # Remove duplicates and sort by relevance
        cli_tools = self._sort_tools_by_relevance(cli_tools, job_def["tools_needed"])
        mcp_tools = self._sort_tools_by_relevance(mcp_tools, job_def["tools_needed"])
        sdk_tools = self._sort_tools_by_relevance(sdk_tools, job_def["tools_needed"])
        
        total_tools = len(cli_tools) + len(mcp_tools) + len(sdk_tools)
        
        return JobToolbox(
            job_name=job_name,
            description=job_def["description"],
            workflow_steps=job_def["workflow"],
            cli_tools=cli_tools,
            mcp_tools=mcp_tools,
            sdk_tools=sdk_tools,
            total_tools=total_tools,
            estimated_time=job_def["estimated_time"],
            complexity=job_def["complexity"],
            prerequisites=job_def["prerequisites"],
            common_patterns=self._get_common_patterns(job_name)
        )
    
    def _sort_tools_by_relevance(self, tools: List[Dict], needs: List[str]) -> List[Dict]:
        """Sort tools by relevance to job needs"""
        scored_tools = []
        
        for tool in tools:
            score = 0
            tool_text = f"{tool['name']} {tool['description']} {tool['category']}".lower()
            
            # Score based on keyword matches
            for need in needs:
                if need.lower() in tool_text:
                    score += 2
                # Partial matches
                for word in need.split():
                    if word.lower() in tool_text:
                        score += 1
            
            scored_tools.append((tool, score))
        
        # Sort by score, keep top tools
        scored_tools.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, score in scored_tools if score > 0][:15]  # Limit to top 15 per type
    
    def _get_common_patterns(self, job_name: str) -> List[str]:
        """Get common patterns and best practices for this job"""
        patterns = {
            "vm_deployment_production": [
                "Use managed identity for authentication",
                "Enable boot diagnostics for troubleshooting",
                "Configure automated patching",
                "Use Azure Backup for VM protection",
                "Implement NSG rules for least privilege"
            ],
            "fred_data_pipeline": [
                "Implement 800ms rate limiting for FRED API",
                "Use partition keys for optimal Cosmos DB performance",
                "Setup dead letter queues for failed messages",
                "Monitor throughput and scale accordingly",
                "Implement data validation at ingestion"
            ],
            "react_fastapi_deployment": [
                "Use multi-stage Docker builds",
                "Implement health checks for all services",
                "Configure horizontal pod autoscaling",
                "Use Azure Container Registry",
                "Setup ingress with SSL termination"
            ],
            "database_setup_production": [
                "Enable transparent data encryption",
                "Configure automated backups with retention",
                "Use read replicas for scaling",
                "Implement connection pooling",
                "Monitor query performance"
            ],
            "security_hardening": [
                "Rotate secrets regularly",
                "Use managed identities everywhere",
                "Enable Azure Security Center",
                "Implement conditional access",
                "Regular security assessments"
            ],
            "monitoring_observability": [
                "Set up actionable alerts only",
                "Use structured logging",
                "Implement distributed tracing",
                "Monitor business metrics",
                "Setup automated remediation"
            ],
            "disaster_recovery": [
                "Test recovery procedures regularly",
                "Document all recovery steps",
                "Automate backup verification",
                "Monitor recovery metrics",
                "Regular DR drills"
            ]
        }
        
        return patterns.get(job_name, [])
    
    def suggest_jobs_for_query(self, query: str) -> List[Dict[str, Any]]:
        """Suggest jobs based on user query"""
        query_lower = query.lower()
        suggestions = []
        
        for job_name, job_def in self.job_definitions.items():
            score = 0
            
            # Check job description
            if any(word in job_def["description"].lower() for word in query_lower.split()):
                score += 3
            
            # Check workflow steps
            for step in job_def["workflow"]:
                if any(word in step.lower() for word in query_lower.split()):
                    score += 2
            
            # Check tools needed
            for tool in job_def["tools_needed"]:
                if any(word in tool.lower() for word in query_lower.split()):
                    score += 1
            
            if score > 0:
                suggestions.append({
                    "job_name": job_name,
                    "score": score,
                    "description": job_def["description"],
                    "complexity": job_def["complexity"],
                    "estimated_time": job_def["estimated_time"]
                })
        
        # Sort by score
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return suggestions
    
    def get_available_jobs(self) -> List[Dict[str, Any]]:
        """Get all available job toolboxes"""
        jobs = []
        for job_name, job_def in self.job_definitions.items():
            jobs.append({
                "job_name": job_name,
                "description": job_def["description"],
                "complexity": job_def["complexity"],
                "estimated_time": job_def["estimated_time"],
                "categories": job_def["categories"]
            })
        
        return sorted(jobs, key=lambda x: x["complexity"])
    
    def generate_deployment_script(self, job_name: str, language: str = "python") -> str:
        """Generate deployment script for a job"""
        toolbox = self.get_toolbox_for_job(job_name)
        if not toolbox:
            return "Job not found"
        
        script_parts = [
            f"# Azure {job_name.replace('_', ' ').title()} Deployment Script",
            f"# Generated by Azure Job-Based Toolbox System",
            f"# Estimated time: {toolbox.estimated_time}",
            f"# Complexity: {toolbox.complexity}",
            "",
            "# Prerequisites:",
        ]
        
        for prereq in toolbox.prerequisites:
            script_parts.append(f"# - {prereq}")
        
        script_parts.extend([
            "",
            "# Workflow Steps:",
        ])
        
        for i, step in enumerate(toolbox.workflow_steps, 1):
            script_parts.append(f"# {i}. {step}")
        
        script_parts.extend([
            "",
            "# Required Tools:",
            f"# CLI Tools: {len(toolbox.cli_tools)}",
            f"# MCP Tools: {len(toolbox.mcp_tools)}",
            f"# SDK Tools: {len(toolbox.sdk_tools)}",
            "",
            "# Implementation would go here based on specific requirements",
        ])
        
        return "\n".join(script_parts)

def demo_job_toolbox_system():
    """Demonstrate the comprehensive job-based toolbox system"""
    
    print("=== AZURE JOB-BASED TOOLBOX SYSTEM ===")
    print("Built from comprehensive 858-tool repository\n")
    
    toolbox_system = AzureJobBasedToolbox(
        "/Users/mikaeleage/Research & Analytics Services/azure_tools_comprehensive.json"
    )
    
    # Show available jobs
    print("1. AVAILABLE JOB TOOLBOXES")
    print("-" * 50)
    jobs = toolbox_system.get_available_jobs()
    for job in jobs:
        print(f"  {job['job_name']}")
        print(f"    Description: {job['description']}")
        print(f"    Complexity: {job['complexity']} | Time: {job['estimated_time']}")
        print(f"    Categories: {', '.join(job['categories'])}")
        print()
    
    # Demo specific job toolbox
    print("2. SAMPLE JOB TOOLBOX: FRED Data Pipeline")
    print("-" * 50)
    fred_toolbox = toolbox_system.get_toolbox_for_job("fred_data_pipeline")
    
    if fred_toolbox:
        print(f"Job: {fred_toolbox.job_name}")
        print(f"Description: {fred_toolbox.description}")
        print(f"Complexity: {fred_toolbox.complexity} | Time: {fred_toolbox.estimated_time}")
        print(f"Total Tools: {fred_toolbox.total_tools}")
        
        print("\nWorkflow:")
        for i, step in enumerate(fred_toolbox.workflow_steps, 1):
            print(f"  {i}. {step}")
        
        print(f"\nCLI Tools ({len(fred_toolbox.cli_tools)}):")
        for tool in fred_toolbox.cli_tools[:5]:
            print(f"  • {tool['name']} - {tool['description'][:60]}...")
        
        print(f"\nSDK Tools ({len(fred_toolbox.sdk_tools)}):")
        for tool in fred_toolbox.sdk_tools[:5]:
            print(f"  • {tool['name']} ({tool['language']}) - {tool['description'][:50]}...")
        
        print("\nCommon Patterns:")
        for pattern in fred_toolbox.common_patterns:
            print(f"  • {pattern}")
    
    # Demo query suggestions
    print("\n3. QUERY-BASED JOB SUGGESTIONS")
    print("-" * 50)
    
    test_queries = [
        "I need to deploy a web application",
        "Setting up database with security",
        "Monitoring and observability",
        "Disaster recovery planning"
    ]
    
    for query in test_queries:
        print(f"Query: '{query}'")
        suggestions = toolbox_system.suggest_jobs_for_query(query)
        for suggestion in suggestions[:2]:
            print(f"  → {suggestion['job_name']} (score: {suggestion['score']})")
            print(f"    {suggestion['description']}")
        print()

if __name__ == "__main__":
    demo_job_toolbox_system()