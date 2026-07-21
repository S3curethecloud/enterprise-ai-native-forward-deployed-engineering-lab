"""Tests for deterministic Phase 5G context construction."""

from datetime import timedelta

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.contracts.enums import FreshnessStatus
from incident_diagnostic_api.retrieval.context import (
    CONTEXT_BUDGET_VERSION,
    ContextBudget,
    ContextConstructionResult,
    ContextDisposition,
    ContextInsufficiencyCode,
    build_context,
)
from incident_diagnostic_api.retrieval.corpus import SyntheticEvidenceCorpus
from incident_diagnostic_api.retrieval.enums import EvidenceLifecycleStatus
from incident_diagnostic_api.retrieval.hybrid import retrieve_hybrid
from incident_diagnostic_api.retrieval.keyword import retrieve_keywords
from incident_diagnostic_api.retrieval.models import RetrievalQuery, RetrievalResult
from incident_diagnostic_api.retrieval.vector import build_vector_index
from tests.retrieval.test_keyword import (
    COMPLETED_AT,
    build_authorization,
    build_chunk,
    build_corpus,
    build_document,
    build_query,
    build_source,
)

CONSTRUCTED_AT = COMPLETED_AT + timedelta(seconds=1)


def build_retrieval(
    *,
    corpus: SyntheticEvidenceCorpus | None = None,
    query: RetrievalQuery | None = None,
) -> tuple[SyntheticEvidenceCorpus, RetrievalResult]:
    """Return a successful deterministic hybrid retrieval result."""

    resolved_corpus = build_corpus() if corpus is None else corpus
    resolved_query = build_query() if query is None else query
    authorization = build_authorization(query=resolved_query)
    result = retrieve_hybrid(
        index=build_vector_index(resolved_corpus),
        query=resolved_query,
        authorization=authorization,
        completed_at=COMPLETED_AT,
    )

    assert result.disposition.value == "candidates"
    return resolved_corpus, result


def build_multi_source_corpus() -> SyntheticEvidenceCorpus:
    """Return two relevant chunks owned by distinct authorized sources."""

    source_a = build_source(source_id="source-a")
    source_b = build_source(source_id="source-b")
    document_a = build_document(
        source=source_a,
        document_id="document-a",
        content="Payment queue recovery procedure.",
    )
    document_b = build_document(
        source=source_b,
        document_id="document-b",
        content="Payment queue latency investigation.",
    )
    chunk_a = build_chunk(
        document=document_a,
        chunk_id="chunk-a",
        content=document_a.content,
    )
    chunk_b = build_chunk(
        document=document_b,
        chunk_id="chunk-b",
        content=document_b.content,
    )

    return SyntheticEvidenceCorpus(
        corpus_id="phase5g-multi-source-corpus",
        corpus_version="corpus-v1",
        sources=(source_a, source_b),
        documents=(document_a, document_b),
        chunks=(chunk_a, chunk_b),
    )


def execute_context(
    *,
    corpus: SyntheticEvidenceCorpus | None = None,
    retrieval: RetrievalResult | None = None,
    budget: ContextBudget | None = None,
) -> ContextConstructionResult:
    """Build context with the default successful retrieval fixture."""

    if corpus is None or retrieval is None:
        default_corpus, default_retrieval = build_retrieval(corpus=corpus)
        resolved_corpus = default_corpus if corpus is None else corpus
        resolved_retrieval = default_retrieval if retrieval is None else retrieval
    else:
        resolved_corpus = corpus
        resolved_retrieval = retrieval

    return build_context(
        corpus=resolved_corpus,
        retrieval=resolved_retrieval,
        budget=ContextBudget() if budget is None else budget,
        constructed_at=CONSTRUCTED_AT,
    )


def test_context_budget_defaults_are_versioned() -> None:
    budget = ContextBudget()

    assert budget.budget_version == CONTEXT_BUDGET_VERSION
    assert budget.max_items == 10
    assert budget.max_items_per_source == 3
    assert budget.max_token_estimate == 4096
    assert budget.minimum_source_count == 1


@pytest.mark.parametrize(
    "values",
    [
        {"max_items": 1, "max_items_per_source": 2},
        {"max_items": 1, "minimum_source_count": 2},
    ],
)
def test_context_budget_rejects_inconsistent_limits(
    values: dict[str, int],
) -> None:
    with pytest.raises(ValidationError):
        ContextBudget(**values)  # type: ignore[arg-type]


def test_build_context_returns_complete_ordered_bundle() -> None:
    result = execute_context()

    assert result.disposition is ContextDisposition.BUNDLE
    assert result.insufficiency is None
    assert result.bundle is not None
    assert [item.chunk_id for item in result.bundle.items] == [
        "chunk-a",
        "chunk-b",
    ]
    assert [item.context_rank for item in result.bundle.items] == [1, 2]
    assert [item.retrieval_rank for item in result.bundle.items] == [1, 2]
    assert result.bundle.total_token_estimate == 7
    assert result.bundle.omitted_candidate_count == 0
    assert result.bundle.truncated is False


def test_context_preserves_query_policy_and_citation_lineage() -> None:
    _, retrieval = build_retrieval()
    result = execute_context(retrieval=retrieval)

    assert result.bundle is not None
    bundle = result.bundle
    assert bundle.request_id == retrieval.request_id
    assert bundle.trace_id == retrieval.trace_id
    assert bundle.subject_id == retrieval.query.subject_id
    assert bundle.tenant_id == retrieval.query.tenant_id
    assert bundle.service_id == retrieval.query.service_id
    assert bundle.policy_decision_id == retrieval.query.policy_decision_id
    assert bundle.policy_version == retrieval.query.policy_version
    assert bundle.request_summary == retrieval.query.query_text
    assert [item.citation for item in bundle.items] == [
        candidate.citation for candidate in retrieval.candidates
    ]


def test_item_limit_records_whole_chunk_omission() -> None:
    result = execute_context(
        budget=ContextBudget(max_items=1, max_items_per_source=1),
    )

    assert result.bundle is not None
    assert [item.chunk_id for item in result.bundle.items] == ["chunk-a"]
    assert result.bundle.items[0].content == "Payment queue recovery procedure."
    assert result.bundle.omitted_candidate_count == 1
    assert result.bundle.truncated is True


def test_token_budget_selects_only_complete_chunks() -> None:
    result = execute_context(
        budget=ContextBudget(max_token_estimate=4),
    )

    assert result.bundle is not None
    assert [item.chunk_id for item in result.bundle.items] == ["chunk-a"]
    assert result.bundle.total_token_estimate == 4
    assert result.bundle.omitted_candidate_count == 1


def test_token_budget_can_skip_a_larger_higher_ranked_chunk() -> None:
    result = execute_context(
        budget=ContextBudget(max_token_estimate=3),
    )

    assert result.bundle is not None
    assert [item.chunk_id for item in result.bundle.items] == ["chunk-b"]
    assert result.bundle.items[0].retrieval_rank == 2
    assert result.bundle.items[0].context_rank == 1
    assert result.bundle.items[0].content == "Payment latency investigation."


def test_per_source_limit_is_enforced() -> None:
    result = execute_context(
        budget=ContextBudget(max_items_per_source=1),
    )

    assert result.bundle is not None
    assert [item.chunk_id for item in result.bundle.items] == ["chunk-a"]
    assert result.bundle.omitted_candidate_count == 1


def test_missing_required_source_diversity_is_controlled() -> None:
    result = execute_context(
        budget=ContextBudget(
            max_items=2,
            max_items_per_source=2,
            minimum_source_count=2,
        ),
    )

    assert result.disposition is ContextDisposition.INSUFFICIENCY
    assert result.bundle is None
    assert result.insufficiency is not None
    assert result.insufficiency.code is ContextInsufficiencyCode.REQUIRED_SOURCE_DIVERSITY


def test_required_source_diversity_selects_distinct_sources() -> None:
    corpus = build_multi_source_corpus()
    query = build_query(allowed_source_ids=("source-a", "source-b"))
    corpus, retrieval = build_retrieval(corpus=corpus, query=query)
    result = execute_context(
        corpus=corpus,
        retrieval=retrieval,
        budget=ContextBudget(
            max_items=2,
            max_items_per_source=1,
            minimum_source_count=2,
        ),
    )

    assert result.bundle is not None
    assert {item.source_id for item in result.bundle.items} == {
        "source-a",
        "source-b",
    }
    assert [item.retrieval_rank for item in result.bundle.items] == [1, 2]


def test_retrieval_abstention_becomes_context_insufficiency() -> None:
    corpus = build_corpus()
    query = build_query(query_text="---")
    authorization = build_authorization(query=query)
    retrieval = retrieve_keywords(
        corpus=corpus,
        query=query,
        authorization=authorization,
        completed_at=COMPLETED_AT,
    )
    result = execute_context(corpus=corpus, retrieval=retrieval)

    assert result.disposition is ContextDisposition.INSUFFICIENCY
    assert result.insufficiency is not None
    assert result.insufficiency.code is ContextInsufficiencyCode.RETRIEVAL_ABSTAINED
    assert result.insufficiency.candidate_count == 0


def test_missing_candidate_chunk_fails_closed() -> None:
    corpus, retrieval = build_retrieval()
    incomplete_corpus = corpus.model_copy(update={"chunks": corpus.chunks[1:]})
    result = execute_context(corpus=incomplete_corpus, retrieval=retrieval)

    assert result.insufficiency is not None
    assert result.insufficiency.code is ContextInsufficiencyCode.INTEGRITY_FAILURE


def test_candidate_content_hash_mismatch_fails_closed() -> None:
    corpus, retrieval = build_retrieval()
    candidate = retrieval.candidates[0]
    citation = candidate.citation.model_copy(update={"content_hash": "deadbeef"})
    changed = candidate.model_copy(update={"citation": citation})
    malformed = retrieval.model_copy(update={"candidates": (changed, *retrieval.candidates[1:])})
    result = execute_context(corpus=corpus, retrieval=malformed)

    assert result.insufficiency is not None
    assert result.insufficiency.code is ContextInsufficiencyCode.INTEGRITY_FAILURE


def test_candidate_locator_mismatch_fails_closed() -> None:
    corpus, retrieval = build_retrieval()
    candidate = retrieval.candidates[0]
    citation = candidate.citation.model_copy(update={"locator": "chunk:999"})
    changed = candidate.model_copy(update={"citation": citation})
    malformed = retrieval.model_copy(update={"candidates": (changed, *retrieval.candidates[1:])})
    result = execute_context(corpus=corpus, retrieval=malformed)

    assert result.insufficiency is not None
    assert result.insufficiency.code is ContextInsufficiencyCode.INTEGRITY_FAILURE


def test_tombstoned_chunk_fails_closed() -> None:
    corpus, retrieval = build_retrieval()
    changed = corpus.chunks[0].model_copy(
        update={"lifecycle_status": EvidenceLifecycleStatus.TOMBSTONED}
    )
    malformed_corpus = corpus.model_copy(update={"chunks": (changed, *corpus.chunks[1:])})
    result = execute_context(corpus=malformed_corpus, retrieval=retrieval)

    assert result.insufficiency is not None
    assert result.insufficiency.code is ContextInsufficiencyCode.INTEGRITY_FAILURE


def test_stale_candidate_fails_closed() -> None:
    corpus, retrieval = build_retrieval()
    changed = retrieval.candidates[0].model_copy(update={"freshness": FreshnessStatus.STALE})
    malformed = retrieval.model_copy(update={"candidates": (changed, *retrieval.candidates[1:])})
    result = execute_context(corpus=corpus, retrieval=malformed)

    assert result.insufficiency is not None
    assert result.insufficiency.code is ContextInsufficiencyCode.INTEGRITY_FAILURE


def test_retrieval_timestamp_mismatch_fails_closed() -> None:
    corpus, retrieval = build_retrieval()
    candidate = retrieval.candidates[0]
    citation = candidate.citation.model_copy(
        update={"retrieved_at": COMPLETED_AT - timedelta(seconds=1)}
    )
    changed = candidate.model_copy(update={"citation": citation})
    malformed = retrieval.model_copy(update={"candidates": (changed, *retrieval.candidates[1:])})
    result = execute_context(corpus=corpus, retrieval=malformed)

    assert result.insufficiency is not None
    assert result.insufficiency.code is ContextInsufficiencyCode.INTEGRITY_FAILURE


def test_duplicate_candidate_chunk_fails_closed() -> None:
    corpus, retrieval = build_retrieval()
    duplicate = retrieval.candidates[0].model_copy(update={"rank": 2})
    malformed = retrieval.model_copy(update={"candidates": (retrieval.candidates[0], duplicate)})
    result = execute_context(corpus=corpus, retrieval=malformed)

    assert result.insufficiency is not None
    assert result.insufficiency.code is ContextInsufficiencyCode.INTEGRITY_FAILURE


def test_no_complete_item_within_budget_is_controlled() -> None:
    result = execute_context(
        budget=ContextBudget(max_token_estimate=2),
    )

    assert result.disposition is ContextDisposition.INSUFFICIENCY
    assert result.insufficiency is not None
    assert result.insufficiency.code is ContextInsufficiencyCode.BUDGET_EXHAUSTED


def test_constructed_at_cannot_precede_retrieval() -> None:
    corpus, retrieval = build_retrieval()

    with pytest.raises(ValueError, match="cannot precede retrieval completion"):
        build_context(
            corpus=corpus,
            retrieval=retrieval,
            budget=ContextBudget(),
            constructed_at=COMPLETED_AT - timedelta(seconds=1),
        )


def test_context_construction_is_repeatable() -> None:
    first = execute_context()
    second = execute_context()

    assert first == second
