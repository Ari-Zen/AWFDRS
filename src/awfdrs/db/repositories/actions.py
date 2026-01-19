"""
Action repository for action execution records.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.actions import Action
from src.awfdrs.core.enums import ActionType, ActionStatus


class ActionRepository:
    """
    Repository for action operations.

    Note: Actions are immutable once created, but status can be updated.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository."""
        self.session = session

    async def create_action(
        self,
        decision_id: UUID,
        action_type: ActionType,
        parameters: Optional[dict] = None,
        is_reversible: bool = False,
        correlation_id: str = ""
    ) -> Action:
        """
        Create a new action record.

        Args:
            decision_id: Associated decision ID
            action_type: Type of action to execute
            parameters: Action parameters
            is_reversible: Whether action can be reversed
            correlation_id: Request correlation ID

        Returns:
            Created action
        """
        action = Action(
            decision_id=decision_id,
            action_type=action_type,
            status=ActionStatus.PENDING,
            parameters=parameters or {},
            is_reversible=is_reversible,
            correlation_id=correlation_id,
            created_at=datetime.utcnow()
        )

        self.session.add(action)
        await self.session.commit()
        await self.session.refresh(action)
        return action

    async def get(self, action_id: UUID) -> Optional[Action]:
        """
        Get action by ID.

        Args:
            action_id: Action ID

        Returns:
            Action if found, None otherwise
        """
        stmt = select(Action).where(Action.id == action_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        action_id: UUID,
        status: ActionStatus,
        result: Optional[dict] = None,
        error: Optional[str] = None
    ) -> Optional[Action]:
        """
        Update action status.

        Args:
            action_id: Action ID
            status: New status
            result: Action result data
            error: Error message if failed

        Returns:
            Updated action if found, None otherwise
        """
        update_values = {"status": status}
        if result is not None:
            update_values["result"] = result
        if error is not None:
            update_values["error"] = error

        stmt = (
            update(Action)
            .where(Action.id == action_id)
            .values(**update_values)
            .returning(Action)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def list_by_decision(self, decision_id: UUID) -> List[Action]:
        """
        List all actions for a decision.

        Args:
            decision_id: Decision ID

        Returns:
            List of actions ordered by creation time
        """
        stmt = (
            select(Action)
            .where(Action.decision_id == decision_id)
            .order_by(Action.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_incident(self, incident_id: UUID) -> List[Action]:
        """
        List all actions for an incident (via decisions).

        Args:
            incident_id: Incident ID

        Returns:
            List of actions ordered by creation time
        """
        # Join through decisions to get incident's actions
        from src.awfdrs.db.models.decisions import Decision

        stmt = (
            select(Action)
            .join(Decision, Action.decision_id == Decision.id)
            .where(Decision.incident_id == incident_id)
            .order_by(Action.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_reversible_actions(self, incident_id: UUID) -> List[Action]:
        """
        Get all reversible actions for an incident.

        Args:
            incident_id: Incident ID

        Returns:
            List of reversible actions
        """
        from src.awfdrs.db.models.decisions import Decision

        stmt = (
            select(Action)
            .join(Decision, Action.decision_id == Decision.id)
            .where(
                Decision.incident_id == incident_id,
                Action.is_reversible == True,
                Action.status == ActionStatus.COMPLETED
            )
            .order_by(Action.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
