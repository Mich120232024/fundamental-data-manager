"""
FX Price WebSocket Streaming from Redis
Real-time streaming of spot and forward FX prices
"""
import asyncio
import json
import logging
from typing import Dict, Set, List, Any
from datetime import datetime
import redis

from app.core.azure_keyvault import keyvault_client

logger = logging.getLogger(__name__)


class FXPriceStreamManager:
    """Manages real-time FX price streaming from Redis to WebSocket clients"""
    
    def __init__(self):
        self.redis_client = None
        self.streaming_task = None
        self.subscribed_pairs: Dict[str, Set[str]] = {}  # pair -> set of session_ids
        self.session_pairs: Dict[str, Set[str]] = {}  # session_id -> set of pairs
        self.is_streaming = False
        self.stream_interval = 1.0  # 1 second refresh rate
        
    async def connect_redis(self):
        """Connect to Azure Redis"""
        try:
            if self.redis_client is None:
                # Get Redis connection from Key Vault
                redis_secret = keyvault_client.get_secret('redis-connection-string')
                if not redis_secret:
                    raise Exception("No Redis connection string found")
                
                # Parse Redis URL
                from urllib.parse import urlparse
                parsed = urlparse(redis_secret)
                
                self.redis_client = redis.Redis(
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
                self.redis_client.ping()
                logger.info("Connected to Azure Redis for FX price streaming")
                
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            raise
    
    async def start_streaming(self):
        """Start the price streaming task"""
        if not self.is_streaming:
            await self.connect_redis()
            self.is_streaming = True
            self.streaming_task = asyncio.create_task(self._stream_prices())
            logger.info("FX price streaming started")
    
    async def stop_streaming(self):
        """Stop the price streaming task"""
        self.is_streaming = False
        if self.streaming_task:
            self.streaming_task.cancel()
            try:
                await self.streaming_task
            except asyncio.CancelledError:
                pass
        logger.info("FX price streaming stopped")
    
    async def subscribe_client(self, session_id: str, currency_pairs: List[str]):
        """Subscribe a client to currency pair updates"""
        # Initialize session
        if session_id not in self.session_pairs:
            self.session_pairs[session_id] = set()
        
        # Subscribe to each pair
        for pair in currency_pairs:
            pair = pair.upper()
            if pair not in self.subscribed_pairs:
                self.subscribed_pairs[pair] = set()
            
            self.subscribed_pairs[pair].add(session_id)
            self.session_pairs[session_id].add(pair)
        
        logger.info(f"Client {session_id} subscribed to pairs: {currency_pairs}")
        
        # Send initial prices
        await self._send_initial_prices(session_id, currency_pairs)
    
    async def unsubscribe_client(self, session_id: str):
        """Unsubscribe a client from all updates"""
        if session_id in self.session_pairs:
            # Remove from all pair subscriptions
            for pair in self.session_pairs[session_id]:
                if pair in self.subscribed_pairs:
                    self.subscribed_pairs[pair].discard(session_id)
                    if not self.subscribed_pairs[pair]:
                        del self.subscribed_pairs[pair]
            
            # Remove session
            del self.session_pairs[session_id]
            logger.info(f"Client {session_id} unsubscribed from all pairs")
    
    async def _stream_prices(self):
        """Main streaming loop"""
        while self.is_streaming:
            try:
                if self.subscribed_pairs and self.redis_client:
                    # Fetch prices for all subscribed pairs
                    price_updates = await self._fetch_current_prices()
                    
                    # Send updates to subscribed clients
                    if price_updates:
                        await self._broadcast_price_updates(price_updates)
                
                # Wait before next update
                await asyncio.sleep(self.stream_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in price streaming loop: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def _fetch_current_prices(self) -> Dict[str, Any]:
        """Fetch current prices from Redis for all subscribed pairs"""
        price_updates = {}
        
        try:
            for pair in self.subscribed_pairs.keys():
                # Fetch spot prices
                spot_prices = await self._fetch_spot_prices(pair)
                
                # Fetch forward prices (1M)
                forward_prices = await self._fetch_forward_prices(pair, "M1", 1000000)
                
                if spot_prices or forward_prices:
                    price_updates[pair] = {
                        "pair": pair,
                        "spot": spot_prices,
                        "forward": forward_prices,
                        "timestamp": datetime.now().isoformat()
                    }
        
        except Exception as e:
            logger.error(f"Error fetching prices: {e}")
        
        return price_updates
    
    async def _fetch_spot_prices(self, pair: str) -> Dict[str, Any]:
        """Fetch spot prices for a currency pair"""
        spot_prices = {}
        
        try:
            # Pattern for ESP spot prices
            pattern = f"exchange_rate:esp:{pair}:SPOT:*"
            
            # Scan for matching keys
            cursor = 0
            keys = []
            while True:
                cursor, batch = self.redis_client.scan(cursor, match=pattern, count=50)
                keys.extend(batch)
                if cursor == 0 or len(keys) > 100:
                    break
            
            # Get best bid/ask
            best_bid = None
            best_ask = None
            
            for key in keys:
                try:
                    value = self.redis_client.get(key)
                    if value:
                        data = json.loads(value)
                        rate = float(data.get("rate", 0))
                        
                        # Parse key to get bid/ask
                        parts = key.split(':')
                        if len(parts) >= 5:
                            side = parts[4]
                            bank = parts[5] if len(parts) > 5 else "UNKNOWN"
                            
                            if side == "Bid":
                                if best_bid is None or rate > best_bid['rate']:
                                    best_bid = {
                                        'rate': rate,
                                        'bank': bank,
                                        'timestamp': data.get('timestamp')
                                    }
                            elif side == "Ask":
                                if best_ask is None or rate < best_ask['rate']:
                                    best_ask = {
                                        'rate': rate,
                                        'bank': bank,
                                        'timestamp': data.get('timestamp')
                                    }
                except:
                    continue
            
            if best_bid:
                spot_prices['bid'] = best_bid
            if best_ask:
                spot_prices['ask'] = best_ask
                
        except Exception as e:
            logger.error(f"Error fetching spot prices for {pair}: {e}")
        
        return spot_prices
    
    async def _fetch_forward_prices(self, pair: str, tenor: str, amount: int) -> Dict[str, Any]:
        """Fetch forward prices for a currency pair"""
        forward_prices = {}
        
        try:
            # Pattern for ESP forward prices
            pattern = f"exchange_rate:esp:{pair}:FORWARD:{amount}:*:{tenor}:*"
            
            # Scan for matching keys
            cursor = 0
            keys = []
            while True:
                cursor, batch = self.redis_client.scan(cursor, match=pattern, count=50)
                keys.extend(batch)
                if cursor == 0 or len(keys) > 100:
                    break
            
            # Get best bid/ask
            best_bid = None
            best_ask = None
            
            for key in keys:
                try:
                    value = self.redis_client.get(key)
                    if value:
                        data = json.loads(value)
                        rate = float(data.get("rate", 0))
                        
                        # Parse key to get bid/ask
                        parts = key.split(':')
                        if len(parts) >= 7:
                            side = parts[5]
                            bank = parts[7] if len(parts) > 7 else "UNKNOWN"
                            
                            if side == "Bid":
                                if best_bid is None or rate > best_bid['rate']:
                                    best_bid = {
                                        'rate': rate,
                                        'bank': bank,
                                        'timestamp': data.get('timestamp'),
                                        'tenor': tenor,
                                        'amount': amount
                                    }
                            elif side == "Ask":
                                if best_ask is None or rate < best_ask['rate']:
                                    best_ask = {
                                        'rate': rate,
                                        'bank': bank,
                                        'timestamp': data.get('timestamp'),
                                        'tenor': tenor,
                                        'amount': amount
                                    }
                except:
                    continue
            
            if best_bid:
                forward_prices['bid'] = best_bid
            if best_ask:
                forward_prices['ask'] = best_ask
                
        except Exception as e:
            logger.error(f"Error fetching forward prices for {pair}: {e}")
        
        return forward_prices
    
    async def _send_initial_prices(self, session_id: str, currency_pairs: List[str]):
        """Send initial prices to a newly subscribed client"""
        try:
            initial_prices = {}
            
            for pair in currency_pairs:
                pair = pair.upper()
                spot_prices = await self._fetch_spot_prices(pair)
                forward_prices = await self._fetch_forward_prices(pair, "M1", 1000000)
                
                if spot_prices or forward_prices:
                    initial_prices[pair] = {
                        "pair": pair,
                        "spot": spot_prices,
                        "forward": forward_prices,
                        "timestamp": datetime.now().isoformat()
                    }
            
            if initial_prices:
                # Import here to avoid circular dependency
                from app.websockets.manager import sio
                
                await sio.emit("fx_prices_initial", {
                    "prices": initial_prices,
                    "timestamp": datetime.now().isoformat()
                }, room=session_id)
                
        except Exception as e:
            logger.error(f"Error sending initial prices: {e}")
    
    async def _broadcast_price_updates(self, price_updates: Dict[str, Any]):
        """Broadcast price updates to subscribed clients"""
        try:
            # Import here to avoid circular dependency
            from app.websockets.manager import sio
            
            # Send updates to clients subscribed to each pair
            for pair, price_data in price_updates.items():
                if pair in self.subscribed_pairs:
                    sessions = list(self.subscribed_pairs[pair])
                    
                    for session_id in sessions:
                        try:
                            await sio.emit("fx_price_update", {
                                "pair": pair,
                                "data": price_data,
                                "timestamp": datetime.now().isoformat()
                            }, room=session_id)
                        except Exception as e:
                            logger.error(f"Error sending to session {session_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error broadcasting price updates: {e}")


# Global instance
fx_price_stream_manager = FXPriceStreamManager()