#!/usr/bin/env python3
"""
Diagnose Azure Cosmos DB authentication issues
"""

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

import os
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load .env
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

endpoint = os.getenv('COSMOS_ENDPOINT')
key = os.getenv('COSMOS_KEY')

print("🔍 COSMOS DB AUTHENTICATION DIAGNOSTICS")
print("="*50)

print(f"Endpoint: {endpoint[:50]}..." if endpoint else "❌ No endpoint found")
print(f"Key: {'✓ Present' if key else '❌ Missing'}")
print(f"Key length: {len(key) if key else 0} characters")

if not endpoint or not key:
    print("\n❌ Missing credentials in .env file")
    exit(1)

# Test basic connectivity
print(f"\n🌐 Testing basic connectivity...")
try:
    # Just test if we can reach the endpoint
    response = requests.get(endpoint, timeout=10)
    print(f"✓ Can reach endpoint (status: {response.status_code})")
except Exception as e:
    print(f"❌ Cannot reach endpoint: {e}")

# Try to connect with Azure Cosmos client
print(f"\n🔑 Testing Cosmos DB authentication...")

try:
    from azure.cosmos import CosmosClient
    
    # Try with minimal permissions
    client = CosmosClient(endpoint, key)
    
    # Test database access
    try:
        database = client.get_database_client('research-analytics-db')
        print("✓ Database connection successful")
        
        # Test container access
        try:
            container = database.get_container_client('system_inbox')
            print("✓ Container access successful")
            
            # Test simple query
            try:
                count = container.query_items(
                    query="SELECT VALUE COUNT(1) FROM c",
                    enable_cross_partition_query=True,
                    max_item_count=1
                ).next()
                print(f"✓ Query successful - {count} messages found")
                
            except Exception as e:
                print(f"❌ Query failed: {e}")
                if "Request blocked by Auth" in str(e):
                    print("   🚫 AUTH BLOCK - Check IP allowlist in Azure Portal")
                elif "401" in str(e):
                    print("   🔑 Invalid credentials - Key may be wrong/expired")
                elif "403" in str(e):
                    print("   🚫 Forbidden - Check permissions")
                    
        except Exception as e:
            print(f"❌ Container access failed: {e}")
            
    except Exception as e:
        print(f"❌ Database access failed: {e}")
        
except Exception as e:
    print(f"❌ Client initialization failed: {e}")

print(f"\n🛠️  TROUBLESHOOTING STEPS:")
print("1. Check Azure Portal > Cosmos DB > Networking")
print("   - Ensure 'Allow access from Azure Portal' is enabled")
print("   - Add your current IP to allowlist if using IP filtering")
print("2. Check Azure Portal > Cosmos DB > Keys")
print("   - Verify primary/secondary key matches .env file")
print("3. Check Azure Portal > Cosmos DB > Access Control (IAM)")
print("   - Ensure proper permissions are assigned")
print("4. Try regenerating keys if needed (but update .env!)")

print(f"\n💡 If 'Request blocked by Auth' persists:")
print("   - This usually means IP filtering is blocking your location")
print("   - Go to Cosmos DB > Networking > Firewall and virtual networks")
print("   - Either disable firewall or add your current IP address")