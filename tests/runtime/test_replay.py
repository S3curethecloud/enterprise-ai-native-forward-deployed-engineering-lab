"""Tests for deterministic Phase 4 checkpoint replay."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.runtime import (
    CheckpointVersionConflictError,
    InMemoryCheckpointStore,
    ReplayIntegrityError,
    ReplayResult,
    ReplayStep,
    RuntimeCheckpoint,
    RuntimeReasonCode,
    RuntimeState,
    RuntimeStateRecord,
    StageRetryCount,
    TransitionCommand,
    replay_checkpoint_history,
)

BASE_TIME = datetime(2026, 7, 19, 18, 30, tzinfo=UTC)


def build_initial(**overrides: object) -> RuntimeStateRecord:
    """Build a genesis runtime snapshot."""

    values: dict[str, object] = {
        "workflow_id": "workflow-replay-201",
        "request_id": "request-replay-201",
        "trace_id": "trace-replay-201",
        "created_at": BASE_TIME,
        "updated_at": BASE_TIME,
    }
    values.update(overrides)

    return RuntimeStateRecord.model_validate(values)


def build_next(
    previous: RuntimeStateRecord,
    *,
    state: RuntimeState,
    reason_code: RuntimeReasonCode,
    **overrides: object,
) -> RuntimeStateRecord:
    """Build one normal state-changing snapshot."""

    values: dict[str, object] = {
        **previous.model_dump(mode="python"),
        "state": state,
        "state_version": previous.state_version + 1,
        "step_count": previous.step_count + 1,
        "reason_codes": (reason_code,),
        "updated_at": BASE_TIME + timedelta(seconds=previous.state_version + 1),
    }
    values.update(overrides)

    return RuntimeStateRecord.model_validate(values)


def checkpoint_chain(
    *snapshots: RuntimeStateRecord,
) -> tuple[RuntimeCheckpoint, ...]:
    """Store snapshots and return their checkpoint history."""

    store = InMemoryCheckpointStore()
    expected_previous_version: int | None = None

    for index, snapshot in enumerate(snapshots):
        store.append(
            snapshot,
            expected_previous_version=expected_previous_version,
            created_at=BASE_TIME + timedelta(seconds=index),
        )
        expected_previous_version = snapshot.state_version

    return store.history(snapshots[0].workflow_id)


def test_genesis_only_history_replays() -> None:
    """A valid genesis checkpoint is independently replayable."""

    initial = build_initial()

    result = replay_checkpoint_history(checkpoint_chain(initial))

    assert result.verified
    assert result.reason_code is RuntimeReasonCode.REPLAY_VERIFIED
    assert result.checkpoint_count == 1
    assert result.final_state is RuntimeState.RECEIVED
    assert result.final_state_version == 0
    assert result.steps[0].source_state is None
    assert result.steps[0].command is None
    assert result.steps[0].target_state is RuntimeState.RECEIVED


def test_normal_transition_chain_is_reconstructed() -> None:
    """Replay reconstructs commands from authorized state changes."""

    initial = build_initial()
    validating = build_next(
        initial,
        state=RuntimeState.REQUEST_VALIDATING,
        reason_code=RuntimeReasonCode.REQUEST_VALIDATION_STARTED,
    )
    identity = build_next(
        validating,
        state=RuntimeState.IDENTITY_VALIDATING,
        reason_code=RuntimeReasonCode.REQUEST_VALIDATED,
    )

    result = replay_checkpoint_history(checkpoint_chain(initial, validating, identity))

    assert result.checkpoint_count == 3
    assert result.final_state is RuntimeState.IDENTITY_VALIDATING
    assert result.final_state_version == 2
    assert result.steps[1].command is (TransitionCommand.BEGIN_REQUEST_VALIDATION)
    assert result.steps[2].command is (TransitionCommand.REQUEST_VALIDATED)
    assert result.steps[2].source_state is (RuntimeState.REQUEST_VALIDATING)


def test_same_state_retry_is_reconstructed() -> None:
    """A same-state retry requires explicit retry-counter evidence."""

    initial = build_initial()
    validating = build_next(
        initial,
        state=RuntimeState.REQUEST_VALIDATING,
        reason_code=RuntimeReasonCode.REQUEST_VALIDATION_STARTED,
    )
    retry = RuntimeStateRecord.model_validate(
        {
            **validating.model_dump(mode="python"),
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
            "updated_at": BASE_TIME + timedelta(seconds=2),
        }
    )

    result = replay_checkpoint_history(checkpoint_chain(initial, validating, retry))

    assert result.verified
    assert result.steps[2].command is (TransitionCommand.RETRY_CURRENT_STAGE)
    assert result.steps[2].source_state is (RuntimeState.REQUEST_VALIDATING)
    assert result.steps[2].target_state is (RuntimeState.REQUEST_VALIDATING)


def test_empty_history_fails_closed() -> None:
    """Replay requires at least one integrity-protected checkpoint."""

    with pytest.raises(ReplayIntegrityError) as captured:
        replay_checkpoint_history(())

    assert captured.value.reason_code is RuntimeReasonCode.CHECKPOINT_INTEGRITY_FAILURE
    assert captured.value.sequence is None


def test_tampered_checkpoint_hash_fails_before_replay() -> None:
    """Hash tampering is classified as checkpoint-integrity failure."""

    initial = build_initial()
    checkpoints = checkpoint_chain(initial)
    tampered = checkpoints[0].model_copy(update={"checkpoint_hash": "f" * 64})

    with pytest.raises(ReplayIntegrityError) as captured:
        replay_checkpoint_history((tampered,))

    assert captured.value.reason_code is RuntimeReasonCode.CHECKPOINT_INTEGRITY_FAILURE


def test_non_received_genesis_fails_replay() -> None:
    """A history cannot begin in the middle of the workflow."""

    invalid_genesis = build_initial(
        state=RuntimeState.REQUEST_VALIDATING,
    )

    with pytest.raises(ReplayIntegrityError) as captured:
        replay_checkpoint_history(checkpoint_chain(invalid_genesis))

    assert captured.value.reason_code is RuntimeReasonCode.REPLAY_DIVERGENCE
    assert captured.value.sequence == 0


@pytest.mark.parametrize(
    "changed_field",
    ["request_id", "trace_id"],
)
def test_identity_lineage_change_fails_replay(
    changed_field: str,
) -> None:
    """Request and trace identity cannot change between snapshots."""

    initial = build_initial()
    overrides = {changed_field: f"changed-{changed_field}"}
    validating = build_next(
        initial,
        state=RuntimeState.REQUEST_VALIDATING,
        reason_code=RuntimeReasonCode.REQUEST_VALIDATION_STARTED,
        **overrides,
    )

    with pytest.raises(ReplayIntegrityError) as captured:
        replay_checkpoint_history(checkpoint_chain(initial, validating))

    assert captured.value.sequence == 1
    assert captured.value.reason_code is RuntimeReasonCode.REPLAY_DIVERGENCE


def test_unauthorized_state_jump_fails_replay() -> None:
    """Replay rejects state changes absent from the transition table."""

    initial = build_initial()
    jumped = build_next(
        initial,
        state=RuntimeState.POLICY_EVALUATING,
        reason_code=RuntimeReasonCode.POLICY_ALLOWED,
    )

    with pytest.raises(ReplayIntegrityError) as captured:
        replay_checkpoint_history(checkpoint_chain(initial, jumped))

    assert captured.value.sequence == 1


def test_wrong_transition_reason_fails_replay() -> None:
    """State and reason evidence must describe the same transition."""

    initial = build_initial()
    validating = build_next(
        initial,
        state=RuntimeState.REQUEST_VALIDATING,
        reason_code=RuntimeReasonCode.ACCESS_DENIED,
    )

    with pytest.raises(ReplayIntegrityError) as captured:
        replay_checkpoint_history(checkpoint_chain(initial, validating))

    assert captured.value.sequence == 1


def test_normal_transition_cannot_change_retry_count() -> None:
    """Retry accounting cannot be hidden inside a state change."""

    initial = build_initial()
    validating = build_next(
        initial,
        state=RuntimeState.REQUEST_VALIDATING,
        reason_code=RuntimeReasonCode.REQUEST_VALIDATION_STARTED,
        retry_count=1,
        stage_retry_counts=(
            StageRetryCount(
                state=RuntimeState.RECEIVED,
                retry_count=1,
            ),
        ),
    )

    with pytest.raises(ReplayIntegrityError) as captured:
        replay_checkpoint_history(checkpoint_chain(initial, validating))

    assert captured.value.sequence == 1


def test_step_count_must_advance_exactly_once() -> None:
    """Replay rejects skipped or duplicated step counters."""

    initial = build_initial()
    validating = build_next(
        initial,
        state=RuntimeState.REQUEST_VALIDATING,
        reason_code=RuntimeReasonCode.REQUEST_VALIDATION_STARTED,
        step_count=2,
    )

    with pytest.raises(ReplayIntegrityError) as captured:
        replay_checkpoint_history(checkpoint_chain(initial, validating))

    assert captured.value.sequence == 1


def test_same_state_requires_retry_increment() -> None:
    """Remaining in an active state requires retry evidence."""

    initial = build_initial()
    validating = build_next(
        initial,
        state=RuntimeState.REQUEST_VALIDATING,
        reason_code=RuntimeReasonCode.REQUEST_VALIDATION_STARTED,
    )
    invalid_retry = RuntimeStateRecord.model_validate(
        {
            **validating.model_dump(mode="python"),
            "state_version": 2,
            "step_count": 2,
            "reason_codes": (RuntimeReasonCode.RETRY_SCHEDULED,),
            "updated_at": BASE_TIME + timedelta(seconds=2),
        }
    )

    with pytest.raises(ReplayIntegrityError) as captured:
        replay_checkpoint_history(checkpoint_chain(initial, validating, invalid_retry))

    assert captured.value.sequence == 2


def test_same_state_requires_matching_stage_retry() -> None:
    """The current active state's retry counter must increment."""

    initial = build_initial()
    validating = build_next(
        initial,
        state=RuntimeState.REQUEST_VALIDATING,
        reason_code=RuntimeReasonCode.REQUEST_VALIDATION_STARTED,
    )
    invalid_retry = RuntimeStateRecord.model_validate(
        {
            **validating.model_dump(mode="python"),
            "state_version": 2,
            "step_count": 2,
            "retry_count": 1,
            "stage_retry_counts": (
                StageRetryCount(
                    state=RuntimeState.IDENTITY_VALIDATING,
                    retry_count=1,
                ),
            ),
            "reason_codes": (RuntimeReasonCode.RETRY_SCHEDULED,),
            "updated_at": BASE_TIME + timedelta(seconds=2),
        }
    )

    with pytest.raises(ReplayIntegrityError) as captured:
        replay_checkpoint_history(checkpoint_chain(initial, validating, invalid_retry))

    assert captured.value.sequence == 2


def test_same_state_requires_retry_reason() -> None:
    """Retry counters require RETRY_SCHEDULED evidence."""

    initial = build_initial()
    validating = build_next(
        initial,
        state=RuntimeState.REQUEST_VALIDATING,
        reason_code=RuntimeReasonCode.REQUEST_VALIDATION_STARTED,
    )
    invalid_retry = RuntimeStateRecord.model_validate(
        {
            **validating.model_dump(mode="python"),
            "state_version": 2,
            "step_count": 2,
            "retry_count": 1,
            "stage_retry_counts": (
                StageRetryCount(
                    state=RuntimeState.REQUEST_VALIDATING,
                    retry_count=1,
                ),
            ),
            "reason_codes": (RuntimeReasonCode.TRANSIENT_FAILURE_RECORDED,),
            "updated_at": BASE_TIME + timedelta(seconds=2),
        }
    )

    with pytest.raises(ReplayIntegrityError) as captured:
        replay_checkpoint_history(checkpoint_chain(initial, validating, invalid_retry))

    assert captured.value.sequence == 2


def test_genesis_replay_step_rejects_command() -> None:
    """Genesis cannot falsely claim a transition command."""

    with pytest.raises(
        ValidationError,
        match="genesis replay step",
    ):
        ReplayStep(
            sequence=0,
            checkpoint_id="checkpoint-genesis",
            state_version=0,
            source_state=RuntimeState.RECEIVED,
            command=TransitionCommand.BEGIN_REQUEST_VALIDATION,
            target_state=RuntimeState.REQUEST_VALIDATING,
            checkpoint_hash="a" * 64,
        )


def test_non_genesis_replay_step_requires_command() -> None:
    """Later replay steps require source and command evidence."""

    with pytest.raises(
        ValidationError,
        match="non-genesis replay step",
    ):
        ReplayStep(
            sequence=1,
            checkpoint_id="checkpoint-later",
            state_version=1,
            target_state=RuntimeState.REQUEST_VALIDATING,
            checkpoint_hash="a" * 64,
        )


def test_replay_result_summary_is_consistent() -> None:
    """Verified replay summary matches its final reconstructed step."""

    initial = build_initial()
    result = replay_checkpoint_history(checkpoint_chain(initial))

    assert result.workflow_id == initial.workflow_id
    assert result.request_id == initial.request_id
    assert result.trace_id == initial.trace_id
    assert result.final_checkpoint_hash == result.steps[-1].checkpoint_hash


def test_replay_result_rejects_unverified_claim() -> None:
    """ReplayResult cannot represent failed evidence as a result."""

    initial = build_initial()
    valid = replay_checkpoint_history(checkpoint_chain(initial))

    with pytest.raises(
        ValidationError,
        match="verified replay evidence only",
    ):
        ReplayResult.model_validate(
            {
                **valid.model_dump(mode="python"),
                "verified": False,
            }
        )


def test_checkpoint_store_still_rejects_skipped_version() -> None:
    """Replay tests do not weaken checkpoint version enforcement."""

    store = InMemoryCheckpointStore()
    initial = build_initial()
    store.append(
        initial,
        expected_previous_version=None,
        created_at=BASE_TIME,
    )
    skipped = build_next(
        initial,
        state=RuntimeState.IDENTITY_VALIDATING,
        reason_code=RuntimeReasonCode.REQUEST_VALIDATED,
        state_version=2,
        step_count=2,
    )

    with pytest.raises(CheckpointVersionConflictError):
        store.append(
            skipped,
            expected_previous_version=0,
            created_at=BASE_TIME + timedelta(seconds=2),
        )
