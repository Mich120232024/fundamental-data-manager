#!/usr/bin/env python3
"""
Azure MCP Tools - Model Context Protocol Integration
First set of proven Azure tools using MCP SDK and CLI integration
"""

import os
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# MCP SDK imports (if available)
try:
    from mcp import ClientSession, StdioServerParameters
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP SDK not available, falling back to direct Azure CLI")

class AzureMCPTools:
    """Azure tools using Model Context Protocol and CLI integration"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = Path("./azure_mcp_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Tool registry
        self.tools = {
            'list_resources': self.list_resources,
            'get_resource_info': self.get_resource_info,
            'list_storage_accounts': self.list_storage_accounts,
            'check_synapse_status': self.check_synapse_status,
            'get_cost_analysis': self.get_cost_analysis,
            'verify_access': self.verify_access,
            'run_diagnostic': self.run_diagnostic
        }
        
        print(f"[AZURE-MCP] Initialized with {len(self.tools)} tools")
    
    def execute_azure_cli(self, command: str, output_format: str = "json") -> Dict[str, Any]:
        """Execute Azure CLI command with error handling and logging"""
        full_command = f"az {command}"
        if output_format:
            full_command += f" --output {output_format}"
        
        print(f"[AZURE-CLI] Executing: {full_command}")
        
        try:
            start_time = datetime.now()
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            end_time = datetime.now()
            
            execution_data = {
                'command': full_command,
                'exit_code': result.returncode,
                'duration_ms': int((end_time - start_time).total_seconds() * 1000),
                'timestamp': start_time.isoformat(),
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            if result.returncode == 0:
                # Parse JSON output if possible
                if output_format == "json" and result.stdout.strip():
                    try:
                        execution_data['parsed_output'] = json.loads(result.stdout)
                    except json.JSONDecodeError as e:
                        execution_data['parse_error'] = str(e)
                        execution_data['parsed_output'] = None
                
                print(f"[AZURE-CLI] ✅ Success in {execution_data['duration_ms']}ms")
            else:
                print(f"[AZURE-CLI] ❌ Failed with code {result.returncode}")
                print(f"[AZURE-CLI] Error: {result.stderr}")
            
            return execution_data
            
        except subprocess.TimeoutExpired:
            error_data = {
                'command': full_command,
                'error': 'timeout',
                'timeout_seconds': 120,
                'timestamp': datetime.now().isoformat()
            }
            print(f"[AZURE-CLI] ❌ Command timed out")
            return error_data
            
        except Exception as e:
            error_data = {
                'command': full_command,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"[AZURE-CLI] ❌ Exception: {e}")
            return error_data
    
    def list_resources(self, resource_group: Optional[str] = None) -> Dict[str, Any]:
        """List Azure resources with filtering options"""
        print(f"[TOOL] list_resources - resource_group: {resource_group}")
        
        command = "resource list"
        if resource_group:
            command += f" --resource-group {resource_group}"
        
        result = self.execute_azure_cli(command)
        
        if result.get('parsed_output'):
            resources = result['parsed_output']
            
            # Add summary statistics
            resource_types = {}
            locations = {}
            
            for resource in resources:
                res_type = resource.get('type', 'Unknown')
                location = resource.get('location', 'Unknown')
                
                resource_types[res_type] = resource_types.get(res_type, 0) + 1
                locations[location] = locations.get(location, 0) + 1
            
            summary = {
                'total_resources': len(resources),
                'resource_types': resource_types,
                'locations': locations,
                'resources': resources[:10]  # First 10 for brevity
            }
            
            result['summary'] = summary
            print(f"[TOOL] ✅ Found {len(resources)} resources")
        
        return result
    
    def get_resource_info(self, resource_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific resource"""
        print(f"[TOOL] get_resource_info - resource_id: {resource_id}")
        
        command = f"resource show --ids {resource_id}"
        result = self.execute_azure_cli(command)
        
        if result.get('parsed_output'):
            resource = result['parsed_output']
            
            # Extract key information
            summary = {
                'name': resource.get('name'),
                'type': resource.get('type'),
                'location': resource.get('location'),
                'resource_group': resource.get('resourceGroup'),
                'provisioning_state': resource.get('properties', {}).get('provisioningState'),
                'created_time': resource.get('properties', {}).get('createdTime'),
                'tags': resource.get('tags', {})
            }
            
            result['summary'] = summary
            print(f"[TOOL] ✅ Retrieved info for {summary['name']}")
        
        return result
    
    def list_storage_accounts(self) -> Dict[str, Any]:
        """List all storage accounts with key properties"""
        print(f"[TOOL] list_storage_accounts")
        
        result = self.execute_azure_cli("storage account list")
        
        if result.get('parsed_output'):
            accounts = result['parsed_output']
            
            # Extract key information for each account
            account_summary = []
            for account in accounts:
                summary = {
                    'name': account.get('name'),
                    'resource_group': account.get('resourceGroup'),
                    'location': account.get('location'),
                    'sku': account.get('sku', {}).get('name'),
                    'kind': account.get('kind'),
                    'access_tier': account.get('accessTier'),
                    'provisioning_state': account.get('provisioningState'),
                    'https_only': account.get('enableHttpsTrafficOnly'),
                    'blob_public_access': account.get('allowBlobPublicAccess')
                }
                account_summary.append(summary)
            
            result['account_summary'] = account_summary
            result['total_accounts'] = len(accounts)
            print(f"[TOOL] ✅ Found {len(accounts)} storage accounts")
        
        return result
    
    def check_synapse_status(self, workspace_name: Optional[str] = None) -> Dict[str, Any]:
        """Check Synapse workspace status and resources"""
        print(f"[TOOL] check_synapse_status - workspace: {workspace_name}")
        
        # List all Synapse workspaces
        result = self.execute_azure_cli("synapse workspace list")
        
        if result.get('parsed_output'):
            workspaces = result['parsed_output']
            
            # Filter by workspace name if provided
            if workspace_name:
                workspaces = [ws for ws in workspaces if ws.get('name') == workspace_name]
            
            workspace_details = []
            for workspace in workspaces:
                # Get additional details for each workspace
                ws_name = workspace.get('name')
                rg_name = workspace.get('resourceGroup')
                
                details = {
                    'name': ws_name,
                    'resource_group': rg_name,
                    'location': workspace.get('location'),
                    'provisioning_state': workspace.get('provisioningState'),
                    'sql_admin_login': workspace.get('sqlAdministratorLogin'),
                    'workspace_uid': workspace.get('workspaceUID'),
                    'connectivity_endpoints': workspace.get('connectivityEndpoints', {})
                }
                
                # Get Spark pools for this workspace
                spark_result = self.execute_azure_cli(
                    f"synapse spark pool list --workspace-name {ws_name} --resource-group {rg_name}"
                )
                
                if spark_result.get('parsed_output'):
                    spark_pools = spark_result['parsed_output']
                    details['spark_pools'] = [
                        {
                            'name': pool.get('name'),
                            'node_count': pool.get('nodeCount'),
                            'node_size': pool.get('nodeSize'),
                            'auto_scale': pool.get('autoScale', {}).get('enabled'),
                            'provisioning_state': pool.get('provisioningState')
                        }
                        for pool in spark_pools
                    ]
                    details['spark_pool_count'] = len(spark_pools)
                else:
                    details['spark_pools'] = []
                    details['spark_pool_count'] = 0
                
                workspace_details.append(details)
            
            result['workspace_details'] = workspace_details
            result['total_workspaces'] = len(workspaces)
            print(f"[TOOL] ✅ Found {len(workspaces)} Synapse workspaces")
        
        return result
    
    def get_cost_analysis(self, scope: str = "subscription", days: int = 30) -> Dict[str, Any]:
        """Get cost analysis for Azure resources"""
        print(f"[TOOL] get_cost_analysis - scope: {scope}, days: {days}")
        
        # Azure CLI cost management command
        command = f"costmanagement query --type Usage --timeframe Custom --time-period from={days}DaysAgo to=today --dataset-granularity Daily"
        
        result = self.execute_azure_cli(command)
        
        if result.get('parsed_output'):
            cost_data = result['parsed_output']
            
            # Process cost data if available
            if isinstance(cost_data, dict) and 'rows' in cost_data:
                rows = cost_data['rows']
                columns = cost_data.get('columns', [])
                
                # Create summary
                total_cost = 0
                daily_costs = []
                
                for row in rows:
                    if len(row) > 0:
                        try:
                            cost_value = float(row[0]) if row[0] else 0
                            total_cost += cost_value
                            daily_costs.append(cost_value)
                        except (ValueError, IndexError):
                            continue
                
                cost_summary = {
                    'total_cost': total_cost,
                    'average_daily_cost': total_cost / days if days > 0 else 0,
                    'max_daily_cost': max(daily_costs) if daily_costs else 0,
                    'min_daily_cost': min(daily_costs) if daily_costs else 0,
                    'days_analyzed': days,
                    'data_points': len(rows)
                }
                
                result['cost_summary'] = cost_summary
                print(f"[TOOL] ✅ Cost analysis: ${total_cost:.2f} over {days} days")
            else:
                print(f"[TOOL] ⚠️ Cost data format not recognized")
        
        return result
    
    def verify_access(self) -> Dict[str, Any]:
        """Verify Azure access and permissions"""
        print(f"[TOOL] verify_access")
        
        verification_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # Test 1: Account info
        account_result = self.execute_azure_cli("account show")
        if account_result.get('parsed_output'):
            account = account_result['parsed_output']
            verification_results['tests']['account'] = {
                'status': 'success',
                'subscription_id': account.get('id'),
                'subscription_name': account.get('name'),
                'tenant_id': account.get('tenantId'),
                'user': account.get('user', {}).get('name')
            }
        else:
            verification_results['tests']['account'] = {
                'status': 'failed',
                'error': account_result.get('stderr', 'Unknown error')
            }
        
        # Test 2: Resource group access
        rg_result = self.execute_azure_cli("group list")
        if rg_result.get('parsed_output'):
            resource_groups = rg_result['parsed_output']
            verification_results['tests']['resource_groups'] = {
                'status': 'success',
                'count': len(resource_groups),
                'names': [rg.get('name') for rg in resource_groups[:5]]
            }
        else:
            verification_results['tests']['resource_groups'] = {
                'status': 'failed',
                'error': rg_result.get('stderr', 'Unknown error')
            }
        
        # Test 3: Storage account access
        storage_result = self.execute_azure_cli("storage account list")
        if storage_result.get('parsed_output'):
            storage_accounts = storage_result['parsed_output']
            verification_results['tests']['storage_accounts'] = {
                'status': 'success',
                'count': len(storage_accounts)
            }
        else:
            verification_results['tests']['storage_accounts'] = {
                'status': 'failed',
                'error': storage_result.get('stderr', 'Unknown error')
            }
        
        # Calculate overall status
        successful_tests = sum(1 for test in verification_results['tests'].values() if test['status'] == 'success')
        total_tests = len(verification_results['tests'])
        verification_results['overall_status'] = 'success' if successful_tests == total_tests else 'partial'
        verification_results['success_rate'] = successful_tests / total_tests if total_tests > 0 else 0
        
        print(f"[TOOL] ✅ Access verification: {successful_tests}/{total_tests} tests passed")
        
        return verification_results
    
    def run_diagnostic(self) -> Dict[str, Any]:
        """Run comprehensive Azure diagnostic tests"""
        print(f"[TOOL] run_diagnostic")
        
        diagnostic_results = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'diagnostics': {}
        }
        
        # Diagnostic 1: Azure CLI version
        version_result = self.execute_azure_cli("version", output_format="json")
        if version_result.get('parsed_output'):
            diagnostic_results['diagnostics']['azure_cli'] = {
                'status': 'success',
                'version_info': version_result['parsed_output']
            }
        else:
            diagnostic_results['diagnostics']['azure_cli'] = {
                'status': 'failed',
                'error': version_result.get('stderr', 'Unknown error')
            }
        
        # Diagnostic 2: Configuration
        config_result = self.execute_azure_cli("configure --list-defaults", output_format="table")
        diagnostic_results['diagnostics']['configuration'] = {
            'status': 'success' if config_result.get('exit_code') == 0 else 'failed',
            'config_output': config_result.get('stdout', '')
        }
        
        # Diagnostic 3: Extensions
        ext_result = self.execute_azure_cli("extension list")
        if ext_result.get('parsed_output'):
            extensions = ext_result['parsed_output']
            diagnostic_results['diagnostics']['extensions'] = {
                'status': 'success',
                'count': len(extensions),
                'extensions': [ext.get('name') for ext in extensions]
            }
        else:
            diagnostic_results['diagnostics']['extensions'] = {
                'status': 'failed',
                'error': ext_result.get('stderr', 'Unknown error')
            }
        
        # Save diagnostic results
        diag_file = self.results_dir / f"diagnostic_{self.session_id}.json"
        with open(diag_file, 'w') as f:
            json.dump(diagnostic_results, f, indent=2)
        
        print(f"[TOOL] ✅ Diagnostic completed, saved to {diag_file}")
        
        return diagnostic_results
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a specific tool by name"""
        if tool_name not in self.tools:
            return {
                'error': f"Tool '{tool_name}' not found",
                'available_tools': list(self.tools.keys())
            }
        
        try:
            result = self.tools[tool_name](**kwargs)
            
            # Save result to file
            result_file = self.results_dir / f"{tool_name}_{self.session_id}.json"
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            return result
            
        except Exception as e:
            error_result = {
                'tool_name': tool_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"[TOOL] ❌ Error in {tool_name}: {e}")
            return error_result

def test_azure_mcp_tools():
    """Test the Azure MCP tools"""
    print("=" * 60)
    print("AZURE MCP TOOLS TEST")
    print("=" * 60)
    
    tools = AzureMCPTools()
    
    # Test each tool
    test_results = {}
    
    # 1. Verify access
    print("\n1. Testing access verification...")
    test_results['verify_access'] = tools.execute_tool('verify_access')
    
    # 2. List resources
    print("\n2. Testing resource listing...")
    test_results['list_resources'] = tools.execute_tool('list_resources')
    
    # 3. Storage accounts
    print("\n3. Testing storage account listing...")
    test_results['list_storage_accounts'] = tools.execute_tool('list_storage_accounts')
    
    # 4. Synapse status
    print("\n4. Testing Synapse status...")
    test_results['check_synapse_status'] = tools.execute_tool('check_synapse_status')
    
    # 5. Run diagnostic
    print("\n5. Testing diagnostic...")
    test_results['run_diagnostic'] = tools.execute_tool('run_diagnostic')
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for tool_name, result in test_results.items():
        if 'error' in result:
            print(f"❌ {tool_name}: {result['error']}")
        else:
            print(f"✅ {tool_name}: Success")
    
    return test_results

def test_real_resources():
    """Test with real Azure resources from HEAD_OF_ENGINEERING config"""
    from azure_config import get_azure_config, get_synapse_workspace
    
    print("=" * 60)
    print("TESTING WITH REAL AZURE RESOURCES")
    print("=" * 60)
    
    config = get_azure_config()
    print(f"Resource Group: {config['resource_group']}")
    print(f"Synapse Workspace: {config['synapse_workspace']}")
    print(f"Storage Account: {config['storage_account']}")
    
    tools = AzureMCPTools()
    
    # Test with real Synapse workspace
    synapse_result = tools.execute_tool('check_synapse_status', workspace_name=get_synapse_workspace())
    print(f"Synapse Test: {'✅ Success' if 'error' not in synapse_result else '❌ Failed'}")
    
    return synapse_result

if __name__ == "__main__":
    # Test with real resources first
    test_real_resources()
    print("\n" + "="*60 + "\n")
    # Then run full test suite
    test_azure_mcp_tools()