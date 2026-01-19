"""
Decision model for immutable decision audit trail.
"""

from sqlalchemy import String, ForeignKey, Float, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from typing import Optional

from src.awfdrs.db.base import BaseModel, CorrelationMixin
from src.awfdrs.core.enums import DecisionType


class Decision(BaseModel, CorrelationMixin):
    """
    Immutable decision audit model.

    Decisions are never updated, only inserted. Provides complete audit trail.

    Attributes:
        incident_id: Foreign key to incident
        decision_type: Type of decision (rule-based, AI-assisted, etc.)
        rule_triggered: Name of rule that triggered (if applicable)
        ai_hypothesis: AI-generated hypothesis (if applicable)
        confidence_score: Confidence in decision (0-1)
        reasoning: Human-readable reasoning
        metadata: Additional decision metadata (JSON)
        correlation_id: Request correlation ID (from CorrelationMixin)
    """

    __tablename__ = "decisions"

    incident_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True
    )
    decision_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    rule_triggered: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    ai_hypothesis: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )
    reasoning: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True
    )
