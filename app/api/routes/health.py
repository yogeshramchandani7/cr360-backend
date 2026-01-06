"""
Health Check API Routes

Endpoints for monitoring service health
"""

from fastapi import APIRouter, status
from app.api.schemas import HealthResponse
from app.config import settings
from app.database.client import get_database_client
from app.llm.context_loader import get_context_loader
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check the health of the service and its dependencies"
)
async def health_check() -> HealthResponse:
    """
    Check health of the service and its components

    Returns:
        HealthResponse with status of all components
    """
    logger.info("health_check_requested")

    components = {}

    # Check database connection
    try:
        db_client = get_database_client()
        await db_client.test_connection()
        components['database'] = 'healthy'
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        components['database'] = 'unhealthy'

    # Check context loader
    try:
        context_loader = get_context_loader()
        if not context_loader._loaded:
            context_loader.load()
        components['context_loader'] = 'healthy'
    except Exception as e:
        logger.error("context_loader_health_check_failed", error=str(e))
        components['context_loader'] = 'unhealthy'

    # Check LLM (just verify configuration exists)
    try:
        if settings.GOOGLE_API_KEY:
            components['llm'] = 'configured'
        else:
            components['llm'] = 'not_configured'
    except Exception:
        components['llm'] = 'error'

    # Overall status
    overall_status = 'healthy' if all(
        v in ['healthy', 'configured'] for v in components.values()
    ) else 'unhealthy'

    response = HealthResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        components=components
    )

    logger.info(
        "health_check_completed",
        status=overall_status,
        components=components
    )

    return response


@router.get(
    "/",
    summary="Root endpoint",
    description="Simple endpoint to verify service is running"
)
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running"
    }
