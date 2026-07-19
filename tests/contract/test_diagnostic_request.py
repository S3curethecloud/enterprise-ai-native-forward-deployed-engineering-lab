"""Positive and negative contract tests for CT-01."""

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.contracts import DiagnosticRequest


def valid_request_payload() -> dict[str, Any]:
    """Return an isolated valid CT-01 payload."""

    return {
        "contract_version": "1.0",
        "request_id": "req-7f31",
        "trace_id": "trace-a812",
        "incident_id": "INC-10427",
        "service_id": "payments-api",
        "environment": "production",
        "incident_summary": "Elevated payment authorization failures",
        "observed_symptoms": [
            "HTTP 503 rate increased",
            "Dependency timeout alerts firing",
        ],
        "request_timestamp": datetime(2026, 7, 19, 18, 30, tzinfo=UTC),
        "request_type": "diagnostic_recommendation",
        "alert_ids": ["ALT-8801"],
        "affected_component": "authorization-adapter",
    }


def test_valid_request_is_accepted() -> None:
    request = DiagnosticRequest.model_validate(valid_request_payload())

    assert request.request_id == "req-7f31"
    assert request.environment.value == "production"
    assert request.request_type.value == "diagnostic_recommendation"
    assert request.observed_symptoms == (
        "HTTP 503 rate increased",
        "Dependency timeout alerts firing",
    )
    assert request.alert_ids == ("ALT-8801",)


@pytest.mark.parametrize(
    "required_field",
    [
        "request_id",
        "trace_id",
        "incident_id",
        "service_id",
        "environment",
        "incident_summary",
        "observed_symptoms",
        "request_timestamp",
        "request_type",
    ],
)
def test_missing_required_field_is_rejected(required_field: str) -> None:
    payload = valid_request_payload()
    payload.pop(required_field)

    with pytest.raises(ValidationError):
        DiagnosticRequest.model_validate(payload)


def test_unknown_field_is_rejected() -> None:
    payload = valid_request_payload()
    payload["unexpected"] = "not permitted"

    with pytest.raises(ValidationError):
        DiagnosticRequest.model_validate(payload)


def test_self_asserted_identity_field_is_rejected() -> None:
    payload = valid_request_payload()
    payload["subject_id"] = "self-asserted-user"

    with pytest.raises(ValidationError):
        DiagnosticRequest.model_validate(payload)


def test_execution_request_type_is_rejected() -> None:
    payload = valid_request_payload()
    payload["request_type"] = "execute_remediation"

    with pytest.raises(ValidationError):
        DiagnosticRequest.model_validate(payload)


def test_naive_request_timestamp_is_rejected() -> None:
    payload = valid_request_payload()
    payload["request_timestamp"] = datetime(2026, 7, 19, 18, 30)

    with pytest.raises(ValidationError):
        DiagnosticRequest.model_validate(payload)


def test_empty_observed_symptoms_are_rejected() -> None:
    payload = valid_request_payload()
    payload["observed_symptoms"] = []

    with pytest.raises(ValidationError):
        DiagnosticRequest.model_validate(payload)


def test_more_than_twenty_symptoms_are_rejected() -> None:
    payload = valid_request_payload()
    payload["observed_symptoms"] = [f"symptom-{index}" for index in range(21)]

    with pytest.raises(ValidationError):
        DiagnosticRequest.model_validate(payload)


def test_more_than_fifty_alert_identifiers_are_rejected() -> None:
    payload = valid_request_payload()
    payload["alert_ids"] = [f"ALT-{index}" for index in range(51)]

    with pytest.raises(ValidationError):
        DiagnosticRequest.model_validate(payload)


def test_request_model_is_frozen() -> None:
    request = DiagnosticRequest.model_validate(valid_request_payload())

    with pytest.raises(ValidationError):
        request.request_id = "req-replacement"


def test_request_collections_are_immutable() -> None:
    request = DiagnosticRequest.model_validate(valid_request_payload())
    original_symptoms = deepcopy(request.observed_symptoms)

    with pytest.raises(AttributeError):
        request.observed_symptoms.append("unauthorized mutation")  # type: ignore[attr-defined]

    assert request.observed_symptoms == original_symptoms


def test_json_serialization_preserves_contract_values() -> None:
    request = DiagnosticRequest.model_validate(valid_request_payload())
    serialized = request.model_dump(mode="json")

    assert serialized["environment"] == "production"
    assert serialized["request_type"] == "diagnostic_recommendation"
    assert serialized["observed_symptoms"] == [
        "HTTP 503 rate increased",
        "Dependency timeout alerts firing",
    ]
