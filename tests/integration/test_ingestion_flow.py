"""
Integration tests for event ingestion flow.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime
from uuid import uuid4

from src.awfdrs.db.models.tenants import Tenant
from src.awfdrs.db.models.workflows import Workflow
from tests.fixtures.events import TENANT_ACME, WORKFLOW_PAYMENT


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ingest_valid_event(client: AsyncClient, db_session):
    """Test ingesting a valid event."""
    # Setup: Create tenant and workflow
    tenant = Tenant(
        id=TENANT_ACME,
        name="Test Tenant",
        is_active=True
    )
    db_session.add(tenant)

    workflow = Workflow(
        id=WORKFLOW_PAYMENT,
        tenant_id=TENANT_ACME,
        name="test_workflow",
        is_kill_switched=False
    )
    db_session.add(workflow)
    await db_session.commit()

    # Test: Submit event
    event_data = {
        "tenant_id": str(TENANT_ACME),
        "workflow_id": str(WORKFLOW_PAYMENT),
        "event_type": "payment.completed",
        "payload": {
            "amount": 100.00,
            "currency": "USD"
        },
        "idempotency_key": f"test-{uuid4()}",
        "occurred_at": datetime.utcnow().isoformat(),
        "schema_version": "1.0.0"
    }

    response = await client.post("/api/v1/events", json=event_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "accepted"
    assert "event_id" in data
    assert "correlation_id" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ingest_duplicate_idempotency_key(client: AsyncClient, db_session):
    """Test that duplicate idempotency key returns 409."""
    # Setup
    tenant = Tenant(id=TENANT_ACME, name="Test Tenant", is_active=True)
    db_session.add(tenant)

    workflow = Workflow(
        id=WORKFLOW_PAYMENT,
        tenant_id=TENANT_ACME,
        name="test_workflow",
        is_kill_switched=False
    )
    db_session.add(workflow)
    await db_session.commit()

    idempotency_key = f"test-duplicate-{uuid4()}"

    event_data = {
        "tenant_id": str(TENANT_ACME),
        "workflow_id": str(WORKFLOW_PAYMENT),
        "event_type": "payment.completed",
        "payload": {"amount": 100.00},
        "idempotency_key": idempotency_key,
        "occurred_at": datetime.utcnow().isoformat(),
        "schema_version": "1.0.0"
    }

    # First submission should succeed
    response1 = await client.post("/api/v1/events", json=event_data)
    assert response1.status_code == 201

    # Second submission with same idempotency key should fail
    response2 = await client.post("/api/v1/events", json=event_data)
    assert response2.status_code == 409


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ingest_invalid_tenant(client: AsyncClient, db_session):
    """Test that invalid tenant returns 404."""
    event_data = {
        "tenant_id": str(uuid4()),  # Non-existent tenant
        "workflow_id": str(uuid4()),
        "event_type": "test.event",
        "payload": {"test": "data"},
        "idempotency_key": f"test-{uuid4()}",
        "occurred_at": datetime.utcnow().isoformat(),
        "schema_version": "1.0.0"
    }

    response = await client.post("/api/v1/events", json=event_data)
    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ingest_kill_switched_workflow(client: AsyncClient, db_session):
    """Test that kill-switched workflow returns 403."""
    # Setup
    tenant = Tenant(id=TENANT_ACME, name="Test Tenant", is_active=True)
    db_session.add(tenant)

    workflow = Workflow(
        id=WORKFLOW_PAYMENT,
        tenant_id=TENANT_ACME,
        name="test_workflow",
        is_kill_switched=True  # Kill switch active
    )
    db_session.add(workflow)
    await db_session.commit()

    event_data = {
        "tenant_id": str(TENANT_ACME),
        "workflow_id": str(WORKFLOW_PAYMENT),
        "event_type": "test.event",
        "payload": {"test": "data"},
        "idempotency_key": f"test-{uuid4()}",
        "occurred_at": datetime.utcnow().isoformat(),
        "schema_version": "1.0.0"
    }

    response = await client.post("/api/v1/events", json=event_data)
    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ingest_invalid_schema_version(client: AsyncClient, db_session):
    """Test that invalid schema version returns 422."""
    tenant = Tenant(id=TENANT_ACME, name="Test Tenant", is_active=True)
    db_session.add(tenant)

    workflow = Workflow(
        id=WORKFLOW_PAYMENT,
        tenant_id=TENANT_ACME,
        name="test_workflow",
        is_kill_switched=False
    )
    db_session.add(workflow)
    await db_session.commit()

    event_data = {
        "tenant_id": str(TENANT_ACME),
        "workflow_id": str(WORKFLOW_PAYMENT),
        "event_type": "test.event",
        "payload": {"test": "data"},
        "idempotency_key": f"test-{uuid4()}",
        "occurred_at": datetime.utcnow().isoformat(),
        "schema_version": "99.0.0"  # Invalid version
    }

    response = await client.post("/api/v1/events", json=event_data)
    assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient):
    """Test readiness check endpoint."""
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert data["database"] == "ok"
