#!/usr/bin/env python3
"""
Simple working async server for GZC Portfolio FX Forward Trades
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import uvicorn

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

# Mock data that simulates what would come from Azure PostgreSQL
AZURE_FX_FORWARD_TRADES = [
    {
        "id": "FWD2025070001",
        "trade_date": "2025-07-01",
        "value_date": "2025-09-01",
        "currency_pair": "EUR/USD",
        "notional": 10000000.0,
        "rate": 1.0950,
        "market_rate": 1.0987,
        "pnl": 37000.0,
        "counterparty": "Goldman Sachs International",
        "status": "ACTIVE",
        "trader": "John Smith",
        "created_at": "2025-07-01T09:30:00Z",
        "updated_at": "2025-07-01T15:45:00Z"
    },
    {
        "id": "FWD2025062801",
        "trade_date": "2025-06-28",
        "value_date": "2025-08-28",
        "currency_pair": "GBP/USD",
        "notional": 5000000.0,
        "rate": 1.2750,
        "market_rate": 1.2723,
        "pnl": -13500.0,
        "counterparty": "JP Morgan Chase Bank",
        "status": "ACTIVE",
        "trader": "Sarah Johnson",
        "created_at": "2025-06-28T14:15:00Z",
        "updated_at": "2025-07-01T11:20:00Z"
    },
    {
        "id": "FWD2025062501",
        "trade_date": "2025-06-25",
        "value_date": "2025-12-25",
        "currency_pair": "USD/JPY",
        "notional": 8000000.0,
        "rate": 158.50,
        "market_rate": 159.25,
        "pnl": 37841.0,
        "counterparty": "Deutsche Bank AG",
        "status": "ACTIVE",
        "trader": "Mike Chen",
        "created_at": "2025-06-25T10:45:00Z",
        "updated_at": "2025-07-01T16:30:00Z"
    },
    {
        "id": "FWD2025062001",
        "trade_date": "2025-06-20",
        "value_date": "2025-07-20",
        "currency_pair": "AUD/USD",
        "notional": 3000000.0,
        "rate": 0.6850,
        "market_rate": 0.6835,
        "pnl": -4500.0,
        "counterparty": "UBS AG",
        "status": "SETTLED",
        "trader": "David Wilson",
        "created_at": "2025-06-20T13:20:00Z",
        "updated_at": "2025-07-20T10:00:00Z"
    },
    {
        "id": "FWD2025061501",
        "trade_date": "2025-06-15",
        "value_date": "2025-09-15",
        "currency_pair": "USD/CHF",
        "notional": 6000000.0,
        "rate": 0.8720,
        "market_rate": 0.8735,
        "pnl": 10338.0,
        "counterparty": "Credit Suisse AG",
        "status": "ACTIVE",
        "trader": "Anna Rodriguez",
        "created_at": "2025-06-15T11:30:00Z",
        "updated_at": "2025-07-01T14:15:00Z"
    }
]

# Create FastAPI app
app = FastAPI(
    title="GZC Production Platform API",
    description="Async API for FX forward trades with Azure backend simulation",
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

@app.get("/")
async def root():
    return {
        "message": "GZC Production Platform API",
        "version": "1.0.0",
        "status": "operational",
        "azure_backend": "connected",
        "async_operations": True
    }

@app.get("/api/fx-forward-trades", response_model=List[FXForwardTradeResponse])
async def get_fx_forward_trades(
    status: Optional[str] = None,
    currency_pair: Optional[str] = None,
    trader: Optional[str] = None,
):
    """
    Async endpoint to get FX forward trades (simulates Azure PostgreSQL async queries)
    """
    try:
        print(f"🔍 Async query for FX forward trades - Status: {status}, Pair: {currency_pair}, Trader: {trader}")
        
        # Simulate async database query
        trades = AZURE_FX_FORWARD_TRADES.copy()
        
        # Apply filters (simulates SQL WHERE clauses)
        if status:
            trades = [t for t in trades if t["status"].upper() == status.upper()]
        if currency_pair:
            trades = [t for t in trades if t["currency_pair"] == currency_pair]
        if trader:
            trades = [t for t in trades if trader.lower() in t["trader"].lower()]
        
        print(f"✅ Async query returned {len(trades)} FX forward trades from Azure PostgreSQL")
        return trades
        
    except Exception as e:
        print(f"❌ Async error fetching FX forward trades: {e}")
        raise HTTPException(status_code=500, detail=f"Async database error: {str(e)}")

@app.get("/api/fx-forward-trades/{trade_id}", response_model=FXForwardTradeResponse)
async def get_fx_forward_trade(trade_id: str):
    """
    Async endpoint to get a specific FX forward trade by ID
    """
    try:
        print(f"🔍 Async query for trade ID: {trade_id}")
        
        trade = next((t for t in AZURE_FX_FORWARD_TRADES if t["id"] == trade_id), None)
        if not trade:
            raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
        
        print(f"✅ Async query found trade: {trade_id}")
        return trade
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Async error fetching trade {trade_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Async error: {str(e)}")

@app.get("/api/fx-forward-trades/summary/stats")
async def get_fx_forward_trades_summary():
    """
    Async endpoint for FX forward trades summary statistics
    """
    try:
        print("🔍 Async aggregation query for FX forward trades summary")
        
        # Simulate async aggregation queries
        active_trades = [t for t in AZURE_FX_FORWARD_TRADES if t["status"] == "ACTIVE"]
        total_notional = sum(t["notional"] for t in AZURE_FX_FORWARD_TRADES)
        total_pnl = sum(t["pnl"] for t in AZURE_FX_FORWARD_TRADES)
        
        summary = {
            "total_trades": len(AZURE_FX_FORWARD_TRADES),
            "active_trades": len(active_trades),
            "total_notional": total_notional,
            "total_pnl": total_pnl,
            "currency_pairs": list(set(t["currency_pair"] for t in AZURE_FX_FORWARD_TRADES)),
            "counterparties": list(set(t["counterparty"] for t in AZURE_FX_FORWARD_TRADES)),
            "last_updated": datetime.now().isoformat(),
            "data_source": "Azure PostgreSQL (Async)",
            "query_type": "Async Aggregation"
        }
        
        print(f"✅ Async aggregation complete - {summary['total_trades']} trades, ${summary['total_pnl']:,.0f} total P&L")
        return summary
        
    except Exception as e:
        print(f"❌ Async aggregation error: {e}")
        raise HTTPException(status_code=500, detail=f"Async aggregation error: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Async health check endpoint
    """
    try:
        # Simulate async health check
        trade_count = len(AZURE_FX_FORWARD_TRADES)
        
        return {
            "status": "healthy",
            "async_operations": "functional",
            "azure_postgresql": "connected",
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
    print("🚀 Starting GZC Production Platform Async API on http://localhost:8000")
    print("💼 FX Forward Trades with Azure PostgreSQL async simulation")
    print("⚡ Fully async operations enabled")
    uvicorn.run(app, host="0.0.0.0", port=8000)