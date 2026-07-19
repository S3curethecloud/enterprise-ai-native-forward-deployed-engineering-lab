"""CT-05 executable diagnostic response contract."""

from typing import Annotated, Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    ContractModel,
    OpaqueIdentifier,
    ReasonCode,
    ShortText,
    Timestamp,
    VersionedContract,
)
from incident_diagnostic_api.contracts.enums import (
    ActionClass,
    ConfidenceClassification,
    ExecutionStatus,
    PolicyOutcome,
    ResponseStatus,
    SupportType,
)
from incident_diagnostic_api.contracts.evidence import EvidenceItem

EvidenceIdentifiers = Annotated[
    tuple[OpaqueIdentifier, ...],
    Field(min_length=1, max_length=50),
]

BoundedLimitations = Annotated[
    tuple[ShortText, ...],
    Field(max_length=20),
]


class Observation(ContractModel):
    """One explicitly labeled observed fact."""

    claim_id: OpaqueIdentifier
    text: ShortText


class Inference(ContractModel):
    """One explicitly labeled evidence-derived interpretation."""

    claim_id: OpaqueIdentifier
    text: ShortText


class EvidenceCitation(ContractModel):
    """Mapping from one response claim to retrieved evidence."""

    claim_id: OpaqueIdentifier
    evidence_ids: EvidenceIdentifiers
    support_type: SupportType
    citation_note: ShortText | None = None


class RecommendedNextStep(ContractModel):
    """One recommendation that is structurally non-executing."""

    step_id: OpaqueIdentifier
    description: ShortText
    action_class: ActionClass
    execution_status: ExecutionStatus
    supporting_evidence_ids: EvidenceIdentifiers
    risk_note: ShortText


class AbstentionReason(ContractModel):
    """Controlled reason for returning no diagnosis."""

    reason_code: ReasonCode
    safe_message: ShortText


class PolicyOutcomeReference(ContractModel):
    """Reference to the deterministic policy decision used."""

    policy_decision_id: OpaqueIdentifier
    outcome: PolicyOutcome


class DiagnosticResponse(VersionedContract):
    """Citation-backed recommendation, abstention, or bounded error result."""

    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    incident_id: OpaqueIdentifier
    service_id: OpaqueIdentifier
    response_status: ResponseStatus
    diagnostic_summary: ShortText | None = None
    observations: tuple[Observation, ...] = Field(default_factory=tuple, max_length=50)
    inferences: tuple[Inference, ...] = Field(default_factory=tuple, max_length=50)
    evidence_citations: tuple[EvidenceCitation, ...] = Field(
        default_factory=tuple,
        max_length=100,
    )
    recommended_next_steps: tuple[RecommendedNextStep, ...] = Field(
        default_factory=tuple,
        max_length=20,
    )
    confidence_classification: ConfidenceClassification | None = None
    limitations: BoundedLimitations = Field(default_factory=tuple)
    abstention_reason: AbstentionReason | None = None
    policy_outcome: PolicyOutcomeReference
    generated_at: Timestamp

    @model_validator(mode="after")
    def validate_response_invariants(self) -> Self:
        """Enforce status, citation, and recommendation invariants."""

        if self.response_status is ResponseStatus.RECOMMENDATION:
            if self.diagnostic_summary is None:
                raise ValueError("recommendation requires a diagnostic summary")
            if self.confidence_classification is None:
                raise ValueError("recommendation requires a confidence classification")
            if self.abstention_reason is not None:
                raise ValueError("recommendation cannot contain an abstention reason")

        if self.response_status is ResponseStatus.ABSTENTION:
            if self.abstention_reason is None:
                raise ValueError("abstention requires an abstention reason")
            if self.confidence_classification is not None:
                raise ValueError("abstention cannot contain a confidence classification")
            if self.recommended_next_steps:
                raise ValueError("abstention cannot contain recommended next steps")

        if self.response_status is ResponseStatus.ERROR:
            if self.confidence_classification is not None:
                raise ValueError("error cannot contain a confidence classification")
            if self.recommended_next_steps:
                raise ValueError("error cannot contain recommended next steps")

        observation_claim_ids = [observation.claim_id for observation in self.observations]
        inference_claim_id_list = [inference.claim_id for inference in self.inferences]
        claim_ids = observation_claim_ids + inference_claim_id_list

        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("response claim identifiers must be unique")

        citation_claim_ids = {citation.claim_id for citation in self.evidence_citations}
        known_claim_ids = set(claim_ids)

        if not citation_claim_ids.issubset(known_claim_ids):
            raise ValueError("citations must reference known response claims")

        inference_claim_ids = set(inference_claim_id_list)

        if not inference_claim_ids.issubset(citation_claim_ids):
            raise ValueError("every inference must contain an evidence citation")

        step_ids = [step.step_id for step in self.recommended_next_steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("recommended step identifiers must be unique")

        return self

    def has_valid_evidence_lineage(
        self,
        evidence_items: tuple[EvidenceItem, ...],
    ) -> bool:
        """Verify every cited and recommended evidence identifier."""

        evidence_by_id = {
            evidence.evidence_id: evidence
            for evidence in evidence_items
            if evidence.request_id == self.request_id and evidence.trace_id == self.trace_id
        }

        cited_ids = {
            evidence_id
            for citation in self.evidence_citations
            for evidence_id in citation.evidence_ids
        }

        recommended_ids = {
            evidence_id
            for step in self.recommended_next_steps
            for evidence_id in step.supporting_evidence_ids
        }

        required_ids = cited_ids | recommended_ids

        return bool(required_ids) and required_ids.issubset(evidence_by_id)
