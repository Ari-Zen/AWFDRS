"""
Vendor repository for vendor-specific operations.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.vendors import Vendor
from src.awfdrs.db.repositories.base import BaseRepository
from src.awfdrs.core.enums import CircuitBreakerState


class VendorRepository(BaseRepository[Vendor]):
    """Repository for vendor operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository."""
        super().__init__(session, Vendor)

    async def get_by_name(self, name: str) -> Optional[Vendor]:
        """
        Get vendor by name.

        Args:
            name: Vendor name

        Returns:
            Vendor if found, None otherwise
        """
        stmt = select(Vendor).where(Vendor.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_circuit_breaker_state(
        self,
        vendor_id: UUID,
        state: CircuitBreakerState
    ) -> Optional[Vendor]:
        """
        Update circuit breaker state for a vendor.

        Args:
            vendor_id: Vendor ID
            state: New circuit breaker state

        Returns:
            Updated vendor if found, None otherwise
        """
        stmt = (
            update(Vendor)
            .where(Vendor.id == vendor_id)
            .values(circuit_breaker_state=state)
            .returning(Vendor)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def increment_failure_count(self, vendor_id: UUID) -> Optional[Vendor]:
        """
        Increment failure count for a vendor.

        Args:
            vendor_id: Vendor ID

        Returns:
            Updated vendor if found, None otherwise
        """
        vendor = await self.get(vendor_id)
        if vendor:
            vendor.failure_count += 1
            await self.session.commit()
            await self.session.refresh(vendor)
        return vendor

    async def reset_failure_count(self, vendor_id: UUID) -> Optional[Vendor]:
        """
        Reset failure count for a vendor.

        Args:
            vendor_id: Vendor ID

        Returns:
            Updated vendor if found, None otherwise
        """
        stmt = (
            update(Vendor)
            .where(Vendor.id == vendor_id)
            .values(failure_count=0)
            .returning(Vendor)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()
