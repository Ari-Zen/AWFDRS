"""
Database initialization script.
Creates all tables and runs migrations.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.awfdrs.db.session import init_db, engine
from src.awfdrs.db.base import Base
from src.awfdrs.core.logging import setup_logging, get_logger

# Import all models to ensure they're registered
from src.awfdrs.db.models import (
    Tenant,
    Workflow,
    Vendor,
    Event,
    Incident,
    Decision,
    Action,
    KillSwitch,
)

setup_logging()
logger = get_logger(__name__)


async def main() -> None:
    """Initialize database."""
    logger.info("Starting database initialization...")

    try:
        # Create all tables
        async with engine.begin() as conn:
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")

        logger.info("Database initialization complete!")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
