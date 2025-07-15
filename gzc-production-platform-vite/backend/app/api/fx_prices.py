"""
FX Prices API - Fetch spot and forward rates from Azure Redis
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
import redis
import json
from datetime import datetime
import logging
from app.core.azure_keyvault import keyvault_client

logger = logging.getLogger(__name__)
router = APIRouter()

# Global Redis client
redis_client = None


def get_redis_client():
    """Get or create Redis client"""
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
            logger.info("Connected to Azure Redis for FX prices")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise HTTPException(status_code=503, detail="Redis connection failed")
    
    return redis_client


@router.get("/api/fx-prices/{currency_pair}")
async def get_fx_prices(
    currency_pair: str,
    tenor: Optional[str] = "SPOT",
    amount: Optional[int] = 1000000
):
    """
    Get FX prices for a currency pair
    
    Args:
        currency_pair: Currency pair (e.g., EUR/USD, GBP/USD)
        tenor: SPOT or forward tenor (M1, M3, M6, M12)
        amount: Notional amount for forward rates
    """
    try:
        client = get_redis_client()
        
        # Normalize currency pair
        pair = currency_pair.upper().replace('_', '/')
        
        prices = {
            "currency_pair": pair,
            "tenor": tenor,
            "amount": amount,
            "spot": {},
            "forward": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Get SPOT prices
        if tenor == "SPOT" or tenor == "ALL":
            spot_pattern = f"exchange_rate:esp:{pair}:SPOT:*"
            spot_keys = []
            
            # Scan for spot prices
            cursor = 0
            while True:
                cursor, keys = client.scan(cursor, match=spot_pattern, count=100)
                spot_keys.extend(keys)
                if cursor == 0:
                    break
            
            # Parse spot prices
            for key in spot_keys:
                try:
                    value = client.get(key)
                    if value:
                        data = json.loads(value)
                        parts = key.split(':')
                        if len(parts) >= 6:
                            bank = parts[5] if len(parts) > 5 else "UNKNOWN"
                            side = parts[4] if len(parts) > 4 else "MID"
                            
                            if bank not in prices["spot"]:
                                prices["spot"][bank] = {}
                            
                            prices["spot"][bank][side.lower()] = {
                                "rate": float(data.get("rate", 0)),
                                "timestamp": data.get("timestamp", "")
                            }
                except Exception as e:
                    logger.error(f"Error parsing spot price {key}: {e}")
        
        # Get FORWARD prices
        if tenor != "SPOT":
            forward_tenor = "M1" if tenor == "ALL" else tenor
            forward_pattern = f"exchange_rate:esp:{pair}:FORWARD:{amount}:*:{forward_tenor}:*"
            forward_keys = []
            
            # Scan for forward prices
            cursor = 0
            while True:
                cursor, keys = client.scan(cursor, match=forward_pattern, count=100)
                forward_keys.extend(keys)
                if cursor == 0:
                    break
            
            # Parse forward prices
            for key in forward_keys:
                try:
                    value = client.get(key)
                    if value:
                        data = json.loads(value)
                        parts = key.split(':')
                        if len(parts) >= 7:
                            bank = parts[7] if len(parts) > 7 else "UNKNOWN"
                            side = parts[5] if len(parts) > 5 else "MID"
                            
                            if bank not in prices["forward"]:
                                prices["forward"][bank] = {}
                            
                            prices["forward"][bank][side.lower()] = {
                                "rate": float(data.get("rate", 0)),
                                "timestamp": data.get("timestamp", ""),
                                "tenor": forward_tenor,
                                "amount": amount
                            }
                except Exception as e:
                    logger.error(f"Error parsing forward price {key}: {e}")
        
        # If no prices found, try alternative patterns
        if not prices["spot"] and not prices["forward"]:
            # Try without ESP prefix
            alt_patterns = [
                f"quote:{pair}",
                f"price:{pair}",
                f"fx:{pair}",
                f"{pair}:*"
            ]
            
            for pattern in alt_patterns:
                cursor = 0
                cursor, keys = client.scan(cursor, match=pattern, count=10)
                for key in keys:
                    try:
                        value = client.get(key)
                        if value:
                            prices["alternative_keys"] = prices.get("alternative_keys", {})
                            prices["alternative_keys"][key] = json.loads(value) if value.startswith('{') else value
                    except:
                        pass
        
        return prices
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching FX prices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch FX prices: {str(e)}")


@router.get("/api/fx-prices")
async def get_multiple_fx_prices(
    pairs: str = "EUR/USD,GBP/USD,USD/JPY,EUR/GBP,AUD/USD",
    tenor: str = "ALL"
):
    """
    Get FX prices for multiple currency pairs
    
    Args:
        pairs: Comma-separated list of currency pairs
        tenor: SPOT, M1, M3, M6, M12, or ALL
    """
    try:
        client = get_redis_client()
        
        currency_pairs = [p.strip() for p in pairs.split(',')]
        results = {}
        
        for pair in currency_pairs:
            try:
                # Get both spot and 1M forward if ALL
                if tenor == "ALL":
                    prices = await get_fx_prices(pair, "ALL", 1000000)
                else:
                    prices = await get_fx_prices(pair, tenor, 1000000)
                
                results[pair] = prices
            except Exception as e:
                logger.error(f"Error fetching prices for {pair}: {e}")
                results[pair] = {
                    "error": str(e),
                    "currency_pair": pair
                }
        
        return {
            "prices": results,
            "timestamp": datetime.now().isoformat(),
            "source": "Azure Redis Cache"
        }
        
    except Exception as e:
        logger.error(f"Error fetching multiple FX prices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch FX prices: {str(e)}")


@router.get("/api/fx-banks")
async def get_available_banks():
    """Get list of banks providing FX quotes"""
    try:
        client = get_redis_client()
        
        # Scan for all exchange rate keys
        pattern = "exchange_rate:esp:*"
        all_keys = []
        
        cursor = 0
        while True:
            cursor, keys = client.scan(cursor, match=pattern, count=100)
            all_keys.extend(keys)
            if cursor == 0 or len(all_keys) > 1000:
                break
        
        # Extract unique banks
        banks = set()
        for key in all_keys:
            parts = key.split(':')
            if len(parts) >= 7:
                bank = parts[7] if parts[3] == "FORWARD" else parts[5] if parts[3] == "SPOT" else None
                if bank:
                    banks.add(bank)
        
        return {
            "banks": sorted(list(banks)),
            "total_keys": len(all_keys),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching banks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch banks: {str(e)}")