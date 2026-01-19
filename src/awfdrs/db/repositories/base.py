"""
Base repository with generic CRUD operations.
"""

from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing generic CRUD operations.

    Type parameter ModelType must be a subclass of BaseModel.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            session: Database session
        """
        self.model = model
        self.session = session

    async def get(self, id: UUID) -> Optional[ModelType]:
        """
        Get a single record by ID.

        Args:
            id: Record ID

        Returns:
            Model instance or None if not found
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        List records with optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of column:value filters

        Returns:
            List of model instances
        """
        query = select(self.model)

        if filters:
            for column, value in filters.items():
                if hasattr(self.model, column):
                    query = query.where(getattr(self.model, column) == value)

        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> ModelType:
        """
        Create a new record.

        Args:
            **kwargs: Model fields

        Returns:
            Created model instance
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: UUID, **kwargs: Any) -> Optional[ModelType]:
        """
        Update an existing record.

        Args:
            id: Record ID
            **kwargs: Fields to update

        Returns:
            Updated model instance or None if not found
        """
        instance = await self.get(id)
        if not instance:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: UUID) -> bool:
        """
        Delete a record.

        Args:
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        instance = await self.get(id)
        if not instance:
            return False

        await self.session.delete(instance)
        await self.session.commit()
        return True
