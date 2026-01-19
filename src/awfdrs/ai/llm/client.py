"""
LLM client factory with mock implementation.
"""

from typing import Protocol
from src.awfdrs.config import settings
from tests.mocks.mock_openai import MockOpenAIClient


class BaseLLMClient(Protocol):
    """Base protocol for LLM clients."""

    chat: any


def get_llm_client() -> BaseLLMClient:
    """
    Get LLM client instance.

    Returns mock client as this is a mock-only project.

    Returns:
        LLM client instance

    Raises:
        ValueError: If mode is not 'mock'
    """
    if settings.ai.mode == "mock":
        return MockOpenAIClient()
    else:
        raise ValueError(
            "Real API mode is disabled. This is a mock-only project. "
            "Set AI_MODE=mock in environment."
        )
