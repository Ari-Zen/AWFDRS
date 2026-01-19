"""
AI decision service for orchestrating AI analysis.
"""

import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.incidents import Incident
from src.awfdrs.db.models.decisions import Decision
from src.awfdrs.db.repositories.decisions import DecisionRepository
from src.awfdrs.ai.agents.detector import AIErrorDetector
from src.awfdrs.ai.agents.rca import AIRootCauseAnalyzer
from src.awfdrs.core.enums import DecisionType
from src.awfdrs.config import settings

logger = logging.getLogger(__name__)


class AIDecisionService:
    """
    Orchestrates AI analysis and creates decision records.

    Coordinates between detection, RCA, and decision storage.
    """

    def __init__(
        self,
        session: AsyncSession,
        correlation_id: str = ""
    ) -> None:
        """
        Initialize AI decision service.

        Args:
            session: Database session
            correlation_id: Request correlation ID
        """
        self.session = session
        self.correlation_id = correlation_id
        self.decision_repo = DecisionRepository(session)
        self.detector = AIErrorDetector()
        self.rca_analyzer = AIRootCauseAnalyzer()

    async def create_detection_decision(
        self,
        incident: Incident
    ) -> Optional[Decision]:
        """
        Create a decision based on AI error detection.

        Args:
            incident: Incident to analyze

        Returns:
            Created decision if analysis successful
        """
        logger.info(
            f"Creating AI detection decision for incident: {incident.id}",
            extra={
                "correlation_id": self.correlation_id,
                "incident_id": str(incident.id)
            }
        )

        # Note: We would typically load the triggering event here
        # For now, we'll create a basic decision
        # In a full implementation, you'd fetch the event and analyze it

        decision = await self.decision_repo.create_decision(
            incident_id=incident.id,
            decision_type=DecisionType.AI_ASSISTED,
            rule_triggered="ai_detection",
            ai_hypothesis="AI-detected error pattern",
            confidence_score=0.75,
            reasoning="AI detection analysis performed",
            metadata={
                "detection_type": "ai",
                "analyzer": "AIErrorDetector"
            },
            correlation_id=self.correlation_id
        )

        return decision

    async def create_rca_decision(self, incident: Incident) -> Optional[Decision]:
        """
        Create a decision based on AI root cause analysis.

        Args:
            incident: Incident to analyze

        Returns:
            Created decision
        """
        logger.info(
            f"Creating AI RCA decision for incident: {incident.id}",
            extra={
                "correlation_id": self.correlation_id,
                "incident_id": str(incident.id)
            }
        )

        # Perform RCA
        rca_result = await self.rca_analyzer.analyze_incident(incident)

        # Create decision with RCA results
        decision = await self.decision_repo.create_decision(
            incident_id=incident.id,
            decision_type=DecisionType.AI_ASSISTED,
            rule_triggered="ai_rca",
            ai_hypothesis=rca_result.root_cause,
            confidence_score=rca_result.confidence,
            reasoning=f"RCA identified {len(rca_result.contributing_factors)} contributing factors",
            metadata={
                "rca_result": {
                    "contributing_factors": rca_result.contributing_factors,
                    "recommendations": [r.dict() for r in rca_result.recommendations],
                    "similar_incidents_count": len(rca_result.similar_incidents)
                },
                "analyzer": "AIRootCauseAnalyzer"
            },
            correlation_id=self.correlation_id
        )

        return decision

    async def evaluate_confidence(self, decision: Decision) -> bool:
        """
        Evaluate if decision confidence meets threshold.

        Args:
            decision: Decision to evaluate

        Returns:
            True if confidence meets threshold, False otherwise
        """
        if not decision.confidence_score:
            return False

        return decision.confidence_score >= settings.ai.confidence_threshold
