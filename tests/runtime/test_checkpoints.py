"""Tests for append-only Phase 4 runtime checkpoints."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.runtime import (
    CheckpointNotFoundError,
    CheckpointVersionConflictError,
    InMemoryCheckpointStore,
    RuntimeCheckpoint,
    RuntimeReasonCode,
    RuntimeState,
    RuntimeStateRecord,
    calculate_checkpoint_hash,
    hash_runtime_state,
    verify_checkpoint_history,
)

BASE_TIME = datetime(2026, 7, 19, 18, 30, tzinfo=UTC)


def build_snapshot(**overrides: object) -> RuntimeStateRecord:
    """Build a valid runtime snapshot."""

    values: dict[str, object] = {
        "workflow_id": "workflow-checkpoint-201",
        "request_id": "request-checkpoint-201",
        "trace_id": "trace-checkpoint-201",
        "created_at": BASE_TIME,
        "updated_at": BASE_TIME,
    }
    values.update(overrides)

    return RuntimeStateRecord.model_validate(values)


def transition_snapshot(
    snapshot: RuntimeStateRecord,
) -> RuntimeStateRecord:
    """Create the next valid snapshot for checkpoint tests."""

    return RuntimeStateRecord.model_validate(
        {
            **snapshot.model_dump(mode="python"),
            "state": RuntimeState.REQUEST_VALIDATING,
            "state_version": 1,
            "step_count": 1,
            "reason_codes": (RuntimeReasonCode.REQUEST_VALIDATION_STARTED,),
            "updated_at": BASE_TIME + timedelta(seconds=1),
        }
    )


def test_state_hash_is_deterministic() -> None:
    """Equivalent immutable snapshots produce the same hash."""

    first = build_snapshot()
    second = build_snapshot()

    assert hash_runtime_state(first) == hash_runtime_state(second)
    assert len(hash_runtime_state(first)) == 64


def test_state_hash_changes_with_snapshot_content() -> None:
    """A meaningful state change produces a different hash."""

    initial = build_snapshot()
    transitioned = transition_snapshot(initial)

    assert hash_runtime_state(initial) != hash_runtime_state(transitioned)


def test_checkpoint_hash_is_deterministic() -> None:
    """Equivalent checkpoint metadata produces the same chain hash."""

    first = calculate_checkpoint_hash(
        checkpoint_id="checkpoint-test-000000",
        workflow_id="workflow-checkpoint-201",
        sequence=0,
        state_version=0,
        state_hash="a" * 64,
        previous_checkpoint_hash=None,
        created_at=BASE_TIME,
    )
    second = calculate_checkpoint_hash(
        checkpoint_id="checkpoint-test-000000",
        workflow_id="workflow-checkpoint-201",
        sequence=0,
        state_version=0,
        state_hash="a" * 64,
        previous_checkpoint_hash=None,
        created_at=BASE_TIME,
    )

    assert first == second
    assert len(first) == 64


def test_genesis_checkpoint_has_expected_lineage() -> None:
    """The first checkpoint begins sequence and version zero."""

    store = InMemoryCheckpointStore()
    snapshot = build_snapshot()

    checkpoint = store.append(
        snapshot,
        expected_previous_version=None,
        created_at=BASE_TIME,
    )

    assert checkpoint.sequence == 0
    assert checkpoint.state_version == 0
    assert checkpoint.previous_checkpoint_hash is None
    assert checkpoint.state_hash == hash_runtime_state(snapshot)
    assert checkpoint.snapshot == snapshot
    assert store.latest(snapshot.workflow_id) == checkpoint


def test_second_checkpoint_links_to_genesis() -> None:
    """A later checkpoint carries the preceding checkpoint hash."""

    store = InMemoryCheckpointStore()
    initial = build_snapshot()
    first = store.append(
        initial,
        expected_previous_version=None,
        created_at=BASE_TIME,
    )
    transitioned = transition_snapshot(initial)
    second = store.append(
        transitioned,
        expected_previous_version=0,
        created_at=BASE_TIME + timedelta(seconds=1),
    )

    assert second.sequence == 1
    assert second.state_version == 1
    assert second.previous_checkpoint_hash == first.checkpoint_hash
    assert store.history(initial.workflow_id) == (first, second)
    assert verify_checkpoint_history((first, second))


def test_checkpoint_store_isolates_workflow_histories() -> None:
    """One workflow cannot appear in another workflow's history."""

    store = InMemoryCheckpointStore()
    first = build_snapshot()
    second = build_snapshot(
        workflow_id="workflow-checkpoint-202",
        request_id="request-checkpoint-202",
        trace_id="trace-checkpoint-202",
    )

    first_checkpoint = store.append(
        first,
        expected_previous_version=None,
        created_at=BASE_TIME,
    )
    second_checkpoint = store.append(
        second,
        expected_previous_version=None,
        created_at=BASE_TIME,
    )

    assert store.workflow_count() == 2
    assert store.checkpoint_count() == 2
    assert store.history(first.workflow_id) == (first_checkpoint,)
    assert store.history(second.workflow_id) == (second_checkpoint,)


def test_unknown_history_returns_empty_tuple() -> None:
    """Read-only history lookup does not create storage state."""

    store = InMemoryCheckpointStore()

    assert store.history("unknown-workflow") == ()
    assert store.workflow_count() == 0
    assert store.checkpoint_count() == 0


def test_latest_unknown_workflow_fails_closed() -> None:
    """A missing latest checkpoint raises a controlled exception."""

    store = InMemoryCheckpointStore()

    with pytest.raises(CheckpointNotFoundError) as captured:
        store.latest("unknown-workflow")

    assert captured.value.workflow_id == "unknown-workflow"
    assert str(captured.value) == "no checkpoints exist for workflow 'unknown-workflow'"


def test_stale_writer_is_rejected() -> None:
    """Optimistic concurrency rejects an obsolete expected version."""

    store = InMemoryCheckpointStore()
    initial = build_snapshot()
    store.append(
        initial,
        expected_previous_version=None,
        created_at=BASE_TIME,
    )
    transitioned = transition_snapshot(initial)
    store.append(
        transitioned,
        expected_previous_version=0,
        created_at=BASE_TIME + timedelta(seconds=1),
    )

    proposed = RuntimeStateRecord.model_validate(
        {
            **transitioned.model_dump(mode="python"),
            "state": RuntimeState.IDENTITY_VALIDATING,
            "state_version": 2,
            "step_count": 2,
            "updated_at": BASE_TIME + timedelta(seconds=2),
        }
    )

    with pytest.raises(CheckpointVersionConflictError) as captured:
        store.append(
            proposed,
            expected_previous_version=0,
            created_at=BASE_TIME + timedelta(seconds=2),
        )

    error = captured.value

    assert error.reason_code is RuntimeReasonCode.VERSION_CONFLICT
    assert error.expected_previous_version == 0
    assert error.actual_previous_version == 1
    assert error.proposed_version == 2
    assert store.checkpoint_count() == 2


def test_skipped_state_version_is_rejected() -> None:
    """Checkpoint versions must advance exactly one at a time."""

    store = InMemoryCheckpointStore()
    initial = build_snapshot()
    store.append(
        initial,
        expected_previous_version=None,
        created_at=BASE_TIME,
    )

    skipped = RuntimeStateRecord.model_validate(
        {
            **initial.model_dump(mode="python"),
            "state": RuntimeState.IDENTITY_VALIDATING,
            "state_version": 2,
            "step_count": 2,
            "updated_at": BASE_TIME + timedelta(seconds=2),
        }
    )

    with pytest.raises(CheckpointVersionConflictError):
        store.append(
            skipped,
            expected_previous_version=0,
            created_at=BASE_TIME + timedelta(seconds=2),
        )

    assert store.checkpoint_count() == 1


def test_nonzero_genesis_version_is_rejected() -> None:
    """A new history must begin with version zero."""

    store = InMemoryCheckpointStore()
    proposed = build_snapshot(
        state=RuntimeState.REQUEST_VALIDATING,
        state_version=1,
        step_count=1,
    )

    with pytest.raises(CheckpointVersionConflictError):
        store.append(
            proposed,
            expected_previous_version=None,
            created_at=BASE_TIME,
        )

    assert store.checkpoint_count() == 0


def test_wrong_initial_expectation_is_rejected() -> None:
    """A caller cannot claim a previous version for a new workflow."""

    store = InMemoryCheckpointStore()

    with pytest.raises(CheckpointVersionConflictError):
        store.append(
            build_snapshot(),
            expected_previous_version=0,
            created_at=BASE_TIME,
        )


def test_checkpoint_rejects_workflow_mismatch() -> None:
    """Checkpoint and snapshot workflow identities must match."""

    snapshot = build_snapshot()

    with pytest.raises(
        ValidationError,
        match="workflow_id must match",
    ):
        RuntimeCheckpoint(
            checkpoint_id="checkpoint-mismatch-000000",
            workflow_id="different-workflow",
            sequence=0,
            state_version=0,
            state_hash="a" * 64,
            checkpoint_hash="b" * 64,
            created_at=BASE_TIME,
            snapshot=snapshot,
        )


def test_checkpoint_rejects_state_version_mismatch() -> None:
    """Checkpoint metadata cannot misstate snapshot version."""

    snapshot = build_snapshot()

    with pytest.raises(
        ValidationError,
        match="state_version must match",
    ):
        RuntimeCheckpoint(
            checkpoint_id="checkpoint-version-000000",
            workflow_id=snapshot.workflow_id,
            sequence=0,
            state_version=1,
            state_hash="a" * 64,
            checkpoint_hash="b" * 64,
            created_at=BASE_TIME,
            snapshot=snapshot,
        )


def test_genesis_checkpoint_rejects_previous_hash() -> None:
    """Genesis evidence cannot claim a predecessor."""

    snapshot = build_snapshot()

    with pytest.raises(
        ValidationError,
        match="genesis checkpoint cannot have a previous hash",
    ):
        RuntimeCheckpoint(
            checkpoint_id="checkpoint-genesis-000000",
            workflow_id=snapshot.workflow_id,
            sequence=0,
            state_version=0,
            state_hash="a" * 64,
            previous_checkpoint_hash="c" * 64,
            checkpoint_hash="b" * 64,
            created_at=BASE_TIME,
            snapshot=snapshot,
        )


def test_non_genesis_checkpoint_requires_previous_hash() -> None:
    """Later checkpoint evidence must link to its predecessor."""

    snapshot = transition_snapshot(build_snapshot())

    with pytest.raises(
        ValidationError,
        match="requires a previous hash",
    ):
        RuntimeCheckpoint(
            checkpoint_id="checkpoint-later-000001",
            workflow_id=snapshot.workflow_id,
            sequence=1,
            state_version=1,
            state_hash="a" * 64,
            checkpoint_hash="b" * 64,
            created_at=BASE_TIME,
            snapshot=snapshot,
        )


def test_verifier_accepts_empty_history() -> None:
    """An empty history contains no broken lineage."""

    assert verify_checkpoint_history(())


@pytest.mark.parametrize(
    "field",
    [
        "sequence",
        "state_version",
        "state_hash",
        "previous_checkpoint_hash",
        "checkpoint_hash",
    ],
)
def test_verifier_rejects_tampered_checkpoint(
    field: str,
) -> None:
    """Any mutation of stored lineage evidence fails verification."""

    store = InMemoryCheckpointStore()
    initial = build_snapshot()
    first = store.append(
        initial,
        expected_previous_version=None,
        created_at=BASE_TIME,
    )
    transitioned = transition_snapshot(initial)
    second = store.append(
        transitioned,
        expected_previous_version=0,
        created_at=BASE_TIME + timedelta(seconds=1),
    )

    tampered_values: dict[str, object] = {
        "sequence": 9,
        "state_version": 9,
        "state_hash": "d" * 64,
        "previous_checkpoint_hash": "e" * 64,
        "checkpoint_hash": "f" * 64,
    }
    tampered = second.model_copy(update={field: tampered_values[field]})

    assert not verify_checkpoint_history((first, tampered))


def test_returned_history_is_immutable_tuple() -> None:
    """Callers receive an immutable view of checkpoint history."""

    store = InMemoryCheckpointStore()
    snapshot = build_snapshot()
    checkpoint = store.append(
        snapshot,
        expected_previous_version=None,
        created_at=BASE_TIME,
    )

    history = store.history(snapshot.workflow_id)

    assert history == (checkpoint,)
    assert isinstance(history, tuple)
