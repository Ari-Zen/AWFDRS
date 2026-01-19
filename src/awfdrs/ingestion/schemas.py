"""
Ingestion API schemas.
"""

from datetime import datetime
from typing import Dict, Any
from uuid import UUID
from pydantic import Field, field_validator

from src.awfdrs.core.schemas import BaseSchema


class WorkflowEventV1(BaseSchema):
    """
    Workflow event schema v1.0.0

    This is the primary schema for event ingestion.
    """

    tenant_id: UUID = Field(..., description="Tenant identifier")
    workflow_id: UUID = Field(..., description="Workflow identifier")
    event_type: str = Field(..., description="Event type (e.g., 'payment.failed')")
    payload: Dict[str, Any] = Field(..., description="Event payload")
    idempotency_key: str = Field(..., description="Unique key for deduplication")
    occurred_at: datetime = Field(..., description="When the event occurred")
    schema_version: str = Field(default="1.0.0", description="Event schema version")

    @field_validator('event_type')
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        """Validate event type format."""
        if not v or len(v) < 3:
            raise ValueError("Event type must be at least 3 characters")
        if not all(c.isalnum() or c in "._-" for c in v):
            raise ValueError("Event type can only contain alphanumeric, dot, hyphen, and underscore")
        return v

    @field_validator('idempotency_key')
    @classmethod
    def validate_idempotency_key(cls, v: str) -> str:
        """Validate idempotency key."""
        if not v or len(v) < 1:
            raise ValueError("Idempotency key cannot be empty")
        if len(v) > 255:
            raise ValueError("Idempotency key cannot exceed 255 characters")
        return v

    @field_validator('schema_version')
    @classmethod
    def validate_schema_version(cls, v: str) -> str:
        """Validate schema version."""
        supported_versions = ["1.0.0"]
        if v not in supported_versions:
            raise ValueError(f"Schema version must be one of: {supported_versions}")
        return v


class EventResponse(BaseSchema):
    """Response after event ingestion."""

    event_id: UUID = Field(..., description="Created event ID")
    status: str = Field(default="accepted", description="Ingestion status")
    message: str = Field(default="Event ingested successfully", description="Status message")
    correlation_id: str = Field(..., description="Request correlation ID")


class HealthResponse(BaseSchema):
    """Health check response."""

    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")


class ReadinessResponse(BaseSchema):
    """Readiness check response."""

    status: str = Field(..., description="Readiness status")
    database: str = Field(..., description="Database status")
    redis: str = Field(default="ok", description="Redis status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
