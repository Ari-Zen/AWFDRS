"""
Incident repository for incident management.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.incidents import Incident
from src.awfdrs.db.repositories.base import BaseRepository
from src.awfdrs.core.enums import IncidentStatus


class IncidentRepository(BaseRepository[Incident]):
    """Repository for incident operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository."""
        super().__init__(Incident, session)

    async def get_active_by_signature(
        self,
        tenant_id: UUID,
        error_signature: str
    ) -> Optional[Incident]:
        """
        Get active incident by error signature.

        Args:
            tenant_id: Tenant ID
            error_signature: Error signature

        Returns:
            Active incident or None
        """
        result = await self.session.execute(
            select(Incident)
            .where(Incident.tenant_id == tenant_id)
            .where(Incident.error_signature == error_signature)
            .where(Incident.status == IncidentStatus.DETECTED)
            .order_by(Incident.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        incident_id: UUID,
        status: IncidentStatus,
        resolution_notes: Optional[str] = None
    ) -> Optional[Incident]:
        """
        Update incident status.

        Args:
            incident_id: Incident ID
            status: New status
            resolution_notes: Optional resolution notes

        Returns:
            Updated incident or None
        """
        update_data = {"status": status}
        if resolution_notes:
            update_data["resolution_notes"] = resolution_notes

        return await self.update(incident_id, **update_data)

    async def list_by_status(
        self,
        tenant_id: UUID,
        status: IncidentStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Incident]:
        """
        List incidents by status.

        Args:
            tenant_id: Tenant ID
            status: Incident status
            skip: Number to skip
            limit: Maximum to return

        Returns:
            List of incidents
        """
        result = await self.session.execute(
            select(Incident)
            .where(Incident.tenant_id == tenant_id)
            .where(Incident.status == status)
            .order_by(Incident.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
