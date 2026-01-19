"""
Event ingestion validation logic.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.awfdrs.db.repositories.tenants import TenantRepository
from src.awfdrs.db.repositories.workflows import WorkflowRepository
from src.awfdrs.db.repositories.events import EventRepository
from src.awfdrs.core.exceptions import (
    ValidationError,
    NotFoundError,
    KillSwitchActiveError,
    ConflictError
)


async def validate_schema_version(schema_version: str) -> None:
    """
    Validate that schema version is supported.

    Args:
        schema_version: Schema version string

    Raises:
        ValidationError: If schema version is not supported
    """
    supported_versions = ["1.0.0"]
    if schema_version not in supported_versions:
        raise ValidationError(
            f"Unsupported schema version: {schema_version}",
            details={"supported_versions": supported_versions}
        )


async def validate_tenant_exists(
    session: AsyncSession,
    tenant_id: UUID
) -> None:
    """
    Validate that tenant exists and is active.

    Args:
        session: Database session
        tenant_id: Tenant ID

    Raises:
        NotFoundError: If tenant not found
        ValidationError: If tenant is not active
    """
    tenant_repo = TenantRepository(session)
    tenant = await tenant_repo.get(tenant_id)

    if not tenant:
        raise NotFoundError(
            f"Tenant not found: {tenant_id}",
            details={"tenant_id": str(tenant_id)}
        )

    if not tenant.is_active:
        raise ValidationError(
            f"Tenant is not active: {tenant_id}",
            details={"tenant_id": str(tenant_id)}
        )


async def validate_workflow_exists(
    session: AsyncSession,
    workflow_id: UUID
) -> None:
    """
    Validate that workflow exists and is not kill-switched.

    Args:
        session: Database session
        workflow_id: Workflow ID

    Raises:
        NotFoundError: If workflow not found
        KillSwitchActiveError: If workflow is kill-switched
    """
    workflow_repo = WorkflowRepository(session)
    workflow = await workflow_repo.get(workflow_id)

    if not workflow:
        raise NotFoundError(
            f"Workflow not found: {workflow_id}",
            details={"workflow_id": str(workflow_id)}
        )

    if workflow.is_kill_switched:
        raise KillSwitchActiveError(
            f"Workflow is kill-switched: {workflow_id}",
            details={"workflow_id": str(workflow_id)}
        )


async def validate_idempotency_key(
    session: AsyncSession,
    idempotency_key: str
) -> None:
    """
    Validate that idempotency key is not duplicate.

    Args:
        session: Database session
        idempotency_key: Idempotency key

    Raises:
        ConflictError: If idempotency key already exists
    """
    event_repo = EventRepository(session)
    existing = await event_repo.get_by_idempotency_key(idempotency_key)

    if existing:
        raise ConflictError(
            f"Event with idempotency key already exists: {idempotency_key}",
            details={
                "idempotency_key": idempotency_key,
                "existing_event_id": str(existing.id)
            }
        )


async def validate_payload_structure(payload: dict) -> None:
    """
    Basic payload validation.

    Args:
        payload: Event payload

    Raises:
        ValidationError: If payload is invalid
    """
    if not isinstance(payload, dict):
        raise ValidationError(
            "Payload must be a dictionary",
            details={"type": type(payload).__name__}
        )

    if not payload:
        raise ValidationError(
            "Payload cannot be empty",
            details={}
        )

    # Check for maximum payload size (e.g., 1MB)
    import json
    payload_size = len(json.dumps(payload))
    max_size = 1024 * 1024  # 1MB

    if payload_size > max_size:
        raise ValidationError(
            f"Payload size exceeds maximum of {max_size} bytes",
            details={"size": payload_size, "max_size": max_size}
        )
