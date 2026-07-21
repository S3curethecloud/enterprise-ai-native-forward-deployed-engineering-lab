"""Deterministic retrieval evaluation and bounded lifecycle telemetry."""

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated, Final, Literal, Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    ConfidenceScore,
    ContentHash,
    ContractModel,
    NonNegativeDuration,
    OpaqueIdentifier,
    Timestamp,
)
from incident_diagnostic_api.retrieval.citation_validation import (
    CitationAbstentionCode,
    CitationValidationDisposition,
    CitationValidationResult,
)
from incident_diagnostic_api.retrieval.enums import RetrievalDisposition
from incident_diagnostic_api.retrieval.models import RetrievalResult

RETRIEVAL_EVALUATION_VERSION: Final[Literal["retrieval-evaluation-v1"]] = "retrieval-evaluation-v1"
RETRIEVAL_TELEMETRY_VERSION: Final[Literal["retrieval-telemetry-v1"]] = "retrieval-telemetry-v1"
GENESIS_TELEMETRY_HASH: Final[str] = "GENESIS"


class RetrievalEvaluationDisposition(StrEnum):
    """Bounded outcome of one deterministic retrieval evaluation."""

    PASSED = "passed"
    FAILED = "failed"


class RetrievalLifecycleStage(StrEnum):
    """Allowlisted stages observable in the local retrieval lifecycle."""

    RETRIEVAL_COMPLETED = "retrieval_completed"
    CONTEXT_CONSTRUCTED = "context_constructed"
    CONTENT_INSPECTED = "content_inspected"
    CITATIONS_VALIDATED = "citations_validated"
    EVALUATION_COMPLETED = "evaluation_completed"


class RetrievalLifecycleOutcome(StrEnum):
    """Allowlisted lifecycle outcomes without unrestricted payloads."""

    SUCCEEDED = "succeeded"
    ABSTAINED = "abstained"
    FAILED = "failed"


RelevantChunkIdentifiers = Annotated[
    tuple[OpaqueIdentifier, ...],
    Field(max_length=50),
]


class RetrievalEvaluationExpectation(ContractModel):
    """Ground truth and correctness expectations for one synthetic case."""

    case_id: OpaqueIdentifier
    relevant_chunk_ids: RelevantChunkIdentifiers = Field(default_factory=tuple)
    cutoff_k: Annotated[int, Field(default=10, ge=1, le=50)]
    expect_retrieval_abstention: bool = False
    expect_citations_valid: bool = True
    expect_freshness_valid: bool = True

    @model_validator(mode="after")
    def validate_expectation(self) -> Self:
        """Keep relevance labels and abstention expectations coherent."""

        if len(self.relevant_chunk_ids) != len(set(self.relevant_chunk_ids)):
            raise ValueError("relevant chunk identifiers must be unique")

        if self.expect_retrieval_abstention and self.relevant_chunk_ids:
            raise ValueError("an expected abstention cannot declare relevant chunks")

        return self


class RetrievalEvaluationMetrics(ContractModel):
    """Deterministic quality and lifecycle measurements for one case."""

    cutoff_k: Annotated[int, Field(ge=1, le=50)]
    relevant_chunk_count: Annotated[int, Field(ge=0, le=50)]
    retrieved_at_k_count: Annotated[int, Field(ge=0, le=50)]
    relevant_at_k_count: Annotated[int, Field(ge=0, le=50)]
    precision_at_k: ConfidenceScore
    recall_at_k: ConfidenceScore
    reciprocal_rank: ConfidenceScore
    citation_correctness: ConfidenceScore
    freshness_correctness: ConfidenceScore
    abstention_correctness: ConfidenceScore
    query_latency_ms: NonNegativeDuration
    context_item_count: Annotated[int, Field(ge=0, le=50)]
    context_token_estimate: Annotated[int, Field(ge=0, le=32_768)]

    @model_validator(mode="after")
    def validate_counts(self) -> Self:
        """Reject impossible retrieval metric counts."""

        if self.relevant_at_k_count > self.retrieved_at_k_count:
            raise ValueError("relevant_at_k_count cannot exceed retrieved_at_k_count")

        if self.relevant_at_k_count > self.relevant_chunk_count:
            raise ValueError("relevant_at_k_count cannot exceed relevant_chunk_count")

        if self.retrieved_at_k_count > self.cutoff_k:
            raise ValueError("retrieved_at_k_count cannot exceed cutoff_k")

        return self


class RetrievalEvaluationThresholds(ContractModel):
    """Explicit local pass thresholds for deterministic evaluation."""

    minimum_precision_at_k: ConfidenceScore = 0.0
    minimum_recall_at_k: ConfidenceScore = 0.0
    minimum_reciprocal_rank: ConfidenceScore = 0.0
    minimum_citation_correctness: ConfidenceScore = 1.0
    minimum_freshness_correctness: ConfidenceScore = 1.0
    minimum_abstention_correctness: ConfidenceScore = 1.0
    maximum_query_latency_ms: NonNegativeDuration = 10_000.0
    maximum_context_items: Annotated[int, Field(default=50, ge=0, le=50)]
    maximum_context_token_estimate: Annotated[
        int,
        Field(default=32_768, ge=0, le=32_768),
    ]


class RetrievalEvaluationResult(ContractModel):
    """Immutable result for one locally evaluated synthetic retrieval case."""

    evaluation_version: Literal["retrieval-evaluation-v1"] = RETRIEVAL_EVALUATION_VERSION
    evaluation_id: OpaqueIdentifier
    case_id: OpaqueIdentifier
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    disposition: RetrievalEvaluationDisposition
    metrics: RetrievalEvaluationMetrics
    failed_checks: Annotated[
        tuple[OpaqueIdentifier, ...],
        Field(max_length=9),
    ] = Field(default_factory=tuple)
    evaluated_at: Timestamp

    @model_validator(mode="after")
    def validate_disposition(self) -> Self:
        """Align pass/fail disposition with failed-check evidence."""

        if len(self.failed_checks) != len(set(self.failed_checks)):
            raise ValueError("failed checks must be unique")

        if self.disposition is RetrievalEvaluationDisposition.PASSED and self.failed_checks:
            raise ValueError("a passed evaluation cannot contain failed checks")

        if self.disposition is RetrievalEvaluationDisposition.FAILED and not self.failed_checks:
            raise ValueError("a failed evaluation requires failed checks")

        return self


def _binary_correct(actual: bool, expected: bool) -> float:
    """Return deterministic binary correctness."""

    return 1.0 if actual is expected else 0.0


def _citation_state(validation: CitationValidationResult) -> tuple[bool, bool]:
    """Derive citation and freshness validity from a controlled outcome."""

    if validation.disposition is CitationValidationDisposition.VALIDATED:
        return True, True

    if validation.abstention is None:
        return False, False

    reasons = set(validation.abstention.reason_codes)
    citation_valid = not bool(
        reasons
        & {
            CitationAbstentionCode.CITATION_MISMATCH,
            CitationAbstentionCode.INTEGRITY_FAILURE,
        }
    )
    freshness_valid = CitationAbstentionCode.EVIDENCE_STALE not in reasons

    return citation_valid, freshness_valid


def calculate_retrieval_metrics(
    *,
    expectation: RetrievalEvaluationExpectation,
    retrieval: RetrievalResult,
    citation_validation: CitationValidationResult,
    query_latency_ms: float,
    context_item_count: int,
    context_token_estimate: int,
) -> RetrievalEvaluationMetrics:
    """Calculate bounded deterministic retrieval and lifecycle metrics."""

    if citation_validation.request_id != retrieval.request_id:
        raise ValueError("citation validation request_id must match retrieval")

    if citation_validation.trace_id != retrieval.trace_id:
        raise ValueError("citation validation trace_id must match retrieval")

    ranked_ids = tuple(candidate.chunk_id for candidate in retrieval.candidates)
    retrieved_at_k = ranked_ids[: expectation.cutoff_k]
    relevant_ids = set(expectation.relevant_chunk_ids)
    relevant_at_k = sum(chunk_id in relevant_ids for chunk_id in retrieved_at_k)

    precision = relevant_at_k / len(retrieved_at_k) if retrieved_at_k else 0.0
    if relevant_ids:
        recall = relevant_at_k / len(relevant_ids)
    else:
        recall = 1.0 if expectation.expect_retrieval_abstention else 0.0

    reciprocal_rank = 0.0
    for rank, chunk_id in enumerate(ranked_ids, start=1):
        if chunk_id in relevant_ids:
            reciprocal_rank = 1.0 / rank
            break

    actual_abstention = retrieval.disposition is RetrievalDisposition.ABSTENTION
    citations_valid, freshness_valid = _citation_state(citation_validation)

    return RetrievalEvaluationMetrics(
        cutoff_k=expectation.cutoff_k,
        relevant_chunk_count=len(relevant_ids),
        retrieved_at_k_count=len(retrieved_at_k),
        relevant_at_k_count=relevant_at_k,
        precision_at_k=precision,
        recall_at_k=recall,
        reciprocal_rank=reciprocal_rank,
        citation_correctness=_binary_correct(
            citations_valid,
            expectation.expect_citations_valid,
        ),
        freshness_correctness=_binary_correct(
            freshness_valid,
            expectation.expect_freshness_valid,
        ),
        abstention_correctness=_binary_correct(
            actual_abstention,
            expectation.expect_retrieval_abstention,
        ),
        query_latency_ms=query_latency_ms,
        context_item_count=context_item_count,
        context_token_estimate=context_token_estimate,
    )


def evaluate_retrieval(
    *,
    evaluation_id: str,
    expectation: RetrievalEvaluationExpectation,
    retrieval: RetrievalResult,
    citation_validation: CitationValidationResult,
    thresholds: RetrievalEvaluationThresholds,
    query_latency_ms: float,
    context_item_count: int,
    context_token_estimate: int,
    evaluated_at: Timestamp,
) -> RetrievalEvaluationResult:
    """Evaluate one synthetic retrieval case against explicit thresholds."""

    if evaluated_at < retrieval.completed_at:
        raise ValueError("evaluated_at cannot precede retrieval completion")

    if evaluated_at < citation_validation.completed_at:
        raise ValueError("evaluated_at cannot precede citation validation")

    metrics = calculate_retrieval_metrics(
        expectation=expectation,
        retrieval=retrieval,
        citation_validation=citation_validation,
        query_latency_ms=query_latency_ms,
        context_item_count=context_item_count,
        context_token_estimate=context_token_estimate,
    )
    failed: list[str] = []

    checks = (
        ("precision_at_k", metrics.precision_at_k >= thresholds.minimum_precision_at_k),
        ("recall_at_k", metrics.recall_at_k >= thresholds.minimum_recall_at_k),
        (
            "reciprocal_rank",
            metrics.reciprocal_rank >= thresholds.minimum_reciprocal_rank,
        ),
        (
            "citation_correctness",
            metrics.citation_correctness >= thresholds.minimum_citation_correctness,
        ),
        (
            "freshness_correctness",
            metrics.freshness_correctness >= thresholds.minimum_freshness_correctness,
        ),
        (
            "abstention_correctness",
            metrics.abstention_correctness >= thresholds.minimum_abstention_correctness,
        ),
        (
            "query_latency_ms",
            metrics.query_latency_ms <= thresholds.maximum_query_latency_ms,
        ),
        (
            "context_item_count",
            metrics.context_item_count <= thresholds.maximum_context_items,
        ),
        (
            "context_token_estimate",
            metrics.context_token_estimate <= thresholds.maximum_context_token_estimate,
        ),
    )

    for name, passed in checks:
        if not passed:
            failed.append(name)

    disposition = (
        RetrievalEvaluationDisposition.PASSED
        if not failed
        else RetrievalEvaluationDisposition.FAILED
    )

    return RetrievalEvaluationResult(
        evaluation_id=evaluation_id,
        case_id=expectation.case_id,
        request_id=retrieval.request_id,
        trace_id=retrieval.trace_id,
        disposition=disposition,
        metrics=metrics,
        failed_checks=tuple(failed),
        evaluated_at=evaluated_at,
    )


class RetrievalTelemetryMeasurement(ContractModel):
    """Allowlisted numeric lifecycle metadata without evidence content."""

    candidate_count: Annotated[int, Field(ge=0, le=50)] | None = None
    context_item_count: Annotated[int, Field(ge=0, le=50)] | None = None
    context_token_estimate: Annotated[int, Field(ge=0, le=32_768)] | None = None
    quarantined_item_count: Annotated[int, Field(ge=0, le=50)] | None = None
    validated_item_count: Annotated[int, Field(ge=0, le=50)] | None = None
    duration_ms: NonNegativeDuration | None = None


class RetrievalTelemetryEvent(ContractModel):
    """One immutable retrieval lifecycle event with hash-chain lineage."""

    telemetry_version: Literal["retrieval-telemetry-v1"] = RETRIEVAL_TELEMETRY_VERSION
    event_id: OpaqueIdentifier
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    sequence: Annotated[int, Field(ge=0, le=100)]
    stage: RetrievalLifecycleStage
    outcome: RetrievalLifecycleOutcome
    input_reference: OpaqueIdentifier | None = None
    output_reference: OpaqueIdentifier | None = None
    measurement: RetrievalTelemetryMeasurement
    previous_event_hash: ContentHash | None = None
    event_hash: ContentHash
    occurred_at: Timestamp

    @model_validator(mode="after")
    def validate_lineage_shape(self) -> Self:
        """Require genesis and non-genesis hash lineage."""

        if self.sequence == 0 and self.previous_event_hash is not None:
            raise ValueError("the genesis telemetry event cannot have a previous hash")

        if self.sequence > 0 and self.previous_event_hash is None:
            raise ValueError("a non-genesis telemetry event requires a previous hash")

        return self


def calculate_telemetry_event_hash(
    *,
    event_id: str,
    request_id: str,
    trace_id: str,
    sequence: int,
    stage: RetrievalLifecycleStage,
    outcome: RetrievalLifecycleOutcome,
    input_reference: str | None,
    output_reference: str | None,
    measurement: RetrievalTelemetryMeasurement,
    previous_event_hash: str | None,
    occurred_at: Timestamp,
) -> str:
    """Return a deterministic SHA-256 hash for one telemetry event."""

    payload = {
        "event_id": event_id,
        "request_id": request_id,
        "trace_id": trace_id,
        "sequence": sequence,
        "stage": stage.value,
        "outcome": outcome.value,
        "input_reference": input_reference,
        "output_reference": output_reference,
        "measurement": measurement.model_dump(mode="json"),
        "previous_event_hash": previous_event_hash or GENESIS_TELEMETRY_HASH,
        "occurred_at": occurred_at.isoformat(),
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class TelemetryCapacityExceededError(Exception):
    """Raised before an append would exceed a configured local bound."""

    trace_id: str
    maximum_events_per_trace: int

    def __str__(self) -> str:
        """Return a controlled capacity description."""

        return (
            f"telemetry capacity exceeded for trace {self.trace_id!r}: "
            f"maximum {self.maximum_events_per_trace} events"
        )


class InMemoryRetrievalTelemetryStore:
    """Bounded append-only local telemetry with per-trace hash lineage."""

    def __init__(self, *, maximum_events_per_trace: int = 20) -> None:
        if not 1 <= maximum_events_per_trace <= 100:
            raise ValueError("maximum_events_per_trace must be between 1 and 100")

        self._maximum_events_per_trace = maximum_events_per_trace
        self._histories: dict[str, list[RetrievalTelemetryEvent]] = {}

    def append(
        self,
        *,
        request_id: str,
        trace_id: str,
        stage: RetrievalLifecycleStage,
        outcome: RetrievalLifecycleOutcome,
        measurement: RetrievalTelemetryMeasurement,
        occurred_at: Timestamp,
        input_reference: str | None = None,
        output_reference: str | None = None,
    ) -> RetrievalTelemetryEvent:
        """Append one correlated event without accepting unrestricted payloads."""

        history = self._histories.get(trace_id, [])

        if len(history) >= self._maximum_events_per_trace:
            raise TelemetryCapacityExceededError(
                trace_id=trace_id,
                maximum_events_per_trace=self._maximum_events_per_trace,
            )

        previous = history[-1] if history else None

        if previous is not None:
            if previous.request_id != request_id:
                raise ValueError("telemetry request_id cannot change within a trace")

            if occurred_at < previous.occurred_at:
                raise ValueError("telemetry timestamps must be nondecreasing")

        sequence = len(history)
        event_id = f"retrieval-event-{trace_id}-{sequence:06d}"
        previous_hash = previous.event_hash if previous is not None else None
        event_hash = calculate_telemetry_event_hash(
            event_id=event_id,
            request_id=request_id,
            trace_id=trace_id,
            sequence=sequence,
            stage=stage,
            outcome=outcome,
            input_reference=input_reference,
            output_reference=output_reference,
            measurement=measurement,
            previous_event_hash=previous_hash,
            occurred_at=occurred_at,
        )
        event = RetrievalTelemetryEvent(
            event_id=event_id,
            request_id=request_id,
            trace_id=trace_id,
            sequence=sequence,
            stage=stage,
            outcome=outcome,
            input_reference=input_reference,
            output_reference=output_reference,
            measurement=measurement,
            previous_event_hash=previous_hash,
            event_hash=event_hash,
            occurred_at=occurred_at,
        )

        self._histories.setdefault(trace_id, []).append(event)

        return event

    def history(self, trace_id: str) -> tuple[RetrievalTelemetryEvent, ...]:
        """Return an immutable view without creating storage state."""

        return tuple(self._histories.get(trace_id, ()))

    def trace_count(self) -> int:
        """Return the number of traces with telemetry evidence."""

        return len(self._histories)

    def event_count(self) -> int:
        """Return the total number of stored telemetry events."""

        return sum(len(history) for history in self._histories.values())


def verify_retrieval_telemetry_history(
    events: tuple[RetrievalTelemetryEvent, ...],
) -> bool:
    """Verify correlation, order, timestamps, and complete hash lineage."""

    if not events:
        return False

    request_id = events[0].request_id
    trace_id = events[0].trace_id

    for index, event in enumerate(events):
        if event.sequence != index:
            return False

        if event.request_id != request_id or event.trace_id != trace_id:
            return False

        expected_previous = None if index == 0 else events[index - 1].event_hash
        if event.previous_event_hash != expected_previous:
            return False

        if index > 0 and event.occurred_at < events[index - 1].occurred_at:
            return False

        expected_hash = calculate_telemetry_event_hash(
            event_id=event.event_id,
            request_id=event.request_id,
            trace_id=event.trace_id,
            sequence=event.sequence,
            stage=event.stage,
            outcome=event.outcome,
            input_reference=event.input_reference,
            output_reference=event.output_reference,
            measurement=event.measurement,
            previous_event_hash=event.previous_event_hash,
            occurred_at=event.occurred_at,
        )

        if event.event_hash != expected_hash:
            return False

    return True
