"""
Incident correlation logic.
"""

import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.incidents import Incident
from src.awfdrs.db.repositories.incidents import IncidentRepository
from src.awfdrs.core.enums import IncidentStatus

logger = logging.getLogger(__name__)


class IncidentCorrelator:
    """
    Correlates events to incidents based on error signatures.
    """

    # Time window for correlation (30 minutes)
    CORRELATION_WINDOW_MINUTES = 30

    # Escalation threshold (10 correlated events)
    ESCALATION_THRESHOLD = 10

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize incident correlator.

        Args:
            session: Database session
        """
        self.session = session
        self.incident_repo = IncidentRepository(session)

    async def find_related_incident(
        self,
        signature: str,
        tenant_id: UUID
    ) -> Optional[Incident]:
        """
        Find an existing active incident with matching signature.

        Args:
            signature: Error signature
            tenant_id: Tenant ID for isolation

        Returns:
            Related incident if found, None otherwise
        """
        # Calculate time window
        time_threshold = datetime.utcnow() - timedelta(
            minutes=self.CORRELATION_WINDOW_MINUTES
        )

        # Search for active incident with same signature
        incidents = await self.incident_repo.get_active_by_signature(
            tenant_id,
            signature
        )

        # Filter by time window and non-resolved status
        for incident in incidents:
            if (
                incident.status != IncidentStatus.RESOLVED and
                incident.last_occurrence_at >= time_threshold
            ):
                return incident

        return None

    async def add_event_to_incident(
        self,
        incident: Incident,
        event_id: UUID
    ) -> Incident:
        """
        Add an event to an existing incident.

        Args:
            incident: Incident to update
            event_id: Event ID to add

        Returns:
            Updated incident
        """
        # Add event to correlated events
        if event_id not in incident.correlated_event_ids:
            updated_ids = incident.correlated_event_ids + [event_id]

            # Update incident
            updated_incident = await self.incident_repo.update(
                incident.id,
                correlated_event_ids=updated_ids,
                last_occurrence_at=datetime.utcnow()
            )

            return updated_incident or incident

        return incident

    async def should_escalate(self, incident: Incident) -> bool:
        """
        Determine if incident should be escalated.

        Args:
            incident: Incident to check

        Returns:
            True if should escalate, False otherwise
        """
        # Already escalated
        if incident.status == IncidentStatus.ESCALATED:
            return False

        # Check correlated event count
        if len(incident.correlated_event_ids) >= self.ESCALATION_THRESHOLD:
            return True

        # Check if critical severity
        from src.awfdrs.core.enums import ErrorSeverity
        if incident.severity == ErrorSeverity.CRITICAL:
            return True

        return False
