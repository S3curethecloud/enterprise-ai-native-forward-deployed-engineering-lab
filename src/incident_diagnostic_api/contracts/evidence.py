"""CT-04 executable authorized evidence-item contract."""

from typing import Annotated

from pydantic import Field

from incident_diagnostic_api.contracts.authorization import AuthorizationDecision
from incident_diagnostic_api.contracts.common import (
    BoundedText,
    ConfidenceScore,
    ContentHash,
    OpaqueIdentifier,
    ShortText,
    Timestamp,
    VersionedContract,
)
from incident_diagnostic_api.contracts.enums import (
    FreshnessStatus,
    PolicyOperation,
    SensitivityClassification,
    SourceType,
)


class EvidenceItem(VersionedContract):
    """One authorized, traceable unit of retrieved operational evidence."""

    evidence_id: OpaqueIdentifier
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    source_id: OpaqueIdentifier
    source_type: SourceType
    document_id: OpaqueIdentifier
    document_version: OpaqueIdentifier
    passage_id: OpaqueIdentifier
    content: BoundedText
    title: ShortText
    retrieval_score: ConfidenceScore
    authorization_decision_id: OpaqueIdentifier
    freshness_status: FreshnessStatus
    effective_at: Timestamp | None = None
    retrieved_at: Timestamp
    sensitivity_classification: SensitivityClassification
    content_hash: ContentHash

    def is_authorized_by(
        self,
        decision: AuthorizationDecision,
        *,
        at: Annotated[Timestamp, Field()],
    ) -> bool:
        """Verify evidence lineage against an unexpired retrieval decision."""

        if decision.operation is not PolicyOperation.RETRIEVE_RUNBOOK_EVIDENCE:
            return False

        if self.authorization_decision_id != decision.policy_decision_id:
            return False

        if self.request_id != decision.request_id:
            return False

        if self.trace_id != decision.trace_id:
            return False

        return decision.permits_resource(self.source_id, at)
