"""
FX Options Pricing Engine API
Integrates with Bloomberg data for real-time options pricing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import health, market_data, pricing
import uvicorn

app = FastAPI(
    title="FX Options Pricing Engine",
    description="Real-time FX options pricing with Bloomberg data",
    version="0.1.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3501", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(market_data.router, prefix="/api/market-data", tags=["market"])
app.include_router(pricing.router, prefix="/api/pricing", tags=["pricing"])

@app.get("/")
async def root():
    return {
        "message": "FX Options Pricing Engine",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "market_data": "/api/market-data",
            "pricing": "/api/pricing"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)