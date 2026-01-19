"""
Core enums for the AWFDRS system.
"""

from enum import Enum


class IncidentStatus(str, Enum):
    """Incident lifecycle status."""

    DETECTED = "detected"
    ANALYZING = "analyzing"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    IGNORED = "ignored"


class ActionType(str, Enum):
    """Types of actions that can be taken."""

    RETRY = "retry"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    CIRCUIT_BREAKER_CLOSE = "circuit_breaker_close"
    KILL_SWITCH_ACTIVATE = "kill_switch_activate"
    KILL_SWITCH_DEACTIVATE = "kill_switch_deactivate"
    ESCALATE = "escalate"
    NOTIFY = "notify"
    ROLLBACK = "rollback"


class ActionStatus(str, Enum):
    """Action execution status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ErrorSeverity(str, Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


class DecisionType(str, Enum):
    """Types of decisions that can be made."""

    RULE_BASED = "rule_based"
    AI_ASSISTED = "ai_assisted"
    MANUAL = "manual"
    AUTOMATED = "automated"


class KillSwitchScope(str, Enum):
    """Scope of kill switch activation."""

    WORKFLOW = "workflow"
    VENDOR = "vendor"
    TENANT = "tenant"
    GLOBAL = "global"


class EventType(str, Enum):
    """Types of workflow events."""

    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    STEP_STARTED = "step.started"
    STEP_COMPLETED = "step.completed"
    STEP_FAILED = "step.failed"
    API_CALL_STARTED = "api_call.started"
    API_CALL_COMPLETED = "api_call.completed"
    API_CALL_FAILED = "api_call.failed"
    PAYMENT_INITIATED = "payment.initiated"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    USER_ACTION = "user.action"
    SYSTEM_EVENT = "system.event"
