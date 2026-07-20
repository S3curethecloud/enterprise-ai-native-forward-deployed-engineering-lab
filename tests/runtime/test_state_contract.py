"""Tests for runtime enumerations and immutable state snapshots."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.runtime import (
    ACTIVE_STATES,
    INITIAL_STATES,
    STATE_TYPES,
    TERMINAL_STATES,
    RuntimeReasonCode,
    RuntimeState,
    RuntimeStateRecord,
    RuntimeStateType,
    StageRetryCount,
    is_terminal_state,
    state_type,
)

BASE_TIME = datetime(2026, 7, 19, 18, 30, tzinfo=UTC)


def build_record(**overrides: object) -> RuntimeStateRecord:
    """Build a valid runtime snapshot with explicit test overrides."""

    values: dict[str, object] = {
        "workflow_id": "workflow-101",
        "request_id": "request-101",
        "trace_id": "trace-101",
        "created_at": BASE_TIME,
        "updated_at": BASE_TIME,
    }
    values.update(overrides)

    return RuntimeStateRecord.model_validate(values)


def test_runtime_state_inventory_is_complete_and_disjoint() -> None:
    """Every state belongs to exactly one lifecycle classification."""

    assert len(RuntimeState) == 13
    assert len(INITIAL_STATES) == 1
    assert len(ACTIVE_STATES) == 7
    assert len(TERMINAL_STATES) == 5

    assert INITIAL_STATES.isdisjoint(ACTIVE_STATES)
    assert INITIAL_STATES.isdisjoint(TERMINAL_STATES)
    assert ACTIVE_STATES.isdisjoint(TERMINAL_STATES)

    assert set(RuntimeState) == INITIAL_STATES | ACTIVE_STATES | TERMINAL_STATES


@pytest.mark.parametrize(
    ("state", "expected_type"),
    [
        (RuntimeState.RECEIVED, RuntimeStateType.INITIAL),
        (RuntimeState.REQUEST_VALIDATING, RuntimeStateType.ACTIVE),
        (RuntimeState.IDENTITY_VALIDATING, RuntimeStateType.ACTIVE),
        (RuntimeState.POLICY_EVALUATING, RuntimeStateType.ACTIVE),
        (RuntimeState.EVIDENCE_PENDING, RuntimeStateType.ACTIVE),
        (RuntimeState.EVIDENCE_ASSESSING, RuntimeStateType.ACTIVE),
        (RuntimeState.GENERATION_PENDING, RuntimeStateType.ACTIVE),
        (RuntimeState.RESPONSE_VALIDATING, RuntimeStateType.ACTIVE),
        (
            RuntimeState.COMPLETED_RECOMMENDATION,
            RuntimeStateType.TERMINAL,
        ),
        (RuntimeState.COMPLETED_ABSTENTION, RuntimeStateType.TERMINAL),
        (RuntimeState.COMPLETED_DENIAL, RuntimeStateType.TERMINAL),
        (RuntimeState.COMPLETED_FAILURE, RuntimeStateType.TERMINAL),
        (
            RuntimeState.COMPLETED_SECURITY_STOP,
            RuntimeStateType.TERMINAL,
        ),
    ],
)
def test_every_runtime_state_has_expected_type(
    state: RuntimeState,
    expected_type: RuntimeStateType,
) -> None:
    """The classification map matches the approved state design."""

    assert state_type(state) is expected_type
    assert STATE_TYPES[state] is expected_type


@pytest.mark.parametrize("state", list(TERMINAL_STATES))
def test_terminal_state_helper_accepts_only_terminal_states(
    state: RuntimeState,
) -> None:
    """Terminal states are recognized as permanent workflow stops."""

    assert is_terminal_state(state)


@pytest.mark.parametrize(
    "state",
    list(INITIAL_STATES | ACTIVE_STATES),
)
def test_terminal_state_helper_rejects_nonterminal_states(
    state: RuntimeState,
) -> None:
    """Initial and active states remain nonterminal."""

    assert not is_terminal_state(state)


def test_received_record_has_fail_closed_defaults() -> None:
    """A new runtime snapshot begins without delegated authority."""

    record = build_record()

    assert record.state is RuntimeState.RECEIVED
    assert record.state_version == 0
    assert record.step_count == 0
    assert record.retry_count == 0
    assert record.stage_retry_counts == ()
    assert record.reason_codes == (RuntimeReasonCode.RUNTIME_CREATED,)
    assert record.policy_decision_id is None
    assert record.authorization_expires_at is None
    assert not record.terminal


def test_runtime_record_is_immutable() -> None:
    """Callers cannot mutate an accepted runtime snapshot."""

    record = build_record()

    with pytest.raises(ValidationError, match="frozen"):
        record.state = RuntimeState.REQUEST_VALIDATING


def test_extra_fields_are_rejected() -> None:
    """Unknown state fields cannot silently expand runtime authority."""

    with pytest.raises(ValidationError, match="Extra inputs"):
        build_record(unrestricted_tool_access=True)


def test_updated_time_cannot_precede_created_time() -> None:
    """Runtime chronology must remain internally consistent."""

    with pytest.raises(
        ValidationError,
        match="updated_at cannot precede created_at",
    ):
        build_record(updated_at=BASE_TIME - timedelta(seconds=1))


def test_retry_count_cannot_exceed_step_count() -> None:
    """A retry must always consume an already recorded step."""

    with pytest.raises(
        ValidationError,
        match="retry_count cannot exceed step_count",
    ):
        build_record(
            state=RuntimeState.REQUEST_VALIDATING,
            state_version=1,
            step_count=0,
            retry_count=1,
            stage_retry_counts=(
                StageRetryCount(
                    state=RuntimeState.REQUEST_VALIDATING,
                    retry_count=1,
                ),
            ),
        )


def test_stage_retry_counts_must_be_unique() -> None:
    """A state has one canonical retry counter in each snapshot."""

    duplicate = StageRetryCount(
        state=RuntimeState.REQUEST_VALIDATING,
        retry_count=1,
    )

    with pytest.raises(
        ValidationError,
        match="cannot contain duplicate states",
    ):
        build_record(
            state=RuntimeState.REQUEST_VALIDATING,
            state_version=2,
            step_count=2,
            retry_count=2,
            stage_retry_counts=(duplicate, duplicate),
        )


def test_stage_retry_total_must_match_global_retry_count() -> None:
    """Per-stage retry evidence reconciles with the global counter."""

    with pytest.raises(
        ValidationError,
        match="must sum to the total retry_count",
    ):
        build_record(
            state=RuntimeState.REQUEST_VALIDATING,
            state_version=2,
            step_count=2,
            retry_count=2,
            stage_retry_counts=(
                StageRetryCount(
                    state=RuntimeState.REQUEST_VALIDATING,
                    retry_count=1,
                ),
            ),
        )


def test_terminal_states_cannot_receive_retry_counters() -> None:
    """Terminal workflows cannot be retried in place."""

    with pytest.raises(
        ValidationError,
        match="cannot be assigned to terminal states",
    ):
        StageRetryCount(
            state=RuntimeState.COMPLETED_FAILURE,
            retry_count=1,
        )


def test_authorization_expiry_requires_policy_lineage() -> None:
    """The runtime cannot invent authorization without a decision record."""

    with pytest.raises(
        ValidationError,
        match="requires policy_decision_id",
    ):
        build_record(
            authorization_expires_at=BASE_TIME + timedelta(minutes=5),
        )


def test_policy_lineage_can_be_recorded_without_granting_authority() -> None:
    """The snapshot may reference a policy decision but cannot create one."""

    record = build_record(
        state=RuntimeState.POLICY_EVALUATING,
        state_version=3,
        step_count=3,
        policy_decision_id="policy-decision-101",
        authorization_expires_at=BASE_TIME + timedelta(minutes=5),
    )

    assert record.policy_decision_id == "policy-decision-101"
    assert record.authorization_expires_at == BASE_TIME + timedelta(minutes=5)
    assert not record.terminal


def test_received_state_requires_zero_counters() -> None:
    """The initial state cannot claim work that has not occurred."""

    with pytest.raises(
        ValidationError,
        match="must begin at version and count zero",
    ):
        build_record(
            state_version=1,
            step_count=1,
        )


def test_retry_lookup_returns_recorded_and_default_counts() -> None:
    """Retry lookup is deterministic for present and absent states."""

    record = build_record(
        state=RuntimeState.REQUEST_VALIDATING,
        state_version=2,
        step_count=2,
        retry_count=1,
        stage_retry_counts=(
            StageRetryCount(
                state=RuntimeState.REQUEST_VALIDATING,
                retry_count=1,
            ),
        ),
    )

    assert record.retry_count_for(RuntimeState.REQUEST_VALIDATING) == 1
    assert record.retry_count_for(RuntimeState.POLICY_EVALUATING) == 0


def test_terminal_property_is_derived_from_state() -> None:
    """Terminal posture is derived rather than independently asserted."""

    record = build_record(
        state=RuntimeState.COMPLETED_ABSTENTION,
        state_version=4,
        step_count=4,
        reason_codes=(RuntimeReasonCode.EVIDENCE_INSUFFICIENT,),
    )

    assert record.terminal
