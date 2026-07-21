"""Deterministic read-only keyword retrieval over synthetic evidence."""

import re
from collections.abc import Iterable
from typing import Final

from incident_diagnostic_api.contracts.common import Timestamp
from incident_diagnostic_api.contracts.enums import FreshnessStatus
from incident_diagnostic_api.retrieval.corpus import (
    SyntheticEvidenceCorpus,
)
from incident_diagnostic_api.retrieval.enums import (
    EvidenceLifecycleStatus,
    RetrievalAbstentionCode,
    RetrievalDisposition,
    RetrievalMethod,
)
from incident_diagnostic_api.retrieval.models import (
    Citation,
    EvidenceChunk,
    RetrievalAbstention,
    RetrievalCandidate,
    RetrievalQuery,
    RetrievalResult,
)

_TOKEN_PATTERN: Final[re.Pattern[str]] = re.compile(r"[a-z0-9]+")


def tokenize_keywords(text: str) -> tuple[str, ...]:
    """Return unique normalized tokens in deterministic sorted order."""

    return tuple(sorted(set(_TOKEN_PATTERN.findall(text.casefold()))))


def calculate_keyword_score(
    query_tokens: Iterable[str],
    content: str,
) -> float:
    """Return the fraction of unique query tokens found in content."""

    normalized_query = frozenset(query_tokens)

    if not normalized_query:
        return 0.0

    content_tokens = frozenset(tokenize_keywords(content))
    overlap_count = len(normalized_query & content_tokens)

    return overlap_count / len(normalized_query)


def _authorized_active_chunks(
    corpus: SyntheticEvidenceCorpus,
    query: RetrievalQuery,
) -> tuple[EvidenceChunk, ...]:
    """Apply Phase 5C source scope and lifecycle checks before scoring."""

    allowed_source_ids = frozenset(query.allowed_source_ids)
    allowed_source_kinds = frozenset(query.allowed_source_kinds)

    return tuple(
        chunk
        for chunk in corpus.chunks
        if chunk.source_id in allowed_source_ids
        and chunk.source_kind in allowed_source_kinds
        and chunk.lifecycle_status is EvidenceLifecycleStatus.ACTIVE
    )


def _abstain(
    *,
    query: RetrievalQuery,
    code: RetrievalAbstentionCode,
    safe_message: str,
    sources_searched: int,
    authorized_source_count: int,
    completed_at: Timestamp,
) -> RetrievalResult:
    """Return one explicit, correlated abstention result."""

    abstention = RetrievalAbstention(
        request_id=query.request_id,
        trace_id=query.trace_id,
        code=code,
        reason_codes=(code.value,),
        sources_searched=sources_searched,
        authorized_source_count=authorized_source_count,
        candidate_count=0,
        safe_message=safe_message,
        occurred_at=completed_at,
    )

    return RetrievalResult(
        request_id=query.request_id,
        trace_id=query.trace_id,
        query=query,
        disposition=RetrievalDisposition.ABSTENTION,
        candidates=(),
        abstention=abstention,
        completed_at=completed_at,
    )


def retrieve_keywords(
    *,
    corpus: SyntheticEvidenceCorpus,
    query: RetrievalQuery,
    completed_at: Timestamp,
) -> RetrievalResult:
    """Retrieve deterministically ranked synthetic keyword evidence."""

    sources_searched = len(corpus.sources)

    if completed_at >= query.authorization_expires_at:
        return _abstain(
            query=query,
            code=RetrievalAbstentionCode.AUTHORIZATION_MISSING,
            safe_message="Retrieval authorization is no longer valid.",
            sources_searched=sources_searched,
            authorized_source_count=0,
            completed_at=completed_at,
        )

    query_tokens = tokenize_keywords(query.query_text)

    if not query_tokens:
        return _abstain(
            query=query,
            code=RetrievalAbstentionCode.NO_RELEVANT_EVIDENCE,
            safe_message="The query contains no searchable keywords.",
            sources_searched=sources_searched,
            authorized_source_count=0,
            completed_at=completed_at,
        )

    chunks = _authorized_active_chunks(corpus, query)
    authorized_source_ids = {chunk.source_id for chunk in chunks}
    authorized_source_count = len(authorized_source_ids)

    if not chunks:
        return _abstain(
            query=query,
            code=RetrievalAbstentionCode.NO_AUTHORIZED_SOURCES,
            safe_message="No active evidence sources are authorized.",
            sources_searched=sources_searched,
            authorized_source_count=0,
            completed_at=completed_at,
        )

    scored_chunks = [
        (
            calculate_keyword_score(query_tokens, chunk.content),
            chunk,
        )
        for chunk in chunks
    ]
    eligible_chunks = [
        (score, chunk)
        for score, chunk in scored_chunks
        if score > 0.0 and score >= query.minimum_score
    ]
    eligible_chunks.sort(
        key=lambda item: (
            -item[0],
            item[1].source_id,
            item[1].document_id,
            item[1].chunk_index,
            item[1].chunk_id,
        )
    )
    selected_chunks = eligible_chunks[: query.max_candidates]

    if not selected_chunks:
        return _abstain(
            query=query,
            code=RetrievalAbstentionCode.NO_RELEVANT_EVIDENCE,
            safe_message=("No authorized evidence met the keyword relevance threshold."),
            sources_searched=sources_searched,
            authorized_source_count=authorized_source_count,
            completed_at=completed_at,
        )

    candidates = tuple(
        RetrievalCandidate(
            request_id=query.request_id,
            trace_id=query.trace_id,
            policy_decision_id=query.policy_decision_id,
            source_id=chunk.source_id,
            document_id=chunk.document_id,
            document_version=chunk.document_version,
            chunk_id=chunk.chunk_id,
            method=RetrievalMethod.KEYWORD,
            score=score,
            rank=rank,
            freshness=FreshnessStatus.CURRENT,
            citation=Citation(
                source_id=chunk.source_id,
                document_id=chunk.document_id,
                document_version=chunk.document_version,
                chunk_id=chunk.chunk_id,
                content_hash=chunk.content_hash,
                locator=f"chunk:{chunk.chunk_index}",
                retrieved_at=completed_at,
            ),
        )
        for rank, (score, chunk) in enumerate(
            selected_chunks,
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
