import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.redis_client import redis_client
from app.models.portfolio import LiveQuote, PortfolioPosition
from app.services.auth import MSALAuthenticator

logger = logging.getLogger(__name__)


class PortfolioStreamManager:
    def __init__(self):
        # Active WebSocket connections: user_id -> {websockets}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Subscribed symbols: user_id -> {symbols}
        self.user_subscriptions: Dict[str, Set[str]] = {}
        self.authenticator = MSALAuthenticator()
        self._streaming_task = None
        
    async def connect(self, websocket: WebSocket, token: str):
        """
        Handle new WebSocket connection with authentication
        """
        try:
            # Verify authentication token
            user_data = self.authenticator.verify_token(token)
            if not user_data:
                await websocket.close(code=1008, reason="Invalid authentication")
                return None
            
            user_id = user_data.get("sub", "unknown")
            
            # Accept connection
            await websocket.accept()
            
            # Add to active connections
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
            
            # Initialize subscriptions
            if user_id not in self.user_subscriptions:
                self.user_subscriptions[user_id] = set()
            
            logger.info(f"WebSocket connected for user: {user_id}")
            
            # Send welcome message
            await self.send_to_user(user_id, {
                "type": "connection",
                "status": "connected",
                "user_id": user_id,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            return user_id
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            await websocket.close(code=1011, reason="Connection failed")
            return None
    
    async def disconnect(self, websocket: WebSocket, user_id: str = None):
        """
        Handle WebSocket disconnection
        """
        try:
            if user_id and user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                
                # Remove user if no active connections
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    if user_id in self.user_subscriptions:
                        del self.user_subscriptions[user_id]
                    
                logger.info(f"WebSocket disconnected for user: {user_id}")
            
        except Exception as e:
            logger.error(f"WebSocket disconnect error: {e}")
    
    async def send_to_user(self, user_id: str, data: dict):
        """
        Send data to all WebSocket connections for a user
        """
        if user_id not in self.active_connections:
            return
        
        message = json.dumps(data)
        disconnected = set()
        
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to websocket: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected WebSockets
        for websocket in disconnected:
            self.active_connections[user_id].discard(websocket)
    
    async def handle_message(self, websocket: WebSocket, user_id: str, data: dict):
        """
        Handle incoming WebSocket messages
        """
        try:
            message_type = data.get("type")
            
            if message_type == "subscribe":
                # Subscribe to symbol updates
                symbols = data.get("symbols", [])
                if isinstance(symbols, str):
                    symbols = [symbols]
                
                self.user_subscriptions[user_id].update(symbols)
                
                await self.send_to_user(user_id, {
                    "type": "subscription",
                    "status": "subscribed",
                    "symbols": list(self.user_subscriptions[user_id])
                })
                
            elif message_type == "unsubscribe":
                # Unsubscribe from symbol updates
                symbols = data.get("symbols", [])
                if isinstance(symbols, str):
                    symbols = [symbols]
                
                for symbol in symbols:
                    self.user_subscriptions[user_id].discard(symbol)
                
                await self.send_to_user(user_id, {
                    "type": "subscription",
                    "status": "unsubscribed",
                    "symbols": list(self.user_subscriptions[user_id])
                })
                
            elif message_type == "ping":
                # Health check
                await self.send_to_user(user_id, {
                    "type": "pong",
                    "timestamp": asyncio.get_event_loop().time()
                })
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def broadcast_quote_update(self, symbol: str, quote_data: dict):
        """
        Broadcast quote updates to subscribed users
        """
        try:
            message = {
                "type": "quote_update",
                "symbol": symbol,
                "data": quote_data,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Send to users subscribed to this symbol
            for user_id, subscriptions in self.user_subscriptions.items():
                if symbol in subscriptions:
                    await self.send_to_user(user_id, message)
                    
        except Exception as e:
            logger.error(f"Error broadcasting quote update: {e}")
    
    async def broadcast_portfolio_update(self, user_id: str, portfolio_data: dict):
        """
        Broadcast portfolio updates to specific user
        """
        try:
            message = {
                "type": "portfolio_update",
                "data": portfolio_data,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await self.send_to_user(user_id, message)
            
        except Exception as e:
            logger.error(f"Error broadcasting portfolio update: {e}")
    
    async def start_streaming(self):
        """
        Start background streaming task
        """
        if self._streaming_task and not self._streaming_task.done():
            return
        
        self._streaming_task = asyncio.create_task(self._stream_quotes())
        logger.info("Portfolio streaming service started")
    
    async def stop_streaming(self):
        """
        Stop background streaming task
        """
        if self._streaming_task and not self._streaming_task.done():
            self._streaming_task.cancel()
            try:
                await self._streaming_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Portfolio streaming service stopped")
    
    async def _stream_quotes(self):
        """
        Background task to stream live quotes
        """
        while True:
            try:
                # Get all subscribed symbols
                all_symbols = set()
                for subscriptions in self.user_subscriptions.values():
                    all_symbols.update(subscriptions)
                
                if not all_symbols:
                    await asyncio.sleep(1)
                    continue
                
                # Fetch quotes from database
                async with AsyncSessionLocal() as db:
                    query = select(LiveQuote).where(LiveQuote.Symbol.in_(all_symbols))
                    result = await db.execute(query)
                    quotes = result.scalars().all()
                    
                    # Broadcast updates
                    for quote in quotes:
                        quote_data = quote.to_dict()
                        
                        # Cache the quote
                        await redis_client.set_quote_cache(quote.Symbol, quote_data)
                        
                        # Broadcast to subscribed users
                        await self.broadcast_quote_update(quote.Symbol, quote_data)
                
                # Stream every 1 second
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in quote streaming: {e}")
                await asyncio.sleep(5)  # Wait before retrying


# Global stream manager
portfolio_stream_manager = PortfolioStreamManager()