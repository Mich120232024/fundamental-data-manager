from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.core.database import init_db, close_db, initialize_database
from app.core.redis_client import redis_client
from app.core.azure_keyvault import keyvault_client
from app.api import health, auth, layouts, components, portfolio, fx_prices
from app.routers import fx_forward_trades
from app.websockets import manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting up GZC Production Platform API")
    
    try:
        # Load secrets from Azure Key Vault
        logger.info("Loading secrets from Azure Key Vault...")
        database_url = keyvault_client.get_secret("postgres-connection-string")
        redis_url = keyvault_client.get_secret("redis-connection-string")
        
        if not database_url or not redis_url:
            raise Exception("Failed to load required secrets from Key Vault")
        
        # Update settings with Key Vault secrets
        settings.DATABASE_URL = database_url
        settings.REDIS_URL = redis_url
        logger.info("Secrets loaded successfully from Key Vault")
        
        # Initialize database engine with the loaded connection string
        initialize_database(database_url)
        
        # Initialize database tables
        await init_db()
        logger.info("Database initialized")
        
        # Connect to Redis
        await redis_client.connect()
        logger.info("Redis connected")
        
        # Start WebSocket manager
        await manager.startup()
        logger.info("WebSocket services started")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down GZC Production Platform API")
    
    try:
        # Stop WebSocket services
        await manager.shutdown()
        
        # Close Redis connection
        await redis_client.disconnect()
        
        # Close database connections
        await close_db()
        
        logger.info("Shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Create FastAPI app
app = FastAPI(
    title="GZC Production Platform API",
    description="Production-ready trading platform API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(layouts.router, prefix="/api/layouts", tags=["layouts"])
app.include_router(components.router, prefix="/api/components", tags=["components"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(fx_forward_trades.router, tags=["fx-forward-trades"])
app.include_router(fx_prices.router, tags=["fx-prices"])

# WebSocket endpoint
app.mount("/ws", manager.socket_app)

@app.get("/")
async def root():
    return {
        "message": "GZC Production Platform API",
        "version": "1.0.0",
        "status": "operational"
    }