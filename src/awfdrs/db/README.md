# Database Layer Module

## Overview

The `db/` module contains all database-related components: ORM models, repositories, session management, and base classes. This layer abstracts all data persistence concerns from business logic.

## Purpose

- **Data persistence** - Store and retrieve application data
- **Repository pattern** - Abstract database access from services
- **Transaction management** - Control commit/rollback boundaries
- **Tenant isolation** - Enforce multi-tenant data separation
- **Type safety** - SQLAlchemy 2.0 with full type hints

## Architecture

```
Services (business logic)
    ↓
Repositories (data access abstraction)
    ↓
Models (SQLAlchemy ORM)
    ↓
Database (PostgreSQL)
```

---

## Components

### `base.py`
**Purpose:** Base model classes and reusable mixins.

**Classes:**
- `BaseModel` - Base for all ORM models (adds `id`, `created_at`, `updated_at`)
- `TenantMixin` - Adds `tenant_id` for multi-tenant isolation
- `CorrelationMixin` - Adds `correlation_id` for request tracing

**Usage:**
```python
from src.awfdrs.db.base import BaseModel, TenantMixin

class Event(BaseModel, TenantMixin):
    __tablename__ = "events"

    event_type: Mapped[str] = mapped_column(String(255))
    # Inherits: id, created_at, updated_at, tenant_id
```

---

### `session.py`
**Purpose:** Database session and connection management.

**Functions:**
- `get_engine()` - Create async SQLAlchemy engine
- `get_session()` - Async context manager for database sessions
- `close_db()` - Cleanup database connections

**Configuration:**
- Connection pooling (configurable pool size)
- Async PostgreSQL driver (asyncpg)
- Automatic session cleanup

**Usage:**
```python
from src.awfdrs.db.session import get_session

async def my_service_function():
    async with get_session() as session:
        # Use session for database operations
        result = await session.execute(select(Event))
        await session.commit()
```

---

### `models/` Directory

**Purpose:** SQLAlchemy ORM model definitions.

**Models:**

#### `tenants.py` - Multi-tenant organizations
```python
class Tenant(BaseModel):
    name: Mapped[str]
    is_active: Mapped[bool]
    settings: Mapped[dict]
```

#### `workflows.py` - Workflow registry
```python
class Workflow(BaseModel, TenantMixin):
    name: Mapped[str]
    description: Mapped[str]
    is_active: Mapped[bool]
```

#### `vendors.py` - External service configurations
```python
class Vendor(BaseModel):
    name: Mapped[str]
    circuit_breaker_state: Mapped[str]
    circuit_breaker_failure_count: Mapped[int]
    rate_limit_per_minute: Mapped[int]
```

#### `events.py` - Immutable event log
```python
class Event(BaseModel, TenantMixin, CorrelationMixin):
    workflow_id: Mapped[UUID]
    event_type: Mapped[str]
    payload: Mapped[dict]
    idempotency_key: Mapped[str]  # Unique constraint
    occurred_at: Mapped[datetime]
    # NEVER UPDATED - append-only table
```

#### `incidents.py` - Failure tracking
```python
class Incident(BaseModel, TenantMixin, CorrelationMixin):
    signature: Mapped[str]  # Error fingerprint
    title: Mapped[str]
    status: Mapped[str]  # NEW, ANALYZING, ACTIONED, RESOLVED, IGNORED
    severity: Mapped[str]
    event_count: Mapped[int]
    first_seen_at: Mapped[datetime]
    last_seen_at: Mapped[datetime]
```

#### `decisions.py` - AI decision audit trail
```python
class Decision(BaseModel):
    incident_id: Mapped[UUID]
    decision_type: Mapped[str]
    reasoning: Mapped[str]
    confidence_score: Mapped[float]
    ai_model: Mapped[str]
    # Immutable - audit trail
```

#### `actions.py` - Remediation actions
```python
class Action(BaseModel):
    incident_id: Mapped[UUID]
    action_type: Mapped[str]  # retry, escalate, manual
    status: Mapped[str]  # PENDING, IN_PROGRESS, SUCCEEDED, FAILED
    parameters: Mapped[dict]
    result: Mapped[Optional[dict]]
    is_reversible: Mapped[bool]
```

#### `kill_switches.py` - Emergency controls
```python
class KillSwitch(BaseModel, TenantMixin):
    workflow_id: Mapped[Optional[UUID]]  # Null = tenant-wide
    is_active: Mapped[bool]
    reason: Mapped[str]
    activated_by: Mapped[str]
```

---

### `repositories/` Directory

**Purpose:** Data access layer implementing repository pattern.

**Base Repository:**
```python
# repositories/base.py
class BaseRepository[T]:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by ID."""
        pass

    async def create(self, data: dict) -> T:
        """Create new entity."""
        pass

    async def update(self, entity: T) -> T:
        """Update existing entity."""
        pass

    async def delete(self, id: UUID) -> None:
        """Delete entity (soft delete if supported)."""
        pass
```

**Repositories:**
- `events.py` - EventRepository
- `incidents.py` - IncidentRepository
- `actions.py` - ActionRepository
- `decisions.py` - DecisionRepository
- `tenants.py` - TenantRepository
- `workflows.py` - WorkflowRepository
- `vendors.py` - VendorRepository

**Example Repository:**
```python
# repositories/events.py
class EventRepository(BaseRepository[Event]):
    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
        tenant_id: UUID
    ) -> Optional[Event]:
        """Find event by idempotency key (tenant-scoped)."""
        result = await self.session.execute(
            select(Event)
            .where(Event.idempotency_key == idempotency_key)
            .where(Event.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_recent_events(
        self,
        tenant_id: UUID,
        workflow_id: UUID,
        hours: int = 24
    ) -> List[Event]:
        """Get events from last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        result = await self.session.execute(
            select(Event)
            .where(Event.tenant_id == tenant_id)
            .where(Event.workflow_id == workflow_id)
            .where(Event.occurred_at >= cutoff)
            .order_by(Event.occurred_at.desc())
        )
        return list(result.scalars().all())
```

---

## Design Principles

### 1. Repository Pattern
**Why:** Decouples business logic from database implementation.

**Benefits:**
- Testable (mock repositories in unit tests)
- Reusable (common queries defined once)
- Type-safe (repositories return typed models)

**Rule:** Services NEVER use raw SQLAlchemy queries. Always go through repositories.

### 2. Tenant Isolation
**Implementation:** Every query filters by `tenant_id`.

**Enforcement:**
```python
# Repositories automatically filter by tenant
async def get_by_id(self, id: UUID, tenant_id: UUID) -> Optional[Event]:
    result = await self.session.execute(
        select(Event)
        .where(Event.id == id)
        .where(Event.tenant_id == tenant_id)  # Always filter!
    )
    return result.scalar_one_or_none()
```

### 3. Immutable Tables
**Events and Decisions are append-only:**
- Events: NEVER updated, only inserted
- Decisions: NEVER updated, creates audit trail

**Mutable tables:**
- Incidents: Status and event_count updated
- Actions: Status updated during execution
- Vendors: Circuit breaker state changes

### 4. Transaction Control
**Repositories don't commit** - Services control transaction boundaries.

```python
# Good - Service controls commit
async def ingest_event(event_data: dict):
    async with get_session() as session:
        event_repo = EventRepository(session)
        incident_repo = IncidentRepository(session)

        event = await event_repo.create(event_data)
        incident = await incident_repo.create_from_event(event)

        await session.commit()  # Single commit for both

# Bad - Repository commits (violates transaction control)
async def create(self, data: dict):
    entity = Entity(**data)
    self.session.add(entity)
    await self.session.commit()  # DON'T DO THIS!
```

---

## Database Indexing Strategy

### Primary Indexes
- All tables: `id` (UUID primary key)
- Events: `idempotency_key` (unique)
- Workflows: `name` per tenant

### Composite Indexes
```sql
-- Common query patterns
CREATE INDEX ix_events_tenant_workflow ON events(tenant_id, workflow_id);
CREATE INDEX ix_events_tenant_occurred ON events(tenant_id, occurred_at);
CREATE INDEX ix_incidents_tenant_status ON incidents(tenant_id, status);
CREATE INDEX ix_actions_incident_status ON actions(incident_id, status);
```

### Query Optimization
```python
# Good - Uses index
events = await session.execute(
    select(Event)
    .where(Event.tenant_id == tenant_id)
    .where(Event.occurred_at >= start_date)
    .order_by(Event.occurred_at.desc())
)

# Bad - Full table scan
events = await session.execute(
    select(Event).where(Event.payload["error_code"] == "timeout")
)
```

---

## Migrations (Alembic)

### Create Migration
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add kill_switches table"

# Review generated migration file
# Edit if needed (Alembic doesn't catch everything)
```

### Apply Migration
```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Check current version
alembic current
```

### Migration Best Practices
1. **Review auto-generated migrations** - Alembic misses some changes
2. **Test migrations** - Apply to test database first
3. **Make migrations reversible** - Implement `downgrade()`
4. **Never edit applied migrations** - Create new migration instead
5. **Document breaking changes** - Add comments in migration file

---

## Testing

### Unit Tests (Mock Database)
```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_event_repository_get_by_id():
    # Mock session
    session = AsyncMock(spec=AsyncSession)

    # Mock query result
    mock_event = Event(id=UUID(...), event_type="test.event")
    session.execute.return_value.scalar_one_or_none.return_value = mock_event

    # Test repository
    repo = EventRepository(session)
    event = await repo.get_by_id(mock_event.id, tenant_id)

    assert event.event_type == "test.event"
```

### Integration Tests (Real Database)
```python
@pytest.mark.asyncio
async def test_event_create_persists_to_database(db_session):
    repo = EventRepository(db_session)

    event = await repo.create({
        "tenant_id": test_tenant_id,
        "workflow_id": test_workflow_id,
        "event_type": "payment.failed",
        "payload": {},
        "idempotency_key": "test-001",
        "occurred_at": datetime.utcnow()
    })

    await db_session.commit()

    # Verify persisted
    retrieved = await repo.get_by_id(event.id, test_tenant_id)
    assert retrieved is not None
    assert retrieved.event_type == "payment.failed"
```

---

## Common Patterns

### Pagination
```python
async def get_incidents_paginated(
    self,
    tenant_id: UUID,
    page: int = 1,
    page_size: int = 20
) -> List[Incident]:
    offset = (page - 1) * page_size
    result = await self.session.execute(
        select(Incident)
        .where(Incident.tenant_id == tenant_id)
        .offset(offset)
        .limit(page_size)
    )
    return list(result.scalars().all())
```

### Filtering
```python
async def get_incidents_by_status(
    self,
    tenant_id: UUID,
    status: IncidentStatus
) -> List[Incident]:
    result = await self.session.execute(
        select(Incident)
        .where(Incident.tenant_id == tenant_id)
        .where(Incident.status == status.value)
        .order_by(Incident.created_at.desc())
    )
    return list(result.scalars().all())
```

### Counting
```python
async def count_events(self, tenant_id: UUID, workflow_id: UUID) -> int:
    result = await self.session.execute(
        select(func.count(Event.id))
        .where(Event.tenant_id == tenant_id)
        .where(Event.workflow_id == workflow_id)
    )
    return result.scalar_one()
```

---

## Troubleshooting

### Issue: Connection Pool Exhausted
**Symptom:** `TimeoutError: QueuePool limit exceeded`
**Solution:**
- Increase `DATABASE_POOL_SIZE` in config
- Ensure sessions are properly closed (use context managers)
- Check for connection leaks

### Issue: Slow Queries
**Symptom:** High latency on database operations
**Solution:**
- Check query execution plan: `EXPLAIN ANALYZE <query>`
- Add missing indexes
- Avoid N+1 queries (use eager loading)

### Issue: Migration Conflicts
**Symptom:** `alembic.util.exc.CommandError: Target database is not up to date`
**Solution:**
```bash
# Check current version
alembic current

# Review pending migrations
alembic history

# Apply migrations
alembic upgrade head
```

---

## See Also

- [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) - Database schema design
- [TESTING.md](../../../docs/TESTING.md) - Database testing strategies
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
