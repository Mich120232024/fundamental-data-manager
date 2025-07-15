#!/usr/bin/env python3
"""
Simple test to verify Key Vault secrets
"""
import asyncio
from app.core.azure_keyvault import keyvault_client

async def main():
    print("🔍 Testing Azure Key Vault access...")
    
    # Test getting secrets
    db_secret = keyvault_client.get_secret("postgres-connection-string")
    redis_secret = keyvault_client.get_secret("redis-connection-string")
    
    if db_secret and redis_secret:
        print("✅ Key Vault secrets retrieved successfully!")
        print(f"   Database URL: {db_secret[:50]}...")
        print(f"   Redis URL: {redis_secret[:50]}...")
        return True
    else:
        print("❌ Failed to retrieve secrets from Key Vault")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    print(f"\n{'🎉 Success!' if success else '❌ Failed!'}")