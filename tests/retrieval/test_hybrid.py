"""Tests for deterministic Phase 5F fusion primitives."""

from dataclasses import FrozenInstanceError

import pytest

from incident_diagnostic_api.retrieval import (
    RetrievalAbstentionCode,
    RetrievalCandidate,
    RetrievalDisposition,
    RetrievalMethod,
    RetrievalResult,
)
from incident_diagnostic_api.retrieval.hybrid import (
    HybridRetrievalConfig,
    calculate_hybrid_score,
    calculate_reciprocal_rank_score,
    normalize_candidate_scores,
    retrieve_hybrid,
)
from incident_diagnostic_api.retrieval.keyword import retrieve_keywords
from incident_diagnostic_api.retrieval.vector import (
    build_vector_index,
)
from tests.retrieval.test_keyword import (
    COMPLETED_AT,
    build_authorization,
    build_corpus,
    build_query,
)
from tests.retrieval.test_vector import (
    build_tie_corpus,
)


def build_keyword_candidates() -> tuple[RetrievalCandidate, ...]:
    """Return known deterministic keyword candidates."""

    query = build_query()
    result = retrieve_keywords(
        corpus=build_corpus(),
        query=query,
        authorization=build_authorization(query=query),
        completed_at=COMPLETED_AT,
    )

    return result.candidates


def test_default_hybrid_configuration_is_explicit() -> None:
    config = HybridRetrievalConfig()

    assert config.config_version == "hybrid-fusion-v1"
    assert config.keyword_weight == 0.45
    assert config.vector_weight == 0.45
    assert config.rank_weight == 0.10
    assert config.reciprocal_rank_constant == 60


def test_hybrid_configuration_is_immutable() -> None:
    config = HybridRetrievalConfig()

    with pytest.raises(FrozenInstanceError):
        config.keyword_weight = 1.0  # type: ignore[misc]


def test_unsupported_configuration_version_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="configuration version is unsupported",
    ):
        HybridRetrievalConfig(config_version="unknown")


@pytest.mark.parametrize(
    "keyword_weight",
    [-0.1, 1.1],
)
def test_out_of_range_weight_is_rejected(
    keyword_weight: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="weights must be between zero and one",
    ):
        HybridRetrievalConfig(
            keyword_weight=keyword_weight,
        )


def test_weights_that_do_not_sum_to_one_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="weights must sum to one",
    ):
        HybridRetrievalConfig(
            keyword_weight=0.4,
            vector_weight=0.4,
            rank_weight=0.1,
        )


def test_nonpositive_reciprocal_rank_constant_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="rank constant must be positive",
    ):
        HybridRetrievalConfig(
            reciprocal_rank_constant=0,
        )


def test_empty_candidate_scores_normalize_to_empty() -> None:
    assert normalize_candidate_scores(()) == {}


def test_candidate_scores_normalize_by_method_maximum() -> None:
    normalized = normalize_candidate_scores(build_keyword_candidates())

    assert normalized == {
        "chunk-a": 1.0,
        "chunk-b": 0.5,
    }


def test_duplicate_candidate_chunk_is_rejected() -> None:
    candidate = build_keyword_candidates()[0]

    with pytest.raises(
        ValueError,
        match="duplicate chunk",
    ):
        normalize_candidate_scores((candidate, candidate))


def test_two_first_place_ranks_normalize_to_one() -> None:
    score = calculate_reciprocal_rank_score(
        keyword_rank=1,
        vector_rank=1,
        reciprocal_rank_constant=60,
    )

    assert score == 1.0


def test_one_first_place_rank_has_half_rank_evidence() -> None:
    score = calculate_reciprocal_rank_score(
        keyword_rank=1,
        vector_rank=None,
        reciprocal_rank_constant=60,
    )

    assert score == 0.5


def test_later_ranks_have_less_reciprocal_rank_evidence() -> None:
    first = calculate_reciprocal_rank_score(
        keyword_rank=1,
        vector_rank=1,
        reciprocal_rank_constant=60,
    )
    later = calculate_reciprocal_rank_score(
        keyword_rank=5,
        vector_rank=5,
        reciprocal_rank_constant=60,
    )

    assert later < first


def test_missing_ranks_have_zero_rank_evidence() -> None:
    assert (
        calculate_reciprocal_rank_score(
            keyword_rank=None,
            vector_rank=None,
            reciprocal_rank_constant=60,
        )
        == 0.0
    )


def test_invalid_candidate_rank_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="ranks must be positive",
    ):
        calculate_reciprocal_rank_score(
            keyword_rank=0,
            vector_rank=1,
            reciprocal_rank_constant=60,
        )


def test_invalid_function_rank_constant_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="rank constant must be positive",
    ):
        calculate_reciprocal_rank_score(
            keyword_rank=1,
            vector_rank=1,
            reciprocal_rank_constant=0,
        )


def test_hybrid_score_uses_transparent_weighted_formula() -> None:
    config = HybridRetrievalConfig()

    score = calculate_hybrid_score(
        keyword_score=1.0,
        vector_score=0.5,
        reciprocal_rank_score=0.25,
        config=config,
    )

    assert score == pytest.approx(0.45 * 1.0 + 0.45 * 0.5 + 0.10 * 0.25)


@pytest.mark.parametrize(
    ("keyword_score", "vector_score", "rank_score"),
    [
        (-0.1, 0.5, 0.5),
        (0.5, 1.1, 0.5),
        (0.5, 0.5, 1.1),
    ],
)
def test_out_of_range_hybrid_input_is_rejected(
    keyword_score: float,
    vector_score: float,
    rank_score: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="inputs must be between zero and one",
    ):
        calculate_hybrid_score(
            keyword_score=keyword_score,
            vector_score=vector_score,
            reciprocal_rank_score=rank_score,
            config=HybridRetrievalConfig(),
        )


def execute_hybrid_retrieval(
    *,
    query_text: str = "payment queue",
    minimum_score: float = 0.0,
    max_candidates: int = 10,
    max_evidence_items: int = 50,
    allowed_tenant_ids: tuple[str, ...] = ("tenant-a",),
    config: HybridRetrievalConfig | None = None,
) -> RetrievalResult:
    """Execute hybrid retrieval with matching bounded authority."""

    corpus = build_corpus()
    query = build_query(
        query_text=query_text,
        minimum_score=minimum_score,
        max_candidates=max_candidates,
    )
    authorization = build_authorization(
        query=query,
        allowed_tenant_ids=allowed_tenant_ids,
        max_evidence_items=max_evidence_items,
    )

    return retrieve_hybrid(
        index=build_vector_index(corpus),
        query=query,
        authorization=authorization,
        completed_at=COMPLETED_AT,
        config=config,
    )


def test_hybrid_retrieval_returns_ranked_candidates() -> None:
    result = execute_hybrid_retrieval()

    assert result.disposition is RetrievalDisposition.CANDIDATES
    assert [candidate.chunk_id for candidate in result.candidates] == [
        "chunk-a",
        "chunk-b",
    ]
    assert [candidate.rank for candidate in result.candidates] == [1, 2]
    assert all(candidate.method is RetrievalMethod.HYBRID for candidate in result.candidates)


def test_hybrid_scores_match_verified_order() -> None:
    result = execute_hybrid_retrieval()

    assert result.candidates[0].score == pytest.approx(1.0)
    assert result.candidates[1].score == pytest.approx(
        0.583195,
        abs=0.000001,
    )


def test_hybrid_retrieval_deduplicates_chunk_identity() -> None:
    result = execute_hybrid_retrieval()
    chunk_ids = [candidate.chunk_id for candidate in result.candidates]

    assert len(chunk_ids) == len(set(chunk_ids))


def test_hybrid_candidate_preserves_citation_lineage() -> None:
    result = execute_hybrid_retrieval()

    for candidate in result.candidates:
        assert candidate.source_id == candidate.citation.source_id
        assert candidate.document_id == candidate.citation.document_id
        assert candidate.chunk_id == candidate.citation.chunk_id
        assert candidate.policy_decision_id == (result.query.policy_decision_id)


def test_hybrid_retrieval_is_repeatable() -> None:
    first = execute_hybrid_retrieval()
    second = execute_hybrid_retrieval()

    assert first == second


def test_empty_hybrid_query_abstains() -> None:
    result = execute_hybrid_retrieval(
        query_text="!!!",
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.abstention is not None
    assert result.abstention.code is RetrievalAbstentionCode.NO_RELEVANT_EVIDENCE


def test_mismatched_hybrid_authority_abstains() -> None:
    corpus = build_corpus()
    query = build_query()
    authorization = build_authorization(
        query=query,
    ).model_copy(
        update={
            "trace_id": "different-trace",
        }
    )

    result = retrieve_hybrid(
        index=build_vector_index(corpus),
        query=query,
        authorization=authorization,
        completed_at=COMPLETED_AT,
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.abstention is not None
    assert result.abstention.code is RetrievalAbstentionCode.AUTHORIZATION_MISSING


def test_hybrid_tenant_scope_is_enforced() -> None:
    result = execute_hybrid_retrieval(
        allowed_tenant_ids=("tenant-b",),
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.abstention is not None
    assert result.abstention.code is RetrievalAbstentionCode.NO_AUTHORIZED_SOURCES


def test_policy_limit_applies_after_hybrid_fusion() -> None:
    result = execute_hybrid_retrieval(
        max_candidates=10,
        max_evidence_items=1,
    )

    assert len(result.candidates) == 1
    assert result.candidates[0].rank == 1


def test_query_limit_applies_after_hybrid_fusion() -> None:
    result = execute_hybrid_retrieval(
        max_candidates=1,
        max_evidence_items=10,
    )

    assert len(result.candidates) == 1


def test_keyword_only_configuration_is_transparent() -> None:
    result = execute_hybrid_retrieval(
        config=HybridRetrievalConfig(
            keyword_weight=1.0,
            vector_weight=0.0,
            rank_weight=0.0,
        )
    )

    assert result.candidates[0].score == pytest.approx(1.0)
    assert result.candidates[1].score == pytest.approx(0.5)


def test_hybrid_threshold_applies_after_fusion() -> None:
    result = execute_hybrid_retrieval(
        minimum_score=0.6,
    )

    assert [candidate.chunk_id for candidate in result.candidates] == [
        "chunk-a",
    ]
    assert result.query.minimum_score == 0.6


def test_equal_hybrid_scores_use_stable_tie_breaking() -> None:
    corpus = build_tie_corpus()
    query = build_query()
    authorization = build_authorization(query=query)
    no_rank_config = HybridRetrievalConfig(
        keyword_weight=0.5,
        vector_weight=0.5,
        rank_weight=0.0,
    )

    result = retrieve_hybrid(
        index=build_vector_index(corpus),
        query=query,
        authorization=authorization,
        completed_at=COMPLETED_AT,
        config=no_rank_config,
    )

    assert [candidate.chunk_id for candidate in result.candidates] == [
        "chunk-a",
        "chunk-b",
    ]
    assert result.candidates[0].score == pytest.approx(result.candidates[1].score)
