"""CT-07 executable lifecycle trace-event contract."""

from typing import Annotated, Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    ContractModel,
    NonNegativeDuration,
    OpaqueIdentifier,
    ReasonCode,
    Timestamp,
    VersionedContract,
)
from incident_diagnostic_api.contracts.enums import (
    ErrorCode,
    LifecycleStage,
    TraceEventName,
    TraceOutcome,
)

ReasonCodes = Annotated[
    tuple[ReasonCode, ...],
    Field(max_length=20),
]

SourceIdentifiers = Annotated[
    tuple[OpaqueIdentifier, ...],
    Field(max_length=50),
]

EXPECTED_EVENT_STAGES: dict[TraceEventName, LifecycleStage] = {
    TraceEventName.REQUEST_RECEIVED: LifecycleStage.ADMISSION,
    TraceEventName.REQUEST_VALIDATED: LifecycleStage.ADMISSION,
    TraceEventName.IDENTITY_VALIDATED: LifecycleStage.IDENTITY,
    TraceEventName.POLICY_EVALUATED: LifecycleStage.POLICY,
    TraceEventName.RETRIEVAL_STARTED: LifecycleStage.RETRIEVAL,
    TraceEventName.RETRIEVAL_COMPLETED: LifecycleStage.RETRIEVAL,
    TraceEventName.EVIDENCE_ASSESSED: LifecycleStage.EVIDENCE_ASSESSMENT,
    TraceEventName.GENERATION_STARTED: LifecycleStage.GENERATION,
    TraceEventName.GENERATION_COMPLETED: LifecycleStage.GENERATION,
    TraceEventName.RESPONSE_VALIDATED: LifecycleStage.RESPONSE_VALIDATION,
    TraceEventName.RESPONSE_RETURNED: LifecycleStage.RESPONSE_DELIVERY,
}


class TraceAttributes(ContractModel):
    """Allowlisted lifecycle metadata; unrestricted payloads are prohibited."""

    tenant_id: OpaqueIdentifier | None = None
    service_id: OpaqueIdentifier | None = None
    evidence_count: Annotated[int, Field(ge=0, le=50)] | None = None
    source_ids: SourceIdentifiers = Field(default_factory=tuple)
    retry_attempt: Annotated[int, Field(ge=0, le=5)] | None = None
    error_code: ErrorCode | None = None
    contract_name: OpaqueIdentifier | None = None
    contract_version_used: OpaqueIdentifier | None = None


class TraceEvent(VersionedContract):
    """One allowlisted event in the diagnostic request lifecycle."""

    event_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    request_id: OpaqueIdentifier
    event_name: TraceEventName
    component: OpaqueIdentifier
    stage: LifecycleStage
    outcome: TraceOutcome
    policy_decision_id: OpaqueIdentifier | None = None
    duration_ms: NonNegativeDuration | None = None
    input_reference: OpaqueIdentifier | None = None
    output_reference: OpaqueIdentifier | None = None
    reason_codes: ReasonCodes
    timestamp: Timestamp
    attributes: TraceAttributes

    @model_validator(mode="after")
    def validate_trace_invariants(self) -> Self:
        """Enforce event-stage and policy-evidence invariants."""

        expected_stage = EXPECTED_EVENT_STAGES.get(self.event_name)
        if expected_stage is not None and self.stage is not expected_stage:
            raise ValueError("trace event does not match its lifecycle stage")

        if self.event_name is TraceEventName.POLICY_EVALUATED and self.policy_decision_id is None:
            raise ValueError("policy evaluation requires a policy decision identifier")

        if (
            self.outcome is TraceOutcome.DENIED
            and self.policy_decision_id is None
            and self.stage is LifecycleStage.POLICY
        ):
            raise ValueError("policy denial requires a policy decision identifier")

        return self
