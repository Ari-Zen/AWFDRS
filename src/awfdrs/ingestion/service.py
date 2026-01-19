"""
Event ingestion service.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.ingestion.schemas import WorkflowEventV1, EventResponse
from src.awfdrs.ingestion.validators import (
    validate_schema_version,
    validate_tenant_exists,
    validate_workflow_exists,
    validate_idempotency_key,
    validate_payload_structure
)
from src.awfdrs.db.repositories.events import EventRepository
from src.awfdrs.core.exceptions import AWFDRSException

logger = logging.getLogger(__name__)


class IngestionService:
    """
    Service for ingesting workflow events.

    Handles validation, deduplication, and storage of events.
    """

    def __init__(self, session: AsyncSession, correlation_id: str = "") -> None:
        """
        Initialize service.

        Args:
            session: Database session
            correlation_id: Request correlation ID
        """
        self.session = session
        self.correlation_id = correlation_id
        self.event_repo = EventRepository(session)

    async def ingest_event(self, event: WorkflowEventV1) -> EventResponse:
        """
        Ingest a workflow event.

        Validates event and stores it in the database.

        Args:
            event: Event to ingest

        Returns:
            EventResponse with event ID

        Raises:
            ValidationError: If validation fails
            ConflictError: If idempotency key is duplicate
            NotFoundError: If tenant or workflow not found
            KillSwitchActiveError: If workflow is kill-switched
        """
        logger.info(
            f"Ingesting event: {event.event_type}",
            extra={
                "correlation_id": self.correlation_id,
                "tenant_id": str(event.tenant_id),
                "workflow_id": str(event.workflow_id),
                "event_type": event.event_type,
                "idempotency_key": event.idempotency_key
            }
        )

        try:
            # Validate schema version
            await validate_schema_version(event.schema_version)

            # Validate payload structure
            await validate_payload_structure(event.payload)

            # Validate tenant exists and is active
            await validate_tenant_exists(self.session, event.tenant_id)

            # Validate workflow exists and is not kill-switched
            await validate_workflow_exists(self.session, event.workflow_id)

            # Validate idempotency key (will raise ConflictError if duplicate)
            await validate_idempotency_key(self.session, event.idempotency_key)

            # Create event in database
            created_event = await self.event_repo.create_event(
                tenant_id=event.tenant_id,
                workflow_id=event.workflow_id,
                event_type=event.event_type,
                payload=event.payload,
                idempotency_key=event.idempotency_key,
                occurred_at=event.occurred_at,
                schema_version=event.schema_version,
                correlation_id=self.correlation_id
            )

            logger.info(
                f"Event ingested successfully: {created_event.id}",
                extra={
                    "correlation_id": self.correlation_id,
                    "event_id": str(created_event.id),
                    "tenant_id": str(event.tenant_id)
                }
            )

            return EventResponse(
                event_id=created_event.id,
                status="accepted",
                message="Event ingested successfully",
                correlation_id=self.correlation_id
            )

        except AWFDRSException as e:
            logger.error(
                f"Event ingestion failed: {e.message}",
                extra={
                    "correlation_id": self.correlation_id,
                    "error": e.message,
                    "details": e.details
                }
            )
            raise

        except Exception as e:
            logger.error(
                f"Unexpected error during event ingestion: {str(e)}",
                extra={
                    "correlation_id": self.correlation_id,
                    "error": str(e)
                },
                exc_info=True
            )
            raise
