"""Tests for deterministic Phase 5C keyword retrieval."""

from datetime import UTC, datetime, timedelta

from incident_diagnostic_api.contracts.enums import (
    SensitivityClassification,
)
from incident_diagnostic_api.retrieval import (
    EvidenceChunk,
    EvidenceDocument,
    EvidenceLifecycleStatus,
    EvidenceSource,
    EvidenceSourceKind,
    RetrievalAbstentionCode,
    RetrievalDisposition,
    RetrievalQuery,
)
from incident_diagnostic_api.retrieval.corpus import (
    SyntheticEvidenceCorpus,
    calculate_content_hash,
)
from incident_diagnostic_api.retrieval.keyword import (
    calculate_keyword_score,
    retrieve_keywords,
    tokenize_keywords,
)

NOW = datetime(2026, 7, 20, 20, 30, tzinfo=UTC)
COMPLETED_AT = NOW + timedelta(seconds=1)


def build_source(
    *,
    source_id: str = "source-a",
    source_kind: EvidenceSourceKind = EvidenceSourceKind.RUNBOOK,
) -> EvidenceSource:
    """Return one synthetic evidence source."""

    return EvidenceSource(
        contract_version="1.0",
        source_id=source_id,
        source_kind=source_kind,
        owner_id="platform-team",
        tenant_id="tenant-a",
        service_ids=("payments-api",),
        sensitivity=SensitivityClassification.INTERNAL,
        source_version="source-v1",
        freshness_ttl_seconds=3600,
        retention_days=365,
    )


def build_document(
    *,
    source: EvidenceSource,
    document_id: str,
    content: str,
    lifecycle_status: EvidenceLifecycleStatus = (EvidenceLifecycleStatus.ACTIVE),
) -> EvidenceDocument:
    """Return one synthetic evidence document."""

    tombstoned_at = (
        NOW + timedelta(minutes=1)
        if lifecycle_status is EvidenceLifecycleStatus.TOMBSTONED
        else None
    )

    return EvidenceDocument(
        contract_version="1.0",
        document_id=document_id,
        source_id=source.source_id,
        source_kind=source.source_kind,
        document_version="doc-v1",
        title=f"Evidence for {document_id}",
        content=content,
        tenant_id=source.tenant_id,
        service_ids=source.service_ids,
        sensitivity=source.sensitivity,
        effective_at=NOW,
        content_hash=calculate_content_hash(content),
        ingested_at=NOW,
        lifecycle_status=lifecycle_status,
        tombstoned_at=tombstoned_at,
    )


def build_chunk(
    *,
    document: EvidenceDocument,
    chunk_id: str,
    content: str,
    chunk_index: int = 0,
) -> EvidenceChunk:
    """Return one synthetic evidence chunk."""

    return EvidenceChunk(
        contract_version="1.0",
        chunk_id=chunk_id,
        document_id=document.document_id,
        document_version=document.document_version,
        source_id=document.source_id,
        source_kind=document.source_kind,
        chunk_index=chunk_index,
        content=content,
        content_hash=calculate_content_hash(content),
        token_estimate=max(1, len(content.split())),
        tenant_id=document.tenant_id,
        service_ids=document.service_ids,
        sensitivity=document.sensitivity,
        lifecycle_status=document.lifecycle_status,
    )


def build_corpus() -> SyntheticEvidenceCorpus:
    """Return a corpus with two deterministically rankable chunks."""

    source = build_source()
    primary_document = build_document(
        source=source,
        document_id="document-a",
        content="Payment queue recovery procedure.",
    )
    secondary_document = build_document(
        source=source,
        document_id="document-b",
        content="Payment latency investigation.",
    )
    primary_chunk = build_chunk(
        document=primary_document,
        chunk_id="chunk-a",
        content="Payment queue recovery procedure.",
    )
    secondary_chunk = build_chunk(
        document=secondary_document,
        chunk_id="chunk-b",
        content="Payment latency investigation.",
    )

    return SyntheticEvidenceCorpus(
        corpus_id="phase5c-corpus",
        corpus_version="corpus-v1",
        sources=(source,),
        documents=(primary_document, secondary_document),
        chunks=(primary_chunk, secondary_chunk),
    )


def build_query(
    *,
    query_text: str = "payment queue",
    allowed_source_ids: tuple[str, ...] = ("source-a",),
    allowed_source_kinds: tuple[EvidenceSourceKind, ...] = (EvidenceSourceKind.RUNBOOK,),
    minimum_score: float = 0.0,
    max_candidates: int = 10,
) -> RetrievalQuery:
    """Return one valid bounded retrieval query."""

    return RetrievalQuery(
        contract_version="1.0",
        request_id="request-201",
        trace_id="trace-201",
        subject_id="engineer-201",
        tenant_id="tenant-a",
        service_id="payments-api",
        query_text=query_text,
        allowed_source_ids=allowed_source_ids,
        allowed_source_kinds=allowed_source_kinds,
        max_candidates=max_candidates,
        minimum_score=minimum_score,
        policy_decision_id="policy-decision-201",
        policy_version="policy-v1",
        authorization_expires_at=NOW + timedelta(minutes=5),
        requested_at=NOW,
    )


def test_keyword_tokenization_is_normalized_and_deterministic() -> None:
    tokens = tokenize_keywords("Payment PAYMENT queue-health, queue!")

    assert tokens == ("health", "payment", "queue")


def test_keyword_score_uses_unique_query_token_overlap() -> None:
    score = calculate_keyword_score(
        ("payment", "payment", "queue", "worker"),
        "Payment queue recovery",
    )

    assert score == 2 / 3


def test_empty_keyword_set_scores_zero() -> None:
    assert calculate_keyword_score((), "Payment queue") == 0.0


def test_keyword_retrieval_returns_ranked_candidates() -> None:
    result = retrieve_keywords(
        corpus=build_corpus(),
        query=build_query(),
        completed_at=COMPLETED_AT,
    )

    assert result.disposition is RetrievalDisposition.CANDIDATES
    assert [item.chunk_id for item in result.candidates] == [
        "chunk-a",
        "chunk-b",
    ]
    assert [item.score for item in result.candidates] == [1.0, 0.5]
    assert [item.rank for item in result.candidates] == [1, 2]


def test_same_input_produces_same_serialized_result() -> None:
    corpus = build_corpus()
    query = build_query()

    first = retrieve_keywords(
        corpus=corpus,
        query=query,
        completed_at=COMPLETED_AT,
    )
    second = retrieve_keywords(
        corpus=corpus,
        query=query,
        completed_at=COMPLETED_AT,
    )

    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_maximum_candidate_count_is_enforced() -> None:
    result = retrieve_keywords(
        corpus=build_corpus(),
        query=build_query(max_candidates=1),
        completed_at=COMPLETED_AT,
    )

    assert len(result.candidates) == 1
    assert result.candidates[0].chunk_id == "chunk-a"


def test_minimum_score_is_enforced() -> None:
    result = retrieve_keywords(
        corpus=build_corpus(),
        query=build_query(minimum_score=0.75),
        completed_at=COMPLETED_AT,
    )

    assert [item.chunk_id for item in result.candidates] == ["chunk-a"]


def test_no_candidate_meeting_threshold_abstains() -> None:
    result = retrieve_keywords(
        corpus=build_corpus(),
        query=build_query(
            query_text="unrelated evidence",
            minimum_score=0.5,
        ),
        completed_at=COMPLETED_AT,
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.abstention is not None
    assert result.abstention.code is RetrievalAbstentionCode.NO_RELEVANT_EVIDENCE


def test_punctuation_only_query_abstains() -> None:
    result = retrieve_keywords(
        corpus=build_corpus(),
        query=build_query(query_text="... !!! ---"),
        completed_at=COMPLETED_AT,
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.abstention is not None
    assert result.abstention.code is RetrievalAbstentionCode.NO_RELEVANT_EVIDENCE


def test_expired_execution_authority_abstains() -> None:
    result = retrieve_keywords(
        corpus=build_corpus(),
        query=build_query(),
        completed_at=NOW + timedelta(minutes=5),
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.abstention is not None
    assert result.abstention.code is RetrievalAbstentionCode.AUTHORIZATION_MISSING


def test_nonallowlisted_source_abstains() -> None:
    result = retrieve_keywords(
        corpus=build_corpus(),
        query=build_query(
            allowed_source_ids=("different-source",),
        ),
        completed_at=COMPLETED_AT,
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.abstention is not None
    assert result.abstention.code is RetrievalAbstentionCode.NO_AUTHORIZED_SOURCES


def test_nonallowlisted_source_kind_abstains() -> None:
    result = retrieve_keywords(
        corpus=build_corpus(),
        query=build_query(
            allowed_source_kinds=(EvidenceSourceKind.SERVICE_CATALOG,),
        ),
        completed_at=COMPLETED_AT,
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.abstention is not None
    assert result.abstention.code is RetrievalAbstentionCode.NO_AUTHORIZED_SOURCES


def test_tombstoned_chunk_is_excluded() -> None:
    source = build_source()
    document = build_document(
        source=source,
        document_id="deleted-document",
        content="Payment queue recovery.",
        lifecycle_status=EvidenceLifecycleStatus.TOMBSTONED,
    )
    chunk = build_chunk(
        document=document,
        chunk_id="deleted-chunk",
        content="Payment queue recovery.",
    )
    corpus = SyntheticEvidenceCorpus(
        corpus_id="tombstoned-corpus",
        corpus_version="corpus-v1",
        sources=(source,),
        documents=(document,),
        chunks=(chunk,),
    )

    result = retrieve_keywords(
        corpus=corpus,
        query=build_query(),
        completed_at=COMPLETED_AT,
    )

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.abstention is not None
    assert result.abstention.code is RetrievalAbstentionCode.NO_AUTHORIZED_SOURCES


def test_equal_scores_use_stable_document_order() -> None:
    source = build_source()
    document_b = build_document(
        source=source,
        document_id="document-b",
        content="Payment queue.",
    )
    document_a = build_document(
        source=source,
        document_id="document-a",
        content="Payment queue.",
    )
    chunk_b = build_chunk(
        document=document_b,
        chunk_id="chunk-b",
        content="Payment queue.",
    )
    chunk_a = build_chunk(
        document=document_a,
        chunk_id="chunk-a",
        content="Payment queue.",
    )
    corpus = SyntheticEvidenceCorpus(
        corpus_id="tie-corpus",
        corpus_version="corpus-v1",
        sources=(source,),
        documents=(document_b, document_a),
        chunks=(chunk_b, chunk_a),
    )

    result = retrieve_keywords(
        corpus=corpus,
        query=build_query(),
        completed_at=COMPLETED_AT,
    )

    assert [item.document_id for item in result.candidates] == [
        "document-a",
        "document-b",
    ]


def test_candidate_preserves_query_and_citation_lineage() -> None:
    result = retrieve_keywords(
        corpus=build_corpus(),
        query=build_query(),
        completed_at=COMPLETED_AT,
    )
    candidate = result.candidates[0]

    assert candidate.request_id == result.query.request_id
    assert candidate.trace_id == result.query.trace_id
    assert candidate.policy_decision_id == result.query.policy_decision_id
    assert candidate.chunk_id == candidate.citation.chunk_id
    assert candidate.source_id == candidate.citation.source_id
    assert candidate.citation.retrieved_at == COMPLETED_AT


def test_retrieval_does_not_mutate_corpus_or_query() -> None:
    corpus = build_corpus()
    query = build_query()
    corpus_before = corpus.model_dump(mode="json")
    query_before = query.model_dump(mode="json")

    retrieve_keywords(
        corpus=corpus,
        query=query,
        completed_at=COMPLETED_AT,
    )

    assert corpus.model_dump(mode="json") == corpus_before
    assert query.model_dump(mode="json") == query_before
