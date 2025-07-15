import socketio
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI
from typing import Dict, Any

from app.websockets.portfolio_stream import portfolio_stream_manager
from app.websockets.fx_price_stream import fx_price_stream_manager
from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)


# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://localhost:3000", "http://localhost:3200"],
    logger=False,
    engineio_logger=False
)

# Create Socket.IO app
socket_app = socketio.ASGIApp(sio)


class WebSocketManager:
    def __init__(self):
        self.sio = sio
        self.connected_clients: Dict[str, str] = {}  # session_id -> user_id
    
    async def startup(self):
        """Initialize WebSocket services on startup"""
        try:
            # Connect to Redis
            await redis_client.connect()
            
            # Start portfolio streaming
            await portfolio_stream_manager.start_streaming()
            
            # Start FX price streaming
            await fx_price_stream_manager.start_streaming()
            
            logger.info("WebSocket services started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket services: {e}")
    
    async def shutdown(self):
        """Cleanup WebSocket services on shutdown"""
        try:
            # Stop portfolio streaming
            await portfolio_stream_manager.stop_streaming()
            
            # Stop FX price streaming
            await fx_price_stream_manager.stop_streaming()
            
            # Disconnect from Redis
            await redis_client.disconnect()
            
            logger.info("WebSocket services shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during WebSocket shutdown: {e}")


# Global manager instance
manager = WebSocketManager()


@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    try:
        # Extract token from auth
        token = auth.get("token") if auth else None
        if not token:
            logger.warning(f"Connection rejected for {sid}: No authentication token")
            return False
        
        # Authenticate with portfolio stream manager
        # For Socket.IO, we'll store the token and validate on message
        await sio.save_session(sid, {"token": token})
        
        logger.info(f"Socket.IO client connected: {sid}")
        return True
        
    except Exception as e:
        logger.error(f"Connection error for {sid}: {e}")
        return False


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    try:
        # Unsubscribe from FX prices
        await fx_price_stream_manager.unsubscribe_client(sid)
        
        if sid in manager.connected_clients:
            user_id = manager.connected_clients.pop(sid)
            logger.info(f"Socket.IO client disconnected: {sid} (user: {user_id})")
        else:
            logger.info(f"Socket.IO client disconnected: {sid}")
            
    except Exception as e:
        logger.error(f"Disconnect error for {sid}: {e}")


@sio.event
async def subscribe_portfolio(sid, data):
    """Subscribe to portfolio updates"""
    try:
        session = await sio.get_session(sid)
        token = session.get("token")
        
        if not token:
            await sio.emit("error", {"message": "Not authenticated"}, room=sid)
            return
        
        # Validate token and get user info
        from app.services.auth import MSALAuthenticator
        authenticator = MSALAuthenticator()
        user_data = authenticator.verify_token(token)
        
        if not user_data:
            await sio.emit("error", {"message": "Invalid token"}, room=sid)
            return
        
        user_id = user_data.get("sub", "unknown")
        manager.connected_clients[sid] = user_id
        
        # Subscribe to symbols
        symbols = data.get("symbols", [])
        if symbols:
            # For now, just acknowledge subscription
            await sio.emit("portfolio_subscribed", {
                "symbols": symbols,
                "user_id": user_id
            }, room=sid)
            
            logger.info(f"User {user_id} subscribed to portfolio symbols: {symbols}")
        
    except Exception as e:
        logger.error(f"Portfolio subscription error for {sid}: {e}")
        await sio.emit("error", {"message": "Subscription failed"}, room=sid)


@sio.event
async def subscribe_quotes(sid, data):
    """Subscribe to live quote updates"""
    try:
        session = await sio.get_session(sid)
        token = session.get("token")
        
        if not token:
            await sio.emit("error", {"message": "Not authenticated"}, room=sid)
            return
        
        symbols = data.get("symbols", [])
        if not symbols:
            await sio.emit("error", {"message": "No symbols provided"}, room=sid)
            return
        
        # Acknowledge subscription
        await sio.emit("quotes_subscribed", {
            "symbols": symbols,
            "timestamp": asyncio.get_event_loop().time()
        }, room=sid)
        
        logger.info(f"Client {sid} subscribed to quotes: {symbols}")
        
    except Exception as e:
        logger.error(f"Quote subscription error for {sid}: {e}")
        await sio.emit("error", {"message": "Subscription failed"}, room=sid)


@sio.event
async def subscribe_fx_prices(sid, data):
    """Subscribe to FX price updates"""
    try:
        session = await sio.get_session(sid)
        token = session.get("token")
        
        if not token:
            await sio.emit("error", {"message": "Not authenticated"}, room=sid)
            return
        
        currency_pairs = data.get("pairs", [])
        if not currency_pairs:
            await sio.emit("error", {"message": "No currency pairs provided"}, room=sid)
            return
        
        # Subscribe to FX price stream
        await fx_price_stream_manager.subscribe_client(sid, currency_pairs)
        
        # Acknowledge subscription
        await sio.emit("fx_prices_subscribed", {
            "pairs": currency_pairs,
            "refresh_rate": fx_price_stream_manager.stream_interval,
            "timestamp": datetime.now().isoformat()
        }, room=sid)
        
        logger.info(f"Client {sid} subscribed to FX prices: {currency_pairs}")
        
    except Exception as e:
        logger.error(f"FX price subscription error for {sid}: {e}")
        await sio.emit("error", {"message": "FX subscription failed"}, room=sid)


@sio.event
async def unsubscribe_fx_prices(sid):
    """Unsubscribe from FX price updates"""
    try:
        await fx_price_stream_manager.unsubscribe_client(sid)
        await sio.emit("fx_prices_unsubscribed", {
            "timestamp": datetime.now().isoformat()
        }, room=sid)
        
        logger.info(f"Client {sid} unsubscribed from FX prices")
        
    except Exception as e:
        logger.error(f"FX price unsubscription error for {sid}: {e}")


@sio.event
async def ping(sid):
    """Handle ping for health check"""
    try:
        await sio.emit("pong", {
            "timestamp": asyncio.get_event_loop().time()
        }, room=sid)
        
    except Exception as e:
        logger.error(f"Ping error for {sid}: {e}")


# Utility function to broadcast to all connected clients
async def broadcast_to_all(event: str, data: Dict[str, Any]):
    """Broadcast message to all connected clients"""
    try:
        await sio.emit(event, data)
        logger.debug(f"Broadcasted {event} to all clients")
        
    except Exception as e:
        logger.error(f"Broadcast error: {e}")


# Utility function to send to specific user
async def send_to_user(user_id: str, event: str, data: Dict[str, Any]):
    """Send message to specific user"""
    try:
        # Find sessions for this user
        user_sessions = [sid for sid, uid in manager.connected_clients.items() if uid == user_id]
        
        for sid in user_sessions:
            await sio.emit(event, data, room=sid)
        
        if user_sessions:
            logger.debug(f"Sent {event} to user {user_id} ({len(user_sessions)} sessions)")
        
    except Exception as e:
        logger.error(f"Send to user error: {e}")