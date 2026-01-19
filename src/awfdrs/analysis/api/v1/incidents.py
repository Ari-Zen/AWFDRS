"""
Incident management API endpoints.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime

from src.awfdrs.dependencies import get_db_session
from src.awfdrs.db.repositories.incidents import IncidentRepository
from src.awfdrs.db.repositories.events import EventRepository
from src.awfdrs.analysis.incident_manager import IncidentManager
from src.awfdrs.core.enums import IncidentStatus, ErrorSeverity
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# Response schemas
class IncidentResponse(BaseModel):
    """Incident response schema."""

    id: UUID
    tenant_id: UUID
    vendor_id: Optional[UUID]
    error_signature: str
    status: IncidentStatus
    severity: ErrorSeverity
    correlated_event_ids: List[UUID]
    first_occurrence_at: datetime
    last_occurrence_at: datetime
    metadata: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventSummary(BaseModel):
    """Event summary for incident details."""

    id: UUID
    event_type: str
    occurred_at: datetime
    payload: dict

    class Config:
        from_attributes = True


class IncidentDetailsResponse(BaseModel):
    """Detailed incident response with events."""

    incident: IncidentResponse
    events: List[EventSummary]


class StatusUpdateRequest(BaseModel):
    """Request to update incident status."""

    status: IncidentStatus
    notes: Optional[str] = None


class IgnoreRequest(BaseModel):
    """Request to ignore an incident."""

    reason: str = Field(..., min_length=1)


@router.get("/incidents", response_model=List[IncidentResponse])
async def list_incidents(
    tenant_id: Optional[UUID] = Query(None),
    status: Optional[IncidentStatus] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session)
) -> List[IncidentResponse]:
    """
    List incidents with optional filters.

    Args:
        tenant_id: Filter by tenant ID
        status: Filter by status
        limit: Maximum number of results
        offset: Offset for pagination
        session: Database session

    Returns:
        List of incidents
    """
    incident_repo = IncidentRepository(session)

    if tenant_id:
        incidents = await incident_repo.list_by_tenant(tenant_id)
    else:
        # For demo purposes, list all (in production, should require tenant filter)
        from sqlalchemy import select
        from src.awfdrs.db.models.incidents import Incident
        stmt = select(Incident).order_by(Incident.created_at.desc()).limit(limit).offset(offset)
        result = await session.execute(stmt)
        incidents = list(result.scalars().all())

    # Filter by status if provided
    if status:
        incidents = [i for i in incidents if i.status == status]

    return [IncidentResponse.model_validate(i) for i in incidents[:limit]]


@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    session: AsyncSession = Depends(get_db_session)
) -> IncidentResponse:
    """
    Get incident details.

    Args:
        incident_id: Incident ID
        session: Database session

    Returns:
        Incident details
    """
    incident_repo = IncidentRepository(session)
    incident = await incident_repo.get(incident_id)

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    return IncidentResponse.model_validate(incident)


@router.get("/incidents/{incident_id}/events", response_model=List[EventSummary])
async def get_incident_events(
    incident_id: UUID,
    session: AsyncSession = Depends(get_db_session)
) -> List[EventSummary]:
    """
    Get events correlated with an incident.

    Args:
        incident_id: Incident ID
        session: Database session

    Returns:
        List of correlated events
    """
    incident_repo = IncidentRepository(session)
    event_repo = EventRepository(session)

    incident = await incident_repo.get(incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    # Fetch all correlated events
    events = []
    for event_id in incident.correlated_event_ids:
        event = await event_repo.get(event_id)
        if event:
            events.append(EventSummary.model_validate(event))

    return events


@router.patch("/incidents/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: UUID,
    request: StatusUpdateRequest,
    session: AsyncSession = Depends(get_db_session)
) -> IncidentResponse:
    """
    Update incident status (manual override).

    Args:
        incident_id: Incident ID
        request: Status update request
        session: Database session

    Returns:
        Updated incident
    """
    incident_manager = IncidentManager(session)

    if request.status == IncidentStatus.RESOLVED:
        incident = await incident_manager.resolve_incident(
            incident_id,
            request.notes or "Manual resolution"
        )
    elif request.status == IncidentStatus.ESCALATED:
        incident = await incident_manager.escalate_incident(
            incident_id,
            request.notes or "Manual escalation"
        )
    else:
        incident_repo = IncidentRepository(session)
        incident = await incident_repo.update_status(incident_id, request.status)

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    return IncidentResponse.model_validate(incident)


@router.post("/incidents/{incident_id}/ignore", response_model=IncidentResponse)
async def ignore_incident(
    incident_id: UUID,
    request: IgnoreRequest,
    session: AsyncSession = Depends(get_db_session)
) -> IncidentResponse:
    """
    Mark incident as ignored.

    Args:
        incident_id: Incident ID
        request: Ignore request with reason
        session: Database session

    Returns:
        Updated incident
    """
    incident_manager = IncidentManager(session)
    incident = await incident_manager.ignore_incident(incident_id, request.reason)

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    return IncidentResponse.model_validate(incident)
