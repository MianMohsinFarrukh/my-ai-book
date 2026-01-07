from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from .api.health import router as health_router
from .api.chat import router as chat_router
from .api.ingest import router as ingest_router
from .api.query import router as query_router  # New router for query functionality

# Import middleware
from .middleware.logging_middleware import setup_logging_middleware

# Import services
from .database import init_db, close_db
from .vector_db import init_vector_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for application startup and shutdown
    """
    logger.info("Starting up Book RAG Chatbot application...")
    # Initialize services here
    try:
        await init_db()
        await init_vector_db()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    yield
    # Cleanup services here
    await close_db()
    logger.info("Shutting down Book RAG Chatbot application...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    app = FastAPI(
        title="Book RAG Chatbot API",
        description="API for RAG-based chatbot that answers questions about book content",
        version="0.1.0",
        lifespan=lifespan
    )

    # Add logging middleware first
    app = setup_logging_middleware(app)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
    app.include_router(ingest_router, prefix="/api/v1", tags=["ingest"])
    app.include_router(query_router, prefix="/api/v1", tags=["query"])  # Add query router

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)