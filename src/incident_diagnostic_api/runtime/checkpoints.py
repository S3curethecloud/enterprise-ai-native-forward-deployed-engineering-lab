"""Append-only in-memory checkpoints for the Phase 4 runtime."""

import hashlib
import json
from dataclasses import dataclass
from typing import Final, Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    ContentHash,
    ContractModel,
    OpaqueIdentifier,
    Timestamp,
)
from incident_diagnostic_api.runtime.enums import RuntimeReasonCode
from incident_diagnostic_api.runtime.models import RuntimeStateRecord

GENESIS_CHECKPOINT_HASH: Final[str] = "GENESIS"


@dataclass(frozen=True, slots=True)
class CheckpointVersionConflictError(Exception):
    """Raised when optimistic checkpoint version checks fail."""

    workflow_id: str
    expected_previous_version: int | None
    actual_previous_version: int | None
    proposed_version: int
    reason_code: RuntimeReasonCode = RuntimeReasonCode.VERSION_CONFLICT

    def __str__(self) -> str:
        """Return a controlled conflict description."""

        return (
            f"checkpoint version conflict for workflow "
            f"{self.workflow_id!r}: expected previous version "
            f"{self.expected_previous_version!r}, actual previous "
            f"version {self.actual_previous_version!r}, proposed "
            f"version {self.proposed_version}"
        )


@dataclass(frozen=True, slots=True)
class CheckpointNotFoundError(Exception):
    """Raised when a workflow has no checkpoint history."""

    workflow_id: str

    def __str__(self) -> str:
        """Return a controlled missing-checkpoint description."""

        return f"no checkpoints exist for workflow {self.workflow_id!r}"


class RuntimeCheckpoint(ContractModel):
    """Immutable checkpoint containing one complete runtime snapshot."""

    checkpoint_id: OpaqueIdentifier
    workflow_id: OpaqueIdentifier
    sequence: int = Field(ge=0)
    state_version: int = Field(ge=0)
    state_hash: ContentHash
    previous_checkpoint_hash: ContentHash | None = None
    checkpoint_hash: ContentHash
    created_at: Timestamp
    snapshot: RuntimeStateRecord

    @model_validator(mode="after")
    def validate_checkpoint_lineage(self) -> Self:
        """Keep checkpoint metadata aligned with its snapshot."""

        if self.workflow_id != self.snapshot.workflow_id:
            raise ValueError("checkpoint workflow_id must match snapshot workflow_id")

        if self.state_version != self.snapshot.state_version:
            raise ValueError("checkpoint state_version must match snapshot state_version")

        if self.sequence == 0 and self.previous_checkpoint_hash is not None:
            raise ValueError("the genesis checkpoint cannot have a previous hash")

        if self.sequence > 0 and self.previous_checkpoint_hash is None:
            raise ValueError("a non-genesis checkpoint requires a previous hash")

        return self


def hash_runtime_state(snapshot: RuntimeStateRecord) -> str:
    """Create a deterministic SHA-256 hash of a runtime snapshot."""

    canonical = json.dumps(
        snapshot.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def calculate_checkpoint_hash(
    *,
    checkpoint_id: str,
    workflow_id: str,
    sequence: int,
    state_version: int,
    state_hash: str,
    previous_checkpoint_hash: str | None,
    created_at: Timestamp,
) -> str:
    """Create a deterministic SHA-256 checkpoint-chain hash."""

    payload = {
        "checkpoint_id": checkpoint_id,
        "workflow_id": workflow_id,
        "sequence": sequence,
        "state_version": state_version,
        "state_hash": state_hash,
        "previous_checkpoint_hash": (previous_checkpoint_hash or GENESIS_CHECKPOINT_HASH),
        "created_at": created_at.isoformat(),
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class InMemoryCheckpointStore:
    """Local append-only checkpoint store with optimistic version checks."""

    def __init__(self) -> None:
        self._histories: dict[str, list[RuntimeCheckpoint]] = {}

    def append(
        self,
        snapshot: RuntimeStateRecord,
        *,
        expected_previous_version: int | None,
        created_at: Timestamp,
    ) -> RuntimeCheckpoint:
        """Append one checkpoint when version lineage is valid."""

        history = self._histories.get(snapshot.workflow_id, [])
        previous = history[-1] if history else None
        actual_previous_version = previous.state_version if previous is not None else None

        if expected_previous_version != actual_previous_version:
            raise CheckpointVersionConflictError(
                workflow_id=snapshot.workflow_id,
                expected_previous_version=expected_previous_version,
                actual_previous_version=actual_previous_version,
                proposed_version=snapshot.state_version,
            )

        required_version = 0 if previous is None else previous.state_version + 1

        if snapshot.state_version != required_version:
            raise CheckpointVersionConflictError(
                workflow_id=snapshot.workflow_id,
                expected_previous_version=expected_previous_version,
                actual_previous_version=actual_previous_version,
                proposed_version=snapshot.state_version,
            )

        sequence = len(history)
        checkpoint_id = f"checkpoint-{snapshot.workflow_id}-{sequence:06d}"
        state_hash = hash_runtime_state(snapshot)
        previous_hash = previous.checkpoint_hash if previous is not None else None
        checkpoint_hash = calculate_checkpoint_hash(
            checkpoint_id=checkpoint_id,
            workflow_id=snapshot.workflow_id,
            sequence=sequence,
            state_version=snapshot.state_version,
            state_hash=state_hash,
            previous_checkpoint_hash=previous_hash,
            created_at=created_at,
        )

        checkpoint = RuntimeCheckpoint(
            checkpoint_id=checkpoint_id,
            workflow_id=snapshot.workflow_id,
            sequence=sequence,
            state_version=snapshot.state_version,
            state_hash=state_hash,
            previous_checkpoint_hash=previous_hash,
            checkpoint_hash=checkpoint_hash,
            created_at=created_at,
            snapshot=snapshot,
        )

        self._histories.setdefault(snapshot.workflow_id, []).append(checkpoint)

        return checkpoint

    def latest(self, workflow_id: str) -> RuntimeCheckpoint:
        """Return the latest checkpoint for a workflow."""

        history = self._histories.get(workflow_id)

        if not history:
            raise CheckpointNotFoundError(workflow_id=workflow_id)

        return history[-1]

    def history(
        self,
        workflow_id: str,
    ) -> tuple[RuntimeCheckpoint, ...]:
        """Return an immutable view of checkpoint history."""

        return tuple(self._histories.get(workflow_id, ()))

    def workflow_count(self) -> int:
        """Return the number of workflows with checkpoint evidence."""

        return len(self._histories)

    def checkpoint_count(self) -> int:
        """Return the total number of stored checkpoints."""

        return sum(len(history) for history in self._histories.values())


def verify_checkpoint_history(
    checkpoints: tuple[RuntimeCheckpoint, ...],
) -> bool:
    """Verify sequence, state, and hash lineage for a checkpoint chain."""

    for index, checkpoint in enumerate(checkpoints):
        if checkpoint.sequence != index:
            return False

        if checkpoint.state_version != index:
            return False

        expected_previous_hash = None if index == 0 else checkpoints[index - 1].checkpoint_hash

        if checkpoint.previous_checkpoint_hash != expected_previous_hash:
            return False

        if checkpoint.state_hash != hash_runtime_state(checkpoint.snapshot):
            return False

        expected_checkpoint_hash = calculate_checkpoint_hash(
            checkpoint_id=checkpoint.checkpoint_id,
            workflow_id=checkpoint.workflow_id,
            sequence=checkpoint.sequence,
            state_version=checkpoint.state_version,
            state_hash=checkpoint.state_hash,
            previous_checkpoint_hash=checkpoint.previous_checkpoint_hash,
            created_at=checkpoint.created_at,
        )

        if checkpoint.checkpoint_hash != expected_checkpoint_hash:
            return False

    return True
