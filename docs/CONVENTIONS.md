# AWFDRS Coding Conventions

## Overview

This document establishes coding standards, style guidelines, and best practices for AWFDRS development. Consistency in code style improves readability, maintainability, and collaboration.

---

## General Principles

1. **Readability over cleverness** - Code is read more often than written
2. **Explicit is better than implicit** - Clear intent over magic
3. **Type safety** - Use type hints everywhere
4. **DRY (Don't Repeat Yourself)** - Abstract common patterns
5. **YAGNI (You Aren't Gonna Need It)** - Don't build features speculatively
6. **Fail fast** - Validate early and raise clear errors
7. **Security first** - Never trust user input

---

## Python Style Guide

### Base Standards

**Follow PEP 8** with the following project-specific additions:
- Line length: 100 characters (not 79)
- Use Black for automatic formatting
- Use Ruff for linting
- Use mypy for type checking

### Code Formatting

**Use Black:**
```bash
black src/ tests/
```

**Configuration** (in pyproject.toml):
```toml
[tool.black]
line-length = 100
target-version = ['py311']
```

---

## Naming Conventions

### Modules and Packages

**snake_case, descriptive names**

```python
# Good
ingestion_service.py
circuit_breaker.py
event_repository.py

# Bad
svc.py
cb.py
repo.py
```

### Classes

**PascalCase, noun phrases**

```python
# Good
class EventRepository:
class CircuitBreaker:
class IngestionService:

# Bad
class event_repository:  # Wrong case
class DoIngestion:       # Verb phrase
class Repo:              # Abbreviation
```

### Functions and Methods

**snake_case, verb phrases**

```python
# Good
def create_event():
def validate_tenant():
def get_incident_by_id():

# Bad
def CreateEvent():       # Wrong case
def event():             # Not a verb
def getIncById():        # Abbreviations
```

### Variables

**snake_case, descriptive names**

```python
# Good
event_id = "evt-123"
retry_count = 3
is_active = True
has_errors = False

# Bad
eventId = "evt-123"      # camelCase (not Python convention)
rc = 3                   # Abbreviation
active = True            # Ambiguous (is_active is clearer)
```

### Constants

**UPPER_SNAKE_CASE**

```python
# Good
MAX_RETRIES = 5
DEFAULT_TIMEOUT_SECONDS = 30
API_VERSION = "v1"

# Bad
max_retries = 5          # Not uppercase
MaxRetries = 5           # Wrong case
```

### Private Members

**Prefix with single underscore**

```python
class EventProcessor:
    def __init__(self):
        self._internal_state = {}  # Private attribute

    def _helper_method(self):      # Private method
        pass

    def public_method(self):       # Public method
        return self._helper_method()
```

**Double underscore for name mangling (rare):**
```python
class BaseClass:
    def __internal(self):  # Name mangled to _BaseClass__internal
        pass
```

---

## Type Hints

### Required Everywhere

**All functions must have type hints:**

```python
# Good
def create_event(event_data: dict) -> Event:
    pass

async def get_event_by_id(event_id: UUID) -> Optional[Event]:
    pass

# Bad
def create_event(event_data):  # No type hints
    pass
```

### Type Hint Syntax

```python
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime

# Simple types
def calculate_total(amount: int) -> int:
    return amount * 2

# Optional (can be None)
def find_event(event_id: UUID) -> Optional[Event]:
    return event or None

# Lists and Dicts
def process_events(events: List[Event]) -> Dict[str, Any]:
    return {"count": len(events)}

# Union types
def parse_id(id_value: Union[str, UUID]) -> UUID:
    if isinstance(id_value, str):
        return UUID(id_value)
    return id_value

# Async functions
async def fetch_data() -> dict:
    return {}
```

### SQLAlchemy 2.0 Type Hints

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from uuid import UUID

class Event(BaseModel):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
```

### Pydantic Models

```python
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class WorkflowEventV1(BaseModel):
    tenant_id: UUID
    workflow_id: UUID
    event_type: str = Field(..., min_length=1, max_length=255)
    payload: dict
    idempotency_key: str
    occurred_at: datetime
    schema_version: str = "1.0.0"
```

---

## Docstrings

### All Public Functions and Classes

**Use Google-style docstrings:**

```python
def create_incident(
    event: Event,
    signature: str,
    severity: str
) -> Incident:
    """
    Create a new incident from an event.

    Args:
        event: The event that triggered the incident
        signature: Unique signature for grouping similar incidents
        severity: Incident severity (low, medium, high, critical)

    Returns:
        Incident: The created incident object

    Raises:
        ValidationError: If severity is not valid
        DatabaseError: If database operation fails

    Example:
        >>> incident = create_incident(event, "payment.timeout:wf-123", "high")
        >>> print(incident.id)
    """
    pass
```

### Class Docstrings

```python
class CircuitBreaker:
    """
    Circuit breaker for protecting external service calls.

    Implements the circuit breaker pattern with three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing if service recovered

    Attributes:
        vendor: Vendor name
        threshold: Failure count to trigger opening
        timeout: Seconds before transitioning to HALF_OPEN
        state: Current circuit breaker state

    Example:
        >>> breaker = CircuitBreaker(vendor="stripe", threshold=5)
        >>> if breaker.is_open():
        >>>     raise ServiceUnavailableError("Circuit breaker open")
    """
    pass
```

### Module Docstrings

**Every module must have a docstring:**

```python
"""
Event ingestion service module.

Handles validation, deduplication, and persistence of workflow events.
Enforces tenant isolation and idempotency guarantees.
"""

# Rest of module code...
```

---

## Error Handling

### Custom Exceptions

**Use custom exceptions from `core/exceptions.py`:**

```python
from src.awfdrs.core.exceptions import (
    AWFDRSException,
    ValidationError,
    NotFoundError,
    DuplicateError
)

# Raise with clear messages
raise NotFoundError(f"Tenant {tenant_id} not found")
raise ValidationError("Event type must not be empty")
raise DuplicateError(f"Event with idempotency key {key} already exists")
```

### Exception Hierarchy

```python
AWFDRSException (base)
├── ValidationError (400)
├── NotFoundError (404)
├── DuplicateError (409)
├── RateLimitError (429)
├── CircuitBreakerError (503)
└── InternalError (500)
```

### Catching Exceptions

```python
# Good - Catch specific exceptions
try:
    event = await repository.get_by_id(event_id)
except NotFoundError:
    logger.warning(f"Event {event_id} not found")
    return None
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise

# Bad - Catching broad exceptions
try:
    event = await repository.get_by_id(event_id)
except Exception:  # Too broad!
    pass
```

### Re-raising with Context

```python
try:
    result = await external_service.call()
except ExternalServiceError as e:
    # Add context before re-raising
    raise InternalError(f"Failed to call external service: {e}") from e
```

---

## Async/Await Best Practices

### Use Async for I/O Operations

```python
# Good - Async for database and external calls
async def get_event(event_id: UUID) -> Event:
    async with get_session() as session:
        return await session.get(Event, event_id)

# Bad - Sync for I/O (blocks event loop)
def get_event(event_id: UUID) -> Event:
    session = get_session()
    return session.query(Event).get(event_id)
```

### Await All Async Calls

```python
# Good
result = await async_function()

# Bad - Missing await (returns coroutine, not result)
result = async_function()
```

### Concurrent Execution

```python
import asyncio

# Execute multiple async operations concurrently
results = await asyncio.gather(
    fetch_tenant(tenant_id),
    fetch_workflow(workflow_id),
    fetch_vendor(vendor_id)
)
tenant, workflow, vendor = results
```

---

## Database Best Practices

### Use Repositories, Not Raw Queries

```python
# Good - Use repository
from src.awfdrs.db.repositories.events import EventRepository

repo = EventRepository(session)
event = await repo.create(event_data)

# Bad - Raw SQLAlchemy queries in service
event = Event(**event_data)
session.add(event)
await session.commit()
```

### Transaction Management

```python
# Service controls transactions, not repositories
async def ingest_event(event_data: dict) -> Event:
    async with get_session() as session:
        repo = EventRepository(session)

        # Multiple operations in one transaction
        event = await repo.create(event_data)
        await incident_detector.detect(event)

        await session.commit()  # Commit once at the end
        return event
```

### Avoid N+1 Queries

```python
# Bad - N+1 queries
incidents = await incident_repo.get_all()
for incident in incidents:
    events = await event_repo.get_by_incident(incident.id)  # N queries!

# Good - Single query with join or eager loading
incidents = await incident_repo.get_all_with_events()  # 1 query
```

---

## Security Best Practices

### Input Validation

**Always validate user input:**

```python
from pydantic import BaseModel, Field, validator

class WorkflowEventV1(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=255)
    payload: dict

    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.replace('.', '').replace('_', '').isalnum():
            raise ValueError("Event type must contain only alphanumeric, dots, and underscores")
        return v
```

### SQL Injection Prevention

**Use SQLAlchemy ORM, never string concatenation:**

```python
# Good - Parameterized queries
result = await session.execute(
    select(Event).where(Event.tenant_id == tenant_id)
)

# Bad - String concatenation (SQL injection risk!)
query = f"SELECT * FROM events WHERE tenant_id = '{tenant_id}'"
```

### Secrets Management

**Never hardcode secrets:**

```python
# Good - Load from environment
from src.awfdrs.config import settings
api_key = settings.ai.openai_api_key

# Bad - Hardcoded
api_key = "sk-abc123..."  # NEVER DO THIS
```

### Log Sanitization

**Never log secrets or sensitive data:**

```python
# Good - Sanitized logging
logger.info(f"API call to vendor {vendor_name}")

# Bad - Leaking secrets
logger.info(f"API call with key {api_key}")  # DANGER!
```

---

## Testing Conventions

### Test Naming

```python
# Pattern: test_<function_name>_<scenario>

def test_create_event_with_valid_payload():
    pass

def test_create_event_rejects_missing_tenant_id():
    pass

def test_circuit_breaker_opens_after_threshold_exceeded():
    pass
```

### Test Structure (Arrange-Act-Assert)

```python
def test_signature_generator_normalizes_error_code():
    # ARRANGE - Set up test data
    generator = SignatureGenerator()
    event_data = {"event_type": "payment.failed", "error_code": "TIMEOUT"}

    # ACT - Perform the action
    signature = generator.generate(event_data)

    # ASSERT - Verify outcome
    assert "timeout" in signature.lower()  # Normalized to lowercase
```

### Use Fixtures for Setup

```python
@pytest.fixture
def valid_event_data():
    """Provide valid event data for tests."""
    return {
        "tenant_id": UUID("00000000-0000-0000-0000-000000000001"),
        "workflow_id": UUID("10000000-0000-0000-0000-000000000001"),
        "event_type": "test.event",
        "payload": {},
        "idempotency_key": f"test-{uuid4()}",
        "occurred_at": datetime.utcnow().isoformat(),
    }

def test_ingest_event(valid_event_data):
    # Use fixture
    event = create_event(valid_event_data)
    assert event.event_type == "test.event"
```

---

## Code Organization

### Import Order

**Follow this order:**

1. Standard library imports
2. Third-party imports
3. Local application imports

**Separate groups with blank line:**

```python
# Standard library
import logging
from datetime import datetime
from typing import Optional, List
from uuid import UUID

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy import select
from pydantic import BaseModel

# Local application
from src.awfdrs.config import settings
from src.awfdrs.core.exceptions import NotFoundError
from src.awfdrs.db.repositories.events import EventRepository
```

### File Structure

```python
"""
Module docstring explaining purpose.
"""

# Imports (ordered as above)
import logging
from typing import Optional

# Constants
MAX_RETRIES = 5
DEFAULT_TIMEOUT = 30

# Type definitions
EventDict = dict[str, Any]

# Classes
class MyClass:
    pass

# Functions
def my_function():
    pass

# Module initialization (if needed)
logger = logging.getLogger(__name__)
```

---

## Configuration

### Use Pydantic Settings

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class DatabaseSettings(BaseSettings):
    url: str = Field(
        default="postgresql+asyncpg://localhost/db",
        alias="DATABASE_URL"
    )
    pool_size: int = Field(default=20, alias="DATABASE_POOL_SIZE")
```

### Never Use os.getenv() Directly

```python
# Bad - Can be None, no validation
import os
db_url = os.getenv("DATABASE_URL")

# Good - Validated, typed, with defaults
from src.awfdrs.config import settings
db_url = settings.database.url
```

---

## Logging

### Use Structured Logging

```python
import logging

logger = logging.getLogger(__name__)

# Good - Structured with context
logger.info(
    "Event ingested",
    extra={
        "event_id": str(event.id),
        "tenant_id": str(event.tenant_id),
        "event_type": event.event_type
    }
)

# Bad - String interpolation only
logger.info(f"Event {event.id} ingested")  # Hard to query
```

### Log Levels

```python
logger.debug("Detailed variable state for troubleshooting")
logger.info("Normal operation event occurred")
logger.warning("Unexpected but handled condition")
logger.error("Error requiring attention", exc_info=True)
logger.critical("System-level failure")
```

---

## Performance Best Practices

### Avoid Premature Optimization

**Profile before optimizing:**

```python
# Don't optimize without measurement
# Use cProfile, pytest-benchmark, or similar tools first
```

### Use List Comprehensions for Simple Cases

```python
# Good - Readable and fast
event_ids = [event.id for event in events]

# Avoid - Less Pythonic
event_ids = []
for event in events:
    event_ids.append(event.id)
```

### Cache Expensive Operations

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_error_code_config(error_code: str) -> dict:
    """Cached config lookup (config rarely changes)."""
    return load_yaml_config()["error_codes"][error_code]
```

---

## Git Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code restructuring without behavior change
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks (dependencies, config)

### Examples

```
feat(ingestion): add idempotency key validation

Validates that idempotency keys are unique per tenant to prevent
duplicate event processing.

Closes #123
```

```
fix(circuit-breaker): correct state transition logic

Circuit breaker was not transitioning from HALF_OPEN to CLOSED
correctly. Fixed transition condition.
```

---

## Code Review Checklist

### Before Submitting PR

- [ ] All tests pass (`pytest`)
- [ ] Code formatted with Black (`black src/ tests/`)
- [ ] Linting passes (`ruff check src/ tests/`)
- [ ] Type checking passes (`mypy src/`)
- [ ] Coverage meets minimum threshold (`pytest --cov`)
- [ ] No security issues (`bandit -r src/`)
- [ ] Docstrings added for public functions/classes
- [ ] CHANGELOG.md updated (if applicable)

### During Code Review

- [ ] Code follows naming conventions
- [ ] Type hints present on all functions
- [ ] Exceptions are specific, not broad `except Exception`
- [ ] No hardcoded secrets or sensitive data
- [ ] Logging doesn't leak sensitive information
- [ ] Tests cover edge cases
- [ ] No N+1 database queries
- [ ] Async/await used correctly

---

## Tools Configuration

### Black (pyproject.toml)

```toml
[tool.black]
line-length = 100
target-version = ['py311']
```

### Ruff (pyproject.toml)

```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]
```

### mypy (pyproject.toml)

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
plugins = ["pydantic.mypy"]
```

### pytest (pytest.ini)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --cov=src/awfdrs --cov-report=term-missing
asyncio_mode = auto
```

---

## IDE Configuration

### VS Code (.vscode/settings.json)

```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "editor.rulers": [100]
}
```

---

## Summary

**Consistency is key.** Following these conventions ensures:
- **Readability** - Code is easy to understand
- **Maintainability** - Changes are predictable
- **Collaboration** - Team members follow same patterns
- **Quality** - Automated tools catch issues early

**When in doubt:**
1. Check existing code for patterns
2. Refer to this document
3. Ask during code review
4. Default to PEP 8

**Remember:** These are guidelines to help us write better code. If you have a good reason to deviate, document why in a comment.
