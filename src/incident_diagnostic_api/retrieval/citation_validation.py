"""Deterministic citation validation and controlled abstention."""

from datetime import timedelta
from enum import StrEnum
from typing import Annotated, Final, Literal, Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    ContractModel,
    OpaqueIdentifier,
    ShortText,
    Timestamp,
)
from incident_diagnostic_api.retrieval.content_controls import (
    CONTENT_CONTROL_VERSION,
    ContentControlDisposition,
    ContentControlResult,
    ContentTrustLabel,
    ControlledContextItem,
)
from incident_diagnostic_api.retrieval.corpus import (
    SyntheticEvidenceCorpus,
    calculate_content_hash,
)
from incident_diagnostic_api.retrieval.enums import EvidenceLifecycleStatus
from incident_diagnostic_api.retrieval.models import (
    Citation,
    EvidenceChunk,
    EvidenceDocument,
    EvidenceSource,
)

CITATION_VALIDATION_VERSION: Final[Literal["citation-validation-v1"]] = "citation-validation-v1"


class CitationValidationDisposition(StrEnum):
    """Possible outcomes after validating controlled evidence citations."""

    VALIDATED = "validated"
    ABSTENTION = "abstention"


class CitationAbstentionCode(StrEnum):
    """Fail-closed reasons why validated evidence cannot be returned."""

    CONTENT_BLOCKED = "CONTENT_BLOCKED"
    NO_RETAINED_EVIDENCE = "NO_RETAINED_EVIDENCE"
    CITATION_MISMATCH = "CITATION_MISMATCH"
    EVIDENCE_STALE = "EVIDENCE_STALE"
    INTEGRITY_FAILURE = "INTEGRITY_FAILURE"


class CitationValidationEvidence(ContractModel):
    """Recorded proof that one citation resolved to current corpus evidence."""

    citation: Citation
    corpus_id: OpaqueIdentifier
    corpus_version: OpaqueIdentifier
    source_version: OpaqueIdentifier
    freshness_deadline: Timestamp
    validated_at: Timestamp

    @model_validator(mode="after")
    def validate_evidence_time(self) -> Self:
        """Require validation before the evidence freshness deadline."""

        if self.validated_at >= self.freshness_deadline:
            raise ValueError("citation validation must precede freshness deadline")

        return self


class ValidatedEvidenceItem(ContractModel):
    """One unchanged retained item with citation-validation evidence."""

    validation_rank: Annotated[int, Field(ge=1, le=50)]
    trust_label: Literal[ContentTrustLabel.UNTRUSTED_EVIDENCE] = (
        ContentTrustLabel.UNTRUSTED_EVIDENCE
    )
    controlled: ControlledContextItem
    evidence: CitationValidationEvidence

    @model_validator(mode="after")
    def validate_item_evidence(self) -> Self:
        """Keep validation rank and citation aligned with the controlled item."""

        if self.validation_rank != self.controlled.safe_rank:
            raise ValueError("validation rank must preserve safe rank")

        if self.evidence.citation != self.controlled.item.citation:
            raise ValueError("validation evidence must match the controlled citation")

        return self


ValidatedItems = Annotated[
    tuple[ValidatedEvidenceItem, ...],
    Field(min_length=1, max_length=50),
]


class ValidatedEvidenceBundle(ContractModel):
    """Ordered all-valid evidence with corpus and policy lineage."""

    validation_version: Literal["citation-validation-v1"] = CITATION_VALIDATION_VERSION
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    policy_decision_id: OpaqueIdentifier
    control_version: Literal["deterministic-content-controls-v1"] = CONTENT_CONTROL_VERSION
    corpus_id: OpaqueIdentifier
    corpus_version: OpaqueIdentifier
    items: ValidatedItems
    validated_at: Timestamp

    @model_validator(mode="after")
    def validate_bundle(self) -> Self:
        """Enforce correlation, ordering, uniqueness, and validation time."""

        expected_ranks = list(range(1, len(self.items) + 1))
        actual_ranks = [item.validation_rank for item in self.items]

        if actual_ranks != expected_ranks:
            raise ValueError("validation ranks must be ordered and contiguous")

        chunk_ids = [item.controlled.item.chunk_id for item in self.items]

        if len(chunk_ids) != len(set(chunk_ids)):
            raise ValueError("validated chunk identifiers must be unique")

        for validated in self.items:
            item = validated.controlled.item
            evidence = validated.evidence

            if item.request_id != self.request_id:
                raise ValueError("validated item request_id must match bundle")

            if item.trace_id != self.trace_id:
                raise ValueError("validated item trace_id must match bundle")

            if item.policy_decision_id != self.policy_decision_id:
                raise ValueError("validated item policy decision must match bundle")

            if evidence.corpus_id != self.corpus_id:
                raise ValueError("validation evidence corpus_id must match bundle")

            if evidence.corpus_version != self.corpus_version:
                raise ValueError("validation evidence corpus version must match bundle")

            if evidence.validated_at != self.validated_at:
                raise ValueError("item validation time must match bundle")

        return self


class CitationAbstention(ContractModel):
    """Explicit safe outcome when controlled evidence cannot be validated."""

    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    policy_decision_id: OpaqueIdentifier
    code: CitationAbstentionCode
    reason_codes: Annotated[
        tuple[CitationAbstentionCode, ...],
        Field(min_length=1, max_length=5),
    ]
    retained_item_count: Annotated[int, Field(ge=0, le=50)]
    quarantined_item_count: Annotated[int, Field(ge=0, le=50)]
    safe_message: ShortText
    occurred_at: Timestamp

    @model_validator(mode="after")
    def validate_reason_codes(self) -> Self:
        """Require the primary abstention code to lead unique reasons."""

        if self.reason_codes[0] is not self.code:
            raise ValueError("primary abstention code must lead reason_codes")

        if len(self.reason_codes) != len(set(self.reason_codes)):
            raise ValueError("abstention reason_codes must be unique")

        return self


class CitationValidationResult(ContractModel):
    """Mutually exclusive validated bundle or controlled abstention."""

    validation_version: Literal["citation-validation-v1"] = CITATION_VALIDATION_VERSION
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    policy_decision_id: OpaqueIdentifier
    disposition: CitationValidationDisposition
    bundle: ValidatedEvidenceBundle | None = None
    abstention: CitationAbstention | None = None
    completed_at: Timestamp

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        """Enforce exclusivity, correlation, and completion timestamps."""

        if self.disposition is CitationValidationDisposition.VALIDATED and (
            self.bundle is None or self.abstention is not None
        ):
            raise ValueError("validated disposition requires only a bundle")

        if self.disposition is CitationValidationDisposition.ABSTENTION and (
            self.abstention is None or self.bundle is not None
        ):
            raise ValueError("abstention disposition requires only an abstention")

        correlated = self.bundle if self.bundle is not None else self.abstention

        if correlated is not None:
            if correlated.request_id != self.request_id:
                raise ValueError("citation outcome request_id must match result")

            if correlated.trace_id != self.trace_id:
                raise ValueError("citation outcome trace_id must match result")

            if correlated.policy_decision_id != self.policy_decision_id:
                raise ValueError("citation outcome policy decision must match result")

        if self.bundle is not None and self.bundle.validated_at != self.completed_at:
            raise ValueError("bundle validation time must match completion time")

        if self.abstention is not None and self.abstention.occurred_at != self.completed_at:
            raise ValueError("abstention time must match completion time")

        return self


def _abstain(
    *,
    controlled: ContentControlResult,
    code: CitationAbstentionCode,
    safe_message: str,
    validated_at: Timestamp,
) -> CitationValidationResult:
    """Return one correlated controlled citation abstention."""

    abstention = CitationAbstention(
        request_id=controlled.request_id,
        trace_id=controlled.trace_id,
        policy_decision_id=controlled.policy_decision_id,
        code=code,
        reason_codes=(code,),
        retained_item_count=len(controlled.items),
        quarantined_item_count=controlled.quarantined_item_count,
        safe_message=safe_message,
        occurred_at=validated_at,
    )

    return CitationValidationResult(
        request_id=controlled.request_id,
        trace_id=controlled.trace_id,
        policy_decision_id=controlled.policy_decision_id,
        disposition=CitationValidationDisposition.ABSTENTION,
        bundle=None,
        abstention=abstention,
        completed_at=validated_at,
    )


def _citation_matches(
    *,
    controlled: ControlledContextItem,
    source: EvidenceSource,
    document: EvidenceDocument,
    chunk: EvidenceChunk,
) -> bool:
    """Return whether one retained item resolves to exact corpus lineage."""

    item = controlled.item
    citation = item.citation

    return (
        citation.source_id == item.source_id == source.source_id == chunk.source_id
        and citation.document_id == item.document_id == document.document_id == chunk.document_id
        and citation.document_version
        == item.document_version
        == document.document_version
        == chunk.document_version
        and citation.chunk_id == item.chunk_id == chunk.chunk_id
        and citation.content_hash == item.content_hash == chunk.content_hash
        and citation.locator == f"chunk:{chunk.chunk_index}"
        and item.content == chunk.content
        and calculate_content_hash(item.content) == item.content_hash
        and source.source_id == document.source_id
        and source.source_kind is document.source_kind is chunk.source_kind
    )


def _freshness_deadline(
    *,
    source: EvidenceSource,
    document: EvidenceDocument,
) -> Timestamp:
    """Return the earliest explicit or TTL-derived freshness deadline."""

    ttl_deadline = document.ingested_at + timedelta(seconds=source.freshness_ttl_seconds)

    if document.expires_at is None:
        return ttl_deadline

    return min(ttl_deadline, document.expires_at)


def validate_citations(
    *,
    corpus: SyntheticEvidenceCorpus,
    controlled: ContentControlResult,
    validated_at: Timestamp,
) -> CitationValidationResult:
    """Validate every retained citation or abstain without partial output."""

    if validated_at < controlled.analyzed_at:
        return _abstain(
            controlled=controlled,
            code=CitationAbstentionCode.INTEGRITY_FAILURE,
            safe_message="Citation validation time precedes content inspection.",
            validated_at=validated_at,
        )

    if controlled.disposition is ContentControlDisposition.BLOCKED:
        return _abstain(
            controlled=controlled,
            code=CitationAbstentionCode.CONTENT_BLOCKED,
            safe_message="Controlled evidence was blocked before citation validation.",
            validated_at=validated_at,
        )

    if not controlled.items:
        return _abstain(
            controlled=controlled,
            code=CitationAbstentionCode.NO_RETAINED_EVIDENCE,
            safe_message="No retained evidence is available for citation validation.",
            validated_at=validated_at,
        )

    assessments = {assessment.chunk_id: assessment for assessment in controlled.assessments}
    sources = {source.source_id: source for source in corpus.sources}
    documents = {document.document_id: document for document in corpus.documents}
    chunks = {chunk.chunk_id: chunk for chunk in corpus.chunks}
    validated_items: list[ValidatedEvidenceItem] = []

    for retained in controlled.items:
        item = retained.item
        assessment = assessments.get(item.chunk_id)

        if (
            assessment is None
            or assessment.quarantined
            or assessment.content_hash != item.content_hash
            or assessment.signals
        ):
            return _abstain(
                controlled=controlled,
                code=CitationAbstentionCode.INTEGRITY_FAILURE,
                safe_message="Controlled evidence assessments are inconsistent.",
                validated_at=validated_at,
            )

        source = sources.get(item.source_id)
        document = documents.get(item.document_id)
        chunk = chunks.get(item.chunk_id)

        if source is None or document is None or chunk is None:
            return _abstain(
                controlled=controlled,
                code=CitationAbstentionCode.CITATION_MISMATCH,
                safe_message="A citation does not resolve to the evidence corpus.",
                validated_at=validated_at,
            )

        if not _citation_matches(
            controlled=retained,
            source=source,
            document=document,
            chunk=chunk,
        ):
            return _abstain(
                controlled=controlled,
                code=CitationAbstentionCode.CITATION_MISMATCH,
                safe_message="Citation lineage does not match the evidence corpus.",
                validated_at=validated_at,
            )

        if (
            document.lifecycle_status is not EvidenceLifecycleStatus.ACTIVE
            or chunk.lifecycle_status is not EvidenceLifecycleStatus.ACTIVE
            or item.citation.retrieved_at < document.effective_at
            or item.citation.retrieved_at > controlled.source_context_constructed_at
        ):
            return _abstain(
                controlled=controlled,
                code=CitationAbstentionCode.EVIDENCE_STALE,
                safe_message="Cited evidence is not current for validation.",
                validated_at=validated_at,
            )

        deadline = _freshness_deadline(source=source, document=document)

        if validated_at >= deadline:
            return _abstain(
                controlled=controlled,
                code=CitationAbstentionCode.EVIDENCE_STALE,
                safe_message="Cited evidence exceeded its freshness boundary.",
                validated_at=validated_at,
            )

        evidence = CitationValidationEvidence(
            citation=item.citation,
            corpus_id=corpus.corpus_id,
            corpus_version=corpus.corpus_version,
            source_version=source.source_version,
            freshness_deadline=deadline,
            validated_at=validated_at,
        )
        validated_items.append(
            ValidatedEvidenceItem(
                validation_rank=retained.safe_rank,
                controlled=retained,
                evidence=evidence,
            )
        )

    bundle = ValidatedEvidenceBundle(
        request_id=controlled.request_id,
        trace_id=controlled.trace_id,
        policy_decision_id=controlled.policy_decision_id,
        control_version=controlled.control_version,
        corpus_id=corpus.corpus_id,
        corpus_version=corpus.corpus_version,
        items=tuple(validated_items),
        validated_at=validated_at,
    )

    return CitationValidationResult(
        request_id=controlled.request_id,
        trace_id=controlled.trace_id,
        policy_decision_id=controlled.policy_decision_id,
        disposition=CitationValidationDisposition.VALIDATED,
        bundle=bundle,
        abstention=None,
        completed_at=validated_at,
    )
