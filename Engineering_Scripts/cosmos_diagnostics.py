#!/usr/bin/env python3
"""
Cosmos DB Connection Diagnostics and Testing Script
Diagnoses environment issues and tests Cosmos DB connectivity
"""

import os
import sys
import json
import warnings
import ssl
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Suppress the NotOpenSSLWarning
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def check_environment():
    """Check Python environment and dependencies"""
    print_section("ENVIRONMENT CHECK")
    
    # Python version
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    
    # Platform info
    print(f"\nPlatform: {platform.platform()}")
    print(f"System: {platform.system()}")
    print(f"Machine: {platform.machine()}")
    
    # SSL version
    print(f"\nSSL Version: {ssl.OPENSSL_VERSION}")
    
    # Check for required packages
    required_packages = ['azure.cosmos', 'dotenv']
    missing_packages = []
    
    print("\nChecking required packages:")
    for package in required_packages:
        try:
            if package == 'dotenv':
                import dotenv
                print(f"✓ python-dotenv: {dotenv.__version__ if hasattr(dotenv, '__version__') else 'installed'}")
            else:
                __import__(package)
                print(f"✓ {package}: installed")
        except ImportError:
            print(f"✗ {package}: NOT INSTALLED")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_env_vars():
    """Check if required environment variables are set"""
    print_section("ENVIRONMENT VARIABLES CHECK")
    
    # Try to load .env file
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"✓ Loaded .env file from: {env_path}")
        else:
            print(f"ℹ No .env file found at: {env_path}")
    except Exception as e:
        print(f"⚠ Error loading .env file: {e}")
    
    required_vars = [
        'COSMOS_ENDPOINT',
        'COSMOS_KEY',
        'COSMOS_DATABASE_NAME',
        'COSMOS_CONTAINER_NAME'
    ]
    
    missing_vars = []
    found_vars = {}
    
    print("\nChecking Cosmos DB environment variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive information
            if 'KEY' in var:
                masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            elif 'ENDPOINT' in var:
                masked_value = value.replace('.documents.azure.com', '.***.azure.com')
            else:
                masked_value = value
            print(f"✓ {var}: {masked_value}")
            found_vars[var] = value
        else:
            print(f"✗ {var}: NOT SET")
            missing_vars.append(var)
    
    return len(missing_vars) == 0, found_vars

def test_cosmos_connection(config: Dict[str, str]) -> Tuple[bool, Optional[str]]:
    """Test Cosmos DB connection with detailed error handling"""
    print_section("COSMOS DB CONNECTION TEST")
    
    try:
        from azure.cosmos import CosmosClient
        from azure.cosmos.exceptions import CosmosHttpResponseError
    except ImportError:
        return False, "azure-cosmos package not installed"
    
    # Validate configuration
    if not all(key in config for key in ['COSMOS_ENDPOINT', 'COSMOS_KEY']):
        return False, "Missing required configuration (endpoint or key)"
    
    # Special handling for endpoint format
    endpoint = config['COSMOS_ENDPOINT']
    if not endpoint.startswith('https://'):
        print(f"⚠ Endpoint doesn't start with https://. Current value: {endpoint}")
        print("  Attempting to fix...")
        endpoint = f"https://{endpoint}"
        print(f"  Using: {endpoint}")
    
    if not endpoint.endswith('.documents.azure.com'):
        print(f"⚠ Endpoint doesn't end with .documents.azure.com")
        print("  This might cause connection issues")
    
    try:
        print(f"\nConnecting to Cosmos DB...")
        print(f"Endpoint: {endpoint.replace('.documents.azure.com', '.***.azure.com')}")
        
        # Create client with explicit SSL settings
        client = CosmosClient(
            endpoint,
            credential=config['COSMOS_KEY'],
            connection_verify=True  # Ensure SSL verification is enabled
        )
        
        # Test connection by listing databases
        print("\nTesting connection by listing databases...")
        databases = list(client.list_databases())
        print(f"✓ Successfully connected! Found {len(databases)} database(s)")
        
        for db in databases[:3]:  # Show first 3 databases
            print(f"  - {db['id']}")
        
        return True, None
        
    except CosmosHttpResponseError as e:
        error_msg = f"Cosmos HTTP Error: {e.status_code} - {e.message}"
        print(f"\n✗ {error_msg}")
        
        # Provide specific guidance based on error
        if e.status_code == 401:
            print("\n⚠ Authentication failed. Please check:")
            print("  1. Your Cosmos DB key is correct")
            print("  2. The key hasn't been regenerated")
            print("  3. You're using the correct endpoint")
        elif e.status_code == 403:
            print("\n⚠ Access forbidden. Please check:")
            print("  1. Your account has access to this Cosmos DB")
            print("  2. Firewall rules allow your IP")
        elif "One of the input values is invalid" in str(e):
            print("\n⚠ Invalid input error. This often means:")
            print("  1. The endpoint format is incorrect")
            print("  2. The endpoint should be: https://<account-name>.documents.azure.com")
            print("  3. Check for extra spaces or special characters")
        
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error: {type(e).__name__} - {str(e)}"
        print(f"\n✗ {error_msg}")
        return False, error_msg

def query_messages(config: Dict[str, str]):
    """Query for recent messages to/from HEAD_OF_ENGINEERING"""
    print_section("QUERYING RECENT MESSAGES")
    
    if not all(key in config for key in ['COSMOS_DATABASE_NAME', 'COSMOS_CONTAINER_NAME']):
        print("✗ Missing database or container name in configuration")
        return
    
    try:
        from azure.cosmos import CosmosClient
        
        # Fix endpoint if needed
        endpoint = config['COSMOS_ENDPOINT']
        if not endpoint.startswith('https://'):
            endpoint = f"https://{endpoint}"
        
        client = CosmosClient(endpoint, credential=config['COSMOS_KEY'])
        database = client.get_database_client(config['COSMOS_DATABASE_NAME'])
        container = database.get_container_client(config['COSMOS_CONTAINER_NAME'])
        
        print(f"\nDatabase: {config['COSMOS_DATABASE_NAME']}")
        print(f"Container: {config['COSMOS_CONTAINER_NAME']}")
        
        # Query for messages involving HEAD_OF_ENGINEERING from last 7 days
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        
        query = """
        SELECT TOP 10 c.id, c.sender, c.recipient, c.subject, c.timestamp, c.priority
        FROM c
        WHERE (c.sender = 'HEAD_OF_ENGINEERING' OR c.recipient = 'HEAD_OF_ENGINEERING')
        AND c.timestamp > @cutoff_date
        ORDER BY c.timestamp DESC
        """
        
        print(f"\nQuerying messages from last 7 days...")
        
        results = list(container.query_items(
            query=query,
            parameters=[{"name": "@cutoff_date", "value": seven_days_ago}],
            enable_cross_partition_query=True
        ))
        
        if results:
            print(f"\n✓ Found {len(results)} recent message(s):")
            for msg in results:
                print(f"\n  Message ID: {msg.get('id', 'N/A')}")
                print(f"  From: {msg.get('sender', 'N/A')} → To: {msg.get('recipient', 'N/A')}")
                print(f"  Subject: {msg.get('subject', 'N/A')}")
                print(f"  Priority: {msg.get('priority', 'N/A')}")
                print(f"  Timestamp: {msg.get('timestamp', 'N/A')}")
        else:
            print("\nℹ No messages found for HEAD_OF_ENGINEERING in the last 7 days")
            
            # Try a simpler query to verify container access
            print("\nTrying to count total messages in container...")
            count_query = "SELECT VALUE COUNT(1) FROM c"
            count_result = list(container.query_items(
                query=count_query,
                enable_cross_partition_query=True
            ))
            if count_result:
                print(f"✓ Total messages in container: {count_result[0]}")
            
    except Exception as e:
        print(f"\n✗ Error querying messages: {type(e).__name__} - {str(e)}")

def provide_recommendations(env_ok: bool, vars_ok: bool, conn_ok: bool, conn_error: Optional[str]):
    """Provide actionable recommendations based on diagnostics"""
    print_section("RECOMMENDATIONS")
    
    if env_ok and vars_ok and conn_ok:
        print("\n✅ Everything is working correctly!")
        print("\nTo suppress the SSL warning in your scripts, add this at the top:")
        print("import warnings")
        print("warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')")
        return
    
    print("\n⚠ Issues detected. Here's how to fix them:")
    
    if not env_ok:
        print("\n1. Install missing packages:")
        print("   pip3 install azure-cosmos python-dotenv")
    
    if not vars_ok:
        print("\n2. Set up environment variables:")
        print("   Create a .env file in your script directory with:")
        print("   COSMOS_ENDPOINT=https://<your-account>.documents.azure.com")
        print("   COSMOS_KEY=<your-primary-or-secondary-key>")
        print("   COSMOS_DATABASE_NAME=<your-database-name>")
        print("   COSMOS_CONTAINER_NAME=<your-container-name>")
    
    if not conn_ok and conn_error:
        print("\n3. Fix connection issues:")
        if "One of the input values is invalid" in conn_error:
            print("   - Ensure COSMOS_ENDPOINT is in format: https://<account>.documents.azure.com")
            print("   - Remove any trailing slashes or spaces")
            print("   - Don't include port numbers or paths")
        elif "401" in conn_error:
            print("   - Verify your Cosmos DB key is correct")
            print("   - Try regenerating the key in Azure Portal")
        else:
            print(f"   - Error: {conn_error}")

def main():
    """Main diagnostic flow"""
    print("\n🔍 COSMOS DB DIAGNOSTIC TOOL")
    print("This tool will help diagnose and fix your Cosmos DB connection issues")
    
    # Check environment
    env_ok = check_environment()
    
    # Check environment variables
    vars_ok, config = check_env_vars()
    
    # Test Cosmos connection if we have config
    conn_ok = False
    conn_error = None
    if vars_ok:
        conn_ok, conn_error = test_cosmos_connection(config)
        
        # Try querying if connection successful
        if conn_ok:
            query_messages(config)
    
    # Provide recommendations
    provide_recommendations(env_ok, vars_ok, conn_ok, conn_error)
    
    print("\n" + "="*60)
    print("\n✨ Diagnostic complete!")

if __name__ == "__main__":
    main()