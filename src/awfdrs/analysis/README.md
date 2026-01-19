# Incident Analysis Module

## Overview

The `analysis/` module handles failure detection, incident correlation, and incident lifecycle management. It transforms individual events into actionable incidents.

## Purpose

- **Failure detection** - Identify failures from events
- **Error grouping** - Group similar errors into incidents
- **Correlation** - Link related events to incidents
- **Lifecycle management** - Track incidents from detection to resolution

---

## Components

### `signature.py` - Error Signature Generation
**Purpose:** Create unique fingerprints for error patterns.

**Key Function:**
```python
def generate_signature(event: Event) -> str:
    """
    Generate error signature for incident grouping.

    Format: {event_type}:{error_code}:{workflow_id}

    Example: "payment.failed:timeout:wf-123"
    """
```

**Signature Rules:**
- Normalize error codes (lowercase, strip whitespace)
- Include workflow_id for workflow-specific grouping
- Consistent format for query efficiency

---

### `incident_detector.py` - Failure Detection
**Purpose:** Detect failures from events and create/update incidents.

**Class: IncidentDetector**

**Key Method:**
```python
async def detect(self, event: Event) -> Optional[Incident]:
    """
    Analyze event and create/update incident if failure detected.

    Steps:
    1. Check if event represents a failure
    2. Generate error signature
    3. Find existing incident with same signature
    4. Create new incident OR update existing (increment event_count)

    Returns:
        Incident if failure detected, None otherwise
    """
```

**Failure Criteria:**
- Event type contains "failed", "error", "timeout"
- Payload contains error_code
- Configurable pattern matching

---

### `correlator.py` - Event Correlation
**Purpose:** Link related events to incidents.

**Class: EventCorrelator**

**Key Method:**
```python
async def correlate_events(
    self,
    incident: Incident,
    time_window_hours: int = 24
) -> List[Event]:
    """
    Find events related to incident within time window.

    Correlation Strategy:
    - Same workflow_id
    - Same error signature
    - Within time window of first occurrence

    Returns:
        List of correlated events
    """
```

---

### `incident_manager.py` - Lifecycle Management
**Purpose:** Manage incident status transitions and operations.

**Class: IncidentManager**

**Key Methods:**
```python
async def create_incident(self, event: Event) -> Incident:
    """Create new incident from event."""

async def update_status(
    self,
    incident_id: UUID,
    new_status: IncidentStatus
) -> Incident:
    """Transition incident to new status."""

async def mark_resolved(self, incident_id: UUID) -> Incident:
    """Mark incident as resolved."""

async def mark_ignored(
    self,
    incident_id: UUID,
    reason: str
) -> Incident:
    """Mark incident as ignored with reason."""

async def get_similar_incidents(
    self,
    incident: Incident,
    limit: int = 10
) -> List[Incident]:
    """Find historically similar incidents (for learning)."""
```

---

### `api/v1/incidents.py` - REST API
**Purpose:** HTTP endpoints for incident management.

**Endpoints:**

#### GET /api/v1/incidents
List incidents with filtering and pagination.

**Query Parameters:**
- `tenant_id` (required) - Tenant UUID
- `status` (optional) - Filter by status
- `severity` (optional) - Filter by severity
- `workflow_id` (optional) - Filter by workflow
- `page` (default: 1)
- `page_size` (default: 20)

**Response:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20
}
```

#### GET /api/v1/incidents/{id}
Get incident details.

**Response:**
```json
{
  "id": "inc-abc-123",
  "signature": "payment.failed:timeout:wf-123",
  "title": "Payment timeout errors",
  "status": "ANALYZING",
  "severity": "high",
  "event_count": 15,
  "first_seen_at": "2026-01-19T10:00:00Z",
  "last_seen_at": "2026-01-19T11:30:00Z"
}
```

#### GET /api/v1/incidents/{id}/events
Get events correlated to incident.

#### PATCH /api/v1/incidents/{id}/status
Update incident status.

**Request:**
```json
{
  "status": "RESOLVED"
}
```

#### POST /api/v1/incidents/{id}/ignore
Mark incident as ignored.

**Request:**
```json
{
  "reason": "Known issue, not actionable"
}
```

---

## Incident Lifecycle

```
NEW (created)
  ↓
ANALYZING (AI analysis in progress)
  ↓
ACTIONED (remediation executed)
  ↓
RESOLVED (issue fixed)

or

IGNORED (marked as non-actionable)
```

**State Transitions:**
- NEW → ANALYZING (automatic, when AI analysis starts)
- ANALYZING → ACTIONED (when action executed)
- ACTIONED → RESOLVED (when action succeeds)
- ACTIONED → NEW (if action fails, retry)
- Any state → IGNORED (manual intervention)

---

## Incident Severity

**Calculation:**
Based on error code configuration in `config/rules/error_codes.yaml`.

**Levels:**
- `CRITICAL` - System-wide outage, data loss
- `HIGH` - Major functionality broken, revenue impact
- `MEDIUM` - Non-critical feature degraded
- `LOW` - Minor issue, workaround available

**Auto-escalation:**
- Incident event_count > 100 → Upgrade severity
- Incident duration > 1 hour → Upgrade severity

---

## Signature Generation Examples

```python
# Payment timeout
Event: {event_type: "payment.failed", error_code: "timeout"}
Signature: "payment.failed:timeout:wf-abc-123"

# Database connection error
Event: {event_type: "db.error", error_code: "connection_refused"}
Signature: "db.error:connection_refused:wf-xyz-789"

# Generic error (no error_code)
Event: {event_type: "order.failed", error_code: null}
Signature: "order.failed:unknown:wf-def-456"
```

---

## Correlation Strategy

### Time-Based Correlation
Group events that occur within time window (default: 24 hours).

### Signature-Based Correlation
Group events with identical error signatures.

### Workflow-Based Correlation
Only correlate events from same workflow (tenant isolation).

**Example:**
```
Incident: "payment.failed:timeout:wf-123"
Correlated Events:
  - Event 1: 2026-01-19T10:00:00Z
  - Event 2: 2026-01-19T10:15:00Z
  - Event 3: 2026-01-19T10:30:00Z
  - ... (all with same signature, last 24 hours)
```

---

## Performance

### Caching
- Incident signatures cached (5 minutes)
- Error code configuration cached (until restart)

### Indexing
```sql
CREATE INDEX ix_incidents_signature ON incidents(tenant_id, signature);
CREATE INDEX ix_incidents_status ON incidents(tenant_id, status);
CREATE INDEX ix_incidents_severity ON incidents(severity);
CREATE INDEX ix_events_signature ON events(tenant_id, event_type, occurred_at);
```

### Query Optimization
```python
# Good - Use signature for grouping
incidents = await repo.find_by_signature(signature, tenant_id)

# Bad - Full table scan
incidents = await repo.get_all().filter(lambda i: i.signature == signature)
```

---

## Testing

```python
def test_signature_generator_normalizes_error_code():
    event = Event(event_type="payment.failed", error_code="TIMEOUT")
    signature = SignatureGenerator().generate(event)
    assert "timeout" in signature.lower()

@pytest.mark.asyncio
async def test_incident_detector_creates_new_incident(db_session):
    detector = IncidentDetector(db_session)
    event = create_failure_event()

    incident = await detector.detect(event)

    assert incident is not None
    assert incident.status == IncidentStatus.NEW
    assert incident.event_count == 1
```

---

## Monitoring

### Metrics
- `incidents_detected_total` - Total incidents created
- `incidents_by_severity` - Breakdown by severity level
- `incident_detection_latency_seconds` - Time from event to incident
- `incident_event_count_distribution` - Histogram of event counts per incident

### Alerts
- Alert if CRITICAL incidents > 5 per hour
- Alert if incident remains in NEW status > 1 hour
- Alert if incident event_count > 1000 (unusual pattern)

---

## See Also

- [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) - System design
- [METRICS.md](../../../docs/METRICS.md) - Observability
