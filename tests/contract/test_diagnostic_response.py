"""Positive and negative contract tests for CT-05."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.contracts import DiagnosticResponse, EvidenceItem

NOW = datetime(2026, 7, 19, 18, 10, tzinfo=UTC)


def valid_evidence_payload() -> dict[str, Any]:
    """Return evidence matching the response request and trace."""

    return {
        "contract_version": "1.0",
        "evidence_id": "ev-1",
        "request_id": "req-7f31",
        "trace_id": "trace-a812",
        "source_id": "runbook:payments-api",
        "source_type": "runbook",
        "document_id": "payments-runbook",
        "document_version": "v3",
        "passage_id": "dependency-timeout",
        "content": ("Check downstream dependency health when timeout alerts fire."),
        "title": "Payments dependency timeout procedure",
        "retrieval_score": 0.93,
        "authorization_decision_id": "pd-991",
        "freshness_status": "current",
        "retrieved_at": NOW,
        "sensitivity_classification": "internal",
        "content_hash": "a1b2c3d4",
    }


def valid_recommendation_payload() -> dict[str, Any]:
    """Return a valid recommendation response."""

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
        "generated_at": NOW,
    }


def valid_abstention_payload() -> dict[str, Any]:
    """Return a valid safe abstention response."""

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
            "safe_message": "The available evidence cannot support a diagnosis.",
        },
        "policy_outcome": {
            "policy_decision_id": "pd-992",
            "outcome": "allow",
        },
        "generated_at": NOW,
    }


def test_valid_recommendation_is_accepted() -> None:
    response = DiagnosticResponse.model_validate(valid_recommendation_payload())

    assert response.response_status.value == "recommendation"
    assert response.confidence_classification is not None
    assert response.confidence_classification.value == "moderate"
    assert response.recommended_next_steps[0].execution_status.value == "not_executed"


def test_valid_abstention_is_accepted() -> None:
    response = DiagnosticResponse.model_validate(valid_abstention_payload())

    assert response.response_status.value == "abstention"
    assert response.abstention_reason is not None
    assert response.abstention_reason.reason_code == "EVIDENCE_INSUFFICIENT"
    assert response.recommended_next_steps == ()


def test_recommendation_requires_diagnostic_summary() -> None:
    payload = valid_recommendation_payload()
    payload["diagnostic_summary"] = None

    with pytest.raises(
        ValidationError,
        match="recommendation requires a diagnostic summary",
    ):
        DiagnosticResponse.model_validate(payload)


def test_recommendation_requires_confidence_classification() -> None:
    payload = valid_recommendation_payload()
    payload["confidence_classification"] = None

    with pytest.raises(
        ValidationError,
        match="recommendation requires a confidence classification",
    ):
        DiagnosticResponse.model_validate(payload)


def test_recommendation_cannot_contain_abstention_reason() -> None:
    payload = valid_recommendation_payload()
    payload["abstention_reason"] = {
        "reason_code": "EVIDENCE_INSUFFICIENT",
        "safe_message": "Conflicting state",
    }

    with pytest.raises(
        ValidationError,
        match="recommendation cannot contain an abstention reason",
    ):
        DiagnosticResponse.model_validate(payload)


def test_abstention_requires_reason() -> None:
    payload = valid_abstention_payload()
    payload["abstention_reason"] = None

    with pytest.raises(
        ValidationError,
        match="abstention requires an abstention reason",
    ):
        DiagnosticResponse.model_validate(payload)


def test_abstention_cannot_contain_confidence() -> None:
    payload = valid_abstention_payload()
    payload["confidence_classification"] = "high"

    with pytest.raises(
        ValidationError,
        match="abstention cannot contain a confidence classification",
    ):
        DiagnosticResponse.model_validate(payload)


def test_abstention_cannot_contain_recommended_steps() -> None:
    payload = valid_abstention_payload()
    payload["recommended_next_steps"] = valid_recommendation_payload()["recommended_next_steps"]

    with pytest.raises(
        ValidationError,
        match="abstention cannot contain recommended next steps",
    ):
        DiagnosticResponse.model_validate(payload)


def test_duplicate_claim_identifiers_are_rejected() -> None:
    payload = valid_recommendation_payload()
    payload["inferences"][0]["claim_id"] = "claim-1"
    payload["evidence_citations"][0]["claim_id"] = "claim-1"

    with pytest.raises(
        ValidationError,
        match="response claim identifiers must be unique",
    ):
        DiagnosticResponse.model_validate(payload)


def test_citation_must_reference_known_claim() -> None:
    payload = valid_recommendation_payload()
    payload["evidence_citations"][0]["claim_id"] = "claim-unknown"

    with pytest.raises(
        ValidationError,
        match="citations must reference known response claims",
    ):
        DiagnosticResponse.model_validate(payload)


def test_every_inference_requires_citation() -> None:
    payload = valid_recommendation_payload()
    payload["evidence_citations"] = []

    with pytest.raises(
        ValidationError,
        match="every inference must contain an evidence citation",
    ):
        DiagnosticResponse.model_validate(payload)


def test_duplicate_step_identifiers_are_rejected() -> None:
    payload = valid_recommendation_payload()
    duplicate = dict(payload["recommended_next_steps"][0])
    payload["recommended_next_steps"].append(duplicate)

    with pytest.raises(
        ValidationError,
        match="recommended step identifiers must be unique",
    ):
        DiagnosticResponse.model_validate(payload)


def test_executed_status_is_rejected() -> None:
    payload = valid_recommendation_payload()
    payload["recommended_next_steps"][0]["execution_status"] = "executed"

    with pytest.raises(ValidationError):
        DiagnosticResponse.model_validate(payload)


def test_autonomous_action_class_is_rejected() -> None:
    payload = valid_recommendation_payload()
    payload["recommended_next_steps"][0]["action_class"] = "autonomous_execution"

    with pytest.raises(ValidationError):
        DiagnosticResponse.model_validate(payload)


def test_valid_evidence_lineage_is_accepted() -> None:
    response = DiagnosticResponse.model_validate(valid_recommendation_payload())
    evidence = EvidenceItem.model_validate(valid_evidence_payload())

    assert response.has_valid_evidence_lineage((evidence,))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("request_id", "req-another"),
        ("trace_id", "trace-another"),
        ("evidence_id", "ev-another"),
    ],
)
def test_mismatched_evidence_lineage_is_rejected(
    field: str,
    value: str,
) -> None:
    response = DiagnosticResponse.model_validate(valid_recommendation_payload())
    payload = valid_evidence_payload()
    payload[field] = value
    evidence = EvidenceItem.model_validate(payload)

    assert not response.has_valid_evidence_lineage((evidence,))


def test_empty_evidence_set_fails_lineage() -> None:
    response = DiagnosticResponse.model_validate(valid_recommendation_payload())

    assert not response.has_valid_evidence_lineage(())


def test_unknown_response_field_is_rejected() -> None:
    payload = valid_recommendation_payload()
    payload["remediation_executed"] = True

    with pytest.raises(ValidationError):
        DiagnosticResponse.model_validate(payload)


def test_response_collections_are_immutable() -> None:
    response = DiagnosticResponse.model_validate(valid_recommendation_payload())

    with pytest.raises(AttributeError):
        response.evidence_citations.append(  # type: ignore[attr-defined]
            response.evidence_citations[0]
        )

    assert len(response.evidence_citations) == 1


def test_error_response_cannot_contain_confidence() -> None:
    payload = valid_abstention_payload()
    payload["response_status"] = "error"
    payload["abstention_reason"] = None
    payload["confidence_classification"] = "high"

    with pytest.raises(
        ValidationError,
        match="error cannot contain a confidence classification",
    ):
        DiagnosticResponse.model_validate(payload)


def test_error_response_cannot_contain_recommended_steps() -> None:
    payload = valid_abstention_payload()
    payload["response_status"] = "error"
    payload["abstention_reason"] = None
    payload["recommended_next_steps"] = valid_recommendation_payload()["recommended_next_steps"]

    with pytest.raises(
        ValidationError,
        match="error cannot contain recommended next steps",
    ):
        DiagnosticResponse.model_validate(payload)
