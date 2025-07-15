#!/usr/bin/env python3
"""
Combined Azure Server V2 - PostgreSQL + Redis FX Prices + GZC Data
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
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

class FXTradeResponse(BaseModel):
    trades: List[Dict[str, Any]]
    count: int
    source: str

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
            redis_client = None
    
    return redis_client

# Create FastAPI app
app = FastAPI(
    title="GZC Trading Platform API",
    description="Real Azure data with PostgreSQL and Redis",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3200", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Azure Trading Platform API V2",
        "version": "2.0.0",
        "status": "operational",
        "postgres": "Azure PostgreSQL",
        "redis": "Azure Redis Cache",
        "mock_data": False,
        "gzc_data": True
    }

@app.get("/api/fx-forward-trades", response_model=FXTradeResponse)
async def get_fx_forward_trades(
    source: str = Query("gzc", description="Data source: 'original', 'gzc', or 'combined'"),
    status: Optional[str] = None,
    currency_pair: Optional[str] = None,
    trader: Optional[str] = None,
    fund_id: Optional[int] = Query(None, description="Fund ID: 1=GMF, 6=GCF"),
    active_status: Optional[str] = Query(None, description="Filter by active status: 'active' (not matured), 'inactive' (matured), or None for all"),
    limit: int = Query(100, description="Maximum number of records"),
):
    """Get FX forward trades from Azure PostgreSQL
    
    Sources:
    - 'original': fx_forward_trades table (5 demo trades)
    - 'gzc': gzc_fx_trade table (1,100+ real historical trades)
    - 'combined': Both sources merged
    """
    try:
        conn = get_azure_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        trades = []
        
        # Get original trades
        if source in ["original", "combined"]:
            query = """
                SELECT id, trade_date, value_date, currency_pair, notional, rate, 
                       market_rate, pnl, counterparty, status, trader, created_at, updated_at
                FROM fx_forward_trades 
                WHERE 1=1
            """
            
            params = []
            if status:
                query += " AND status = %s"
                params.append(status)
            if currency_pair:
                query += " AND currency_pair = %s"
                params.append(currency_pair)
            if trader:
                query += " AND trader ILIKE %s"
                params.append(f"%{trader}%")
            
            # Add active status filter based on value date
            if active_status == "active":
                query += " AND value_date > CURRENT_DATE"
            elif active_status == "inactive":
                query += " AND value_date <= CURRENT_DATE"
            
            query += " ORDER BY trade_date DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            for row in rows:
                trade = dict(row)
                trade["trade_date"] = trade["trade_date"].isoformat() if trade["trade_date"] else None
                trade["value_date"] = trade["value_date"].isoformat() if trade["value_date"] else None
                trade["created_at"] = trade["created_at"].isoformat() if trade["created_at"] else None
                trade["updated_at"] = trade["updated_at"].isoformat() if trade["updated_at"] else None
                trade["source"] = "original"
                trades.append(trade)
        
        # Get GZC trades
        if source in ["gzc", "combined"]:
            query = """
                SELECT 
                    'GZC-' || trade_id::text as id,
                    trade_date,
                    maturity_date as value_date,
                    trade_currency || '/' || settlement_currency as currency_pair,
                    quantity as notional,
                    price as rate,
                    price as market_rate,
                    0 as pnl,
                    counter_party_code as counterparty,
                    CASE WHEN active THEN 'ACTIVE' ELSE 'INACTIVE' END as status,
                    trader,
                    mod_timestamp as created_at,
                    mod_timestamp as updated_at
                FROM gzc_fx_trade
                WHERE 1=1
            """
            
            params = []
            if status:
                if status == "ACTIVE":
                    query += " AND active = true"
                elif status == "INACTIVE":
                    query += " AND active = false"
            if currency_pair:
                query += " AND (trade_currency || '/' || settlement_currency) = %s"
                params.append(currency_pair)
            if trader:
                query += " AND trader ILIKE %s"
                params.append(f"%{trader}%")
            
            # Add active status filter based on maturity date
            if active_status == "active":
                query += " AND maturity_date > CURRENT_DATE"
            elif active_status == "inactive":
                query += " AND maturity_date <= CURRENT_DATE"
            
            # Add fund filter
            if fund_id:
                query += " AND fund_id = %s"
                params.append(fund_id)
            
            query += f" ORDER BY trade_date DESC LIMIT {limit}"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            for row in rows:
                trade = dict(row)
                trade["trade_date"] = trade["trade_date"].isoformat() if trade["trade_date"] else None
                trade["value_date"] = trade["value_date"].isoformat() if trade["value_date"] else None
                trade["created_at"] = trade["created_at"].isoformat() if trade["created_at"] else None
                trade["updated_at"] = trade["updated_at"].isoformat() if trade["updated_at"] else None
                trade["notional"] = float(trade["notional"]) if trade["notional"] else 0
                trade["rate"] = float(trade["rate"]) if trade["rate"] else 0
                trade["market_rate"] = float(trade["market_rate"]) if trade["market_rate"] else 0
                trade["pnl"] = float(trade["pnl"]) if trade["pnl"] else 0
                trade["source"] = "gzc"
                trades.append(trade)
        
        cursor.close()
        conn.close()
        
        # Sort by trade date (newest first)
        trades.sort(key=lambda x: x['trade_date'] or '', reverse=True)
        
        # Limit total results
        trades = trades[:limit]
        
        print(f"✅ Retrieved {len(trades)} trades from source: {source}")
        return {"trades": trades, "count": len(trades), "source": source}
        
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
        if not client:
            return {"error": "Redis not available", "prices": {}}
        
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
            
            # Get SPOT prices
            spot_pattern = f"exchange_rate:esp:{pair}:SPOT:*"
            spot_keys = client.keys(spot_pattern)
            
            if spot_keys:
                for key in spot_keys[:5]:  # Limit to avoid too many
                    try:
                        data = client.get(key)
                        if data:
                            price_data = json.loads(data)
                            parts = key.split(':')
                            if len(parts) >= 6:
                                side = parts[5].lower()
                                prices["spot"][side] = price_data.get("rate", 0)
                    except:
                        pass
            
            # Get FORWARD prices
            forward_pattern = f"exchange_rate:esp:{pair}:FORWARD:*"
            forward_keys = client.keys(forward_pattern)
            
            if forward_keys:
                forward_by_tenor = {}
                for key in forward_keys[:10]:  # Limit
                    try:
                        data = client.get(key)
                        if data:
                            price_data = json.loads(data)
                            parts = key.split(':')
                            if len(parts) >= 7:
                                tenor_code = parts[6]  # M1, M3, etc
                                side = parts[5].lower()
                                if tenor_code not in forward_by_tenor:
                                    forward_by_tenor[tenor_code] = {}
                                forward_by_tenor[tenor_code][side] = price_data.get("rate", 0)
                    except:
                        pass
                
                prices["forward"] = forward_by_tenor
            
            results[pair] = prices
        
        return {"prices": results, "source": "azure_redis"}
        
    except Exception as e:
        print(f"❌ Redis error: {e}")
        return {"error": str(e), "prices": {}}

@app.get("/api/fx-positions")
async def get_fx_positions(
    as_of_date: Optional[str] = None,
    currency_pair: Optional[str] = None,
    trader: Optional[str] = None,
    fund_id: Optional[int] = Query(None, description="Fund ID: 1=GMF, 6=GCF"),
    active_status: Optional[str] = Query(None, description="Filter by active status based on maturity date")
):
    """Calculate FX positions from trades using GZCDB methodology"""
    try:
        conn = get_azure_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build query with filters
        conditions = ["1=1"]
        params = []
        
        if as_of_date:
            conditions.append("trade_date <= %s")
            params.append(as_of_date)
        
        if currency_pair:
            conditions.append("(trade_currency || '/' || settlement_currency) = %s")
            params.append(currency_pair)
        
        if trader:
            conditions.append("trader = %s")
            params.append(trader)
        
        if fund_id:
            conditions.append("fund_id = %s")
            params.append(fund_id)
        
        if active_status == "active":
            conditions.append("maturity_date > CURRENT_DATE")
        elif active_status == "inactive":
            conditions.append("maturity_date <= CURRENT_DATE")
        
        where_clause = " AND ".join(conditions)
        
        # Calculate positions using GZCDB methodology
        query = f"""
            WITH position_calc AS (
                SELECT 
                    trade_currency || '/' || settlement_currency as currency_pair,
                    trader,
                    counter_party_code,
                    -- Net position: BUY adds, SELL subtracts
                    SUM(CASE 
                        WHEN UPPER(position) = 'BUY' THEN quantity 
                        ELSE -quantity 
                    END) as net_position,
                    COUNT(*) as trade_count,
                    -- Weighted average rate
                    SUM(price * ABS(quantity)) / NULLIF(SUM(ABS(quantity)), 0) as weighted_avg_rate,
                    MAX(trade_date) as last_trade_date,
                    MIN(trade_date) as first_trade_date,
                    SUM(CASE WHEN active THEN 1 ELSE 0 END) as active_trades,
                    SUM(ABS(quantity)) as total_volume
                FROM gzc_fx_trade
                WHERE {where_clause}
                GROUP BY trade_currency || '/' || settlement_currency, trader, counter_party_code
            )
            SELECT 
                currency_pair,
                trader,
                counter_party_code,
                net_position,
                trade_count,
                weighted_avg_rate,
                last_trade_date,
                first_trade_date,
                active_trades,
                total_volume,
                CASE 
                    WHEN net_position > 0 THEN 'LONG'
                    WHEN net_position < 0 THEN 'SHORT'
                    ELSE 'FLAT'
                END as position_status
            FROM position_calc
            WHERE ABS(net_position) > 0
            ORDER BY ABS(net_position) DESC
        """
        
        cursor.execute(query, params)
        positions = cursor.fetchall()
        
        # Convert decimals to floats for JSON
        for pos in positions:
            pos['net_position'] = float(pos['net_position']) if pos['net_position'] else 0
            pos['weighted_avg_rate'] = float(pos['weighted_avg_rate']) if pos['weighted_avg_rate'] else 0
            pos['total_volume'] = float(pos['total_volume']) if pos['total_volume'] else 0
            pos['last_trade_date'] = pos['last_trade_date'].isoformat() if pos['last_trade_date'] else None
            pos['first_trade_date'] = pos['first_trade_date'].isoformat() if pos['first_trade_date'] else None
        
        # Calculate summary statistics
        summary = {
            'total_positions': len(positions),
            'long_positions': sum(1 for p in positions if p['position_status'] == 'LONG'),
            'short_positions': sum(1 for p in positions if p['position_status'] == 'SHORT'),
            'total_volume': sum(p['total_volume'] for p in positions),
            'unique_pairs': len(set(p['currency_pair'] for p in positions)),
            'unique_traders': len(set(p['trader'] for p in positions))
        }
        
        cursor.close()
        conn.close()
        
        return {
            'as_of_date': as_of_date or 'current',
            'summary': summary,
            'positions': positions
        }
        
    except Exception as e:
        print(f"❌ Error calculating positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fx-positions-aggregated")
async def get_fx_positions_aggregated(
    fund_id: Optional[int] = Query(None, description="Fund ID: 1=GMF, 6=GCF"),
    active_status: Optional[str] = Query(None, description="Filter by active status: 'active' or 'inactive'")
):
    """Get positions aggregated by currency pair"""
    try:
        conn = get_azure_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build query with filters
        conditions = ["1=1"]
        params = []
        
        if fund_id:
            conditions.append("fund_id = %s")
            params.append(fund_id)
        
        if active_status == "active":
            conditions.append("maturity_date > CURRENT_DATE")
        elif active_status == "inactive":
            conditions.append("maturity_date <= CURRENT_DATE")
        
        where_clause = " AND ".join(conditions)
        
        # Aggregate positions by currency pair only
        query = f"""
            WITH aggregated AS (
                SELECT 
                    trade_currency || '/' || settlement_currency as currency_pair,
                    SUM(CASE 
                        WHEN UPPER(position) = 'BUY' THEN quantity 
                        ELSE -quantity 
                    END) as net_position,
                    COUNT(*) as trade_count,
                    SUM(price * ABS(quantity)) / NULLIF(SUM(ABS(quantity)), 0) as weighted_avg_rate,
                    SUM(ABS(quantity)) as total_volume,
                    MAX(trade_date) as last_trade_date
                FROM gzc_fx_trade
                WHERE {where_clause}
                GROUP BY trade_currency || '/' || settlement_currency
                HAVING ABS(SUM(CASE 
                    WHEN UPPER(position) = 'BUY' THEN quantity 
                    ELSE -quantity 
                END)) > 0
            )
            SELECT 
                currency_pair,
                net_position,
                trade_count,
                weighted_avg_rate,
                total_volume,
                last_trade_date,
                CASE 
                    WHEN net_position > 0 THEN 'LONG'
                    WHEN net_position < 0 THEN 'SHORT'
                    ELSE 'FLAT'
                END as position_status
            FROM aggregated
            ORDER BY ABS(net_position) DESC
        """
        
        cursor.execute(query, params)
        positions = cursor.fetchall()
        
        # Convert decimals to floats
        for pos in positions:
            pos['net_position'] = float(pos['net_position']) if pos['net_position'] else 0
            pos['weighted_avg_rate'] = float(pos['weighted_avg_rate']) if pos['weighted_avg_rate'] else 0
            pos['total_volume'] = float(pos['total_volume']) if pos['total_volume'] else 0
            pos['last_trade_date'] = pos['last_trade_date'].isoformat() if pos['last_trade_date'] else None
        
        # Calculate summary
        summary = {
            'total_positions': len(positions),
            'long_positions': sum(1 for p in positions if p['position_status'] == 'LONG'),
            'short_positions': sum(1 for p in positions if p['position_status'] == 'SHORT'),
            'total_volume': sum(p['total_volume'] for p in positions),
            'unique_pairs': len(positions)
        }
        
        cursor.close()
        conn.close()
        
        return {
            'summary': summary,
            'positions': positions,
            'filter': {
                'fund_id': fund_id,
                'active_status': active_status
            }
        }
        
    except Exception as e:
        print(f"❌ Error calculating aggregated positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gzc-stats")
async def get_gzc_stats():
    """Get statistics about GZC data"""
    try:
        conn = get_azure_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Total trades
        cursor.execute("SELECT COUNT(*) as total FROM gzc_fx_trade")
        total = cursor.fetchone()["total"]
        
        # By status
        cursor.execute("""
            SELECT 
                CASE WHEN active THEN 'ACTIVE' ELSE 'INACTIVE' END as status,
                COUNT(*) as count
            FROM gzc_fx_trade
            GROUP BY active
        """)
        status_breakdown = {row["status"]: row["count"] for row in cursor.fetchall()}
        
        # By year
        cursor.execute("""
            SELECT 
                EXTRACT(YEAR FROM trade_date) as year,
                COUNT(*) as count
            FROM gzc_fx_trade
            GROUP BY EXTRACT(YEAR FROM trade_date)
            ORDER BY year DESC
            LIMIT 10
        """)
        yearly_breakdown = [{"year": int(row["year"]), "count": row["count"]} for row in cursor.fetchall()]
        
        # Top currency pairs
        cursor.execute("""
            SELECT 
                trade_currency || '/' || settlement_currency as pair,
                COUNT(*) as count
            FROM gzc_fx_trade
            GROUP BY trade_currency, settlement_currency
            ORDER BY count DESC
            LIMIT 10
        """)
        top_pairs = [{"pair": row["pair"], "count": row["count"]} for row in cursor.fetchall()]
        
        # Available currencies
        cursor.execute("SELECT currency, yield_curve_id FROM gzc_currency ORDER BY currency")
        currencies = [{"code": row["currency"], "yield_curve": row["yield_curve_id"]} for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {
            "total_trades": total,
            "status_breakdown": status_breakdown,
            "yearly_breakdown": yearly_breakdown,
            "top_currency_pairs": top_pairs,
            "available_currencies": currencies,
            "data_source": "GZCDB imported to Azure PostgreSQL"
        }
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Combined Azure API V2 on http://localhost:8001")
    print("📊 PostgreSQL: Azure Database for FX Trades (Original + GZC)")
    print("💹 Redis: Azure Cache for Real-time FX Prices")
    print("✅ NO MOCK DATA - 100% Azure Services")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)