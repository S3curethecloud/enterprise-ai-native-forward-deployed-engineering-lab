"""Tests for deterministic Phase 4 stop-condition evaluation."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.runtime import (
    RuntimeBudgetLimits,
    RuntimeReasonCode,
    RuntimeState,
    RuntimeStateRecord,
    StageRetryCount,
    StopCondition,
    StopDecision,
    StopDisposition,
    evaluate_pre_transition_stop,
    evaluate_retry_stop,
)

BASE_TIME = datetime(2026, 7, 19, 18, 30, tzinfo=UTC)


def build_record(**overrides: object) -> RuntimeStateRecord:
    """Build a valid active runtime record."""

    values: dict[str, object] = {
        "workflow_id": "workflow-stop-201",
        "request_id": "request-stop-201",
        "trace_id": "trace-stop-201",
        "state": RuntimeState.REQUEST_VALIDATING,
        "state_version": 1,
        "step_count": 1,
        "created_at": BASE_TIME,
        "updated_at": BASE_TIME,
    }
    values.update(overrides)

    return RuntimeStateRecord.model_validate(values)


def test_active_workflow_below_limits_may_continue() -> None:
    """A bounded nonterminal workflow receives a continue decision."""

    decision = evaluate_pre_transition_stop(
        build_record(),
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    assert not decision.should_stop
    assert decision.allows_continuation
    assert decision.disposition is StopDisposition.CONTINUE
    assert decision.condition is StopCondition.NONE
    assert decision.reason_code is None


@pytest.mark.parametrize(
    ("state", "disposition"),
    [
        (
            RuntimeState.COMPLETED_RECOMMENDATION,
            StopDisposition.COMPLETE_RECOMMENDATION,
        ),
        (
            RuntimeState.COMPLETED_ABSTENTION,
            StopDisposition.ABSTAIN,
        ),
        (
            RuntimeState.COMPLETED_DENIAL,
            StopDisposition.DENY,
        ),
        (
            RuntimeState.COMPLETED_FAILURE,
            StopDisposition.FAIL,
        ),
        (
            RuntimeState.COMPLETED_SECURITY_STOP,
            StopDisposition.SECURITY_STOP,
        ),
    ],
)
def test_terminal_states_remain_stopped(
    state: RuntimeState,
    disposition: StopDisposition,
) -> None:
    """Every terminal state maps to an explicit disposition."""

    record = build_record(
        state=state,
        reason_codes=(RuntimeReasonCode.SECURITY_CONTAINMENT,),
    )

    decision = evaluate_pre_transition_stop(
        record,
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    assert decision.should_stop
    assert not decision.allows_continuation
    assert decision.disposition is disposition
    assert decision.condition is StopCondition.TERMINAL_STATE
    assert decision.reason_code is RuntimeReasonCode.SECURITY_CONTAINMENT


def test_terminal_state_without_reason_uses_fallback() -> None:
    """Missing historical reason evidence produces a controlled code."""

    record = build_record(
        state=RuntimeState.COMPLETED_FAILURE,
        reason_codes=(),
    )

    decision = evaluate_pre_transition_stop(
        record,
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    assert decision.reason_code is RuntimeReasonCode.INVALID_TRANSITION


@pytest.mark.parametrize(
    "evaluated_at",
    [
        BASE_TIME,
        BASE_TIME + timedelta(seconds=1),
    ],
)
def test_expired_authorization_stops_coordination(
    evaluated_at: datetime,
) -> None:
    """Authorization is invalid at and after its expiry time."""

    record = build_record(
        state=RuntimeState.EVIDENCE_PENDING,
        state_version=4,
        step_count=4,
        policy_decision_id="policy-stop-201",
        authorization_expires_at=BASE_TIME,
    )

    decision = evaluate_pre_transition_stop(
        record,
        RuntimeBudgetLimits(),
        evaluated_at,
    )

    assert decision.should_stop
    assert decision.disposition is StopDisposition.DENY
    assert decision.condition is StopCondition.AUTHORIZATION_EXPIRED
    assert decision.reason_code is RuntimeReasonCode.AUTHORIZATION_EXPIRED


def test_unexpired_authorization_allows_continuation() -> None:
    """An unexpired external policy reference remains usable."""

    record = build_record(
        state=RuntimeState.EVIDENCE_PENDING,
        state_version=4,
        step_count=4,
        policy_decision_id="policy-stop-202",
        authorization_expires_at=BASE_TIME + timedelta(seconds=1),
    )

    decision = evaluate_pre_transition_stop(
        record,
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    assert decision.allows_continuation


def test_absent_authorization_does_not_create_authority() -> None:
    """A record without policy lineage remains non-authorizing."""

    record = build_record()

    decision = evaluate_pre_transition_stop(
        record,
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    assert record.policy_decision_id is None
    assert decision.allows_continuation


def test_exhausted_step_budget_stops_coordination() -> None:
    """No transition is allowed after step-budget exhaustion."""

    record = build_record(
        state_version=16,
        step_count=16,
    )

    decision = evaluate_pre_transition_stop(
        record,
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    assert decision.should_stop
    assert decision.disposition is StopDisposition.FAIL
    assert decision.condition is StopCondition.STEP_BUDGET_EXHAUSTED
    assert decision.reason_code is RuntimeReasonCode.STEP_BUDGET_EXHAUSTED


def test_terminal_state_has_highest_precedence() -> None:
    """Later checks cannot reclassify an existing terminal state."""

    record = build_record(
        state=RuntimeState.COMPLETED_DENIAL,
        state_version=16,
        step_count=16,
        policy_decision_id="policy-stop-203",
        authorization_expires_at=BASE_TIME,
        reason_codes=(RuntimeReasonCode.ACCESS_DENIED,),
    )

    decision = evaluate_pre_transition_stop(
        record,
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    assert decision.condition is StopCondition.TERMINAL_STATE
    assert decision.disposition is StopDisposition.DENY
    assert decision.reason_code is RuntimeReasonCode.ACCESS_DENIED


def test_expired_authorization_precedes_step_exhaustion() -> None:
    """Authorization expiry is classified before budget failure."""

    record = build_record(
        state=RuntimeState.EVIDENCE_PENDING,
        state_version=16,
        step_count=16,
        policy_decision_id="policy-stop-204",
        authorization_expires_at=BASE_TIME,
    )

    decision = evaluate_pre_transition_stop(
        record,
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    assert decision.condition is StopCondition.AUTHORIZATION_EXPIRED
    assert decision.disposition is StopDisposition.DENY


def test_retry_is_allowed_below_all_limits() -> None:
    """A retry proceeds only while all limits remain available."""

    decision = evaluate_retry_stop(
        build_record(),
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    assert decision.allows_continuation


def test_retry_preserves_pre_transition_stop() -> None:
    """Retry evaluation cannot bypass authorization expiry."""

    record = build_record(
        state=RuntimeState.EVIDENCE_PENDING,
        state_version=4,
        step_count=4,
        policy_decision_id="policy-stop-205",
        authorization_expires_at=BASE_TIME,
    )

    decision = evaluate_retry_stop(
        record,
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    assert decision.condition is StopCondition.AUTHORIZATION_EXPIRED
    assert decision.disposition is StopDisposition.DENY


def test_total_retry_exhaustion_stops_retry() -> None:
    """The workflow-wide retry budget is enforced."""

    record = build_record(
        state=RuntimeState.POLICY_EVALUATING,
        state_version=5,
        step_count=5,
        retry_count=2,
        stage_retry_counts=(
            StageRetryCount(
                state=RuntimeState.REQUEST_VALIDATING,
                retry_count=1,
            ),
            StageRetryCount(
                state=RuntimeState.IDENTITY_VALIDATING,
                retry_count=1,
            ),
        ),
    )

    decision = evaluate_retry_stop(
        record,
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    assert decision.should_stop
    assert decision.disposition is StopDisposition.FAIL
    assert decision.condition is StopCondition.RETRY_BUDGET_EXHAUSTED
    assert decision.reason_code is RuntimeReasonCode.RETRY_BUDGET_EXHAUSTED


def test_stage_retry_exhaustion_stops_retry() -> None:
    """A stage cannot exceed its independent retry budget."""

    record = build_record(
        state_version=3,
        step_count=3,
        retry_count=1,
        stage_retry_counts=(
            StageRetryCount(
                state=RuntimeState.REQUEST_VALIDATING,
                retry_count=1,
            ),
        ),
    )

    decision = evaluate_retry_stop(
        record,
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    assert decision.should_stop
    assert decision.disposition is StopDisposition.FAIL
    assert decision.condition is StopCondition.STAGE_RETRY_BUDGET_EXHAUSTED
    assert decision.reason_code is RuntimeReasonCode.STAGE_RETRY_BUDGET_EXHAUSTED


@pytest.mark.parametrize(
    "values",
    [
        {
            "should_stop": True,
            "disposition": StopDisposition.CONTINUE,
            "condition": StopCondition.TERMINAL_STATE,
            "reason_code": RuntimeReasonCode.INVALID_TRANSITION,
        },
        {
            "should_stop": True,
            "disposition": StopDisposition.FAIL,
            "condition": StopCondition.NONE,
            "reason_code": RuntimeReasonCode.INVALID_TRANSITION,
        },
        {
            "should_stop": True,
            "disposition": StopDisposition.FAIL,
            "condition": StopCondition.STEP_BUDGET_EXHAUSTED,
            "reason_code": None,
        },
        {
            "should_stop": False,
            "disposition": StopDisposition.FAIL,
            "condition": StopCondition.NONE,
            "reason_code": None,
        },
        {
            "should_stop": False,
            "disposition": StopDisposition.CONTINUE,
            "condition": StopCondition.TERMINAL_STATE,
            "reason_code": None,
        },
        {
            "should_stop": False,
            "disposition": StopDisposition.CONTINUE,
            "condition": StopCondition.NONE,
            "reason_code": RuntimeReasonCode.INVALID_TRANSITION,
        },
    ],
)
def test_stop_decision_rejects_inconsistent_fields(
    values: dict[str, object],
) -> None:
    """Contradictory stop-decision fields fail validation."""

    with pytest.raises(ValidationError):
        StopDecision.model_validate(
            {
                **values,
                "safe_message": "Controlled test decision.",
                "evaluated_at": BASE_TIME,
            }
        )


def test_stop_decision_is_immutable() -> None:
    """Accepted stop evidence cannot be mutated."""

    decision = evaluate_pre_transition_stop(
        build_record(),
        RuntimeBudgetLimits(),
        BASE_TIME,
    )

    with pytest.raises(ValidationError, match="frozen"):
        decision.should_stop = True
