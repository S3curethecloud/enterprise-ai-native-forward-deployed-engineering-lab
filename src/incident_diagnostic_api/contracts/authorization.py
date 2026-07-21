"""CT-03 executable deterministic authorization-decision contract."""

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    ContractModel,
    OpaqueIdentifier,
    ReasonCode,
    Timestamp,
    VersionedContract,
)
from incident_diagnostic_api.contracts.enums import (
    PolicyOperation,
    PolicyOutcome,
    SensitivityClassification,
    SourceType,
)

ResourceIdentifiers = Annotated[
    tuple[OpaqueIdentifier, ...],
    Field(min_length=1, max_length=100),
]

AllowedResourceIdentifiers = Annotated[
    tuple[OpaqueIdentifier, ...],
    Field(max_length=100),
]

ReasonCodes = Annotated[
    tuple[ReasonCode, ...],
    Field(min_length=1, max_length=20),
]

AllowedSourceTypes = Annotated[
    tuple[SourceType, ...],
    Field(min_length=1, max_length=2),
]

AllowedTenantIdentifiers = Annotated[
    tuple[OpaqueIdentifier, ...],
    Field(max_length=20),
]

AllowedServiceIdentifiers = Annotated[
    tuple[OpaqueIdentifier, ...],
    Field(max_length=100),
]

AllowedSensitivities = Annotated[
    tuple[SensitivityClassification, ...],
    Field(max_length=4),
]


class PolicyConstraints(ContractModel):
    """Machine-enforceable restrictions applied to an allowed operation."""

    max_evidence_items: Annotated[int, Field(ge=1, le=50)]
    allowed_source_types: AllowedSourceTypes
    allowed_tenant_ids: AllowedTenantIdentifiers = Field(default_factory=tuple)
    allowed_service_ids: AllowedServiceIdentifiers = Field(default_factory=tuple)
    allowed_sensitivities: AllowedSensitivities = Field(default_factory=tuple)
    require_citations: Literal[True] = True
    recommendation_only: Literal[True] = True


class AuthorizationDecision(VersionedContract):
    """Deterministic allow, deny, or constrain decision."""

    policy_decision_id: OpaqueIdentifier
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    subject_id: OpaqueIdentifier
    operation: PolicyOperation
    resource_ids: ResourceIdentifiers
    outcome: PolicyOutcome
    allowed_resource_ids: AllowedResourceIdentifiers
    constraints: PolicyConstraints
    reason_codes: ReasonCodes
    policy_version: OpaqueIdentifier
    decided_at: Timestamp
    expires_at: Timestamp

    @model_validator(mode="after")
    def validate_decision_invariants(self) -> Self:
        """Enforce resource, outcome, and timeline invariants."""

        if self.expires_at <= self.decided_at:
            raise ValueError("authorization decision must expire after decision time")

        requested = set(self.resource_ids)
        allowed = set(self.allowed_resource_ids)

        if not allowed.issubset(requested):
            raise ValueError("allowed resources must be a subset of requested resources")

        if self.outcome is PolicyOutcome.DENY and allowed:
            raise ValueError("denied decisions cannot contain allowed resources")

        if (
            self.operation is PolicyOperation.RETRIEVE_RUNBOOK_EVIDENCE
            and self.outcome in {PolicyOutcome.ALLOW, PolicyOutcome.CONSTRAIN}
            and not allowed
        ):
            raise ValueError("permitted retrieval requires at least one allowed resource")

        permitted_retrieval = (
            self.operation is PolicyOperation.RETRIEVE_RUNBOOK_EVIDENCE
            and self.outcome in {PolicyOutcome.ALLOW, PolicyOutcome.CONSTRAIN}
        )

        if permitted_retrieval and not self.constraints.allowed_tenant_ids:
            raise ValueError("permitted retrieval requires an allowed tenant")

        if permitted_retrieval and not self.constraints.allowed_service_ids:
            raise ValueError("permitted retrieval requires an allowed service")

        if permitted_retrieval and not self.constraints.allowed_sensitivities:
            raise ValueError("permitted retrieval requires allowed sensitivities")

        return self

    def is_expired(self, at: datetime) -> bool:
        """Return whether the decision is expired at an aware time."""

        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("expiration checks require a timezone-aware timestamp")

        return at >= self.expires_at

    def permits_resource(self, resource_id: str, at: datetime) -> bool:
        """Return whether this unexpired decision permits one resource."""

        if self.is_expired(at):
            return False

        if self.outcome is PolicyOutcome.DENY:
            return False

        return resource_id in self.allowed_resource_ids
