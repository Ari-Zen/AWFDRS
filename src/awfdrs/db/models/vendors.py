"""
Vendor model for external service tracking.
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from src.awfdrs.db.base import BaseModel
from src.awfdrs.core.enums import CircuitBreakerState


class Vendor(BaseModel):
    """
    External vendor/service tracking model.

    Tracks circuit breaker state and failure metrics for external services.

    Attributes:
        name: Vendor name (e.g., "stripe", "plaid", "twilio")
        circuit_breaker_state: Current circuit breaker state
        failure_count: Number of consecutive failures
        last_failure_at: Timestamp of last failure
        last_success_at: Timestamp of last success
        config: Vendor-specific configuration (JSON)
    """

    __tablename__ = "vendors"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    circuit_breaker_state: Mapped[str] = mapped_column(
        String(50),
        default=CircuitBreakerState.CLOSED,
        nullable=False
    )
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_failure_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    last_success_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
