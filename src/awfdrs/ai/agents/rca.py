"""
AI root cause analysis agent.
"""

import json
import logging
from typing import List, Dict, Any
from pydantic import BaseModel
from uuid import UUID

from src.awfdrs.db.models.incidents import Incident
from src.awfdrs.ai.llm.client import get_llm_client
from src.awfdrs.ai.similarity.search import SimilaritySearch
from src.awfdrs.core.enums import ActionType

logger = logging.getLogger(__name__)


class SimilarIncident(BaseModel):
    """Similar incident from history."""

    incident_id: UUID
    similarity_score: float
    error_signature: str
    metadata: Dict[str, Any]


class ActionRecommendation(BaseModel):
    """Recommended action."""

    action_type: ActionType
    confidence: float
    reasoning: str
    parameters: Dict[str, Any]


class RCAResult(BaseModel):
    """Root cause analysis result."""

    root_cause: str
    confidence: float
    contributing_factors: List[str]
    recommendations: List[ActionRecommendation]
    similar_incidents: List[SimilarIncident]
    metadata: Dict[str, Any]


class AIRootCauseAnalyzer:
    """
    AI agent for performing root cause analysis on incidents.

    Uses LLM and historical incident data to generate hypotheses.
    """

    def __init__(self) -> None:
        """Initialize RCA analyzer."""
        self.llm_client = get_llm_client()
        self.similarity_search = SimilaritySearch()

    async def analyze_incident(self, incident: Incident) -> RCAResult:
        """
        Perform root cause analysis on an incident.

        Args:
            incident: Incident to analyze

        Returns:
            RCA result with hypothesis and recommendations
        """
        logger.info(
            f"AI performing RCA on incident: {incident.id}",
            extra={"incident_id": str(incident.id)}
        )

        # Find similar historical incidents
        similar = await self.find_similar_incidents(incident)

        # Generate hypothesis using LLM
        hypothesis = await self.generate_hypothesis(incident, {
            "similar_incidents": [s.dict() for s in similar]
        })

        # Parse LLM response
        rca_data = json.loads(hypothesis)

        # Generate action recommendations
        recommendations = await self.recommend_actions(rca_data)

        return RCAResult(
            root_cause=rca_data.get("root_cause", "Unknown"),
            confidence=rca_data.get("confidence", 0.5),
            contributing_factors=rca_data.get("contributing_factors", []),
            recommendations=recommendations,
            similar_incidents=similar,
            metadata={
                "analysis_timestamp": str(incident.updated_at),
                "correlated_events_count": len(incident.correlated_event_ids)
            }
        )

    async def find_similar_incidents(
        self,
        incident: Incident,
        top_k: int = 5
    ) -> List[SimilarIncident]:
        """
        Find similar historical incidents.

        Args:
            incident: Current incident
            top_k: Number of similar incidents to return

        Returns:
            List of similar incidents
        """
        similar_results = await self.similarity_search.find_similar(incident, top_k)
        return similar_results

    async def generate_hypothesis(
        self,
        incident: Incident,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate root cause hypothesis using LLM.

        Args:
            incident: Incident to analyze
            context: Additional context (similar incidents, etc.)

        Returns:
            JSON string with RCA results
        """
        prompt = self._build_rca_prompt(incident, context)

        response = self.llm_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at root cause analysis for system failures."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        return response.choices[0].message["content"]

    async def recommend_actions(self, rca_data: Dict[str, Any]) -> List[ActionRecommendation]:
        """
        Generate action recommendations from RCA.

        Args:
            rca_data: RCA analysis data

        Returns:
            List of recommended actions
        """
        recommendations = rca_data.get("recommendations", [])
        action_recs = []

        for rec in recommendations:
            # Map recommendation to action type
            action_type = self._map_to_action_type(rec)

            action_recs.append(ActionRecommendation(
                action_type=action_type,
                confidence=rca_data.get("confidence", 0.5),
                reasoning=rec,
                parameters={}
            ))

        return action_recs

    def _map_to_action_type(self, recommendation: str) -> ActionType:
        """Map recommendation text to action type."""
        rec_lower = recommendation.lower()

        if "retry" in rec_lower or "re-run" in rec_lower:
            return ActionType.RETRY
        elif "escalate" in rec_lower or "notify" in rec_lower:
            return ActionType.ESCALATE
        elif "circuit breaker" in rec_lower or "disable" in rec_lower:
            return ActionType.CIRCUIT_BREAKER
        else:
            return ActionType.NOTIFY

    def _build_rca_prompt(self, incident: Incident, context: Dict[str, Any]) -> str:
        """Build LLM prompt for RCA."""
        similar_incidents_str = json.dumps(context.get("similar_incidents", []), indent=2)

        return f"""Perform root cause analysis on this incident:

Incident ID: {incident.id}
Error Signature: {incident.error_signature}
Status: {incident.status}
Severity: {incident.severity}
Correlated Events: {len(incident.correlated_event_ids)}
Metadata: {json.dumps(incident.metadata, indent=2)}

Similar Historical Incidents:
{similar_incidents_str}

Analyze the root cause, identify contributing factors, and provide recommendations.
Return JSON with: root_cause, confidence (0-1), contributing_factors (array), recommendations (array)
"""
