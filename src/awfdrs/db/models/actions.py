"""
Action model for tracking executed actions.
"""

from sqlalchemy import String, ForeignKey, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from typing import Optional

from src.awfdrs.db.base import BaseModel, CorrelationMixin
from src.awfdrs.core.enums import ActionType, ActionStatus


class Action(BaseModel, CorrelationMixin):
    """
    Action execution tracking model.

    Tracks actions taken in response to incidents.

    Attributes:
        decision_id: Foreign key to decision
        action_type: Type of action taken
        status: Current action status
        result: Action result (JSON)
        error_message: Error message if action failed
        is_reversible: Whether action can be reversed
        reversal_action_id: ID of action that reverses this one (if applicable)
        correlation_id: Request correlation ID (from CorrelationMixin)
    """

    __tablename__ = "actions"

    decision_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True
    )
    action_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=ActionStatus.PENDING,
        nullable=False,
        index=True
    )
    result: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    is_reversible: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    reversal_action_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True
    )
