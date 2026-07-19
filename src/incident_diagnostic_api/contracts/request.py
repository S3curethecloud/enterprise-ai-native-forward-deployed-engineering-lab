"""CT-01 executable diagnostic request contract."""

from typing import Annotated

from pydantic import Field

from incident_diagnostic_api.contracts.common import (
    BoundedText,
    OpaqueIdentifier,
    ShortText,
    Timestamp,
    VersionedContract,
)
from incident_diagnostic_api.contracts.enums import Environment, RequestType

ObservedSymptoms = Annotated[
    tuple[ShortText, ...],
    Field(min_length=1, max_length=20),
]

BoundedIdentifiers = Annotated[
    tuple[OpaqueIdentifier, ...],
    Field(max_length=50),
]


class DiagnosticRequest(VersionedContract):
    """Structured recommendation-only incident diagnostic request."""

    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    incident_id: OpaqueIdentifier
    service_id: OpaqueIdentifier
    environment: Environment
    incident_summary: ShortText
    observed_symptoms: ObservedSymptoms
    request_timestamp: Timestamp
    request_type: RequestType
    alert_ids: BoundedIdentifiers = Field(default_factory=tuple)
    deployment_id: OpaqueIdentifier | None = None
    error_codes: BoundedIdentifiers = Field(default_factory=tuple)
    affected_component: OpaqueIdentifier | None = None
    known_start_time: Timestamp | None = None
    existing_ticket_reference: OpaqueIdentifier | None = None
    additional_context: BoundedText | None = None
