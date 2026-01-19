"""
Action management API endpoints.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime

from src.awfdrs.dependencies import get_db_session
from src.awfdrs.db.repositories.actions import ActionRepository
from src.awfdrs.actions.executor import ActionExecutor
from src.awfdrs.core.enums import ActionType, ActionStatus
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# Response schemas
class ActionResponse(BaseModel):
    """Action response schema."""

    id: UUID
    decision_id: UUID
    action_type: ActionType
    status: ActionStatus
    parameters: dict
    result: Optional[dict]
    error: Optional[str]
    is_reversible: bool
    correlation_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReverseActionRequest(BaseModel):
    """Request to reverse an action."""

    reason: Optional[str] = Field(None, description="Reason for reversal")


@router.get("/actions", response_model=List[ActionResponse])
async def list_actions(
    status: Optional[ActionStatus] = Query(None),
    action_type: Optional[ActionType] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session)
) -> List[ActionResponse]:
    """
    List actions with optional filters.

    Args:
        status: Filter by status
        action_type: Filter by action type
        limit: Maximum number of results
        offset: Offset for pagination
        session: Database session

    Returns:
        List of actions
    """
    # For demo, list all actions
    from sqlalchemy import select
    from src.awfdrs.db.models.actions import Action

    stmt = select(Action).order_by(Action.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(stmt)
    actions = list(result.scalars().all())

    # Apply filters
    if status:
        actions = [a for a in actions if a.status == status]
    if action_type:
        actions = [a for a in actions if a.action_type == action_type]

    return [ActionResponse.model_validate(a) for a in actions]


@router.get("/actions/{action_id}", response_model=ActionResponse)
async def get_action(
    action_id: UUID,
    session: AsyncSession = Depends(get_db_session)
) -> ActionResponse:
    """
    Get action details.

    Args:
        action_id: Action ID
        session: Database session

    Returns:
        Action details
    """
    action_repo = ActionRepository(session)
    action = await action_repo.get(action_id)

    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )

    return ActionResponse.model_validate(action)


@router.post("/actions/{action_id}/reverse", response_model=ActionResponse)
async def reverse_action(
    action_id: UUID,
    request: ReverseActionRequest,
    session: AsyncSession = Depends(get_db_session)
) -> ActionResponse:
    """
    Reverse a reversible action.

    Args:
        action_id: Action ID to reverse
        request: Reversal request
        session: Database session

    Returns:
        New action representing the reversal
    """
    action_repo = ActionRepository(session)
    action = await action_repo.get(action_id)

    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )

    if not action.is_reversible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action is not reversible"
        )

    if action.status != ActionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only reverse completed actions"
        )

    # Execute reversal
    executor = ActionExecutor(session)
    reversal_action = await executor.reverse_action(action)

    return ActionResponse.model_validate(reversal_action)


@router.get("/incidents/{incident_id}/actions", response_model=List[ActionResponse])
async def get_incident_actions(
    incident_id: UUID,
    session: AsyncSession = Depends(get_db_session)
) -> List[ActionResponse]:
    """
    Get all actions for an incident.

    Args:
        incident_id: Incident ID
        session: Database session

    Returns:
        List of actions
    """
    action_repo = ActionRepository(session)
    actions = await action_repo.list_by_incident(incident_id)

    return [ActionResponse.model_validate(a) for a in actions]
