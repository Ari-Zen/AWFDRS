"""
Sample event data for testing.
"""

from datetime import datetime
from uuid import UUID, uuid4


# Sample tenant IDs
TENANT_ACME = UUID("00000000-0000-0000-0000-000000000001")
TENANT_GLOBAL = UUID("00000000-0000-0000-0000-000000000002")

# Sample workflow IDs
WORKFLOW_PAYMENT = UUID("10000000-0000-0000-0000-000000000001")
WORKFLOW_ONBOARDING = UUID("10000000-0000-0000-0000-000000000002")
WORKFLOW_COMPLIANCE = UUID("10000000-0000-0000-0000-000000000003")


def sample_payment_success_event(idempotency_key: str = None) -> dict:
    """Generate a sample successful payment event."""
    return {
        "tenant_id": str(TENANT_ACME),
        "workflow_id": str(WORKFLOW_PAYMENT),
        "event_type": "payment.completed",
        "payload": {
            "payment_id": "pay_12345",
            "amount": 100.00,
            "currency": "USD",
            "status": "succeeded",
            "payment_method": "card",
            "customer_id": "cust_67890"
        },
        "idempotency_key": idempotency_key or f"test-payment-success-{uuid4()}",
        "occurred_at": datetime.utcnow().isoformat(),
        "schema_version": "1.0.0"
    }


def sample_payment_failed_event(
    idempotency_key: str = None,
    error_code: str = "card_declined"
) -> dict:
    """Generate a sample failed payment event."""
    return {
        "tenant_id": str(TENANT_ACME),
        "workflow_id": str(WORKFLOW_PAYMENT),
        "event_type": "payment.failed",
        "payload": {
            "payment_id": "pay_12346",
            "amount": 100.00,
            "currency": "USD",
            "status": "failed",
            "error_code": error_code,
            "error_message": "Payment processing failed",
            "payment_method": "card",
            "customer_id": "cust_67890",
            "retry_count": 0
        },
        "idempotency_key": idempotency_key or f"test-payment-failed-{uuid4()}",
        "occurred_at": datetime.utcnow().isoformat(),
        "schema_version": "1.0.0"
    }


def sample_onboarding_event(idempotency_key: str = None) -> dict:
    """Generate a sample user onboarding event."""
    return {
        "tenant_id": str(TENANT_ACME),
        "workflow_id": str(WORKFLOW_ONBOARDING),
        "event_type": "user.onboarding.started",
        "payload": {
            "user_id": "user_11111",
            "email": "test@example.com",
            "step": "email_verification",
            "status": "in_progress"
        },
        "idempotency_key": idempotency_key or f"test-onboarding-{uuid4()}",
        "occurred_at": datetime.utcnow().isoformat(),
        "schema_version": "1.0.0"
    }


def sample_api_call_failed_event(
    idempotency_key: str = None,
    vendor: str = "stripe"
) -> dict:
    """Generate a sample API call failure event."""
    return {
        "tenant_id": str(TENANT_ACME),
        "workflow_id": str(WORKFLOW_PAYMENT),
        "event_type": "api_call.failed",
        "payload": {
            "vendor": vendor,
            "endpoint": "/v1/payment_intents",
            "method": "POST",
            "status_code": 500,
            "error_code": "internal_server_error",
            "error_message": "The server encountered an internal error",
            "request_id": "req_xyz123",
            "retry_count": 0
        },
        "idempotency_key": idempotency_key or f"test-api-failed-{uuid4()}",
        "occurred_at": datetime.utcnow().isoformat(),
        "schema_version": "1.0.0"
    }


def sample_timeout_event(idempotency_key: str = None) -> dict:
    """Generate a sample timeout event."""
    return {
        "tenant_id": str(TENANT_ACME),
        "workflow_id": str(WORKFLOW_PAYMENT),
        "event_type": "api_call.failed",
        "payload": {
            "vendor": "plaid",
            "endpoint": "/accounts/balance/get",
            "method": "POST",
            "error_code": "timeout",
            "error_message": "Request timed out after 30 seconds",
            "timeout_duration": 30,
            "retry_count": 1
        },
        "idempotency_key": idempotency_key or f"test-timeout-{uuid4()}",
        "occurred_at": datetime.utcnow().isoformat(),
        "schema_version": "1.0.0"
    }


def sample_rate_limit_event(idempotency_key: str = None) -> dict:
    """Generate a sample rate limit event."""
    return {
        "tenant_id": str(TENANT_ACME),
        "workflow_id": str(WORKFLOW_PAYMENT),
        "event_type": "api_call.failed",
        "payload": {
            "vendor": "twilio",
            "endpoint": "/Messages.json",
            "method": "POST",
            "status_code": 429,
            "error_code": "rate_limit_exceeded",
            "error_message": "Too many requests",
            "retry_after": 60,
            "retry_count": 0
        },
        "idempotency_key": idempotency_key or f"test-rate-limit-{uuid4()}",
        "occurred_at": datetime.utcnow().isoformat(),
        "schema_version": "1.0.0"
    }


def sample_compliance_check_event(idempotency_key: str = None) -> dict:
    """Generate a sample compliance check event."""
    return {
        "tenant_id": str(TENANT_GLOBAL),
        "workflow_id": str(WORKFLOW_COMPLIANCE),
        "event_type": "compliance.check.completed",
        "payload": {
            "check_id": "check_22222",
            "user_id": "user_33333",
            "check_type": "kyc_verification",
            "status": "passed",
            "risk_score": 25
        },
        "idempotency_key": idempotency_key or f"test-compliance-{uuid4()}",
        "occurred_at": datetime.utcnow().isoformat(),
        "schema_version": "1.0.0"
    }


# Collection of all sample events
SAMPLE_EVENTS = {
    "payment_success": sample_payment_success_event,
    "payment_failed": sample_payment_failed_event,
    "onboarding": sample_onboarding_event,
    "api_failed": sample_api_call_failed_event,
    "timeout": sample_timeout_event,
    "rate_limit": sample_rate_limit_event,
    "compliance": sample_compliance_check_event,
}
