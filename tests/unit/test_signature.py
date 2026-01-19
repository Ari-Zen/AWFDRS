"""
Unit tests for error signature generation.

Tests the signature generation logic used for grouping similar incidents.
"""

from uuid import UUID
from datetime import datetime
from src.awfdrs.analysis.signature import SignatureGenerator
from src.awfdrs.db.models.events import Event


def test_generate_signature_for_payment_timeout():
    """Test signature generation for payment timeout error."""
    # ARRANGE
    generator = SignatureGenerator()
    event = Event(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        tenant_id=UUID("10000000-0000-0000-0000-000000000001"),
        workflow_id=UUID("20000000-0000-0000-0000-000000000001"),
        event_type="payment.failed",
        payload={"error_code": "payment_timeout"},
        idempotency_key="test-001",
        occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # ACT
    signature = generator.generate(event)

    # ASSERT
    assert signature == "payment.failed:payment_timeout:20000000-0000-0000-0000-000000000001"
    assert isinstance(signature, str)


def test_generate_signature_normalizes_error_code_to_lowercase():
    """Test that error codes are normalized to lowercase."""
    # ARRANGE
    generator = SignatureGenerator()
    event = Event(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        tenant_id=UUID("10000000-0000-0000-0000-000000000001"),
        workflow_id=UUID("20000000-0000-0000-0000-000000000001"),
        event_type="order.failed",
        payload={"error_code": "TIMEOUT_ERROR"},
        idempotency_key="test-002",
        occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # ACT
    signature = generator.generate(event)

    # ASSERT
    assert "timeout_error" in signature
    assert "TIMEOUT_ERROR" not in signature


def test_generate_signature_handles_missing_error_code():
    """Test signature generation when error_code is missing from payload."""
    # ARRANGE
    generator = SignatureGenerator()
    event = Event(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        tenant_id=UUID("10000000-0000-0000-0000-000000000001"),
        workflow_id=UUID("20000000-0000-0000-0000-000000000001"),
        event_type="generic.error",
        payload={},  # No error_code
        idempotency_key="test-003",
        occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # ACT
    signature = generator.generate(event)

    # ASSERT
    assert "unknown" in signature or "generic.error" in signature


def test_generate_signature_includes_workflow_id():
    """Test that signature includes workflow_id for workflow-specific grouping."""
    # ARRANGE
    generator = SignatureGenerator()
    workflow_id = UUID("20000000-0000-0000-0000-000000000001")
    event = Event(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        tenant_id=UUID("10000000-0000-0000-0000-000000000001"),
        workflow_id=workflow_id,
        event_type="payment.failed",
        payload={"error_code": "timeout"},
        idempotency_key="test-004",
        occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # ACT
    signature = generator.generate(event)

    # ASSERT
    assert str(workflow_id) in signature


def test_same_error_pattern_generates_same_signature():
    """Test that identical error patterns produce identical signatures."""
    # ARRANGE
    generator = SignatureGenerator()
    workflow_id = UUID("20000000-0000-0000-0000-000000000001")

    event1 = Event(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        tenant_id=UUID("10000000-0000-0000-0000-000000000001"),
        workflow_id=workflow_id,
        event_type="payment.failed",
        payload={"error_code": "timeout"},
        idempotency_key="test-005",
        occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    event2 = Event(
        id=UUID("00000000-0000-0000-0000-000000000002"),
        tenant_id=UUID("10000000-0000-0000-0000-000000000001"),
        workflow_id=workflow_id,
        event_type="payment.failed",
        payload={"error_code": "timeout"},
        idempotency_key="test-006",
        occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # ACT
    signature1 = generator.generate(event1)
    signature2 = generator.generate(event2)

    # ASSERT
    assert signature1 == signature2


def test_different_workflows_generate_different_signatures():
    """Test that same error in different workflows produces different signatures."""
    # ARRANGE
    generator = SignatureGenerator()

    event1 = Event(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        tenant_id=UUID("10000000-0000-0000-0000-000000000001"),
        workflow_id=UUID("20000000-0000-0000-0000-000000000001"),
        event_type="payment.failed",
        payload={"error_code": "timeout"},
        idempotency_key="test-007",
        occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    event2 = Event(
        id=UUID("00000000-0000-0000-0000-000000000002"),
        tenant_id=UUID("10000000-0000-0000-0000-000000000001"),
        workflow_id=UUID("30000000-0000-0000-0000-000000000001"),  # Different workflow
        event_type="payment.failed",
        payload={"error_code": "timeout"},
        idempotency_key="test-008",
        occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # ACT
    signature1 = generator.generate(event1)
    signature2 = generator.generate(event2)

    # ASSERT
    assert signature1 != signature2
