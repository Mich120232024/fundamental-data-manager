#!/usr/bin/env python3
"""
Check Azure Key Vault for Redis connection
"""
import sys
sys.path.append('/Users/mikaeleage/Projects Container/gzc-production-platform/backend')

from app.core.azure_keyvault import keyvault_client


def check_azure_redis():
    """Check Azure Key Vault for Redis connection"""
    print("🔑 Checking Azure Key Vault for Redis configuration...")
    
    # Check for Redis-related secrets
    redis_secrets = [
        'redis-connection-string',
        'redis-url',
        'redis-host',
        'redis-password',
        'cache-connection-string',
        'azure-cache-redis'
    ]
    
    found_secrets = []
    
    for secret_name in redis_secrets:
        try:
            value = keyvault_client.get_secret(secret_name)
            if value:
                found_secrets.append(secret_name)
                # Don't print full connection strings for security
                if 'connection-string' in secret_name or 'password' in secret_name:
                    print(f"✅ Found secret: {secret_name} (hidden for security)")
                else:
                    print(f"✅ Found secret: {secret_name} = {value[:50]}...")
        except Exception as e:
            if "not found" not in str(e).lower():
                print(f"⚠️  Error checking {secret_name}: {e}")
    
    if not found_secrets:
        print("\n❌ No Redis secrets found in Key Vault")
        print("\n📝 Available options:")
        print("1. Install Redis locally: brew install redis")
        print("2. Use Azure Cache for Redis")
        print("3. Run Redis in Docker")
    else:
        print(f"\n✅ Found {len(found_secrets)} Redis-related secrets")
        
    # List all secrets to see what's available
    print("\n📋 All available secrets in Key Vault:")
    try:
        secrets = keyvault_client.list_secrets()
        for secret in secrets[:20]:  # Show first 20
            print(f"  - {secret}")
    except Exception as e:
        print(f"❌ Error listing secrets: {e}")


if __name__ == "__main__":
    check_azure_redis()