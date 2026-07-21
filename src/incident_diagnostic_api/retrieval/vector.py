"""Deterministic vector retrieval over authorized synthetic evidence."""

from dataclasses import dataclass
from typing import Final

from incident_diagnostic_api.contracts import AuthorizationDecision
from incident_diagnostic_api.contracts.common import Timestamp
from incident_diagnostic_api.contracts.enums import FreshnessStatus
from incident_diagnostic_api.retrieval.corpus import SyntheticEvidenceCorpus
from incident_diagnostic_api.retrieval.embeddings import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_VERSION,
    EmbeddingVector,
    cosine_similarity,
    embed_text,
)
from incident_diagnostic_api.retrieval.enums import (
    RetrievalAbstentionCode,
    RetrievalDisposition,
    RetrievalMethod,
)
from incident_diagnostic_api.retrieval.models import (
    Citation,
    EvidenceChunk,
    RetrievalCandidate,
    RetrievalQuery,
    RetrievalResult,
)
from incident_diagnostic_api.retrieval.security import (
    authorization_matches_query,
    authorized_active_chunks,
    build_abstention_result,
)

VECTOR_INDEX_VERSION: Final[str] = "synthetic-vector-index-v1"


@dataclass(frozen=True, slots=True)
class VectorIndexEntry:
    """One immutable content-addressed synthetic vector entry."""

    chunk_id: str
    content_hash: str
    embedding_version: str
    vector: EmbeddingVector

    def __post_init__(self) -> None:
        if not self.chunk_id:
            raise ValueError("vector entry requires a chunk identifier")

        if not self.content_hash:
            raise ValueError("vector entry requires a content hash")

        if self.embedding_version != EMBEDDING_VERSION:
            raise ValueError("vector entry embedding version is unsupported")

        if len(self.vector) != EMBEDDING_DIMENSIONS:
            raise ValueError("vector entry has an invalid dimension")


@dataclass(frozen=True, slots=True)
class SyntheticVectorIndex:
    """Immutable vectors aligned with one synthetic evidence corpus."""

    index_version: str
    embedding_version: str
    corpus: SyntheticEvidenceCorpus
    entries: tuple[VectorIndexEntry, ...]

    def __post_init__(self) -> None:
        if self.index_version != VECTOR_INDEX_VERSION:
            raise ValueError("vector index version is unsupported")

        if self.embedding_version != EMBEDDING_VERSION:
            raise ValueError("vector index embedding version is unsupported")

        expected_chunks = {chunk.chunk_id: chunk for chunk in self.corpus.chunks}
        actual_entries = {entry.chunk_id: entry for entry in self.entries}

        if len(actual_entries) != len(self.entries):
            raise ValueError("vector index contains duplicate chunk entries")

        if set(actual_entries) != set(expected_chunks):
            raise ValueError("vector index must cover the corpus exactly")

        for chunk_id, chunk in expected_chunks.items():
            entry = actual_entries[chunk_id]

            if entry.content_hash != chunk.content_hash:
                raise ValueError("vector entry content hash does not match its chunk")

            if entry.embedding_version != self.embedding_version:
                raise ValueError("vector entry embedding version does not match its index")

    def entry_for(self, chunk: EvidenceChunk) -> VectorIndexEntry:
        """Return the integrity-aligned entry for one corpus chunk."""

        for entry in self.entries:
            if entry.chunk_id == chunk.chunk_id:
                if entry.content_hash != chunk.content_hash:
                    raise ValueError("vector entry content hash does not match its chunk")

                return entry

        raise ValueError("vector index does not contain the requested chunk")


def build_vector_index(
    corpus: SyntheticEvidenceCorpus,
) -> SyntheticVectorIndex:
    """Build a deterministic immutable index over synthetic chunks."""

    entries = tuple(
        VectorIndexEntry(
            chunk_id=chunk.chunk_id,
            content_hash=chunk.content_hash,
            embedding_version=EMBEDDING_VERSION,
            vector=embed_text(chunk.content),
        )
        for chunk in sorted(
            corpus.chunks,
            key=lambda item: (
                item.source_id,
                item.document_id,
                item.chunk_index,
                item.chunk_id,
            ),
        )
    )

    return SyntheticVectorIndex(
        index_version=VECTOR_INDEX_VERSION,
        embedding_version=EMBEDDING_VERSION,
        corpus=corpus,
        entries=entries,
    )


def retrieve_vectors(
    *,
    index: SyntheticVectorIndex,
    query: RetrievalQuery,
    authorization: AuthorizationDecision,
    completed_at: Timestamp,
) -> RetrievalResult:
    """Retrieve authorized synthetic evidence by cosine similarity."""

    sources_searched = len(index.corpus.sources)

    if not authorization_matches_query(
        authorization=authorization,
        query=query,
        completed_at=completed_at,
    ):
        return build_abstention_result(
            query=query,
            code=RetrievalAbstentionCode.AUTHORIZATION_MISSING,
            safe_message="Retrieval authorization is no longer valid.",
            sources_searched=sources_searched,
            authorized_source_count=0,
            completed_at=completed_at,
        )

    query_vector = embed_text(query.query_text)

    if not any(query_vector):
        return build_abstention_result(
            query=query,
            code=RetrievalAbstentionCode.NO_RELEVANT_EVIDENCE,
            safe_message="The query cannot produce a local embedding.",
            sources_searched=sources_searched,
            authorized_source_count=0,
            completed_at=completed_at,
        )

    chunks = authorized_active_chunks(
        index.corpus,
        query,
        authorization,
    )
    authorized_source_count = len({chunk.source_id for chunk in chunks})

    if not chunks:
        return build_abstention_result(
            query=query,
            code=RetrievalAbstentionCode.NO_AUTHORIZED_SOURCES,
            safe_message="No active evidence sources are authorized.",
            sources_searched=sources_searched,
            authorized_source_count=0,
            completed_at=completed_at,
        )

    scored_chunks = [
        (
            max(
                0.0,
                cosine_similarity(
                    query_vector,
                    index.entry_for(chunk).vector,
                ),
            ),
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
    candidate_limit = min(
        query.max_candidates,
        authorization.constraints.max_evidence_items,
    )
    selected_chunks = eligible_chunks[:candidate_limit]

    if not selected_chunks:
        return build_abstention_result(
            query=query,
            code=RetrievalAbstentionCode.NO_RELEVANT_EVIDENCE,
            safe_message=("No authorized evidence met the vector relevance threshold."),
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
            method=RetrievalMethod.VECTOR,
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
