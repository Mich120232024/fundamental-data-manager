#!/usr/bin/env python3
"""
Test async connection to Azure PostgreSQL
"""
import asyncio
import asyncpg
import sys
sys.path.append('/Users/mikaeleage/Projects Container/gzc-production-platform/backend')

from app.core.azure_keyvault import keyvault_client

async def test_connection():
    try:
        print("🔑 Getting Azure Key Vault credentials...")
        db_secret = keyvault_client.get_secret("postgres-connection-string")
        
        if not db_secret:
            raise Exception("No database connection string")
        
        print(f"🔗 Connection string: {db_secret[:50]}...")
        
        # Parse connection string
        connection_url = db_secret.replace("postgresql+asyncpg://", "")
        
        if "@" in connection_url:
            auth_part, rest = connection_url.split("@", 1)
            user_pass = auth_part.split(":", 1)
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            
            # Remove query parameters
            if "?" in rest:
                host_db, query = rest.split("?", 1)
            else:
                host_db = rest
            
            host_port, database = host_db.split("/", 1)
            
            if ":" in host_port:
                host, port = host_port.split(":", 1)
                port = int(port)
            else:
                host = host_port
                port = 5432
        
        print(f"📊 Connecting to: {host}:{port}/{database} as {user}")
        
        # Test connection
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            ssl='require'
        )
        
        print("✅ Connected successfully!")
        
        # Test query
        result = await conn.fetchval("SELECT version()")
        print(f"📈 PostgreSQL version: {result}")
        
        # Test if fx_forward_trades table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'fx_forward_trades'
            )
        """)
        
        print(f"📋 fx_forward_trades table exists: {table_exists}")
        
        await conn.close()
        print("🎉 Async connection test successful!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())