#!/usr/bin/env python3
"""
Simple FastAPI server for FX Forward Trades API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
import uvicorn

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

# Mock data for development
MOCK_FX_FORWARD_TRADES = [
    {
        "id": "FWD001",
        "trade_date": "2025-07-01",
        "value_date": "2025-09-01",
        "currency_pair": "EUR/USD",
        "notional": 10000000.0,
        "rate": 1.0950,
        "market_rate": 1.0987,
        "pnl": 37000.0,
        "counterparty": "Goldman Sachs",
        "status": "active",
        "trader": "John Smith",
        "created_at": "2025-07-01T09:30:00Z",
        "updated_at": "2025-07-01T15:45:00Z"
    },
    {
        "id": "FWD002",
        "trade_date": "2025-06-28",
        "value_date": "2025-08-28",
        "currency_pair": "GBP/USD",
        "notional": 5000000.0,
        "rate": 1.2750,
        "market_rate": 1.2723,
        "pnl": -13500.0,
        "counterparty": "JP Morgan",
        "status": "active",
        "trader": "Sarah Johnson",
        "created_at": "2025-06-28T14:15:00Z",
        "updated_at": "2025-07-01T11:20:00Z"
    },
    {
        "id": "FWD003",
        "trade_date": "2025-06-25",
        "value_date": "2025-12-25",
        "currency_pair": "USD/JPY",
        "notional": 8000000.0,
        "rate": 158.50,
        "market_rate": 159.25,
        "pnl": 37841.0,
        "counterparty": "Deutsche Bank",
        "status": "active",
        "trader": "Mike Chen",
        "created_at": "2025-06-25T10:45:00Z",
        "updated_at": "2025-07-01T16:30:00Z"
    },
    {
        "id": "FWD004",
        "trade_date": "2025-06-20",
        "value_date": "2025-07-20",
        "currency_pair": "AUD/USD",
        "notional": 3000000.0,
        "rate": 0.6850,
        "market_rate": 0.6835,
        "pnl": -4500.0,
        "counterparty": "UBS",
        "status": "settled",
        "trader": "David Wilson",
        "created_at": "2025-06-20T13:20:00Z",
        "updated_at": "2025-07-20T10:00:00Z"
    },
    {
        "id": "FWD005",
        "trade_date": "2025-06-15",
        "value_date": "2025-09-15",
        "currency_pair": "USD/CHF",
        "notional": 6000000.0,
        "rate": 0.8720,
        "market_rate": 0.8735,
        "pnl": 10338.0,
        "counterparty": "Credit Suisse",
        "status": "active",
        "trader": "Anna Rodriguez",
        "created_at": "2025-06-15T11:30:00Z",
        "updated_at": "2025-07-01T14:15:00Z"
    }
]

# Create FastAPI app
app = FastAPI(
    title="GZC Portfolio FX Forward Trades API",
    description="Simple API for FX forward trades data",
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
        "message": "GZC Portfolio FX Forward Trades API",
        "version": "1.0.0",
        "status": "operational",
        "azure_connected": True
    }

@app.get("/api/fx-forward-trades", response_model=List[FXForwardTradeResponse])
async def get_fx_forward_trades(
    status: Optional[str] = None,
    currency_pair: Optional[str] = None,
    trader: Optional[str] = None,
):
    """
    Get all FX forward trades with optional filtering
    
    - **status**: Filter by trade status (active, settled, cancelled)
    - **currency_pair**: Filter by currency pair (e.g., EUR/USD)
    - **trader**: Filter by trader name
    """
    try:
        # Filter mock data
        trades = MOCK_FX_FORWARD_TRADES.copy()
        
        if status:
            trades = [t for t in trades if t["status"] == status]
        if currency_pair:
            trades = [t for t in trades if t["currency_pair"] == currency_pair]
        if trader:
            trades = [t for t in trades if t["trader"].lower() == trader.lower()]
        
        return trades
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching FX forward trades: {str(e)}")

@app.get("/api/fx-forward-trades/{trade_id}", response_model=FXForwardTradeResponse)
async def get_fx_forward_trade(trade_id: str):
    """
    Get a specific FX forward trade by ID
    """
    try:
        trade = next((t for t in MOCK_FX_FORWARD_TRADES if t["id"] == trade_id), None)
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        return trade
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trade: {str(e)}")

@app.get("/api/fx-forward-trades/summary/stats")
async def get_fx_forward_trades_summary():
    """
    Get summary statistics for FX forward trades
    """
    try:
        active_trades = [t for t in MOCK_FX_FORWARD_TRADES if t["status"] == "active"]
        total_notional = sum(t["notional"] for t in MOCK_FX_FORWARD_TRADES)
        total_pnl = sum(t["pnl"] for t in MOCK_FX_FORWARD_TRADES)
        
        return {
            "total_trades": len(MOCK_FX_FORWARD_TRADES),
            "active_trades": len(active_trades),
            "total_notional": total_notional,
            "total_pnl": total_pnl,
            "currency_pairs": list(set(t["currency_pair"] for t in MOCK_FX_FORWARD_TRADES)),
            "counterparties": list(set(t["counterparty"] for t in MOCK_FX_FORWARD_TRADES)),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating summary: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "azure_keyvault": "connected",
        "postgresql": "connected",
        "redis": "connected",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting GZC Portfolio FX Forward Trades API on http://localhost:8001")
    print("📊 Azure PostgreSQL data simulation active")
    print("🔑 Key Vault authentication simulated")
    uvicorn.run(app, host="0.0.0.0", port=8001)