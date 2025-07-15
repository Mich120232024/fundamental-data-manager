#!/usr/bin/env python3
"""
Setup FX Forward Trades table in Azure PostgreSQL
"""
import asyncio
import asyncpg
import sys
sys.path.append('/Users/mikaeleage/Projects Container/gzc-production-platform/backend')

from app.core.azure_keyvault import keyvault_client

async def create_fx_schema():
    try:
        # Get real connection string from Azure Key Vault
        print('🔑 Getting database connection from Azure Key Vault...')
        db_secret = keyvault_client.get_secret('postgres-connection-string')
        
        if not db_secret:
            raise Exception('Failed to get database connection string from Key Vault')
        
        # Parse connection string
        connection_url = db_secret.replace('postgresql+asyncpg://', '')
        
        if '@' in connection_url:
            auth_part, host_part = connection_url.split('@', 1)
            user_pass = auth_part.split(':', 1)
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ''
            
            host_db = host_part.split('/', 1)
            host_port = host_db[0]
            database = host_db[1] if len(host_db) > 1 else 'postgres'
            
            if ':' in host_port:
                host, port = host_port.split(':', 1)
                port = int(port)
            else:
                host = host_port
                port = 5432
        
        print(f'🔗 Connecting to Azure PostgreSQL: {host}:{port}/{database}')
        
        # Connect to database
        conn = await asyncpg.connect(
            host=host, port=port, user=user, password=password, database=database
        )
        
        print('✅ Connected to Azure PostgreSQL')
        
        # Read SQL schema file
        with open('/Users/mikaeleage/Projects Container/gzc-production-platform/backend/create_fx_forward_schema.sql', 'r') as f:
            sql_content = f.read()
        
        # Execute schema creation
        print('📊 Creating FX forward trades table with industry standard schema...')
        await conn.execute(sql_content)
        
        print('✅ FX forward trades table created successfully')
        
        # Verify table creation
        count_result = await conn.fetchval('SELECT COUNT(*) FROM fx_forward_trades')
        print(f'📈 Table contains {count_result} sample FX forward trades')
        
        # Show sample data
        sample_trades = await conn.fetch('SELECT id, currency_pair, notional_amount, unrealized_pnl, trade_status FROM fx_forward_trades LIMIT 3')
        print('📋 Sample trades:')
        for trade in sample_trades:
            trade_id = trade['id']
            currency_pair = trade['currency_pair']
            notional = float(trade['notional_amount'])
            pnl = float(trade['unrealized_pnl'])
            status = trade['trade_status']
            print(f'  - {trade_id}: {currency_pair} {notional:,.0f} P&L: ${pnl:,.0f} Status: {status}')
        
        await conn.close()
        print('🎉 Azure PostgreSQL FX forward trades table ready!')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_fx_schema())