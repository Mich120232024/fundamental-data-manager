import redis.asyncio as redis
import json
import logging
from typing import Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            await self.redis.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set a key-value pair with optional TTL"""
        if not self.redis:
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if ttl:
                await self.redis.setex(key, ttl, value)
            else:
                await self.redis.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value by key"""
        if not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key"""
        if not self.redis:
            return False
        
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis:
            return False
        
        try:
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False
    
    async def set_portfolio_cache(self, user_id: str, filters: dict, data: list, ttl: int = None):
        """Cache portfolio data with filters as part of key"""
        cache_key = f"portfolio:{user_id}:{hash(str(sorted(filters.items())))}"
        ttl = ttl or settings.CACHE_TTL
        return await self.set(cache_key, data, ttl)
    
    async def get_portfolio_cache(self, user_id: str, filters: dict):
        """Get cached portfolio data"""
        cache_key = f"portfolio:{user_id}:{hash(str(sorted(filters.items())))}"
        return await self.get(cache_key)
    
    async def set_quote_cache(self, symbol: str, quote_data: dict, ttl: int = None):
        """Cache live quote data"""
        cache_key = f"quote:{symbol}"
        ttl = ttl or settings.QUOTES_CACHE_TTL
        return await self.set(cache_key, quote_data, ttl)
    
    async def get_quote_cache(self, symbol: str):
        """Get cached quote data"""
        cache_key = f"quote:{symbol}"
        return await self.get(cache_key)


# Global Redis client instance
redis_client = RedisClient()