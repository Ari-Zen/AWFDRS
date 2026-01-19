"""
Circuit breaker manager for vendor protection.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.core.enums import CircuitBreakerState
from src.awfdrs.db.repositories.vendors import VendorRepository
from src.awfdrs.config import settings


class CircuitBreakerManager:
    """
    Manages circuit breaker state transitions for vendors.

    Implements the circuit breaker pattern:
    - CLOSED: Normal operation
    - OPEN: Too many failures, block requests
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        session: AsyncSession,
        config_dir: str = "config/rules"
    ) -> None:
        """
        Initialize circuit breaker manager.

        Args:
            session: Database session
            config_dir: Directory containing vendor configuration
        """
        self.session = session
        self.vendor_repo = VendorRepository(session)
        self.config_dir = Path(config_dir)
        self.vendor_configs: Dict[str, Any] = {}
        self._load_vendor_configs()

    def _load_vendor_configs(self) -> None:
        """Load vendor configurations from YAML."""
        vendor_config_file = self.config_dir / "vendor_config.yaml"
        if vendor_config_file.exists():
            with open(vendor_config_file, 'r') as f:
                data = yaml.safe_load(f)
                vendors = data.get('vendors', [])
                self.vendor_configs = {v['name']: v for v in vendors}

    async def record_failure(self, vendor_id: UUID) -> CircuitBreakerState:
        """
        Record a failure for a vendor and update circuit breaker state.

        Args:
            vendor_id: Vendor ID

        Returns:
            New circuit breaker state
        """
        vendor = await self.vendor_repo.get(vendor_id)
        if not vendor:
            return CircuitBreakerState.CLOSED

        # Get vendor configuration
        vendor_config = self.vendor_configs.get(vendor.name, {})
        failure_threshold = vendor_config.get(
            'circuit_breaker',
            {}
        ).get('failure_threshold', settings.safety.circuit_breaker_threshold)

        # Increment failure count
        vendor = await self.vendor_repo.increment_failure_count(vendor_id)
        if not vendor:
            return CircuitBreakerState.CLOSED

        # Check if should open circuit breaker
        if (
            vendor.circuit_breaker_state == CircuitBreakerState.CLOSED and
            vendor.failure_count >= failure_threshold
        ):
            # Open circuit breaker
            vendor = await self.vendor_repo.update_circuit_breaker_state(
                vendor_id,
                CircuitBreakerState.OPEN
            )
            return CircuitBreakerState.OPEN

        return vendor.circuit_breaker_state

    async def record_success(self, vendor_id: UUID) -> CircuitBreakerState:
        """
        Record a success for a vendor and update circuit breaker state.

        Args:
            vendor_id: Vendor ID

        Returns:
            New circuit breaker state
        """
        vendor = await self.vendor_repo.get(vendor_id)
        if not vendor:
            return CircuitBreakerState.CLOSED

        # If in HALF_OPEN, success means we can close the circuit
        if vendor.circuit_breaker_state == CircuitBreakerState.HALF_OPEN:
            await self.vendor_repo.reset_failure_count(vendor_id)
            vendor = await self.vendor_repo.update_circuit_breaker_state(
                vendor_id,
                CircuitBreakerState.CLOSED
            )
            return CircuitBreakerState.CLOSED

        # In CLOSED state, just reset failure count
        if vendor.circuit_breaker_state == CircuitBreakerState.CLOSED:
            await self.vendor_repo.reset_failure_count(vendor_id)

        return vendor.circuit_breaker_state

    async def check_state(self, vendor_id: UUID) -> CircuitBreakerState:
        """
        Check current circuit breaker state.

        If circuit is OPEN and timeout has elapsed, transition to HALF_OPEN.

        Args:
            vendor_id: Vendor ID

        Returns:
            Current circuit breaker state
        """
        vendor = await self.vendor_repo.get(vendor_id)
        if not vendor:
            return CircuitBreakerState.CLOSED

        # If OPEN, check if timeout has elapsed
        if vendor.circuit_breaker_state == CircuitBreakerState.OPEN:
            if vendor.last_failure_at:
                vendor_config = self.vendor_configs.get(vendor.name, {})
                timeout_seconds = vendor_config.get(
                    'circuit_breaker',
                    {}
                ).get('timeout_seconds', settings.safety.circuit_breaker_timeout_seconds)

                elapsed = (datetime.utcnow() - vendor.last_failure_at).total_seconds()
                if elapsed >= timeout_seconds:
                    # Transition to HALF_OPEN for testing
                    vendor = await self.vendor_repo.update_circuit_breaker_state(
                        vendor_id,
                        CircuitBreakerState.HALF_OPEN
                    )
                    return CircuitBreakerState.HALF_OPEN

        return vendor.circuit_breaker_state

    async def should_allow_request(self, vendor_id: UUID) -> bool:
        """
        Determine if a request should be allowed to a vendor.

        Args:
            vendor_id: Vendor ID

        Returns:
            True if request should be allowed, False otherwise
        """
        state = await self.check_state(vendor_id)

        # OPEN means block all requests
        if state == CircuitBreakerState.OPEN:
            return False

        # CLOSED and HALF_OPEN allow requests
        return True

    async def handle_half_open_result(
        self,
        vendor_id: UUID,
        success: bool
    ) -> CircuitBreakerState:
        """
        Handle the result of a request in HALF_OPEN state.

        Args:
            vendor_id: Vendor ID
            success: Whether the request succeeded

        Returns:
            New circuit breaker state
        """
        if success:
            return await self.record_success(vendor_id)
        else:
            # Failure in HALF_OPEN means go back to OPEN
            vendor = await self.vendor_repo.update_circuit_breaker_state(
                vendor_id,
                CircuitBreakerState.OPEN
            )
            await self.vendor_repo.increment_failure_count(vendor_id)
            return CircuitBreakerState.OPEN
