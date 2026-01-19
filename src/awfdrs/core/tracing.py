"""
Request tracing and correlation ID middleware.
"""

import uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from contextvars import ContextVar


# Context variable to store correlation ID
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """Get the current correlation ID."""
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID."""
    correlation_id_var.set(correlation_id)


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that generates and propagates correlation IDs.

    The correlation ID is:
    1. Extracted from X-Correlation-ID header if present
    2. Generated as a new UUID if not present
    3. Added to the response headers
    4. Made available throughout the request lifecycle
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request and add correlation ID."""
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Set in context
        set_correlation_id(correlation_id)

        # Add to request state for access in route handlers
        request.state.correlation_id = correlation_id

        # Process request
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs incoming requests."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Log request details."""
        import logging

        logger = logging.getLogger(__name__)

        # Get correlation ID
        correlation_id = getattr(request.state, "correlation_id", "unknown")

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            }
        )

        # Process request
        response = await call_next(request)

        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            }
        )

        return response
