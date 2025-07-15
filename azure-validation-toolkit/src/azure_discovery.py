#!/usr/bin/env python3
"""
Azure Resource Discovery Tool
Real discovery of Azure resources using authenticated Azure CLI session
"""

import subprocess
import json
import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.synapse import SynapseManagementClient

def get_subscription_id():
    """Get subscription ID from Azure CLI"""
    try:
        result = subprocess.run(['az', 'account', 'show'], capture_output=True, text=True)
        if result.returncode == 0:
            account = json.loads(result.stdout)
            return account['id']
    except Exception as e:
        print(f"Error getting subscription: {e}")
    return None

def discover_synapse_workspaces():
    """Discover real Synapse workspaces"""
    print("🔍 Discovering Synapse Analytics workspaces...")
    
    try:
        result = subprocess.run([
            'az', 'synapse', 'workspace', 'list', '--output', 'json'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            workspaces = json.loads(result.stdout)
            print(f"Found {len(workspaces)} Synapse workspace(s):")
            
            for ws in workspaces:
                print(f"  📊 Name: {ws['name']}")
                print(f"     Resource Group: {ws['resourceGroup']}")
                print(f"     Location: {ws['location']}")
                print(f"     Status: {ws.get('provisioningState', 'Unknown')}")
                
                # Get Spark pools
                pools_result = subprocess.run([
                    'az', 'synapse', 'spark', 'pool', 'list', 
                    '--workspace-name', ws['name'], '--output', 'json'
                ], capture_output=True, text=True)
                
                if pools_result.returncode == 0:
                    pools = json.loads(pools_result.stdout)
                    print(f"     Spark Pools: {len(pools)}")
                    for pool in pools:
                        print(f"       - {pool['name']} ({pool.get('nodeSize', 'Unknown')} nodes)")
                
                print()
                
            return workspaces
        else:
            print(f"❌ Error discovering workspaces: {result.stderr}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def discover_storage_accounts():
    """Discover storage accounts"""
    print("🔍 Discovering Storage accounts...")
    
    try:
        result = subprocess.run([
            'az', 'storage', 'account', 'list', '--output', 'json'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            accounts = json.loads(result.stdout)
            print(f"Found {len(accounts)} storage account(s):")
            
            for acc in accounts:
                print(f"  💾 Name: {acc['name']}")
                print(f"     Resource Group: {acc['resourceGroup']}")
                print(f"     Location: {acc['location']}")
                print(f"     Kind: {acc['kind']}")
                print(f"     Tier: {acc['sku']['tier']}")
                print()
                
            return accounts
        else:
            print(f"❌ Error discovering storage: {result.stderr}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def discover_key_vaults():
    """Discover Key Vaults"""
    print("🔍 Discovering Key Vaults...")
    
    try:
        result = subprocess.run([
            'az', 'keyvault', 'list', '--output', 'json'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            vaults = json.loads(result.stdout)
            print(f"Found {len(vaults)} Key Vault(s):")
            
            for vault in vaults:
                print(f"  🔐 Name: {vault['name']}")
                print(f"     Resource Group: {vault['resourceGroup']}")
                print(f"     Location: {vault['location']}")
                print(f"     Vault URI: {vault['properties']['vaultUri']}")
                print()
                
            return vaults
        else:
            print(f"❌ Error discovering key vaults: {result.stderr}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_synapse_connection(workspace_name):
    """Test connection to specific Synapse workspace"""
    print(f"🧪 Testing connection to Synapse workspace: {workspace_name}")
    
    try:
        # Test listing notebooks
        result = subprocess.run([
            'az', 'synapse', 'notebook', 'list',
            '--workspace-name', workspace_name,
            '--output', 'json'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            notebooks = json.loads(result.stdout)
            print(f"✅ Successfully connected! Found {len(notebooks)} notebook(s)")
            
            for nb in notebooks[:3]:  # Show first 3
                print(f"   - {nb['name']}")
                
            return True
        else:
            print(f"❌ Connection failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def generate_environment_config(workspaces, storage_accounts, key_vaults):
    """Generate environment configuration from discovered resources"""
    print("📝 Generating environment configuration...")
    
    if not workspaces:
        print("❌ No Synapse workspaces found")
        return
    
    # Use first workspace found
    workspace = workspaces[0]
    storage = storage_accounts[0] if storage_accounts else None
    vault = key_vaults[0] if key_vaults else None
    
    config = f"""
# Azure Environment Configuration (discovered resources)
export AZURE_SUBSCRIPTION_ID="{get_subscription_id()}"
export AZURE_RESOURCE_GROUP="{workspace['resourceGroup']}"
export AZURE_SYNAPSE_WORKSPACE="{workspace['name']}"
"""
    
    if storage:
        config += f'export AZURE_STORAGE_ACCOUNT="{storage["name"]}"\n'
    
    if vault:
        config += f'export AZURE_KEY_VAULT_NAME="{vault["name"]}"\n'
    
    config += f'export AZURE_LOCATION="{workspace["location"]}"\n'
    
    print("Environment configuration:")
    print(config)
    
    # Save to file
    with open('azure_env_config.sh', 'w') as f:
        f.write(config)
    print("✅ Configuration saved to azure_env_config.sh")

def main():
    """Main discovery process"""
    print("🚀 Azure Resource Discovery Tool")
    print("=" * 50)
    
    # Check Azure CLI login
    sub_id = get_subscription_id()
    if not sub_id:
        print("❌ Not logged into Azure CLI. Run 'az login' first.")
        return
    
    print(f"✅ Authenticated with subscription: {sub_id}")
    print()
    
    # Discover resources
    workspaces = discover_synapse_workspaces()
    storage_accounts = discover_storage_accounts()
    key_vaults = discover_key_vaults()
    
    # Test connection to first workspace
    if workspaces:
        test_synapse_connection(workspaces[0]['name'])
    
    # Generate configuration
    generate_environment_config(workspaces, storage_accounts, key_vaults)
    
    print("🎯 Discovery complete!")

if __name__ == "__main__":
    main()