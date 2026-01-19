"""
Vector store client factory with mock implementation.
"""

from typing import Protocol, List, Dict, Any
from src.awfdrs.config import settings
from tests.mocks.mock_pinecone import MockPineconeClient


class BaseVectorClient(Protocol):
    """Base protocol for vector store clients."""

    def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filter: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Query vector store."""
        ...


def get_vector_client() -> BaseVectorClient:
    """
    Get vector store client instance.

    Returns mock client as this is a mock-only project.

    Returns:
        Vector store client instance

    Raises:
        ValueError: If mode is not 'mock'
    """
    if settings.ai.mode == "mock":
        return MockPineconeClient()
    else:
        raise ValueError(
            "Real API mode is disabled. This is a mock-only project. "
            "Set AI_MODE=mock in environment."
        )
