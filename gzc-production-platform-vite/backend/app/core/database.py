from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global variables for engine and session
engine: Optional[object] = None
AsyncSessionLocal: Optional[object] = None

# Base class for models
Base = declarative_base()


def initialize_database(database_url: str):
    """Initialize database engine and session factory"""
    global engine, AsyncSessionLocal
    
    # Create async engine
    engine = create_async_engine(
        database_url,
        poolclass=NullPool,  # Better for Azure PostgreSQL
        echo=False,  # Set to True for SQL debugging
        future=True
    )
    
    # Create async session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    logger.info("Database engine and session factory initialized")


async def get_db():
    """Dependency to get database session"""
    if not AsyncSessionLocal:
        raise RuntimeError("Database not initialized. Call initialize_database first.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    if not engine:
        raise RuntimeError("Database engine not initialized. Call initialize_database first.")
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def close_db():
    """Close database connections"""
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")