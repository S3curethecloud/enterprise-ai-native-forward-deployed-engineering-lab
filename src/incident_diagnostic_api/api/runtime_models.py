"""Typed HTTP request contracts for the local Phase 4 runtime service."""

from typing import Annotated

from pydantic import Field

from incident_diagnostic_api.contracts.common import (
    ContractModel,
    NonNegativeDuration,
    OpaqueIdentifier,
    Timestamp,
)
from incident_diagnostic_api.runtime import (
    RuntimeRetryRequest,
    RuntimeStateRecord,
    RuntimeTransitionContext,
    TransitionCommand,
)

StateVersion = Annotated[int, Field(ge=0)]


class RuntimeStartRequest(ContractModel):
    """Request creation of one local deterministic workflow."""

    record: RuntimeStateRecord
    event_id: OpaqueIdentifier
    timestamp: Timestamp


class RuntimeTransitionRequest(ContractModel):
    """Request one deterministic transition using optimistic concurrency."""

    expected_state_version: StateVersion
    command: TransitionCommand
    event_id: OpaqueIdentifier
    timestamp: Timestamp
    context: RuntimeTransitionContext | None = None
    duration_ms: NonNegativeDuration | None = None


class RuntimeRetryApiRequest(ContractModel):
    """Request one bounded retry for an explicitly transient failure."""

    expected_state_version: StateVersion
    retry_request: RuntimeRetryRequest
    event_id: OpaqueIdentifier
    timestamp: Timestamp
    duration_ms: NonNegativeDuration | None = None
