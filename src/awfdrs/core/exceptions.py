"""
Custom exception hierarchy for AWFDRS.
"""

from typing import Any, Dict, Optional


class AWFDRSException(Exception):
    """Base exception for all AWFDRS errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ) -> None:
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AWFDRSException):
    """Raised when validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details, status_code=422)


class NotFoundError(AWFDRSException):
    """Raised when a resource is not found."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details, status_code=404)


class ConflictError(AWFDRSException):
    """Raised when there's a conflict (e.g., duplicate key)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details, status_code=409)


class UnauthorizedError(AWFDRSException):
    """Raised when authentication fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details, status_code=401)


class ForbiddenError(AWFDRSException):
    """Raised when authorization fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details, status_code=403)


class DatabaseError(AWFDRSException):
    """Raised when database operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details, status_code=500)


class ExternalServiceError(AWFDRSException):
    """Raised when external service calls fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details, status_code=502)


class RateLimitError(AWFDRSException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details, status_code=429)


class CircuitBreakerOpenError(AWFDRSException):
    """Raised when circuit breaker is open."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details, status_code=503)


class KillSwitchActiveError(AWFDRSException):
    """Raised when a kill switch is active."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details, status_code=403)


class SafetyLimitExceededError(AWFDRSException):
    """Raised when safety limits are exceeded."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details, status_code=429)


class AIServiceError(AWFDRSException):
    """Raised when AI service operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details, status_code=500)
