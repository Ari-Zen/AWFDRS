"""
Kill switch model for emergency controls.
"""

from sqlalchemy import String, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from typing import Optional

from src.awfdrs.db.base import BaseModel
from src.awfdrs.core.enums import KillSwitchScope


class KillSwitch(BaseModel):
    """
    Kill switch model for emergency controls.

    Provides ability to quickly disable workflows, vendors, or tenants.

    Attributes:
        scope: Scope of kill switch (workflow, vendor, tenant, global)
        target_id: ID of target (workflow_id, vendor_id, or tenant_id)
        is_active: Whether kill switch is currently active
        reason: Reason for activation
        activated_by: User who activated (for audit)
    """

    __tablename__ = "kill_switches"

    scope: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    target_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    activated_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    # Composite indexes
    __table_args__ = (
        Index("ix_kill_switches_scope_target", "scope", "target_id"),
        Index("ix_kill_switches_active", "is_active", "scope"),
    )
