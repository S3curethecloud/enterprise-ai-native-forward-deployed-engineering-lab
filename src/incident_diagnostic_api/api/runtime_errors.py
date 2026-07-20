"""Controlled HTTP error contracts for the local Phase 4 runtime API."""

from enum import StrEnum
from typing import Annotated, NoReturn

from fastapi import HTTPException
from pydantic import Field

from incident_diagnostic_api.contracts.common import (
    ContractModel,
    OpaqueIdentifier,
    ReasonCode,
)
from incident_diagnostic_api.runtime import RuntimeReasonCode, RuntimeState


class RuntimeApiErrorCode(StrEnum):
    """Allowlisted runtime API failure codes."""

    WORKFLOW_NOT_FOUND = "WORKFLOW_NOT_FOUND"
    VERSION_CONFLICT = "VERSION_CONFLICT"
    INVALID_TRANSITION = "INVALID_TRANSITION"
    EXECUTION_STOPPED = "EXECUTION_STOPPED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    REPLAY_INTEGRITY_FAILURE = "REPLAY_INTEGRITY_FAILURE"
    RUNTIME_INTERNAL_ERROR = "RUNTIME_INTERNAL_ERROR"


class RuntimeApiError(ContractModel):
    """Non-sensitive error returned by the bounded runtime service."""

    error_code: RuntimeApiErrorCode
    safe_message: Annotated[str, Field(min_length=1, max_length=500)]
    retryable: bool = False
    workflow_id: OpaqueIdentifier | None = None
    state: RuntimeState | None = None
    reason_code: RuntimeReasonCode | ReasonCode | None = None


def raise_runtime_api_error(
    *,
    status_code: int,
    error_code: RuntimeApiErrorCode,
    safe_message: str,
    retryable: bool = False,
    workflow_id: str | None = None,
    state: RuntimeState | None = None,
    reason_code: RuntimeReasonCode | ReasonCode | None = None,
) -> NoReturn:
    """Raise one controlled FastAPI error without leaking runtime internals."""

    error = RuntimeApiError(
        error_code=error_code,
        safe_message=safe_message,
        retryable=retryable,
        workflow_id=workflow_id,
        state=state,
        reason_code=reason_code,
    )

    raise HTTPException(
        status_code=status_code,
        detail=error.model_dump(mode="json"),
    )
