"""
Event model for immutable event storage.
"""

from datetime import datetime
from sqlalchemy import String, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID

from src.awfdrs.db.base import BaseModel, TenantMixin, CorrelationMixin


class Event(BaseModel, TenantMixin, CorrelationMixin):
    """
    Immutable event storage model.

    Events are never updated, only inserted. This provides a complete audit trail.

    Attributes:
        tenant_id: Foreign key to tenant (from TenantMixin)
        workflow_id: Foreign key to workflow
        event_type: Type of event (e.g., "payment.failed")
        payload: Event payload (JSON)
        idempotency_key: Unique key for deduplication
        occurred_at: When the event actually occurred
        schema_version: Event schema version
        correlation_id: Request correlation ID (from CorrelationMixin)
    """

    __tablename__ = "events"

    workflow_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True
    )
    event_type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    schema_version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_events_tenant_workflow", "tenant_id", "workflow_id"),
        Index("ix_events_tenant_occurred", "tenant_id", "occurred_at"),
        Index("ix_events_tenant_type", "tenant_id", "event_type"),
    )
