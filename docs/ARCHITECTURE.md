# AWFDRS Architecture Documentation

## System Overview

**AWFDRS (Autonomous Workflow Failure Detection & Recovery System)** is an enterprise-grade event-driven system designed to automatically detect, analyze, and remediate workflow failures across distributed systems.

### Core Capabilities

- **Real-time Event Ingestion** - High-throughput event processing with idempotency guarantees
- **Intelligent Failure Detection** - Pattern-based error detection and incident correlation
- **AI-Assisted Analysis** - Mock AI integration for error classification and root cause analysis (zero API costs)
- **Automated Remediation** - Configurable retry strategies and escalation workflows
- **Safety Controls** - Circuit breakers, rate limiting, and kill switches
- **Multi-Tenant Isolation** - Complete tenant data isolation with per-tenant quotas

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         External Systems / Clients                       │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          API Layer (FastAPI)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │   Events     │  │  Incidents   │  │   Actions    │  │   Health     ││
│  │  /api/v1/*   │  │  /api/v1/*   │  │  /api/v1/*   │  │  /api/v1/*   ││
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘│
│         │                  │                  │                  │       │
│         └──────────────────┴──────────────────┴──────────────────┘       │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   Middleware    │   │   Middleware    │   │  Exception      │
│  Correlation ID │   │  Request Logger │   │  Handlers       │
└─────────────────┘   └─────────────────┘   └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Service Layer                                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │ Ingestion Service│  │ Incident Manager │  │ Action Executor  │      │
│  │ - Validation     │  │ - Correlation    │  │ - Retry Coord    │      │
│  │ - Idempotency    │  │ - Lifecycle Mgmt │  │ - Escalation     │      │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘      │
└───────────┼────────────────────┼────────────────────┼─────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Safety Layer                                     │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐            │
│  │ Rate Limiter   │  │ Circuit Breaker│  │  Safety Limits │            │
│  │ (Redis-backed) │  │ (Per Vendor)   │  │  Enforcer      │            │
│  └────────────────┘  └────────────────┘  └────────────────┘            │
└─────────────────────────────────────────────────────────────────────────┘
            │                    │                    │
            └────────────────────┼────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Analysis & Intelligence                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │ Incident Detector│  │  Signature Gen   │  │  Correlator      │      │
│  │ - Pattern Match  │  │  - Error Grouping│  │  - Event Linking │      │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘      │
│           │                     │                     │                 │
│  ┌────────┴─────────────────────┴─────────────────────┴─────────┐      │
│  │                   AI Decision Service (Mock)                  │      │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │      │
│  │  │ AI Detector  │  │  AI RCA      │  │  Similarity  │        │      │
│  │  │ (Mock LLM)   │  │  (Mock LLM)  │  │  Search      │        │      │
│  │  └──────────────┘  └──────────────┘  └──────────────┘        │      │
│  └───────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
            │                    │                    │
            └────────────────────┼────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Data Layer                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  Repositories    │  │   Session Mgmt   │  │   Base Models    │      │
│  │  - Events        │  │   - Connection   │  │   - Mixins       │      │
│  │  - Incidents     │  │   - Pool         │  │   - Timestamps   │      │
│  │  - Actions       │  │   - Transaction  │  │   - Tenant Iso   │      │
│  │  - Decisions     │  └──────────────────┘  └──────────────────┘      │
│  │  - Workflows     │                                                   │
│  │  - Vendors       │                                                   │
│  │  - Tenants       │                                                   │
│  └────────┬─────────┘                                                   │
└───────────┼─────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  PostgreSQL      │  │      Redis       │  │   Config Files   │      │
│  │  - Events        │  │  - Rate Limits   │  │  - error_codes   │      │
│  │  - Incidents     │  │  - Circuit State │  │  - retry_policy  │      │
│  │  - Actions       │  │  - Session Cache │  │  - vendor_config │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Responsibilities

### 1. API Layer (`src/awfdrs/ingestion/api/`, `src/awfdrs/analysis/api/`, `src/awfdrs/actions/api/`)

**Purpose:** HTTP request handling, routing, validation, and response formatting.

**Responsibilities:**
- FastAPI route handlers for all REST endpoints
- Request/response schema validation using Pydantic
- OpenAPI documentation generation
- HTTP error handling and status code mapping
- Dependency injection for services and database sessions

**Key Design Decisions:**
- Versioned APIs (`/api/v1/`) for backward compatibility
- Separate routers per domain (events, incidents, actions)
- Comprehensive docstrings for OpenAPI documentation
- Structured error responses with correlation IDs

### 2. Service Layer (`src/awfdrs/ingestion/service.py`, `src/awfdrs/analysis/incident_manager.py`, etc.)

**Purpose:** Business logic orchestration and workflow coordination.

**Responsibilities:**
- Event validation and ingestion workflow
- Incident lifecycle management (detect → analyze → remediate)
- Action execution coordination
- Cross-service orchestration

**Key Design Decisions:**
- Services are stateless and instantiated per request
- Database session and correlation ID injected via constructor
- All business logic isolated from HTTP layer
- Services use repositories for data access (never direct DB calls)

### 3. Safety Layer (`src/awfdrs/safety/`)

**Purpose:** Protective controls to prevent cascading failures and enforce operational limits.

**Components:**
- **Rules Engine** (`rules_engine.py`) - Evaluates error codes against YAML configurations
- **Circuit Breaker** (`circuit_breaker.py`) - Per-vendor failure protection with state machine
- **Rate Limiter** (`rate_limiter.py`) - Redis-backed request throttling
- **Safety Limits** (`limits.py`) - Enforces maximum retry attempts per workflow/vendor

**Key Design Decisions:**
- Redis for distributed rate limiting and circuit breaker state
- YAML configuration for easy operational updates without code changes
- Separate limits per tenant for isolation
- Circuit breaker states: CLOSED → OPEN → HALF_OPEN with configurable timeouts

### 4. Analysis & Intelligence (`src/awfdrs/analysis/`, `src/awfdrs/ai/`)

**Purpose:** Failure pattern detection, incident correlation, and AI-assisted decision making.

**Components:**
- **Signature Generator** (`signature.py`) - Creates unique fingerprints for error patterns
- **Incident Detector** (`incident_detector.py`) - Identifies failures from events
- **Correlator** (`correlator.py`) - Links related events to incidents
- **AI Decision Service** (`decision_service.py`) - Orchestrates mock AI analysis
- **Mock AI Agents** (`ai/agents/`) - Deterministic AI responses (zero API costs)

**Key Design Decisions:**
- Error signatures use normalized error codes + workflow ID for grouping
- All AI integrations are mocked to prevent API costs
- AI mode validation enforces mock-only operation
- Similarity search returns deterministic mock results

### 5. Data Layer (`src/awfdrs/db/`)

**Purpose:** Data persistence, retrieval, and transaction management.

**Components:**
- **Models** (`models/`) - SQLAlchemy ORM models with full type hints
- **Repositories** (`repositories/`) - Data access abstraction layer
- **Session Management** (`session.py`) - Database connection and transaction handling
- **Base Classes** (`base.py`) - Reusable mixins (TenantMixin, CorrelationMixin, timestamps)

**Key Design Decisions:**
- Repository pattern isolates SQL from business logic
- All models include `created_at` and `updated_at` timestamps
- Tenant ID in all queries for multi-tenant isolation
- Immutable event storage (append-only, never updated)
- Composite indexes for common query patterns

### 6. Core Utilities (`src/awfdrs/core/`)

**Purpose:** Shared infrastructure and cross-cutting concerns.

**Components:**
- **Configuration** (`../config.py`) - Pydantic-based type-safe configuration
- **Logging** (`logging.py`) - Structured JSON logging with correlation IDs
- **Tracing** (`tracing.py`) - Request correlation and middleware
- **Exceptions** (`exceptions.py`) - Custom exception hierarchy
- **Enums** (`enums.py`) - Shared enumerations (status codes, event types)
- **Schemas** (`schemas.py`) - Shared Pydantic schemas

**Key Design Decisions:**
- Centralized configuration with environment variable validation
- Structured logging for machine-readable observability
- Correlation IDs on every request for distributed tracing
- Custom exception types map to HTTP status codes

---

## Data Flow

### Event Ingestion Flow

```
1. POST /api/v1/events
   ↓
2. Request validation (Pydantic schema)
   ↓
3. Correlation ID injection (middleware)
   ↓
4. IngestionService.ingest_event()
   ↓
5. Idempotency check (duplicate detection)
   ↓
6. Tenant validation (active tenant?)
   ↓
7. Workflow validation (exists? kill-switched?)
   ↓
8. Rate limiting check (Safety Layer)
   ↓
9. Event storage (immutable append)
   ↓
10. Incident detection trigger
   ↓
11. Return EventResponse with event_id
```

### Incident Detection & Remediation Flow

```
1. Event stored in database
   ↓
2. IncidentDetector analyzes event
   ↓
3. Error signature generated
   ↓
4. Check for existing incident with same signature
   ├─ Exists: Link event to existing incident
   └─ New: Create new incident
   ↓
5. Correlator groups related events
   ↓
6. AI Decision Service invoked (mock)
   ├─ AI Detector classifies error
   ├─ AI RCA analyzes root cause
   └─ Similarity search finds similar past incidents
   ↓
7. Decision record created (audit trail)
   ↓
8. Action determination
   ├─ Retry eligible? → Schedule retry
   ├─ Escalation needed? → Create escalation
   └─ No action → Monitor
   ↓
9. Action execution
   ↓
10. State machine tracks action lifecycle
```

---

## Database Schema

### Core Tables

#### `tenants`
- Multi-tenant organization entities
- Attributes: `id`, `name`, `is_active`, `settings`

#### `workflows`
- Workflow registry per tenant
- Attributes: `id`, `tenant_id`, `name`, `description`, `is_active`

#### `vendors`
- External vendor/service configurations
- Attributes: `id`, `name`, `circuit_breaker_state`, `rate_limit_settings`

#### `events` (Immutable)
- Append-only event log
- Attributes: `id`, `tenant_id`, `workflow_id`, `event_type`, `payload`, `idempotency_key`, `occurred_at`, `correlation_id`
- **Never updated, only inserted**

#### `incidents`
- Failure tracking and lifecycle management
- Attributes: `id`, `tenant_id`, `signature`, `title`, `status`, `severity`, `first_seen_at`, `last_seen_at`, `event_count`

#### `decisions`
- AI decision audit trail
- Attributes: `id`, `incident_id`, `decision_type`, `reasoning`, `confidence_score`, `ai_model`

#### `actions`
- Remediation action execution log
- Attributes: `id`, `incident_id`, `action_type`, `status`, `parameters`, `result`, `is_reversible`

#### `kill_switches`
- Emergency workflow controls
- Attributes: `id`, `tenant_id`, `workflow_id`, `is_active`, `reason`

### Indexes

- **Tenant isolation:** All queries filtered by `tenant_id`
- **Time-range queries:** Indexes on `occurred_at`, `created_at`
- **Lookup optimization:** Indexes on `idempotency_key`, `workflow_id`, `event_type`
- **Composite indexes:** `(tenant_id, workflow_id)`, `(tenant_id, occurred_at)`

---

## Security Architecture

### Authentication & Authorization
- JWT-based authentication (configured, not implemented in phase 1-7)
- Tenant-scoped access control
- Secrets management via environment variables

### Data Protection
- Tenant data isolation enforced at database query level
- No cross-tenant data leakage
- Immutable event log for audit compliance
- Correlation IDs for forensic analysis

### Input Validation
- Pydantic schema validation on all API inputs
- Type checking with mypy
- SQL injection prevention via SQLAlchemy ORM
- Idempotency keys prevent duplicate processing

### Operational Security
- **Rate limiting** prevents abuse and DoS
- **Circuit breakers** protect vendor relationships
- **Kill switches** enable emergency workflow disabling
- **Retry limits** prevent infinite retry loops
- **Log sanitization** prevents credential leakage (TODO: Implement log scrubbing)

---

## Scalability & Performance

### Horizontal Scaling
- **Stateless services** - Any instance can handle any request
- **Database connection pooling** - Configurable pool size
- **Redis for distributed state** - Rate limits and circuit breaker state shared across instances

### Performance Optimizations
- **Composite database indexes** for common query patterns
- **Pagination** on list endpoints
- **Async I/O** throughout (FastAPI + SQLAlchemy async)
- **Lazy loading** of related entities

### Bottleneck Mitigation
- **Redis rate limiting** prevents database overload
- **Circuit breakers** shed load during vendor outages
- **Event batching** (future enhancement)
- **Background job processing** (future enhancement - Phase 8)

---

## Observability

### Logging
- **Structured JSON logs** for machine parsing
- **Correlation IDs** on every request
- **Tenant IDs** in all logs for filtering
- **Log levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL

### Tracing
- **Correlation ID propagation** across service boundaries
- **Request logging middleware** captures all HTTP traffic
- **Timing information** (future: add request duration)

### Metrics (Placeholders - See METRICS.md)
- Request counts by endpoint
- Error rates by type
- Incident detection latency
- Action success/failure rates
- Circuit breaker state changes

---

## Configuration Management

### Environment-Based Config
- **Pydantic Settings** for type-safe configuration
- **.env file** for local development
- **Environment variables** for production deployment
- **Validation on startup** with clear error messages

### YAML Configuration Files
- **error_codes.yaml** - Error definitions and severity
- **retry_policies.yaml** - Retry strategy configurations
- **vendor_config.yaml** - Vendor-specific settings (circuit breaker, rate limits)

**Rationale:** YAML allows operational teams to update configurations without code changes.

---

## Testing Strategy

See [TESTING.md](./TESTING.md) for comprehensive testing documentation.

**Summary:**
- **Unit tests** for business logic
- **Integration tests** for database interactions
- **Mock backends** for all external dependencies (AI, vendors)
- **Fixture-based** test data
- **Coverage enforcement** via pytest-cov

---

## Deployment Architecture

### Local Development
```
Docker Compose:
  - PostgreSQL (port 5432)
  - Redis (port 6379)

Local Python:
  - FastAPI app (uvicorn, port 8000)
```

### Production (Recommended)
```
Kubernetes:
  - API Pods (horizontal autoscaling)
  - PostgreSQL (managed service: AWS RDS, Azure Database, GCP Cloud SQL)
  - Redis (managed service: AWS ElastiCache, Azure Cache, GCP Memorystore)
  - Background Workers (future: Celery or similar)

Ingress:
  - Load Balancer → API Pods
  - TLS termination
  - Rate limiting at ingress layer
```

---

## Future Enhancements

### Phase 8: Background Workers
- **Event processor worker** - Async job queue for heavy processing
- **Retry scheduler** - Delayed job execution with cron-like scheduling
- **Metrics collector** - Time-series aggregation

### Phase 9: Enhanced Observability
- **Prometheus metrics export** - /metrics endpoint
- **Grafana dashboards** - Pre-built dashboards for SRE teams
- **Distributed tracing** - OpenTelemetry integration
- **Alerting** - Integration with PagerDuty, Opsgenie

### Phase 10: Real AI Integration (Optional)
- **Fine-tuned models** for domain-specific error classification
- **Pattern learning** from historical resolution data
- **Anomaly detection** for novel failure modes
- **Cost controls** - Token budgets and caching

---

## Technology Stack

### Core Framework
- **Python 3.11+** - Async/await, type hints
- **FastAPI** - High-performance async web framework
- **Pydantic** - Data validation and settings management
- **SQLAlchemy 2.0** - Async ORM with type hints
- **Alembic** - Database migrations

### Data Stores
- **PostgreSQL** - Primary relational database
- **Redis** - Distributed caching and rate limiting

### Development Tools
- **pytest** - Testing framework
- **Black** - Code formatting
- **mypy** - Static type checking
- **Ruff** - Fast Python linter
- **pre-commit** - Git hooks

### Mock Integrations
- **OpenAI API** - Mocked for zero-cost development
- **Pinecone** - Mocked vector database

---

## Directory Layout Explanation

```
AWFDRS/
├── src/awfdrs/           # Application source code
│   ├── core/             # Shared utilities (logging, config, exceptions)
│   ├── db/               # Database layer (models, repositories, session)
│   ├── ingestion/        # Event ingestion service + API
│   ├── analysis/         # Incident management + API
│   ├── actions/          # Action coordination + API
│   ├── ai/               # AI analysis plane (mock implementations)
│   ├── safety/           # Safety controls (rate limit, circuit breaker, rules)
│   ├── jobs/             # Background job definitions (future)
│   ├── config.py         # Centralized configuration
│   ├── dependencies.py   # FastAPI dependency injection
│   └── main.py           # Application entry point
├── tests/                # Automated tests
│   ├── unit/             # Unit tests (isolated, fast)
│   ├── integration/      # Integration tests (database, external services)
│   ├── mocks/            # Mock implementations (AI, vendors)
│   └── fixtures/         # Test data fixtures
├── alembic/              # Database migrations
├── config/               # YAML configuration files
│   └── rules/            # Business rules (error codes, retry policies, vendors)
├── scripts/              # Operational scripts (DB init, seed data)
├── docs/                 # Architecture and design documentation
└── [config files]        # pyproject.toml, docker-compose.yml, etc.
```

**Rationale:** Clear separation between API handlers, business logic, data access, and infrastructure.

---

## Design Principles

1. **Separation of Concerns** - API, service, data layers cleanly separated
2. **Dependency Inversion** - Services depend on repository interfaces, not concrete implementations
3. **Immutability** - Events and decisions never modified after creation
4. **Fail-Safe Defaults** - Rate limits, circuit breakers prevent cascading failures
5. **Type Safety** - Comprehensive type hints + mypy enforcement
6. **Testability** - Mock all external dependencies
7. **Observability First** - Correlation IDs, structured logs, audit trails
8. **Configuration as Code** - YAML for operational parameters
9. **Multi-Tenancy** - Tenant isolation at every layer

---

## Additional Resources

- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Testing Strategy:** [TESTING.md](./TESTING.md)
- **Metrics & SLA:** [METRICS.md](./METRICS.md)
- **Coding Conventions:** [CONVENTIONS.md](./CONVENTIONS.md)
- **Setup Guide:** [../SETUP.md](../SETUP.md)
