#!/usr/bin/env python3
"""
Real Azure PostgreSQL FastAPI server for FX Forward Trades
"""
import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
import asyncpg
import uvicorn
import sys
sys.path.append('/Users/mikaeleage/Projects Container/gzc-production-platform/backend')

from app.core.azure_keyvault import keyvault_client

# Pydantic models for API responses
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

# Global database connection pool
db_pool = None

# Create FastAPI app
app = FastAPI(
    title="GZC Portfolio Real Azure PostgreSQL API",
    description="Real Azure PostgreSQL API for FX forward trades",
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

async def get_database_connection():
    """Get real Azure PostgreSQL connection"""
    global db_pool
    
    if db_pool is None:
        try:
            # Get real connection string from Azure Key Vault
            print("🔑 Getting database connection from Azure Key Vault...")
            db_secret = keyvault_client.get_secret("postgres-connection-string")
            
            if not db_secret:
                raise Exception("Failed to get database connection string from Key Vault")
            
            # Parse the connection string to get host, database, user, password
            # Format: postgresql+asyncpg://user:password@host:port/database
            connection_url = db_secret.replace("postgresql+asyncpg://", "")
            
            # Extract components
            if "@" in connection_url:
                auth_part, host_part = connection_url.split("@", 1)
                user_pass = auth_part.split(":", 1)
                user = user_pass[0]
                password = user_pass[1] if len(user_pass) > 1 else ""
                
                host_db = host_part.split("/", 1)
                host_port = host_db[0]
                database = host_db[1] if len(host_db) > 1 else "postgres"
                
                if ":" in host_port:
                    host, port = host_port.split(":", 1)
                    port = int(port)
                else:
                    host = host_port
                    port = 5432
            else:
                raise Exception("Invalid database connection string format")
            
            print(f"🔗 Connecting to Azure PostgreSQL: {host}:{port}/{database}")
            
            # Create connection pool with SSL and timeout settings
            db_pool = await asyncpg.create_pool(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                ssl='require',
                command_timeout=30,
                server_settings={'application_name': 'gzc_portfolio_api'},
                min_size=1,
                max_size=10
            )
            
            print("✅ Azure PostgreSQL connection pool created successfully!")
            
        except Exception as e:
            print(f"❌ Failed to connect to Azure PostgreSQL: {e}")
            raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
    
    return db_pool

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await get_database_connection()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    global db_pool
    if db_pool:
        await db_pool.close()

@app.get("/")
async def root():
    return {
        "message": "GZC Portfolio Real Azure PostgreSQL API",
        "version": "1.0.0",
        "status": "operational",
        "azure_connected": True,
        "database": "Azure PostgreSQL",
        "authentication": "Azure Key Vault"
    }

@app.get("/api/fx-forward-trades", response_model=List[FXForwardTradeResponse])
async def get_fx_forward_trades(
    status: Optional[str] = None,
    currency_pair: Optional[str] = None,
    trader: Optional[str] = None,
):
    """
    Get all FX forward trades from Azure PostgreSQL
    """
    try:
        pool = await get_database_connection()
        
        # Build SQL query with optional filters
        base_query = """
        SELECT 
            id, trade_date, value_date, currency_pair, notional, 
            rate, market_rate, pnl, counterparty, status, trader,
            created_at, updated_at
        FROM fx_forward_trades 
        WHERE 1=1
        """
        
        params = []
        param_count = 1
        
        if status:
            base_query += f" AND status = ${param_count}"
            params.append(status)
            param_count += 1
            
        if currency_pair:
            base_query += f" AND currency_pair = ${param_count}"
            params.append(currency_pair)
            param_count += 1
            
        if trader:
            base_query += f" AND trader ILIKE ${param_count}"
            params.append(f"%{trader}%")
            param_count += 1
        
        base_query += " ORDER BY trade_date DESC"
        
        async with pool.acquire() as connection:
            print(f"🔍 Executing query: {base_query}")
            print(f"📊 Parameters: {params}")
            
            rows = await connection.fetch(base_query, *params)
            
            print(f"✅ Found {len(rows)} FX forward trades in Azure PostgreSQL")
            
            # Convert rows to response format
            trades = []
            for row in rows:
                trade = {
                    "id": row["id"],
                    "trade_date": row["trade_date"].isoformat() if row["trade_date"] else "",
                    "value_date": row["value_date"].isoformat() if row["value_date"] else "",
                    "currency_pair": row["currency_pair"],
                    "notional": float(row["notional"]) if row["notional"] else 0.0,
                    "rate": float(row["rate"]) if row["rate"] else 0.0,
                    "market_rate": float(row["market_rate"]) if row["market_rate"] else 0.0,
                    "pnl": float(row["pnl"]) if row["pnl"] else 0.0,
                    "counterparty": row["counterparty"] or "",
                    "status": row["status"] or "",
                    "trader": row["trader"] or "",
                    "created_at": row["created_at"].isoformat() if row["created_at"] else "",
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else ""
                }
                trades.append(trade)
            
            return trades
        
    except Exception as e:
        print(f"❌ Error fetching FX forward trades: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching FX forward trades: {str(e)}")

@app.get("/api/fx-forward-trades/{trade_id}", response_model=FXForwardTradeResponse)
async def get_fx_forward_trade(trade_id: str):
    """
    Get a specific FX forward trade by ID from Azure PostgreSQL
    """
    try:
        pool = await get_database_connection()
        
        query = """
        SELECT 
            id, trade_date, value_date, currency_pair, notional, 
            rate, market_rate, pnl, counterparty, status, trader,
            created_at, updated_at
        FROM fx_forward_trades 
        WHERE id = $1
        """
        
        async with pool.acquire() as connection:
            row = await connection.fetchrow(query, trade_id)
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
            
            trade = {
                "id": row["id"],
                "trade_date": row["trade_date"].isoformat() if row["trade_date"] else "",
                "value_date": row["value_date"].isoformat() if row["value_date"] else "",
                "currency_pair": row["currency_pair"],
                "notional": float(row["notional"]) if row["notional"] else 0.0,
                "rate": float(row["rate"]) if row["rate"] else 0.0,
                "market_rate": float(row["market_rate"]) if row["market_rate"] else 0.0,
                "pnl": float(row["pnl"]) if row["pnl"] else 0.0,
                "counterparty": row["counterparty"] or "",
                "status": row["status"] or "",
                "trader": row["trader"] or "",
                "created_at": row["created_at"].isoformat() if row["created_at"] else "",
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else ""
            }
            
            return trade
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching trade {trade_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching trade: {str(e)}")

@app.get("/api/fx-forward-trades/summary/stats")
async def get_fx_forward_trades_summary():
    """
    Get summary statistics for FX forward trades from Azure PostgreSQL
    """
    try:
        pool = await get_database_connection()
        
        query = """
        SELECT 
            COUNT(*) as total_trades,
            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_trades,
            COALESCE(SUM(notional), 0) as total_notional,
            COALESCE(SUM(pnl), 0) as total_pnl,
            array_agg(DISTINCT currency_pair) as currency_pairs,
            array_agg(DISTINCT counterparty) as counterparties
        FROM fx_forward_trades
        """
        
        async with pool.acquire() as connection:
            row = await connection.fetchrow(query)
            
            return {
                "total_trades": row["total_trades"],
                "active_trades": row["active_trades"],
                "total_notional": float(row["total_notional"]),
                "total_pnl": float(row["total_pnl"]),
                "currency_pairs": [cp for cp in row["currency_pairs"] if cp],
                "counterparties": [cp for cp in row["counterparties"] if cp],
                "last_updated": datetime.now().isoformat(),
                "data_source": "Azure PostgreSQL",
                "authentication": "Azure Key Vault"
            }
        
    except Exception as e:
        print(f"❌ Error calculating summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating summary: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check with real Azure connections
    """
    try:
        pool = await get_database_connection()
        
        # Test database connection
        async with pool.acquire() as connection:
            await connection.fetchval("SELECT 1")
        
        return {
            "status": "healthy",
            "azure_keyvault": "connected",
            "postgresql": "connected",
            "data_source": "Azure PostgreSQL",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("🚀 Starting Real Azure PostgreSQL API on http://localhost:8002")
    print("🔑 Using Azure Key Vault for authentication")
    print("🗄️ Connecting to Azure PostgreSQL database")
    uvicorn.run(app, host="0.0.0.0", port=8002)