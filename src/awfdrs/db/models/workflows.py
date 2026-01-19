"""
Workflow model for workflow registry.
"""

from sqlalchemy import String, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID

from src.awfdrs.db.base import BaseModel, TenantMixin


class Workflow(BaseModel, TenantMixin):
    """
    Workflow registry model.

    Workflows are registered processes that can generate events.

    Attributes:
        tenant_id: Foreign key to tenant
        name: Workflow name
        schema_version: Event schema version
        config: Workflow configuration (JSON)
        is_kill_switched: Whether workflow is kill-switched
    """

    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    schema_version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    config: Mapped[dict] = mapped_column(JSON, nullable=True)
    is_kill_switched: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Note: tenant_id is inherited from TenantMixin
    # Add unique constraint on tenant_id + name
    __table_args__ = (
        {"schema": None},
    )
