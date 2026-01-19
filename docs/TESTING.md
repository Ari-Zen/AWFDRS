# AWFDRS Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for AWFDRS, including unit tests, integration tests, test coverage requirements, and testing best practices.

---

## Testing Philosophy

### Core Principles

1. **Test Behavior, Not Implementation** - Tests should verify observable behavior, not internal implementation details
2. **Fast Feedback** - Unit tests must be fast (<1s total), integration tests acceptable up to 30s
3. **Deterministic** - Tests must produce consistent results (no flaky tests)
4. **Isolated** - Each test is independent and can run in any order
5. **Readable** - Tests serve as living documentation of system behavior
6. **Mock External Dependencies** - Never call real APIs or external services in tests

---

## Test Pyramid

```
               ╱╲
              ╱  ╲
             ╱ E2E ╲          5%  - End-to-end (future)
            ╱──────╲
           ╱        ╲
          ╱   Integ  ╲        20% - Integration tests
         ╱────────────╲
        ╱              ╲
       ╱      Unit      ╲     75% - Unit tests
      ╱──────────────────╲
```

**Target Coverage:**
- **Overall:** 85% minimum
- **Core business logic:** 95% minimum
- **API handlers:** 90% minimum
- **Database repositories:** 90% minimum
- **Utilities:** 80% minimum

---

## Test Categories

### 1. Unit Tests (`tests/unit/`)

**Purpose:** Test individual functions, classes, and methods in isolation.

**Characteristics:**
- **No database** - Mock all database calls
- **No external services** - Mock Redis, AI clients, external APIs
- **No I/O** - Mock file system operations
- **Fast** - Each test <10ms, full suite <1s
- **Focused** - One logical assertion per test

**Example Structure:**

```python
# tests/unit/test_signature_generator.py
from src.awfdrs.analysis.signature import SignatureGenerator

def test_generate_signature_for_payment_timeout():
    """Test signature generation for payment timeout error."""
    # ARRANGE
    generator = SignatureGenerator()
    event_data = {
        "event_type": "payment.failed",
        "payload": {"error_code": "payment_timeout"},
        "workflow_id": "wf-123"
    }

    # ACT
    signature = generator.generate(event_data)

    # ASSERT
    assert signature == "payment.failed:payment_timeout:wf-123"
    assert isinstance(signature, str)
```

**What to Test:**
- Business logic functions
- Data transformations
- Validation rules
- Error handling
- Edge cases and boundary conditions

**What NOT to Test:**
- Database queries (use integration tests)
- External API calls (use mocks)
- Framework internals (FastAPI, SQLAlchemy)

### 2. Integration Tests (`tests/integration/`)

**Purpose:** Test component interactions with real dependencies (database, Redis).

**Characteristics:**
- **Real database** - Use test database with migrations
- **Real Redis** - Use separate Redis DB index for tests
- **Mock external services** - Still mock AI, vendor APIs
- **Slower** - Each test <500ms, full suite <30s
- **Transactional** - Each test rolls back database changes

**Example Structure:**

```python
# tests/integration/test_event_repository.py
import pytest
from src.awfdrs.db.repositories.events import EventRepository

@pytest.mark.asyncio
async def test_create_event_stores_in_database(db_session, mock_event_data):
    """Test event creation persists to database."""
    # ARRANGE
    repo = EventRepository(db_session)

    # ACT
    event = await repo.create(mock_event_data)
    await db_session.commit()

    # ASSERT
    retrieved = await repo.get_by_id(event.id)
    assert retrieved is not None
    assert retrieved.event_type == mock_event_data["event_type"]
    assert retrieved.idempotency_key == mock_event_data["idempotency_key"]
```

**What to Test:**
- Database CRUD operations
- Transaction handling
- Repository methods
- Multi-step workflows
- API endpoint flows (POST → DB → GET)

### 3. End-to-End Tests (Future)

**Purpose:** Test complete user workflows through the API.

**Characteristics:**
- **Full stack** - Real HTTP requests to running application
- **Real dependencies** - Database, Redis, all services
- **Mock external only** - AI and vendor APIs still mocked
- **Slowest** - Each test 1-5s
- **User-centric** - Test from user perspective

**Example Scenarios:**
- Submit event → Detect incident → Execute action → Verify outcome
- Rate limiting: Submit 100 events → Verify throttling
- Circuit breaker: Trigger failures → Verify breaker opens

---

## Test Organization

### Directory Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── unit/                          # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_signature.py
│   ├── test_rules_engine.py
│   ├── test_circuit_breaker.py
│   ├── test_validators.py
│   └── test_utils.py
├── integration/                   # Integration tests (DB, Redis)
│   ├── __init__.py
│   ├── test_ingestion_flow.py
│   ├── test_event_repository.py
│   ├── test_incident_manager.py
│   └── test_action_executor.py
├── mocks/                         # Mock implementations
│   ├── __init__.py
│   ├── mock_openai.py
│   ├── mock_pinecone.py
│   └── mock_vendors.py
└── fixtures/                      # Test data
    ├── __init__.py
    └── events.py
```

### Naming Conventions

- **Test files:** `test_<module_name>.py`
- **Test functions:** `test_<function_name>_<scenario>()`
- **Fixtures:** `<resource_name>_fixture()` or `mock_<service>()`
- **Test classes:** `Test<ClassName>` (use sparingly, prefer flat functions)

**Examples:**
```python
test_validate_event_accepts_valid_payload()
test_validate_event_rejects_missing_tenant_id()
test_circuit_breaker_opens_after_threshold_exceeded()
test_rate_limiter_blocks_request_when_limit_exceeded()
```

---

## Fixtures (`tests/conftest.py`)

### Database Fixtures

```python
@pytest.fixture
async def db_session():
    """Provide isolated database session for each test."""
    # Create session
    session = AsyncSession(test_engine)

    # Run migrations
    await run_migrations()

    yield session

    # Rollback and cleanup
    await session.rollback()
    await session.close()
```

### Mock Fixtures

```python
@pytest.fixture
def mock_openai_client():
    """Provide mock OpenAI client with deterministic responses."""
    from tests.mocks.mock_openai import MockOpenAIClient
    return MockOpenAIClient()

@pytest.fixture
def mock_redis():
    """Provide mock Redis client."""
    from unittest.mock import AsyncMock
    redis = AsyncMock()
    redis.incr.return_value = 1
    redis.expire.return_value = True
    return redis
```

### Data Fixtures

```python
@pytest.fixture
def valid_event_payload():
    """Provide valid event data for testing."""
    return {
        "tenant_id": "00000000-0000-0000-0000-000000000001",
        "workflow_id": "10000000-0000-0000-0000-000000000001",
        "event_type": "payment.failed",
        "payload": {
            "amount": 100.00,
            "error_code": "payment_timeout"
        },
        "idempotency_key": "test-event-001",
        "occurred_at": "2026-01-19T10:00:00Z",
        "schema_version": "1.0.0"
    }
```

---

## Mock Implementations

### Mock AI Clients (`tests/mocks/`)

**Purpose:** Deterministic AI responses with zero API costs.

**mock_openai.py:**
```python
class MockOpenAIClient:
    """Mock OpenAI client that returns deterministic responses."""

    def __init__(self):
        self.chat = MockChatCompletion()

class MockChatCompletion:
    """Mock chat completion endpoint."""

    async def create(self, model: str, messages: list, **kwargs):
        """Return deterministic mock response."""
        prompt = messages[-1]["content"]

        if "classify" in prompt.lower():
            return MockChatResponse(
                content='{"category": "payment_failure", "confidence": 0.95}'
            )
        elif "root cause" in prompt.lower():
            return MockChatResponse(
                content='{"root_cause": "gateway_timeout", "evidence": [...]}'
            )
        else:
            return MockChatResponse(content='{"analysis": "mock response"}')
```

**mock_pinecone.py:**
```python
class MockPineconeClient:
    """Mock Pinecone vector database."""

    def __init__(self):
        self.index_data = {}

    async def query(self, vector: list, top_k: int = 5):
        """Return deterministic similar incidents."""
        return {
            "matches": [
                {"id": "inc-001", "score": 0.95, "metadata": {...}},
                {"id": "inc-002", "score": 0.87, "metadata": {...}}
            ]
        }
```

### Mock Vendor APIs (`tests/mocks/mock_vendors.py`)

```python
class MockStripeClient:
    """Mock Stripe API for testing payment retry logic."""

    def __init__(self, should_succeed: bool = True):
        self.should_succeed = should_succeed
        self.call_count = 0

    async def process_payment(self, payment_id: str):
        """Mock payment processing."""
        self.call_count += 1

        if self.should_succeed:
            return {"status": "success", "transaction_id": "txn-123"}
        else:
            raise PaymentError("Gateway timeout")
```

---

## Test Coverage Requirements

### Per-Module Coverage Targets

| Module | Minimum Coverage | Rationale |
|--------|------------------|-----------|
| `core/` | 80% | Shared utilities, lower risk |
| `db/models/` | 60% | ORM models, mostly framework code |
| `db/repositories/` | 90% | Data access critical path |
| `ingestion/` | 90% | Entry point, high risk |
| `analysis/` | 95% | Core business logic |
| `actions/` | 90% | Remediation critical |
| `safety/` | 95% | Safety controls, must be reliable |
| `ai/` | 80% | Mock implementations, lower risk |

### Coverage Enforcement

**Run with coverage:**
```bash
pytest --cov=src/awfdrs --cov-report=html --cov-report=term-missing
```

**Coverage report:**
```
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
src/awfdrs/analysis/signature.py      45      2    95%   78-79
src/awfdrs/safety/circuit_breaker.py  67      3    96%   121, 145, 189
...
-----------------------------------------------------------------
TOTAL                               2847    142    95%
```

**Fail on insufficient coverage:**
```bash
pytest --cov=src/awfdrs --cov-fail-under=85
```

### Uncovered Code Categories

**Acceptable to skip:**
- Exception handlers for truly exceptional cases (disk full, out of memory)
- Logging statements
- `if __name__ == "__main__"` blocks
- Abstract base class methods (if never called directly)
- Defensive assertions that should never trigger

**Mark with pragma:**
```python
def handle_catastrophic_failure():  # pragma: no cover
    """This should never happen in normal operation."""
    sys.exit(1)
```

---

## Testing Best Practices

### 1. Arrange-Act-Assert Pattern

```python
def test_circuit_breaker_opens_after_threshold():
    # ARRANGE - Set up test data and dependencies
    breaker = CircuitBreaker(threshold=3)

    # ACT - Perform the action being tested
    for _ in range(3):
        breaker.record_failure()

    # ASSERT - Verify expected outcome
    assert breaker.state == CircuitBreakerState.OPEN
```

### 2. One Assertion per Test (Guideline)

**Prefer:**
```python
def test_event_has_correlation_id():
    event = create_event()
    assert event.correlation_id is not None

def test_event_correlation_id_is_uuid():
    event = create_event()
    assert UUID(event.correlation_id)  # Raises if invalid UUID
```

**Over:**
```python
def test_event_correlation_id():  # Testing too much
    event = create_event()
    assert event.correlation_id is not None
    assert isinstance(event.correlation_id, str)
    assert len(event.correlation_id) == 36
    assert UUID(event.correlation_id)
```

### 3. Descriptive Test Names

**Good:**
```python
test_ingestion_service_rejects_event_with_inactive_tenant()
test_rate_limiter_allows_request_when_under_limit()
test_signature_generator_normalizes_error_codes_to_lowercase()
```

**Bad:**
```python
test_ingestion()
test_rate_limit()
test_signature()
```

### 4. Test Edge Cases

**Always test:**
- Empty inputs (`[]`, `{}`, `""`)
- None values
- Boundary conditions (0, -1, MAX_INT)
- Duplicates
- Concurrent access (when relevant)

### 5. Async Test Handling

**Use pytest-asyncio:**
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

### 6. Parameterized Tests

**Test multiple scenarios efficiently:**
```python
@pytest.mark.parametrize("error_code,expected_severity", [
    ("payment_timeout", "high"),
    ("network_error", "medium"),
    ("validation_error", "low"),
])
def test_rules_engine_assigns_correct_severity(error_code, expected_severity):
    rules = RulesEngine()
    severity = rules.get_severity(error_code)
    assert severity == expected_severity
```

---

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Category

```bash
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
```

### Run Specific Test File

```bash
pytest tests/unit/test_signature.py
```

### Run Specific Test

```bash
pytest tests/unit/test_signature.py::test_generate_signature_for_payment_timeout
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage

```bash
pytest --cov=src/awfdrs --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Run with Markers

```bash
pytest -m "not slow"     # Skip slow tests
pytest -m "integration"  # Run only integration tests
```

### Run Failed Tests Only

```bash
pytest --lf  # Last failed
pytest --ff  # Failed first, then others
```

---

## Continuous Integration

### Pre-commit Hooks

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

### GitHub Actions (Example)

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests with coverage
        run: pytest --cov=src/awfdrs --cov-fail-under=85
```

---

## Test Data Management

### Fixture Data Strategy

1. **Minimal fixtures** - Only create data necessary for the test
2. **Reusable fixtures** - Define common data in `conftest.py`
3. **Factory functions** - For complex object creation

**Example factory:**
```python
def create_event(
    tenant_id=DEFAULT_TENANT,
    workflow_id=DEFAULT_WORKFLOW,
    event_type="test.event",
    **overrides
):
    """Factory function for creating test events."""
    data = {
        "tenant_id": tenant_id,
        "workflow_id": workflow_id,
        "event_type": event_type,
        "payload": {},
        "idempotency_key": f"test-{uuid4()}",
        "occurred_at": datetime.utcnow().isoformat(),
        "schema_version": "1.0.0",
    }
    data.update(overrides)
    return data
```

### Database Seeding for Tests

**Seed minimal required data:**
```python
@pytest.fixture(scope="session")
async def seed_test_data(db_session):
    """Seed required reference data for tests."""
    # Create test tenant
    tenant = Tenant(id=TEST_TENANT_ID, name="Test Tenant", is_active=True)
    db_session.add(tenant)

    # Create test workflow
    workflow = Workflow(
        id=TEST_WORKFLOW_ID,
        tenant_id=TEST_TENANT_ID,
        name="Test Workflow",
        is_active=True
    )
    db_session.add(workflow)

    await db_session.commit()
```

---

## Troubleshooting Tests

### Flaky Tests

**Common causes:**
- Time-dependent tests (use freezegun or fixed timestamps)
- Race conditions (ensure proper async/await)
- Shared state between tests (ensure isolation)
- External dependencies (mock everything external)

**Fix time-dependent tests:**
```python
from freezegun import freeze_time

@freeze_time("2026-01-19 10:00:00")
def test_timestamp_calculation():
    result = calculate_expiry()
    assert result == "2026-01-19 11:00:00"
```

### Slow Tests

**Identify slow tests:**
```bash
pytest --durations=10  # Show 10 slowest tests
```

**Optimize:**
- Move to integration tests if doing I/O
- Use smaller test data sets
- Mock expensive operations
- Use session-scoped fixtures for shared setup

### Database Test Failures

**Common issues:**
- Migrations not applied
- Connection pool exhaustion
- Uncommitted transactions

**Debug:**
```python
@pytest.fixture
async def db_session():
    session = AsyncSession(engine)

    # Run migrations
    await run_migrations()

    yield session

    # Cleanup
    await session.rollback()  # Undo test changes
    await session.close()
```

---

## Test Quality Metrics

### Track Over Time

1. **Coverage percentage** - Target: 85%+
2. **Test execution time** - Target: <30s for full suite
3. **Flaky test rate** - Target: 0%
4. **Test count** - Track growth with codebase

### Code Review Checklist

- [ ] New code has corresponding tests
- [ ] Tests follow naming conventions
- [ ] Tests are isolated and deterministic
- [ ] No real external API calls in tests
- [ ] Coverage meets minimum threshold
- [ ] Tests document expected behavior
- [ ] Edge cases are tested
- [ ] Async tests use `@pytest.mark.asyncio`

---

## Additional Resources

- **pytest documentation:** https://docs.pytest.org/
- **pytest-asyncio:** https://pytest-asyncio.readthedocs.io/
- **pytest-cov:** https://pytest-cov.readthedocs.io/
- **unittest.mock:** https://docs.python.org/3/library/unittest.mock.html

---

## Summary

**Testing is not optional** - It's a core part of development at AWFDRS. Every feature must have tests before being merged.

**Quick Reference:**
- Unit tests: Fast, isolated, mock everything
- Integration tests: Real database, mock external services
- Coverage target: 85% minimum overall
- Run tests: `pytest --cov=src/awfdrs`
- Pre-commit: Tests run automatically before commit

**When in doubt:** Write the test. Test behavior, not implementation. Keep tests simple and readable.
