#!/usr/bin/env python3
"""
Azure Authentication Module - Working Implementation
Provides tested authentication patterns for all Azure operations
"""

import os
import sys
from datetime import datetime
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential, ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.synapse import SynapseManagementClient
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient

class AzureAuthenticator:
    """Centralized Azure authentication with multiple credential fallbacks"""
    
    def __init__(self, subscription_id=None):
        self.subscription_id = subscription_id or os.getenv('AZURE_SUBSCRIPTION_ID')
        self.credential = None
        self.authenticated_clients = {}
        
        if not self.subscription_id:
            raise ValueError("AZURE_SUBSCRIPTION_ID environment variable required")
    
    def authenticate(self):
        """Establish Azure credentials with fallback patterns"""
        print(f"[{datetime.now()}] Starting Azure authentication...")
        
        # Try DefaultAzureCredential first (recommended)
        try:
            self.credential = DefaultAzureCredential()
            # Test credential by listing resource groups
            resource_client = ResourceManagementClient(self.credential, self.subscription_id)
            rgs = list(resource_client.resource_groups.list())
            print(f"✅ DefaultAzureCredential successful - Found {len(rgs)} resource groups")
            return True
            
        except Exception as e:
            print(f"❌ DefaultAzureCredential failed: {e}")
        
        # Try Managed Identity (for Azure-hosted scenarios)
        try:
            self.credential = ManagedIdentityCredential()
            resource_client = ResourceManagementClient(self.credential, self.subscription_id)
            rgs = list(resource_client.resource_groups.list())
            print(f"✅ ManagedIdentityCredential successful - Found {len(rgs)} resource groups")
            return True
            
        except Exception as e:
            print(f"❌ ManagedIdentityCredential failed: {e}")
        
        # Try Service Principal (if environment variables set)
        if all(os.getenv(var) for var in ['AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID']):
            try:
                self.credential = ClientSecretCredential(
                    tenant_id=os.getenv('AZURE_TENANT_ID'),
                    client_id=os.getenv('AZURE_CLIENT_ID'),
                    client_secret=os.getenv('AZURE_CLIENT_SECRET')
                )
                resource_client = ResourceManagementClient(self.credential, self.subscription_id)
                rgs = list(resource_client.resource_groups.list())
                print(f"✅ ClientSecretCredential successful - Found {len(rgs)} resource groups")
                return True
                
            except Exception as e:
                print(f"❌ ClientSecretCredential failed: {e}")
        
        print("❌ All authentication methods failed")
        return False
    
    def get_resource_client(self):
        """Get authenticated Resource Management client"""
        if 'resource' not in self.authenticated_clients:
            self.authenticated_clients['resource'] = ResourceManagementClient(
                self.credential, self.subscription_id
            )
        return self.authenticated_clients['resource']
    
    def get_storage_client(self):
        """Get authenticated Storage Management client"""
        if 'storage' not in self.authenticated_clients:
            self.authenticated_clients['storage'] = StorageManagementClient(
                self.credential, self.subscription_id
            )
        return self.authenticated_clients['storage']
    
    def get_synapse_client(self):
        """Get authenticated Synapse Management client"""
        if 'synapse' not in self.authenticated_clients:
            self.authenticated_clients['synapse'] = SynapseManagementClient(
                self.credential, self.subscription_id
            )
        return self.authenticated_clients['synapse']
    
    def get_blob_client(self, storage_account_name):
        """Get authenticated Blob Service client"""
        account_url = f"https://{storage_account_name}.blob.core.windows.net"
        return BlobServiceClient(account_url=account_url, credential=self.credential)
    
    def get_cosmos_client(self, account_endpoint):
        """Get authenticated Cosmos DB client"""
        return CosmosClient(account_endpoint, credential=self.credential)
    
    def verify_access(self):
        """Verify access to core Azure services"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'subscription_id': self.subscription_id,
            'tests': {}
        }
        
        # Test Resource Groups access
        try:
            resource_client = self.get_resource_client()
            rgs = list(resource_client.resource_groups.list())
            results['tests']['resource_groups'] = {
                'status': 'success',
                'count': len(rgs),
                'names': [rg.name for rg in rgs[:5]]  # First 5 names
            }
        except Exception as e:
            results['tests']['resource_groups'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # Test Storage Accounts access
        try:
            storage_client = self.get_storage_client()
            accounts = list(storage_client.storage_accounts.list())
            results['tests']['storage_accounts'] = {
                'status': 'success',
                'count': len(accounts),
                'names': [acc.name for acc in accounts[:3]]
            }
        except Exception as e:
            results['tests']['storage_accounts'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # Test Synapse Workspaces access
        try:
            synapse_client = self.get_synapse_client()
            workspaces = list(synapse_client.workspaces.list())
            results['tests']['synapse_workspaces'] = {
                'status': 'success',
                'count': len(workspaces),
                'names': [ws.name for ws in workspaces[:3]]
            }
        except Exception as e:
            results['tests']['synapse_workspaces'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        return results

def test_authentication():
    """Test authentication and verify access"""
    print("=" * 60)
    print("AZURE AUTHENTICATION TEST")
    print("=" * 60)
    
    auth = AzureAuthenticator()
    
    if not auth.authenticate():
        print("Authentication failed - check credentials")
        return False
    
    print("\nVerifying access to Azure services...")
    results = auth.verify_access()
    
    print(f"\nTest Results ({results['timestamp']}):")
    print(f"Subscription: {results['subscription_id']}")
    
    for service, result in results['tests'].items():
        if result['status'] == 'success':
            print(f"✅ {service}: {result['count']} found")
            if 'names' in result and result['names']:
                print(f"   Examples: {', '.join(result['names'])}")
        else:
            print(f"❌ {service}: {result['error']}")
    
    return True

if __name__ == "__main__":
    test_authentication()