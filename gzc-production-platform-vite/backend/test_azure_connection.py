#!/usr/bin/env python3
"""
Test Azure PostgreSQL and Redis connections
"""
import asyncio
import asyncpg
import redis
import sys
import getpass
import os

async def test_postgres_connection():
    """Test Azure PostgreSQL connection"""
    print("🔍 Testing Azure PostgreSQL connection...")
    
    # Get password from user
    password = getpass.getpass("Enter PostgreSQL password for user 'mikael': ")
    
    connection_string = f"postgresql://mikael:{password}@gzcdevserver.postgres.database.azure.com:5432/gzc_platform?sslmode=require"
    
    try:
        conn = await asyncpg.connect(connection_string)
        
        # Test query
        result = await conn.fetchval('SELECT version()')
        print(f"✅ PostgreSQL connected successfully!")
        print(f"   Version: {result}")
        
        # Test database access
        await conn.execute('SELECT 1')
        print(f"✅ Database 'gzc_platform' accessible")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_redis_connection():
    """Test Azure Redis connection"""
    print("\n🔍 Testing Azure Redis connection...")
    
    try:
        # Get Redis password from environment or prompt user
        redis_password = os.getenv('AZURE_REDIS_PASSWORD')
        if not redis_password:
            redis_password = getpass.getpass("Enter Azure Redis password: ")
        
        # Connect to Azure Redis
        r = redis.Redis(
            host='GZCRedis.redis.cache.windows.net',
            port=6380,
            password=redis_password,
            ssl=True,
            decode_responses=True
        )
        
        # Test ping
        result = r.ping()
        print(f"✅ Redis connected successfully!")
        print(f"   Ping response: {result}")
        
        # Test set/get
        r.set('test_key', 'test_value', ex=30)
        value = r.get('test_key')
        print(f"✅ Redis read/write test successful: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

async def main():
    """Test both Azure services"""
    print("🚀 Testing Azure connections for GZC Platform...\n")
    
    postgres_ok = await test_postgres_connection()
    redis_ok = test_redis_connection()
    
    print(f"\n📊 Connection Test Results:")
    print(f"   PostgreSQL: {'✅ Success' if postgres_ok else '❌ Failed'}")
    print(f"   Redis:      {'✅ Success' if redis_ok else '❌ Failed'}")
    
    if postgres_ok and redis_ok:
        print(f"\n🎉 All Azure services connected successfully!")
        print(f"   Ready to start the FastAPI backend with Azure integration!")
        return True
    else:
        print(f"\n⚠️  Some connections failed. Please check credentials and network access.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)