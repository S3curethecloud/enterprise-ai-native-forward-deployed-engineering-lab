"""Tests for the deterministic Phase 4 orchestration engine."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.contracts import (
    TraceEventName,
    TraceOutcome,
)
from incident_diagnostic_api.runtime import (
    CheckpointNotFoundError,
    CheckpointVersionConflictError,
    DeterministicRuntimeEngine,
    FailureClassification,
    InvalidTransitionError,
    RuntimeBudgetLimits,
    RuntimeExecutionStoppedError,
    RuntimeReasonCode,
    RuntimeRetryRequest,
    RuntimeState,
    RuntimeStateRecord,
    RuntimeTransitionContext,
    TransitionCommand,
)

BASE_TIME = datetime(2026, 7, 19, 18, 30, tzinfo=UTC)


def build_initial(
    workflow_id: str = "workflow-engine-301",
) -> RuntimeStateRecord:
    """Build a valid engine genesis snapshot."""

    return RuntimeStateRecord(
        workflow_id=workflow_id,
        request_id=f"request-{workflow_id}",
        trace_id=f"trace-{workflow_id}",
        created_at=BASE_TIME,
        updated_at=BASE_TIME,
    )


def start_engine(
    *,
    workflow_id: str = "workflow-engine-301",
    limits: RuntimeBudgetLimits | None = None,
) -> tuple[
    DeterministicRuntimeEngine,
    RuntimeStateRecord,
]:
    """Create an engine and its genesis workflow."""

    engine = DeterministicRuntimeEngine(limits=limits)
    initial = build_initial(workflow_id)
    engine.start(
        initial,
        event_id=f"event-{workflow_id}-000",
        timestamp=BASE_TIME,
    )

    return engine, initial


def test_start_creates_genesis_evidence() -> None:
    """Workflow creation records a checkpoint and CT-07 event."""

    engine = DeterministicRuntimeEngine()
    initial = build_initial()

    result = engine.start(
        initial,
        event_id="event-engine-start",
        timestamp=BASE_TIME,
    )

    assert result.snapshot == initial
    assert result.checkpoint.sequence == 0
    assert result.checkpoint.state_version == 0
    assert result.trace_event.event_name is (TraceEventName.REQUEST_RECEIVED)
    assert result.trace_event.outcome is TraceOutcome.STARTED
    assert engine.current(initial.workflow_id) == initial
    assert engine.checkpoint_history(initial.workflow_id) == (result.checkpoint,)


def test_duplicate_workflow_start_fails_closed() -> None:
    """An existing workflow cannot receive a second genesis."""

    engine, initial = start_engine()

    with pytest.raises(CheckpointVersionConflictError):
        engine.start(
            initial,
            event_id="event-duplicate-start",
            timestamp=BASE_TIME,
        )

    assert len(engine.checkpoint_history(initial.workflow_id)) == 1


def test_unknown_current_workflow_fails_closed() -> None:
    """Reading an unknown workflow raises a controlled exception."""

    engine = DeterministicRuntimeEngine()

    with pytest.raises(CheckpointNotFoundError):
        engine.current("unknown-workflow")


def test_authorized_transition_records_all_evidence() -> None:
    """One accepted command returns state, checkpoint, and trace."""

    engine, initial = start_engine()

    result = engine.apply_transition(
        initial.workflow_id,
        expected_state_version=0,
        command=TransitionCommand.BEGIN_REQUEST_VALIDATION,
        event_id="event-transition-301",
        timestamp=BASE_TIME + timedelta(seconds=1),
        duration_ms=1.25,
    )

    assert result.command is (TransitionCommand.BEGIN_REQUEST_VALIDATION)
    assert result.snapshot.state is RuntimeState.REQUEST_VALIDATING
    assert result.snapshot.state_version == 1
    assert result.snapshot.step_count == 1
    assert result.checkpoint.sequence == 1
    assert result.trace_event.event_name is (TraceEventName.RUNTIME_TRANSITION_APPLIED)
    assert result.trace_event.duration_ms == 1.25
    assert engine.current(initial.workflow_id) == result.snapshot


def test_invalid_transition_does_not_create_checkpoint() -> None:
    """Rejected commands leave checkpoint history unchanged."""

    engine, initial = start_engine()

    with pytest.raises(InvalidTransitionError):
        engine.apply_transition(
            initial.workflow_id,
            expected_state_version=0,
            command=TransitionCommand.RESPONSE_VALIDATED,
            event_id="event-invalid-transition",
            timestamp=BASE_TIME + timedelta(seconds=1),
        )

    assert len(engine.checkpoint_history(initial.workflow_id)) == 1
    assert engine.current(initial.workflow_id).state is (RuntimeState.RECEIVED)


def test_stale_transition_writer_is_rejected() -> None:
    """Optimistic state versions reject stale callers."""

    engine, initial = start_engine()
    engine.apply_transition(
        initial.workflow_id,
        expected_state_version=0,
        command=TransitionCommand.BEGIN_REQUEST_VALIDATION,
        event_id="event-current-writer",
        timestamp=BASE_TIME + timedelta(seconds=1),
    )

    with pytest.raises(CheckpointVersionConflictError) as captured:
        engine.apply_transition(
            initial.workflow_id,
            expected_state_version=0,
            command=TransitionCommand.REQUEST_VALIDATED,
            event_id="event-stale-writer",
            timestamp=BASE_TIME + timedelta(seconds=2),
        )

    assert captured.value.actual_previous_version == 1
    assert len(engine.checkpoint_history(initial.workflow_id)) == 2


def test_transition_context_records_policy_lineage() -> None:
    """Typed context carries external policy evidence without creating it."""

    engine, initial = start_engine()
    validating = engine.apply_transition(
        initial.workflow_id,
        expected_state_version=0,
        command=TransitionCommand.BEGIN_REQUEST_VALIDATION,
        event_id="event-context-001",
        timestamp=BASE_TIME + timedelta(seconds=1),
    )
    identity = engine.apply_transition(
        initial.workflow_id,
        expected_state_version=validating.snapshot.state_version,
        command=TransitionCommand.REQUEST_VALIDATED,
        event_id="event-context-002",
        timestamp=BASE_TIME + timedelta(seconds=2),
    )
    policy = engine.apply_transition(
        initial.workflow_id,
        expected_state_version=identity.snapshot.state_version,
        command=TransitionCommand.IDENTITY_VALIDATED,
        event_id="event-context-003",
        timestamp=BASE_TIME + timedelta(seconds=3),
    )
    allowed = engine.apply_transition(
        initial.workflow_id,
        expected_state_version=policy.snapshot.state_version,
        command=TransitionCommand.POLICY_ALLOWED,
        event_id="event-context-004",
        timestamp=BASE_TIME + timedelta(seconds=4),
        context=RuntimeTransitionContext(
            policy_decision_id="policy-context-301",
            authorization_expires_at=(BASE_TIME + timedelta(minutes=5)),
            evidence_reference="evidence-request-301",
        ),
    )

    assert allowed.snapshot.state is RuntimeState.EVIDENCE_PENDING
    assert allowed.snapshot.policy_decision_id == "policy-context-301"
    assert allowed.snapshot.evidence_reference == ("evidence-request-301")
    assert allowed.trace_event.policy_decision_id == ("policy-context-301")


def test_unspecified_context_fields_preserve_existing_lineage() -> None:
    """A later empty context does not erase policy evidence."""

    engine, initial = start_engine()
    steps = [
        TransitionCommand.BEGIN_REQUEST_VALIDATION,
        TransitionCommand.REQUEST_VALIDATED,
        TransitionCommand.IDENTITY_VALIDATED,
    ]
    version = 0

    for index, command in enumerate(steps, start=1):
        result = engine.apply_transition(
            initial.workflow_id,
            expected_state_version=version,
            command=command,
            event_id=f"event-preserve-{index}",
            timestamp=BASE_TIME + timedelta(seconds=index),
        )
        version = result.snapshot.state_version

    allowed = engine.apply_transition(
        initial.workflow_id,
        expected_state_version=version,
        command=TransitionCommand.POLICY_ALLOWED,
        event_id="event-preserve-policy",
        timestamp=BASE_TIME + timedelta(seconds=4),
        context=RuntimeTransitionContext(
            policy_decision_id="policy-preserve-301",
        ),
    )
    evidence = engine.apply_transition(
        initial.workflow_id,
        expected_state_version=allowed.snapshot.state_version,
        command=TransitionCommand.EVIDENCE_AVAILABLE,
        event_id="event-preserve-evidence",
        timestamp=BASE_TIME + timedelta(seconds=5),
        context=RuntimeTransitionContext(),
    )

    assert evidence.snapshot.policy_decision_id == ("policy-preserve-301")


def test_full_recommendation_path_replays() -> None:
    """The bounded synthetic path reaches recommendation and replays."""

    engine, initial = start_engine()
    commands = [
        TransitionCommand.BEGIN_REQUEST_VALIDATION,
        TransitionCommand.REQUEST_VALIDATED,
        TransitionCommand.IDENTITY_VALIDATED,
        TransitionCommand.POLICY_ALLOWED,
        TransitionCommand.EVIDENCE_AVAILABLE,
        TransitionCommand.EVIDENCE_SUFFICIENT,
        TransitionCommand.GENERATION_COMPLETED,
        TransitionCommand.RESPONSE_VALIDATED,
    ]
    version = 0

    for index, command in enumerate(commands, start=1):
        context = None

        if command is TransitionCommand.POLICY_ALLOWED:
            context = RuntimeTransitionContext(
                policy_decision_id="policy-happy-path-301",
                authorization_expires_at=(BASE_TIME + timedelta(minutes=5)),
            )

        result = engine.apply_transition(
            initial.workflow_id,
            expected_state_version=version,
            command=command,
            event_id=f"event-happy-{index:03d}",
            timestamp=BASE_TIME + timedelta(seconds=index),
            context=context,
        )
        version = result.snapshot.state_version

    final = engine.current(initial.workflow_id)
    replay = engine.replay(initial.workflow_id)

    assert final.state is RuntimeState.COMPLETED_RECOMMENDATION
    assert final.state_version == 8
    assert len(engine.checkpoint_history(initial.workflow_id)) == 9
    assert replay.verified
    assert replay.final_state is (RuntimeState.COMPLETED_RECOMMENDATION)


@pytest.mark.parametrize(
    "classification",
    [
        FailureClassification.PERMANENT,
        FailureClassification.DENIAL,
        FailureClassification.ABSTENTION,
        FailureClassification.SECURITY,
    ],
)
def test_only_transient_failures_are_retryable(
    classification: FailureClassification,
) -> None:
    """Retry requests reject every nontransient classification."""

    with pytest.raises(
        ValidationError,
        match="only transient failures",
    ):
        RuntimeRetryRequest(
            failure_classification=classification,
            failure_reason_code="DEPENDENCY_FAILURE",
        )


def test_transient_retry_records_counters_trace_and_replay() -> None:
    """One transient retry produces complete deterministic evidence."""

    engine, initial = start_engine()
    validating = engine.apply_transition(
        initial.workflow_id,
        expected_state_version=0,
        command=TransitionCommand.BEGIN_REQUEST_VALIDATION,
        event_id="event-retry-transition",
        timestamp=BASE_TIME + timedelta(seconds=1),
    )

    retried = engine.schedule_retry(
        initial.workflow_id,
        expected_state_version=validating.snapshot.state_version,
        retry_request=RuntimeRetryRequest(
            failure_classification=FailureClassification.TRANSIENT,
            failure_reason_code="DEPENDENCY_TIMEOUT",
        ),
        event_id="event-retry-scheduled",
        timestamp=BASE_TIME + timedelta(seconds=2),
    )

    assert retried.command is TransitionCommand.RETRY_CURRENT_STAGE
    assert retried.snapshot.state is RuntimeState.REQUEST_VALIDATING
    assert retried.snapshot.retry_count == 1
    assert retried.snapshot.retry_count_for(RuntimeState.REQUEST_VALIDATING) == 1
    assert retried.trace_event.event_name is (TraceEventName.RUNTIME_RETRY_SCHEDULED)
    assert engine.replay(initial.workflow_id).verified


def test_stage_retry_exhaustion_emits_stop_without_checkpoint() -> None:
    """A second same-stage retry fails closed with CT-07 stop evidence."""

    engine, initial = start_engine()
    validating = engine.apply_transition(
        initial.workflow_id,
        expected_state_version=0,
        command=TransitionCommand.BEGIN_REQUEST_VALIDATION,
        event_id="event-stage-limit-001",
        timestamp=BASE_TIME + timedelta(seconds=1),
    )
    first_retry = engine.schedule_retry(
        initial.workflow_id,
        expected_state_version=validating.snapshot.state_version,
        retry_request=RuntimeRetryRequest(
            failure_classification=FailureClassification.TRANSIENT,
            failure_reason_code="DEPENDENCY_TIMEOUT",
        ),
        event_id="event-stage-limit-002",
        timestamp=BASE_TIME + timedelta(seconds=2),
    )
    checkpoint_count = len(engine.checkpoint_history(initial.workflow_id))

    with pytest.raises(RuntimeExecutionStoppedError) as captured:
        engine.schedule_retry(
            initial.workflow_id,
            expected_state_version=(first_retry.snapshot.state_version),
            retry_request=RuntimeRetryRequest(
                failure_classification=(FailureClassification.TRANSIENT),
                failure_reason_code="DEPENDENCY_TIMEOUT",
            ),
            event_id="event-stage-limit-003",
            timestamp=BASE_TIME + timedelta(seconds=3),
        )

    error = captured.value

    assert error.decision.reason_code is (RuntimeReasonCode.STAGE_RETRY_BUDGET_EXHAUSTED)
    assert error.trace_event.event_name is (TraceEventName.RUNTIME_STOP_ENFORCED)
    assert len(engine.checkpoint_history(initial.workflow_id)) == (checkpoint_count)


def test_step_exhaustion_emits_stop_without_mutation() -> None:
    """A step-budget stop leaves the latest checkpoint unchanged."""

    engine, initial = start_engine(limits=RuntimeBudgetLimits(max_steps=1))
    validating = engine.apply_transition(
        initial.workflow_id,
        expected_state_version=0,
        command=TransitionCommand.BEGIN_REQUEST_VALIDATION,
        event_id="event-step-limit-001",
        timestamp=BASE_TIME + timedelta(seconds=1),
    )

    with pytest.raises(RuntimeExecutionStoppedError) as captured:
        engine.apply_transition(
            initial.workflow_id,
            expected_state_version=validating.snapshot.state_version,
            command=TransitionCommand.REQUEST_VALIDATED,
            event_id="event-step-limit-002",
            timestamp=BASE_TIME + timedelta(seconds=2),
        )

    assert captured.value.decision.reason_code is (RuntimeReasonCode.STEP_BUDGET_EXHAUSTED)
    assert engine.current(initial.workflow_id) == validating.snapshot
    assert len(engine.checkpoint_history(initial.workflow_id)) == 2


def test_terminal_workflow_cannot_restart() -> None:
    """A terminal recommendation remains permanently stopped."""

    engine, initial = start_engine()
    commands = [
        TransitionCommand.BEGIN_REQUEST_VALIDATION,
        TransitionCommand.REQUEST_VALIDATED,
        TransitionCommand.IDENTITY_VALIDATED,
        TransitionCommand.POLICY_ALLOWED,
        TransitionCommand.EVIDENCE_AVAILABLE,
        TransitionCommand.EVIDENCE_SUFFICIENT,
        TransitionCommand.GENERATION_COMPLETED,
        TransitionCommand.RESPONSE_VALIDATED,
    ]
    version = 0

    for index, command in enumerate(commands, start=1):
        context = (
            RuntimeTransitionContext(policy_decision_id="policy-terminal-301")
            if command is TransitionCommand.POLICY_ALLOWED
            else None
        )
        result = engine.apply_transition(
            initial.workflow_id,
            expected_state_version=version,
            command=command,
            event_id=f"event-terminal-{index}",
            timestamp=BASE_TIME + timedelta(seconds=index),
            context=context,
        )
        version = result.snapshot.state_version

    with pytest.raises(RuntimeExecutionStoppedError) as captured:
        engine.apply_transition(
            initial.workflow_id,
            expected_state_version=version,
            command=TransitionCommand.BEGIN_REQUEST_VALIDATION,
            event_id="event-terminal-restart",
            timestamp=BASE_TIME + timedelta(seconds=9),
        )

    assert captured.value.decision.condition.value == "terminal_state"
    assert engine.current(initial.workflow_id).state is (RuntimeState.COMPLETED_RECOMMENDATION)


def test_engine_exposes_no_external_execution_methods() -> None:
    """Phase 4 engine has no model, retrieval, tool, or shell method."""

    public_names = {name for name in dir(DeterministicRuntimeEngine) if not name.startswith("_")}

    prohibited = {
        "call_model",
        "retrieve_enterprise_data",
        "execute_tool",
        "execute_shell",
        "mutate_infrastructure",
        "deploy_to_cloud",
    }

    assert public_names.isdisjoint(prohibited)
