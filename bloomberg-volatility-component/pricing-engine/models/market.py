"""Market data models"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class SpotRateRequest(BaseModel):
    """Request for spot rates"""
    pairs: List[str] = Field(..., example=["EURUSD", "GBPUSD"])

class ForwardPointsRequest(BaseModel):
    """Request for forward points"""
    pairs: List[str] = Field(..., example=["EURUSD", "GBPUSD"])
    tenors: List[str] = Field(..., example=["1W", "1M", "3M"])

class InterestRatesRequest(BaseModel):
    """Request for interest rates"""
    currencies: List[str] = Field(..., example=["USD", "EUR"])
    tenors: List[str] = Field(..., example=["ON", "1M", "3M"])

class MarketDataResponse(BaseModel):
    """Market data response"""
    success: bool
    timestamp: datetime
    data: Dict[str, Dict]  # Security -> Fields mapping
    errors: Optional[List[str]] = None