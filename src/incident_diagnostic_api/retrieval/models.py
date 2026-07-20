"""Immutable contracts for permission-aware retrieval evidence."""

from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    BoundedText,
    ConfidenceScore,
    ContentHash,
    ContractModel,
    OpaqueIdentifier,
    ReasonCode,
    ShortText,
    Timestamp,
    VersionedContract,
)
from incident_diagnostic_api.contracts.enums import (
    FreshnessStatus,
    SensitivityClassification,
)
from incident_diagnostic_api.retrieval.enums import (
    EvidenceLifecycleStatus,
    EvidenceSourceKind,
    RetrievalAbstentionCode,
    RetrievalDisposition,
    RetrievalMethod,
)

Identifiers = Annotated[
    tuple[OpaqueIdentifier, ...],
    Field(min_length=1, max_length=50),
]
ReasonCodes = Annotated[
    tuple[ReasonCode, ...],
    Field(min_length=1, max_length=20),
]
SourceKinds = Annotated[
    tuple[EvidenceSourceKind, ...],
    Field(min_length=1, max_length=5),
]


class EvidenceSource(VersionedContract):
    """Authority-bearing metadata for one bounded evidence source."""

    source_id: OpaqueIdentifier
    source_kind: EvidenceSourceKind
    owner_id: OpaqueIdentifier
    tenant_id: OpaqueIdentifier
    service_ids: Identifiers
    sensitivity: SensitivityClassification
    source_version: OpaqueIdentifier
    freshness_ttl_seconds: Annotated[int, Field(ge=60, le=2_592_000)]
    retention_days: Annotated[int, Field(ge=1, le=3_650)]
    authoritative: Literal[True] = True


class EvidenceDocument(VersionedContract):
    """Versioned evidence document with integrity and lifecycle metadata."""

    document_id: OpaqueIdentifier
    source_id: OpaqueIdentifier
    source_kind: EvidenceSourceKind
    document_version: OpaqueIdentifier
    title: ShortText
    content: BoundedText
    tenant_id: OpaqueIdentifier
    service_ids: Identifiers
    sensitivity: SensitivityClassification
    effective_at: Timestamp
    expires_at: Timestamp | None = None
    content_hash: ContentHash
    ingested_at: Timestamp
    lifecycle_status: EvidenceLifecycleStatus
    tombstoned_at: Timestamp | None = None

    @model_validator(mode="after")
    def validate_document_lifecycle(self) -> Self:
        """Keep temporal and tombstone metadata internally consistent."""

        if self.expires_at is not None and self.expires_at <= self.effective_at:
            raise ValueError("expires_at must be later than effective_at")

        if self.ingested_at < self.effective_at:
            raise ValueError("ingested_at cannot precede effective_at")

        if (
            self.lifecycle_status is EvidenceLifecycleStatus.ACTIVE
            and self.tombstoned_at is not None
        ):
            raise ValueError("an active document cannot have tombstoned_at")

        if (
            self.lifecycle_status is EvidenceLifecycleStatus.TOMBSTONED
            and self.tombstoned_at is None
        ):
            raise ValueError("a tombstoned document requires tombstoned_at")

        if self.tombstoned_at is not None and self.tombstoned_at < self.ingested_at:
            raise ValueError("tombstoned_at cannot precede ingested_at")

        return self


class EvidenceChunk(VersionedContract):
    """Stable, independently citable unit derived from one document version."""

    chunk_id: OpaqueIdentifier
    document_id: OpaqueIdentifier
    document_version: OpaqueIdentifier
    source_id: OpaqueIdentifier
    source_kind: EvidenceSourceKind
    chunk_index: Annotated[int, Field(ge=0, le=100_000)]
    content: BoundedText
    content_hash: ContentHash
    token_estimate: Annotated[int, Field(ge=1, le=8_192)]
    tenant_id: OpaqueIdentifier
    service_ids: Identifiers
    sensitivity: SensitivityClassification
    lifecycle_status: EvidenceLifecycleStatus


class RetrievalQuery(VersionedContract):
    """Authorized, bounded query submitted to a future retrieval boundary."""

    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    subject_id: OpaqueIdentifier
    tenant_id: OpaqueIdentifier
    service_id: OpaqueIdentifier
    query_text: BoundedText
    allowed_source_ids: Identifiers
    allowed_source_kinds: SourceKinds
    time_window_start: Timestamp | None = None
    time_window_end: Timestamp | None = None
    max_candidates: Annotated[int, Field(default=10, ge=1, le=50)]
    minimum_score: ConfidenceScore = 0.0
    policy_decision_id: OpaqueIdentifier
    policy_version: OpaqueIdentifier
    authorization_expires_at: Timestamp
    requested_at: Timestamp

    @model_validator(mode="after")
    def validate_query_authority(self) -> Self:
        """Require live authority and a complete optional time window."""

        if self.authorization_expires_at <= self.requested_at:
            raise ValueError("authorization_expires_at must be later than requested_at")

        has_start = self.time_window_start is not None
        has_end = self.time_window_end is not None

        if has_start != has_end:
            raise ValueError("time window start and end must be supplied together")

        if (
            self.time_window_start is not None
            and self.time_window_end is not None
            and self.time_window_end <= self.time_window_start
        ):
            raise ValueError("time_window_end must be later than time_window_start")

        return self


class Citation(ContractModel):
    """Stable provenance pointer for one retrieved evidence chunk."""

    source_id: OpaqueIdentifier
    document_id: OpaqueIdentifier
    document_version: OpaqueIdentifier
    chunk_id: OpaqueIdentifier
    content_hash: ContentHash
    locator: ShortText
    retrieved_at: Timestamp


class RetrievalCandidate(ContractModel):
    """One authorized candidate with score, rank, and provenance."""

    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    policy_decision_id: OpaqueIdentifier
    source_id: OpaqueIdentifier
    document_id: OpaqueIdentifier
    document_version: OpaqueIdentifier
    chunk_id: OpaqueIdentifier
    method: RetrievalMethod
    score: ConfidenceScore
    rank: Annotated[int, Field(ge=1, le=50)]
    freshness: FreshnessStatus
    citation: Citation

    @model_validator(mode="after")
    def validate_candidate_provenance(self) -> Self:
        """Keep candidate identity aligned with its citation."""

        expected = (
            self.source_id,
            self.document_id,
            self.document_version,
            self.chunk_id,
        )
        cited = (
            self.citation.source_id,
            self.citation.document_id,
            self.citation.document_version,
            self.citation.chunk_id,
        )

        if cited != expected:
            raise ValueError("candidate identifiers must match citation identifiers")

        return self


class RetrievalAbstention(ContractModel):
    """Explicit fail-closed outcome when evidence cannot be returned."""

    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    disposition: Literal[RetrievalDisposition.ABSTENTION] = RetrievalDisposition.ABSTENTION
    code: RetrievalAbstentionCode
    reason_codes: ReasonCodes
    sources_searched: Annotated[int, Field(ge=0, le=50)]
    authorized_source_count: Annotated[int, Field(ge=0, le=50)]
    candidate_count: Annotated[int, Field(ge=0, le=50)]
    safe_message: ShortText
    occurred_at: Timestamp

    @model_validator(mode="after")
    def validate_abstention_counts(self) -> Self:
        """Prevent impossible source and candidate counts."""

        if self.authorized_source_count > self.sources_searched:
            raise ValueError("authorized_source_count cannot exceed sources_searched")

        return self


class RetrievalResult(ContractModel):
    """Mutually exclusive candidate or abstention retrieval outcome."""

    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    query: RetrievalQuery
    disposition: RetrievalDisposition
    candidates: Annotated[
        tuple[RetrievalCandidate, ...],
        Field(max_length=50),
    ] = Field(default_factory=tuple)
    abstention: RetrievalAbstention | None = None
    completed_at: Timestamp

    @model_validator(mode="after")
    def validate_result_shape(self) -> Self:
        """Enforce outcome exclusivity, lineage, and bounded ranking."""

        if self.request_id != self.query.request_id:
            raise ValueError("result request_id must match query request_id")

        if self.trace_id != self.query.trace_id:
            raise ValueError("result trace_id must match query trace_id")

        if self.completed_at < self.query.requested_at:
            raise ValueError("completed_at cannot precede requested_at")

        if self.disposition is RetrievalDisposition.CANDIDATES:
            if not self.candidates:
                raise ValueError("candidate disposition requires at least one candidate")

            if self.abstention is not None:
                raise ValueError("candidate disposition cannot include an abstention")

        if self.disposition is RetrievalDisposition.ABSTENTION:
            if self.candidates:
                raise ValueError("abstention disposition cannot include candidates")

            if self.abstention is None:
                raise ValueError("abstention disposition requires an abstention")

        if len(self.candidates) > self.query.max_candidates:
            raise ValueError("candidate count exceeds query max_candidates")

        expected_ranks = list(range(1, len(self.candidates) + 1))
        actual_ranks = [candidate.rank for candidate in self.candidates]

        if actual_ranks != expected_ranks:
            raise ValueError("candidate ranks must be unique, ordered, and contiguous")

        for candidate in self.candidates:
            if candidate.request_id != self.request_id:
                raise ValueError("candidate request_id must match result request_id")

            if candidate.trace_id != self.trace_id:
                raise ValueError("candidate trace_id must match result trace_id")

            if candidate.policy_decision_id != self.query.policy_decision_id:
                raise ValueError("candidate policy decision must match query authority")

            if candidate.source_id not in self.query.allowed_source_ids:
                raise ValueError("candidate source is outside the query allowlist")

        if self.abstention is not None:
            if self.abstention.request_id != self.request_id:
                raise ValueError("abstention request_id must match result request_id")

            if self.abstention.trace_id != self.trace_id:
                raise ValueError("abstention trace_id must match result trace_id")

        return self
