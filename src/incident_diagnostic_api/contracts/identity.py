"""CT-02 executable trusted identity-context contract."""

from datetime import datetime
from typing import Annotated, Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    ContractModel,
    OpaqueIdentifier,
    ShortText,
    Timestamp,
    VersionedContract,
)
from incident_diagnostic_api.contracts.enums import (
    AssuranceLevel,
    AuthenticationMethod,
)

IdentityClaims = Annotated[
    tuple[OpaqueIdentifier, ...],
    Field(max_length=100),
]


class DelegationContext(ContractModel):
    """Explicit bounded identity-delegation context."""

    delegator_subject_id: OpaqueIdentifier
    delegate_subject_id: OpaqueIdentifier
    reason: ShortText
    expires_at: Timestamp


class IdentityContext(VersionedContract):
    """Verified identity attributes supplied by a trusted adapter."""

    subject_id: OpaqueIdentifier
    tenant_id: OpaqueIdentifier
    authentication_method: AuthenticationMethod
    authentication_time: Timestamp
    session_id: OpaqueIdentifier
    roles: IdentityClaims
    groups: IdentityClaims
    source_entitlements: IdentityClaims
    assurance_level: AssuranceLevel
    expires_at: Timestamp
    issuer: OpaqueIdentifier
    delegation_context: DelegationContext | None = None

    @model_validator(mode="after")
    def validate_identity_timeline(self) -> Self:
        """Reject impossible authentication and delegation timelines."""

        if self.expires_at <= self.authentication_time:
            raise ValueError("identity context must expire after authentication")

        delegation = self.delegation_context
        if delegation is not None:
            if delegation.delegate_subject_id != self.subject_id:
                raise ValueError("delegated subject must match identity subject")
            if delegation.expires_at > self.expires_at:
                raise ValueError("delegation cannot outlive identity context")

        return self

    def is_expired(self, at: datetime) -> bool:
        """Return whether the identity context is expired at an aware time."""

        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("expiration checks require a timezone-aware timestamp")

        return at >= self.expires_at
