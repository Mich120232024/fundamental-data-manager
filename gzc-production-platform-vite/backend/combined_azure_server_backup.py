#!/usr/bin/env python3
"""
Combined Azure Server - PostgreSQL + Redis FX Prices
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import uvicorn
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import json
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

# Global connections
db_connection_string = None
redis_client = None

def get_azure_connection():
    """Get REAL Azure PostgreSQL connection"""
    global db_connection_string
    
    if not db_connection_string:
        try:
            print("🔑 Getting REAL Azure connection from Key Vault...")
            db_secret = keyvault_client.get_secret('postgres-connection-string')
            if not db_secret:
                raise Exception("No Azure database connection string found")
            
            # Convert to psycopg2 format
            db_connection_string = db_secret.replace('postgresql+asyncpg://', 'postgresql://')
            print("✅ Azure Key Vault connection string retrieved")
        except Exception as e:
            print(f"❌ Failed to get Azure connection: {e}")
            raise HTTPException(status_code=503, detail="Azure Key Vault connection failed")
    
    try:
        conn = psycopg2.connect(
            db_connection_string,
            connect_timeout=30,
            sslmode='require'
        )
        return conn
    except Exception as e:
        print(f"❌ Azure PostgreSQL connection failed: {e}")
        raise HTTPException(status_code=503, detail="Azure PostgreSQL connection failed")

def get_redis_client():
    """Get Azure Redis client"""
    global redis_client
    
    if redis_client is None:
        try:
            # Get Redis connection from Key Vault
            redis_secret = keyvault_client.get_secret('redis-connection-string')
            if not redis_secret:
                raise Exception("No Redis connection string found")
            
            # Parse Redis URL
            from urllib.parse import urlparse
            parsed = urlparse(redis_secret)
            
            redis_client = redis.Redis(
                host=parsed.hostname,
                port=parsed.port or 6380,
                password=parsed.password,
                ssl=True,
                ssl_cert_reqs=None,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            redis_client.ping()
            print("✅ Connected to Azure Redis for FX prices")
            
        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            raise HTTPException(status_code=503, detail="Redis connection failed")
    
    return redis_client

# Create FastAPI app
app = FastAPI(
    title="Azure Trading Platform API",
    description="Real Azure PostgreSQL & Redis - NO MOCK DATA",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Azure Trading Platform API",
        "version": "1.0.0",
        "status": "operational",
        "postgres": "Azure PostgreSQL",
        "redis": "Azure Redis Cache",
        "mock_data": False
    }

@app.get("/api/fx-forward-trades", response_model=List[FXForwardTradeResponse])
async def get_fx_forward_trades(
    status: Optional[str] = None,
    currency_pair: Optional[str] = None,
    trader: Optional[str] = None,
):
    """Get FX forward trades from REAL Azure PostgreSQL database"""
    try:
        conn = get_azure_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build SQL query
        base_query = """
            SELECT id, trade_date, value_date, currency_pair, notional, rate, market_rate, pnl,
                   counterparty, status, trader, created_at, updated_at
            FROM fx_forward_trades 
            WHERE 1=1
        """
        
        params = []
        if status:
            base_query += " AND status = %s"
            params.append(status)
        if currency_pair:
            base_query += " AND currency_pair = %s"
            params.append(currency_pair)
        if trader:
            base_query += " AND trader ILIKE %s"
            params.append(f"%{trader}%")
        
        base_query += " ORDER BY trade_date DESC"
        
        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        
        # Convert to response format
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
        
        cursor.close()
        conn.close()
        
        return trades
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/fx-prices")
async def get_fx_prices(
    pairs: str = "EUR/USD,GBP/USD,USD/JPY,EUR/GBP,AUD/USD",
    tenor: str = "ALL"
):
    """Get FX prices from Azure Redis"""
    try:
        client = get_redis_client()
        
        currency_pairs = [p.strip().upper() for p in pairs.split(',')]
        results = {}
        
        for pair in currency_pairs:
            prices = {
                "currency_pair": pair,
                "tenor": tenor,
                "spot": {},
                "forward": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Get SPOT prices (looking for keys without FORWARD)
            spot_pattern = f"exchange_rate:esp:{pair}:SPOT:*"
            spot_keys = []
            
            # First check if SPOT pattern exists
            cursor = 0
            cursor, test_keys = client.scan(cursor, match=spot_pattern, count=10)
            
            if not test_keys:
                # Try without SPOT in pattern (some feeds might not have it)
                spot_pattern = f"exchange_rate:esp:{pair}:*"
                cursor = 0
                while True:
                    cursor, keys = client.scan(cursor, match=spot_pattern, count=100)
                    # Filter out FORWARD keys
                    spot_keys.extend([k for k in keys if 'FORWARD' not in k])
                    if cursor == 0:
                        break
            else:
                # Use SPOT pattern
                cursor = 0
                while True:
                    cursor, keys = client.scan(cursor, match=spot_pattern, count=100)
                    spot_keys.extend(keys)
                    if cursor == 0:
                        break
            
            # Parse spot prices
            for key in spot_keys[:20]:  # Limit to prevent too many
                try:
                    value = client.get(key)
                    if value:
                        data = json.loads(value)
                        parts = key.split(':')
                        if len(parts) >= 5:
                            bank = parts[-1]  # Last part is usually bank
                            side = parts[-2] if parts[-2] in ['Bid', 'Ask'] else 'Mid'
                            
                            if bank not in prices["spot"]:
                                prices["spot"][bank] = {}
                            
                            prices["spot"][bank][side.lower()] = {
                                "rate": float(data.get("rate", 0)),
                                "timestamp": data.get("timestamp", "")
                            }
                except Exception as e:
                    print(f"Error parsing {key}: {e}")
            
            # Get FORWARD prices
            if tenor != "SPOT":
                forward_tenor = "M1" if tenor == "ALL" else tenor
                forward_pattern = f"exchange_rate:esp:{pair}:FORWARD:*:*:{forward_tenor}:*"
                forward_keys = []
                
                cursor = 0
                while True:
                    cursor, keys = client.scan(cursor, match=forward_pattern, count=100)
                    forward_keys.extend(keys)
                    if cursor == 0:
                        break
                
                # Parse forward prices
                for key in forward_keys[:20]:  # Limit
                    try:
                        value = client.get(key)
                        if value:
                            data = json.loads(value)
                            parts = key.split(':')
                            if len(parts) >= 7:
                                bank = parts[7] if len(parts) > 7 else "UNKNOWN"
                                side = parts[5] if len(parts) > 5 else "Mid"
                                
                                if bank not in prices["forward"]:
                                    prices["forward"][bank] = {}
                                
                                prices["forward"][bank][side.lower()] = {
                                    "rate": float(data.get("rate", 0)),
                                    "timestamp": data.get("timestamp", ""),
                                    "tenor": forward_tenor
                                }
                    except Exception as e:
                        print(f"Error parsing {key}: {e}")
            
            results[pair] = prices
        
        return {
            "prices": results,
            "timestamp": datetime.now().isoformat(),
            "source": "Azure Redis Cache"
        }
        
    except Exception as e:
        print(f"❌ Redis error: {e}")
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check"""
    try:
        # Test PostgreSQL
        conn = get_azure_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fx_forward_trades")
        trade_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        # Test Redis
        client = get_redis_client()
        client.ping()
        
        return {
            "status": "healthy",
            "postgres": "connected",
            "redis": "connected",
            "fx_trades_count": trade_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("🚀 Starting Combined Azure API on http://localhost:8000")
    print("📊 PostgreSQL: Azure Database for FX Forward Trades")
    print("💹 Redis: Azure Cache for Real-time FX Prices")
    print("✅ NO MOCK DATA - 100% Azure Services")
    uvicorn.run(app, host="0.0.0.0", port=8000)