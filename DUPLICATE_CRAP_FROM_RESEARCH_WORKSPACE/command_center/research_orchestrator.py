"""
Advanced Research Command Center
Orchestrates multi-agent research workflows with real-time monitoring
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json

from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential


class ResearchStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ResearchTask:
    id: str
    title: str
    description: str
    assigned_agents: List[str]
    status: ResearchStatus
    priority: int
    created_at: datetime
    updated_at: datetime
    data_sources: List[str]
    results: Optional[Dict[str, Any]] = None
    evidence_links: List[str] = None


class ResearchOrchestrator:
    """
    Central orchestrator for advanced research operations
    Manages agent coordination, task distribution, and result synthesis
    """
    
    def __init__(self, cosmos_endpoint: str, database_name: str = "ResearchDB"):
        self.credential = DefaultAzureCredential()
        self.cosmos_client = CosmosClient(cosmos_endpoint, self.credential)
        self.database = self.cosmos_client.get_database_client(database_name)
        self.tasks_container = self.database.get_container_client("research_tasks")
        self.agents_container = self.database.get_container_client("agent_mailboxes")
        
        self.logger = logging.getLogger(__name__)
        self.active_tasks: Dict[str, ResearchTask] = {}
        
        # Available research agents
        self.research_agents = [
            "Research_Advanced_Analyst",
            "Research_Quantitative_Analyst", 
            "Research_Strategy_Analyst",
            "Data_Analyst",
            "HEAD_OF_RESEARCH"
        ]
    
    async def create_research_project(
        self,
        title: str,
        description: str,
        data_sources: List[str],
        priority: int = 5,
        agent_assignments: Optional[Dict[str, List[str]]] = None
    ) -> str:
        """
        Create comprehensive research project with automated agent assignment
        """
        task_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Auto-assign agents based on task requirements
        if not agent_assignments:
            assigned_agents = self._auto_assign_agents(description, data_sources)
        else:
            assigned_agents = [agent for agents in agent_assignments.values() for agent in agents]
        
        task = ResearchTask(
            id=task_id,
            title=title,
            description=description,
            assigned_agents=assigned_agents,
            status=ResearchStatus.PENDING,
            priority=priority,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            data_sources=data_sources,
            evidence_links=[]
        )
        
        # Store in Cosmos DB
        await self._store_task(task)
        self.active_tasks[task_id] = task
        
        # Dispatch to agents
        await self._dispatch_to_agents(task)
        
        self.logger.info(f"Created research project: {task_id}")
        return task_id
    
    def _auto_assign_agents(self, description: str, data_sources: List[str]) -> List[str]:
        """
        Intelligent agent assignment based on task characteristics
        """
        assigned = []
        desc_lower = description.lower()
        
        # Strategy analyst for high-level analysis
        if any(word in desc_lower for word in ["strategy", "trend", "outlook", "forecast"]):
            assigned.append("Research_Strategy_Analyst")
        
        # Quantitative analyst for data-heavy tasks
        if any(word in desc_lower for word in ["statistical", "model", "regression", "analysis"]):
            assigned.append("Research_Quantitative_Analyst")
        
        # Advanced analyst for complex synthesis
        if any(word in desc_lower for word in ["comprehensive", "deep", "advanced", "investigation"]):
            assigned.append("Research_Advanced_Analyst")
        
        # Data analyst for API/data tasks
        if any(source in ["fred", "bloomberg", "api"] for source in data_sources):
            assigned.append("Data_Analyst")
        
        # Always include head of research for coordination
        assigned.append("HEAD_OF_RESEARCH")
        
        return list(set(assigned))  # Remove duplicates
    
    async def _store_task(self, task: ResearchTask):
        """Store task in Cosmos DB"""
        task_dict = asdict(task)
        task_dict['created_at'] = task.created_at.isoformat()
        task_dict['updated_at'] = task.updated_at.isoformat()
        task_dict['status'] = task.status.value
        
        await self.tasks_container.upsert_item(task_dict)
    
    async def _dispatch_to_agents(self, task: ResearchTask):
        """
        Send task instructions to assigned agents via mailbox system
        """
        for agent in task.assigned_agents:
            message = {
                "id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "task_id": task.id,
                "agent": agent,
                "instruction": f"""
Research Task Assignment:
Title: {task.title}
Description: {task.description}
Data Sources: {', '.join(task.data_sources)}
Priority: {task.priority}

Expected Deliverables:
- Analysis report with evidence citations
- Data visualizations where applicable  
- Methodology documentation
- Source verification

Coordination: Report progress to HEAD_OF_RESEARCH
Evidence Requirement: All claims must include file:line citations
                """,
                "timestamp": datetime.now().isoformat(),
                "status": "pending"
            }
            
            # Store in agent's mailbox
            await self.agents_container.upsert_item(message)
    
    async def get_research_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of research task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "id": task.id,
                "title": task.title,
                "status": task.status.value,
                "assigned_agents": task.assigned_agents,
                "progress": await self._calculate_progress(task_id),
                "last_updated": task.updated_at.isoformat()
            }
        return None
    
    async def _calculate_progress(self, task_id: str) -> Dict[str, Any]:
        """Calculate research progress based on agent responses"""
        # Query agent responses for this task
        query = f"SELECT * FROM c WHERE c.task_id = '{task_id}' AND c.status = 'completed'"
        responses = list(self.agents_container.query_items(query, enable_cross_partition_query=True))
        
        total_agents = len(self.active_tasks[task_id].assigned_agents)
        completed_responses = len(responses)
        
        return {
            "completion_percentage": (completed_responses / total_agents) * 100,
            "completed_agents": completed_responses,
            "total_agents": total_agents,
            "pending_agents": total_agents - completed_responses
        }
    
    async def synthesize_results(self, task_id: str) -> Dict[str, Any]:
        """
        Synthesize results from all agents into comprehensive research report
        """
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        # Collect all agent responses
        query = f"SELECT * FROM c WHERE c.task_id = '{task_id}'"
        responses = list(self.agents_container.query_items(query, enable_cross_partition_query=True))
        
        synthesis = {
            "task_id": task_id,
            "title": self.active_tasks[task_id].title,
            "executive_summary": "",
            "key_findings": [],
            "evidence_links": [],
            "methodology": "",
            "agent_contributions": {},
            "generated_at": datetime.now().isoformat()
        }
        
        # Process each agent's contribution
        for response in responses:
            agent = response.get("agent", "unknown")
            synthesis["agent_contributions"][agent] = {
                "analysis": response.get("analysis", ""),
                "findings": response.get("findings", []),
                "evidence": response.get("evidence", []),
                "methodology": response.get("methodology", "")
            }
        
        # Update task status
        self.active_tasks[task_id].status = ResearchStatus.COMPLETED
        self.active_tasks[task_id].results = synthesis
        await self._store_task(self.active_tasks[task_id])
        
        return synthesis


# Research dashboard interface
class ResearchDashboard:
    """
    Web-based interface for research monitoring and control
    """
    
    def __init__(self, orchestrator: ResearchOrchestrator):
        self.orchestrator = orchestrator
    
    async def get_active_projects(self) -> List[Dict[str, Any]]:
        """Get all active research projects"""
        projects = []
        for task_id, task in self.orchestrator.active_tasks.items():
            status = await self.orchestrator.get_research_status(task_id)
            projects.append(status)
        return projects
    
    async def get_agent_workload(self) -> Dict[str, int]:
        """Get current workload distribution across agents"""
        workload = {agent: 0 for agent in self.orchestrator.research_agents}
        
        for task in self.orchestrator.active_tasks.values():
            if task.status in [ResearchStatus.PENDING, ResearchStatus.IN_PROGRESS]:
                for agent in task.assigned_agents:
                    workload[agent] += 1
        
        return workload