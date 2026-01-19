"""
Safety limits enforcement for workflow and vendor operations.
"""

from typing import Optional
from uuid import UUID
import redis.asyncio as redis
from datetime import datetime, timedelta

from src.awfdrs.config import settings


class SafetyLimitsEnforcer:
    """
    Enforces safety thresholds to prevent cascading failures.

    Uses Redis counters with TTL for sliding window tracking.
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None) -> None:
        """
        Initialize safety limits enforcer.

        Args:
            redis_client: Redis client instance
        """
        self.redis_client = redis_client

    async def _get_redis_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self.redis_client is None:
            self.redis_client = redis.from_url(
                settings.redis.url,
                encoding="utf-8",
                decode_responses=True
            )
        return self.redis_client

    def _get_workflow_retry_key(self, workflow_id: UUID) -> str:
        """Generate Redis key for workflow retry tracking."""
        return f"safety:workflow_retries:{workflow_id}"

    def _get_vendor_retry_key(self, vendor_id: UUID) -> str:
        """Generate Redis key for vendor retry tracking."""
        return f"safety:vendor_retries:{vendor_id}"

    def _get_tenant_quota_key(self, tenant_id: UUID, resource: str) -> str:
        """Generate Redis key for tenant quota tracking."""
        return f"safety:tenant_quota:{tenant_id}:{resource}"

    async def check_workflow_retry_limit(self, workflow_id: UUID) -> bool:
        """
        Check if workflow is within retry limits.

        Args:
            workflow_id: Workflow ID

        Returns:
            True if within limit, False if exceeded
        """
        redis_client = await self._get_redis_client()
        key = self._get_workflow_retry_key(workflow_id)
        window_seconds = 3600  # 1 hour window

        try:
            current_count = await redis_client.get(key)
            current_count = int(current_count) if current_count else 0
            return current_count < settings.safety.max_retries_per_workflow

        except Exception:
            # If Redis fails, allow (fail open)
            return True

    async def increment_workflow_retry_count(self, workflow_id: UUID) -> int:
        """
        Increment workflow retry counter.

        Args:
            workflow_id: Workflow ID

        Returns:
            New retry count
        """
        redis_client = await self._get_redis_client()
        key = self._get_workflow_retry_key(workflow_id)
        window_seconds = 3600  # 1 hour window

        try:
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            results = await pipe.execute()
            return results[0]

        except Exception:
            return 0

    async def check_vendor_retry_limit(self, vendor_id: UUID) -> bool:
        """
        Check if vendor is within retry limits.

        Args:
            vendor_id: Vendor ID

        Returns:
            True if within limit, False if exceeded
        """
        redis_client = await self._get_redis_client()
        key = self._get_vendor_retry_key(vendor_id)
        window_seconds = 3600  # 1 hour window

        try:
            current_count = await redis_client.get(key)
            current_count = int(current_count) if current_count else 0
            return current_count < settings.safety.max_retries_per_vendor

        except Exception:
            # If Redis fails, allow (fail open)
            return True

    async def increment_vendor_retry_count(self, vendor_id: UUID) -> int:
        """
        Increment vendor retry counter.

        Args:
            vendor_id: Vendor ID

        Returns:
            New retry count
        """
        redis_client = await self._get_redis_client()
        key = self._get_vendor_retry_key(vendor_id)
        window_seconds = 3600  # 1 hour window

        try:
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            results = await pipe.execute()
            return results[0]

        except Exception:
            return 0

    async def check_tenant_quota(self, tenant_id: UUID, resource: str) -> bool:
        """
        Check if tenant is within resource quota.

        Args:
            tenant_id: Tenant ID
            resource: Resource type (e.g., 'events', 'incidents')

        Returns:
            True if within quota, False if exceeded
        """
        redis_client = await self._get_redis_client()
        key = self._get_tenant_quota_key(tenant_id, resource)
        window_seconds = 86400  # 24 hour window

        # Default quotas
        quotas = {
            'events': 10000,
            'incidents': 1000,
            'actions': 5000
        }
        limit = quotas.get(resource, 10000)

        try:
            current_count = await redis_client.get(key)
            current_count = int(current_count) if current_count else 0
            return current_count < limit

        except Exception:
            # If Redis fails, allow (fail open)
            return True

    async def increment_tenant_quota(
        self,
        tenant_id: UUID,
        resource: str
    ) -> int:
        """
        Increment tenant resource quota counter.

        Args:
            tenant_id: Tenant ID
            resource: Resource type

        Returns:
            New count
        """
        redis_client = await self._get_redis_client()
        key = self._get_tenant_quota_key(tenant_id, resource)
        window_seconds = 86400  # 24 hour window

        try:
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            results = await pipe.execute()
            return results[0]

        except Exception:
            return 0

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
