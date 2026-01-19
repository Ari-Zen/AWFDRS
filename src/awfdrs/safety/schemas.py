"""
Pydantic schemas for safety layer.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from src.awfdrs.core.enums import ErrorSeverity, ActionType


class ErrorContext(BaseModel):
    """Context for error evaluation."""

    error_code: str
    vendor: Optional[str] = None
    workflow_id: Optional[str] = None
    tenant_id: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RuleEvaluation(BaseModel):
    """Result of rule evaluation."""

    should_retry: bool
    recommended_action: ActionType
    backoff_seconds: float
    severity: ErrorSeverity
    rule_triggered: Optional[str] = None
    reasoning: str


class BackoffCalculation(BaseModel):
    """Backoff timing calculation."""

    base_delay: float
    jitter: float
    total_delay: float
    retry_count: int


class RateLimitResult(BaseModel):
    """Result of rate limit check."""

    allowed: bool
    remaining: int
    retry_after: Optional[int] = None
    limit: int
