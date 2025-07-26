"""Market data API endpoints"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from services.bloomberg import BloombergClient
from models.market import (
    SpotRateRequest, 
    ForwardPointsRequest,
    InterestRatesRequest,
    MarketDataResponse
)

router = APIRouter()
bloomberg_client = BloombergClient()

@router.post("/spot", response_model=MarketDataResponse)
async def get_spot_rates(request: SpotRateRequest):
    """Get real-time spot rates from Bloomberg"""
    try:
        data = await bloomberg_client.get_spot_rates(request.pairs)
        return MarketDataResponse(
            success=True,
            timestamp=datetime.utcnow(),
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch spot rates: {str(e)}")

@router.post("/forward-points", response_model=MarketDataResponse)
async def get_forward_points(request: ForwardPointsRequest):
    """Get forward points from Bloomberg"""
    try:
        data = await bloomberg_client.get_forward_points(request.pairs, request.tenors)
        return MarketDataResponse(
            success=True,
            timestamp=datetime.utcnow(),
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch forward points: {str(e)}")

@router.post("/interest-rates", response_model=MarketDataResponse)
async def get_interest_rates(request: InterestRatesRequest):
    """Get interest rates from Bloomberg"""
    try:
        data = await bloomberg_client.get_interest_rates(request.currencies, request.tenors)
        return MarketDataResponse(
            success=True,
            timestamp=datetime.utcnow(),
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch interest rates: {str(e)}")

@router.post("/volatility-surface")
async def get_volatility_surface(pair: str, tenors: List[str]):
    """Get volatility surface data from Bloomberg"""
    try:
        data = await bloomberg_client.get_volatility_surface(pair, tenors)
        return MarketDataResponse(
            success=True,
            timestamp=datetime.utcnow(),
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch volatility surface: {str(e)}")