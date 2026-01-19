# Action Coordinator Module

## Overview

The `actions/` module orchestrates automated remediation actions, retry logic, and escalation workflows in response to detected incidents.

## Purpose

- **Action execution** - Execute remediation actions
- **Retry coordination** - Smart retry scheduling with backoff
- **Escalation handling** - Notify humans when automation fails
- **State tracking** - Manage action lifecycle states

---

## Components

### `executor.py` - Action Execution
**Purpose:** Execute remediation actions based on incident analysis.

**Class: ActionExecutor**

```python
async def execute_action(
    self,
    incident: Incident,
    action_type: str,
    parameters: dict
) -> Action:
    """
    Execute remediation action for incident.

    Action Types:
    - retry: Retry failed operation
    - escalate: Notify humans
    - manual_intervention: Create ticket

    Returns:
        Action record with execution result
    """
```

---

### `retry_coordinator.py` - Retry Logic
**Purpose:** Schedule and execute intelligent retries.

**Class: RetryCoordinator**

**Retry Strategies:**
- **Exponential backoff:** delay = initial * (multiplier ^ attempt)
- **Linear backoff:** delay = initial * attempt
- **Fixed delay:** constant delay between retries

**Configuration:** `config/rules/retry_policies.yaml`

```yaml
exponential_backoff:
  retryable: true
  max_retries: 5
  initial_delay_seconds: 1
  max_delay_seconds: 300
  backoff_multiplier: 2.0
  jitter: true  # Add randomness to prevent thundering herd
```

**Key Method:**
```python
async def schedule_retry(
    self,
    incident: Incident,
    attempt_number: int
) -> Action:
    """
    Schedule retry with appropriate backoff.

    Calculates delay based on retry policy:
    - attempt 1: 1s
    - attempt 2: 2s
    - attempt 3: 4s
    - attempt 4: 8s
    - attempt 5: 16s
    (with jitter ±20%)
    """
```

---

### `escalation.py` - Escalation Handler
**Purpose:** Escalate to human operators when automation fails.

**Class: EscalationHandler**

**Escalation Types:**
- **Notification:** Send alert (Slack, email, PagerDuty)
- **Ticket creation:** Create Jira/ServiceNow ticket
- **Manual approval:** Request human decision

**Key Method:**
```python
async def escalate(
    self,
    incident: Incident,
    escalation_level: int = 1
) -> Action:
    """
    Escalate incident to humans.

    Levels:
    1 - Team notification (Slack)
    2 - On-call page (PagerDuty)
    3 - Management escalation

    Note: Mock implementation (no real notifications sent)
    """
```

---

### `state_machine.py` - Action State Management
**Purpose:** Track action execution lifecycle.

**States:**
```
PENDING → IN_PROGRESS → SUCCEEDED
                     → FAILED
```

**Class: ActionStateMachine**

```python
def transition(
    self,
    action: Action,
    new_status: ActionStatus
) -> Action:
    """
    Transition action to new status.

    Validates state transitions:
    - PENDING → IN_PROGRESS (OK)
    - IN_PROGRESS → SUCCEEDED (OK)
    - SUCCEEDED → IN_PROGRESS (INVALID)
    """
```

---

### `api/v1/actions.py` - REST API
**Purpose:** HTTP endpoints for action management.

**Endpoints:**

#### GET /api/v1/actions
List actions with filtering.

**Query Parameters:**
- `tenant_id` (required)
- `incident_id` (optional)
- `status` (optional)
- `action_type` (optional)

#### GET /api/v1/actions/{id}
Get action details.

**Response:**
```json
{
  "id": "act-abc-123",
  "incident_id": "inc-xyz-789",
  "action_type": "retry",
  "status": "SUCCEEDED",
  "parameters": {
    "attempt_number": 3,
    "delay_seconds": 4
  },
  "result": {
    "success": true,
    "message": "Retry succeeded"
  },
  "is_reversible": true,
  "created_at": "2026-01-19T10:00:00Z",
  "completed_at": "2026-01-19T10:00:15Z"
}
```

#### POST /api/v1/actions/{id}/reverse
Reverse a reversible action (undo).

**Request:**
```json
{
  "reason": "Action had unintended consequences"
}
```

#### GET /api/v1/incidents/{id}/actions
Get all actions for an incident.

---

## Action Types

### 1. Retry Action
**Purpose:** Automatically retry failed operations.

**When Used:**
- Transient errors (timeout, network glitch)
- Error code marked as retryable
- Retry count under limit

**Parameters:**
```json
{
  "attempt_number": 3,
  "delay_seconds": 4,
  "original_payload": {...}
}
```

**Execution:**
1. Wait for calculated delay
2. Re-execute original operation
3. Record result (success/failure)
4. If failed and retries remaining, schedule next retry

---

### 2. Escalation Action
**Purpose:** Alert humans to take over.

**When Used:**
- Max retries exceeded
- Error code marked as non-retryable
- Incident severity is CRITICAL
- Manual approval required

**Parameters:**
```json
{
  "escalation_level": 2,
  "notification_channels": ["slack", "pagerduty"],
  "incident_summary": "Payment gateway down"
}
```

**Execution (Mock):**
1. Generate escalation message
2. Log escalation (no real notification sent)
3. Create audit trail
4. Mark action as SUCCEEDED (logged)

---

### 3. Manual Intervention Action
**Purpose:** Create ticket for human investigation.

**When Used:**
- Complex issues requiring human analysis
- Incident pattern not recognized
- System in degraded state

**Parameters:**
```json
{
  "ticket_system": "jira",
  "priority": "high",
  "assignee": "on-call-team"
}
```

---

## Retry Logic

### Exponential Backoff Calculation

```python
def calculate_delay(
    attempt: int,
    initial_delay: float,
    multiplier: float,
    max_delay: float,
    jitter: bool = True
) -> float:
    """
    Calculate retry delay with exponential backoff.

    Formula: delay = min(initial * (multiplier ^ attempt), max_delay)
    With jitter: delay = delay * (1 ± random(0, 0.2))
    """
    delay = min(initial_delay * (multiplier ** attempt), max_delay)

    if jitter:
        jitter_range = delay * 0.2
        delay += random.uniform(-jitter_range, jitter_range)

    return delay
```

**Example (initial=1, multiplier=2, jitter=20%):**
- Attempt 1: 1s ± 0.2s = 0.8-1.2s
- Attempt 2: 2s ± 0.4s = 1.6-2.4s
- Attempt 3: 4s ± 0.8s = 3.2-4.8s
- Attempt 4: 8s ± 1.6s = 6.4-9.6s
- Attempt 5: 16s ± 3.2s = 12.8-19.2s

---

## Safety Limits

### Maximum Retries
**Per Workflow:** 5 retries (configurable)
**Per Vendor:** 100 retries/hour (circuit breaker)

**Enforcement:**
```python
if incident.retry_count >= MAX_RETRIES_PER_WORKFLOW:
    # Stop retrying, escalate instead
    await escalation_handler.escalate(incident)
```

### Reversible Actions
**Purpose:** Allow undo of actions with side effects.

**Examples:**
- Retry: Reversible (can cancel scheduled retry)
- Escalation: Not reversible (can't "un-notify")
- Data modification: Reversible (can restore previous state)

**Implementation:**
```python
class Action:
    is_reversible: bool
    reversal_parameters: Optional[dict]  # Undo instructions

async def reverse_action(action: Action):
    if not action.is_reversible:
        raise ValueError("Action cannot be reversed")

    # Execute reversal logic
    ...
```

---

## Testing

```python
@pytest.mark.asyncio
async def test_retry_coordinator_calculates_exponential_backoff():
    coordinator = RetryCoordinator()

    delay1 = coordinator.calculate_delay(attempt=1, initial=1, multiplier=2)
    delay2 = coordinator.calculate_delay(attempt=2, initial=1, multiplier=2)

    assert 0.8 <= delay1 <= 1.2  # 1s ± jitter
    assert 1.6 <= delay2 <= 2.4  # 2s ± jitter

@pytest.mark.asyncio
async def test_action_executor_respects_max_retries(db_session):
    executor = ActionExecutor(db_session)
    incident = create_incident_with_max_retries_exceeded()

    action = await executor.execute_action(incident, "retry", {})

    # Should escalate instead of retry
    assert action.action_type == "escalate"
```

---

## Monitoring

### Metrics
- `actions_executed_total{action_type, status}` - Action execution counts
- `action_success_rate{action_type}` - Success rate by action type
- `retry_attempts_distribution` - Histogram of retry attempts before success
- `escalations_total{escalation_level}` - Escalation counts by level

### Logging
```json
{
  "level": "INFO",
  "message": "Action executed",
  "action_id": "act-abc-123",
  "incident_id": "inc-xyz-789",
  "action_type": "retry",
  "status": "SUCCEEDED",
  "attempt_number": 3,
  "duration_ms": 150
}
```

### Alerts
- Alert if action failure rate > 20%
- Alert if retry attempts consistently hitting max limit
- Alert if escalation_level 2+ triggered

---

## See Also

- [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) - System design
- [config/rules/retry_policies.yaml](../../../config/rules/retry_policies.yaml) - Retry configuration
