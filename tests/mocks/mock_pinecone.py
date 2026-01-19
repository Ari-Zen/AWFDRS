"""
Mock Pinecone vector database client for testing.
Returns deterministic similarity search results without making real API calls.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import random


@dataclass
class MockMatch:
    """Mock vector similarity match."""

    id: str
    score: float
    metadata: Dict[str, Any]


@dataclass
class MockQueryResponse:
    """Mock query response."""

    matches: List[MockMatch]
    namespace: str = ""


class MockPineconeIndex:
    """
    Mock Pinecone index that simulates vector similarity search.
    Stores vectors in memory and returns mock similarity results.
    """

    def __init__(self, name: str) -> None:
        """Initialize mock index."""
        self.name = name
        self._vectors: Dict[str, Dict[str, Any]] = {}

    def upsert(
        self,
        vectors: List[Any],
        namespace: str = ""
    ) -> Dict[str, int]:
        """
        Mock upsert operation.

        Args:
            vectors: List of vector data (tuples or dicts)
            namespace: Namespace for vectors

        Returns:
            Dictionary with upserted count
        """
        for vector_data in vectors:
            # Handle both dict format and tuple format
            if isinstance(vector_data, dict):
                vector_id = vector_data.get("id")
                vector_values = vector_data.get("values", [])
                metadata = vector_data.get("metadata", {})
            else:
                # Tuple format: (id, values, metadata)
                vector_id = vector_data[0]
                vector_values = vector_data[1] if len(vector_data) > 1 else []
                metadata = vector_data[2] if len(vector_data) > 2 else {}

            self._vectors[vector_id] = {
                "values": vector_values,
                "metadata": metadata,
                "namespace": namespace
            }

        return {"upserted_count": len(vectors)}

    def query(
        self,
        vector: Optional[List[float]] = None,
        id: Optional[str] = None,
        top_k: int = 5,
        namespace: str = "",
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Mock query operation.

        Returns deterministic similarity results based on stored vectors.

        Args:
            vector: Query vector
            id: Query by ID instead of vector
            top_k: Number of results to return
            namespace: Namespace to query
            filter: Metadata filter
            include_metadata: Whether to include metadata

        Returns:
            Dictionary with matches list
        """
        # Generate mock matches with decreasing similarity scores
        matches = []

        if not self._vectors:
            # Return default mock matches if no vectors stored
            mock_matches = self._get_default_matches(top_k)
            matches = [{"id": m.id, "score": m.score, "metadata": m.metadata} for m in mock_matches]
        else:
            # Return matches from stored vectors
            stored_ids = list(self._vectors.keys())
            for i in range(min(top_k, len(stored_ids))):
                vector_id = stored_ids[i]
                vector_data = self._vectors[vector_id]

                # Apply filter if provided
                if filter:
                    metadata = vector_data.get("metadata", {})
                    # Simple filter check
                    if not all(metadata.get(k) == v for k, v in filter.items()):
                        continue

                # Generate mock similarity score (higher for earlier results)
                score = 0.95 - (i * 0.1)

                matches.append({
                    "id": vector_id,
                    "score": score,
                    "metadata": vector_data.get("metadata", {})
                })

        return {"matches": matches, "namespace": namespace}

    def _get_default_matches(self, top_k: int) -> List[MockMatch]:
        """Generate default mock matches."""
        matches = []
        for i in range(top_k):
            matches.append(MockMatch(
                id=f"mock-incident-{i:03d}",
                score=0.90 - (i * 0.08),
                metadata={
                    "error_code": "PAYMENT_FAILED",
                    "vendor": "stripe",
                    "timestamp": "2026-01-19T10:00:00Z",
                    "resolution": "retry_successful" if i % 2 == 0 else "escalated"
                }
            ))
        return matches

    def delete(
        self,
        ids: Optional[List[str]] = None,
        delete_all: bool = False,
        namespace: str = ""
    ) -> Dict[str, Any]:
        """Mock delete operation."""
        if delete_all:
            count = len(self._vectors)
            self._vectors.clear()
            return {"deleted_count": count}

        if ids:
            count = 0
            for vector_id in ids:
                if vector_id in self._vectors:
                    del self._vectors[vector_id]
                    count += 1
            return {"deleted_count": count}

        return {"deleted_count": 0}

    def describe_index_stats(self) -> Dict[str, Any]:
        """Mock index stats."""
        return {
            "dimension": 1536,
            "index_fullness": 0.1,
            "namespaces": {
                "": {
                    "vector_count": len(self._vectors)
                }
            },
            "total_vector_count": len(self._vectors)
        }


class MockPineconeClient:
    """
    Mock Pinecone client.
    No real API calls are made.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize mock client."""
        self.api_key = api_key or "mock-api-key"
        self._indexes: Dict[str, MockPineconeIndex] = {}

    def Index(self, name: str) -> MockPineconeIndex:
        """Get or create a mock index."""
        if name not in self._indexes:
            self._indexes[name] = MockPineconeIndex(name)
        return self._indexes[name]

    def list_indexes(self) -> List[str]:
        """List all mock indexes."""
        return list(self._indexes.keys())

    def create_index(
        self,
        name: str,
        dimension: int,
        metric: str = "cosine",
        **kwargs: Any
    ) -> None:
        """Create a mock index."""
        self._indexes[name] = MockPineconeIndex(name)

    def delete_index(self, name: str) -> None:
        """Delete a mock index."""
        if name in self._indexes:
            del self._indexes[name]


def get_mock_pinecone_client() -> MockPineconeClient:
    """Get a mock Pinecone client instance."""
    return MockPineconeClient()
