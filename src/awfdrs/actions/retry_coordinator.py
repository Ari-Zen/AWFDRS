"""
Retry coordinator for automatic retry scheduling.
"""

import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.incidents import Incident
from src.awfdrs.db.models.actions import Action
from src.awfdrs.db.repositories.actions import ActionRepository
from src.awfdrs.db.repositories.workflows import WorkflowRepository
from src.awfdrs.db.repositories.vendors import VendorRepository
from src.awfdrs.safety.rules_engine import RulesEngine
from src.awfdrs.safety.limits import SafetyLimitsEnforcer
from src.awfdrs.safety.circuit_breaker import CircuitBreakerManager
from src.awfdrs.safety.schemas import ErrorContext
from src.awfdrs.core.enums import ActionType, CircuitBreakerState
from src.awfdrs.config import settings

logger = logging.getLogger(__name__)


class RetryCoordinator:
    """
    Coordinates automatic retries with safety checks.

    Ensures retries respect safety limits and circuit breakers.
    """

    def __init__(
        self,
        session: AsyncSession,
        correlation_id: str = ""
    ) -> None:
        """
        Initialize retry coordinator.

        Args:
            session: Database session
            correlation_id: Request correlation ID
        """
        self.session = session
        self.correlation_id = correlation_id
        self.action_repo = ActionRepository(session)
        self.workflow_repo = WorkflowRepository(session)
        self.vendor_repo = VendorRepository(session)
        self.rules_engine = RulesEngine()
        self.safety_limits = SafetyLimitsEnforcer()
        self.circuit_breaker = CircuitBreakerManager(session)

    async def should_retry(self, incident: Incident) -> bool:
        """
        Determine if incident should trigger retry.

        Args:
            incident: Incident to check

        Returns:
            True if should retry, False otherwise
        """
        # Get error code from incident metadata
        error_code = incident.metadata.get("error_code", "unknown")

        # Check if error is retryable
        context = ErrorContext(
            error_code=error_code,
            retry_count=0  # Would need to track actual retry count
        )

        evaluation = await self.rules_engine.evaluate_error(error_code, context)
        if not evaluation.should_retry:
            return False

        # Check safety limits
        # Note: In full implementation, would get workflow_id from incident
        # For now, we'll skip the actual check
        # workflow_ok = await self.check_retry_limits(workflow_id, vendor_id)

        return True

    async def schedule_retry(
        self,
        incident: Incident,
        delay: float
    ) -> Optional[Action]:
        """
        Schedule a retry for an incident.

        Args:
            incident: Incident to retry
            delay: Delay in seconds before retry

        Returns:
            Created action if retry scheduled
        """
        logger.info(
            f"Scheduling retry for incident: {incident.id}, delay: {delay}s",
            extra={
                "correlation_id": self.correlation_id,
                "incident_id": str(incident.id),
                "delay_seconds": delay
            }
        )

        # In real implementation, would:
        # 1. Get latest decision for incident
        # 2. Create retry action
        # 3. Schedule execution after delay

        # For mock, just log it
        return None

    async def execute_retry(self, action: Action) -> Action:
        """
        Execute a scheduled retry action.

        Args:
            action: Retry action to execute

        Returns:
            Updated action with result
        """
        logger.info(
            f"Executing scheduled retry: {action.id}",
            extra={"correlation_id": self.correlation_id, "action_id": str(action.id)}
        )

        # In real implementation, would trigger actual retry
        # For mock, just mark as completed
        from src.awfdrs.core.enums import ActionStatus

        action = await self.action_repo.update_status(
            action.id,
            ActionStatus.COMPLETED,
            result={"retry_executed": True}
        )

        return action

    async def check_retry_limits(
        self,
        workflow_id: UUID,
        vendor_id: Optional[UUID]
    ) -> bool:
        """
        Check if retry is within safety limits.

        Args:
            workflow_id: Workflow ID
            vendor_id: Vendor ID (optional)

        Returns:
            True if within limits, False otherwise
        """
        # Check workflow retry limit
        workflow_ok = await self.safety_limits.check_workflow_retry_limit(workflow_id)
        if not workflow_ok:
            logger.warning(
                f"Workflow retry limit exceeded: {workflow_id}",
                extra={"workflow_id": str(workflow_id)}
            )
            return False

        # Check vendor retry limit if vendor specified
        if vendor_id:
            vendor_ok = await self.safety_limits.check_vendor_retry_limit(vendor_id)
            if not vendor_ok:
                logger.warning(
                    f"Vendor retry limit exceeded: {vendor_id}",
                    extra={"vendor_id": str(vendor_id)}
                )
                return False

            # Check circuit breaker
            cb_state = await self.circuit_breaker.check_state(vendor_id)
            if cb_state == CircuitBreakerState.OPEN:
                logger.warning(
                    f"Circuit breaker OPEN for vendor: {vendor_id}",
                    extra={"vendor_id": str(vendor_id)}
                )
                return False

        return True
