#!/usr/bin/env python3
"""
Synapse Control Module - Full Workspace Management
Complete control over Synapse pipelines, notebooks, and operations
"""

import os
import json
import time
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.synapse.artifacts import ArtifactsClient
from azure.synapse.monitoring import MonitoringClient
from azure.synapse.spark import SparkClient
from azure.mgmt.synapse import SynapseManagementClient

class SynapseController:
    """Full control over Azure Synapse Analytics workspace"""
    
    def __init__(self, workspace_name=None, subscription_id=None):
        # Use real workspace from HEAD_OF_ENGINEERING config
        from azure_config import get_synapse_workspace, AZURE_CONFIG
        
        self.workspace_name = workspace_name or get_synapse_workspace()
        self.subscription_id = subscription_id or os.getenv('AZURE_SUBSCRIPTION_ID')
        self.workspace_url = AZURE_CONFIG["synapse_endpoint"]
        self.resource_group = AZURE_CONFIG["resource_group"]
        
        # Initialize credentials
        self.credential = DefaultAzureCredential()
        
        # Initialize clients
        self.artifacts_client = ArtifactsClient(
            credential=self.credential,
            endpoint=self.workspace_url
        )
        
        self.monitoring_client = MonitoringClient(
            credential=self.credential,
            endpoint=self.workspace_url
        )
        
        self.spark_client = SparkClient(
            credential=self.credential,
            endpoint=self.workspace_url
        )
        
        self.mgmt_client = SynapseManagementClient(
            credential=self.credential,
            subscription_id=self.subscription_id
        )
    
    def list_pipelines(self):
        """List all pipelines in workspace"""
        print(f"[{datetime.now()}] Listing pipelines in {self.workspace_name}...")
        
        try:
            pipelines = list(self.artifacts_client.pipeline.get_pipelines_by_workspace())
            results = []
            
            for pipeline in pipelines:
                pipeline_info = {
                    'name': pipeline.name,
                    'type': pipeline.type,
                    'etag': pipeline.etag,
                    'activities_count': len(pipeline.properties.activities) if pipeline.properties.activities else 0
                }
                results.append(pipeline_info)
            
            print(f"✅ Found {len(results)} pipelines")
            return results
            
        except Exception as e:
            print(f"❌ Failed to list pipelines: {e}")
            return []
    
    def run_pipeline(self, pipeline_name, parameters=None):
        """Execute a pipeline with optional parameters"""
        print(f"[{datetime.now()}] Running pipeline: {pipeline_name}")
        
        try:
            # Start pipeline run
            run_response = self.artifacts_client.pipeline_run.run_pipeline(
                pipeline_name=pipeline_name,
                parameters=parameters or {}
            )
            
            run_id = run_response.run_id
            print(f"✅ Pipeline started - Run ID: {run_id}")
            
            return {
                'run_id': run_id,
                'pipeline_name': pipeline_name,
                'status': 'InProgress',
                'start_time': datetime.now().isoformat(),
                'parameters': parameters
            }
            
        except Exception as e:
            print(f"❌ Failed to run pipeline {pipeline_name}: {e}")
            return None
    
    def get_pipeline_status(self, run_id):
        """Get status of pipeline run"""
        try:
            run_status = self.monitoring_client.pipeline_run.get_pipeline_run(run_id)
            
            return {
                'run_id': run_id,
                'status': run_status.status,
                'pipeline_name': run_status.pipeline_name,
                'run_start': run_status.run_start.isoformat() if run_status.run_start else None,
                'run_end': run_status.run_end.isoformat() if run_status.run_end else None,
                'duration_ms': run_status.duration_in_ms,
                'message': run_status.message
            }
            
        except Exception as e:
            print(f"❌ Failed to get pipeline status: {e}")
            return None
    
    def wait_for_pipeline(self, run_id, timeout_minutes=30):
        """Wait for pipeline completion with timeout"""
        print(f"[{datetime.now()}] Waiting for pipeline {run_id} to complete...")
        
        start_time = datetime.now()
        timeout = timedelta(minutes=timeout_minutes)
        
        while datetime.now() - start_time < timeout:
            status = self.get_pipeline_status(run_id)
            
            if not status:
                return None
            
            print(f"Pipeline {run_id} status: {status['status']}")
            
            if status['status'] in ['Succeeded', 'Failed', 'Cancelled']:
                return status
            
            time.sleep(30)  # Check every 30 seconds
        
        print(f"❌ Pipeline {run_id} timed out after {timeout_minutes} minutes")
        return self.get_pipeline_status(run_id)
    
    def list_notebooks(self):
        """List all notebooks in workspace"""
        print(f"[{datetime.now()}] Listing notebooks in {self.workspace_name}...")
        
        try:
            notebooks = list(self.artifacts_client.notebook.get_notebooks_by_workspace())
            results = []
            
            for notebook in notebooks:
                notebook_info = {
                    'name': notebook.name,
                    'type': notebook.type,
                    'etag': notebook.etag,
                    'language': notebook.properties.language_info.name if notebook.properties.language_info else 'Unknown'
                }
                results.append(notebook_info)
            
            print(f"✅ Found {len(results)} notebooks")
            return results
            
        except Exception as e:
            print(f"❌ Failed to list notebooks: {e}")
            return []
    
    def get_notebook_content(self, notebook_name):
        """Get notebook content and metadata"""
        try:
            notebook = self.artifacts_client.notebook.get_notebook(notebook_name)
            
            return {
                'name': notebook.name,
                'language': notebook.properties.language_info.name if notebook.properties.language_info else 'Unknown',
                'cells_count': len(notebook.properties.cells) if notebook.properties.cells else 0,
                'metadata': notebook.properties.metadata,
                'etag': notebook.etag
            }
            
        except Exception as e:
            print(f"❌ Failed to get notebook {notebook_name}: {e}")
            return None
    
    def list_spark_pools(self):
        """List all Spark pools in workspace"""
        print(f"[{datetime.now()}] Listing Spark pools in {self.workspace_name}...")
        
        try:
            # Need resource group name for this call
            resource_groups = list(self.mgmt_client.resource_groups.list())
            
            all_pools = []
            for rg in resource_groups:
                try:
                    pools = list(self.mgmt_client.big_data_pools.list_by_workspace(
                        resource_group_name=rg.name,
                        workspace_name=self.workspace_name
                    ))
                    
                    for pool in pools:
                        pool_info = {
                            'name': pool.name,
                            'location': pool.location,
                            'provisioning_state': pool.provisioning_state,
                            'auto_scale': pool.auto_scale.enabled if pool.auto_scale else False,
                            'node_count': pool.node_count,
                            'node_size': pool.node_size
                        }
                        all_pools.append(pool_info)
                        
                except:
                    continue  # Workspace might not be in this RG
            
            print(f"✅ Found {len(all_pools)} Spark pools")
            return all_pools
            
        except Exception as e:
            print(f"❌ Failed to list Spark pools: {e}")
            return []
    
    def get_recent_pipeline_runs(self, hours=24):
        """Get recent pipeline runs for monitoring"""
        print(f"[{datetime.now()}] Getting pipeline runs from last {hours} hours...")
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            runs = list(self.monitoring_client.pipeline_run.query_pipeline_runs_by_workspace(
                filter_parameters={
                    'lastUpdatedAfter': start_time.isoformat(),
                    'lastUpdatedBefore': end_time.isoformat()
                }
            ))
            
            results = []
            for run in runs:
                run_info = {
                    'run_id': run.run_id,
                    'pipeline_name': run.pipeline_name,
                    'status': run.status,
                    'run_start': run.run_start.isoformat() if run.run_start else None,
                    'run_end': run.run_end.isoformat() if run.run_end else None,
                    'duration_ms': run.duration_in_ms
                }
                results.append(run_info)
            
            print(f"✅ Found {len(results)} pipeline runs")
            return results
            
        except Exception as e:
            print(f"❌ Failed to get pipeline runs: {e}")
            return []
    
    def workspace_status(self):
        """Get comprehensive workspace status"""
        print(f"[{datetime.now()}] Getting workspace status for {self.workspace_name}...")
        
        status = {
            'workspace_name': self.workspace_name,
            'timestamp': datetime.now().isoformat(),
            'pipelines': self.list_pipelines(),
            'notebooks': self.list_notebooks(),
            'spark_pools': self.list_spark_pools(),
            'recent_runs': self.get_recent_pipeline_runs(hours=24)
        }
        
        # Summary statistics
        status['summary'] = {
            'total_pipelines': len(status['pipelines']),
            'total_notebooks': len(status['notebooks']),
            'total_spark_pools': len(status['spark_pools']),
            'recent_runs': len(status['recent_runs']),
            'successful_runs': len([r for r in status['recent_runs'] if r['status'] == 'Succeeded']),
            'failed_runs': len([r for r in status['recent_runs'] if r['status'] == 'Failed'])
        }
        
        return status

def test_synapse_control(workspace_name):
    """Test Synapse control functionality"""
    print("=" * 60)
    print(f"SYNAPSE CONTROL TEST - {workspace_name}")
    print("=" * 60)
    
    controller = SynapseController(workspace_name)
    
    # Get workspace status
    status = controller.workspace_status()
    
    print(f"\nWorkspace Summary:")
    print(f"Pipelines: {status['summary']['total_pipelines']}")
    print(f"Notebooks: {status['summary']['total_notebooks']}")
    print(f"Spark Pools: {status['summary']['total_spark_pools']}")
    print(f"Recent Runs (24h): {status['summary']['recent_runs']}")
    print(f"Success Rate: {status['summary']['successful_runs']}/{status['summary']['recent_runs']}")
    
    return status

if __name__ == "__main__":
    # Use REAL production Synapse workspace - NO DEFAULTS
    from azure_config import get_synapse_workspace
    workspace_name = os.getenv('SYNAPSE_WORKSPACE_NAME', get_synapse_workspace())
    test_synapse_control(workspace_name)