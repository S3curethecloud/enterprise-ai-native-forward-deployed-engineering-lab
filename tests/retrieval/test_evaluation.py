"""Tests for deterministic Phase 5J retrieval evaluation and telemetry."""

from datetime import timedelta

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.contracts.common import Timestamp
from incident_diagnostic_api.retrieval.evaluation import (
    GENESIS_TELEMETRY_HASH,
    RETRIEVAL_EVALUATION_VERSION,
    RETRIEVAL_TELEMETRY_VERSION,
    InMemoryRetrievalTelemetryStore,
    RetrievalEvaluationDisposition,
    RetrievalEvaluationExpectation,
    RetrievalEvaluationMetrics,
    RetrievalEvaluationResult,
    RetrievalEvaluationThresholds,
    RetrievalLifecycleOutcome,
    RetrievalLifecycleStage,
    RetrievalTelemetryEvent,
    RetrievalTelemetryMeasurement,
    TelemetryCapacityExceededError,
    calculate_retrieval_metrics,
    calculate_telemetry_event_hash,
    evaluate_retrieval,
    verify_retrieval_telemetry_history,
)
from incident_diagnostic_api.retrieval.models import RetrievalResult
from tests.retrieval.test_citation_validation import VALIDATED_AT, validate
from tests.retrieval.test_context import build_retrieval
from tests.retrieval.test_keyword import build_corpus

EVALUATED_AT = VALIDATED_AT + timedelta(seconds=1)


def retrieval_result() -> RetrievalResult:
    """Return the correlated default candidate result."""

    _, result = build_retrieval()
    return result


def expectation(**overrides: object) -> RetrievalEvaluationExpectation:
    """Return explicit deterministic relevance expectations."""

    values: dict[str, object] = {
        "case_id": "evaluation-case-201",
        "relevant_chunk_ids": ("chunk-a", "chunk-b"),
        "cutoff_k": 2,
        "expect_retrieval_abstention": False,
        "expect_citations_valid": True,
        "expect_freshness_valid": True,
    }
    values.update(overrides)
    return RetrievalEvaluationExpectation.model_validate(values)


def thresholds(**overrides: object) -> RetrievalEvaluationThresholds:
    """Return explicit thresholds compatible with strict mypy."""

    values: dict[str, object] = {
        "minimum_precision_at_k": 1.0,
        "minimum_recall_at_k": 1.0,
        "minimum_reciprocal_rank": 1.0,
        "minimum_citation_correctness": 1.0,
        "minimum_freshness_correctness": 1.0,
        "minimum_abstention_correctness": 1.0,
        "maximum_query_latency_ms": 500.0,
        "maximum_context_items": 2,
        "maximum_context_token_estimate": 20,
    }
    values.update(overrides)
    return RetrievalEvaluationThresholds.model_validate(values)


def metrics(**overrides: object) -> RetrievalEvaluationMetrics:
    """Return valid explicit metric evidence."""

    values: dict[str, object] = {
        "cutoff_k": 2,
        "relevant_chunk_count": 2,
        "retrieved_at_k_count": 2,
        "relevant_at_k_count": 2,
        "precision_at_k": 1.0,
        "recall_at_k": 1.0,
        "reciprocal_rank": 1.0,
        "citation_correctness": 1.0,
        "freshness_correctness": 1.0,
        "abstention_correctness": 1.0,
        "query_latency_ms": 25.0,
        "context_item_count": 2,
        "context_token_estimate": 8,
    }
    values.update(overrides)
    return RetrievalEvaluationMetrics.model_validate(values)


def evaluate(**overrides: object) -> RetrievalEvaluationResult:
    """Evaluate the default correlated synthetic case."""

    values: dict[str, object] = {
        "evaluation_id": "evaluation-201",
        "expectation": expectation(),
        "retrieval": retrieval_result(),
        "citation_validation": validate(),
        "thresholds": thresholds(),
        "query_latency_ms": 25.0,
        "context_item_count": 2,
        "context_token_estimate": 8,
        "evaluated_at": EVALUATED_AT,
    }
    values.update(overrides)
    return evaluate_retrieval(**values)  # type: ignore[arg-type]


def measurement(**overrides: object) -> RetrievalTelemetryMeasurement:
    """Return bounded allowlisted telemetry measurements."""

    values: dict[str, object] = {
        "candidate_count": 2,
        "context_item_count": 2,
        "context_token_estimate": 8,
        "quarantined_item_count": 0,
        "validated_item_count": 2,
        "duration_ms": 25.0,
    }
    values.update(overrides)
    return RetrievalTelemetryMeasurement.model_validate(values)


def append_event(
    store: InMemoryRetrievalTelemetryStore,
    *,
    stage: RetrievalLifecycleStage = RetrievalLifecycleStage.RETRIEVAL_COMPLETED,
    outcome: RetrievalLifecycleOutcome = RetrievalLifecycleOutcome.SUCCEEDED,
    occurred_at: Timestamp = VALIDATED_AT,
) -> RetrievalTelemetryEvent:
    """Append one default correlated telemetry event."""

    return store.append(
        request_id="request-201",
        trace_id="trace-201",
        stage=stage,
        outcome=outcome,
        measurement=measurement(),
        occurred_at=occurred_at,
        input_reference="input-201",
        output_reference="output-201",
    )


def test_contract_versions_and_enums_are_bounded() -> None:
    assert RETRIEVAL_EVALUATION_VERSION == "retrieval-evaluation-v1"
    assert RETRIEVAL_TELEMETRY_VERSION == "retrieval-telemetry-v1"
    assert GENESIS_TELEMETRY_HASH == "GENESIS"
    assert [item.value for item in RetrievalEvaluationDisposition] == [
        "passed",
        "failed",
    ]
    assert [item.value for item in RetrievalLifecycleStage] == [
        "retrieval_completed",
        "context_constructed",
        "content_inspected",
        "citations_validated",
        "evaluation_completed",
    ]


def test_expectation_rejects_duplicate_relevant_chunks() -> None:
    with pytest.raises(ValidationError, match="relevant chunk identifiers must be unique"):
        expectation(relevant_chunk_ids=("chunk-a", "chunk-a"))


def test_expected_abstention_rejects_relevant_chunks() -> None:
    with pytest.raises(ValidationError, match="expected abstention"):
        expectation(expect_retrieval_abstention=True)


def test_perfect_candidate_metrics_are_one() -> None:
    result = calculate_retrieval_metrics(
        expectation=expectation(),
        retrieval=retrieval_result(),
        citation_validation=validate(),
        query_latency_ms=25.0,
        context_item_count=2,
        context_token_estimate=8,
    )

    assert result.precision_at_k == 1.0
    assert result.recall_at_k == 1.0
    assert result.reciprocal_rank == 1.0
    assert result.citation_correctness == 1.0
    assert result.freshness_correctness == 1.0
    assert result.abstention_correctness == 1.0


def test_precision_recall_and_rank_use_relevance_labels() -> None:
    result = calculate_retrieval_metrics(
        expectation=expectation(relevant_chunk_ids=("chunk-b",)),
        retrieval=retrieval_result(),
        citation_validation=validate(),
        query_latency_ms=25.0,
        context_item_count=2,
        context_token_estimate=8,
    )

    assert result.precision_at_k == 0.5
    assert result.recall_at_k == 1.0
    assert result.reciprocal_rank == 0.5


def test_cutoff_limits_precision_and_recall_inputs() -> None:
    result = calculate_retrieval_metrics(
        expectation=expectation(cutoff_k=1),
        retrieval=retrieval_result(),
        citation_validation=validate(),
        query_latency_ms=25.0,
        context_item_count=2,
        context_token_estimate=8,
    )

    assert result.retrieved_at_k_count == 1
    assert result.relevant_at_k_count == 1
    assert result.precision_at_k == 1.0
    assert result.recall_at_k == 0.5


def test_no_relevance_labels_produce_zero_relevance_metrics() -> None:
    result = calculate_retrieval_metrics(
        expectation=expectation(relevant_chunk_ids=()),
        retrieval=retrieval_result(),
        citation_validation=validate(),
        query_latency_ms=25.0,
        context_item_count=2,
        context_token_estimate=8,
    )

    assert result.precision_at_k == 0.0
    assert result.recall_at_k == 0.0
    assert result.reciprocal_rank == 0.0


def test_stale_validation_is_measured_as_expected_failure() -> None:
    stale = validate(validated_at=VALIDATED_AT + timedelta(hours=2))
    result = calculate_retrieval_metrics(
        expectation=expectation(),
        retrieval=retrieval_result(),
        citation_validation=stale,
        query_latency_ms=25.0,
        context_item_count=2,
        context_token_estimate=8,
    )

    assert result.freshness_correctness == 0.0


def test_citation_mismatch_is_measured_as_expected_failure() -> None:
    corpus = build_corpus()
    incomplete = corpus.model_copy(update={"chunks": corpus.chunks[1:]})
    mismatched = validate(corpus=incomplete)
    result = calculate_retrieval_metrics(
        expectation=expectation(),
        retrieval=retrieval_result(),
        citation_validation=mismatched,
        query_latency_ms=25.0,
        context_item_count=2,
        context_token_estimate=8,
    )

    assert result.citation_correctness == 0.0


def test_metric_calculation_rejects_request_mismatch() -> None:
    changed = validate().model_copy(update={"request_id": "request-other"})

    with pytest.raises(ValueError, match="request_id must match retrieval"):
        calculate_retrieval_metrics(
            expectation=expectation(),
            retrieval=retrieval_result(),
            citation_validation=changed,
            query_latency_ms=25.0,
            context_item_count=2,
            context_token_estimate=8,
        )


def test_metric_calculation_rejects_trace_mismatch() -> None:
    changed = validate().model_copy(update={"trace_id": "trace-other"})

    with pytest.raises(ValueError, match="trace_id must match retrieval"):
        calculate_retrieval_metrics(
            expectation=expectation(),
            retrieval=retrieval_result(),
            citation_validation=changed,
            query_latency_ms=25.0,
            context_item_count=2,
            context_token_estimate=8,
        )


def test_negative_latency_fails_closed() -> None:
    with pytest.raises(ValidationError):
        calculate_retrieval_metrics(
            expectation=expectation(),
            retrieval=retrieval_result(),
            citation_validation=validate(),
            query_latency_ms=-1.0,
            context_item_count=2,
            context_token_estimate=8,
        )


def test_perfect_case_passes_explicit_thresholds() -> None:
    result = evaluate()

    assert result.disposition is RetrievalEvaluationDisposition.PASSED
    assert result.failed_checks == ()
    assert result.request_id == "request-201"
    assert result.trace_id == "trace-201"


def test_failed_checks_are_stable_and_ordered() -> None:
    result = evaluate(
        expectation=expectation(relevant_chunk_ids=("chunk-b",)),
        query_latency_ms=600.0,
        context_item_count=3,
        context_token_estimate=21,
    )

    assert result.disposition is RetrievalEvaluationDisposition.FAILED
    assert result.failed_checks == (
        "precision_at_k",
        "reciprocal_rank",
        "query_latency_ms",
        "context_item_count",
        "context_token_estimate",
    )


def test_evaluation_cannot_precede_upstream_completion() -> None:
    with pytest.raises(ValueError, match="citation validation"):
        evaluate(evaluated_at=VALIDATED_AT - timedelta(microseconds=1))


def test_passed_result_rejects_failed_checks() -> None:
    with pytest.raises(ValidationError, match="passed evaluation"):
        RetrievalEvaluationResult(
            evaluation_id="evaluation-invalid",
            case_id="case-invalid",
            request_id="request-201",
            trace_id="trace-201",
            disposition=RetrievalEvaluationDisposition.PASSED,
            metrics=metrics(),
            failed_checks=("precision_at_k",),
            evaluated_at=EVALUATED_AT,
        )


def test_failed_result_requires_failed_checks() -> None:
    with pytest.raises(ValidationError, match="failed evaluation requires"):
        RetrievalEvaluationResult(
            evaluation_id="evaluation-invalid",
            case_id="case-invalid",
            request_id="request-201",
            trace_id="trace-201",
            disposition=RetrievalEvaluationDisposition.FAILED,
            metrics=metrics(),
            failed_checks=(),
            evaluated_at=EVALUATED_AT,
        )


def test_metric_contract_rejects_impossible_counts() -> None:
    with pytest.raises(ValidationError, match="cannot exceed retrieved"):
        metrics(retrieved_at_k_count=1, relevant_at_k_count=2)


def test_telemetry_hash_is_deterministic() -> None:
    values = {
        "event_id": "retrieval-event-trace-201-000000",
        "request_id": "request-201",
        "trace_id": "trace-201",
        "sequence": 0,
        "stage": RetrievalLifecycleStage.RETRIEVAL_COMPLETED,
        "outcome": RetrievalLifecycleOutcome.SUCCEEDED,
        "input_reference": "input-201",
        "output_reference": "output-201",
        "measurement": measurement(),
        "previous_event_hash": None,
        "occurred_at": VALIDATED_AT,
    }

    first = calculate_telemetry_event_hash(**values)  # type: ignore[arg-type]
    second = calculate_telemetry_event_hash(**values)  # type: ignore[arg-type]

    assert first == second
    assert len(first) == 64


def test_genesis_event_has_expected_lineage() -> None:
    store = InMemoryRetrievalTelemetryStore(maximum_events_per_trace=5)
    event = append_event(store)

    assert event.sequence == 0
    assert event.previous_event_hash is None
    assert store.history("trace-201") == (event,)
    assert verify_retrieval_telemetry_history((event,))


def test_second_event_links_to_genesis() -> None:
    store = InMemoryRetrievalTelemetryStore(maximum_events_per_trace=5)
    first = append_event(store)
    second = append_event(
        store,
        stage=RetrievalLifecycleStage.CONTEXT_CONSTRUCTED,
        occurred_at=VALIDATED_AT + timedelta(seconds=1),
    )

    assert second.sequence == 1
    assert second.previous_event_hash == first.event_hash
    assert verify_retrieval_telemetry_history((first, second))


def test_unknown_history_is_empty_and_read_only() -> None:
    store = InMemoryRetrievalTelemetryStore(maximum_events_per_trace=5)

    assert store.history("unknown-trace") == ()
    assert store.trace_count() == 0
    assert store.event_count() == 0


def test_store_isolates_trace_histories() -> None:
    store = InMemoryRetrievalTelemetryStore(maximum_events_per_trace=5)
    first = append_event(store)
    second = store.append(
        request_id="request-202",
        trace_id="trace-202",
        stage=RetrievalLifecycleStage.RETRIEVAL_COMPLETED,
        outcome=RetrievalLifecycleOutcome.ABSTAINED,
        measurement=measurement(candidate_count=0),
        occurred_at=VALIDATED_AT,
    )

    assert store.trace_count() == 2
    assert store.event_count() == 2
    assert store.history("trace-201") == (first,)
    assert store.history("trace-202") == (second,)


def test_request_identity_cannot_change_within_trace() -> None:
    store = InMemoryRetrievalTelemetryStore(maximum_events_per_trace=5)
    append_event(store)

    with pytest.raises(ValueError, match="request_id cannot change"):
        store.append(
            request_id="request-other",
            trace_id="trace-201",
            stage=RetrievalLifecycleStage.CONTEXT_CONSTRUCTED,
            outcome=RetrievalLifecycleOutcome.SUCCEEDED,
            measurement=measurement(),
            occurred_at=VALIDATED_AT + timedelta(seconds=1),
        )


def test_telemetry_timestamps_cannot_move_backwards() -> None:
    store = InMemoryRetrievalTelemetryStore(maximum_events_per_trace=5)
    append_event(store)

    with pytest.raises(ValueError, match="timestamps must be nondecreasing"):
        append_event(store, occurred_at=VALIDATED_AT - timedelta(microseconds=1))


def test_store_capacity_fails_before_mutation() -> None:
    store = InMemoryRetrievalTelemetryStore(maximum_events_per_trace=1)
    first = append_event(store)

    with pytest.raises(TelemetryCapacityExceededError) as captured:
        append_event(
            store,
            stage=RetrievalLifecycleStage.CONTEXT_CONSTRUCTED,
            occurred_at=VALIDATED_AT + timedelta(seconds=1),
        )

    assert captured.value.trace_id == "trace-201"
    assert store.history("trace-201") == (first,)


@pytest.mark.parametrize("capacity", [0, 101])
def test_store_rejects_invalid_capacity(capacity: int) -> None:
    with pytest.raises(ValueError, match="between 1 and 100"):
        InMemoryRetrievalTelemetryStore(maximum_events_per_trace=capacity)


def test_telemetry_rejects_unrestricted_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        RetrievalTelemetryMeasurement.model_validate(
            {
                **measurement().model_dump(mode="python"),
                "query_text": "sensitive raw query",
            }
        )


def test_history_verification_detects_hash_tampering() -> None:
    store = InMemoryRetrievalTelemetryStore(maximum_events_per_trace=5)
    event = append_event(store)
    changed = event.model_copy(update={"event_hash": "f" * 64})

    assert not verify_retrieval_telemetry_history((changed,))


def test_history_verification_detects_sequence_tampering() -> None:
    store = InMemoryRetrievalTelemetryStore(maximum_events_per_trace=5)
    event = append_event(store)
    changed = event.model_copy(update={"sequence": 1})

    assert not verify_retrieval_telemetry_history((changed,))


def test_empty_history_is_not_verified_evidence() -> None:
    assert not verify_retrieval_telemetry_history(())


def test_equivalent_evaluation_and_telemetry_are_repeatable() -> None:
    assert evaluate() == evaluate()

    first_store = InMemoryRetrievalTelemetryStore(maximum_events_per_trace=5)
    second_store = InMemoryRetrievalTelemetryStore(maximum_events_per_trace=5)

    assert append_event(first_store) == append_event(second_store)
