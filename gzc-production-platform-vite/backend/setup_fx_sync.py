#!/usr/bin/env python3
"""
Setup FX Forward Trades table in Azure PostgreSQL (synchronous version)
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
sys.path.append('/Users/mikaeleage/Projects Container/gzc-production-platform/backend')

from app.core.azure_keyvault import keyvault_client

def create_fx_schema():
    try:
        # Get real connection string from Azure Key Vault
        print('🔑 Getting database connection from Azure Key Vault...')
        db_secret = keyvault_client.get_secret('postgres-connection-string')
        
        if not db_secret:
            raise Exception('Failed to get database connection string from Key Vault')
        
        # Parse connection string for psycopg2
        # Format: postgresql+asyncpg://user:password@host:port/database?sslmode=require
        connection_url = db_secret.replace('postgresql+asyncpg://', 'postgresql://')
        
        print(f'🔗 Connecting to Azure PostgreSQL...')
        
        # Connect to database
        conn = psycopg2.connect(connection_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print('✅ Connected to Azure PostgreSQL')
        
        # Read SQL schema file
        with open('/Users/mikaeleage/Projects Container/gzc-production-platform/backend/create_fx_forward_schema.sql', 'r') as f:
            sql_content = f.read()
        
        # Execute schema creation
        print('📊 Creating FX forward trades table with industry standard schema...')
        cursor.execute(sql_content)
        conn.commit()
        
        print('✅ FX forward trades table created successfully')
        
        # Verify table creation
        cursor.execute('SELECT COUNT(*) FROM fx_forward_trades')
        count_result = cursor.fetchone()[0]
        print(f'📈 Table contains {count_result} sample FX forward trades')
        
        # Show sample data
        cursor.execute('SELECT id, currency_pair, notional_amount, unrealized_pnl, trade_status FROM fx_forward_trades LIMIT 3')
        sample_trades = cursor.fetchall()
        print('📋 Sample trades:')
        for trade in sample_trades:
            trade_id = trade['id']
            currency_pair = trade['currency_pair']
            notional = float(trade['notional_amount'])
            pnl = float(trade['unrealized_pnl'])
            status = trade['trade_status']
            print(f'  - {trade_id}: {currency_pair} {notional:,.0f} P&L: ${pnl:,.0f} Status: {status}')
        
        cursor.close()
        conn.close()
        print('🎉 Azure PostgreSQL FX forward trades table ready!')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_fx_schema()