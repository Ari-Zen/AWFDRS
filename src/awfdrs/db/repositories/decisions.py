"""
Decision repository for immutable decision records.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.decisions import Decision
from src.awfdrs.core.enums import DecisionType


class DecisionRepository:
    """
    Repository for decision operations.

    Note: Decisions are immutable - no update methods provided.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository."""
        self.session = session

    async def create_decision(
        self,
        incident_id: UUID,
        decision_type: DecisionType,
        rule_triggered: Optional[str] = None,
        ai_hypothesis: Optional[str] = None,
        confidence_score: Optional[float] = None,
        reasoning: Optional[str] = None,
        metadata: Optional[dict] = None,
        correlation_id: str = ""
    ) -> Decision:
        """
        Create a new decision record.

        Args:
            incident_id: Associated incident ID
            decision_type: Type of decision
            rule_triggered: Name of rule that triggered decision
            ai_hypothesis: AI-generated hypothesis
            confidence_score: Confidence score (0-1)
            reasoning: Human-readable reasoning
            metadata: Additional metadata
            correlation_id: Request correlation ID

        Returns:
            Created decision
        """
        decision = Decision(
            incident_id=incident_id,
            decision_type=decision_type,
            rule_triggered=rule_triggered,
            ai_hypothesis=ai_hypothesis,
            confidence_score=confidence_score,
            reasoning=reasoning,
            metadata=metadata or {},
            correlation_id=correlation_id,
            created_at=datetime.utcnow()
        )

        self.session.add(decision)
        await self.session.commit()
        await self.session.refresh(decision)
        return decision

    async def get(self, decision_id: UUID) -> Optional[Decision]:
        """
        Get decision by ID.

        Args:
            decision_id: Decision ID

        Returns:
            Decision if found, None otherwise
        """
        stmt = select(Decision).where(Decision.id == decision_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_incident(self, incident_id: UUID) -> List[Decision]:
        """
        List all decisions for an incident.

        Args:
            incident_id: Incident ID

        Returns:
            List of decisions ordered by creation time
        """
        stmt = (
            select(Decision)
            .where(Decision.incident_id == incident_id)
            .order_by(Decision.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_by_incident(self, incident_id: UUID) -> Optional[Decision]:
        """
        Get the most recent decision for an incident.

        Args:
            incident_id: Incident ID

        Returns:
            Latest decision if exists, None otherwise
        """
        stmt = (
            select(Decision)
            .where(Decision.incident_id == incident_id)
            .order_by(Decision.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
