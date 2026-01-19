"""
Mock OpenAI client for testing.
Returns deterministic responses without making real API calls.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import json


@dataclass
class MockChoice:
    """Mock choice object."""

    message: Dict[str, Any]
    index: int = 0
    finish_reason: str = "stop"


@dataclass
class MockChatCompletion:
    """Mock chat completion response."""

    id: str
    choices: List[MockChoice]
    model: str = "gpt-4"
    object: str = "chat.completion"


class MockChatCompletions:
    """Mock chat completions API."""

    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs: Any
    ) -> MockChatCompletion:
        """
        Create a mock chat completion.

        Returns deterministic responses based on message content.
        """
        # Extract the last user message
        user_messages = [m for m in messages if m.get("role") == "user"]
        last_message = user_messages[-1]["content"] if user_messages else ""

        # Determine response based on content
        if "error" in last_message.lower() or "failure" in last_message.lower():
            response_content = self._error_analysis_response()
        elif "root cause" in last_message.lower() or "rca" in last_message.lower():
            response_content = self._root_cause_response()
        elif "similar" in last_message.lower():
            response_content = self._similarity_response()
        else:
            response_content = self._default_response()

        return MockChatCompletion(
            id="mock-completion-id",
            choices=[
                MockChoice(
                    message={
                        "role": "assistant",
                        "content": json.dumps(response_content)
                    }
                )
            ]
        )

    def _error_analysis_response(self) -> Dict[str, Any]:
        """Return mock error analysis."""
        return {
            "error_type": "payment_processing_error",
            "severity": "high",
            "confidence": 0.85,
            "hypothesis": "Payment gateway timeout due to network congestion",
            "suggested_action": "retry",
            "reasoning": "Similar pattern observed in historical incidents"
        }

    def _root_cause_response(self) -> Dict[str, Any]:
        """Return mock root cause analysis."""
        return {
            "root_cause": "Database connection pool exhaustion",
            "confidence": 0.78,
            "contributing_factors": [
                "High concurrent user load",
                "Inefficient query patterns",
                "Insufficient connection pool size"
            ],
            "recommendations": [
                "Increase connection pool size",
                "Optimize database queries",
                "Implement connection pooling monitoring"
            ]
        }

    def _similarity_response(self) -> Dict[str, Any]:
        """Return mock similarity analysis."""
        return {
            "is_similar": True,
            "confidence": 0.82,
            "similar_incidents": [
                "incident-001",
                "incident-042"
            ],
            "common_patterns": [
                "Same error code",
                "Same vendor",
                "Similar time of day"
            ]
        }

    def _default_response(self) -> Dict[str, Any]:
        """Return default mock response."""
        return {
            "status": "analyzed",
            "confidence": 0.75,
            "message": "Mock AI analysis completed"
        }


class MockChat:
    """Mock chat API."""

    def __init__(self) -> None:
        self.completions = MockChatCompletions()


class MockOpenAIClient:
    """
    Mock OpenAI client that returns deterministic responses.
    No real API calls are made.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize mock client."""
        self.api_key = api_key or "mock-api-key"
        self.chat = MockChat()


def get_mock_openai_client() -> MockOpenAIClient:
    """Get a mock OpenAI client instance."""
    return MockOpenAIClient()
