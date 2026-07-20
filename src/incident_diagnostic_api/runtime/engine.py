"""Deterministic local orchestration engine for Phase 4."""

from dataclasses import dataclass
from threading import RLock
from typing import Self

from pydantic import model_validator

from incident_diagnostic_api.contracts import TraceEvent
from incident_diagnostic_api.contracts.common import (
    ContractModel,
    OpaqueIdentifier,
    ReasonCode,
    Timestamp,
)
from incident_diagnostic_api.runtime.budgets import (
    RuntimeBudgetLimits,
    increment_stage_retry_counts,
)
from incident_diagnostic_api.runtime.checkpoints import (
    CheckpointVersionConflictError,
    InMemoryCheckpointStore,
    RuntimeCheckpoint,
)
from incident_diagnostic_api.runtime.enums import (
    FailureClassification,
    RuntimeReasonCode,
    TransitionCommand,
)
from incident_diagnostic_api.runtime.models import RuntimeStateRecord
from incident_diagnostic_api.runtime.replay import (
    ReplayResult,
    replay_checkpoint_history,
)
from incident_diagnostic_api.runtime.stops import (
    StopDecision,
    evaluate_pre_transition_stop,
    evaluate_retry_stop,
)
from incident_diagnostic_api.runtime.traces import (
    build_genesis_trace_event,
    build_retry_trace_event,
    build_stop_trace_event,
    build_transition_trace_event,
)
from incident_diagnostic_api.runtime.transitions import resolve_transition


class RuntimeTransitionContext(ContractModel):
    """Typed references supplied to one deterministic transition."""

    policy_decision_id: OpaqueIdentifier | None = None
    authorization_expires_at: Timestamp | None = None
    request_reference: OpaqueIdentifier | None = None
    identity_reference: OpaqueIdentifier | None = None
    evidence_reference: OpaqueIdentifier | None = None
    response_reference: OpaqueIdentifier | None = None
    error_reference: OpaqueIdentifier | None = None


class RuntimeRetryRequest(ContractModel):
    """Typed evidence required before scheduling one retry."""

    failure_classification: FailureClassification
    failure_reason_code: ReasonCode

    @model_validator(mode="after")
    def require_transient_failure(self) -> Self:
        """Only explicitly transient failures are retryable."""

        if self.failure_classification is not FailureClassification.TRANSIENT:
            raise ValueError("only transient failures may schedule a retry")

        return self


class RuntimeStartResult(ContractModel):
    """Evidence returned when a workflow is created."""

    snapshot: RuntimeStateRecord
    checkpoint: RuntimeCheckpoint
    trace_event: TraceEvent


class RuntimeStepResult(ContractModel):
    """Evidence returned after one accepted runtime step."""

    command: TransitionCommand
    snapshot: RuntimeStateRecord
    checkpoint: RuntimeCheckpoint
    trace_event: TraceEvent


@dataclass(frozen=True, slots=True)
class RuntimeExecutionStoppedError(Exception):
    """Raised when a deterministic stop blocks coordination."""

    decision: StopDecision
    trace_event: TraceEvent

    def __str__(self) -> str:
        """Return the controlled stop message."""

        return self.decision.safe_message


class DeterministicRuntimeEngine:
    """Coordinate typed local state without external authority."""

    def __init__(
        self,
        *,
        limits: RuntimeBudgetLimits | None = None,
        checkpoint_store: InMemoryCheckpointStore | None = None,
    ) -> None:
        self._limits = limits or RuntimeBudgetLimits()
        self._checkpoints = checkpoint_store or InMemoryCheckpointStore()
        self._lock = RLock()

    @property
    def limits(self) -> RuntimeBudgetLimits:
        """Return immutable runtime budget limits."""

        return self._limits

    def start(
        self,
        record: RuntimeStateRecord,
        *,
        event_id: str,
        timestamp: Timestamp,
    ) -> RuntimeStartResult:
        """Create a workflow, its genesis checkpoint, and CT-07 event."""

        with self._lock:
            trace_event = build_genesis_trace_event(
                record=record,
                event_id=event_id,
                timestamp=timestamp,
            )
            checkpoint = self._checkpoints.append(
                record,
                expected_previous_version=None,
                created_at=timestamp,
            )

            return RuntimeStartResult(
                snapshot=record,
                checkpoint=checkpoint,
                trace_event=trace_event,
            )

    def current(self, workflow_id: str) -> RuntimeStateRecord:
        """Return the latest immutable workflow snapshot."""

        with self._lock:
            return self._checkpoints.latest(workflow_id).snapshot

    def checkpoint_history(
        self,
        workflow_id: str,
    ) -> tuple[RuntimeCheckpoint, ...]:
        """Return immutable checkpoint evidence for one workflow."""

        with self._lock:
            return self._checkpoints.history(workflow_id)

    def replay(self, workflow_id: str) -> ReplayResult:
        """Replay and verify one workflow's checkpoint history."""

        with self._lock:
            return replay_checkpoint_history(self._checkpoints.history(workflow_id))

    def apply_transition(
        self,
        workflow_id: str,
        *,
        expected_state_version: int,
        command: TransitionCommand,
        event_id: str,
        timestamp: Timestamp,
        context: RuntimeTransitionContext | None = None,
        duration_ms: float | None = None,
    ) -> RuntimeStepResult:
        """Apply one authorized transition and record its evidence."""

        with self._lock:
            current = self._checkpoints.latest(workflow_id).snapshot
            self._ensure_expected_version(
                current,
                expected_state_version,
            )

            stop = evaluate_pre_transition_stop(
                current,
                self._limits,
                timestamp,
            )

            if stop.should_stop:
                self._raise_stop(
                    current,
                    stop,
                    event_id=event_id,
                    timestamp=timestamp,
                    duration_ms=duration_ms,
                )

            transition = resolve_transition(current.state, command)
            updates = (
                context.model_dump(
                    mode="python",
                    exclude_unset=True,
                )
                if context is not None
                else {}
            )
            next_values = {
                **current.model_dump(mode="python"),
                **updates,
                "state": transition.target,
                "state_version": current.state_version + 1,
                "step_count": current.step_count + 1,
                "reason_codes": (transition.reason_code,),
                "updated_at": timestamp,
            }
            next_snapshot = RuntimeStateRecord.model_validate(next_values)
            trace_event = build_transition_trace_event(
                before=current,
                after=next_snapshot,
                command=command,
                event_id=event_id,
                timestamp=timestamp,
                duration_ms=duration_ms,
            )
            checkpoint = self._checkpoints.append(
                next_snapshot,
                expected_previous_version=current.state_version,
                created_at=timestamp,
            )

            return RuntimeStepResult(
                command=command,
                snapshot=next_snapshot,
                checkpoint=checkpoint,
                trace_event=trace_event,
            )

    def schedule_retry(
        self,
        workflow_id: str,
        *,
        expected_state_version: int,
        retry_request: RuntimeRetryRequest,
        event_id: str,
        timestamp: Timestamp,
        duration_ms: float | None = None,
    ) -> RuntimeStepResult:
        """Schedule one bounded retry for an explicit transient failure."""

        with self._lock:
            current = self._checkpoints.latest(workflow_id).snapshot
            self._ensure_expected_version(
                current,
                expected_state_version,
            )

            stop = evaluate_retry_stop(
                current,
                self._limits,
                timestamp,
            )

            if stop.should_stop:
                self._raise_stop(
                    current,
                    stop,
                    event_id=event_id,
                    timestamp=timestamp,
                    duration_ms=duration_ms,
                )

            next_values = {
                **current.model_dump(mode="python"),
                "state_version": current.state_version + 1,
                "step_count": current.step_count + 1,
                "retry_count": current.retry_count + 1,
                "stage_retry_counts": increment_stage_retry_counts(current),
                "reason_codes": (
                    RuntimeReasonCode.TRANSIENT_FAILURE_RECORDED,
                    retry_request.failure_reason_code,
                    RuntimeReasonCode.RETRY_SCHEDULED,
                ),
                "updated_at": timestamp,
            }
            next_snapshot = RuntimeStateRecord.model_validate(next_values)
            trace_event = build_retry_trace_event(
                before=current,
                after=next_snapshot,
                event_id=event_id,
                timestamp=timestamp,
                duration_ms=duration_ms,
            )
            checkpoint = self._checkpoints.append(
                next_snapshot,
                expected_previous_version=current.state_version,
                created_at=timestamp,
            )

            return RuntimeStepResult(
                command=TransitionCommand.RETRY_CURRENT_STAGE,
                snapshot=next_snapshot,
                checkpoint=checkpoint,
                trace_event=trace_event,
            )

    def _ensure_expected_version(
        self,
        current: RuntimeStateRecord,
        expected_state_version: int,
    ) -> None:
        """Reject stale callers before any state computation."""

        if current.state_version != expected_state_version:
            raise CheckpointVersionConflictError(
                workflow_id=current.workflow_id,
                expected_previous_version=expected_state_version,
                actual_previous_version=current.state_version,
                proposed_version=current.state_version + 1,
            )

    def _raise_stop(
        self,
        record: RuntimeStateRecord,
        decision: StopDecision,
        *,
        event_id: str,
        timestamp: Timestamp,
        duration_ms: float | None,
    ) -> None:
        """Raise a stop containing immutable CT-07 evidence."""

        trace_event = build_stop_trace_event(
            record=record,
            decision=decision,
            event_id=event_id,
            timestamp=timestamp,
            duration_ms=duration_ms,
        )

        raise RuntimeExecutionStoppedError(
            decision=decision,
            trace_event=trace_event,
        )
