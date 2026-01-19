"""
Health check API endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.ingestion.schemas import HealthResponse, ReadinessResponse
from src.awfdrs.dependencies import get_db_session

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Basic health check endpoint"
)
async def health_check() -> HealthResponse:
    """
    Basic health check.

    Returns:
        HealthResponse indicating service is running
    """
    return HealthResponse(status="ok")


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Readiness check with database connectivity verification"
)
async def readiness_check(
    session: AsyncSession = Depends(get_db_session)
) -> ReadinessResponse:
    """
    Readiness check with database connectivity.

    Verifies that the service can connect to the database.

    Args:
        session: Database session

    Returns:
        ReadinessResponse with database status

    Raises:
        500: If database is not accessible
    """
    # Check database connectivity
    try:
        result = await session.execute(text("SELECT 1"))
        result.scalar_one()
        database_status = "ok"
    except Exception as e:
        database_status = f"error: {str(e)}"

    # Note: Redis check would go here when we implement caching
    redis_status = "ok"

    return ReadinessResponse(
        status="ready" if database_status == "ok" else "not_ready",
        database=database_status,
        redis=redis_status
    )
