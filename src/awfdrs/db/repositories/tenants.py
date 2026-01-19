"""
Tenant repository for tenant management.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.tenants import Tenant
from src.awfdrs.db.repositories.base import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    """Repository for tenant operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository."""
        super().__init__(Tenant, session)

    async def get_by_name(self, name: str) -> Optional[Tenant]:
        """
        Get tenant by name.

        Args:
            name: Tenant name

        Returns:
            Tenant or None
        """
        result = await self.session.execute(
            select(Tenant).where(Tenant.name == name)
        )
        return result.scalar_one_or_none()

    async def is_active(self, tenant_id: UUID) -> bool:
        """
        Check if tenant is active.

        Args:
            tenant_id: Tenant ID

        Returns:
            True if active, False otherwise
        """
        tenant = await self.get(tenant_id)
        return tenant is not None and tenant.is_active
