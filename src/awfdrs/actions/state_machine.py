"""
Action state machine for managing action lifecycle.
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.actions import Action
from src.awfdrs.db.repositories.actions import ActionRepository
from src.awfdrs.core.enums import ActionStatus

logger = logging.getLogger(__name__)


class ActionStateMachine:
    """
    Manages action state transitions and lifecycle.

    Valid transitions:
    - PENDING → IN_PROGRESS
    - IN_PROGRESS → COMPLETED
    - IN_PROGRESS → FAILED
    - Any state → SKIPPED
    """

    VALID_TRANSITIONS = {
        ActionStatus.PENDING: [ActionStatus.IN_PROGRESS, ActionStatus.SKIPPED],
        ActionStatus.IN_PROGRESS: [ActionStatus.COMPLETED, ActionStatus.FAILED, ActionStatus.SKIPPED],
        ActionStatus.COMPLETED: [ActionStatus.SKIPPED],  # Can skip even completed actions
        ActionStatus.FAILED: [ActionStatus.SKIPPED],
        ActionStatus.SKIPPED: []  # Terminal state
    }

    def __init__(
        self,
        session: AsyncSession,
        correlation_id: str = ""
    ) -> None:
        """
        Initialize action state machine.

        Args:
            session: Database session
            correlation_id: Request correlation ID
        """
        self.session = session
        self.correlation_id = correlation_id
        self.action_repo = ActionRepository(session)

    async def transition_to_in_progress(self, action_id: UUID) -> Optional[Action]:
        """
        Transition action to IN_PROGRESS state.

        Args:
            action_id: Action ID

        Returns:
            Updated action
        """
        action = await self.action_repo.get(action_id)
        if not action:
            return None

        if not self._is_valid_transition(action.status, ActionStatus.IN_PROGRESS):
            logger.warning(
                f"Invalid transition: {action.status} → IN_PROGRESS",
                extra={"action_id": str(action_id)}
            )
            return action

        logger.info(
            f"Transitioning action to IN_PROGRESS: {action_id}",
            extra={"correlation_id": self.correlation_id, "action_id": str(action_id)}
        )

        return await self.action_repo.update_status(
            action_id,
            ActionStatus.IN_PROGRESS
        )

    async def mark_completed(
        self,
        action_id: UUID,
        result: Dict[str, Any]
    ) -> Optional[Action]:
        """
        Mark action as completed.

        Args:
            action_id: Action ID
            result: Action result data

        Returns:
            Updated action
        """
        action = await self.action_repo.get(action_id)
        if not action:
            return None

        if not self._is_valid_transition(action.status, ActionStatus.COMPLETED):
            logger.warning(
                f"Invalid transition: {action.status} → COMPLETED",
                extra={"action_id": str(action_id)}
            )
            return action

        logger.info(
            f"Marking action as completed: {action_id}",
            extra={"correlation_id": self.correlation_id, "action_id": str(action_id)}
        )

        return await self.action_repo.update_status(
            action_id,
            ActionStatus.COMPLETED,
            result=result
        )

    async def mark_failed(
        self,
        action_id: UUID,
        error: str
    ) -> Optional[Action]:
        """
        Mark action as failed.

        Args:
            action_id: Action ID
            error: Error message

        Returns:
            Updated action
        """
        action = await self.action_repo.get(action_id)
        if not action:
            return None

        if not self._is_valid_transition(action.status, ActionStatus.FAILED):
            logger.warning(
                f"Invalid transition: {action.status} → FAILED",
                extra={"action_id": str(action_id)}
            )
            return action

        logger.error(
            f"Marking action as failed: {action_id}",
            extra={
                "correlation_id": self.correlation_id,
                "action_id": str(action_id),
                "error": error
            }
        )

        return await self.action_repo.update_status(
            action_id,
            ActionStatus.FAILED,
            error=error
        )

    async def skip_action(
        self,
        action_id: UUID,
        reason: str
    ) -> Optional[Action]:
        """
        Skip an action (manual override).

        Args:
            action_id: Action ID
            reason: Reason for skipping

        Returns:
            Updated action
        """
        action = await self.action_repo.get(action_id)
        if not action:
            return None

        logger.info(
            f"Skipping action: {action_id}",
            extra={
                "correlation_id": self.correlation_id,
                "action_id": str(action_id),
                "reason": reason
            }
        )

        return await self.action_repo.update_status(
            action_id,
            ActionStatus.SKIPPED,
            result={"skip_reason": reason}
        )

    def _is_valid_transition(
        self,
        from_status: ActionStatus,
        to_status: ActionStatus
    ) -> bool:
        """
        Check if state transition is valid.

        Args:
            from_status: Current status
            to_status: Target status

        Returns:
            True if transition is valid, False otherwise
        """
        valid_targets = self.VALID_TRANSITIONS.get(from_status, [])
        return to_status in valid_targets
