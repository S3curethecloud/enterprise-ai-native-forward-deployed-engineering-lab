"""Tests for the immutable Phase 5C synthetic evidence corpus."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.contracts.enums import (
    SensitivityClassification,
)
from incident_diagnostic_api.retrieval import (
    EvidenceChunk,
    EvidenceDocument,
    EvidenceLifecycleStatus,
    EvidenceSource,
    EvidenceSourceKind,
)
from incident_diagnostic_api.retrieval.corpus import (
    SyntheticEvidenceCorpus,
    calculate_content_hash,
)

NOW = datetime(2026, 7, 20, 19, 30, tzinfo=UTC)
DOCUMENT_CONTENT = "Validate queue health before restarting the payment worker."
CHUNK_CONTENT = "Validate queue health before restarting the worker."


def build_source() -> EvidenceSource:
    """Return valid synthetic source metadata."""

    return EvidenceSource(
        contract_version="1.0",
        source_id="synthetic-runbooks",
        source_kind=EvidenceSourceKind.RUNBOOK,
        owner_id="platform-team",
        tenant_id="tenant-a",
        service_ids=("payments-api",),
        sensitivity=SensitivityClassification.INTERNAL,
        source_version="source-v1",
        freshness_ttl_seconds=3600,
        retention_days=365,
    )


def build_document(
    source: EvidenceSource,
) -> EvidenceDocument:
    """Return a valid synthetic evidence document."""

    return EvidenceDocument(
        contract_version="1.0",
        document_id="payment-worker-runbook",
        source_id=source.source_id,
        source_kind=source.source_kind,
        document_version="doc-v1",
        title="Payment worker recovery",
        content=DOCUMENT_CONTENT,
        tenant_id=source.tenant_id,
        service_ids=source.service_ids,
        sensitivity=source.sensitivity,
        effective_at=NOW,
        content_hash=calculate_content_hash(DOCUMENT_CONTENT),
        ingested_at=NOW,
        lifecycle_status=EvidenceLifecycleStatus.ACTIVE,
    )


def build_chunk(
    document: EvidenceDocument,
) -> EvidenceChunk:
    """Return a valid synthetic evidence chunk."""

    return EvidenceChunk(
        contract_version="1.0",
        chunk_id="payment-worker-runbook-chunk-0",
        document_id=document.document_id,
        document_version=document.document_version,
        source_id=document.source_id,
        source_kind=document.source_kind,
        chunk_index=0,
        content=CHUNK_CONTENT,
        content_hash=calculate_content_hash(CHUNK_CONTENT),
        token_estimate=8,
        tenant_id=document.tenant_id,
        service_ids=document.service_ids,
        sensitivity=document.sensitivity,
        lifecycle_status=document.lifecycle_status,
    )


def build_corpus() -> SyntheticEvidenceCorpus:
    """Return a valid synthetic evidence corpus."""

    source = build_source()
    document = build_document(source)
    chunk = build_chunk(document)

    return SyntheticEvidenceCorpus(
        corpus_id="phase5c-synthetic-corpus",
        corpus_version="corpus-v1",
        sources=(source,),
        documents=(document,),
        chunks=(chunk,),
    )


def corpus_payload() -> dict[str, Any]:
    """Return a mutable payload for negative corpus tests."""

    corpus = build_corpus()
    return {
        "corpus_id": corpus.corpus_id,
        "corpus_version": corpus.corpus_version,
        "sources": corpus.sources,
        "documents": corpus.documents,
        "chunks": corpus.chunks,
    }


def test_valid_synthetic_corpus_is_accepted() -> None:
    corpus = build_corpus()

    assert len(corpus.sources) == 1
    assert len(corpus.documents) == 1
    assert len(corpus.chunks) == 1


def test_content_hash_is_deterministic() -> None:
    first = calculate_content_hash(CHUNK_CONTENT)
    second = calculate_content_hash(CHUNK_CONTENT)

    assert first == second
    assert len(first) == 64


def test_content_hash_detects_content_change() -> None:
    original = calculate_content_hash(CHUNK_CONTENT)
    changed = calculate_content_hash(f"{CHUNK_CONTENT} changed")

    assert original != changed


def test_synthetic_corpus_is_immutable() -> None:
    corpus = build_corpus()

    with pytest.raises(ValidationError):
        corpus.corpus_version = "corpus-v2"


def test_source_identifiers_must_be_unique() -> None:
    payload = corpus_payload()
    source = payload["sources"][0]
    payload["sources"] = (source, source)

    with pytest.raises(
        ValidationError,
        match="source identifiers must be unique",
    ):
        SyntheticEvidenceCorpus.model_validate(payload)


def test_document_identifiers_must_be_unique() -> None:
    payload = corpus_payload()
    document = payload["documents"][0]
    payload["documents"] = (document, document)

    with pytest.raises(
        ValidationError,
        match="document identifiers must be unique",
    ):
        SyntheticEvidenceCorpus.model_validate(payload)


def test_chunk_identifiers_must_be_unique() -> None:
    payload = corpus_payload()
    chunk = payload["chunks"][0]
    payload["chunks"] = (chunk, chunk)

    with pytest.raises(
        ValidationError,
        match="chunk identifiers must be unique",
    ):
        SyntheticEvidenceCorpus.model_validate(payload)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        (
            "source_id",
            "missing-source",
            "every document must reference a corpus source",
        ),
        (
            "source_kind",
            EvidenceSourceKind.SERVICE_CATALOG,
            "document source kind must match its source",
        ),
        (
            "tenant_id",
            "tenant-b",
            "document tenant must match its source tenant",
        ),
        (
            "service_ids",
            ("inventory-api",),
            "document services must be allowed by its source",
        ),
        (
            "sensitivity",
            SensitivityClassification.CONFIDENTIAL,
            "document sensitivity must match its source",
        ),
        (
            "content_hash",
            "0" * 64,
            "document content hash is invalid",
        ),
    ],
)
def test_document_lineage_or_integrity_mismatch_is_rejected(
    field: str,
    value: object,
    message: str,
) -> None:
    payload = corpus_payload()
    document = payload["documents"][0]
    payload["documents"] = (document.model_copy(update={field: value}),)

    with pytest.raises(ValidationError, match=message):
        SyntheticEvidenceCorpus.model_validate(payload)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        (
            "document_id",
            "missing-document",
            "every chunk must reference a corpus document",
        ),
        (
            "document_version",
            "doc-v2",
            "chunk document version must match its document",
        ),
        (
            "source_id",
            "different-source",
            "chunk source must match its document source",
        ),
        (
            "source_kind",
            EvidenceSourceKind.SERVICE_CATALOG,
            "chunk source kind must match its document",
        ),
        (
            "tenant_id",
            "tenant-b",
            "chunk tenant must match its document tenant",
        ),
        (
            "service_ids",
            ("inventory-api",),
            "chunk services must match its document services",
        ),
        (
            "sensitivity",
            SensitivityClassification.CONFIDENTIAL,
            "chunk sensitivity must match its document",
        ),
        (
            "lifecycle_status",
            EvidenceLifecycleStatus.TOMBSTONED,
            "chunk lifecycle must match its document lifecycle",
        ),
        (
            "content_hash",
            "0" * 64,
            "chunk content hash is invalid",
        ),
    ],
)
def test_chunk_lineage_or_integrity_mismatch_is_rejected(
    field: str,
    value: object,
    message: str,
) -> None:
    payload = corpus_payload()
    chunk = payload["chunks"][0]
    payload["chunks"] = (chunk.model_copy(update={field: value}),)

    with pytest.raises(ValidationError, match=message):
        SyntheticEvidenceCorpus.model_validate(payload)


def test_unknown_corpus_field_is_rejected() -> None:
    payload = corpus_payload()
    payload["external_source_url"] = "https://example.invalid"

    with pytest.raises(ValidationError):
        SyntheticEvidenceCorpus.model_validate(payload)
