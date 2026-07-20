"""Tests for Phase 4 CT-07 runtime trace generation."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.contracts import (
    LifecycleStage,
    TraceEventName,
    TraceOutcome,
)
from incident_diagnostic_api.runtime import (
    STATE_STAGES,
    TARGET_OUTCOMES,
    TRANSITIONS,
    RuntimeBudgetLimits,
    RuntimeReasonCode,
    RuntimeState,
    RuntimeStateRecord,
    StageRetryCount,
    TraceGenerationError,
    TransitionCommand,
    TransitionDefinition,
    build_retry_trace_event,
    build_stop_trace_event,
    build_transition_trace_event,
    evaluate_pre_transition_stop,
)

BASE_TIME = datetime(2026, 7, 19, 18, 30, tzinfo=UTC)


def build_before(state: RuntimeState) -> RuntimeStateRecord:
    """Build a valid source snapshot for one transition."""

    initial = state is RuntimeState.RECEIVED

    return RuntimeStateRecord(
        workflow_id="workflow-trace-201",
        request_id="request-trace-201",
        trace_id="trace-trace-201",
        state=state,
        state_version=0 if initial else 1,
        step_count=0 if initial else 1,
        policy_decision_id=(
            "policy-trace-201" if state is RuntimeState.POLICY_EVALUATING else None
        ),
        created_at=BASE_TIME,
        updated_at=BASE_TIME,
    )


def build_after(
    before: RuntimeStateRecord,
    transition: TransitionDefinition,
    **overrides: object,
) -> RuntimeStateRecord:
    """Build the matching target snapshot for a transition."""

    values: dict[str, object] = {
        **before.model_dump(mode="python"),
        "state": transition.target,
        "state_version": before.state_version + 1,
        "step_count": before.step_count + 1,
        "reason_codes": (transition.reason_code,),
        "updated_at": BASE_TIME + timedelta(seconds=1),
    }
    values.update(overrides)

    return RuntimeStateRecord.model_validate(values)


@pytest.mark.parametrize(
    "transition",
    tuple(TRANSITIONS.values()),
)
def test_every_authorized_transition_generates_ct07(
    transition: TransitionDefinition,
) -> None:
    """Every authoritative transition creates typed trace evidence."""

    before = build_before(transition.source)
    after = build_after(before, transition)

    event = build_transition_trace_event(
        before=before,
        after=after,
        command=transition.command,
        event_id=(f"event-{transition.source.value}-{transition.command.value}"),
        timestamp=BASE_TIME + timedelta(seconds=1),
        duration_ms=1.5,
    )

    assert event.event_name is (TraceEventName.RUNTIME_TRANSITION_APPLIED)
    assert event.component == "deterministic-runtime"
    assert event.stage is STATE_STAGES[transition.source]
    assert event.outcome is TARGET_OUTCOMES[transition.target]
    assert event.reason_codes == (transition.reason_code.value,)
    assert event.trace_id == after.trace_id
    assert event.request_id == after.request_id
    assert event.duration_ms == 1.5


def test_transition_trace_contains_state_references() -> None:
    """Trace references identify input and output state versions."""

    transition = TRANSITIONS[
        (
            RuntimeState.RECEIVED,
            TransitionCommand.BEGIN_REQUEST_VALIDATION,
        )
    ]
    before = build_before(transition.source)
    after = build_after(before, transition)

    event = build_transition_trace_event(
        before=before,
        after=after,
        command=transition.command,
        event_id="event-reference-201",
        timestamp=BASE_TIME,
    )

    assert event.input_reference == ("runtime:workflow-trace-201:v0")
    assert event.output_reference == ("runtime:workflow-trace-201:v1")
    assert event.attributes.contract_name == "runtime-state"
    assert event.attributes.contract_version_used == "1.0"


@pytest.mark.parametrize(
    "field",
    ["workflow_id", "request_id", "trace_id"],
)
def test_transition_trace_rejects_identity_change(
    field: str,
) -> None:
    """Trace generation cannot hide identity-lineage changes."""

    transition = TRANSITIONS[
        (
            RuntimeState.RECEIVED,
            TransitionCommand.BEGIN_REQUEST_VALIDATION,
        )
    ]
    before = build_before(transition.source)
    after = build_after(
        before,
        transition,
        **{field: f"changed-{field}"},
    )

    with pytest.raises(TraceGenerationError):
        build_transition_trace_event(
            before=before,
            after=after,
            command=transition.command,
            event_id="event-identity-change",
            timestamp=BASE_TIME,
        )


@pytest.mark.parametrize(
    "field",
    ["state_version", "step_count"],
)
def test_transition_trace_rejects_counter_jump(
    field: str,
) -> None:
    """Trace evidence requires exactly one version and step advance."""

    transition = TRANSITIONS[
        (
            RuntimeState.RECEIVED,
            TransitionCommand.BEGIN_REQUEST_VALIDATION,
        )
    ]
    before = build_before(transition.source)
    after = build_after(
        before,
        transition,
        **{field: 2},
    )

    with pytest.raises(TraceGenerationError):
        build_transition_trace_event(
            before=before,
            after=after,
            command=transition.command,
            event_id="event-counter-jump",
            timestamp=BASE_TIME,
        )


def test_transition_trace_rejects_wrong_target() -> None:
    """Command and target state must match the transition table."""

    before = build_before(RuntimeState.REQUEST_VALIDATING)
    rejection = TRANSITIONS[
        (
            RuntimeState.REQUEST_VALIDATING,
            TransitionCommand.REQUEST_REJECTED,
        )
    ]
    after = build_after(before, rejection)

    with pytest.raises(
        TraceGenerationError,
        match="target does not match",
    ):
        build_transition_trace_event(
            before=before,
            after=after,
            command=TransitionCommand.REQUEST_VALIDATED,
            event_id="event-wrong-target",
            timestamp=BASE_TIME,
        )


def test_transition_trace_rejects_wrong_reason() -> None:
    """Transition evidence must carry its authoritative reason."""

    transition = TRANSITIONS[
        (
            RuntimeState.RECEIVED,
            TransitionCommand.BEGIN_REQUEST_VALIDATION,
        )
    ]
    before = build_before(transition.source)
    after = build_after(
        before,
        transition,
        reason_codes=(RuntimeReasonCode.ACCESS_DENIED,),
    )

    with pytest.raises(
        TraceGenerationError,
        match="reason does not match",
    ):
        build_transition_trace_event(
            before=before,
            after=after,
            command=transition.command,
            event_id="event-wrong-reason",
            timestamp=BASE_TIME,
        )


@pytest.mark.parametrize(
    "command",
    [
        TransitionCommand.TRANSIENT_FAILURE,
        TransitionCommand.RETRY_CURRENT_STAGE,
    ],
)
def test_transition_builder_rejects_retry_commands(
    command: TransitionCommand,
) -> None:
    """Retry commands use the dedicated retry trace builder."""

    before = build_before(RuntimeState.REQUEST_VALIDATING)
    after = before.model_copy(
        update={
            "state_version": 2,
            "step_count": 2,
        }
    )

    with pytest.raises(
        TraceGenerationError,
        match="retry commands require",
    ):
        build_transition_trace_event(
            before=before,
            after=after,
            command=command,
            event_id="event-wrong-builder",
            timestamp=BASE_TIME,
        )


def test_policy_denial_requires_decision_lineage() -> None:
    """The runtime cannot fabricate policy-denial authority."""

    transition = TRANSITIONS[
        (
            RuntimeState.POLICY_EVALUATING,
            TransitionCommand.POLICY_DENIED,
        )
    ]
    before = RuntimeStateRecord(
        workflow_id="workflow-policy-denial",
        request_id="request-policy-denial",
        trace_id="trace-policy-denial",
        state=RuntimeState.POLICY_EVALUATING,
        state_version=3,
        step_count=3,
        created_at=BASE_TIME,
        updated_at=BASE_TIME,
    )
    after = build_after(before, transition)

    with pytest.raises(
        TraceGenerationError,
        match="requires policy decision lineage",
    ):
        build_transition_trace_event(
            before=before,
            after=after,
            command=transition.command,
            event_id="event-policy-denial",
            timestamp=BASE_TIME,
        )


def valid_retry_pair() -> tuple[
    RuntimeStateRecord,
    RuntimeStateRecord,
]:
    """Return valid before and after snapshots for one retry."""

    before = build_before(RuntimeState.REQUEST_VALIDATING)
    after = RuntimeStateRecord.model_validate(
        {
            **before.model_dump(mode="python"),
            "state_version": 2,
            "step_count": 2,
            "retry_count": 1,
            "stage_retry_counts": (
                StageRetryCount(
                    state=RuntimeState.REQUEST_VALIDATING,
                    retry_count=1,
                ),
            ),
            "reason_codes": (RuntimeReasonCode.RETRY_SCHEDULED,),
            "updated_at": BASE_TIME + timedelta(seconds=1),
        }
    )

    return before, after


def test_retry_trace_is_ct07_compliant() -> None:
    """A scheduled retry produces allowlisted CT-07 evidence."""

    before, after = valid_retry_pair()

    event = build_retry_trace_event(
        before=before,
        after=after,
        event_id="event-retry-201",
        timestamp=BASE_TIME,
    )

    assert event.event_name is (TraceEventName.RUNTIME_RETRY_SCHEDULED)
    assert event.stage is LifecycleStage.ADMISSION
    assert event.outcome is TraceOutcome.STARTED
    assert event.attributes.retry_attempt == 1
    assert event.reason_codes == ("RETRY_SCHEDULED",)


def test_retry_trace_rejects_state_change() -> None:
    """A retry cannot silently transition to another state."""

    before, after = valid_retry_pair()
    changed = after.model_copy(update={"state": RuntimeState.IDENTITY_VALIDATING})

    with pytest.raises(
        TraceGenerationError,
        match="state to remain unchanged",
    ):
        build_retry_trace_event(
            before=before,
            after=changed,
            event_id="event-retry-state-change",
            timestamp=BASE_TIME,
        )


@pytest.mark.parametrize(
    "updates",
    [
        {"retry_count": 0},
        {
            "stage_retry_counts": (
                StageRetryCount(
                    state=RuntimeState.IDENTITY_VALIDATING,
                    retry_count=1,
                ),
            )
        },
        {"reason_codes": (RuntimeReasonCode.TRANSIENT_FAILURE_RECORDED,)},
    ],
)
def test_retry_trace_rejects_inconsistent_evidence(
    updates: dict[str, object],
) -> None:
    """Retry counters and reasons must remain mutually consistent."""

    before, after = valid_retry_pair()
    invalid = after.model_copy(update=updates)

    with pytest.raises(TraceGenerationError):
        build_retry_trace_event(
            before=before,
            after=invalid,
            event_id="event-invalid-retry",
            timestamp=BASE_TIME,
        )


def test_stop_trace_is_ct07_compliant() -> None:
    """A step-budget stop produces immutable failure evidence."""

    record = RuntimeStateRecord(
        workflow_id="workflow-stop-trace",
        request_id="request-stop-trace",
        trace_id="trace-stop-trace",
        state=RuntimeState.REQUEST_VALIDATING,
        state_version=16,
        step_count=16,
        created_at=BASE_TIME,
        updated_at=BASE_TIME,
    )
    decision = evaluate_pre_transition_stop(
        record,
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    event = build_stop_trace_event(
        record=record,
        decision=decision,
        event_id="event-stop-201",
        timestamp=BASE_TIME,
    )

    assert event.event_name is TraceEventName.RUNTIME_STOP_ENFORCED
    assert event.outcome is TraceOutcome.FAILED
    assert event.stage is LifecycleStage.ADMISSION
    assert event.reason_codes == ("STEP_BUDGET_EXHAUSTED",)
    assert event.output_reference is None


def test_stop_builder_rejects_continue_decision() -> None:
    """A workflow allowed to continue cannot emit stop evidence."""

    record = build_before(RuntimeState.REQUEST_VALIDATING)
    decision = evaluate_pre_transition_stop(
        record,
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    with pytest.raises(
        TraceGenerationError,
        match="continuation decision",
    ):
        build_stop_trace_event(
            record=record,
            decision=decision,
            event_id="event-false-stop",
            timestamp=BASE_TIME,
        )


def test_negative_duration_remains_rejected_by_ct07() -> None:
    """Runtime trace generation preserves CT-07 duration controls."""

    transition = TRANSITIONS[
        (
            RuntimeState.RECEIVED,
            TransitionCommand.BEGIN_REQUEST_VALIDATION,
        )
    ]
    before = build_before(transition.source)
    after = build_after(before, transition)

    with pytest.raises(ValidationError):
        build_transition_trace_event(
            before=before,
            after=after,
            command=transition.command,
            event_id="event-negative-duration",
            timestamp=BASE_TIME,
            duration_ms=-0.01,
        )


def test_trace_mappings_cover_all_runtime_states() -> None:
    """Every runtime state has deterministic stage and outcome mappings."""

    assert set(STATE_STAGES) == set(RuntimeState)
    assert set(TARGET_OUTCOMES) == set(RuntimeState)
