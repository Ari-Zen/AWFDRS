# AWFDRS Observability & Metrics

## Overview

This document defines the observability strategy, metrics, and SLA (Service Level Agreement) requirements for AWFDRS. It serves as a guide for implementing monitoring, alerting, and performance tracking.

---

## Observability Pillars

### 1. Metrics (Quantitative)
- Request counts, latencies, error rates
- Resource utilization (CPU, memory, connections)
- Business metrics (incidents detected, actions executed)

### 2. Logs (Qualitative)
- Structured JSON logs with correlation IDs
- Event-driven audit trail
- Error stack traces and context

### 3. Traces (Distributed)
- Request flow across services
- Latency breakdown by component
- Dependency mapping

---

## Key Performance Indicators (KPIs)

### Service Level Objectives (SLOs)

| Metric | Target | Measurement Period | Priority |
|--------|--------|-------------------|----------|
| **API Availability** | 99.9% | Monthly | P0 |
| **Event Ingestion Latency (P95)** | < 100ms | Hourly | P0 |
| **Event Ingestion Latency (P99)** | < 250ms | Hourly | P0 |
| **Incident Detection Latency** | < 5 seconds | Hourly | P1 |
| **Action Execution Latency** | < 10 seconds | Hourly | P1 |
| **Database Query Latency (P95)** | < 50ms | Hourly | P1 |
| **Error Rate** | < 1% | Hourly | P0 |

**SLA (Service Level Agreement):**
- **Uptime:** 99.9% monthly (43.8 minutes downtime allowed)
- **Data retention:** Events stored for 90 days minimum
- **Incident response:** P0 incidents acknowledged within 15 minutes

---

## Application Metrics

### 1. Request Metrics

#### HTTP Request Count
**Metric name:** `http_requests_total`
**Type:** Counter
**Labels:**
- `method` - HTTP method (GET, POST, etc.)
- `endpoint` - API endpoint path
- `status_code` - HTTP status code
- `tenant_id` - Tenant identifier

**Purpose:** Track API usage patterns and error rates per endpoint.

**Alerting:**
- Alert if 5xx errors > 1% of requests over 5 minutes
- Alert if 4xx errors > 10% of requests over 5 minutes

---

#### HTTP Request Duration
**Metric name:** `http_request_duration_seconds`
**Type:** Histogram
**Labels:**
- `method` - HTTP method
- `endpoint` - API endpoint
- `status_code` - HTTP status code

**Buckets:** 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0 seconds

**Purpose:** Measure API response time distribution.

**Alerting:**
- Alert if P95 latency > 250ms for 5 minutes
- Alert if P99 latency > 1s for 5 minutes

---

### 2. Business Metrics

#### Events Ingested
**Metric name:** `events_ingested_total`
**Type:** Counter
**Labels:**
- `tenant_id` - Tenant identifier
- `workflow_id` - Workflow identifier
- `event_type` - Event type (e.g., payment.failed)

**Purpose:** Track event volume per tenant and workflow.

**Alerting:**
- Alert if event ingestion drops to 0 for > 5 minutes (service down?)
- Alert if event volume increases 10x (potential attack or misconfiguration)

---

#### Events Rejected
**Metric name:** `events_rejected_total`
**Type:** Counter
**Labels:**
- `tenant_id` - Tenant identifier
- `workflow_id` - Workflow identifier
- `reason` - Rejection reason (validation_error, duplicate, tenant_inactive, etc.)

**Purpose:** Track validation failures and duplicate submissions.

**Alerting:**
- Alert if rejection rate > 10% for any tenant

---

#### Incidents Detected
**Metric name:** `incidents_detected_total`
**Type:** Counter
**Labels:**
- `tenant_id` - Tenant identifier
- `workflow_id` - Workflow identifier
- `severity` - Incident severity (low, medium, high, critical)

**Purpose:** Track failure detection rate.

**Alerting:**
- Alert if critical incidents > 5 per hour
- Alert if total incidents increase 5x compared to baseline

---

#### Incident Detection Latency
**Metric name:** `incident_detection_duration_seconds`
**Type:** Histogram
**Labels:**
- `tenant_id` - Tenant identifier
- `workflow_id` - Workflow identifier

**Buckets:** 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0 seconds

**Purpose:** Measure time from event ingestion to incident creation.

**Alerting:**
- Alert if P95 > 10 seconds

---

#### Actions Executed
**Metric name:** `actions_executed_total`
**Type:** Counter
**Labels:**
- `tenant_id` - Tenant identifier
- `action_type` - Type of action (retry, escalate, manual_intervention)
- `status` - Action status (succeeded, failed, pending)

**Purpose:** Track remediation effectiveness.

**Alerting:**
- Alert if action failure rate > 20%

---

#### Action Success Rate
**Metric name:** `action_success_rate`
**Type:** Gauge
**Labels:**
- `tenant_id` - Tenant identifier
- `action_type` - Type of action

**Calculation:** `succeeded / (succeeded + failed)` over rolling 1-hour window

**Purpose:** Monitor remediation effectiveness.

**Alerting:**
- Alert if success rate < 80% for retry actions

---

### 3. Safety Metrics

#### Circuit Breaker State
**Metric name:** `circuit_breaker_state`
**Type:** Gauge
**Labels:**
- `vendor` - Vendor name
- `state` - State (0=closed, 1=open, 2=half_open)

**Purpose:** Monitor vendor health and circuit breaker activations.

**Alerting:**
- Alert when circuit breaker opens (vendor down or degraded)
- Alert if circuit breaker stays open > 15 minutes

---

#### Circuit Breaker Transitions
**Metric name:** `circuit_breaker_transitions_total`
**Type:** Counter
**Labels:**
- `vendor` - Vendor name
- `from_state` - Previous state
- `to_state` - New state

**Purpose:** Track circuit breaker activation frequency.

**Alerting:**
- Alert if > 5 transitions to OPEN in 1 hour (vendor flapping)

---

#### Rate Limiter Rejections
**Metric name:** `rate_limiter_rejections_total`
**Type:** Counter
**Labels:**
- `tenant_id` - Tenant identifier
- `vendor` - Vendor name (if applicable)
- `limit_type` - Type of limit (per_tenant, per_vendor, per_workflow)

**Purpose:** Track rate limiting activations.

**Alerting:**
- Alert if rejections > 1000 per hour (DDoS or misconfiguration)

---

#### Retry Attempts
**Metric name:** `retry_attempts_total`
**Type:** Counter
**Labels:**
- `tenant_id` - Tenant identifier
- `workflow_id` - Workflow identifier
- `attempt_number` - Retry attempt (1, 2, 3, etc.)
- `result` - Result (succeeded, failed, max_retries_exceeded)

**Purpose:** Track retry effectiveness.

**Alerting:**
- Alert if max_retries_exceeded > 10% of retries

---

### 4. Infrastructure Metrics

#### Database Connection Pool
**Metric name:** `db_connection_pool_size`
**Type:** Gauge
**Labels:**
- `state` - Connection state (in_use, available, total)

**Purpose:** Monitor database connection utilization.

**Alerting:**
- Alert if `in_use / total` > 90% (connection pool exhaustion)

---

#### Database Query Duration
**Metric name:** `db_query_duration_seconds`
**Type:** Histogram
**Labels:**
- `operation` - Operation type (select, insert, update, delete)
- `table` - Table name

**Buckets:** 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0 seconds

**Purpose:** Identify slow queries.

**Alerting:**
- Alert if P95 > 100ms for any query

---

#### Redis Connection Count
**Metric name:** `redis_connections_total`
**Type:** Gauge
**Labels:**
- `state` - Connection state (active, idle)

**Purpose:** Monitor Redis connection utilization.

**Alerting:**
- Alert if active connections > max_connections * 0.9

---

#### Redis Operation Duration
**Metric name:** `redis_operation_duration_seconds`
**Type:** Histogram
**Labels:**
- `operation` - Redis command (get, set, incr, expire, etc.)

**Buckets:** 0.001, 0.005, 0.01, 0.05, 0.1, 0.5 seconds

**Purpose:** Identify slow Redis operations.

**Alerting:**
- Alert if P95 > 50ms

---

### 5. System Resource Metrics

#### CPU Usage
**Metric name:** `process_cpu_usage_percent`
**Type:** Gauge

**Purpose:** Monitor CPU utilization.

**Alerting:**
- Alert if > 80% for 5 minutes

---

#### Memory Usage
**Metric name:** `process_memory_usage_bytes`
**Type:** Gauge

**Purpose:** Monitor memory consumption.

**Alerting:**
- Alert if > 90% of available memory

---

#### Garbage Collection Duration
**Metric name:** `gc_duration_seconds`
**Type:** Histogram

**Purpose:** Identify GC pressure.

**Alerting:**
- Alert if GC pauses > 100ms frequently

---

## Logging Strategy

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| **DEBUG** | Development troubleshooting | Variable values, detailed flow |
| **INFO** | Normal operations | Event ingested, incident created |
| **WARNING** | Unexpected but handled | Rate limit approaching, retry scheduled |
| **ERROR** | Errors requiring attention | Database connection failed, validation error |
| **CRITICAL** | System-level failures | Service unable to start, data corruption |

### Structured Log Format

```json
{
  "timestamp": "2026-01-19T10:00:00.123Z",
  "level": "INFO",
  "logger": "src.awfdrs.ingestion.service",
  "message": "Event ingested successfully",
  "correlation_id": "req-abc-123",
  "tenant_id": "tenant-001",
  "workflow_id": "workflow-123",
  "event_id": "evt-456",
  "duration_ms": 45
}
```

### Log Retention

- **Application logs:** 30 days
- **Audit logs (events, decisions, actions):** 90 days minimum
- **Error logs:** 90 days
- **Debug logs:** 7 days (production), unlimited (development)

### Log Aggregation

**Recommended tools:**
- **ELK Stack:** Elasticsearch + Logstash + Kibana
- **Splunk:** Enterprise log management
- **Datadog:** Cloud-native observability
- **Grafana Loki:** Lightweight log aggregation

### Log Queries (Examples)

**Find all errors for a tenant:**
```
level:ERROR AND tenant_id:"tenant-001"
```

**Find all events for a correlation ID:**
```
correlation_id:"req-abc-123"
```

**Find slow requests:**
```
duration_ms:>1000
```

---

## Tracing Strategy

### Distributed Tracing

**Implementation:** OpenTelemetry (future enhancement)

**Trace context:**
- `trace_id` - Unique identifier for entire request flow
- `span_id` - Unique identifier for each operation
- `parent_span_id` - Link to parent operation

**Trace spans:**
1. `http.request` - API handler
2. `service.ingest_event` - Business logic
3. `db.query.insert` - Database operation
4. `redis.incr` - Rate limiter check
5. `service.detect_incident` - Incident detection

### Correlation IDs

**Current implementation:** Correlation IDs track requests.

**Propagation:**
- Generated at API gateway/middleware
- Included in all logs
- Stored in database records
- Returned in API responses

**Example:**
```
Request → req-abc-123
  ↓
Event (correlation_id: req-abc-123)
  ↓
Incident (correlation_id: req-abc-123)
  ↓
Action (correlation_id: req-abc-123)
```

---

## Alerting Strategy

### Alert Severity Levels

| Severity | Response Time | Example |
|----------|---------------|---------|
| **P0 - Critical** | 15 minutes | Service down, data loss |
| **P1 - High** | 1 hour | Elevated error rate, SLO breach |
| **P2 - Medium** | 4 hours | Non-critical feature degraded |
| **P3 - Low** | Next business day | Performance degradation, warnings |

### Alert Channels

- **P0:** PagerDuty → On-call engineer + Slack #alerts-critical
- **P1:** PagerDuty → On-call engineer + Slack #alerts-high
- **P2:** Slack #alerts-medium
- **P3:** Email to team alias

### Alert Examples

#### P0: Service Down
**Trigger:** API availability < 99% for 5 minutes
**Action:** Investigate immediately, failover if needed

#### P0: Database Connection Failure
**Trigger:** Database connection pool exhausted or connection failures > 50%
**Action:** Check database health, restart if needed

#### P1: High Error Rate
**Trigger:** Error rate > 5% for 10 minutes
**Action:** Investigate logs, identify root cause

#### P1: Circuit Breaker Open
**Trigger:** Circuit breaker opens for critical vendor
**Action:** Check vendor status, coordinate with vendor if needed

#### P2: Slow Queries
**Trigger:** P95 query latency > 200ms for 15 minutes
**Action:** Investigate query patterns, add indexes if needed

#### P3: Memory Usage High
**Trigger:** Memory usage > 80% for 1 hour
**Action:** Monitor trend, plan capacity increase if persistent

---

## Dashboard Recommendations

### 1. Service Health Dashboard

**Metrics:**
- API request rate (RPS)
- API latency (P50, P95, P99)
- Error rate (%)
- Service uptime (%)

**Purpose:** High-level service health overview.

---

### 2. Business Metrics Dashboard

**Metrics:**
- Events ingested (count/hour)
- Incidents detected (count/hour)
- Actions executed (count/hour)
- Action success rate (%)
- Incidents by severity (breakdown)

**Purpose:** Business KPIs and operational insights.

---

### 3. Safety Metrics Dashboard

**Metrics:**
- Circuit breaker states (per vendor)
- Rate limiter rejections (count/hour)
- Retry attempts by outcome
- Safety limits triggered

**Purpose:** Monitor safety controls effectiveness.

---

### 4. Infrastructure Dashboard

**Metrics:**
- Database connection pool utilization
- Database query latency
- Redis connection count
- Redis operation latency
- CPU usage
- Memory usage

**Purpose:** Infrastructure health monitoring.

---

### 5. Per-Tenant Dashboard

**Metrics (filtered by tenant_id):**
- Events ingested
- Incidents detected
- Actions executed
- Error rate
- Rate limiter rejections

**Purpose:** Tenant-specific health and usage tracking.

---

## Capacity Planning Metrics

### Resource Utilization Trends

**Track monthly:**
- Peak RPS (requests per second)
- Average database connection usage
- Average Redis connection usage
- Peak memory usage
- 95th percentile query latency

**Capacity alerts:**
- Alert if peak RPS reaches 80% of capacity
- Alert if database connections exceed 70% of pool
- Alert if memory usage trend projects exhaustion within 30 days

### Growth Metrics

**Track quarterly:**
- Total events ingested (growth rate)
- Total tenants (growth rate)
- Total workflows (growth rate)
- Database size (GB)
- Average events per tenant

**Purpose:** Plan infrastructure scaling.

---

## Implementation Roadmap

### Phase 1: Basic Metrics (Current)
- [x] Structured JSON logging
- [x] Correlation ID tracking
- [x] Basic error logging

### Phase 2: Application Metrics (Next)
- [ ] Prometheus metrics export
- [ ] Request counters and histograms
- [ ] Business metrics (events, incidents, actions)
- [ ] Basic Grafana dashboards

### Phase 3: Advanced Observability
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Advanced dashboards
- [ ] Alert rules and PagerDuty integration
- [ ] Log aggregation (ELK or Loki)

### Phase 4: Optimization
- [ ] Query performance profiling
- [ ] Load testing and benchmarking
- [ ] Capacity planning automation
- [ ] SLO monitoring and reporting

---

## Metrics Endpoint (Future)

### Prometheus Format

**Endpoint:** `GET /metrics`

**Example output:**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/api/v1/events",status_code="201"} 15234

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="POST",endpoint="/api/v1/events",le="0.01"} 12000
http_request_duration_seconds_bucket{method="POST",endpoint="/api/v1/events",le="0.05"} 14500
http_request_duration_seconds_bucket{method="POST",endpoint="/api/v1/events",le="0.1"} 15100
http_request_duration_seconds_sum{method="POST",endpoint="/api/v1/events"} 450.23
http_request_duration_seconds_count{method="POST",endpoint="/api/v1/events"} 15234
```

---

## Monitoring Best Practices

### 1. Monitor the Four Golden Signals

- **Latency** - Time to service requests
- **Traffic** - Demand on the system (RPS)
- **Errors** - Rate of failed requests
- **Saturation** - Resource utilization (CPU, memory, connections)

### 2. Use SLOs, Not SLAs

- **SLO (Service Level Objective):** Internal target (e.g., 99.9% uptime)
- **SLA (Service Level Agreement):** External contract with penalties

Keep SLO stricter than SLA to have buffer.

### 3. Alert on Symptoms, Not Causes

**Bad:** Alert on high CPU
**Good:** Alert on high latency (symptom), investigate CPU (cause)

### 4. Avoid Alert Fatigue

- Too many alerts → ignored alerts → missed incidents
- Tune alert thresholds to reduce false positives
- Group related alerts
- Auto-resolve alerts when condition clears

### 5. Test Alerts

- Regularly trigger test alerts to verify notification channels
- Ensure on-call engineers receive and acknowledge alerts

---

## Additional Resources

- **Prometheus:** https://prometheus.io/
- **Grafana:** https://grafana.com/
- **OpenTelemetry:** https://opentelemetry.io/
- **Site Reliability Engineering Book:** https://sre.google/books/

---

## Summary

**Observability is critical for production systems.** This document defines the metrics, logs, and traces needed to monitor AWFDRS health, performance, and business outcomes.

**Immediate priorities:**
1. Implement Prometheus metrics export
2. Create Grafana dashboards
3. Set up alert rules
4. Test alerting channels

**Long-term:**
- Distributed tracing with OpenTelemetry
- Advanced analytics and anomaly detection
- Automated capacity planning
