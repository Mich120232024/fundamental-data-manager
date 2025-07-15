#!/usr/bin/env python3
"""
Bloomberg API Server v2 - Complete Rebuild
Provides REST API access to Bloomberg Terminal data
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add Bloomberg Python API path
sys.path.append(r"C:\blp\API\Python")
import blpapi

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Bloomberg Terminal API Server (REAL)",
    description="Direct access to Bloomberg Terminal data",
    version="3.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bloomberg connection singleton
class BloombergConnection:
    def __init__(self):
        self.session = None
        self.service = None
        self.connected = False
        
    def connect(self):
        """Connect to Bloomberg Terminal"""
        try:
            sessionOptions = blpapi.SessionOptions()
            sessionOptions.setServerHost("localhost")
            sessionOptions.setServerPort(8194)
            
            self.session = blpapi.Session(sessionOptions)
            
            if not self.session.start():
                logger.error("Failed to start Bloomberg session")
                return False
                
            if not self.session.openService("//blp/refdata"):
                logger.error("Failed to open reference data service")
                return False
                
            self.service = self.session.getService("//blp/refdata")
            self.connected = True
            logger.info("✓ Connected to Bloomberg Terminal")
            return True
            
        except Exception as e:
            logger.error(f"Bloomberg connection error: {e}")
            self.connected = False
            return False
    
    def ensure_connected(self):
        """Ensure Bloomberg is connected"""
        if not self.connected:
            return self.connect()
        return True

# Global Bloomberg connection
bloomberg = BloombergConnection()

# Request models
class MarketDataRequest(BaseModel):
    securities: List[str]
    fields: List[str]

class FXRatesRequest(BaseModel):
    pairs: List[str] = ["EURUSD", "GBPUSD", "USDJPY"]

# API Routes
@app.on_event("startup")
async def startup_event():
    """Initialize Bloomberg connection on startup"""
    bloomberg.connect()

@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "message": "Bloomberg Terminal API Server (REAL)",
        "version": "3.0",
        "bloomberg_connected": bloomberg.connected,
        "endpoints": [
            "/health - Server health and Bloomberg status",
            "/api/fx/rates - Real FX rates from Bloomberg",
            "/api/market-data - Real market data",
            "/api/news - Bloomberg news",
            "/api/test - Connection test"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/test")
async def test_connection():
    """Test Bloomberg connection with real data"""
    if not bloomberg.ensure_connected():
        raise HTTPException(status_code=503, detail="Bloomberg Terminal not connected")
    
    try:
        # Test with simple request
        request = bloomberg.service.createRequest("ReferenceDataRequest")
        request.append("securities", "IBM US Equity")
        request.append("fields", "PX_LAST")
        
        bloomberg.session.sendRequest(request)
        
        while True:
            event = bloomberg.session.nextEvent(5000)
            
            for msg in event:
                if msg.hasElement("securityData"):
                    secData = msg.getElement("securityData").getValue(0)
                    if secData.hasElement("fieldData"):
                        fieldData = secData.getElement("fieldData")
                        price = fieldData.getElement("PX_LAST").getValue()
                        
                        return {
                            "status": "success",
                            "message": "Bloomberg connection working",
                            "test_data": {
                                "security": "IBM US Equity",
                                "last_price": float(price)
                            }
                        }
            
            if event.eventType() == blpapi.Event.RESPONSE:
                break
                
    except Exception as e:
        logger.error(f"Test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/market-data")
async def get_market_data(request: MarketDataRequest):
    """Get real-time market data from Bloomberg"""
    if not bloomberg.ensure_connected():
        raise HTTPException(status_code=503, detail="Bloomberg Terminal not connected")
    
    try:
        # Create Bloomberg request
        ref_request = bloomberg.service.createRequest("ReferenceDataRequest")
        
        # Add securities
        for security in request.securities:
            ref_request.append("securities", security)
        
        # Add fields
        for field in request.fields:
            ref_request.append("fields", field)
        
        # Send request
        bloomberg.session.sendRequest(ref_request)
        
        # Collect results
        results = []
        while True:
            event = bloomberg.session.nextEvent(5000)
            
            for msg in event:
                if msg.hasElement("securityData"):
                    securityData = msg.getElement("securityData")
                    
                    for i in range(securityData.numValues()):
                        security = securityData.getValue(i)
                        security_name = security.getElementAsString("security")
                        
                        field_data = {}
                        if security.hasElement("fieldData"):
                            fields = security.getElement("fieldData")
                            
                            for field in request.fields:
                                if fields.hasElement(field):
                                    try:
                                        value = fields.getElement(field).getValue()
                                        # Convert to Python native types
                                        if isinstance(value, (int, float)):
                                            field_data[field] = float(value)
                                        else:
                                            field_data[field] = str(value)
                                    except:
                                        field_data[field] = None
                        
                        results.append({
                            "security": security_name,
                            "fields": field_data
                        })
            
            if event.eventType() == blpapi.Event.RESPONSE:
                break
        
        return results
        
    except Exception as e:
        logger.error(f"Market data error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get market data: {str(e)}")

@app.get("/api/fx/rates")
async def get_fx_rates():
    """Get FX rates from Bloomberg"""
    # Default major pairs
    pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF"]
    securities = [f"{pair} Curncy" for pair in pairs]
    fields = ["PX_LAST", "PX_BID", "PX_ASK", "CHG_PCT_1D"]
    
    request = MarketDataRequest(securities=securities, fields=fields)
    try:
        data = await get_market_data(request)
        return {"rates": data, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get FX rates: {str(e)}")

@app.post("/api/news")
async def get_news():
    """Get Bloomberg news (placeholder - requires news license)"""
    return {
        "message": "News API requires additional Bloomberg license",
        "available": False,
        "suggestion": "Use market data fields like NEWS_HEAT_AVG_DAILY for sentiment"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Bloomberg API Server v3",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    logger.info("Starting Bloomberg API Server on port 8080...")
    logger.info(f"Bloomberg connection: {'Available' if bloomberg.connect() else 'Failed'}")
    
    # Run server
    uvicorn.run(
        app, 
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )