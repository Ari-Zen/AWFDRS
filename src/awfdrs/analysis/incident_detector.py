"""
Incident detection service.
"""

import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.events import Event
from src.awfdrs.db.models.incidents import Incident
from src.awfdrs.db.repositories.incidents import IncidentRepository
from src.awfdrs.analysis.signature import ErrorSignatureGenerator
from src.awfdrs.analysis.correlator import IncidentCorrelator
from src.awfdrs.safety.rules_engine import RulesEngine
from src.awfdrs.core.enums import IncidentStatus

logger = logging.getLogger(__name__)


class IncidentDetector:
    """
    Monitors events and creates/updates incidents.

    Detects failures, generates signatures, and correlates with existing incidents.
    """

    def __init__(
        self,
        session: AsyncSession,
        correlation_id: str = ""
    ) -> None:
        """
        Initialize incident detector.

        Args:
            session: Database session
            correlation_id: Request correlation ID
        """
        self.session = session
        self.correlation_id = correlation_id
        self.incident_repo = IncidentRepository(session)
        self.signature_gen = ErrorSignatureGenerator()
        self.correlator = IncidentCorrelator(session)
        self.rules_engine = RulesEngine()

    async def process_event(self, event: Event) -> Optional[Incident]:
        """
        Process an event and create/update incident if needed.

        Args:
            event: Event to process

        Returns:
            Incident if created/updated, None if event doesn't indicate failure
        """
        # Check if event indicates a failure
        if not self.detect_incident(event):
            return None

        logger.info(
            f"Failure detected in event: {event.id}",
            extra={
                "correlation_id": self.correlation_id,
                "event_id": str(event.id),
                "event_type": event.event_type
            }
        )

        # Generate error signature
        signature = self.signature_gen.generate_signature(event)

        # Check for existing incident with same signature
        existing_incident = await self.correlator.find_related_incident(
            signature,
            event.tenant_id
        )

        if existing_incident:
            # Correlate with existing incident
            incident = await self.correlator.add_event_to_incident(
                existing_incident,
                event.id
            )

            logger.info(
                f"Event correlated to existing incident: {incident.id}",
                extra={
                    "correlation_id": self.correlation_id,
                    "incident_id": str(incident.id),
                    "event_id": str(event.id)
                }
            )
        else:
            # Create new incident
            incident = await self.create_incident(event, signature)

            logger.info(
                f"New incident created: {incident.id}",
                extra={
                    "correlation_id": self.correlation_id,
                    "incident_id": str(incident.id),
                    "event_id": str(event.id),
                    "signature": signature
                }
            )

        # Check if should escalate
        should_escalate = await self.correlator.should_escalate(incident)
        if should_escalate:
            logger.warning(
                f"Incident should be escalated: {incident.id}",
                extra={
                    "correlation_id": self.correlation_id,
                    "incident_id": str(incident.id),
                    "correlated_events": len(incident.correlated_event_ids)
                }
            )

        return incident

    def detect_incident(self, event: Event) -> bool:
        """
        Determine if event indicates a failure.

        Args:
            event: Event to check

        Returns:
            True if event indicates failure, False otherwise
        """
        # Check event type
        failure_indicators = [
            'failed',
            'error',
            'timeout',
            'rejected',
            'exception'
        ]

        event_type_lower = event.event_type.lower()
        for indicator in failure_indicators:
            if indicator in event_type_lower:
                return True

        # Check payload for error indicators
        payload = event.payload
        if payload.get('error_code'):
            return True
        if payload.get('error_message'):
            return True
        if payload.get('status') in ['failed', 'error', 'rejected']:
            return True

        return False

    async def create_incident(self, event: Event, signature: str) -> Incident:
        """
        Create a new incident from an event.

        Args:
            event: Triggering event
            signature: Error signature

        Returns:
            Created incident
        """
        # Get vendor ID from event payload if available
        vendor_id = event.payload.get('vendor_id')

        # Determine severity from rules engine
        error_code = event.payload.get('error_code', 'unknown')
        severity = await self.rules_engine.get_error_severity(error_code)

        # Create incident
        incident = await self.incident_repo.create(
            tenant_id=event.tenant_id,
            vendor_id=UUID(vendor_id) if vendor_id else None,
            error_signature=signature,
            status=IncidentStatus.DETECTED,
            severity=severity,
            correlated_event_ids=[event.id],
            first_occurrence_at=event.occurred_at,
            last_occurrence_at=event.occurred_at,
            metadata={
                'error_code': error_code,
                'event_type': event.event_type,
                'triggering_event_id': str(event.id)
            },
            correlation_id=self.correlation_id
        )

        return incident
