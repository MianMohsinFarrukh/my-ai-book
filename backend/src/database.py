"""
Database connection setup for Neon Postgres
"""
import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from pydantic_settings import BaseSettings


logger = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    database_url: str = ""  # Will be read from environment variable
    echo: bool = False

    class Config:
        env_file = ".env"
        # Don't use env_prefix to allow DATABASE_URL to be read directly
        # env_prefix = "DB_"
        extra = "ignore"  # Ignore extra environment variables


# Global variables for engine and session
_async_engine = None
_async_session = None


def get_async_session() -> async_sessionmaker[AsyncSession]:
    """
    Get the async session factory
    """
    global _async_session
    if _async_session is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _async_session


async def init_db(settings: DatabaseSettings = None) -> None:
    """
    Initialize the database engine and session
    """
    global _async_engine, _async_session

    if settings is None:
        settings = DatabaseSettings()

    # Use NEON_DATABASE_URL as fallback if DATABASE_URL is not set
    if not settings.database_url:
        import os
        settings.database_url = os.getenv("NEON_DATABASE_URL", "sqlite+aiosqlite:///./book_chatbot.db")

    # Check if using SQLite
    is_sqlite = settings.database_url.startswith("sqlite")

    # Create the async engine
    connect_kwargs = {}
    if not is_sqlite:
        connect_kwargs = {
            "poolclass": NullPool,  # Use NullPool for serverless databases like Neon
            "connect_args": {
                "server_settings": {
                    "application_name": "book-rag-chatbot"
                }
            }
        }
    else:
        # SQLite-specific settings
        connect_kwargs = {
            "connect_args": {
                "check_same_thread": False  # Required for SQLite with async operations
            }
        }

    _async_engine = create_async_engine(
        settings.database_url,
        echo=settings.echo,
        **connect_kwargs
    )

    # Create the async session factory
    _async_session = async_sessionmaker(
        _async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    logger.info("Database initialized successfully")


async def close_db() -> None:
    """
    Close the database engine
    """
    global _async_engine
    if _async_engine:
        await _async_engine.dispose()
        logger.info("Database engine disposed")


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session with proper cleanup
    """
    session_factory = get_async_session()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


# Health check function
async def check_db_health() -> bool:
    """
    Check if the database is accessible
    """
    global _async_engine
    if _async_engine is None:
        # Try to initialize the database if not already done
        try:
            await init_db()
        except Exception as e:
            logger.error(f"Failed to initialize database for health check: {e}")
            return False

    if _async_engine is None:
        logger.warning("Database engine not initialized")
        return False

    try:
        async with _async_engine.begin() as conn:
            # Try a simple query to check connectivity (SQLite compatible)
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False