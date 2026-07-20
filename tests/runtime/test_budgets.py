"""Tests for deterministic Phase 4 step and retry budgets."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.runtime import (
    RuntimeBudgetExceededError,
    RuntimeBudgetLimits,
    RuntimeReasonCode,
    RuntimeState,
    RuntimeStateRecord,
    StageRetryCount,
    ensure_retry_budget,
    ensure_step_budget,
    increment_stage_retry_counts,
)

BASE_TIME = datetime(2026, 7, 19, 18, 30, tzinfo=UTC)


def build_active_record(**overrides: object) -> RuntimeStateRecord:
    """Build a valid active runtime snapshot."""

    values: dict[str, object] = {
        "workflow_id": "workflow-budget-101",
        "request_id": "request-budget-101",
        "trace_id": "trace-budget-101",
        "state": RuntimeState.REQUEST_VALIDATING,
        "state_version": 1,
        "step_count": 1,
        "created_at": BASE_TIME,
        "updated_at": BASE_TIME,
    }
    values.update(overrides)

    return RuntimeStateRecord.model_validate(values)


def test_default_budget_limits_match_phase_4_design() -> None:
    """Default execution limits remain intentionally small."""

    limits = RuntimeBudgetLimits()

    assert limits.max_steps == 16
    assert limits.max_retries == 2
    assert limits.max_stage_retries == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("max_steps", 0),
        ("max_steps", 33),
        ("max_retries", -1),
        ("max_retries", 9),
        ("max_stage_retries", -1),
        ("max_stage_retries", 5),
    ],
)
def test_budget_limits_reject_out_of_range_values(
    field: str,
    value: int,
) -> None:
    """Configuration cannot silently exceed approved bounds."""

    with pytest.raises(ValidationError):
        RuntimeBudgetLimits.model_validate({field: value})


def test_stage_retry_limit_cannot_exceed_total_limit() -> None:
    """A per-stage allowance cannot exceed the workflow allowance."""

    with pytest.raises(
        ValidationError,
        match="max_stage_retries cannot exceed max_retries",
    ):
        RuntimeBudgetLimits(
            max_retries=1,
            max_stage_retries=2,
        )


def test_budget_limits_are_immutable() -> None:
    """Runtime code cannot expand accepted limits in place."""

    limits = RuntimeBudgetLimits()

    with pytest.raises(ValidationError, match="frozen"):
        limits.max_steps = 32


@pytest.mark.parametrize("step_count", [0, 1, 15])
def test_step_budget_allows_counts_below_limit(
    step_count: int,
) -> None:
    """Another step is available strictly below the maximum."""

    record = build_active_record(
        state_version=max(step_count, 1),
        step_count=step_count,
    )

    ensure_step_budget(record, RuntimeBudgetLimits(max_steps=16))


@pytest.mark.parametrize("step_count", [16, 17, 32])
def test_step_budget_fails_at_or_above_limit(
    step_count: int,
) -> None:
    """The runtime fails closed when no step remains."""

    record = build_active_record(
        state_version=step_count,
        step_count=step_count,
    )

    with pytest.raises(RuntimeBudgetExceededError) as captured:
        ensure_step_budget(
            record,
            RuntimeBudgetLimits(max_steps=16),
        )

    error = captured.value

    assert error.reason_code is RuntimeReasonCode.STEP_BUDGET_EXHAUSTED
    assert error.state is RuntimeState.REQUEST_VALIDATING
    assert error.current_count == step_count
    assert error.maximum_count == 16


@pytest.mark.parametrize(
    "terminal_state",
    [
        RuntimeState.COMPLETED_RECOMMENDATION,
        RuntimeState.COMPLETED_ABSTENTION,
        RuntimeState.COMPLETED_DENIAL,
        RuntimeState.COMPLETED_FAILURE,
        RuntimeState.COMPLETED_SECURITY_STOP,
    ],
)
def test_terminal_states_cannot_consume_steps(
    terminal_state: RuntimeState,
) -> None:
    """Terminal workflows cannot restart by consuming another step."""

    record = build_active_record(
        state=terminal_state,
    )

    with pytest.raises(RuntimeBudgetExceededError) as captured:
        ensure_step_budget(record, RuntimeBudgetLimits())

    assert captured.value.reason_code is RuntimeReasonCode.INVALID_TRANSITION


def test_retry_budget_allows_first_stage_retry() -> None:
    """The initial retry is permitted within all three limits."""

    record = build_active_record()

    ensure_retry_budget(record, RuntimeBudgetLimits())


def test_retry_budget_checks_step_limit_first() -> None:
    """A retry cannot bypass an exhausted step budget."""

    record = build_active_record(
        state_version=16,
        step_count=16,
    )

    with pytest.raises(RuntimeBudgetExceededError) as captured:
        ensure_retry_budget(record, RuntimeBudgetLimits())

    assert captured.value.reason_code is RuntimeReasonCode.STEP_BUDGET_EXHAUSTED


def test_total_retry_budget_fails_closed() -> None:
    """The workflow-wide retry count is independently bounded."""

    record = build_active_record(
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

    with pytest.raises(RuntimeBudgetExceededError) as captured:
        ensure_retry_budget(record, RuntimeBudgetLimits())

    error = captured.value

    assert error.reason_code is RuntimeReasonCode.RETRY_BUDGET_EXHAUSTED
    assert error.current_count == 2
    assert error.maximum_count == 2


def test_stage_retry_budget_fails_closed() -> None:
    """One stage cannot consume the remaining workflow retry budget."""

    record = build_active_record(
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

    with pytest.raises(RuntimeBudgetExceededError) as captured:
        ensure_retry_budget(record, RuntimeBudgetLimits())

    error = captured.value

    assert error.reason_code is RuntimeReasonCode.STAGE_RETRY_BUDGET_EXHAUSTED
    assert error.current_count == 1
    assert error.maximum_count == 1


def test_increment_adds_current_state_counter() -> None:
    """The first retry creates one immutable stage counter."""

    record = build_active_record()

    updated = increment_stage_retry_counts(record)

    assert updated == (
        StageRetryCount(
            state=RuntimeState.REQUEST_VALIDATING,
            retry_count=1,
        ),
    )
    assert record.stage_retry_counts == ()


def test_increment_updates_existing_state_counter() -> None:
    """A later retry increments the matching state only."""

    original = (
        StageRetryCount(
            state=RuntimeState.REQUEST_VALIDATING,
            retry_count=1,
        ),
    )
    record = build_active_record(
        state_version=3,
        step_count=3,
        retry_count=1,
        stage_retry_counts=original,
    )

    updated = increment_stage_retry_counts(record)

    assert updated == (
        StageRetryCount(
            state=RuntimeState.REQUEST_VALIDATING,
            retry_count=2,
        ),
    )
    assert record.stage_retry_counts == original


def test_increment_preserves_other_stage_counters() -> None:
    """Retry accounting remains attributable across workflow stages."""

    original = (
        StageRetryCount(
            state=RuntimeState.REQUEST_VALIDATING,
            retry_count=1,
        ),
    )
    record = build_active_record(
        state=RuntimeState.IDENTITY_VALIDATING,
        state_version=4,
        step_count=4,
        retry_count=1,
        stage_retry_counts=original,
    )

    updated = increment_stage_retry_counts(record)

    assert {item.state: item.retry_count for item in updated} == {
        RuntimeState.IDENTITY_VALIDATING: 1,
        RuntimeState.REQUEST_VALIDATING: 1,
    }
    assert record.stage_retry_counts == original


def test_budget_error_message_is_controlled() -> None:
    """Budget failures expose bounded counters without sensitive data."""

    record = build_active_record(
        state_version=16,
        step_count=16,
    )

    with pytest.raises(RuntimeBudgetExceededError) as captured:
        ensure_step_budget(record, RuntimeBudgetLimits())

    assert str(captured.value) == "step budget exhausted at 16 of 16"
