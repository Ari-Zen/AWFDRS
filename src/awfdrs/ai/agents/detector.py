"""
AI error detection agent.
"""

import json
import logging
from typing import Dict, Any
from pydantic import BaseModel

from src.awfdrs.db.models.events import Event
from src.awfdrs.ai.llm.client import get_llm_client
from src.awfdrs.core.enums import ErrorSeverity

logger = logging.getLogger(__name__)


class ErrorClassification(BaseModel):
    """Error classification result."""

    error_type: str
    severity: ErrorSeverity
    confidence: float
    reasoning: str


class DetectionResult(BaseModel):
    """AI detection result."""

    classification: ErrorClassification
    should_analyze: bool
    metadata: Dict[str, Any]


class AIErrorDetector:
    """
    AI agent for analyzing events and detecting anomalies.

    Uses LLM to classify errors and determine severity.
    """

    def __init__(self) -> None:
        """Initialize AI error detector."""
        self.llm_client = get_llm_client()

    async def analyze_event(self, event: Event) -> DetectionResult:
        """
        Analyze an event for errors using AI.

        Args:
            event: Event to analyze

        Returns:
            Detection result with classification
        """
        logger.info(
            f"AI analyzing event: {event.id}",
            extra={"event_id": str(event.id)}
        )

        # Build prompt for LLM
        prompt = self._build_detection_prompt(event)

        # Query LLM (mock will return deterministic response)
        response = self.llm_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing workflow errors and failures."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        # Parse response
        content = response.choices[0].message["content"]
        result_data = json.loads(content)

        # Create classification
        classification = ErrorClassification(
            error_type=result_data.get("error_type", "unknown"),
            severity=ErrorSeverity(result_data.get("severity", "medium")),
            confidence=result_data.get("confidence", 0.5),
            reasoning=result_data.get("reasoning", "")
        )

        # Determine if should continue analysis
        should_analyze = classification.confidence >= 0.6

        return DetectionResult(
            classification=classification,
            should_analyze=should_analyze,
            metadata={
                "hypothesis": result_data.get("hypothesis", ""),
                "suggested_action": result_data.get("suggested_action", "")
            }
        )

    async def classify_error(self, event: Event) -> ErrorClassification:
        """
        Classify an error from an event.

        Args:
            event: Event to classify

        Returns:
            Error classification
        """
        result = await self.analyze_event(event)
        return result.classification

    async def calculate_confidence(self, event: Event) -> float:
        """
        Calculate confidence score for error detection.

        Args:
            event: Event to analyze

        Returns:
            Confidence score (0-1)
        """
        result = await self.analyze_event(event)
        return result.classification.confidence

    def _build_detection_prompt(self, event: Event) -> str:
        """
        Build LLM prompt for error detection.

        Args:
            event: Event to analyze

        Returns:
            Prompt string
        """
        return f"""Analyze this workflow event for errors:

Event Type: {event.event_type}
Payload: {json.dumps(event.payload, indent=2)}
Occurred At: {event.occurred_at}

Classify the error type, determine severity (low/medium/high/critical), and provide a confidence score (0-1).
Return JSON with: error_type, severity, confidence, reasoning, hypothesis, suggested_action
"""
