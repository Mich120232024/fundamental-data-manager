#!/usr/bin/env python3
"""
Simple Async FastAPI server that creates FX table if it doesn't exist
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import uvicorn
import asyncpg
import sys
sys.path.append('/Users/mikaeleage/Projects Container/gzc-production-platform/backend')

from app.core.azure_keyvault import keyvault_client

# Pydantic models
class FXForwardTradeResponse(BaseModel):
    id: str
    trade_date: str
    value_date: str
    currency_pair: str
    notional: float
    rate: float
    market_rate: float
    pnl: float
    counterparty: str
    status: str
    trader: str
    created_at: str
    updated_at: str

# Global connection pool
db_pool = None

# Create FastAPI app
app = FastAPI(
    title="GZC Portfolio Async Azure API",
    description="Real async Azure PostgreSQL API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3200", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_db_connection_params():
    """Get database connection parameters from Azure Key Vault"""
    try:
        db_secret = keyvault_client.get_secret("postgres-connection-string")
        if not db_secret:
            raise Exception("No database connection string found")
        
        # Parse connection string
        # postgresql+asyncpg://user:password@host:port/database?sslmode=require
        connection_url = db_secret.replace("postgresql+asyncpg://", "")
        
        if "@" in connection_url:
            auth_part, rest = connection_url.split("@", 1)
            user_pass = auth_part.split(":", 1)
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            
            # Remove query parameters for parsing
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
        
        return {
            'host': host,
            'port': port, 
            'user': user,
            'password': password,
            'database': database
        }
    except Exception as e:
        print(f"❌ Error parsing connection: {e}")
        raise

async def init_database():
    """Initialize database connection and create table if needed"""
    global db_pool
    
    try:
        # Get connection parameters
        conn_params = await get_db_connection_params()
        print(f"🔗 Connecting to {conn_params['host']}:{conn_params['port']}/{conn_params['database']}")
        
        # Create connection pool
        db_pool = await asyncpg.create_pool(
            host=conn_params['host'],
            port=conn_params['port'],
            user=conn_params['user'],
            password=conn_params['password'],
            database=conn_params['database'],
            ssl='require',
            min_size=1,
            max_size=5,
            command_timeout=60
        )
        
        print("✅ Connected to Azure PostgreSQL")
        
        # Create table if it doesn't exist
        async with db_pool.acquire() as conn:
            # Check if table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'fx_forward_trades'
                )
            """)
            
            if not table_exists:
                print("📊 Creating fx_forward_trades table...")
                
                # Create minimal table for demo
                await conn.execute("""
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
                    )
                """)
                
                # Insert sample data
                await conn.execute("""
                    INSERT INTO fx_forward_trades (
                        id, trade_date, value_date, currency_pair, notional, rate, market_rate, pnl,
                        counterparty, status, trader
                    ) VALUES 
                    ('FWD001', '2025-07-01', '2025-09-01', 'EUR/USD', 10000000, 1.0950, 1.0987, 37000, 'Goldman Sachs', 'ACTIVE', 'John Smith'),
                    ('FWD002', '2025-06-28', '2025-08-28', 'GBP/USD', 5000000, 1.2750, 1.2723, -13500, 'JP Morgan', 'ACTIVE', 'Sarah Johnson'),
                    ('FWD003', '2025-06-25', '2025-12-25', 'USD/JPY', 8000000, 158.50, 159.25, 37841, 'Deutsche Bank', 'ACTIVE', 'Mike Chen'),
                    ('FWD004', '2025-06-20', '2025-07-20', 'AUD/USD', 3000000, 0.6850, 0.6835, -4500, 'UBS', 'SETTLED', 'David Wilson'),
                    ('FWD005', '2025-06-15', '2025-09-15', 'USD/CHF', 6000000, 0.8720, 0.8735, 10338, 'Credit Suisse', 'ACTIVE', 'Anna Rodriguez')
                """)
                
                print("✅ Sample FX forward trades inserted")
            else:
                print("✅ fx_forward_trades table already exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    success = await init_database()
    if not success:
        print("⚠️ Starting with limited functionality - database not available")

@app.on_event("shutdown") 
async def shutdown():
    """Close connections on shutdown"""
    global db_pool
    if db_pool:
        await db_pool.close()

@app.get("/")
async def root():
    return {
        "message": "GZC Portfolio Async Azure API",
        "version": "1.0.0",
        "status": "operational",
        "database": "Azure PostgreSQL" if db_pool else "disconnected",
        "async": True
    }

@app.get("/api/fx-forward-trades", response_model=List[FXForwardTradeResponse])
async def get_fx_forward_trades(
    status: Optional[str] = None,
    currency_pair: Optional[str] = None,
    trader: Optional[str] = None,
):
    """Get FX forward trades from Azure PostgreSQL"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Build query
        base_query = """
            SELECT id, trade_date, value_date, currency_pair, notional, rate, market_rate, pnl,
                   counterparty, status, trader, created_at, updated_at
            FROM fx_forward_trades 
            WHERE 1=1
        """
        
        params = []
        if status:
            base_query += f" AND status = ${len(params) + 1}"
            params.append(status)
        if currency_pair:
            base_query += f" AND currency_pair = ${len(params) + 1}"
            params.append(currency_pair)
        if trader:
            base_query += f" AND trader ILIKE ${len(params) + 1}"
            params.append(f"%{trader}%")
        
        base_query += " ORDER BY trade_date DESC"
        
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(base_query, *params)
            
            trades = []
            for row in rows:
                trade = {
                    "id": row["id"],
                    "trade_date": row["trade_date"].isoformat(),
                    "value_date": row["value_date"].isoformat(),
                    "currency_pair": row["currency_pair"],
                    "notional": float(row["notional"]),
                    "rate": float(row["rate"]),
                    "market_rate": float(row["market_rate"]),
                    "pnl": float(row["pnl"]),
                    "counterparty": row["counterparty"],
                    "status": row["status"],
                    "trader": row["trader"],
                    "created_at": row["created_at"].isoformat(),
                    "updated_at": row["updated_at"].isoformat()
                }
                trades.append(trade)
            
            print(f"✅ Returned {len(trades)} FX forward trades from Azure PostgreSQL")
            return trades
            
    except Exception as e:
        print(f"❌ Error fetching trades: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/health")
async def health():
    """Health check with actual database test"""
    try:
        if not db_pool:
            return {"status": "unhealthy", "database": "disconnected"}
        
        async with db_pool.acquire() as conn:
            result = await conn.fetchval("SELECT COUNT(*) FROM fx_forward_trades")
            
        return {
            "status": "healthy",
            "database": "Azure PostgreSQL connected",
            "trades_count": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("🚀 Starting Async Azure PostgreSQL API on http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)