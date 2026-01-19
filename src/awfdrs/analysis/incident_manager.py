"""
Incident lifecycle management.
"""

import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.incidents import Incident
from src.awfdrs.db.repositories.incidents import IncidentRepository
from src.awfdrs.core.enums import IncidentStatus

logger = logging.getLogger(__name__)


class IncidentManager:
    """
    Manages incident state transitions and lifecycle.
    """

    def __init__(
        self,
        session: AsyncSession,
        correlation_id: str = ""
    ) -> None:
        """
        Initialize incident manager.

        Args:
            session: Database session
            correlation_id: Request correlation ID
        """
        self.session = session
        self.correlation_id = correlation_id
        self.incident_repo = IncidentRepository(session)

    async def transition_to_analyzing(self, incident_id: UUID) -> Optional[Incident]:
        """
        Transition incident to ANALYZING state.

        Args:
            incident_id: Incident ID

        Returns:
            Updated incident
        """
        logger.info(
            f"Transitioning incident to ANALYZING: {incident_id}",
            extra={
                "correlation_id": self.correlation_id,
                "incident_id": str(incident_id)
            }
        )

        return await self.incident_repo.update_status(
            incident_id,
            IncidentStatus.ANALYZING
        )

    async def resolve_incident(
        self,
        incident_id: UUID,
        resolution_notes: str
    ) -> Optional[Incident]:
        """
        Resolve an incident.

        Args:
            incident_id: Incident ID
            resolution_notes: Notes about resolution

        Returns:
            Updated incident
        """
        logger.info(
            f"Resolving incident: {incident_id}",
            extra={
                "correlation_id": self.correlation_id,
                "incident_id": str(incident_id)
            }
        )

        incident = await self.incident_repo.get(incident_id)
        if not incident:
            return None

        # Update metadata with resolution notes
        metadata = incident.metadata or {}
        metadata['resolution_notes'] = resolution_notes

        return await self.incident_repo.update(
            incident_id,
            status=IncidentStatus.RESOLVED,
            metadata=metadata
        )

    async def escalate_incident(
        self,
        incident_id: UUID,
        reason: str
    ) -> Optional[Incident]:
        """
        Escalate an incident.

        Args:
            incident_id: Incident ID
            reason: Escalation reason

        Returns:
            Updated incident
        """
        logger.warning(
            f"Escalating incident: {incident_id}",
            extra={
                "correlation_id": self.correlation_id,
                "incident_id": str(incident_id),
                "reason": reason
            }
        )

        incident = await self.incident_repo.get(incident_id)
        if not incident:
            return None

        # Update metadata with escalation reason
        metadata = incident.metadata or {}
        metadata['escalation_reason'] = reason

        return await self.incident_repo.update(
            incident_id,
            status=IncidentStatus.ESCALATED,
            metadata=metadata
        )

    async def ignore_incident(
        self,
        incident_id: UUID,
        reason: str
    ) -> Optional[Incident]:
        """
        Mark incident as ignored.

        Args:
            incident_id: Incident ID
            reason: Reason for ignoring

        Returns:
            Updated incident
        """
        logger.info(
            f"Ignoring incident: {incident_id}",
            extra={
                "correlation_id": self.correlation_id,
                "incident_id": str(incident_id),
                "reason": reason
            }
        )

        incident = await self.incident_repo.get(incident_id)
        if not incident:
            return None

        # Update metadata with ignore reason
        metadata = incident.metadata or {}
        metadata['ignore_reason'] = reason

        return await self.incident_repo.update(
            incident_id,
            status=IncidentStatus.IGNORED,
            metadata=metadata
        )
