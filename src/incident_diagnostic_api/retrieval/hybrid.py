"""Deterministic score fusion and reranking for local retrieval."""

from dataclasses import dataclass
from math import isclose

from incident_diagnostic_api.contracts import AuthorizationDecision
from incident_diagnostic_api.contracts.common import Timestamp
from incident_diagnostic_api.retrieval.enums import (
    RetrievalAbstentionCode,
    RetrievalDisposition,
    RetrievalMethod,
)
from incident_diagnostic_api.retrieval.keyword import retrieve_keywords
from incident_diagnostic_api.retrieval.models import (
    RetrievalCandidate,
    RetrievalQuery,
    RetrievalResult,
)
from incident_diagnostic_api.retrieval.security import (
    build_abstention_result,
)
from incident_diagnostic_api.retrieval.vector import (
    SyntheticVectorIndex,
    retrieve_vectors,
)


@dataclass(frozen=True, slots=True)
class HybridRetrievalConfig:
    """Versioned weights for transparent deterministic fusion."""

    config_version: str = "hybrid-fusion-v1"
    keyword_weight: float = 0.45
    vector_weight: float = 0.45
    rank_weight: float = 0.10
    reciprocal_rank_constant: int = 60

    def __post_init__(self) -> None:
        if self.config_version != "hybrid-fusion-v1":
            raise ValueError("hybrid configuration version is unsupported")

        weights = (
            self.keyword_weight,
            self.vector_weight,
            self.rank_weight,
        )

        if any(weight < 0.0 or weight > 1.0 for weight in weights):
            raise ValueError("hybrid weights must be between zero and one")

        if not isclose(sum(weights), 1.0):
            raise ValueError("hybrid weights must sum to one")

        if self.reciprocal_rank_constant < 1:
            raise ValueError("reciprocal rank constant must be positive")


def normalize_candidate_scores(
    candidates: tuple[RetrievalCandidate, ...],
) -> dict[str, float]:
    """Normalize one retrieval method's scores by its maximum."""

    if not candidates:
        return {}

    scores_by_chunk: dict[str, float] = {}

    for candidate in candidates:
        if candidate.chunk_id in scores_by_chunk:
            raise ValueError("candidate scores contain a duplicate chunk")

        scores_by_chunk[candidate.chunk_id] = candidate.score

    maximum = max(scores_by_chunk.values())

    if maximum == 0.0:
        return {chunk_id: 0.0 for chunk_id in scores_by_chunk}

    return {chunk_id: score / maximum for chunk_id, score in scores_by_chunk.items()}


def calculate_reciprocal_rank_score(
    *,
    keyword_rank: int | None,
    vector_rank: int | None,
    reciprocal_rank_constant: int,
) -> float:
    """Return normalized reciprocal-rank evidence from two methods."""

    if reciprocal_rank_constant < 1:
        raise ValueError("reciprocal rank constant must be positive")

    ranks = (keyword_rank, vector_rank)

    if any(rank is not None and rank < 1 for rank in ranks):
        raise ValueError("candidate ranks must be positive")

    observed = [1.0 / (reciprocal_rank_constant + rank) for rank in ranks if rank is not None]

    if not observed:
        return 0.0

    maximum_two_method_score = 2.0 / (reciprocal_rank_constant + 1)

    return sum(observed) / maximum_two_method_score


def calculate_hybrid_score(
    *,
    keyword_score: float,
    vector_score: float,
    reciprocal_rank_score: float,
    config: HybridRetrievalConfig,
) -> float:
    """Return one bounded transparent hybrid score."""

    scores = (
        keyword_score,
        vector_score,
        reciprocal_rank_score,
    )

    if any(score < 0.0 or score > 1.0 for score in scores):
        raise ValueError("normalized hybrid inputs must be between zero and one")

    score = (
        config.keyword_weight * keyword_score
        + config.vector_weight * vector_score
        + config.rank_weight * reciprocal_rank_score
    )

    return max(0.0, min(1.0, score))


def _hybrid_abstention_code(
    keyword_result: RetrievalResult,
    vector_result: RetrievalResult,
) -> RetrievalAbstentionCode:
    """Select the safest shared abstention reason."""

    codes = {
        result.abstention.code
        for result in (keyword_result, vector_result)
        if result.abstention is not None
    }

    if RetrievalAbstentionCode.AUTHORIZATION_MISSING in codes:
        return RetrievalAbstentionCode.AUTHORIZATION_MISSING

    if RetrievalAbstentionCode.NO_AUTHORIZED_SOURCES in codes:
        return RetrievalAbstentionCode.NO_AUTHORIZED_SOURCES

    if RetrievalAbstentionCode.INTEGRITY_FAILURE in codes:
        return RetrievalAbstentionCode.INTEGRITY_FAILURE

    return RetrievalAbstentionCode.NO_RELEVANT_EVIDENCE


def retrieve_hybrid(
    *,
    index: SyntheticVectorIndex,
    query: RetrievalQuery,
    authorization: AuthorizationDecision,
    completed_at: Timestamp,
    config: HybridRetrievalConfig | None = None,
) -> RetrievalResult:
    """Fuse authorized keyword and vector candidates deterministically."""

    resolved_config = HybridRetrievalConfig() if config is None else config
    component_query = query.model_copy(
        update={
            "minimum_score": 0.0,
        }
    )

    keyword_result = retrieve_keywords(
        corpus=index.corpus,
        query=component_query,
        authorization=authorization,
        completed_at=completed_at,
    )
    vector_result = retrieve_vectors(
        index=index,
        query=component_query,
        authorization=authorization,
        completed_at=completed_at,
    )

    keyword_candidates = keyword_result.candidates
    vector_candidates = vector_result.candidates

    if not keyword_candidates and not vector_candidates:
        code = _hybrid_abstention_code(
            keyword_result,
            vector_result,
        )
        authorized_source_count = max(
            (result.abstention.authorized_source_count if result.abstention is not None else 0)
            for result in (
                keyword_result,
                vector_result,
            )
        )

        return build_abstention_result(
            query=query,
            code=code,
            safe_message=("No authorized evidence qualified for hybrid retrieval."),
            sources_searched=len(index.corpus.sources),
            authorized_source_count=authorized_source_count,
            completed_at=completed_at,
        )

    keyword_by_chunk = {candidate.chunk_id: candidate for candidate in keyword_candidates}
    vector_by_chunk = {candidate.chunk_id: candidate for candidate in vector_candidates}
    keyword_scores = normalize_candidate_scores(keyword_candidates)
    vector_scores = normalize_candidate_scores(vector_candidates)

    scored_candidates: list[tuple[float, RetrievalCandidate]] = []

    for chunk_id in sorted(set(keyword_by_chunk) | set(vector_by_chunk)):
        keyword_candidate = keyword_by_chunk.get(chunk_id)
        vector_candidate = vector_by_chunk.get(chunk_id)
        base_candidate = keyword_candidate if keyword_candidate is not None else vector_candidate

        if base_candidate is None:
            raise RuntimeError("hybrid candidate union lost its source candidate")

        rank_score = calculate_reciprocal_rank_score(
            keyword_rank=(keyword_candidate.rank if keyword_candidate is not None else None),
            vector_rank=(vector_candidate.rank if vector_candidate is not None else None),
            reciprocal_rank_constant=(resolved_config.reciprocal_rank_constant),
        )
        hybrid_score = calculate_hybrid_score(
            keyword_score=keyword_scores.get(chunk_id, 0.0),
            vector_score=vector_scores.get(chunk_id, 0.0),
            reciprocal_rank_score=rank_score,
            config=resolved_config,
        )

        if hybrid_score > 0.0 and hybrid_score >= query.minimum_score:
            scored_candidates.append(
                (
                    hybrid_score,
                    base_candidate,
                )
            )

    scored_candidates.sort(
        key=lambda item: (
            -item[0],
            item[1].source_id,
            item[1].document_id,
            item[1].chunk_id,
        )
    )
    candidate_limit = min(
        query.max_candidates,
        authorization.constraints.max_evidence_items,
    )
    selected_candidates = scored_candidates[:candidate_limit]

    if not selected_candidates:
        authorized_source_count = len(
            {
                candidate.source_id
                for candidate in (
                    *keyword_candidates,
                    *vector_candidates,
                )
            }
        )

        return build_abstention_result(
            query=query,
            code=RetrievalAbstentionCode.NO_RELEVANT_EVIDENCE,
            safe_message=("No authorized evidence met the hybrid relevance threshold."),
            sources_searched=len(index.corpus.sources),
            authorized_source_count=authorized_source_count,
            completed_at=completed_at,
        )

    candidates = tuple(
        RetrievalCandidate(
            request_id=query.request_id,
            trace_id=query.trace_id,
            policy_decision_id=query.policy_decision_id,
            source_id=base_candidate.source_id,
            document_id=base_candidate.document_id,
            document_version=base_candidate.document_version,
            chunk_id=base_candidate.chunk_id,
            method=RetrievalMethod.HYBRID,
            score=score,
            rank=rank,
            freshness=base_candidate.freshness,
            citation=base_candidate.citation,
        )
        for rank, (score, base_candidate) in enumerate(
            selected_candidates,
            start=1,
        )
    )

    return RetrievalResult(
        request_id=query.request_id,
        trace_id=query.trace_id,
        query=query,
        disposition=RetrievalDisposition.CANDIDATES,
        candidates=candidates,
        abstention=None,
        completed_at=completed_at,
    )
