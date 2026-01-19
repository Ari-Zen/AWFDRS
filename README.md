# AWFDRS - Autonomous Workflow Failure Detection & Recovery System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.127.0-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**An enterprise-grade, AI-powered system for automatically detecting, analyzing, and remediating workflow failures in distributed systems.**

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Contributing](#contributing)
- [Documentation](#documentation)
- [License](#license)

---

## Overview

AWFDRS is an event-driven platform that automatically detects workflow failures, analyzes root causes, and executes remediation actions. It provides:

- **Real-time failure detection** from ingested events
- **Intelligent incident correlation** grouping similar errors
- **AI-assisted analysis** for error classification and root cause analysis (mock implementation)
- **Automated remediation** with smart retry logic and escalation
- **Safety controls** including circuit breakers, rate limiting, and kill switches
- **Multi-tenant architecture** with complete tenant isolation

### Design Philosophy

- **Safety first** - Circuit breakers and rate limiting prevent cascading failures
- **Zero AI costs** - Mock AI implementation for cost-free development
- **Production-ready** - Enterprise-grade observability, security, and reliability
- **Maintainable** - Clean architecture with comprehensive documentation

---

## Key Features

### 🚨 Failure Detection
- Pattern-based error detection from workflow events
- Error signature generation for grouping similar failures
- Automatic incident creation and correlation
- Configurable severity levels (LOW, MEDIUM, HIGH, CRITICAL)

### 🤖 AI-Assisted Analysis (Mock)
- Error classification and categorization
- Root cause analysis with reasoning
- Historical incident similarity search
- Decision audit trail for transparency
- **Zero API costs** - 100% mock implementation

### 🔄 Automated Remediation
- Smart retry coordination with exponential backoff
- Jitter to prevent thundering herd
- Escalation workflows (notifications, ticketing)
- Reversible actions for safety
- Configurable retry policies via YAML

### 🛡️ Safety Controls
- **Circuit breakers** - Per-vendor failure protection
- **Rate limiting** - Redis-backed distributed throttling
- **Kill switches** - Emergency workflow disabling
- **Retry limits** - Prevent infinite loops
- All limits configurable without code changes

### 📊 Observability
- Structured JSON logging with correlation IDs
- Complete audit trail (immutable events, decisions, actions)
- Prometheus metrics (ready to implement)
- Request tracing across services
- Per-tenant filtering and isolation

### 🏢 Enterprise Features
- Multi-tenant data isolation
- Type-safe configuration (Pydantic)
- Database migrations (Alembic)
- Async/await throughout for high concurrency
- Comprehensive test coverage

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (via Docker)
- Redis 7+ (via Docker)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd AWFDRS

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env

# Review and adjust .env as needed
# Note: AI_MODE must remain "mock"
```

### Start Infrastructure

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Initialize Database

```bash
# Create initial migration
alembic upgrade head

# Seed sample data (optional)
python scripts/seed_data.py
```

### Run Application

```bash
# Start FastAPI application
uvicorn src.awfdrs.main:app --reload --host 0.0.0.0 --port 8000
```

**Application available at:**
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                      │
│  Events │ Incidents │ Actions │ Health                       │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Service Layer                              │
│  Ingestion │ Incident Manager │ Action Executor             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Safety Layer                               │
│  Rate Limiter │ Circuit Breaker │ Rules Engine │ Limits     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Analysis & AI                              │
│  Incident Detector │ Correlator │ AI Agents (Mock)          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Data Layer                                 │
│  Repositories │ Models │ Session Management                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│              Infrastructure                                  │
│  PostgreSQL │ Redis │ Config Files                          │
└─────────────────────────────────────────────────────────────┘
```

**See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.**

---

## Project Structure

```
AWFDRS/
├── src/awfdrs/              # Application source code
│   ├── core/                # Shared utilities (logging, exceptions, config)
│   ├── db/                  # Database layer (models, repositories)
│   ├── ingestion/           # Event ingestion service + API
│   ├── analysis/            # Incident detection & management
│   ├── actions/             # Action coordination & retry logic
│   ├── ai/                  # AI analysis plane (mock)
│   ├── safety/              # Safety controls (circuit breaker, rate limit)
│   ├── config.py            # Centralized configuration
│   ├── dependencies.py      # FastAPI dependency injection
│   └── main.py              # Application entry point
├── tests/                   # Automated tests
│   ├── unit/                # Unit tests (fast, isolated)
│   ├── integration/         # Integration tests (DB, Redis)
│   ├── mocks/               # Mock implementations (AI, vendors)
│   └── fixtures/            # Test data fixtures
├── alembic/                 # Database migrations
├── config/                  # YAML configuration files
│   └── rules/               # Business rules (errors, retries, vendors)
├── scripts/                 # Operational scripts (DB init, seed data)
├── docs/                    # Architecture & design documentation
│   ├── ARCHITECTURE.md      # System design
│   ├── TESTING.md           # Testing strategy
│   ├── MIGRATION.md         # Project structure decisions
│   ├── METRICS.md           # Observability & SLAs
│   └── CONVENTIONS.md       # Coding standards
├── docker-compose.yml       # Docker services (PostgreSQL, Redis)
├── pyproject.toml           # Project configuration
├── requirements.txt         # Runtime dependencies
└── requirements-dev.txt     # Development dependencies
```

---

## API Documentation

### Base URL
`http://localhost:8000/api/v1`

### Health Checks

#### GET /health
Basic health check.

**Response:**
```json
{
  "status": "ok"
}
```

#### GET /health/ready
Readiness check (verifies database and Redis connectivity).

**Response (200 OK):**
```json
{
  "status": "ready",
  "database": "ok",
  "redis": "ok"
}
```

### Event Ingestion

#### POST /events
Submit workflow event for processing.

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

### Incident Management

#### GET /incidents
List incidents with filtering and pagination.

**Query Parameters:**
- `tenant_id` (required) - Tenant UUID
- `status` (optional) - Filter by status
- `severity` (optional) - Filter by severity
- `page` (default: 1)
- `page_size` (default: 20)

#### GET /incidents/{id}
Get incident details.

#### GET /incidents/{id}/events
Get events correlated to incident.

#### PATCH /incidents/{id}/status
Update incident status.

#### POST /incidents/{id}/ignore
Mark incident as ignored.

### Action Management

#### GET /actions
List actions with filtering.

#### GET /actions/{id}
Get action details.

#### POST /actions/{id}/reverse
Reverse a reversible action.

#### GET /incidents/{id}/actions
Get all actions for an incident.

**Interactive API documentation available at:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Development

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black src/ tests/

# Run linting
ruff check src/ tests/

# Run type checking
mypy src/

# Run security scanning
bandit -r src/
```

### Code Quality Tools

- **Black** - Code formatting (line length: 100)
- **Ruff** - Fast Python linter
- **mypy** - Static type checking
- **Bandit** - Security vulnerability scanning
- **pre-commit** - Git hooks for automated checks

### Coding Standards

See [docs/CONVENTIONS.md](docs/CONVENTIONS.md) for comprehensive coding standards.

**Key conventions:**
- Type hints on all functions
- Google-style docstrings
- snake_case for functions/variables
- PascalCase for classes
- Repository pattern for data access
- Async/await for I/O operations

---

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/awfdrs --cov-report=html

# Run specific test category
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only

# Run specific test file
pytest tests/unit/test_signature.py

# Run with verbose output
pytest -v
```

### Test Coverage

**Coverage targets:**
- Overall: 85% minimum
- Core business logic: 95% minimum
- API handlers: 90% minimum
- Database repositories: 90% minimum

**View coverage report:**
```bash
pytest --cov=src/awfdrs --cov-report=html
open htmlcov/index.html  # Or open manually in browser
```

**See [docs/TESTING.md](docs/TESTING.md) for comprehensive testing documentation.**

---

## Deployment

### Production Checklist

- [ ] Update `.env` with production values
- [ ] Change `JWT_SECRET_KEY` to secure random value
- [ ] Configure `CORS_ORIGINS` for production domains
- [ ] Set up managed PostgreSQL (AWS RDS, Azure Database, GCP Cloud SQL)
- [ ] Set up managed Redis (AWS ElastiCache, Azure Cache, GCP Memorystore)
- [ ] Configure log aggregation (ELK, Splunk, Datadog)
- [ ] Set up monitoring and alerting (Prometheus, Grafana)
- [ ] Enable HTTPS/TLS
- [ ] Configure backup and disaster recovery
- [ ] Review and adjust rate limits
- [ ] Enable security headers

### Docker Deployment

```bash
# Build Docker image
docker build -t awfdrs:latest .

# Run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=awfdrs

# View logs
kubectl logs -f deployment/awfdrs
```

---

## Configuration

### Environment Variables

**Required:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

**Optional:**
- `LOG_LEVEL` - Logging level (default: INFO)
- `DATABASE_POOL_SIZE` - Connection pool size (default: 20)
- `MAX_RETRIES_PER_WORKFLOW` - Maximum retries (default: 5)
- `CIRCUIT_BREAKER_THRESHOLD` - Failure threshold (default: 10)
- `ENABLE_AI_DETECTION` - Enable AI features (default: false)

### Configuration Files

**YAML configurations in `config/rules/`:**

- `error_codes.yaml` - Error definitions with severity
- `retry_policies.yaml` - Retry strategy configurations
- `vendor_config.yaml` - Per-vendor settings (circuit breaker, rate limits)

**Example error code configuration:**
```yaml
error_codes:
  payment_timeout:
    severity: high
    retry_policy: exponential_backoff
    description: "Payment gateway timeout"
```

---

## Monitoring

### Key Metrics

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `events_ingested_total` - Events ingested
- `incidents_detected_total` - Incidents detected
- `actions_executed_total` - Actions executed
- `circuit_breaker_state` - Circuit breaker states
- `rate_limiter_rejections_total` - Rate limit rejections

### Logging

**Structured JSON logs:**
```json
{
  "timestamp": "2026-01-19T10:00:00.123Z",
  "level": "INFO",
  "logger": "src.awfdrs.ingestion.service",
  "message": "Event ingested",
  "correlation_id": "req-abc-123",
  "tenant_id": "tenant-001",
  "event_id": "evt-456",
  "duration_ms": 45
}
```

**See [docs/METRICS.md](docs/METRICS.md) for comprehensive observability documentation.**

---

## Contributing

### Development Workflow

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes following [coding conventions](docs/CONVENTIONS.md)
3. Add tests for new functionality
4. Run quality checks: `black src/ tests/ && ruff check && mypy src/ && pytest`
5. Commit changes: `git commit -m "feat: add my feature"`
6. Push branch: `git push origin feature/my-feature`
7. Create pull request

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Example:**
```
feat(ingestion): add idempotency key validation

Validates that idempotency keys are unique per tenant to prevent
duplicate event processing.

Closes #123
```

---

## Documentation

### Core Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design and component responsibilities
- [TESTING.md](docs/TESTING.md) - Testing strategy and coverage requirements
- [MIGRATION.md](docs/MIGRATION.md) - Project structure decisions and rationale
- [METRICS.md](docs/METRICS.md) - Observability, metrics, and SLA definitions
- [CONVENTIONS.md](docs/CONVENTIONS.md) - Coding standards and best practices

### Module Documentation

- [core/](src/awfdrs/core/README.md) - Shared utilities and cross-cutting concerns
- [db/](src/awfdrs/db/README.md) - Database layer (models, repositories)
- [ingestion/](src/awfdrs/ingestion/README.md) - Event ingestion service
- [analysis/](src/awfdrs/analysis/README.md) - Incident detection and management
- [actions/](src/awfdrs/actions/README.md) - Action coordination and retry logic
- [ai/](src/awfdrs/ai/README.md) - AI analysis plane (mock implementation)
- [safety/](src/awfdrs/safety/README.md) - Safety controls and protective mechanisms

---

## Technology Stack

### Core Framework
- **Python 3.11+** - Modern async/await, type hints
- **FastAPI** - High-performance async web framework
- **Pydantic** - Data validation and settings management
- **SQLAlchemy 2.0** - Async ORM with full type hints
- **Alembic** - Database schema migrations

### Data Stores
- **PostgreSQL 15+** - Primary relational database
- **Redis 7+** - Distributed caching and rate limiting

### Development Tools
- **pytest** - Testing framework with async support
- **Black** - Automatic code formatting
- **Ruff** - Fast Python linter
- **mypy** - Static type checking
- **Bandit** - Security vulnerability scanner

---

## Troubleshooting

### Common Issues

**Issue: Database connection failed**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart service
docker-compose restart postgres
```

**Issue: Redis connection refused**
```bash
# Test Redis connectivity
docker-compose exec redis redis-cli ping
# Should return: PONG

# Restart Redis
docker-compose restart redis
```

**Issue: Migration conflicts**
```bash
# Check current version
alembic current

# Reset database (CAUTION: destroys data)
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

**Issue: Tests failing**
```bash
# Clear pytest cache
pytest --cache-clear

# Run specific failing test with verbose output
pytest -vv tests/path/to/test.py::test_name
```

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Support

For issues, questions, or contributions:

1. **Documentation** - Check [docs/](docs/) directory
2. **API Docs** - http://localhost:8000/docs
3. **Issues** - GitHub Issues (if repository is hosted on GitHub)
4. **Discussions** - GitHub Discussions (if enabled)

---

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Database migrations with [Alembic](https://alembic.sqlalchemy.org/)
- Circuit breaker pattern from [Release It!](https://pragprog.com/titles/mnee2/) by Michael Nygard

---

**AWFDRS** - Keeping your workflows healthy, automatically.
