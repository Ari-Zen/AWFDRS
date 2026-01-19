"""
Event repository for immutable event storage.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.events import Event
from src.awfdrs.core.exceptions import ConflictError


class EventRepository:
    """
    Repository for event operations.

    Events are immutable - no update or delete operations are provided.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository."""
        self.session = session

    async def create_event(
        self,
        tenant_id: UUID,
        workflow_id: UUID,
        event_type: str,
        payload: dict,
        idempotency_key: str,
        occurred_at: datetime,
        schema_version: str = "1.0.0",
        correlation_id: Optional[str] = None
    ) -> Event:
        """
        Create a new event.

        Args:
            tenant_id: Tenant ID
            workflow_id: Workflow ID
            event_type: Type of event
            payload: Event payload
            idempotency_key: Unique key for deduplication
            occurred_at: When event occurred
            schema_version: Event schema version
            correlation_id: Request correlation ID

        Returns:
            Created event

        Raises:
            ConflictError: If idempotency key already exists
        """
        # Check for duplicate idempotency key
        existing = await self.get_by_idempotency_key(idempotency_key)
        if existing:
            raise ConflictError(
                f"Event with idempotency_key '{idempotency_key}' already exists",
                details={"event_id": str(existing.id)}
            )

        event = Event(
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            event_type=event_type,
            payload=payload,
            idempotency_key=idempotency_key,
            occurred_at=occurred_at,
            schema_version=schema_version,
            correlation_id=correlation_id
        )

        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Event]:
        """
        Get event by idempotency key.

        Args:
            idempotency_key: Idempotency key

        Returns:
            Event or None
        """
        result = await self.session.execute(
            select(Event).where(Event.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def list_by_workflow(
        self,
        tenant_id: UUID,
        workflow_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """
        List events for a workflow.

        Args:
            tenant_id: Tenant ID
            workflow_id: Workflow ID
            skip: Number to skip
            limit: Maximum to return

        Returns:
            List of events
        """
        result = await self.session.execute(
            select(Event)
            .where(Event.tenant_id == tenant_id)
            .where(Event.workflow_id == workflow_id)
            .order_by(Event.occurred_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_by_type(
        self,
        tenant_id: UUID,
        event_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """
        List events by type.

        Args:
            tenant_id: Tenant ID
            event_type: Event type
            skip: Number to skip
            limit: Maximum to return

        Returns:
            List of events
        """
        result = await self.session.execute(
            select(Event)
            .where(Event.tenant_id == tenant_id)
            .where(Event.event_type == event_type)
            .order_by(Event.occurred_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
