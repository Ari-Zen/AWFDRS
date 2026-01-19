"""
Seed script for populating database with initial data.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from uuid import UUID

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.awfdrs.db.session import AsyncSessionLocal
from src.awfdrs.db.models.tenants import Tenant
from src.awfdrs.db.models.workflows import Workflow
from src.awfdrs.db.models.vendors import Vendor
from src.awfdrs.db.models.events import Event
from src.awfdrs.core.enums import CircuitBreakerState
from src.awfdrs.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


# Fixed UUIDs for predictable testing
TENANT_ACME_ID = UUID("00000000-0000-0000-0000-000000000001")
TENANT_GLOBAL_ID = UUID("00000000-0000-0000-0000-000000000002")
TENANT_DISABLED_ID = UUID("00000000-0000-0000-0000-000000000003")

WORKFLOW_PAYMENT_ID = UUID("10000000-0000-0000-0000-000000000001")
WORKFLOW_ONBOARDING_ID = UUID("10000000-0000-0000-0000-000000000002")
WORKFLOW_COMPLIANCE_ID = UUID("10000000-0000-0000-0000-000000000003")
WORKFLOW_KILLED_ID = UUID("10000000-0000-0000-0000-000000000004")


async def seed_tenants(session) -> None:
    """Seed tenants."""
    logger.info("Seeding tenants...")

    tenants = [
        Tenant(
            id=TENANT_ACME_ID,
            name="Acme Corp",
            is_active=True,
            encryption_key_id="acme-key-001"
        ),
        Tenant(
            id=TENANT_GLOBAL_ID,
            name="Global Inc",
            is_active=True,
            encryption_key_id="global-key-001"
        ),
        Tenant(
            id=TENANT_DISABLED_ID,
            name="Disabled Co",
            is_active=False,
            encryption_key_id="disabled-key-001"
        ),
    ]

    for tenant in tenants:
        session.add(tenant)

    await session.commit()
    logger.info(f"Seeded {len(tenants)} tenants")


async def seed_workflows(session) -> None:
    """Seed workflows."""
    logger.info("Seeding workflows...")

    workflows = [
        Workflow(
            id=WORKFLOW_PAYMENT_ID,
            tenant_id=TENANT_ACME_ID,
            name="payment_processing",
            schema_version="1.0.0",
            config={"max_retries": 3, "timeout": 30},
            is_kill_switched=False
        ),
        Workflow(
            id=WORKFLOW_ONBOARDING_ID,
            tenant_id=TENANT_ACME_ID,
            name="user_onboarding",
            schema_version="1.0.0",
            config={"max_steps": 5},
            is_kill_switched=False
        ),
        Workflow(
            id=WORKFLOW_COMPLIANCE_ID,
            tenant_id=TENANT_GLOBAL_ID,
            name="compliance_check",
            schema_version="1.0.0",
            config={"strict_mode": True},
            is_kill_switched=False
        ),
        Workflow(
            id=WORKFLOW_KILLED_ID,
            tenant_id=TENANT_ACME_ID,
            name="killed_workflow",
            schema_version="1.0.0",
            config={},
            is_kill_switched=True
        ),
    ]

    for workflow in workflows:
        session.add(workflow)

    await session.commit()
    logger.info(f"Seeded {len(workflows)} workflows")


async def seed_vendors(session) -> None:
    """Seed vendors."""
    logger.info("Seeding vendors...")

    vendors = [
        Vendor(
            name="stripe",
            circuit_breaker_state=CircuitBreakerState.CLOSED,
            failure_count=0,
            last_success_at=datetime.utcnow()
        ),
        Vendor(
            name="plaid",
            circuit_breaker_state=CircuitBreakerState.CLOSED,
            failure_count=0,
            last_success_at=datetime.utcnow()
        ),
        Vendor(
            name="twilio",
            circuit_breaker_state=CircuitBreakerState.OPEN,
            failure_count=15,
            last_failure_at=datetime.utcnow()
        ),
    ]

    for vendor in vendors:
        session.add(vendor)

    await session.commit()
    logger.info(f"Seeded {len(vendors)} vendors")


async def seed_events(session) -> None:
    """Seed sample events."""
    logger.info("Seeding events...")

    events = [
        # Successful payment events
        Event(
            tenant_id=TENANT_ACME_ID,
            workflow_id=WORKFLOW_PAYMENT_ID,
            event_type="payment.completed",
            payload={
                "amount": 100.00,
                "currency": "USD",
                "payment_id": "pay_001"
            },
            idempotency_key="seed-payment-001",
            occurred_at=datetime.utcnow(),
            schema_version="1.0.0",
            correlation_id="seed-corr-001"
        ),
        Event(
            tenant_id=TENANT_ACME_ID,
            workflow_id=WORKFLOW_PAYMENT_ID,
            event_type="payment.completed",
            payload={
                "amount": 250.00,
                "currency": "USD",
                "payment_id": "pay_002"
            },
            idempotency_key="seed-payment-002",
            occurred_at=datetime.utcnow(),
            schema_version="1.0.0",
            correlation_id="seed-corr-002"
        ),
        # Failed payment events
        Event(
            tenant_id=TENANT_ACME_ID,
            workflow_id=WORKFLOW_PAYMENT_ID,
            event_type="payment.failed",
            payload={
                "amount": 500.00,
                "currency": "USD",
                "payment_id": "pay_003",
                "error_code": "insufficient_funds"
            },
            idempotency_key="seed-payment-003",
            occurred_at=datetime.utcnow(),
            schema_version="1.0.0",
            correlation_id="seed-corr-003"
        ),
        Event(
            tenant_id=TENANT_ACME_ID,
            workflow_id=WORKFLOW_PAYMENT_ID,
            event_type="payment.failed",
            payload={
                "amount": 150.00,
                "currency": "USD",
                "payment_id": "pay_004",
                "error_code": "card_declined"
            },
            idempotency_key="seed-payment-004",
            occurred_at=datetime.utcnow(),
            schema_version="1.0.0",
            correlation_id="seed-corr-004"
        ),
        # Onboarding events
        Event(
            tenant_id=TENANT_ACME_ID,
            workflow_id=WORKFLOW_ONBOARDING_ID,
            event_type="user.onboarding.started",
            payload={
                "user_id": "user_001",
                "email": "user1@example.com"
            },
            idempotency_key="seed-onboarding-001",
            occurred_at=datetime.utcnow(),
            schema_version="1.0.0",
            correlation_id="seed-corr-005"
        ),
    ]

    for event in events:
        session.add(event)

    await session.commit()
    logger.info(f"Seeded {len(events)} events")


async def main() -> None:
    """Run all seed functions."""
    logger.info("Starting data seeding...")

    async with AsyncSessionLocal() as session:
        try:
            await seed_tenants(session)
            await seed_workflows(session)
            await seed_vendors(session)
            await seed_events(session)

            logger.info("Data seeding complete!")

        except Exception as e:
            logger.error(f"Data seeding failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
