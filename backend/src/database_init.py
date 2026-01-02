"""
Database schema initialization and migration script
"""
import asyncio
import logging
from sqlalchemy import text

from .database import init_db, get_async_session
from .models import Base


logger = logging.getLogger(__name__)


async def create_tables() -> None:
    """
    Create all database tables based on models
    """
    # Initialize the database
    await init_db()

    # Get the async session
    session_factory = get_async_session()

    # Create tables using the engine from the session factory
    async with session_factory.kw["bind"].begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created successfully")


async def drop_tables() -> None:
    """
    Drop all database tables (use with caution!)
    """
    # Initialize the database
    await init_db()

    # Get the async session
    session_factory = get_async_session()

    # Drop all tables using the engine from the session factory
    async with session_factory.kw["bind"].begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)

    logger.info("Database tables dropped successfully")


async def check_schema() -> dict:
    """
    Check the current database schema
    """
    # Initialize the database
    await init_db()

    # Get the async session
    session_factory = get_async_session()

    schema_info = {}

    async with session_factory() as session:
        # Get list of tables
        result = await session.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        ))
        tables = [row[0] for row in result.fetchall()]
        schema_info["tables"] = tables

        # Check each table structure
        table_details = {}
        for table in tables:
            result = await session.execute(text(
                f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table}'"
            ))
            columns = result.fetchall()
            table_details[table] = [{"name": col[0], "type": col[1], "nullable": col[2]} for col in columns]

        schema_info["table_details"] = table_details

    return schema_info


if __name__ == "__main__":
    # Example usage
    asyncio.run(create_tables())