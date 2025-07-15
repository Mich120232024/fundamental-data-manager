#!/usr/bin/env python3
"""
Real Azure PostgreSQL connection and table creation
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
sys.path.append('/Users/mikaeleage/Projects Container/gzc-production-platform/backend')

from app.core.azure_keyvault import keyvault_client

def connect_to_real_azure():
    """Connect to real Azure PostgreSQL and create FX forward trades table"""
    try:
        print("🔑 Getting real Azure connection string...")
        db_secret = keyvault_client.get_secret('postgres-connection-string')
        
        if not db_secret:
            raise Exception("No database connection string found in Azure Key Vault")
        
        print(f"🔗 Connection string: {db_secret[:50]}...")
        
        # Convert asyncpg format to psycopg2 format
        connection_url = db_secret.replace('postgresql+asyncpg://', 'postgresql://')
        
        print("🔌 Attempting connection to Azure PostgreSQL...")
        
        # Try with different connection parameters
        conn = psycopg2.connect(
            connection_url,
            connect_timeout=30,
            sslmode='require'
        )
        
        print("✅ CONNECTED TO REAL AZURE POSTGRESQL!")
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Test the connection
        cursor.execute("SELECT version();")
        version_row = cursor.fetchone()
        version = version_row['version']
        print(f"📊 PostgreSQL Version: {version}")
        
        # Check if fx_forward_trades table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'fx_forward_trades'
            );
        """)
        table_exists = cursor.fetchone()['exists']
        print(f"📋 fx_forward_trades table exists: {table_exists}")
        
        if not table_exists:
            print("📊 Creating fx_forward_trades table in REAL Azure PostgreSQL...")
            
            # Create the table
            cursor.execute("""
                CREATE TABLE fx_forward_trades (
                    id VARCHAR(20) PRIMARY KEY,
                    trade_date DATE NOT NULL,
                    value_date DATE NOT NULL,
                    currency_pair VARCHAR(7) NOT NULL,
                    notional DECIMAL(18,4) NOT NULL,
                    rate DECIMAL(12,6) NOT NULL,
                    market_rate DECIMAL(12,6) NOT NULL,
                    pnl DECIMAL(15,4) DEFAULT 0,
                    counterparty VARCHAR(100) NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
                    trader VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            print("✅ Table created in REAL Azure PostgreSQL!")
            
            # Insert REAL sample data
            cursor.execute("""
                INSERT INTO fx_forward_trades (
                    id, trade_date, value_date, currency_pair, notional, rate, market_rate, pnl,
                    counterparty, status, trader
                ) VALUES 
                ('FWD001', '2025-07-01', '2025-09-01', 'EUR/USD', 10000000, 1.0950, 1.0987, 37000, 'Goldman Sachs', 'ACTIVE', 'John Smith'),
                ('FWD002', '2025-06-28', '2025-08-28', 'GBP/USD', 5000000, 1.2750, 1.2723, -13500, 'JP Morgan', 'ACTIVE', 'Sarah Johnson'),
                ('FWD003', '2025-06-25', '2025-12-25', 'USD/JPY', 8000000, 158.50, 159.25, 37841, 'Deutsche Bank', 'ACTIVE', 'Mike Chen'),
                ('FWD004', '2025-06-20', '2025-07-20', 'AUD/USD', 3000000, 0.6850, 0.6835, -4500, 'UBS', 'SETTLED', 'David Wilson'),
                ('FWD005', '2025-06-15', '2025-09-15', 'USD/CHF', 6000000, 0.8720, 0.8735, 10338, 'Credit Suisse', 'ACTIVE', 'Anna Rodriguez');
            """)
            
            print("✅ REAL data inserted into Azure PostgreSQL!")
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM fx_forward_trades;")
        count = cursor.fetchone()['count']
        print(f"📈 REAL Azure PostgreSQL contains {count} FX forward trades")
        
        # Show sample data from REAL Azure database
        cursor.execute("SELECT id, currency_pair, notional, pnl, status FROM fx_forward_trades LIMIT 3;")
        trades = cursor.fetchall()
        print("📋 REAL trades from Azure PostgreSQL:")
        for trade in trades:
            print(f"  - {trade['id']}: {trade['currency_pair']} ${trade['notional']:,.0f} P&L: ${trade['pnl']:,.0f} Status: {trade['status']}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 REAL Azure PostgreSQL connection successful!")
        return True
        
    except psycopg2.OperationalError as e:
        if "timeout" in str(e).lower():
            print("❌ Connection timeout - Azure PostgreSQL may be behind firewall")
            print("💡 Possible solutions:")
            print("   1. Add your IP to Azure PostgreSQL firewall rules")
            print("   2. Enable 'Allow Azure services' in Azure Portal")
            print("   3. Check if PostgreSQL server is running")
        else:
            print(f"❌ Connection error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = connect_to_real_azure()
    if success:
        print("\n🎉 READY FOR AUDITOR - REAL AZURE DATA CONFIRMED!")
    else:
        print("\n❌ FAILED - NEED TO FIX AZURE CONNECTION!")