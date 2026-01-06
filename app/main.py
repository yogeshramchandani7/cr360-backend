"""
CR360 Backend - FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.utils.logger import configure_logging, get_logger

# Configure logging
configure_logging(settings.LOG_LEVEL)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting CR360 Backend", version=settings.APP_VERSION)

    # Load YAML context at startup
    try:
        from app.llm.context_loader import get_context_loader
        context_loader = get_context_loader()
        context_loader.load()
        dimensions = context_loader.get_dimensions()
        logger.info(
            "Loaded semantic model",
            metrics_count=len(context_loader.get_metrics()),
            dimensions_count=len(dimensions) if dimensions else 0
        )
    except Exception as e:
        logger.error("Failed to load semantic model", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("Shutting down CR360 Backend")

    # Close database connections
    try:
        from app.database.client import get_database_client
        db_client = get_database_client()
        db_client.close()
    except Exception as e:
        logger.error("Error closing database connection", error=str(e))


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CR360 GenAI-powered Credit Risk Analytics Backend",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api.routes import chat_router, health_router

app.include_router(health_router)
app.include_router(chat_router)
