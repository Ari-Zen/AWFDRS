"""
Incident model for failure tracking.
"""

from sqlalchemy import String, ForeignKey, ARRAY, Text, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from typing import Optional, List

from src.awfdrs.db.base import BaseModel, TenantMixin, CorrelationMixin
from src.awfdrs.core.enums import IncidentStatus, ErrorSeverity


class Incident(BaseModel, TenantMixin, CorrelationMixin):
    """
    Incident tracking model.

    Represents a detected failure or anomaly that requires attention.

    Attributes:
        tenant_id: Foreign key to tenant (from TenantMixin)
        vendor_id: Foreign key to vendor (nullable)
        workflow_id: Foreign key to workflow (nullable)
        error_signature: Unique signature for grouping similar errors
        status: Current incident status
        severity: Error severity level
        correlated_event_ids: Array of event IDs related to this incident
        description: Human-readable description
        resolution_notes: Notes about resolution
        correlation_id: Request correlation ID (from CorrelationMixin)
    """

    __tablename__ = "incidents"

    vendor_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        index=True
    )
    workflow_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        index=True
    )
    error_signature: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=IncidentStatus.DETECTED,
        nullable=False,
        index=True
    )
    severity: Mapped[str] = mapped_column(
        String(50),
        default=ErrorSeverity.MEDIUM,
        nullable=False
    )
    correlated_event_ids: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Composite indexes
    __table_args__ = (
        Index("ix_incidents_tenant_status", "tenant_id", "status"),
        Index("ix_incidents_tenant_signature", "tenant_id", "error_signature"),
        Index("ix_incidents_tenant_created", "tenant_id", "created_at"),
    )
