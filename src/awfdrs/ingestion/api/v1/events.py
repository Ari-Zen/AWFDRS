"""
Event ingestion API endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.ingestion.schemas import WorkflowEventV1, EventResponse
from src.awfdrs.ingestion.service import IngestionService
from src.awfdrs.dependencies import get_db_session, get_correlation_id

router = APIRouter()


@router.post(
    "/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit workflow event",
    description="Submit a workflow event for ingestion and processing"
)
async def submit_event(
    event: WorkflowEventV1,
    session: AsyncSession = Depends(get_db_session),
    correlation_id: str = Depends(get_correlation_id)
) -> EventResponse:
    """
    Submit a workflow event.

    Args:
        event: Event to submit
        session: Database session
        correlation_id: Request correlation ID

    Returns:
        EventResponse with event ID

    Raises:
        400: Invalid request
        403: Workflow is kill-switched
        404: Tenant or workflow not found
        409: Duplicate idempotency key
        422: Validation error
    """
    service = IngestionService(session, correlation_id)
    return await service.ingest_event(event)
