"""CT-07 trace-event generation for the Phase 4 runtime."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

from incident_diagnostic_api.contracts import (
    LifecycleStage,
    TraceAttributes,
    TraceEvent,
    TraceEventName,
    TraceOutcome,
)
from incident_diagnostic_api.contracts.common import Timestamp
from incident_diagnostic_api.runtime.enums import (
    RuntimeReasonCode,
    RuntimeState,
    TransitionCommand,
)
from incident_diagnostic_api.runtime.models import RuntimeStateRecord
from incident_diagnostic_api.runtime.stops import (
    StopDecision,
    StopDisposition,
)
from incident_diagnostic_api.runtime.transitions import resolve_transition


@dataclass(frozen=True, slots=True)
class TraceGenerationError(Exception):
    """Controlled failure raised when trace evidence is inconsistent."""

    message: str
    reason_code: RuntimeReasonCode = RuntimeReasonCode.INVALID_TRANSITION

    def __str__(self) -> str:
        """Return a controlled trace-generation description."""

        return self.message


_STATE_STAGES: Final[dict[RuntimeState, LifecycleStage]] = {
    RuntimeState.RECEIVED: LifecycleStage.ADMISSION,
    RuntimeState.REQUEST_VALIDATING: LifecycleStage.ADMISSION,
    RuntimeState.IDENTITY_VALIDATING: LifecycleStage.IDENTITY,
    RuntimeState.POLICY_EVALUATING: LifecycleStage.POLICY,
    RuntimeState.EVIDENCE_PENDING: LifecycleStage.RETRIEVAL,
    RuntimeState.EVIDENCE_ASSESSING: (LifecycleStage.EVIDENCE_ASSESSMENT),
    RuntimeState.GENERATION_PENDING: LifecycleStage.GENERATION,
    RuntimeState.RESPONSE_VALIDATING: (LifecycleStage.RESPONSE_VALIDATION),
    RuntimeState.COMPLETED_RECOMMENDATION: (LifecycleStage.RESPONSE_DELIVERY),
    RuntimeState.COMPLETED_ABSTENTION: (LifecycleStage.RESPONSE_DELIVERY),
    RuntimeState.COMPLETED_DENIAL: LifecycleStage.RESPONSE_DELIVERY,
    RuntimeState.COMPLETED_FAILURE: LifecycleStage.OBSERVABILITY,
    RuntimeState.COMPLETED_SECURITY_STOP: (LifecycleStage.OBSERVABILITY),
}

STATE_STAGES: Final = MappingProxyType(_STATE_STAGES)


_TARGET_OUTCOMES: Final[dict[RuntimeState, TraceOutcome]] = {
    RuntimeState.RECEIVED: TraceOutcome.SUCCEEDED,
    RuntimeState.REQUEST_VALIDATING: TraceOutcome.SUCCEEDED,
    RuntimeState.IDENTITY_VALIDATING: TraceOutcome.SUCCEEDED,
    RuntimeState.POLICY_EVALUATING: TraceOutcome.SUCCEEDED,
    RuntimeState.EVIDENCE_PENDING: TraceOutcome.SUCCEEDED,
    RuntimeState.EVIDENCE_ASSESSING: TraceOutcome.SUCCEEDED,
    RuntimeState.GENERATION_PENDING: TraceOutcome.SUCCEEDED,
    RuntimeState.RESPONSE_VALIDATING: TraceOutcome.SUCCEEDED,
    RuntimeState.COMPLETED_RECOMMENDATION: TraceOutcome.SUCCEEDED,
    RuntimeState.COMPLETED_ABSTENTION: TraceOutcome.ABSTAINED,
    RuntimeState.COMPLETED_DENIAL: TraceOutcome.DENIED,
    RuntimeState.COMPLETED_FAILURE: TraceOutcome.FAILED,
    RuntimeState.COMPLETED_SECURITY_STOP: TraceOutcome.FAILED,
}

TARGET_OUTCOMES: Final = MappingProxyType(_TARGET_OUTCOMES)


_STOP_OUTCOMES: Final[dict[StopDisposition, TraceOutcome]] = {
    StopDisposition.COMPLETE_RECOMMENDATION: TraceOutcome.SUCCEEDED,
    StopDisposition.ABSTAIN: TraceOutcome.ABSTAINED,
    StopDisposition.DENY: TraceOutcome.DENIED,
    StopDisposition.FAIL: TraceOutcome.FAILED,
    StopDisposition.SECURITY_STOP: TraceOutcome.FAILED,
}


def _validate_common_lineage(
    before: RuntimeStateRecord,
    after: RuntimeStateRecord,
) -> None:
    """Validate immutable identity and monotonic counters."""

    if before.workflow_id != after.workflow_id:
        raise TraceGenerationError("workflow identity changed across runtime states")

    if before.request_id != after.request_id:
        raise TraceGenerationError("request identity changed across runtime states")

    if before.trace_id != after.trace_id:
        raise TraceGenerationError("trace identity changed across runtime states")

    if after.state_version != before.state_version + 1:
        raise TraceGenerationError("state version did not advance exactly once")

    if after.step_count != before.step_count + 1:
        raise TraceGenerationError("step count did not advance exactly once")


def _trace_attributes(
    record: RuntimeStateRecord,
) -> TraceAttributes:
    """Build allowlisted runtime-only CT-07 attributes."""

    retry_attempt = record.retry_count if record.retry_count > 0 else None

    return TraceAttributes(
        retry_attempt=retry_attempt,
        contract_name="runtime-state",
        contract_version_used="1.0",
    )


def build_transition_trace_event(
    *,
    before: RuntimeStateRecord,
    after: RuntimeStateRecord,
    command: TransitionCommand,
    event_id: str,
    timestamp: Timestamp,
    duration_ms: float | None = None,
) -> TraceEvent:
    """Build CT-07 evidence for one authorized state transition."""

    _validate_common_lineage(before, after)

    if command in {
        TransitionCommand.TRANSIENT_FAILURE,
        TransitionCommand.RETRY_CURRENT_STAGE,
    }:
        raise TraceGenerationError("retry commands require the retry trace builder")

    transition = resolve_transition(before.state, command)

    if transition.target is not after.state:
        raise TraceGenerationError("trace target does not match the authorized transition")

    if not after.reason_codes or after.reason_codes[-1] is not transition.reason_code:
        raise TraceGenerationError("trace reason does not match the authorized transition")

    outcome = TARGET_OUTCOMES[after.state]
    stage = STATE_STAGES[before.state]

    if (
        stage is LifecycleStage.POLICY
        and outcome is TraceOutcome.DENIED
        and after.policy_decision_id is None
    ):
        raise TraceGenerationError("policy denial trace requires policy decision lineage")

    return TraceEvent(
        event_id=event_id,
        trace_id=after.trace_id,
        request_id=after.request_id,
        event_name=TraceEventName.RUNTIME_TRANSITION_APPLIED,
        component="deterministic-runtime",
        stage=stage,
        outcome=outcome,
        policy_decision_id=after.policy_decision_id,
        duration_ms=duration_ms,
        input_reference=(f"runtime:{before.workflow_id}:v{before.state_version}"),
        output_reference=(f"runtime:{after.workflow_id}:v{after.state_version}"),
        reason_codes=after.reason_codes,
        timestamp=timestamp,
        attributes=_trace_attributes(after),
    )


def build_retry_trace_event(
    *,
    before: RuntimeStateRecord,
    after: RuntimeStateRecord,
    event_id: str,
    timestamp: Timestamp,
    duration_ms: float | None = None,
) -> TraceEvent:
    """Build CT-07 evidence for one scheduled same-state retry."""

    _validate_common_lineage(before, after)

    if after.state is not before.state:
        raise TraceGenerationError("retry trace requires the state to remain unchanged")

    if after.retry_count != before.retry_count + 1:
        raise TraceGenerationError("retry trace requires one additional retry")

    if after.retry_count_for(after.state) != before.retry_count_for(before.state) + 1:
        raise TraceGenerationError("retry trace requires one additional stage retry")

    if not after.reason_codes or after.reason_codes[-1] is not RuntimeReasonCode.RETRY_SCHEDULED:
        raise TraceGenerationError("retry trace requires RETRY_SCHEDULED evidence")

    return TraceEvent(
        event_id=event_id,
        trace_id=after.trace_id,
        request_id=after.request_id,
        event_name=TraceEventName.RUNTIME_RETRY_SCHEDULED,
        component="deterministic-runtime",
        stage=STATE_STAGES[before.state],
        outcome=TraceOutcome.STARTED,
        policy_decision_id=after.policy_decision_id,
        duration_ms=duration_ms,
        input_reference=(f"runtime:{before.workflow_id}:v{before.state_version}"),
        output_reference=(f"runtime:{after.workflow_id}:v{after.state_version}"),
        reason_codes=after.reason_codes,
        timestamp=timestamp,
        attributes=_trace_attributes(after),
    )


def build_stop_trace_event(
    *,
    record: RuntimeStateRecord,
    decision: StopDecision,
    event_id: str,
    timestamp: Timestamp,
    duration_ms: float | None = None,
) -> TraceEvent:
    """Build CT-07 evidence for one enforced deterministic stop."""

    if not decision.should_stop:
        raise TraceGenerationError("a continuation decision cannot produce a stop trace")

    if decision.disposition is StopDisposition.CONTINUE:
        raise TraceGenerationError("a stop trace cannot use the continue disposition")

    if decision.reason_code is None:
        raise TraceGenerationError("a stop trace requires a reason code")

    outcome = _STOP_OUTCOMES[decision.disposition]
    stage = STATE_STAGES[record.state]

    if (
        stage is LifecycleStage.POLICY
        and outcome is TraceOutcome.DENIED
        and record.policy_decision_id is None
    ):
        raise TraceGenerationError("policy denial trace requires policy decision lineage")

    return TraceEvent(
        event_id=event_id,
        trace_id=record.trace_id,
        request_id=record.request_id,
        event_name=TraceEventName.RUNTIME_STOP_ENFORCED,
        component="deterministic-runtime",
        stage=stage,
        outcome=outcome,
        policy_decision_id=record.policy_decision_id,
        duration_ms=duration_ms,
        input_reference=(f"runtime:{record.workflow_id}:v{record.state_version}"),
        output_reference=None,
        reason_codes=(decision.reason_code,),
        timestamp=timestamp,
        attributes=_trace_attributes(record),
    )


def build_genesis_trace_event(
    *,
    record: RuntimeStateRecord,
    event_id: str,
    timestamp: Timestamp,
) -> TraceEvent:
    """Build CT-07 evidence for creation of a bounded workflow."""

    if record.state is not RuntimeState.RECEIVED:
        raise TraceGenerationError("genesis trace requires the RECEIVED state")

    if record.state_version != 0 or record.step_count != 0 or record.retry_count != 0:
        raise TraceGenerationError("genesis trace requires zero runtime counters")

    if not record.reason_codes or record.reason_codes[-1] is not RuntimeReasonCode.RUNTIME_CREATED:
        raise TraceGenerationError("genesis trace requires RUNTIME_CREATED evidence")

    return TraceEvent(
        event_id=event_id,
        trace_id=record.trace_id,
        request_id=record.request_id,
        event_name=TraceEventName.REQUEST_RECEIVED,
        component="deterministic-runtime",
        stage=LifecycleStage.ADMISSION,
        outcome=TraceOutcome.STARTED,
        policy_decision_id=None,
        duration_ms=None,
        input_reference=None,
        output_reference=(f"runtime:{record.workflow_id}:v{record.state_version}"),
        reason_codes=record.reason_codes,
        timestamp=timestamp,
        attributes=_trace_attributes(record),
    )
