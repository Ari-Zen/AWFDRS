"""
Base Pydantic schemas with common fields.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {}
        }
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class IdentifiedSchema(BaseSchema):
    """Schema with ID field."""

    id: UUID = Field(..., description="Unique identifier")


class TenantSchema(BaseSchema):
    """Schema with tenant ID field."""

    tenant_id: UUID = Field(..., description="Tenant identifier")


class CorrelationSchema(BaseSchema):
    """Schema with correlation ID field."""

    correlation_id: str = Field(..., description="Request correlation ID")


class PaginationParams(BaseSchema):
    """Pagination parameters."""

    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")


class ErrorResponse(BaseSchema):
    """Standard error response."""

    error: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")


class SuccessResponse(BaseSchema):
    """Standard success response."""

    message: str = Field(..., description="Success message")
    data: Optional[dict] = Field(None, description="Response data")
