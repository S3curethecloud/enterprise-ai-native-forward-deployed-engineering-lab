"""Deterministic replay for Phase 4 checkpoint histories."""

from dataclasses import dataclass
from typing import Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    ContentHash,
    ContractModel,
    OpaqueIdentifier,
)
from incident_diagnostic_api.runtime.checkpoints import (
    RuntimeCheckpoint,
    verify_checkpoint_history,
)
from incident_diagnostic_api.runtime.enums import (
    RuntimeReasonCode,
    RuntimeState,
    TransitionCommand,
)
from incident_diagnostic_api.runtime.models import RuntimeStateRecord
from incident_diagnostic_api.runtime.transitions import TRANSITIONS


@dataclass(frozen=True, slots=True)
class ReplayIntegrityError(Exception):
    """Controlled failure raised when replay evidence diverges."""

    message: str
    reason_code: RuntimeReasonCode
    sequence: int | None = None

    def __str__(self) -> str:
        """Return a controlled replay failure description."""

        return self.message


class ReplayStep(ContractModel):
    """One reconstructed step in a checkpoint replay."""

    sequence: int = Field(ge=0)
    checkpoint_id: OpaqueIdentifier
    state_version: int = Field(ge=0)
    source_state: RuntimeState | None = None
    command: TransitionCommand | None = None
    target_state: RuntimeState
    checkpoint_hash: ContentHash

    @model_validator(mode="after")
    def validate_step_shape(self) -> Self:
        """Keep genesis and transition steps structurally distinct."""

        if self.sequence == 0:
            if self.source_state is not None or self.command is not None:
                raise ValueError("the genesis replay step cannot declare a source state or command")
        elif self.source_state is None or self.command is None:
            raise ValueError("a non-genesis replay step requires a source state and command")

        return self


class ReplayResult(ContractModel):
    """Immutable evidence from one verified deterministic replay."""

    workflow_id: OpaqueIdentifier
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    verified: bool = True
    reason_code: RuntimeReasonCode = RuntimeReasonCode.REPLAY_VERIFIED
    checkpoint_count: int = Field(ge=1)
    steps: tuple[ReplayStep, ...] = Field(min_length=1)
    final_state: RuntimeState
    final_state_version: int = Field(ge=0)
    final_checkpoint_hash: ContentHash

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        """Keep replay summary fields aligned with replay steps."""

        if not self.verified:
            raise ValueError("ReplayResult represents verified replay evidence only")

        if self.reason_code is not RuntimeReasonCode.REPLAY_VERIFIED:
            raise ValueError("a verified replay requires REPLAY_VERIFIED")

        if self.checkpoint_count != len(self.steps):
            raise ValueError("checkpoint_count must equal the replay-step count")

        final_step = self.steps[-1]

        if self.final_state is not final_step.target_state:
            raise ValueError("final_state must match the final replay step")

        if self.final_state_version != final_step.state_version:
            raise ValueError("final_state_version must match the final replay step")

        if self.final_checkpoint_hash != final_step.checkpoint_hash:
            raise ValueError("final_checkpoint_hash must match the final replay step")

        return self


def _raise_integrity(
    message: str,
    *,
    sequence: int | None = None,
    reason_code: RuntimeReasonCode = (RuntimeReasonCode.REPLAY_DIVERGENCE),
) -> None:
    """Raise one controlled replay-integrity failure."""

    raise ReplayIntegrityError(
        message=message,
        reason_code=reason_code,
        sequence=sequence,
    )


def _ensure_identity_lineage(
    baseline: RuntimeStateRecord,
    current: RuntimeStateRecord,
    *,
    sequence: int,
) -> None:
    """Ensure immutable workflow identity survives every checkpoint."""

    if current.workflow_id != baseline.workflow_id:
        _raise_integrity(
            "workflow identity changed during replay",
            sequence=sequence,
        )

    if current.request_id != baseline.request_id:
        _raise_integrity(
            "request identity changed during replay",
            sequence=sequence,
        )

    if current.trace_id != baseline.trace_id:
        _raise_integrity(
            "trace identity changed during replay",
            sequence=sequence,
        )


def _stage_retry_map(
    snapshot: RuntimeStateRecord,
) -> dict[RuntimeState, int]:
    """Return deterministic per-state retry counters."""

    return {item.state: item.retry_count for item in snapshot.stage_retry_counts}


def _resolve_recorded_command(
    previous: RuntimeStateRecord,
    current: RuntimeStateRecord,
    *,
    sequence: int,
) -> TransitionCommand:
    """Reconstruct one command from two immutable snapshots."""

    if current.step_count != previous.step_count + 1:
        _raise_integrity(
            "step count did not advance exactly once",
            sequence=sequence,
        )

    if current.state is previous.state:
        if current.retry_count != previous.retry_count + 1:
            _raise_integrity(
                "same-state replay requires one additional retry",
                sequence=sequence,
            )

        expected_stage_retries = _stage_retry_map(previous)
        expected_stage_retries[previous.state] = expected_stage_retries.get(previous.state, 0) + 1

        if _stage_retry_map(current) != expected_stage_retries:
            _raise_integrity(
                "same-state replay has inconsistent stage retries",
                sequence=sequence,
            )

        if (
            not current.reason_codes
            or current.reason_codes[-1] is not RuntimeReasonCode.RETRY_SCHEDULED
        ):
            _raise_integrity(
                "same-state replay lacks RETRY_SCHEDULED evidence",
                sequence=sequence,
            )

        return TransitionCommand.RETRY_CURRENT_STAGE

    if current.retry_count != previous.retry_count:
        _raise_integrity(
            "normal transition changed the retry count",
            sequence=sequence,
        )

    candidates = [
        transition
        for transition in TRANSITIONS.values()
        if transition.source is previous.state and transition.target is current.state
    ]

    if len(candidates) != 1:
        _raise_integrity(
            "state change does not map to one authorized transition",
            sequence=sequence,
        )

    transition = candidates[0]

    if not current.reason_codes or current.reason_codes[-1] is not transition.reason_code:
        _raise_integrity(
            "state change reason does not match its transition",
            sequence=sequence,
        )

    return transition.command


def replay_checkpoint_history(
    checkpoints: tuple[RuntimeCheckpoint, ...],
) -> ReplayResult:
    """Verify and reconstruct an append-only checkpoint history."""

    if not checkpoints:
        _raise_integrity(
            "checkpoint history is empty",
            reason_code=(RuntimeReasonCode.CHECKPOINT_INTEGRITY_FAILURE),
        )

    if not verify_checkpoint_history(checkpoints):
        _raise_integrity(
            "checkpoint hash or sequence integrity failed",
            reason_code=(RuntimeReasonCode.CHECKPOINT_INTEGRITY_FAILURE),
        )

    baseline = checkpoints[0].snapshot

    if baseline.state is not RuntimeState.RECEIVED:
        _raise_integrity(
            "checkpoint history does not begin in RECEIVED",
            sequence=0,
        )

    if baseline.state_version != 0 or baseline.step_count != 0 or baseline.retry_count != 0:
        _raise_integrity(
            "genesis runtime counters are invalid",
            sequence=0,
        )

    replay_steps: list[ReplayStep] = [
        ReplayStep(
            sequence=0,
            checkpoint_id=checkpoints[0].checkpoint_id,
            state_version=baseline.state_version,
            target_state=baseline.state,
            checkpoint_hash=checkpoints[0].checkpoint_hash,
        )
    ]

    previous = baseline

    for checkpoint in checkpoints[1:]:
        current = checkpoint.snapshot

        _ensure_identity_lineage(
            baseline,
            current,
            sequence=checkpoint.sequence,
        )

        command = _resolve_recorded_command(
            previous,
            current,
            sequence=checkpoint.sequence,
        )

        replay_steps.append(
            ReplayStep(
                sequence=checkpoint.sequence,
                checkpoint_id=checkpoint.checkpoint_id,
                state_version=current.state_version,
                source_state=previous.state,
                command=command,
                target_state=current.state,
                checkpoint_hash=checkpoint.checkpoint_hash,
            )
        )

        previous = current

    final_checkpoint = checkpoints[-1]

    return ReplayResult(
        workflow_id=baseline.workflow_id,
        request_id=baseline.request_id,
        trace_id=baseline.trace_id,
        checkpoint_count=len(checkpoints),
        steps=tuple(replay_steps),
        final_state=final_checkpoint.snapshot.state,
        final_state_version=final_checkpoint.state_version,
        final_checkpoint_hash=final_checkpoint.checkpoint_hash,
    )
