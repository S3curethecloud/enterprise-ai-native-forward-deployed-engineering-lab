"""Integration tests for gateway CT-05 response validation."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from incident_diagnostic_api.contracts import (
    ControlledError,
    DiagnosticResponse,
)
from incident_diagnostic_api.services.evidence import app as evidence_app
from incident_diagnostic_api.services.gateway import app as gateway_app
from incident_diagnostic_api.services.runtime import app as runtime_app

VALIDATION_PATH = "/v1/contracts/diagnostic-response/validate"


def valid_response_payload() -> dict[str, Any]:
    """Return a JSON-compatible valid CT-05 recommendation."""

    return {
        "contract_version": "1.0",
        "request_id": "req-7f31",
        "trace_id": "trace-a812",
        "incident_id": "INC-10427",
        "service_id": "payments-api",
        "response_status": "recommendation",
        "diagnostic_summary": ("The timeout pattern is consistent with dependency degradation."),
        "observations": [
            {
                "claim_id": "claim-1",
                "text": "Dependency timeout alerts are present.",
            }
        ],
        "inferences": [
            {
                "claim_id": "claim-2",
                "text": "A downstream dependency is a plausible cause.",
            }
        ],
        "evidence_citations": [
            {
                "claim_id": "claim-2",
                "evidence_ids": ["ev-1"],
                "support_type": "direct",
            }
        ],
        "recommended_next_steps": [
            {
                "step_id": "step-1",
                "description": "Verify downstream dependency health.",
                "action_class": "human_review_required",
                "execution_status": "not_executed",
                "supporting_evidence_ids": ["ev-1"],
                "risk_note": "Follow existing incident and change procedures.",
            }
        ],
        "confidence_classification": "moderate",
        "limitations": ["Live production telemetry was not inspected."],
        "policy_outcome": {
            "policy_decision_id": "pd-991",
            "outcome": "allow",
        },
        "generated_at": "2026-07-19T18:30:04Z",
    }


def valid_abstention_payload() -> dict[str, Any]:
    """Return a JSON-compatible valid CT-05 abstention."""

    return {
        "contract_version": "1.0",
        "request_id": "req-7f32",
        "trace_id": "trace-a813",
        "incident_id": "INC-10428",
        "service_id": "payments-api",
        "response_status": "abstention",
        "limitations": ["No sufficient authorized evidence was available."],
        "abstention_reason": {
            "reason_code": "EVIDENCE_INSUFFICIENT",
            "safe_message": ("The available evidence cannot support a diagnosis."),
        },
        "policy_outcome": {
            "policy_decision_id": "pd-992",
            "outcome": "allow",
        },
        "generated_at": "2026-07-19T18:30:04Z",
    }


def test_valid_recommendation_returns_validated_contract() -> None:
    with TestClient(gateway_app) as client:
        response = client.post(
            VALIDATION_PATH,
            json=valid_response_payload(),
            headers={"X-Correlation-ID": "response-validation-101"},
        )

    assert response.status_code == 200
    validated = DiagnosticResponse.model_validate(response.json())

    assert validated.response_status.value == "recommendation"
    assert validated.confidence_classification is not None
    assert validated.confidence_classification.value == "moderate"
    assert validated.recommended_next_steps[0].execution_status.value == "not_executed"
    assert response.headers["X-Correlation-ID"] == "response-validation-101"


def test_valid_abstention_returns_validated_contract() -> None:
    with TestClient(gateway_app) as client:
        response = client.post(
            VALIDATION_PATH,
            json=valid_abstention_payload(),
        )

    assert response.status_code == 200
    validated = DiagnosticResponse.model_validate(response.json())

    assert validated.response_status.value == "abstention"
    assert validated.abstention_reason is not None
    assert validated.abstention_reason.reason_code == "EVIDENCE_INSUFFICIENT"


@pytest.mark.parametrize(
    ("field_path", "invalid_value"),
    [
        ("response_status", "executed"),
        ("confidence_classification", "certain"),
    ],
)
def test_invalid_top_level_value_returns_controlled_error(
    field_path: str,
    invalid_value: str,
) -> None:
    payload = valid_response_payload()
    payload[field_path] = invalid_value

    with TestClient(gateway_app) as client:
        response = client.post(
            VALIDATION_PATH,
            json=payload,
            headers={"X-Correlation-ID": "invalid-response-101"},
        )

    assert response.status_code == 422
    error = ControlledError.model_validate(response.json())

    assert error.error_code.value == "INVALID_REQUEST"
    assert error.error_category.value == "validation"
    assert error.failed_stage.value == "admission"
    assert error.trace_id == "invalid-response-101"


def test_executed_recommendation_is_rejected() -> None:
    payload = valid_response_payload()
    payload["recommended_next_steps"][0]["execution_status"] = "executed"

    with TestClient(gateway_app) as client:
        response = client.post(
            VALIDATION_PATH,
            json=payload,
            headers={"X-Correlation-ID": "execution-claim-101"},
        )

    assert response.status_code == 422
    error = ControlledError.model_validate(response.json())

    assert error.error_code.value == "INVALID_REQUEST"
    assert error.trace_id == "execution-claim-101"
    assert "executed" not in response.text


def test_uncited_inference_is_rejected() -> None:
    payload = valid_response_payload()
    payload["evidence_citations"] = []

    with TestClient(gateway_app) as client:
        response = client.post(
            VALIDATION_PATH,
            json=payload,
        )

    assert response.status_code == 422
    error = ControlledError.model_validate(response.json())

    assert error.error_code.value == "INVALID_REQUEST"


def test_abstention_with_recommended_action_is_rejected() -> None:
    payload = valid_abstention_payload()
    payload["recommended_next_steps"] = valid_response_payload()["recommended_next_steps"]

    with TestClient(gateway_app) as client:
        response = client.post(
            VALIDATION_PATH,
            json=payload,
        )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "application",
    [
        runtime_app,
        evidence_app,
    ],
)
def test_response_validation_route_is_gateway_only(
    application: Any,
) -> None:
    with TestClient(application) as client:
        response = client.post(
            VALIDATION_PATH,
            json=valid_response_payload(),
        )

    assert response.status_code == 404


def test_openapi_documents_ct05_success_and_ct06_failure() -> None:
    with TestClient(gateway_app) as client:
        response = client.get("/openapi.json")

    operation = response.json()["paths"][VALIDATION_PATH]["post"]

    assert "200" in operation["responses"]
    assert "422" in operation["responses"]
    assert (
        operation["responses"]["422"]["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/ControlledError"
    )
