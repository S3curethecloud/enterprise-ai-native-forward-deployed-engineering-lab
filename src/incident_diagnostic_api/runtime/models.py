"""Immutable state contracts for the Phase 4 deterministic runtime."""

from typing import Self

from pydantic import Field, field_validator, model_validator

from incident_diagnostic_api.contracts.common import (
    ContractModel,
    OpaqueIdentifier,
    ReasonCode,
    Timestamp,
)
from incident_diagnostic_api.runtime.enums import (
    RuntimeReasonCode,
    RuntimeState,
    is_terminal_state,
)


class StageRetryCount(ContractModel):
    """Immutable retry count for one runtime state."""

    state: RuntimeState
    retry_count: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def reject_terminal_state(self) -> Self:
        """Prevent retry accounting against terminal states."""

        if is_terminal_state(self.state):
            raise ValueError("retry counts cannot be assigned to terminal states")

        return self


class RuntimeStateRecord(ContractModel):
    """Immutable snapshot of one bounded diagnostic workflow."""

    workflow_id: OpaqueIdentifier
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier

    state: RuntimeState = RuntimeState.RECEIVED
    state_version: int = Field(default=0, ge=0)
    step_count: int = Field(default=0, ge=0)
    retry_count: int = Field(default=0, ge=0)
    stage_retry_counts: tuple[StageRetryCount, ...] = ()

    reason_codes: tuple[RuntimeReasonCode | ReasonCode, ...] = (RuntimeReasonCode.RUNTIME_CREATED,)

    created_at: Timestamp
    updated_at: Timestamp

    policy_decision_id: OpaqueIdentifier | None = None
    authorization_expires_at: Timestamp | None = None

    request_reference: OpaqueIdentifier | None = None
    identity_reference: OpaqueIdentifier | None = None
    evidence_reference: OpaqueIdentifier | None = None
    response_reference: OpaqueIdentifier | None = None
    error_reference: OpaqueIdentifier | None = None

    @field_validator("reason_codes", mode="before")
    @classmethod
    def normalize_runtime_reason_codes(cls, value: object) -> object:
        """Restore known runtime reason codes after JSON transport."""

        if not isinstance(value, (list, tuple)):
            return value

        runtime_reason_codes = {reason_code.value: reason_code for reason_code in RuntimeReasonCode}

        return tuple(
            runtime_reason_codes.get(item, item) if isinstance(item, str) else item
            for item in value
        )

    @model_validator(mode="after")
    def validate_snapshot(self) -> Self:
        """Enforce cross-field state invariants."""

        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot precede created_at")

        if self.retry_count > self.step_count:
            raise ValueError("retry_count cannot exceed step_count")

        retry_states = tuple(item.state for item in self.stage_retry_counts)

        if len(retry_states) != len(set(retry_states)):
            raise ValueError("stage_retry_counts cannot contain duplicate states")

        stage_retry_total = sum(item.retry_count for item in self.stage_retry_counts)

        if stage_retry_total != self.retry_count:
            raise ValueError("stage retry counts must sum to the total retry_count")

        if self.authorization_expires_at is not None and self.policy_decision_id is None:
            raise ValueError("authorization_expires_at requires policy_decision_id")

        if self.state is RuntimeState.RECEIVED and (
            self.state_version != 0 or self.step_count != 0 or self.retry_count != 0
        ):
            raise ValueError("a received runtime record must begin at version and count zero")

        return self

    @property
    def terminal(self) -> bool:
        """Return whether this snapshot represents a terminal workflow."""

        return is_terminal_state(self.state)

    def retry_count_for(self, state: RuntimeState) -> int:
        """Return the recorded retry count for a non-terminal state."""

        for item in self.stage_retry_counts:
            if item.state is state:
                return item.retry_count

        return 0
