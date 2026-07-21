"""Deterministic controls for untrusted retrieved context content."""

import re
from enum import StrEnum
from typing import Annotated, Final, Literal, Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    ContentHash,
    ContractModel,
    OpaqueIdentifier,
    Timestamp,
)
from incident_diagnostic_api.retrieval.context import ContextBundle, ContextItem

CONTENT_CONTROL_VERSION: Final[Literal["deterministic-content-controls-v1"]] = (
    "deterministic-content-controls-v1"
)


class ContentTrustLabel(StrEnum):
    """Trust classification applied to all retrieved evidence content."""

    UNTRUSTED_EVIDENCE = "untrusted_evidence"


class ContentRiskCategory(StrEnum):
    """Bounded instruction-like risk categories detected locally."""

    AUTHORITY_OVERRIDE = "authority_override"
    POLICY_MANIPULATION = "policy_manipulation"
    TENANT_SCOPE_CHANGE = "tenant_scope_change"
    TOOL_REQUEST = "tool_request"
    SECRET_REQUEST = "secret_request"
    EVALUATION_EVASION = "evaluation_evasion"
    CITATION_SUPPRESSION = "citation_suppression"
    BUDGET_MANIPULATION = "budget_manipulation"


class ContentControlDisposition(StrEnum):
    """Possible outcomes after inspecting a context bundle."""

    CLEAN = "clean"
    FILTERED = "filtered"
    BLOCKED = "blocked"


class ContentSignal(ContractModel):
    """One deterministic signal without echoing suspicious content."""

    pattern_id: OpaqueIdentifier
    category: ContentRiskCategory
    content_hash: ContentHash
    start_offset: Annotated[int, Field(ge=0, le=4_000)]
    end_offset: Annotated[int, Field(ge=1, le=4_000)]

    @model_validator(mode="after")
    def validate_offsets(self) -> Self:
        """Require a nonempty bounded match range."""

        if self.end_offset <= self.start_offset:
            raise ValueError("signal end_offset must follow start_offset")

        return self


Signals = Annotated[
    tuple[ContentSignal, ...],
    Field(max_length=20),
]


class ContextItemAssessment(ContractModel):
    """Deterministic control decision for one context item."""

    chunk_id: OpaqueIdentifier
    content_hash: ContentHash
    trust_label: Literal[ContentTrustLabel.UNTRUSTED_EVIDENCE] = (
        ContentTrustLabel.UNTRUSTED_EVIDENCE
    )
    signals: Signals = ()
    quarantined: bool

    @model_validator(mode="after")
    def validate_quarantine_decision(self) -> Self:
        """Quarantine exactly those items carrying one or more signals."""

        if self.quarantined is not bool(self.signals):
            raise ValueError("quarantined must reflect detected signals")

        for signal in self.signals:
            if signal.content_hash != self.content_hash:
                raise ValueError("signal content hash must match assessment")

        return self


class ControlledContextItem(ContractModel):
    """One non-quarantined context item with a contiguous safe rank."""

    safe_rank: Annotated[int, Field(ge=1, le=50)]
    trust_label: Literal[ContentTrustLabel.UNTRUSTED_EVIDENCE] = (
        ContentTrustLabel.UNTRUSTED_EVIDENCE
    )
    item: ContextItem


ControlledItems = Annotated[
    tuple[ControlledContextItem, ...],
    Field(max_length=50),
]
Assessments = Annotated[
    tuple[ContextItemAssessment, ...],
    Field(min_length=1, max_length=50),
]


class ContentControlResult(ContractModel):
    """Immutable context-control result with quarantine evidence."""

    control_version: Literal["deterministic-content-controls-v1"] = CONTENT_CONTROL_VERSION
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    policy_decision_id: OpaqueIdentifier
    source_context_constructed_at: Timestamp
    disposition: ContentControlDisposition
    items: ControlledItems = ()
    assessments: Assessments
    quarantined_item_count: Annotated[int, Field(ge=0, le=50)]
    analyzed_at: Timestamp

    @model_validator(mode="after")
    def validate_control_result(self) -> Self:
        """Enforce correlation, counts, ranks, and outcome semantics."""

        if self.analyzed_at < self.source_context_constructed_at:
            raise ValueError("analyzed_at cannot precede context construction")

        chunk_ids = [assessment.chunk_id for assessment in self.assessments]

        if len(chunk_ids) != len(set(chunk_ids)):
            raise ValueError("assessment chunk identifiers must be unique")

        calculated_quarantined = sum(assessment.quarantined for assessment in self.assessments)

        if self.quarantined_item_count != calculated_quarantined:
            raise ValueError("quarantined_item_count must match assessments")

        expected_safe_ranks = list(range(1, len(self.items) + 1))
        actual_safe_ranks = [item.safe_rank for item in self.items]

        if actual_safe_ranks != expected_safe_ranks:
            raise ValueError("safe ranks must be ordered and contiguous")

        safe_chunk_ids = [controlled.item.chunk_id for controlled in self.items]
        quarantined_ids = {
            assessment.chunk_id for assessment in self.assessments if assessment.quarantined
        }

        if quarantined_ids & set(safe_chunk_ids):
            raise ValueError("quarantined items cannot enter controlled context")

        expected_disposition = (
            ContentControlDisposition.CLEAN
            if self.quarantined_item_count == 0
            else (
                ContentControlDisposition.BLOCKED
                if not self.items
                else ContentControlDisposition.FILTERED
            )
        )

        if self.disposition is not expected_disposition:
            raise ValueError("content-control disposition is inconsistent")

        for controlled in self.items:
            item = controlled.item

            if item.request_id != self.request_id:
                raise ValueError("controlled item request_id must match result")

            if item.trace_id != self.trace_id:
                raise ValueError("controlled item trace_id must match result")

            if item.policy_decision_id != self.policy_decision_id:
                raise ValueError("controlled item policy decision must match result")

        return self


_PatternSpec = tuple[str, ContentRiskCategory, re.Pattern[str]]


def _compile(pattern: str) -> re.Pattern[str]:
    """Compile one bounded case-insensitive content-control expression."""

    return re.compile(pattern, re.IGNORECASE | re.DOTALL)


_PATTERNS: Final[tuple[_PatternSpec, ...]] = (
    (
        "authority.ignore-prior-instructions",
        ContentRiskCategory.AUTHORITY_OVERRIDE,
        _compile(
            r"\b(?:ignore|disregard|override)\b.{0,40}"
            r"\b(?:previous|prior|system|developer)\b.{0,24}"
            r"\b(?:instruction|message|prompt)s?\b"
        ),
    ),
    (
        "policy.bypass-controls",
        ContentRiskCategory.POLICY_MANIPULATION,
        _compile(
            r"\b(?:bypass|disable|ignore|override)\b.{0,40}"
            r"\b(?:policy|guardrail|safety|authorization)\b"
        ),
    ),
    (
        "tenant.change-scope",
        ContentRiskCategory.TENANT_SCOPE_CHANGE,
        _compile(r"\b(?:change|switch|override)\b.{0,30}\btenant\b"),
    ),
    (
        "tool.request-execution",
        ContentRiskCategory.TOOL_REQUEST,
        _compile(
            r"\b(?:call|invoke|execute|run|use)\b.{0,30}"
            r"\b(?:tool|shell|command|terminal)\b"
        ),
    ),
    (
        "secret.request-disclosure",
        ContentRiskCategory.SECRET_REQUEST,
        _compile(
            r"\b(?:reveal|print|show|return|expose)\b.{0,30}"
            r"\b(?:secret|password|credential|api[ -]?key|access token)\b"
        ),
    ),
    (
        "evaluation.disable-checks",
        ContentRiskCategory.EVALUATION_EVASION,
        _compile(
            r"\b(?:disable|skip|evade|ignore)\b.{0,30}"
            r"\b(?:evaluation|validation|check|test)s?\b"
        ),
    ),
    (
        "citation.suppress-evidence",
        ContentRiskCategory.CITATION_SUPPRESSION,
        _compile(
            r"\b(?:suppress|omit|remove|disable|do not include)\b.{0,30}"
            r"\bcitations?\b"
        ),
    ),
    (
        "budget.override-limits",
        ContentRiskCategory.BUDGET_MANIPULATION,
        _compile(
            r"\b(?:change|increase|remove|ignore|override)\b.{0,30}"
            r"\b(?:budget|limit)s?\b"
        ),
    ),
)


def detect_content_signals(item: ContextItem) -> tuple[ContentSignal, ...]:
    """Return bounded deterministic signals for one untrusted item."""

    signals: list[ContentSignal] = []

    for pattern_id, category, pattern in _PATTERNS:
        match = pattern.search(item.content)

        if match is None:
            continue

        signals.append(
            ContentSignal(
                pattern_id=pattern_id,
                category=category,
                content_hash=item.content_hash,
                start_offset=match.start(),
                end_offset=match.end(),
            )
        )

    return tuple(signals)


def inspect_context(
    *,
    bundle: ContextBundle,
    analyzed_at: Timestamp,
) -> ContentControlResult:
    """Quarantine signaled whole items without rewriting evidence content."""

    assessments: list[ContextItemAssessment] = []
    safe_items: list[ContextItem] = []

    for item in bundle.items:
        signals = detect_content_signals(item)
        quarantined = bool(signals)
        assessments.append(
            ContextItemAssessment(
                chunk_id=item.chunk_id,
                content_hash=item.content_hash,
                signals=signals,
                quarantined=quarantined,
            )
        )

        if not quarantined:
            safe_items.append(item)

    controlled_items = tuple(
        ControlledContextItem(
            safe_rank=safe_rank,
            item=item,
        )
        for safe_rank, item in enumerate(safe_items, start=1)
    )
    quarantined_count = len(bundle.items) - len(safe_items)
    disposition = (
        ContentControlDisposition.CLEAN
        if quarantined_count == 0
        else (
            ContentControlDisposition.BLOCKED
            if not safe_items
            else ContentControlDisposition.FILTERED
        )
    )

    return ContentControlResult(
        request_id=bundle.request_id,
        trace_id=bundle.trace_id,
        policy_decision_id=bundle.policy_decision_id,
        source_context_constructed_at=bundle.constructed_at,
        disposition=disposition,
        items=controlled_items,
        assessments=tuple(assessments),
        quarantined_item_count=quarantined_count,
        analyzed_at=analyzed_at,
    )
