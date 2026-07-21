"""Deterministic context construction over authorized retrieval results."""

from collections import Counter
from enum import StrEnum
from typing import Annotated, Final, Literal, Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    BoundedText,
    ConfidenceScore,
    ContentHash,
    ContractModel,
    OpaqueIdentifier,
    ShortText,
    Timestamp,
)
from incident_diagnostic_api.contracts.enums import FreshnessStatus
from incident_diagnostic_api.retrieval.corpus import SyntheticEvidenceCorpus
from incident_diagnostic_api.retrieval.enums import (
    EvidenceLifecycleStatus,
    EvidenceSourceKind,
    RetrievalDisposition,
    RetrievalMethod,
)
from incident_diagnostic_api.retrieval.models import (
    Citation,
    EvidenceChunk,
    RetrievalCandidate,
    RetrievalResult,
)

CONTEXT_BUDGET_VERSION: Final[Literal["context-budget-v1"]] = "context-budget-v1"


class ContextDisposition(StrEnum):
    """Mutually exclusive context-construction outcomes."""

    BUNDLE = "bundle"
    INSUFFICIENCY = "insufficiency"


class ContextInsufficiencyCode(StrEnum):
    """Controlled reasons why no context bundle was constructed."""

    RETRIEVAL_ABSTAINED = "RETRIEVAL_ABSTAINED"
    INTEGRITY_FAILURE = "INTEGRITY_FAILURE"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    REQUIRED_SOURCE_DIVERSITY = "REQUIRED_SOURCE_DIVERSITY"


class ContextBudget(ContractModel):
    """Versioned whole-item limits for deterministic context construction."""

    budget_version: Literal["context-budget-v1"] = CONTEXT_BUDGET_VERSION
    max_items: Annotated[int, Field(ge=1, le=50)] = 10
    max_items_per_source: Annotated[int, Field(ge=1, le=50)] = 3
    max_token_estimate: Annotated[int, Field(ge=1, le=32_768)] = 4096
    minimum_source_count: Annotated[int, Field(ge=1, le=20)] = 1

    @model_validator(mode="after")
    def validate_budget_relationships(self) -> Self:
        """Reject internally inconsistent count and diversity limits."""

        if self.max_items_per_source > self.max_items:
            raise ValueError("max_items_per_source cannot exceed max_items")

        if self.minimum_source_count > self.max_items:
            raise ValueError("minimum_source_count cannot exceed max_items")

        return self


class ContextItem(ContractModel):
    """One complete, content-addressed evidence chunk in model context."""

    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    policy_decision_id: OpaqueIdentifier
    context_rank: Annotated[int, Field(ge=1, le=50)]
    retrieval_rank: Annotated[int, Field(ge=1, le=50)]
    source_id: OpaqueIdentifier
    source_kind: EvidenceSourceKind
    document_id: OpaqueIdentifier
    document_version: OpaqueIdentifier
    chunk_id: OpaqueIdentifier
    content: BoundedText
    content_hash: ContentHash
    token_estimate: Annotated[int, Field(ge=1, le=8_192)]
    retrieval_method: RetrievalMethod
    retrieval_score: ConfidenceScore
    citation: Citation

    @model_validator(mode="after")
    def validate_item_provenance(self) -> Self:
        """Keep context identity and content hash aligned with its citation."""

        item_identity = (
            self.source_id,
            self.document_id,
            self.document_version,
            self.chunk_id,
            self.content_hash,
        )
        citation_identity = (
            self.citation.source_id,
            self.citation.document_id,
            self.citation.document_version,
            self.citation.chunk_id,
            self.citation.content_hash,
        )

        if item_identity != citation_identity:
            raise ValueError("context item must match citation provenance")

        return self


ContextItems = Annotated[
    tuple[ContextItem, ...],
    Field(min_length=1, max_length=50),
]


class ContextBundle(ContractModel):
    """Ordered, budgeted context with authority and evidence lineage."""

    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    subject_id: OpaqueIdentifier
    tenant_id: OpaqueIdentifier
    service_id: OpaqueIdentifier
    policy_decision_id: OpaqueIdentifier
    policy_version: OpaqueIdentifier
    request_summary: BoundedText
    budget: ContextBudget
    items: ContextItems
    total_token_estimate: Annotated[int, Field(ge=1, le=32_768)]
    omitted_candidate_count: Annotated[int, Field(ge=0, le=50)]
    truncated: bool
    constructed_at: Timestamp

    @model_validator(mode="after")
    def validate_bundle_invariants(self) -> Self:
        """Enforce lineage, ordering, uniqueness, diversity, and budgets."""

        if len(self.items) > self.budget.max_items:
            raise ValueError("context item count exceeds max_items")

        expected_context_ranks = list(range(1, len(self.items) + 1))
        actual_context_ranks = [item.context_rank for item in self.items]

        if actual_context_ranks != expected_context_ranks:
            raise ValueError("context ranks must be ordered and contiguous")

        retrieval_ranks = [item.retrieval_rank for item in self.items]

        if retrieval_ranks != sorted(retrieval_ranks):
            raise ValueError("context items must preserve retrieval order")

        chunk_ids = [item.chunk_id for item in self.items]

        if len(chunk_ids) != len(set(chunk_ids)):
            raise ValueError("context chunk identifiers must be unique")

        source_counts = Counter(item.source_id for item in self.items)

        if any(count > self.budget.max_items_per_source for count in source_counts.values()):
            raise ValueError("context exceeds max_items_per_source")

        if len(source_counts) < self.budget.minimum_source_count:
            raise ValueError("context does not meet minimum_source_count")

        calculated_total = sum(item.token_estimate for item in self.items)

        if self.total_token_estimate != calculated_total:
            raise ValueError("total_token_estimate must equal the item sum")

        if self.total_token_estimate > self.budget.max_token_estimate:
            raise ValueError("context exceeds max_token_estimate")

        if self.truncated is not (self.omitted_candidate_count > 0):
            raise ValueError("truncated must reflect omitted candidates")

        for item in self.items:
            if item.request_id != self.request_id:
                raise ValueError("context item request_id must match bundle")

            if item.trace_id != self.trace_id:
                raise ValueError("context item trace_id must match bundle")

            if item.policy_decision_id != self.policy_decision_id:
                raise ValueError("context item policy decision must match bundle")

        return self


class ContextInsufficiency(ContractModel):
    """Explicit fail-closed outcome when context cannot be constructed."""

    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    code: ContextInsufficiencyCode
    safe_message: ShortText
    candidate_count: Annotated[int, Field(ge=0, le=50)]
    occurred_at: Timestamp


class ContextConstructionResult(ContractModel):
    """Mutually exclusive context bundle or controlled insufficiency."""

    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    disposition: ContextDisposition
    bundle: ContextBundle | None = None
    insufficiency: ContextInsufficiency | None = None
    constructed_at: Timestamp

    @model_validator(mode="after")
    def validate_result_shape(self) -> Self:
        """Enforce outcome exclusivity and correlation identifiers."""

        if self.disposition is ContextDisposition.BUNDLE:
            if self.bundle is None:
                raise ValueError("bundle disposition requires a bundle")

            if self.insufficiency is not None:
                raise ValueError("bundle disposition cannot include insufficiency")

        if self.disposition is ContextDisposition.INSUFFICIENCY:
            if self.bundle is not None:
                raise ValueError("insufficiency disposition cannot include a bundle")

            if self.insufficiency is None:
                raise ValueError("insufficiency disposition requires insufficiency")

        correlated = self.bundle if self.bundle is not None else self.insufficiency

        if correlated is not None:
            if correlated.request_id != self.request_id:
                raise ValueError("context outcome request_id must match result")

            if correlated.trace_id != self.trace_id:
                raise ValueError("context outcome trace_id must match result")

        return self


def _insufficient(
    *,
    retrieval: RetrievalResult,
    code: ContextInsufficiencyCode,
    safe_message: str,
    constructed_at: Timestamp,
) -> ContextConstructionResult:
    """Return one correlated controlled context insufficiency."""

    insufficiency = ContextInsufficiency(
        request_id=retrieval.request_id,
        trace_id=retrieval.trace_id,
        code=code,
        safe_message=safe_message,
        candidate_count=len(retrieval.candidates),
        occurred_at=constructed_at,
    )

    return ContextConstructionResult(
        request_id=retrieval.request_id,
        trace_id=retrieval.trace_id,
        disposition=ContextDisposition.INSUFFICIENCY,
        bundle=None,
        insufficiency=insufficiency,
        constructed_at=constructed_at,
    )


def _candidate_matches_chunk(
    candidate: RetrievalCandidate,
    chunk: EvidenceChunk,
    retrieval: RetrievalResult,
) -> bool:
    """Return whether one candidate resolves to the exact active chunk."""

    candidate_lineage = (
        candidate.source_id,
        candidate.document_id,
        candidate.document_version,
        candidate.chunk_id,
        candidate.citation.content_hash,
        candidate.citation.locator,
    )
    chunk_lineage = (
        chunk.source_id,
        chunk.document_id,
        chunk.document_version,
        chunk.chunk_id,
        chunk.content_hash,
        f"chunk:{chunk.chunk_index}",
    )

    return (
        candidate_lineage == chunk_lineage
        and chunk.lifecycle_status is EvidenceLifecycleStatus.ACTIVE
        and candidate.freshness is FreshnessStatus.CURRENT
        and candidate.citation.retrieved_at == retrieval.completed_at
    )


def _resolve_candidates(
    *,
    corpus: SyntheticEvidenceCorpus,
    retrieval: RetrievalResult,
) -> tuple[tuple[RetrievalCandidate, EvidenceChunk], ...] | None:
    """Resolve all candidates to exact corpus chunks or fail closed."""

    chunks_by_id = {chunk.chunk_id: chunk for chunk in corpus.chunks}
    resolved: list[tuple[RetrievalCandidate, EvidenceChunk]] = []
    seen_chunk_ids: set[str] = set()

    for candidate in retrieval.candidates:
        if candidate.chunk_id in seen_chunk_ids:
            return None

        seen_chunk_ids.add(candidate.chunk_id)
        chunk = chunks_by_id.get(candidate.chunk_id)

        if chunk is None or not _candidate_matches_chunk(
            candidate,
            chunk,
            retrieval,
        ):
            return None

        resolved.append((candidate, chunk))

    return tuple(resolved)


def _select_required_sources(
    resolved: tuple[tuple[RetrievalCandidate, EvidenceChunk], ...],
    budget: ContextBudget,
) -> tuple[tuple[RetrievalCandidate, EvidenceChunk], ...] | None:
    """Select the highest-ranked whole chunk from required distinct sources."""

    required: list[tuple[RetrievalCandidate, EvidenceChunk]] = []
    seen_sources: set[str] = set()
    token_total = 0

    for pair in resolved:
        candidate, chunk = pair

        if candidate.source_id in seen_sources:
            continue

        if token_total + chunk.token_estimate > budget.max_token_estimate:
            continue

        required.append(pair)
        seen_sources.add(candidate.source_id)
        token_total += chunk.token_estimate

        if len(required) == budget.minimum_source_count:
            return tuple(required)

    return None


def _select_items(
    resolved: tuple[tuple[RetrievalCandidate, EvidenceChunk], ...],
    required: tuple[tuple[RetrievalCandidate, EvidenceChunk], ...],
    budget: ContextBudget,
) -> tuple[tuple[RetrievalCandidate, EvidenceChunk], ...]:
    """Select whole chunks deterministically within all configured budgets."""

    selected = list(required)
    selected_ids = {candidate.chunk_id for candidate, _ in selected}
    source_counts = Counter(candidate.source_id for candidate, _ in selected)
    token_total = sum(chunk.token_estimate for _, chunk in selected)

    for candidate, chunk in resolved:
        if candidate.chunk_id in selected_ids:
            continue

        if len(selected) >= budget.max_items:
            break

        if source_counts[candidate.source_id] >= budget.max_items_per_source:
            continue

        if token_total + chunk.token_estimate > budget.max_token_estimate:
            continue

        selected.append((candidate, chunk))
        selected_ids.add(candidate.chunk_id)
        source_counts[candidate.source_id] += 1
        token_total += chunk.token_estimate

    selected.sort(key=lambda pair: pair[0].rank)
    return tuple(selected)


def build_context(
    *,
    corpus: SyntheticEvidenceCorpus,
    retrieval: RetrievalResult,
    budget: ContextBudget,
    constructed_at: Timestamp,
) -> ContextConstructionResult:
    """Build deterministic whole-chunk context from authorized retrieval."""

    if constructed_at < retrieval.completed_at:
        raise ValueError("constructed_at cannot precede retrieval completion")

    if retrieval.disposition is RetrievalDisposition.ABSTENTION:
        return _insufficient(
            retrieval=retrieval,
            code=ContextInsufficiencyCode.RETRIEVAL_ABSTAINED,
            safe_message="Retrieval did not return evidence for context.",
            constructed_at=constructed_at,
        )

    resolved = _resolve_candidates(
        corpus=corpus,
        retrieval=retrieval,
    )

    if resolved is None:
        return _insufficient(
            retrieval=retrieval,
            code=ContextInsufficiencyCode.INTEGRITY_FAILURE,
            safe_message="Retrieved evidence could not be verified.",
            constructed_at=constructed_at,
        )

    required = _select_required_sources(resolved, budget)

    if required is None:
        available_sources = {candidate.source_id for candidate, _ in resolved}
        code = (
            ContextInsufficiencyCode.REQUIRED_SOURCE_DIVERSITY
            if len(available_sources) < budget.minimum_source_count
            else ContextInsufficiencyCode.BUDGET_EXHAUSTED
        )
        message = (
            "Retrieved evidence does not meet required source diversity."
            if code is ContextInsufficiencyCode.REQUIRED_SOURCE_DIVERSITY
            else "No required source set fits the context token budget."
        )
        return _insufficient(
            retrieval=retrieval,
            code=code,
            safe_message=message,
            constructed_at=constructed_at,
        )

    selected = _select_items(resolved, required, budget)

    if not selected:
        return _insufficient(
            retrieval=retrieval,
            code=ContextInsufficiencyCode.BUDGET_EXHAUSTED,
            safe_message="No complete evidence item fits the context budget.",
            constructed_at=constructed_at,
        )

    items = tuple(
        ContextItem(
            request_id=retrieval.request_id,
            trace_id=retrieval.trace_id,
            policy_decision_id=retrieval.query.policy_decision_id,
            context_rank=context_rank,
            retrieval_rank=candidate.rank,
            source_id=chunk.source_id,
            source_kind=chunk.source_kind,
            document_id=chunk.document_id,
            document_version=chunk.document_version,
            chunk_id=chunk.chunk_id,
            content=chunk.content,
            content_hash=chunk.content_hash,
            token_estimate=chunk.token_estimate,
            retrieval_method=candidate.method,
            retrieval_score=candidate.score,
            citation=candidate.citation,
        )
        for context_rank, (candidate, chunk) in enumerate(selected, start=1)
    )
    omitted_candidate_count = len(resolved) - len(selected)
    query = retrieval.query
    bundle = ContextBundle(
        request_id=retrieval.request_id,
        trace_id=retrieval.trace_id,
        subject_id=query.subject_id,
        tenant_id=query.tenant_id,
        service_id=query.service_id,
        policy_decision_id=query.policy_decision_id,
        policy_version=query.policy_version,
        request_summary=query.query_text,
        budget=budget,
        items=items,
        total_token_estimate=sum(item.token_estimate for item in items),
        omitted_candidate_count=omitted_candidate_count,
        truncated=omitted_candidate_count > 0,
        constructed_at=constructed_at,
    )

    return ContextConstructionResult(
        request_id=retrieval.request_id,
        trace_id=retrieval.trace_id,
        disposition=ContextDisposition.BUNDLE,
        bundle=bundle,
        insufficiency=None,
        constructed_at=constructed_at,
    )
