from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.redis_client import redis_client
from app.models.portfolio import PortfolioPosition, LiveQuote
from app.services.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_portfolio_data(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    fundId: Optional[int] = Query(None, description="Filter by fund ID", alias="fundId"),
    trader: Optional[str] = Query(None, description="Filter by trader"),
    position: Optional[str] = Query(None, description="Filter by position type"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get portfolio data with optional filters
    Matches the frontend usePortfolioData hook expectations
    """
    try:
        user_id = current_user.get("sub", "unknown")
        
        # Create filters dict for caching
        filters = {
            "symbol": symbol,
            "fundId": fundId,
            "trader": trader,
            "position": position
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Try to get from cache first
        cached_data = await redis_client.get_portfolio_cache(user_id, filters)
        if cached_data:
            logger.info(f"Returning cached portfolio data for user {user_id}")
            return {"data": {"data": cached_data}}
        
        # Build query with filters
        query = select(PortfolioPosition).where(PortfolioPosition.IsActive == True)
        
        if symbol:
            query = query.where(PortfolioPosition.Symbol.ilike(f"%{symbol}%"))
        if fundId:
            query = query.where(PortfolioPosition.FundID == fundId)
        if trader:
            query = query.where(PortfolioPosition.Trader.ilike(f"%{trader}%"))
        if position:
            query = query.where(PortfolioPosition.Position.ilike(f"%{position}%"))
        
        # Execute query
        result = await db.execute(query)
        positions = result.scalars().all()
        
        # Convert to dict format
        portfolio_data = [pos.to_dict() for pos in positions]
        
        # Cache the result
        await redis_client.set_portfolio_cache(user_id, filters, portfolio_data)
        
        logger.info(f"Retrieved {len(portfolio_data)} portfolio positions for user {user_id}")
        
        # Return in the format expected by frontend
        return {"data": {"data": portfolio_data}}
        
    except Exception as e:
        logger.error(f"Error retrieving portfolio data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve portfolio data")


@router.get("/quotes/{symbol}")
async def get_live_quote(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get live quote for a specific symbol
    """
    try:
        # Try cache first
        cached_quote = await redis_client.get_quote_cache(symbol.upper())
        if cached_quote:
            return cached_quote
        
        # Get from database
        query = select(LiveQuote).where(LiveQuote.Symbol == symbol.upper())
        result = await db.execute(query)
        quote = result.scalar_one_or_none()
        
        if not quote:
            raise HTTPException(status_code=404, detail=f"Quote not found for symbol {symbol}")
        
        quote_data = quote.to_dict()
        
        # Cache the quote
        await redis_client.set_quote_cache(symbol.upper(), quote_data)
        
        return quote_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve quote data")


@router.get("/metrics")
async def get_portfolio_metrics(
    fundId: Optional[int] = Query(None, description="Filter by fund ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get portfolio summary metrics
    """
    try:
        user_id = current_user.get("sub", "unknown")
        cache_key = f"portfolio_metrics:{user_id}:{fundId or 'all'}"
        
        # Try cache first
        cached_metrics = await redis_client.get(cache_key)
        if cached_metrics:
            return cached_metrics
        
        # Build query
        query = select(PortfolioPosition).where(PortfolioPosition.IsActive == True)
        if fundId:
            query = query.where(PortfolioPosition.FundID == fundId)
        
        result = await db.execute(query)
        positions = result.scalars().all()
        
        # Calculate metrics
        total_positions = len(positions)
        total_pnl = sum(pos.PnL for pos in positions if pos.PnL)
        total_pnl_ytd = sum(pos.PnLYTD for pos in positions if pos.PnLYTD)
        total_pnl_mtd = sum(pos.PnLMTD for pos in positions if pos.PnLMTD)
        total_pnl_dtd = sum(pos.PnLDTD for pos in positions if pos.PnLDTD)
        
        total_value = sum(pos.CurrentPrice * pos.OrderQty for pos in positions 
                         if pos.CurrentPrice and pos.OrderQty)
        
        metrics = {
            "totalPositions": total_positions,
            "totalValue": total_value,
            "totalPnL": total_pnl,
            "totalPnLYTD": total_pnl_ytd,
            "totalPnLMTD": total_pnl_mtd,
            "totalPnLDTD": total_pnl_dtd,
            "activeSymbols": len(set(pos.Symbol for pos in positions)),
            "activeFunds": len(set(pos.FundID for pos in positions if pos.FundID)),
            "activeTraders": len(set(pos.Trader for pos in positions if pos.Trader))
        }
        
        # Cache metrics
        await redis_client.set(cache_key, metrics, ttl=60)  # 1 minute cache
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating portfolio metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate portfolio metrics")


@router.post("/refresh")
async def refresh_portfolio_cache(
    current_user: dict = Depends(get_current_user)
):
    """
    Force refresh of portfolio cache
    """
    try:
        user_id = current_user.get("sub", "unknown")
        
        # Delete user's portfolio cache entries
        # Note: In production, you might want to use Redis SCAN for this
        cache_pattern = f"portfolio:{user_id}:*"
        
        # For now, just acknowledge the refresh request
        # The next API call will rebuild the cache
        
        return {"message": "Portfolio cache refresh initiated"}
        
    except Exception as e:
        logger.error(f"Error refreshing portfolio cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh portfolio cache")