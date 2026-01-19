"""
Vector similarity search for historical incidents.
"""

import logging
import random
from typing import List, Dict, Any
from uuid import UUID

from src.awfdrs.db.models.incidents import Incident
from src.awfdrs.ai.vectorstore.client import get_vector_client
from src.awfdrs.ai.agents.rca import SimilarIncident

logger = logging.getLogger(__name__)


class SimilaritySearch:
    """
    Vector similarity search for finding related incidents.

    Uses vector store (mocked) to find similar historical incidents.
    """

    def __init__(self) -> None:
        """Initialize similarity search."""
        self.vector_client = get_vector_client()

    async def index_incident(self, incident: Incident) -> None:
        """
        Index an incident in the vector store.

        Args:
            incident: Incident to index
        """
        logger.info(
            f"Indexing incident in vector store: {incident.id}",
            extra={"incident_id": str(incident.id)}
        )

        # Generate embedding (mock)
        embedding = await self.generate_embedding(incident)

        # Store in vector DB (mock implementation will just store metadata)
        metadata = {
            "incident_id": str(incident.id),
            "tenant_id": str(incident.tenant_id),
            "error_signature": incident.error_signature,
            "severity": incident.severity.value,
            "status": incident.status.value
        }

        # In mock implementation, this just stores in memory
        self.vector_client.upsert(
            vectors=[
                {
                    "id": str(incident.id),
                    "values": embedding,
                    "metadata": metadata
                }
            ]
        )

    async def find_similar(
        self,
        incident: Incident,
        top_k: int = 5
    ) -> List[SimilarIncident]:
        """
        Find similar incidents using vector similarity.

        Args:
            incident: Incident to find similar incidents for
            top_k: Number of results to return

        Returns:
            List of similar incidents with scores
        """
        logger.info(
            f"Finding similar incidents for: {incident.id}",
            extra={"incident_id": str(incident.id)}
        )

        # Generate embedding for query
        embedding = await self.generate_embedding(incident)

        # Query vector store (mock)
        results = self.vector_client.query(
            vector=embedding,
            top_k=top_k,
            filter={"tenant_id": str(incident.tenant_id)}
        )

        # Convert to SimilarIncident objects
        similar_incidents = []
        for match in results.get("matches", []):
            similar_incidents.append(SimilarIncident(
                incident_id=UUID(match["id"]),
                similarity_score=match["score"],
                error_signature=match["metadata"].get("error_signature", ""),
                metadata=match["metadata"]
            ))

        return similar_incidents

    async def generate_embedding(self, incident: Incident) -> List[float]:
        """
        Generate vector embedding for an incident.

        In mock mode, this returns a random vector.

        Args:
            incident: Incident to embed

        Returns:
            Vector embedding (list of floats)
        """
        # Mock implementation: generate deterministic random vector based on signature
        random.seed(incident.error_signature)
        embedding = [random.random() for _ in range(384)]  # 384-dimensional vector
        random.seed()  # Reset seed

        return embedding
