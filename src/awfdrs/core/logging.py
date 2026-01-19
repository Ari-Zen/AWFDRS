"""
Structured logging configuration using standard library logging.
Provides correlation ID tracking and structured output.
"""

import logging
import sys
from typing import Any, Dict
from datetime import datetime
import json


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add correlation ID if present
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id

        # Add tenant ID if present
        if hasattr(record, "tenant_id"):
            log_data["tenant_id"] = record.tenant_id

        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class CorrelationIDFilter(logging.Filter):
    """Filter that adds correlation ID to log records."""

    def __init__(self, correlation_id: str = "") -> None:
        super().__init__()
        self.correlation_id = correlation_id

    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID to record."""
        if not hasattr(record, "correlation_id"):
            record.correlation_id = self.correlation_id
        return True


def setup_logging(log_level: str = "INFO", use_json: bool = True) -> None:
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Set formatter
    if use_json:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def add_correlation_id(logger: logging.Logger, correlation_id: str) -> logging.Logger:
    """
    Add correlation ID filter to logger.

    Args:
        logger: Logger instance
        correlation_id: Correlation ID to add

    Returns:
        Logger with correlation ID filter
    """
    logger.addFilter(CorrelationIDFilter(correlation_id))
    return logger
