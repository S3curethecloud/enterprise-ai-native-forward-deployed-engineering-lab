"""Tests for deterministic authorized Phase 5E vector retrieval."""

from dataclasses import FrozenInstanceError, replace
from math import isclose

import pytest

import incident_diagnostic_api.retrieval.vector as vector_module
from incident_diagnostic_api.retrieval import (
    EvidenceLifecycleStatus,
    RetrievalAbstentionCode,
    RetrievalDisposition,
    RetrievalMethod,
    RetrievalResult,
)
from incident_diagnostic_api.retrieval.corpus import SyntheticEvidenceCorpus
from incident_diagnostic_api.retrieval.embeddings import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_VERSION,
)
from incident_diagnostic_api.retrieval.vector import (
    VECTOR_INDEX_VERSION,
    SyntheticVectorIndex,
    VectorIndexEntry,
    build_vector_index,
    retrieve_vectors,
)
from tests.retrieval.test_keyword import (
    COMPLETED_AT,
    build_authorization,
    build_chunk,
    build_corpus,
    build_document,
    build_query,
    build_source,
)


def execute_vector_retrieval(
    *,
    corpus: SyntheticEvidenceCorpus | None = None,
    query_text: str = "payment queue",
    minimum_score: float = 0.0,
    max_candidates: int = 10,
    allowed_tenant_ids: tuple[str, ...] = ("tenant-a",),
    allowed_service_ids: tuple[str, ...] = ("payments-api",),
    allowed_sensitivities: tuple[str, ...] = ("internal",),
    allowed_source_types: tuple[str, ...] = ("runbook",),
    max_evidence_items: int = 50,
) -> RetrievalResult:
    """Execute vector retrieval with matching bounded authority."""

    resolved_corpus = build_corpus() if corpus is None else corpus
    query = build_query(
        query_text=query_text,
        minimum_score=minimum_score,
        max_candidates=max_candidates,
    )
    authorization = build_authorization(
        query=query,
        allowed_tenant_ids=allowed_tenant_ids,
        allowed_service_ids=allowed_service_ids,
        allowed_sensitivities=allowed_sensitivities,
        allowed_source_types=allowed_source_types,
        max_evidence_items=max_evidence_items,
    )

    return retrieve_vectors(
        index=build_vector_index(resolved_corpus),
        query=query,
        authorization=authorization,
        completed_at=COMPLETED_AT,
    )


def build_tie_corpus() -> SyntheticEvidenceCorpus:
    """Return equal-vector chunks in reverse insertion order."""

    source = build_source()
    document_a = build_document(
        source=source,
        document_id="document-a",
        content="Payment queue.",
    )
    document_b = build_document(
        source=source,
        document_id="document-b",
        content="Payment queue.",
    )
    chunk_a = build_chunk(
        document=document_a,
        chunk_id="chunk-a",
        content="Payment queue.",
    )
    chunk_b = build_chunk(
        document=document_b,
        chunk_id="chunk-b",
        content="Payment queue.",
    )

    return SyntheticEvidenceCorpus(
        corpus_id="phase5e-tie-corpus",
        corpus_version="corpus-v1",
        sources=(source,),
        documents=(document_b, document_a),
        chunks=(chunk_b, chunk_a),
    )


def test_vector_index_versions_are_explicit() -> None:
    index = build_vector_index(build_corpus())

    assert index.index_version == VECTOR_INDEX_VERSION
    assert index.embedding_version == EMBEDDING_VERSION


def test_vector_index_covers_every_corpus_chunk() -> None:
    corpus = build_corpus()
    index = build_vector_index(corpus)

    assert {entry.chunk_id for entry in index.entries} == {
        chunk.chunk_id for chunk in corpus.chunks
    }
    assert all(len(entry.vector) == EMBEDDING_DIMENSIONS for entry in index.entries)


def test_vector_index_build_is_deterministic() -> None:
    corpus = build_corpus()

    assert build_vector_index(corpus) == build_vector_index(corpus)


def test_vector_index_is_immutable() -> None:
    index = build_vector_index(build_corpus())

    with pytest.raises(FrozenInstanceError):
        index.index_version = "changed"  # type: ignore[misc]


def test_missing_vector_entry_is_rejected() -> None:
    index = build_vector_index(build_corpus())

    with pytest.raises(
        ValueError,
        match="cover the corpus exactly",
    ):
        SyntheticVectorIndex(
            index_version=index.index_version,
            embedding_version=index.embedding_version,
            corpus=index.corpus,
            entries=index.entries[:-1],
        )


def test_duplicate_vector_entry_is_rejected() -> None:
    index = build_vector_index(build_corpus())

    with pytest.raises(
        ValueError,
        match="duplicate chunk entries",
    ):
        SyntheticVectorIndex(
            index_version=index.index_version,
            embedding_version=index.embedding_version,
            corpus=index.corpus,
            entries=(index.entries[0], index.entries[0]),
        )


def test_vector_entry_content_hash_mismatch_is_rejected() -> None:
    index = build_vector_index(build_corpus())
    changed = replace(
        index.entries[0],
        content_hash="0" * 64,
    )

    with pytest.raises(
        ValueError,
        match="content hash does not match",
    ):
        SyntheticVectorIndex(
            index_version=index.index_version,
            embedding_version=index.embedding_version,
            corpus=index.corpus,
            entries=(changed, *index.entries[1:]),
        )


def test_vector_entry_embedding_version_mismatch_is_rejected() -> None:
    index = build_vector_index(build_corpus())

    with pytest.raises(
        ValueError,
        match="embedding version is unsupported",
    ):
        VectorIndexEntry(
            chunk_id=index.entries[0].chunk_id,
            content_hash=index.entries[0].content_hash,
            embedding_version="unknown-embedding",
            vector=index.entries[0].vector,
        )


def test_vector_entry_dimension_mismatch_is_rejected() -> None:
    index = build_vector_index(build_corpus())

    with pytest.raises(
        ValueError,
        match="invalid dimension",
    ):
        VectorIndexEntry(
            chunk_id=index.entries[0].chunk_id,
            content_hash=index.entries[0].content_hash,
            embedding_version=EMBEDDING_VERSION,
            vector=(1.0,),
        )


def test_vector_retrieval_returns_ranked_candidates() -> None:
    result = execute_vector_retrieval()

    assert result.disposition is RetrievalDisposition.CANDIDATES
    assert [candidate.chunk_id for candidate in result.candidates] == [
        "chunk-a",
        "chunk-b",
    ]
    assert [candidate.rank for candidate in result.candidates] == [1, 2]
    assert all(candidate.method is RetrievalMethod.VECTOR for candidate in result.candidates)


def test_vector_candidate_preserves_citation_integrity() -> None:
    result = execute_vector_retrieval()
    candidate = result.candidates[0]

    assert candidate.chunk_id == candidate.citation.chunk_id
    assert candidate.document_id == candidate.citation.document_id
    assert candidate.source_id == candidate.citation.source_id
    assert candidate.citation.content_hash


def test_vector_retrieval_is_repeatable() -> None:
    corpus = build_corpus()
    index = build_vector_index(corpus)
    query = build_query()
    authorization = build_authorization(query=query)

    first = retrieve_vectors(
        index=index,
        query=query,
        authorization=authorization,
        completed_at=COMPLETED_AT,
    )
    second = retrieve_vectors(
        index=index,
        query=query,
        authorization=authorization,
        completed_at=COMPLETED_AT,
    )

    assert first == second


def test_empty_embedding_query_abstains() -> None:
    result = execute_vector_retrieval(query_text="!!!")

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.abstention is not None
    assert result.abstention.code is RetrievalAbstentionCode.NO_RELEVANT_EVIDENCE


def test_vector_threshold_without_match_abstains() -> None:
    result = execute_vector_retrieval(
        query_text="database latency",
        minimum_score=0.9,
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.abstention is not None
    assert result.abstention.code is RetrievalAbstentionCode.NO_RELEVANT_EVIDENCE


def test_tenant_scope_is_enforced_before_vector_scoring() -> None:
    result = execute_vector_retrieval(
        allowed_tenant_ids=("tenant-b",),
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.abstention is not None
    assert result.abstention.code is RetrievalAbstentionCode.NO_AUTHORIZED_SOURCES


def test_service_scope_is_enforced_before_vector_scoring() -> None:
    result = execute_vector_retrieval(
        allowed_service_ids=("inventory-api",),
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION


def test_classification_scope_is_enforced_before_vector_scoring() -> None:
    result = execute_vector_retrieval(
        allowed_sensitivities=("public",),
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION


def test_source_type_scope_is_enforced_before_vector_scoring() -> None:
    result = execute_vector_retrieval(
        allowed_source_types=("service_metadata",),
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION


def test_rejected_chunks_never_reach_cosine_scoring(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_called(
        left: tuple[float, ...],
        right: tuple[float, ...],
    ) -> float:
        raise AssertionError(f"unauthorized vectors were scored: {len(left)}, {len(right)}")

    monkeypatch.setattr(
        vector_module,
        "cosine_similarity",
        fail_if_called,
    )

    result = execute_vector_retrieval(
        allowed_tenant_ids=("tenant-b",),
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION


def test_policy_result_limit_overrides_query_limit() -> None:
    result = execute_vector_retrieval(
        max_candidates=10,
        max_evidence_items=1,
    )

    assert len(result.candidates) == 1


def test_query_result_limit_can_narrow_policy_limit() -> None:
    result = execute_vector_retrieval(
        max_candidates=1,
        max_evidence_items=10,
    )

    assert len(result.candidates) == 1


def test_equal_scores_use_stable_identifier_tie_breaking() -> None:
    result = execute_vector_retrieval(
        corpus=build_tie_corpus(),
    )

    assert [candidate.chunk_id for candidate in result.candidates] == [
        "chunk-a",
        "chunk-b",
    ]
    assert isclose(
        result.candidates[0].score,
        result.candidates[1].score,
    )


def test_tombstoned_content_is_not_vector_scored() -> None:
    source = build_source()
    document = build_document(
        source=source,
        document_id="document-tombstoned",
        content="Payment queue.",
        lifecycle_status=EvidenceLifecycleStatus.TOMBSTONED,
    )
    chunk = build_chunk(
        document=document,
        chunk_id="chunk-tombstoned",
        content="Payment queue.",
    )
    corpus = SyntheticEvidenceCorpus(
        corpus_id="phase5e-tombstone-corpus",
        corpus_version="corpus-v1",
        sources=(source,),
        documents=(document,),
        chunks=(chunk,),
    )

    result = execute_vector_retrieval(corpus=corpus)

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.abstention is not None
    assert result.abstention.code is RetrievalAbstentionCode.NO_AUTHORIZED_SOURCES
