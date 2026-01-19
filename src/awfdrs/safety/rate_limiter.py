"""
Redis-based rate limiter with sliding window algorithm.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from uuid import UUID
import redis.asyncio as redis
from datetime import datetime

from src.awfdrs.safety.schemas import RateLimitResult
from src.awfdrs.config import settings


class RateLimiter:
    """
    Redis-backed rate limiter using sliding window algorithm.

    Enforces per-vendor and per-tenant rate limits.
    """

    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        config_dir: str = "config/rules"
    ) -> None:
        """
        Initialize rate limiter.

        Args:
            redis_client: Redis client instance
            config_dir: Directory containing vendor configuration
        """
        self.redis_client = redis_client
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

    async def _get_redis_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self.redis_client is None:
            self.redis_client = redis.from_url(
                settings.redis.url,
                encoding="utf-8",
                decode_responses=True
            )
        return self.redis_client

    def _get_rate_limit_key(self, vendor: str, tenant_id: UUID) -> str:
        """
        Generate Redis key for rate limiting.

        Args:
            vendor: Vendor name
            tenant_id: Tenant ID

        Returns:
            Redis key
        """
        return f"ratelimit:{vendor}:{tenant_id}"

    async def check_rate_limit(
        self,
        vendor: str,
        tenant_id: UUID
    ) -> RateLimitResult:
        """
        Check if request is within rate limit.

        Args:
            vendor: Vendor name
            tenant_id: Tenant ID

        Returns:
            Rate limit check result
        """
        # Get vendor configuration
        vendor_config = self.vendor_configs.get(vendor, {})
        rate_limit_config = vendor_config.get('rate_limit', {})

        # Default: 100 requests per minute
        limit = rate_limit_config.get('requests_per_minute', 100)
        window_seconds = 60

        # Get current count from Redis
        redis_client = await self._get_redis_client()
        key = self._get_rate_limit_key(vendor, tenant_id)

        try:
            current_count = await redis_client.get(key)
            current_count = int(current_count) if current_count else 0

            # Check if limit exceeded
            if current_count >= limit:
                # Calculate retry_after based on TTL
                ttl = await redis_client.ttl(key)
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    retry_after=ttl if ttl > 0 else window_seconds,
                    limit=limit
                )

            # Within limit
            remaining = limit - current_count - 1
            return RateLimitResult(
                allowed=True,
                remaining=max(0, remaining),
                retry_after=None,
                limit=limit
            )

        except Exception as e:
            # If Redis fails, allow request (fail open)
            return RateLimitResult(
                allowed=True,
                remaining=limit,
                retry_after=None,
                limit=limit
            )

    async def consume_token(self, vendor: str, tenant_id: UUID) -> bool:
        """
        Consume a rate limit token.

        Args:
            vendor: Vendor name
            tenant_id: Tenant ID

        Returns:
            True if token consumed, False if rate limit exceeded
        """
        result = await self.check_rate_limit(vendor, tenant_id)
        if not result.allowed:
            return False

        # Increment counter in Redis
        redis_client = await self._get_redis_client()
        key = self._get_rate_limit_key(vendor, tenant_id)
        window_seconds = 60

        try:
            # Use pipeline for atomicity
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            await pipe.execute()
            return True

        except Exception:
            # If Redis fails, allow request (fail open)
            return True

    async def get_retry_after(self, vendor: str, tenant_id: UUID) -> Optional[int]:
        """
        Get retry-after time in seconds.

        Args:
            vendor: Vendor name
            tenant_id: Tenant ID

        Returns:
            Seconds until rate limit resets, or None if within limit
        """
        result = await self.check_rate_limit(vendor, tenant_id)
        return result.retry_after

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
