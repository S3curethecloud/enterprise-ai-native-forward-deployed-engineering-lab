"""Integration tests for gateway CT-01 and CT-06 behavior."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from incident_diagnostic_api.contracts import (
    ControlledError,
    DiagnosticRequest,
)
from incident_diagnostic_api.services.evidence import app as evidence_app
from incident_diagnostic_api.services.gateway import app as gateway_app
from incident_diagnostic_api.services.runtime import app as runtime_app

VALIDATION_PATH = "/v1/contracts/diagnostic-request/validate"


def valid_request_payload() -> dict[str, Any]:
    """Return a JSON-compatible valid CT-01 request."""

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
        "request_timestamp": "2026-07-19T18:30:00Z",
        "request_type": "diagnostic_recommendation",
        "alert_ids": ["ALT-8801"],
        "affected_component": "authorization-adapter",
    }


def test_valid_ct01_request_returns_validated_contract() -> None:
    payload = valid_request_payload()

    with TestClient(gateway_app) as client:
        response = client.post(
            VALIDATION_PATH,
            json=payload,
            headers={"X-Correlation-ID": "contract-validation-101"},
        )

    assert response.status_code == 200
    validated = DiagnosticRequest.model_validate(response.json())

    assert validated.request_id == "req-7f31"
    assert validated.request_type.value == "diagnostic_recommendation"
    assert response.headers["X-Correlation-ID"] == "contract-validation-101"


@pytest.mark.parametrize(
    "missing_field",
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
def test_missing_required_field_returns_controlled_error(
    missing_field: str,
) -> None:
    payload = valid_request_payload()
    payload.pop(missing_field)

    with TestClient(gateway_app) as client:
        response = client.post(
            VALIDATION_PATH,
            json=payload,
            headers={"X-Correlation-ID": "invalid-contract-101"},
        )

    assert response.status_code == 422
    error = ControlledError.model_validate(response.json())

    assert error.error_code.value == "INVALID_REQUEST"
    assert error.error_category.value == "validation"
    assert error.retryable is False
    assert error.failed_stage.value == "admission"
    assert error.trace_id == "invalid-contract-101"
    assert response.headers["X-Correlation-ID"] == error.trace_id


def test_execution_request_returns_controlled_error() -> None:
    payload = valid_request_payload()
    payload["request_type"] = "execute_remediation"

    with TestClient(gateway_app) as client:
        response = client.post(
            VALIDATION_PATH,
            json=payload,
            headers={"X-Correlation-ID": "execution-denied-101"},
        )

    assert response.status_code == 422
    error = ControlledError.model_validate(response.json())

    assert error.error_code.value == "INVALID_REQUEST"
    assert error.trace_id == "execution-denied-101"


def test_self_asserted_identity_is_not_reflected_in_error() -> None:
    payload = valid_request_payload()
    payload["subject_id"] = "self-asserted-administrator"

    with TestClient(gateway_app) as client:
        response = client.post(
            VALIDATION_PATH,
            json=payload,
            headers={"X-Correlation-ID": "identity-rejected-101"},
        )

    assert response.status_code == 422
    error = ControlledError.model_validate(response.json())

    assert error.error_code.value == "INVALID_REQUEST"
    assert "self-asserted-administrator" not in response.text
    assert "subject_id" not in response.text


@pytest.mark.parametrize(
    "application",
    [
        runtime_app,
        evidence_app,
    ],
)
def test_validation_route_does_not_exist_on_non_gateway_service(
    application: Any,
) -> None:
    with TestClient(application) as client:
        response = client.post(
            VALIDATION_PATH,
            json=valid_request_payload(),
        )

    assert response.status_code == 404


def test_openapi_documents_ct01_success_and_ct06_failure() -> None:
    with TestClient(gateway_app) as client:
        response = client.get("/openapi.json")

    operation = response.json()["paths"][VALIDATION_PATH]["post"]

    assert "200" in operation["responses"]
    assert "422" in operation["responses"]
    assert (
        operation["responses"]["422"]["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/ControlledError"
    )
