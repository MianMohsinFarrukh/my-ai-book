"""
Health check API endpoints
"""
from fastapi import APIRouter
from pydantic import BaseModel

from ..database import check_db_health
from ..vector_db import get_vector_db_client


router = APIRouter()


class HealthStatus(BaseModel):
    status: str
    details: dict


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Health check endpoint to verify the application is running
    """
    try:
        db_healthy = await check_db_health()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_healthy = False

    try:
        vector_db_client = get_vector_db_client()
        vector_db_healthy = await vector_db_client.health_check()
    except Exception as e:
        logger.error(f"Vector database health check failed: {e}")
        vector_db_healthy = False

    all_healthy = db_healthy and vector_db_healthy

    return HealthStatus(
        status="healthy" if all_healthy else "unhealthy",
        details={
            "database": "healthy" if db_healthy else "unhealthy",
            "vector_database": "healthy" if vector_db_healthy else "unhealthy",
            "application": "running"
        }
    )


@router.get("/ready", response_model=HealthStatus)
async def readiness_check():
    """
    Readiness check endpoint to verify the application is ready to serve requests
    """
    # For now, use the same checks as health
    try:
        db_healthy = await check_db_health()
    except Exception as e:
        logger.error(f"Database readiness check failed: {e}")
        db_healthy = False

    try:
        vector_db_client = get_vector_db_client()
        vector_db_healthy = await vector_db_client.health_check()
    except Exception as e:
        logger.error(f"Vector database readiness check failed: {e}")
        vector_db_healthy = False

    all_healthy = db_healthy and vector_db_healthy

    return HealthStatus(
        status="ready" if all_healthy else "not ready",
        details={
            "database": "ready" if db_healthy else "not ready",
            "vector_database": "ready" if vector_db_healthy else "not ready",
            "application": "ready"
        }
    )