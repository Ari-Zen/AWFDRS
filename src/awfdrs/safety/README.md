# Safety Layer Module

## Overview

The `safety/` module implements protective controls to prevent cascading failures, enforce operational limits, and protect vendor relationships.

## Purpose

- **Circuit breakers** - Protect vendor services from overload
- **Rate limiting** - Prevent abuse and DoS attacks
- **Rules engine** - Evaluate error severity and retry policies
- **Safety limits** - Enforce maximum retry attempts

---

## Components

### `circuit_breaker.py` - Circuit Breaker
**Purpose:** Prevent hammering failing services.

**Pattern:** Circuit Breaker (Michael Nygard, "Release It!")

**States:**
```
CLOSED (normal)
  ↓ (failure threshold exceeded)
OPEN (blocking requests)
  ↓ (timeout expires)
HALF_OPEN (testing recovery)
  ↓ (success) → CLOSED
  ↓ (failure) → OPEN
```

**Class: CircuitBreakerManager**

```python
async def check_circuit(self, vendor: str) -> CircuitBreakerState:
    """
    Check if circuit is open for vendor.

    Raises:
        CircuitBreakerError: If circuit is OPEN
    """

async def record_success(self, vendor: str):
    """
    Record successful request.

    - If HALF_OPEN: Transition to CLOSED
    - If CLOSED: No-op
    """

async def record_failure(self, vendor: str):
    """
    Record failed request.

    - Increment failure count
    - If threshold exceeded: Transition to OPEN
    - If HALF_OPEN: Transition back to OPEN
    """
```

**Configuration (per vendor):**
```yaml
# config/rules/vendor_config.yaml
vendors:
  - name: stripe
    circuit_breaker:
      failure_threshold: 10  # Open after 10 failures
      timeout_seconds: 300   # Stay open for 5 minutes
      half_open_max_calls: 3 # Test with 3 requests
```

**Storage:** Redis (distributed state across instances)

**Redis Keys:**
```
circuit:stripe:state -> "CLOSED" | "OPEN" | "HALF_OPEN"
circuit:stripe:failure_count -> 7
circuit:stripe:opened_at -> 1642598400
```

---

### `rate_limiter.py` - Rate Limiting
**Purpose:** Throttle requests to prevent abuse.

**Algorithm:** Sliding Window (Redis-backed)

**Class: RateLimiter**

```python
async def check_rate_limit(
    self,
    key: str,
    limit: int,
    window_seconds: int = 60
) -> bool:
    """
    Check if request is within rate limit.

    Args:
        key: Rate limit key (e.g., "tenant:abc" or "vendor:stripe")
        limit: Maximum requests per window
        window_seconds: Time window in seconds

    Returns:
        True if within limit, False if exceeded

    Raises:
        RateLimitError: If limit exceeded
    """
```

**Implementation:**
```python
# Sliding window using Redis sorted set
redis.zadd(key, {timestamp: timestamp})  # Add current timestamp
redis.zremrangebyscore(key, 0, timestamp - window_seconds)  # Remove old
count = redis.zcard(key)  # Count requests in window

if count > limit:
    raise RateLimitError(f"Rate limit exceeded: {count}/{limit}")
```

**Rate Limit Scopes:**
- **Per tenant:** 1000 requests/minute
- **Per workflow:** 500 requests/minute
- **Per vendor:** 100 requests/minute

**Configuration:**
```yaml
# config/rules/vendor_config.yaml
vendors:
  - name: stripe
    rate_limit:
      requests_per_minute: 100
      burst_allowance: 120  # Allow brief spikes
```

---

### `rules_engine.py` - Error Rules Engine
**Purpose:** Evaluate errors against configured rules.

**Class: RulesEngine**

```python
def get_error_severity(self, error_code: str) -> str:
    """
    Get severity level for error code.

    Returns: "low", "medium", "high", "critical"
    """

def get_retry_policy(self, error_code: str) -> dict:
    """
    Get retry policy for error code.

    Returns:
    {
      "retryable": true,
      "max_retries": 5,
      "strategy": "exponential_backoff"
    }
    """

def is_retryable(self, error_code: str) -> bool:
    """Check if error is retryable."""
```

**Configuration:**
```yaml
# config/rules/error_codes.yaml
error_codes:
  payment_timeout:
    severity: high
    retry_policy: exponential_backoff
    description: "Payment gateway timeout"

  invalid_card:
    severity: low
    retry_policy: no_retry
    description: "Invalid credit card"
```

```yaml
# config/rules/retry_policies.yaml
retry_policies:
  exponential_backoff:
    retryable: true
    max_retries: 5
    initial_delay_seconds: 1
    max_delay_seconds: 300
    backoff_multiplier: 2.0

  no_retry:
    retryable: false
    max_retries: 0
```

---

### `limits.py` - Safety Limits Enforcer
**Purpose:** Enforce maximum retry and failure limits.

**Class: SafetyLimitsEnforcer**

```python
async def check_workflow_retry_limit(
    self,
    workflow_id: UUID,
    tenant_id: UUID
) -> bool:
    """
    Check if workflow has exceeded retry limit.

    Limit: 5 retries per workflow (default)

    Raises:
        SafetyLimitExceeded: If limit exceeded
    """

async def check_vendor_failure_limit(
    self,
    vendor: str,
    window_hours: int = 1
) -> bool:
    """
    Check if vendor failures exceeded limit in time window.

    Limit: 100 failures per hour (default)

    Raises:
        SafetyLimitExceeded: If limit exceeded
    """
```

**Configuration:**
```env
MAX_RETRIES_PER_WORKFLOW=5
MAX_RETRIES_PER_VENDOR=100
```

---

## Circuit Breaker State Diagram

```
┌─────────┐
│ CLOSED  │  Normal operation
└────┬────┘
     │
     │ failure_count > threshold
     ▼
┌─────────┐
│  OPEN   │  Blocking all requests
└────┬────┘
     │
     │ timeout expires
     ▼
┌──────────┐
│HALF_OPEN │  Testing with limited requests
└────┬─────┘
     │
     ├─ Success → CLOSED
     └─ Failure → OPEN
```

---

## Rate Limiting Example

**Scenario:** Tenant submits 150 events in 1 minute

```
Request 1-100: ACCEPTED (within limit)
Request 101: REJECTED (429 Too Many Requests)
  Response Headers:
    X-RateLimit-Limit: 100
    X-RateLimit-Remaining: 0
    X-RateLimit-Reset: 1642598460
    Retry-After: 60

Wait 60 seconds...

Request 102: ACCEPTED (window reset)
```

---

## Error Severity Levels

| Severity | Description | Auto-Retry? | Escalation |
|----------|-------------|-------------|------------|
| **CRITICAL** | System-wide outage | No | Immediate page |
| **HIGH** | Major functionality broken | Yes (limited) | Team notification |
| **MEDIUM** | Non-critical degradation | Yes | Slack alert |
| **LOW** | Minor issue | Yes | Log only |

---

## Testing

```python
@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_threshold():
    breaker = CircuitBreakerManager(redis_client)
    vendor = "test-vendor"

    # Record failures until threshold
    for _ in range(10):
        await breaker.record_failure(vendor)

    # Circuit should be open
    state = await breaker.get_state(vendor)
    assert state == CircuitBreakerState.OPEN

    # Should reject requests
    with pytest.raises(CircuitBreakerError):
        await breaker.check_circuit(vendor)

@pytest.mark.asyncio
async def test_rate_limiter_blocks_after_limit():
    limiter = RateLimiter(redis_client)
    key = "test:tenant-123"

    # Submit requests up to limit
    for i in range(100):
        allowed = await limiter.check_rate_limit(key, limit=100)
        assert allowed is True

    # Next request should be blocked
    with pytest.raises(RateLimitError):
        await limiter.check_rate_limit(key, limit=100)
```

---

## Redis Data Structures

### Circuit Breaker
```redis
# State
SET circuit:stripe:state "OPEN"

# Failure count
SET circuit:stripe:failure_count 12

# Opened timestamp
SET circuit:stripe:opened_at 1642598400

# TTL for auto-reset
EXPIRE circuit:stripe:state 300
```

### Rate Limiting
```redis
# Sliding window (sorted set)
ZADD ratelimit:tenant:abc 1642598400 "req-1"
ZADD ratelimit:tenant:abc 1642598401 "req-2"
ZADD ratelimit:tenant:abc 1642598402 "req-3"

# Cleanup old entries
ZREMRANGEBYSCORE ratelimit:tenant:abc 0 1642598340

# Count requests
ZCARD ratelimit:tenant:abc  # Returns: 3

# TTL for cleanup
EXPIRE ratelimit:tenant:abc 60
```

---

## Performance

### Redis Connection Pooling
```python
# Single Redis connection pool for entire application
redis_pool = redis.asyncio.ConnectionPool.from_url(
    settings.redis.url,
    max_connections=50
)

redis_client = redis.asyncio.Redis(connection_pool=redis_pool)
```

### Caching
- Error code rules cached in memory (loaded at startup)
- Retry policies cached in memory
- Vendor config cached (5 minutes)

### Optimization
- Batch Redis operations where possible
- Use Redis pipelines for multiple commands
- Set appropriate TTLs to prevent memory leaks

---

## Monitoring

### Metrics
- `circuit_breaker_state{vendor, state}` - Current state per vendor
- `circuit_breaker_transitions_total{vendor, from_state, to_state}` - State changes
- `rate_limiter_rejections_total{key, limit_type}` - Rate limit rejections
- `safety_limits_exceeded_total{limit_type}` - Safety limit violations

### Alerts
- Alert when circuit breaker opens (vendor down)
- Alert if circuit breaker stays open > 15 minutes
- Alert if rate limit rejections > 1000/hour (potential attack)
- Alert if safety limits frequently exceeded

### Logging
```json
{
  "level": "WARNING",
  "message": "Circuit breaker opened",
  "vendor": "stripe",
  "failure_count": 12,
  "threshold": 10,
  "timeout_seconds": 300
}
```

---

## Configuration Management

### YAML Hot Reloading
**Future Enhancement:** Reload YAML configs without restart.

```python
# Watch for config file changes
def watch_config_files():
    for config_file in ["error_codes.yaml", "retry_policies.yaml"]:
        if file_modified(config_file):
            reload_config(config_file)
```

### Operational Updates
**Operators can update configs without code changes:**

```bash
# Update retry policy
vim config/rules/retry_policies.yaml

# Restart application (or hot reload)
kubectl rollout restart deployment/awfdrs
```

---

## Troubleshooting

### Circuit Breaker Stuck Open
**Symptom:** Circuit stays open even after vendor recovered.

**Solution:**
```bash
# Check circuit state
redis-cli GET circuit:stripe:state

# Manually reset (emergency only)
redis-cli DEL circuit:stripe:state
redis-cli DEL circuit:stripe:failure_count
```

### Rate Limit False Positives
**Symptom:** Legitimate requests getting rate limited.

**Solution:**
- Increase limit in vendor config
- Check for clock skew (Redis timestamps)
- Verify sliding window cleanup working

---

## See Also

- [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) - Safety layer design
- [config/rules/](../../../config/rules/) - Configuration files
- [Release It! by Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/) - Circuit breaker pattern
