# Core Utilities Module

## Overview

The `core/` module contains shared utilities, cross-cutting concerns, and foundational components used throughout the AWFDRS application.

## Purpose

- **Centralized utilities** - Logging, exceptions, tracing, enums
- **No business logic** - Pure infrastructure and shared types
- **No external dependencies** - Can be imported anywhere without circular dependencies
- **Type-safe** - Comprehensive type hints for all components

## Components

### `config.py` (Parent Directory)
**Purpose:** Centralized application configuration using Pydantic settings.

**Key Features:**
- Type-safe environment variable parsing
- Nested configuration groups (database, Redis, AI, auth, safety)
- Validation on startup with clear error messages
- No raw `os.getenv()` usage

**Usage:**
```python
from src.awfdrs.config import settings

# Access configuration
db_url = settings.database.url
redis_url = settings.redis.url
log_level = settings.log_level
```

---

### `logging.py`
**Purpose:** Structured logging with correlation ID support.

**Key Features:**
- JSON-formatted logs for machine parsing
- Correlation ID injection via middleware
- Tenant ID tracking in logs
- Standard log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

**Usage:**
```python
from src.awfdrs.core.logging import get_logger, setup_logging

# Setup (done in main.py)
setup_logging(log_level="INFO", use_json=True)

# Get logger
logger = get_logger(__name__)

# Log with context
logger.info(
    "Event ingested",
    extra={"event_id": str(event.id), "tenant_id": str(tenant.id)}
)
```

---

### `exceptions.py`
**Purpose:** Custom exception hierarchy for AWFDRS.

**Exception Types:**
- `AWFDRSException` (base) - HTTP 500
- `ValidationError` - HTTP 400 (invalid input)
- `NotFoundError` - HTTP 404 (resource not found)
- `DuplicateError` - HTTP 409 (idempotency conflict)
- `RateLimitError` - HTTP 429 (rate limit exceeded)
- `CircuitBreakerError` - HTTP 503 (service unavailable)
- `InternalError` - HTTP 500 (internal server error)

**Usage:**
```python
from src.awfdrs.core.exceptions import NotFoundError, ValidationError

# Raise with context
if not tenant:
    raise NotFoundError(f"Tenant {tenant_id} not found")

if not event.event_type:
    raise ValidationError("Event type is required")
```

---

### `tracing.py`
**Purpose:** Request correlation and distributed tracing middleware.

**Components:**
- `CorrelationIDMiddleware` - Generates/extracts correlation IDs
- `RequestLoggingMiddleware` - Logs all HTTP requests

**Key Features:**
- Correlation IDs on every request
- Automatic propagation via `X-Correlation-ID` header
- Request/response logging with timing

**Usage:**
```python
# Added in main.py
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Access in handlers
from src.awfdrs.dependencies import get_correlation_id

@router.post("/events")
async def submit_event(correlation_id: str = Depends(get_correlation_id)):
    logger.info(f"Processing event", extra={"correlation_id": correlation_id})
```

---

### `enums.py`
**Purpose:** Shared enumerations used across modules.

**Enums:**
- `EventType` - Event type categories
- `IncidentStatus` - Incident lifecycle states (NEW, ANALYZING, ACTIONED, RESOLVED, IGNORED)
- `ActionStatus` - Action execution states (PENDING, IN_PROGRESS, SUCCEEDED, FAILED)
- `CircuitBreakerState` - Circuit breaker states (CLOSED, OPEN, HALF_OPEN)
- `Severity` - Severity levels (LOW, MEDIUM, HIGH, CRITICAL)

**Usage:**
```python
from src.awfdrs.core.enums import IncidentStatus, Severity

incident.status = IncidentStatus.ANALYZING
incident.severity = Severity.HIGH
```

---

### `schemas.py`
**Purpose:** Shared Pydantic schemas and base models.

**Components:**
- Base response schemas
- Common validation patterns
- Shared field definitions

**Usage:**
```python
from src.awfdrs.core.schemas import PaginatedResponse

response = PaginatedResponse(
    items=incidents,
    total=100,
    page=1,
    page_size=20
)
```

---

## Design Principles

### 1. No Circular Dependencies
The `core/` module must not import from domain modules (ingestion, analysis, actions, etc.). It only imports from standard library and third-party packages.

### 2. Stateless Utilities
All utilities should be stateless or use dependency injection. No global mutable state.

### 3. Comprehensive Type Hints
Every function and class must have complete type annotations.

### 4. Minimal Business Logic
No domain-specific business logic. Only infrastructure concerns.

---

## Testing

### Unit Tests Location
`tests/unit/core/`

### What to Test
- Exception hierarchy and status code mapping
- Logging formatter output
- Enum value validation
- Correlation ID generation

### Example Test
```python
def test_not_found_error_has_correct_status_code():
    error = NotFoundError("Resource not found")
    assert error.status_code == 404
    assert "not found" in error.message.lower()
```

---

## Extension Guidelines

### Adding a New Exception
1. Inherit from `AWFDRSException`
2. Set appropriate `status_code`
3. Update exception hierarchy documentation
4. Add tests

```python
class ConflictError(AWFDRSException):
    """Raised when resource state conflict occurs."""
    status_code = 409

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, details)
```

### Adding a New Enum
1. Define enum in `enums.py`
2. Use string values for JSON serialization
3. Document all values
4. Add validation tests

```python
class RetryStrategy(str, Enum):
    """Retry strategy types."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"
```

---

## Dependencies

**External:**
- `pydantic` - Data validation and settings
- `pydantic-settings` - Environment variable parsing

**Internal:**
- None (core has no internal dependencies)

---

## Common Issues

### Issue: Circular Import
**Symptom:** `ImportError: cannot import name '...'`
**Solution:** Core modules should never import from domain modules. Move shared types to `core/schemas.py`.

### Issue: Missing Correlation ID
**Symptom:** Logs missing `correlation_id` field
**Solution:** Ensure `CorrelationIDMiddleware` is registered in `main.py` before routes.

### Issue: Configuration Not Loaded
**Symptom:** `ValidationError` on startup
**Solution:** Check `.env` file exists and contains required variables. Review `config.py` validators.

---

## See Also

- [CONVENTIONS.md](../../../docs/CONVENTIONS.md) - Coding standards
- [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) - System design
- [TESTING.md](../../../docs/TESTING.md) - Testing strategy
