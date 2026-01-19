"""
Workflow repository for workflow management.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.models.workflows import Workflow
from src.awfdrs.db.repositories.base import BaseRepository


class WorkflowRepository(BaseRepository[Workflow]):
    """Repository for workflow operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository."""
        super().__init__(Workflow, session)

    async def get_by_name(
        self,
        tenant_id: UUID,
        name: str
    ) -> Optional[Workflow]:
        """
        Get workflow by name for a tenant.

        Args:
            tenant_id: Tenant ID
            name: Workflow name

        Returns:
            Workflow or None
        """
        result = await self.session.execute(
            select(Workflow)
            .where(Workflow.tenant_id == tenant_id)
            .where(Workflow.name == name)
        )
        return result.scalar_one_or_none()

    async def is_kill_switched(self, workflow_id: UUID) -> bool:
        """
        Check if workflow is kill-switched.

        Args:
            workflow_id: Workflow ID

        Returns:
            True if kill-switched, False otherwise
        """
        workflow = await self.get(workflow_id)
        return workflow is not None and workflow.is_kill_switched
