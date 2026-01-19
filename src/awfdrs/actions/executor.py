"""
Action execution engine.
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.decisions import Decision
from src.awfdrs.db.models.actions import Action
from src.awfdrs.db.repositories.actions import ActionRepository
from src.awfdrs.core.enums import ActionType, ActionStatus, CircuitBreakerState

logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Executes actions based on decisions with state tracking.
    """

    def __init__(
        self,
        session: AsyncSession,
        correlation_id: str = ""
    ) -> None:
        """
        Initialize action executor.

        Args:
            session: Database session
            correlation_id: Request correlation ID
        """
        self.session = session
        self.correlation_id = correlation_id
        self.action_repo = ActionRepository(session)

    async def execute_action(
        self,
        decision: Decision,
        action_type: ActionType,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Action:
        """
        Execute an action based on a decision.

        Args:
            decision: Decision that triggered action
            action_type: Type of action to execute
            parameters: Action parameters

        Returns:
            Executed action
        """
        logger.info(
            f"Executing action: {action_type}",
            extra={
                "correlation_id": self.correlation_id,
                "decision_id": str(decision.id),
                "action_type": action_type.value
            }
        )

        # Create action record
        action = await self.action_repo.create_action(
            decision_id=decision.id,
            action_type=action_type,
            parameters=parameters or {},
            is_reversible=(action_type == ActionType.RETRY),
            correlation_id=self.correlation_id
        )

        # Update status to in_progress
        action = await self.action_repo.update_status(
            action.id,
            ActionStatus.IN_PROGRESS
        )

        # Execute based on type
        try:
            if action_type == ActionType.RETRY:
                result = await self.execute_retry(action)
            elif action_type == ActionType.CIRCUIT_BREAKER:
                result = await self.execute_circuit_breaker(
                    action,
                    parameters.get("state", CircuitBreakerState.OPEN)
                )
            elif action_type == ActionType.KILL_SWITCH:
                result = await self.execute_kill_switch(
                    action,
                    parameters.get("activate", True)
                )
            elif action_type == ActionType.ESCALATE:
                result = await self.execute_escalation(action)
            elif action_type == ActionType.NOTIFY:
                result = await self._execute_notify(action)
            else:
                result = {"status": "unknown_action_type"}

            # Mark as completed
            action = await self.action_repo.update_status(
                action.id,
                ActionStatus.COMPLETED,
                result=result
            )

            logger.info(
                f"Action completed successfully: {action.id}",
                extra={"correlation_id": self.correlation_id, "action_id": str(action.id)}
            )

        except Exception as e:
            logger.error(
                f"Action failed: {str(e)}",
                extra={
                    "correlation_id": self.correlation_id,
                    "action_id": str(action.id),
                    "error": str(e)
                },
                exc_info=True
            )

            # Mark as failed
            action = await self.action_repo.update_status(
                action.id,
                ActionStatus.FAILED,
                error=str(e)
            )

        return action

    async def execute_retry(self, action: Action) -> Dict[str, Any]:
        """Execute retry action."""
        logger.info(f"Executing retry action: {action.id}")

        # In real implementation, this would trigger actual retry
        # For mock, we just log it
        return {
            "status": "retry_scheduled",
            "message": "Retry action logged (mock implementation)"
        }

    async def execute_circuit_breaker(
        self,
        action: Action,
        state: CircuitBreakerState
    ) -> Dict[str, Any]:
        """Execute circuit breaker action."""
        logger.info(
            f"Executing circuit breaker action: {action.id}, state: {state}"
        )

        # In real implementation, would update vendor circuit breaker
        return {
            "status": "circuit_breaker_updated",
            "new_state": state.value,
            "message": "Circuit breaker updated (mock implementation)"
        }

    async def execute_kill_switch(
        self,
        action: Action,
        activate: bool
    ) -> Dict[str, Any]:
        """Execute kill switch action."""
        logger.warning(
            f"Executing kill switch action: {action.id}, activate: {activate}"
        )

        # In real implementation, would update workflow kill switch
        return {
            "status": "kill_switch_updated",
            "activated": activate,
            "message": "Kill switch updated (mock implementation)"
        }

    async def execute_escalation(self, action: Action) -> Dict[str, Any]:
        """Execute escalation action."""
        logger.warning(f"Executing escalation action: {action.id}")

        # Escalation is handled by separate escalation handler
        return {
            "status": "escalated",
            "message": "Escalation triggered (mock implementation)"
        }

    async def _execute_notify(self, action: Action) -> Dict[str, Any]:
        """Execute notification action."""
        logger.info(f"Executing notify action: {action.id}")

        # In real implementation, would send notifications
        return {
            "status": "notified",
            "channels": ["email", "slack"],
            "message": "Notifications sent (mock implementation)"
        }

    async def reverse_action(self, action: Action) -> Action:
        """
        Reverse a reversible action.

        Args:
            action: Action to reverse

        Returns:
            New action representing the reversal
        """
        if not action.is_reversible:
            raise ValueError(f"Action {action.id} is not reversible")

        if action.status != ActionStatus.COMPLETED:
            raise ValueError(f"Can only reverse completed actions")

        logger.info(
            f"Reversing action: {action.id}",
            extra={"correlation_id": self.correlation_id, "action_id": str(action.id)}
        )

        # Create reversal action
        reversal_action = await self.action_repo.create_action(
            decision_id=action.decision_id,
            action_type=action.action_type,
            parameters={"reversal_of": str(action.id), **action.parameters},
            is_reversible=False,
            correlation_id=self.correlation_id
        )

        # Execute reversal
        # For mock, just mark as completed
        reversal_action = await self.action_repo.update_status(
            reversal_action.id,
            ActionStatus.COMPLETED,
            result={"reversed_action_id": str(action.id)}
        )

        return reversal_action
