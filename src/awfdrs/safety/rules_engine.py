"""
Rules engine for error evaluation and retry policy determination.
"""

import yaml
import random
from pathlib import Path
from typing import Dict, Any, Optional
from src.awfdrs.safety.schemas import RuleEvaluation, BackoffCalculation, ErrorContext
from src.awfdrs.core.enums import ErrorSeverity, ActionType


class RulesEngine:
    """
    Rules engine for evaluating errors and determining actions.

    Loads error codes and retry policies from YAML configuration files.
    """

    def __init__(self, config_dir: str = "config/rules") -> None:
        """
        Initialize rules engine.

        Args:
            config_dir: Directory containing configuration YAML files
        """
        self.config_dir = Path(config_dir)
        self.error_codes: Dict[str, Any] = {}
        self.retry_policies: Dict[str, Any] = {}
        self._load_configurations()

    def _load_configurations(self) -> None:
        """Load error codes and retry policies from YAML files."""
        # Load error codes
        error_codes_file = self.config_dir / "error_codes.yaml"
        if error_codes_file.exists():
            with open(error_codes_file, 'r') as f:
                data = yaml.safe_load(f)
                self.error_codes = data.get('error_codes', {})

        # Load retry policies
        retry_policies_file = self.config_dir / "retry_policies.yaml"
        if retry_policies_file.exists():
            with open(retry_policies_file, 'r') as f:
                data = yaml.safe_load(f)
                self.retry_policies = data.get('retry_policies', {})

    async def evaluate_error(
        self,
        error_code: str,
        context: ErrorContext
    ) -> RuleEvaluation:
        """
        Evaluate an error and determine appropriate action.

        Args:
            error_code: Error code to evaluate
            context: Error context

        Returns:
            Rule evaluation with recommended action
        """
        # Get error definition
        error_def = self.error_codes.get(error_code, {})
        severity = ErrorSeverity(error_def.get('severity', 'medium'))
        policy_name = error_def.get('retry_policy', 'default')

        # Get retry policy
        policy = self.retry_policies.get(policy_name, {})
        retryable = policy.get('retryable', False)
        max_retries = policy.get('max_retries', 0)

        # Determine if should retry
        should_retry = (
            retryable and
            context.retry_count < max_retries
        )

        # Calculate backoff if retrying
        backoff = 0.0
        if should_retry:
            backoff_calc = await self.calculate_backoff(error_code, context.retry_count)
            backoff = backoff_calc.total_delay

        # Determine recommended action
        if should_retry:
            recommended_action = ActionType.RETRY
        elif severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            recommended_action = ActionType.ESCALATE
        else:
            recommended_action = ActionType.NOTIFY

        return RuleEvaluation(
            should_retry=should_retry,
            recommended_action=recommended_action,
            backoff_seconds=backoff,
            severity=severity,
            rule_triggered=policy_name,
            reasoning=f"Error code '{error_code}' evaluated with policy '{policy_name}'"
        )

    async def should_retry(self, error_code: str, retry_count: int) -> bool:
        """
        Determine if an error should be retried.

        Args:
            error_code: Error code
            retry_count: Current retry count

        Returns:
            True if should retry, False otherwise
        """
        error_def = self.error_codes.get(error_code, {})
        policy_name = error_def.get('retry_policy', 'default')
        policy = self.retry_policies.get(policy_name, {})

        retryable = policy.get('retryable', False)
        max_retries = policy.get('max_retries', 0)

        return retryable and retry_count < max_retries

    async def calculate_backoff(
        self,
        error_code: str,
        retry_count: int
    ) -> BackoffCalculation:
        """
        Calculate backoff delay with exponential backoff and jitter.

        Args:
            error_code: Error code
            retry_count: Current retry count

        Returns:
            Backoff calculation with delays
        """
        error_def = self.error_codes.get(error_code, {})
        policy_name = error_def.get('retry_policy', 'default')
        policy = self.retry_policies.get(policy_name, {})

        # Get backoff configuration
        initial_delay = policy.get('initial_delay_seconds', 1.0)
        max_delay = policy.get('max_delay_seconds', 300.0)
        backoff_multiplier = policy.get('backoff_multiplier', 2.0)

        # Calculate exponential backoff
        base_delay = min(
            initial_delay * (backoff_multiplier ** retry_count),
            max_delay
        )

        # Add jitter (±20% of base delay)
        jitter = base_delay * 0.2 * (2 * random.random() - 1)
        total_delay = max(0, base_delay + jitter)

        return BackoffCalculation(
            base_delay=base_delay,
            jitter=jitter,
            total_delay=total_delay,
            retry_count=retry_count
        )

    async def get_error_severity(self, error_code: str) -> ErrorSeverity:
        """
        Get severity level for an error code.

        Args:
            error_code: Error code

        Returns:
            Error severity
        """
        error_def = self.error_codes.get(error_code, {})
        severity_str = error_def.get('severity', 'medium')
        return ErrorSeverity(severity_str)
