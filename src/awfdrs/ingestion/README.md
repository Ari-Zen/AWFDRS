# Event Ingestion Module

## Overview

The `ingestion/` module handles all incoming workflow events. It serves as the primary entry point for external systems to report workflow failures, successes, and status updates.

## Purpose

- **Event validation** - Validate event structure and data
- **Idempotency** - Prevent duplicate event processing
- **Tenant isolation** - Enforce tenant-scoped access
- **Safety controls** - Rate limiting and kill switch enforcement
- **Audit trail** - Immutable event storage with correlation tracking

---

## Architecture

```
External System
    ↓
POST /api/v1/events
    ↓
EventValidator (schemas, validators)
    ↓
IngestionService (business logic)
    ↓
EventRepository (data persistence)
    ↓
Incident Detector (trigger)
```

---

## Components

### `api/v1/events.py`
**Purpose:** FastAPI route handlers for event ingestion.

**Endpoints:**

#### POST /api/v1/events
Submit a workflow event for processing.

**Request:**
```json
{
  "tenant_id": "00000000-0000-0000-0000-000000000001",
  "workflow_id": "10000000-0000-0000-0000-000000000001",
  "event_type": "payment.failed",
  "payload": {
    "amount": 100.00,
    "error_code": "payment_timeout",
    "vendor": "stripe"
  },
  "idempotency_key": "unique-key-001",
  "occurred_at": "2026-01-19T10:00:00Z",
  "schema_version": "1.0.0"
}
```

**Response (201 Created):**
```json
{
  "event_id": "evt-abc-123",
  "status": "accepted",
  "correlation_id": "req-xyz-789"
}
```

**Error Responses:**
- `400` - Invalid request (validation failure)
- `403` - Workflow is kill-switched
- `404` - Tenant or workflow not found
- `409` - Duplicate idempotency key
- `429` - Rate limit exceeded
- `503` - Circuit breaker open

---

### `api/v1/health.py`
**Purpose:** Health check endpoints.

**Endpoints:**

#### GET /api/v1/health
Basic health check (always returns 200 if service is running).

**Response:**
```json
{
  "status": "ok"
}
```

#### GET /api/v1/health/ready
Readiness check (verifies database and Redis connectivity).

**Response (200 OK):**
```json
{
  "status": "ready",
  "database": "ok",
  "redis": "ok"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "not_ready",
  "database": "error",
  "redis": "ok",
  "details": {"database": "Connection refused"}
}
```

---

### `schemas.py`
**Purpose:** Pydantic models for request/response validation.

**Models:**

#### WorkflowEventV1
```python
class WorkflowEventV1(BaseModel):
    """Event submission schema."""
    tenant_id: UUID
    workflow_id: UUID
    event_type: str = Field(..., min_length=1, max_length=255)
    payload: dict
    idempotency_key: str = Field(..., min_length=1, max_length=255)
    occurred_at: datetime
    schema_version: str = "1.0.0"
```

#### EventResponse
```python
class EventResponse(BaseModel):
    """Event ingestion response."""
    event_id: UUID
    status: str  # "accepted"
    correlation_id: str
```

---

### `validators.py`
**Purpose:** Business validation logic.

**Validators:**

#### TenantValidator
```python
async def validate_tenant(tenant_id: UUID, session: AsyncSession) -> Tenant:
    """
    Validate tenant exists and is active.

    Raises:
        NotFoundError: Tenant not found
        ValidationError: Tenant is inactive
    """
```

#### WorkflowValidator
```python
async def validate_workflow(
    workflow_id: UUID,
    tenant_id: UUID,
    session: AsyncSession
) -> Workflow:
    """
    Validate workflow exists and is not kill-switched.

    Raises:
        NotFoundError: Workflow not found
        ValidationError: Workflow is inactive or kill-switched
    """
```

#### IdempotencyValidator
```python
async def validate_idempotency(
    idempotency_key: str,
    tenant_id: UUID,
    session: AsyncSession
) -> None:
    """
    Validate idempotency key is unique for tenant.

    Raises:
        DuplicateError: Event with this key already exists
    """
```

---

### `service.py`
**Purpose:** Core ingestion business logic.

**Class: IngestionService**

**Methods:**

#### ingest_event()
```python
async def ingest_event(self, event: WorkflowEventV1) -> EventResponse:
    """
    Ingest and process workflow event.

    Steps:
    1. Validate idempotency (prevent duplicates)
    2. Validate tenant (active?)
    3. Validate workflow (exists? kill-switched?)
    4. Check rate limits
    5. Store event (immutable)
    6. Trigger incident detection
    7. Return response

    Args:
        event: Validated event data

    Returns:
        EventResponse with event_id and correlation_id

    Raises:
        ValidationError: Invalid data
        NotFoundError: Tenant/workflow not found
        DuplicateError: Idempotency key collision
        RateLimitError: Rate limit exceeded
    """
```

---

## Data Flow

### Happy Path

```
1. Client sends POST /api/v1/events
   ↓
2. Pydantic validates schema (WorkflowEventV1)
   ↓
3. Middleware injects correlation_id
   ↓
4. IngestionService.ingest_event() called
   ↓
5. Idempotency check (duplicate?)
   - No: Continue
   - Yes: Return 409 Conflict
   ↓
6. Tenant validation (active?)
   - Yes: Continue
   - No: Return 404 or 400
   ↓
7. Workflow validation (exists? kill-switched?)
   - Valid: Continue
   - Invalid: Return 404 or 403
   ↓
8. Rate limit check (under limit?)
   - Yes: Continue
   - No: Return 429 Too Many Requests
   ↓
9. Store event in database (immutable)
   ↓
10. Trigger incident detection (async)
   ↓
11. Commit transaction
   ↓
12. Return 201 Created with event_id
```

### Error Paths

**Duplicate Event (409):**
```
Idempotency check fails
  ↓
Return 409 with existing event_id
```

**Inactive Tenant (400/404):**
```
Tenant validation fails
  ↓
Return 404 if not found
Return 400 if inactive
```

**Kill-Switched Workflow (403):**
```
Workflow validation finds active kill switch
  ↓
Return 403 Forbidden with reason
```

**Rate Limit Exceeded (429):**
```
Rate limiter rejects request
  ↓
Return 429 with retry-after header
```

---

## Validation Rules

### Event Type Format
- **Pattern:** `category.action` (e.g., `payment.failed`, `order.completed`)
- **Length:** 1-255 characters
- **Characters:** Alphanumeric, dots, underscores only
- **Case:** Case-sensitive (recommend lowercase)

**Valid:**
- `payment.failed`
- `order.shipped`
- `user.login_failed`

**Invalid:**
- `` (empty string)
- `payment` (missing action)
- `payment-failed` (hyphen not allowed)
- `PAYMENT.FAILED` (uppercase not recommended but allowed)

### Idempotency Key
- **Purpose:** Prevent duplicate processing
- **Scope:** Unique per tenant (not globally unique)
- **Length:** 1-255 characters
- **Recommendation:** Use UUID or `{source}-{id}-{timestamp}`

**Examples:**
- `stripe-payment-123-1642598400`
- `a1b2c3d4-e5f6-4789-a0b1-c2d3e4f5g6h7`
- `order-456-retry-1`

### Payload
- **Type:** JSON object (dict)
- **Size limit:** 10 KB recommended (no hard limit enforced)
- **Structure:** Freeform, but should be consistent per event_type
- **Sensitive data:** Avoid PII or secrets in payload (logs may capture this)

---

## Safety Controls

### Idempotency Enforcement
**Purpose:** Prevent duplicate event processing.

**Implementation:**
- Unique index on `(tenant_id, idempotency_key)`
- Check before insertion
- Return existing event_id if duplicate detected

**Benefits:**
- Safe retries (client can retry without creating duplicates)
- Network failure resilience

### Rate Limiting
**Purpose:** Prevent abuse and DoS attacks.

**Implementation:**
- Redis-backed sliding window
- Separate limits per tenant and per vendor
- Configurable thresholds

**Limits:**
- Per tenant: 1000 requests/minute (default)
- Per vendor (in payload): 100 requests/minute (default)

### Kill Switches
**Purpose:** Emergency workflow disabling.

**Types:**
- **Tenant-wide:** Disable all workflows for tenant
- **Workflow-specific:** Disable single workflow

**Response:**
- HTTP 403 Forbidden
- Response includes kill switch reason

---

## Error Handling

### Structured Error Responses

**Format:**
```json
{
  "error": "Human-readable error message",
  "details": {
    "field": "specific_field",
    "reason": "detailed_reason"
  },
  "correlation_id": "req-abc-123"
}
```

**Examples:**

**Validation Error (400):**
```json
{
  "error": "Validation failed",
  "details": {
    "field": "event_type",
    "reason": "Field must not be empty"
  },
  "correlation_id": "req-abc-123"
}
```

**Not Found (404):**
```json
{
  "error": "Tenant not found",
  "details": {
    "tenant_id": "00000000-0000-0000-0000-000000000001"
  },
  "correlation_id": "req-abc-123"
}
```

**Kill Switch (403):**
```json
{
  "error": "Workflow is disabled via kill switch",
  "details": {
    "workflow_id": "10000000-0000-0000-0000-000000000001",
    "reason": "Emergency maintenance"
  },
  "correlation_id": "req-abc-123"
}
```

---

## Testing

### Unit Tests
```python
@pytest.mark.asyncio
async def test_ingest_event_accepts_valid_payload(mock_session):
    service = IngestionService(mock_session, "corr-123")

    event = WorkflowEventV1(
        tenant_id=UUID(...),
        workflow_id=UUID(...),
        event_type="payment.failed",
        payload={},
        idempotency_key="test-001",
        occurred_at=datetime.utcnow()
    )

    response = await service.ingest_event(event)

    assert response.status == "accepted"
    assert response.event_id is not None
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_duplicate_event_returns_409(test_client, db_session):
    # Submit event first time
    response1 = await test_client.post("/api/v1/events", json=event_data)
    assert response1.status_code == 201

    # Submit same event again (same idempotency_key)
    response2 = await test_client.post("/api/v1/events", json=event_data)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["error"].lower()
```

---

## Performance Considerations

### Indexing
```sql
CREATE INDEX ix_events_idempotency ON events(tenant_id, idempotency_key);
CREATE INDEX ix_events_workflow ON events(tenant_id, workflow_id);
CREATE INDEX ix_events_occurred ON events(tenant_id, occurred_at);
```

### Caching
- Tenant validation results (5 minutes)
- Workflow validation results (5 minutes)
- Kill switch status (1 minute)

### Async Processing
- Incident detection runs asynchronously (doesn't block response)
- Event storage is synchronous (ensures durability)

---

## Monitoring

### Key Metrics
- `events_ingested_total` - Total events accepted
- `events_rejected_total` - Events rejected (by reason)
- `ingestion_latency_seconds` - P50/P95/P99 latency
- `idempotency_duplicates_total` - Duplicate submissions

### Logging
```json
{
  "level": "INFO",
  "message": "Event ingested",
  "event_id": "evt-abc-123",
  "tenant_id": "tenant-001",
  "workflow_id": "workflow-123",
  "event_type": "payment.failed",
  "correlation_id": "req-xyz-789",
  "duration_ms": 45
}
```

### Alerts
- Alert if ingestion latency P95 > 100ms
- Alert if rejection rate > 10%
- Alert if ingestion drops to 0 (service down?)

---

## See Also

- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) - System design
- [TESTING.md](../../../docs/TESTING.md) - Testing strategies
- [METRICS.md](../../../docs/METRICS.md) - Observability
