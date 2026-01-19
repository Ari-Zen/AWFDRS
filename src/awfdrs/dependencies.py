"""
FastAPI dependencies.
"""

from typing import AsyncGenerator
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.session import get_db


async def get_correlation_id(request: Request) -> str:
    """
    Get correlation ID from request state.

    Args:
        request: FastAPI request

    Returns:
        Correlation ID
    """
    return getattr(request.state, "correlation_id", "unknown")


async def get_db_session(
    session: AsyncSession = Depends(get_db)
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session dependency.

    Args:
        session: Database session

    Yields:
        Database session
    """
    yield session
