"""Tests for immutable permission-aware retrieval contracts."""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.contracts.enums import (
    FreshnessStatus,
    SensitivityClassification,
)
from incident_diagnostic_api.retrieval import (
    Citation,
    EvidenceDocument,
    EvidenceLifecycleStatus,
    EvidenceSource,
    EvidenceSourceKind,
    RetrievalAbstention,
    RetrievalAbstentionCode,
    RetrievalCandidate,
    RetrievalDisposition,
    RetrievalMethod,
    RetrievalQuery,
    RetrievalResult,
)

NOW = datetime(2026, 7, 20, 18, 30, tzinfo=UTC)


def source_payload() -> dict[str, Any]:
    """Return valid evidence-source metadata."""

    return {
        "contract_version": "1.0",
        "source_id": "runbook-source-101",
        "source_kind": EvidenceSourceKind.RUNBOOK,
        "owner_id": "platform-operations",
        "tenant_id": "tenant-a",
        "service_ids": ["payments-api"],
        "sensitivity": SensitivityClassification.INTERNAL,
        "source_version": "source-v1",
        "freshness_ttl_seconds": 3600,
        "retention_days": 365,
        "authoritative": True,
    }


def document_payload() -> dict[str, Any]:
    """Return a valid active evidence document."""

    return {
        "contract_version": "1.0",
        "document_id": "runbook-doc-101",
        "source_id": "runbook-source-101",
        "source_kind": EvidenceSourceKind.RUNBOOK,
        "document_version": "doc-v1",
        "title": "Payments API latency runbook",
        "content": "Validate upstream latency and dependency health.",
        "tenant_id": "tenant-a",
        "service_ids": ["payments-api"],
        "sensitivity": SensitivityClassification.INTERNAL,
        "effective_at": NOW,
        "expires_at": NOW + timedelta(days=30),
        "content_hash": "abcdef1234567890",
        "ingested_at": NOW + timedelta(minutes=1),
        "lifecycle_status": EvidenceLifecycleStatus.ACTIVE,
        "tombstoned_at": None,
    }


def query_payload() -> dict[str, Any]:
    """Return a valid authorized retrieval query."""

    return {
        "contract_version": "1.0",
        "request_id": "request-101",
        "trace_id": "trace-101",
        "subject_id": "engineer-101",
        "tenant_id": "tenant-a",
        "service_id": "payments-api",
        "query_text": "Why is the payments API latency elevated?",
        "allowed_source_ids": ["runbook-source-101"],
        "allowed_source_kinds": [EvidenceSourceKind.RUNBOOK],
        "time_window_start": NOW - timedelta(hours=1),
        "time_window_end": NOW,
        "max_candidates": 10,
        "minimum_score": 0.5,
        "policy_decision_id": "policy-decision-101",
        "policy_version": "policy-v1",
        "authorization_expires_at": NOW + timedelta(minutes=5),
        "requested_at": NOW,
    }


def citation_payload() -> dict[str, Any]:
    """Return valid citation lineage."""

    return {
        "source_id": "runbook-source-101",
        "document_id": "runbook-doc-101",
        "document_version": "doc-v1",
        "chunk_id": "chunk-101",
        "content_hash": "abcdef1234567890",
        "locator": "section 2, paragraph 1",
        "retrieved_at": NOW + timedelta(seconds=1),
    }


def candidate_payload(*, rank: int = 1) -> dict[str, Any]:
    """Return a valid authorized retrieval candidate."""

    return {
        "request_id": "request-101",
        "trace_id": "trace-101",
        "policy_decision_id": "policy-decision-101",
        "source_id": "runbook-source-101",
        "document_id": "runbook-doc-101",
        "document_version": "doc-v1",
        "chunk_id": "chunk-101",
        "method": RetrievalMethod.HYBRID,
        "score": 0.91,
        "rank": rank,
        "freshness": FreshnessStatus.CURRENT,
        "citation": citation_payload(),
    }


def abstention_payload() -> dict[str, Any]:
    """Return a valid fail-closed abstention."""

    return {
        "request_id": "request-101",
        "trace_id": "trace-101",
        "disposition": RetrievalDisposition.ABSTENTION,
        "code": RetrievalAbstentionCode.NO_RELEVANT_EVIDENCE,
        "reason_codes": ["NO_RELEVANT_EVIDENCE"],
        "sources_searched": 1,
        "authorized_source_count": 1,
        "candidate_count": 0,
        "safe_message": "No sufficiently relevant authorized evidence was found.",
        "occurred_at": NOW + timedelta(seconds=2),
    }


def result_payload() -> dict[str, Any]:
    """Return a valid candidate result."""

    return {
        "request_id": "request-101",
        "trace_id": "trace-101",
        "query": query_payload(),
        "disposition": RetrievalDisposition.CANDIDATES,
        "candidates": [candidate_payload()],
        "abstention": None,
        "completed_at": NOW + timedelta(seconds=2),
    }


def test_valid_evidence_source_is_accepted() -> None:
    source = EvidenceSource.model_validate(source_payload())

    assert source.authoritative is True
    assert source.source_kind is EvidenceSourceKind.RUNBOOK


def test_evidence_source_is_immutable() -> None:
    source = EvidenceSource.model_validate(source_payload())

    with pytest.raises(ValidationError):
        source.owner_id = "different-owner"


def test_valid_active_document_is_accepted() -> None:
    document = EvidenceDocument.model_validate(document_payload())

    assert document.lifecycle_status is EvidenceLifecycleStatus.ACTIVE
    assert document.tombstoned_at is None


def test_valid_tombstoned_document_is_accepted() -> None:
    payload = document_payload()
    payload["lifecycle_status"] = EvidenceLifecycleStatus.TOMBSTONED
    payload["tombstoned_at"] = NOW + timedelta(days=1)

    document = EvidenceDocument.model_validate(payload)

    assert document.lifecycle_status is EvidenceLifecycleStatus.TOMBSTONED


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        (
            "expires_at",
            NOW,
            "expires_at must be later than effective_at",
        ),
        (
            "ingested_at",
            NOW - timedelta(seconds=1),
            "ingested_at cannot precede effective_at",
        ),
        (
            "tombstoned_at",
            NOW + timedelta(minutes=2),
            "an active document cannot have tombstoned_at",
        ),
    ],
)
def test_invalid_document_timeline_is_rejected(
    field: str,
    value: object,
    message: str,
) -> None:
    payload = document_payload()
    payload[field] = value

    with pytest.raises(ValidationError, match=message):
        EvidenceDocument.model_validate(payload)


def test_tombstoned_document_requires_timestamp() -> None:
    payload = document_payload()
    payload["lifecycle_status"] = EvidenceLifecycleStatus.TOMBSTONED
    payload["tombstoned_at"] = None

    with pytest.raises(
        ValidationError,
        match="a tombstoned document requires tombstoned_at",
    ):
        EvidenceDocument.model_validate(payload)


def test_tombstone_cannot_precede_ingestion() -> None:
    payload = document_payload()
    payload["lifecycle_status"] = EvidenceLifecycleStatus.TOMBSTONED
    payload["tombstoned_at"] = NOW

    with pytest.raises(
        ValidationError,
        match="tombstoned_at cannot precede ingested_at",
    ):
        EvidenceDocument.model_validate(payload)


def test_valid_authorized_query_is_accepted() -> None:
    query = RetrievalQuery.model_validate(query_payload())

    assert query.policy_decision_id == "policy-decision-101"
    assert query.max_candidates == 10


def test_expired_query_authority_is_rejected() -> None:
    payload = query_payload()
    payload["authorization_expires_at"] = NOW

    with pytest.raises(
        ValidationError,
        match="authorization_expires_at must be later than requested_at",
    ):
        RetrievalQuery.model_validate(payload)


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (NOW - timedelta(hours=1), None),
        (None, NOW),
        (NOW, NOW),
        (NOW, NOW - timedelta(seconds=1)),
    ],
)
def test_invalid_time_window_is_rejected(
    start: datetime | None,
    end: datetime | None,
) -> None:
    payload = query_payload()
    payload["time_window_start"] = start
    payload["time_window_end"] = end

    with pytest.raises(ValidationError, match=r"time window|time_window_end"):
        RetrievalQuery.model_validate(payload)


def test_valid_candidate_preserves_citation_lineage() -> None:
    candidate = RetrievalCandidate.model_validate(candidate_payload())

    assert candidate.chunk_id == candidate.citation.chunk_id
    assert candidate.source_id == candidate.citation.source_id


def test_candidate_citation_mismatch_is_rejected() -> None:
    payload = candidate_payload()
    citation = citation_payload()
    citation["chunk_id"] = "different-chunk"
    payload["citation"] = citation

    with pytest.raises(
        ValidationError,
        match="candidate identifiers must match citation identifiers",
    ):
        RetrievalCandidate.model_validate(payload)


def test_valid_candidate_result_is_accepted() -> None:
    result = RetrievalResult.model_validate(result_payload())

    assert result.disposition is RetrievalDisposition.CANDIDATES
    assert len(result.candidates) == 1
    assert result.abstention is None


def test_candidate_disposition_requires_candidates() -> None:
    payload = result_payload()
    payload["candidates"] = []

    with pytest.raises(
        ValidationError,
        match="candidate disposition requires at least one candidate",
    ):
        RetrievalResult.model_validate(payload)


def test_candidate_disposition_rejects_abstention() -> None:
    payload = result_payload()
    payload["abstention"] = abstention_payload()

    with pytest.raises(
        ValidationError,
        match="candidate disposition cannot include an abstention",
    ):
        RetrievalResult.model_validate(payload)


def test_valid_abstention_result_is_accepted() -> None:
    payload = result_payload()
    payload["disposition"] = RetrievalDisposition.ABSTENTION
    payload["candidates"] = []
    payload["abstention"] = abstention_payload()

    result = RetrievalResult.model_validate(payload)

    assert result.disposition is RetrievalDisposition.ABSTENTION
    assert result.candidates == ()
    assert result.abstention is not None


def test_abstention_disposition_rejects_candidates() -> None:
    payload = result_payload()
    payload["disposition"] = RetrievalDisposition.ABSTENTION
    payload["abstention"] = abstention_payload()

    with pytest.raises(
        ValidationError,
        match="abstention disposition cannot include candidates",
    ):
        RetrievalResult.model_validate(payload)


def test_abstention_disposition_requires_abstention() -> None:
    payload = result_payload()
    payload["disposition"] = RetrievalDisposition.ABSTENTION
    payload["candidates"] = []
    payload["abstention"] = None

    with pytest.raises(
        ValidationError,
        match="abstention disposition requires an abstention",
    ):
        RetrievalResult.model_validate(payload)


def test_candidate_count_cannot_exceed_query_limit() -> None:
    payload = result_payload()
    query = query_payload()
    query["max_candidates"] = 1
    payload["query"] = query
    payload["candidates"] = [
        candidate_payload(rank=1),
        candidate_payload(rank=2),
    ]

    with pytest.raises(
        ValidationError,
        match="candidate count exceeds query max_candidates",
    ):
        RetrievalResult.model_validate(payload)


@pytest.mark.parametrize(
    "ranks",
    [
        [2],
        [1, 1],
        [1, 3],
    ],
)
def test_candidate_ranks_must_be_contiguous(ranks: list[int]) -> None:
    payload = result_payload()
    payload["candidates"] = [candidate_payload(rank=rank) for rank in ranks]

    with pytest.raises(
        ValidationError,
        match="candidate ranks must be unique, ordered, and contiguous",
    ):
        RetrievalResult.model_validate(payload)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        (
            "request_id",
            "different-request",
            "candidate request_id must match result request_id",
        ),
        (
            "trace_id",
            "different-trace",
            "candidate trace_id must match result trace_id",
        ),
        (
            "policy_decision_id",
            "different-policy",
            "candidate policy decision must match query authority",
        ),
        (
            "source_id",
            "unauthorized-source",
            "candidate source is outside the query allowlist",
        ),
    ],
)
def test_candidate_lineage_or_authority_mismatch_is_rejected(
    field: str,
    value: str,
    message: str,
) -> None:
    payload = result_payload()
    candidate = candidate_payload()
    candidate[field] = value

    if field == "source_id":
        citation = citation_payload()
        citation["source_id"] = value
        candidate["citation"] = citation

    payload["candidates"] = [candidate]

    with pytest.raises(ValidationError, match=message):
        RetrievalResult.model_validate(payload)


def test_result_cannot_complete_before_query() -> None:
    payload = result_payload()
    payload["completed_at"] = NOW - timedelta(seconds=1)

    with pytest.raises(
        ValidationError,
        match="completed_at cannot precede requested_at",
    ):
        RetrievalResult.model_validate(payload)


def test_abstention_lineage_must_match_result() -> None:
    payload = result_payload()
    payload["disposition"] = RetrievalDisposition.ABSTENTION
    payload["candidates"] = []
    abstention = abstention_payload()
    abstention["trace_id"] = "different-trace"
    payload["abstention"] = abstention

    with pytest.raises(
        ValidationError,
        match="abstention trace_id must match result trace_id",
    ):
        RetrievalResult.model_validate(payload)


def test_authorized_sources_cannot_exceed_searched_sources() -> None:
    payload = abstention_payload()
    payload["sources_searched"] = 1
    payload["authorized_source_count"] = 2

    with pytest.raises(
        ValidationError,
        match="authorized_source_count cannot exceed sources_searched",
    ):
        RetrievalAbstention.model_validate(payload)


def test_unknown_retrieval_field_is_rejected() -> None:
    payload = query_payload()
    payload["authorization_override"] = True

    with pytest.raises(ValidationError):
        RetrievalQuery.model_validate(payload)


def test_retrieval_collections_are_immutable() -> None:
    result = RetrievalResult.model_validate(result_payload())

    with pytest.raises(AttributeError):
        result.candidates.append(candidate_payload())  # type: ignore[attr-defined]

    assert len(result.candidates) == 1


def test_citation_is_immutable() -> None:
    citation = Citation.model_validate(citation_payload())

    with pytest.raises(ValidationError):
        citation.locator = "different locator"
