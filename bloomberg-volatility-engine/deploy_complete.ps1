# Complete deployment script
Write-Host "Rebuilding Bloomberg API Server..." -ForegroundColor Cyan

# Kill existing processes
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Create the new API server file
$apiCode = @'
#!/usr/bin/env python3
"""Bloomberg API Server - Direct Terminal Access"""

import sys
sys.path.append(r"C:\blp\API\Python")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import uvicorn
import blpapi
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bloomberg API Server", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Bloomberg:
    def __init__(self):
        self.session = None
        self.service = None
        self.connected = False
        
    def connect(self):
        try:
            opts = blpapi.SessionOptions()
            opts.setServerHost("localhost")
            opts.setServerPort(8194)
            self.session = blpapi.Session(opts)
            
            if self.session.start() and self.session.openService("//blp/refdata"):
                self.service = self.session.getService("//blp/refdata")
                self.connected = True
                logger.info("Connected to Bloomberg")
                return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
        return False

bloomberg = Bloomberg()

class MarketDataRequest(BaseModel):
    securities: List[str]
    fields: List[str]

@app.on_event("startup")
async def startup():
    bloomberg.connect()

@app.get("/health")
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "bloomberg_connected": bloomberg.connected,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/market-data")
async def market_data(req: MarketDataRequest):
    if not bloomberg.connected:
        bloomberg.connect()
        if not bloomberg.connected:
            raise HTTPException(503, "Bloomberg not connected")
    
    try:
        request = bloomberg.service.createRequest("ReferenceDataRequest")
        for s in req.securities:
            request.append("securities", s)
        for f in req.fields:
            request.append("fields", f)
        
        bloomberg.session.sendRequest(request)
        
        results = []
        while True:
            event = bloomberg.session.nextEvent(5000)
            for msg in event:
                if msg.hasElement("securityData"):
                    secData = msg.getElement("securityData")
                    for i in range(secData.numValues()):
                        sec = secData.getValue(i)
                        name = sec.getElementAsString("security")
                        data = {}
                        if sec.hasElement("fieldData"):
                            fields = sec.getElement("fieldData")
                            for f in req.fields:
                                if fields.hasElement(f):
                                    val = fields.getElement(f).getValue()
                                    data[f] = float(val) if isinstance(val, (int, float)) else str(val)
                        results.append({"security": name, "fields": data})
            if event.eventType() == blpapi.Event.RESPONSE:
                break
        return results
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/fx/rates")
async def fx_rates():
    req = MarketDataRequest(
        securities=["EURUSD Curncy", "GBPUSD Curncy", "USDJPY Curncy"],
        fields=["PX_LAST", "PX_BID", "PX_ASK", "CHG_PCT_1D"]
    )
    return await market_data(req)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
'@

# Save the file
$apiCode | Out-File -FilePath "C:\Bloomberg\APIServer\bloomberg_api_server_v3.py" -Encoding UTF8
Write-Host "Created new API server file"

# Start the server
cd C:\Bloomberg\APIServer
Start-Process -FilePath "C:\Python311\python.exe" -ArgumentList "bloomberg_api_server_v3.py" -WindowStyle Hidden
Write-Host "Started API server"

# Test after a few seconds
Start-Sleep -Seconds 5
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/health"
    Write-Host "✓ API Server running! Bloomberg connected: $($response.bloomberg_connected)" -ForegroundColor Green
} catch {
    Write-Host "Server starting..." -ForegroundColor Yellow
}