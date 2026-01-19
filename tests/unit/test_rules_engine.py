"""
Unit tests for safety rules engine.

Tests error severity evaluation and retry policy determination.
"""

import pytest
from src.awfdrs.safety.rules_engine import RulesEngine


@pytest.fixture
def rules_engine():
    """Provide RulesEngine instance for tests."""
    return RulesEngine()


def test_get_error_severity_for_payment_timeout(rules_engine):
    """Test severity lookup for payment timeout error."""
    # ACT
    severity = rules_engine.get_error_severity("payment_timeout")

    # ASSERT
    assert severity in ["low", "medium", "high", "critical"]
    assert severity == "high"  # Based on config/rules/error_codes.yaml


def test_get_error_severity_for_unknown_code_returns_default(rules_engine):
    """Test that unknown error codes return default medium severity."""
    # ACT
    severity = rules_engine.get_error_severity("unknown_error_code_xyz")

    # ASSERT
    assert severity == "medium"  # Default fallback


def test_get_retry_policy_for_retryable_error(rules_engine):
    """Test retry policy lookup for retryable error."""
    # ACT
    policy = rules_engine.get_retry_policy("payment_timeout")

    # ASSERT
    assert policy is not None
    assert "retryable" in policy
    assert policy["retryable"] is True
    assert policy["max_retries"] > 0


def test_get_retry_policy_for_non_retryable_error(rules_engine):
    """Test retry policy for non-retryable error (e.g., validation error)."""
    # ACT
    policy = rules_engine.get_retry_policy("invalid_card")

    # ASSERT
    assert policy is not None
    assert policy["retryable"] is False
    assert policy["max_retries"] == 0


def test_is_retryable_returns_true_for_transient_errors(rules_engine):
    """Test that transient errors are marked as retryable."""
    # ACT
    result = rules_engine.is_retryable("payment_timeout")

    # ASSERT
    assert result is True


def test_is_retryable_returns_false_for_permanent_errors(rules_engine):
    """Test that permanent errors are not retryable."""
    # ACT
    result = rules_engine.is_retryable("invalid_card")

    # ASSERT
    assert result is False


def test_get_retry_policy_includes_backoff_configuration(rules_engine):
    """Test that retry policy includes backoff parameters."""
    # ACT
    policy = rules_engine.get_retry_policy("payment_timeout")

    # ASSERT
    if policy["retryable"]:
        assert "initial_delay_seconds" in policy
        assert "max_delay_seconds" in policy
        assert "backoff_multiplier" in policy


@pytest.mark.parametrize("error_code,expected_severity", [
    ("payment_timeout", "high"),
    ("network_error", "medium"),
    ("validation_error", "low"),
])
def test_severity_mapping_for_common_errors(rules_engine, error_code, expected_severity):
    """Test severity mapping for various common error codes."""
    # ACT
    severity = rules_engine.get_error_severity(error_code)

    # ASSERT
    assert severity == expected_severity


@pytest.mark.parametrize("error_code,expected_retryable", [
    ("payment_timeout", True),
    ("network_error", True),
    ("database_connection_error", True),
    ("invalid_input", False),
    ("authentication_failed", False),
])
def test_retryability_for_various_error_types(rules_engine, error_code, expected_retryable):
    """Test retryability determination for different error types."""
    # ACT
    is_retryable = rules_engine.is_retryable(error_code)

    # ASSERT
    assert is_retryable == expected_retryable


def test_error_code_lookup_is_case_insensitive(rules_engine):
    """Test that error code lookup handles different cases."""
    # ACT
    severity_lower = rules_engine.get_error_severity("payment_timeout")
    severity_upper = rules_engine.get_error_severity("PAYMENT_TIMEOUT")
    severity_mixed = rules_engine.get_error_severity("Payment_Timeout")

    # ASSERT
    assert severity_lower == severity_upper == severity_mixed
