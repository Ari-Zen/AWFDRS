"""
Mock external vendor responses for testing.
Simulates vendor errors, timeouts, and rate limits.
"""

from typing import Any, Dict, Optional
from enum import Enum
import time


class VendorErrorType(str, Enum):
    """Types of vendor errors to simulate."""

    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    SERVICE_UNAVAILABLE = "service_unavailable"
    INVALID_REQUEST = "invalid_request"
    AUTHENTICATION_FAILED = "authentication_failed"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    CARD_DECLINED = "card_declined"


class MockStripeClient:
    """Mock Stripe API client."""

    def __init__(self, api_key: str, error_mode: Optional[VendorErrorType] = None) -> None:
        """
        Initialize mock Stripe client.

        Args:
            api_key: API key (not used in mock)
            error_mode: If set, client will simulate this error
        """
        self.api_key = api_key
        self.error_mode = error_mode

    def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Mock payment intent creation.

        Returns:
            Mock payment intent response
        """
        if self.error_mode == VendorErrorType.TIMEOUT:
            time.sleep(10)  # Simulate timeout
            raise TimeoutError("Request timed out")

        if self.error_mode == VendorErrorType.RATE_LIMIT:
            raise Exception("Rate limit exceeded")

        if self.error_mode == VendorErrorType.SERVICE_UNAVAILABLE:
            raise Exception("Service unavailable")

        if self.error_mode == VendorErrorType.CARD_DECLINED:
            return {
                "id": "pi_mock_failed",
                "status": "failed",
                "error": {
                    "code": "card_declined",
                    "message": "Your card was declined"
                }
            }

        # Success response
        return {
            "id": "pi_mock_success_12345",
            "amount": amount,
            "currency": currency,
            "status": "succeeded",
            "client_secret": "pi_mock_secret_12345"
        }


class MockPlaidClient:
    """Mock Plaid API client."""

    def __init__(self, client_id: str, secret: str, error_mode: Optional[VendorErrorType] = None) -> None:
        """Initialize mock Plaid client."""
        self.client_id = client_id
        self.secret = secret
        self.error_mode = error_mode

    def get_balance(self, access_token: str) -> Dict[str, Any]:
        """
        Mock balance retrieval.

        Returns:
            Mock balance response
        """
        if self.error_mode == VendorErrorType.TIMEOUT:
            time.sleep(10)
            raise TimeoutError("Request timed out")

        if self.error_mode == VendorErrorType.AUTHENTICATION_FAILED:
            raise Exception("Invalid access token")

        if self.error_mode == VendorErrorType.INSUFFICIENT_FUNDS:
            return {
                "accounts": [
                    {
                        "account_id": "mock_account_123",
                        "balances": {
                            "available": 0.00,
                            "current": 0.00
                        }
                    }
                ]
            }

        # Success response
        return {
            "accounts": [
                {
                    "account_id": "mock_account_123",
                    "balances": {
                        "available": 1000.00,
                        "current": 1000.00
                    },
                    "name": "Mock Checking Account",
                    "type": "depository"
                }
            ]
        }


class MockTwilioClient:
    """Mock Twilio API client."""

    def __init__(self, account_sid: str, auth_token: str, error_mode: Optional[VendorErrorType] = None) -> None:
        """Initialize mock Twilio client."""
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.error_mode = error_mode

    def send_message(
        self,
        to: str,
        from_: str,
        body: str
    ) -> Dict[str, Any]:
        """
        Mock SMS sending.

        Returns:
            Mock message response
        """
        if self.error_mode == VendorErrorType.TIMEOUT:
            time.sleep(10)
            raise TimeoutError("Request timed out")

        if self.error_mode == VendorErrorType.RATE_LIMIT:
            raise Exception("Rate limit exceeded")

        if self.error_mode == VendorErrorType.INVALID_REQUEST:
            raise Exception("Invalid phone number")

        # Success response
        return {
            "sid": "SM_mock_message_12345",
            "to": to,
            "from": from_,
            "body": body,
            "status": "sent",
            "date_created": "2026-01-19T10:00:00Z"
        }


def get_mock_stripe_client(error_mode: Optional[VendorErrorType] = None) -> MockStripeClient:
    """Get a mock Stripe client."""
    return MockStripeClient("mock_stripe_key", error_mode)


def get_mock_plaid_client(error_mode: Optional[VendorErrorType] = None) -> MockPlaidClient:
    """Get a mock Plaid client."""
    return MockPlaidClient("mock_client_id", "mock_secret", error_mode)


def get_mock_twilio_client(error_mode: Optional[VendorErrorType] = None) -> MockTwilioClient:
    """Get a mock Twilio client."""
    return MockTwilioClient("mock_account_sid", "mock_auth_token", error_mode)
