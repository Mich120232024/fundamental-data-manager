#!/usr/bin/env python3
"""
Azure Configuration - Environment-Based Security-Compliant Setup
NO HARDCODED CREDENTIALS OR RESOURCE NAMES
"""

import os
from typing import Dict, Optional

def get_azure_config() -> Dict[str, str]:
    """
    Get Azure configuration from environment variables - NO HARDCODED VALUES
    All resource names must be provided via environment or fail securely
    """
    
    # Required environment variables - NO DEFAULTS WITH REAL NAMES
    required_vars = {
        'AZURE_RESOURCE_GROUP': 'Primary resource group for Azure operations',
        'AZURE_SYNAPSE_WORKSPACE': 'Synapse Analytics workspace name',
        'AZURE_STORAGE_ACCOUNT': 'Primary storage account name',
        'AZURE_KEY_VAULT_NAME': 'Key Vault for secrets management',
    }
    
    # Check for missing required variables
    missing_vars = []
    for var_name, description in required_vars.items():
        if not os.getenv(var_name):
            missing_vars.append(f"{var_name}: {description}")
    
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables:\n" + 
            "\n".join(f"  - {var}" for var in missing_vars) +
            "\n\nSet these environment variables before running Azure operations."
        )
    
    # Build configuration from environment - SECURE APPROACH
    config = {
        "resource_group": os.getenv('AZURE_RESOURCE_GROUP'),
        "location": os.getenv('AZURE_LOCATION', 'East US'),
        "synapse_workspace": os.getenv('AZURE_SYNAPSE_WORKSPACE'),
        "storage_account": os.getenv('AZURE_STORAGE_ACCOUNT'),
        "key_vault": os.getenv('AZURE_KEY_VAULT_NAME'),
        
        # Optional resources with secure defaults
        "redis_cache": os.getenv('AZURE_REDIS_CACHE'),
        "database_name": os.getenv('AZURE_DATABASE_NAME'),
        
        # Build derived URLs from environment variables
        "synapse_endpoint": f"https://{os.getenv('AZURE_SYNAPSE_WORKSPACE')}.dev.azuresynapse.net" if os.getenv('AZURE_SYNAPSE_WORKSPACE') else None,
        "key_vault_url": f"https://{os.getenv('AZURE_KEY_VAULT_NAME')}.vault.azure.net/" if os.getenv('AZURE_KEY_VAULT_NAME') else None,
        "storage_account_url": f"https://{os.getenv('AZURE_STORAGE_ACCOUNT')}.blob.core.windows.net" if os.getenv('AZURE_STORAGE_ACCOUNT') else None,
        "data_lake_url": f"https://{os.getenv('AZURE_STORAGE_ACCOUNT')}.dfs.core.windows.net" if os.getenv('AZURE_STORAGE_ACCOUNT') else None,
    }
    
    # Build data lake paths from storage account environment variable
    if os.getenv('AZURE_STORAGE_ACCOUNT'):
        storage_account = os.getenv('AZURE_STORAGE_ACCOUNT')
        data_lake_root = f"abfss://data@{storage_account}.dfs.core.windows.net/"
        config["data_lake_root"] = data_lake_root
        config["storage_paths"] = {
            "raw_data": f"{data_lake_root}raw/",
            "processed_data": f"{data_lake_root}processed/",
            "delta_tables": f"{data_lake_root}delta/",
            "notebooks": f"{data_lake_root}notebooks/"
        }
    
    return config

def get_synapse_workspace() -> str:
    """Get Synapse workspace name from environment - SECURE"""
    workspace = os.getenv('AZURE_SYNAPSE_WORKSPACE')
    if not workspace:
        raise EnvironmentError("AZURE_SYNAPSE_WORKSPACE environment variable required")
    return workspace

def get_resource_group() -> str:
    """Get resource group name from environment - SECURE"""
    rg = os.getenv('AZURE_RESOURCE_GROUP')
    if not rg:
        raise EnvironmentError("AZURE_RESOURCE_GROUP environment variable required")
    return rg

def get_storage_account() -> str:
    """Get storage account name from environment - SECURE"""
    storage = os.getenv('AZURE_STORAGE_ACCOUNT')
    if not storage:
        raise EnvironmentError("AZURE_STORAGE_ACCOUNT environment variable required")
    return storage

def validate_configuration() -> Dict[str, bool]:
    """
    Validate Azure configuration without exposing values
    Returns validation status for each component
    """
    validation = {
        "resource_group": bool(os.getenv('AZURE_RESOURCE_GROUP')),
        "synapse_workspace": bool(os.getenv('AZURE_SYNAPSE_WORKSPACE')),
        "storage_account": bool(os.getenv('AZURE_STORAGE_ACCOUNT')),
        "key_vault": bool(os.getenv('AZURE_KEY_VAULT_NAME')),
        "subscription_id": bool(os.getenv('AZURE_SUBSCRIPTION_ID')),
    }
    
    validation["all_required"] = all([
        validation["resource_group"],
        validation["synapse_workspace"], 
        validation["storage_account"],
        validation["key_vault"]
    ])
    
    return validation

def get_environment_setup_guide() -> str:
    """
    Return setup guide for required environment variables
    NO REAL VALUES EXPOSED
    """
    return """
Azure Environment Setup Guide:

Required Environment Variables:
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_RESOURCE_GROUP="your-resource-group"
export AZURE_SYNAPSE_WORKSPACE="your-synapse-workspace"
export AZURE_STORAGE_ACCOUNT="your-storage-account"
export AZURE_KEY_VAULT_NAME="your-key-vault"

Optional Environment Variables:
export AZURE_LOCATION="East US"
export AZURE_REDIS_CACHE="your-redis-cache"
export AZURE_DATABASE_NAME="your-database"

Authentication (choose one):
1. Azure CLI: az login
2. Managed Identity: Automatic on Azure resources
3. Service Principal: Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID

Verification:
python -c "from azure_config import validate_configuration; print(validate_configuration())"
"""

if __name__ == "__main__":
    print("Azure Configuration Validation")
    print("=" * 40)
    
    try:
        validation = validate_configuration()
        print("Configuration Status:")
        for component, status in validation.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {component}")
        
        if validation["all_required"]:
            print("\n✅ All required configuration is set")
            config = get_azure_config()
            print(f"✅ Configuration loaded successfully")
        else:
            print("\n❌ Missing required environment variables")
            print("\nSetup Guide:")
            print(get_environment_setup_guide())
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\nSetup Guide:")
        print(get_environment_setup_guide())