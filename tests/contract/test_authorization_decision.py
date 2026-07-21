"""Positive and negative contract tests for CT-03."""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.contracts import AuthorizationDecision

DECIDED_AT = datetime(2026, 7, 19, 18, 5, tzinfo=UTC)


def valid_decision_payload() -> dict[str, Any]:
    """Return an isolated valid constrained retrieval decision."""

    return {
        "contract_version": "1.0",
        "policy_decision_id": "pd-991",
        "request_id": "req-7f31",
        "trace_id": "trace-a812",
        "subject_id": "user-1042",
        "operation": "retrieve_runbook_evidence",
        "resource_ids": [
            "runbook:payments-api",
            "runbook:restricted-service",
        ],
        "outcome": "constrain",
        "allowed_resource_ids": [
            "runbook:payments-api",
        ],
        "constraints": {
            "max_evidence_items": 10,
            "allowed_source_types": ["runbook"],
            "allowed_tenant_ids": ["tenant-a"],
            "allowed_service_ids": ["payments-api"],
            "allowed_sensitivities": ["internal"],
            "require_citations": True,
            "recommendation_only": True,
        },
        "reason_codes": ["AUTHORIZED_SERVICE_SCOPE"],
        "policy_version": "policy-1.0",
        "decided_at": DECIDED_AT,
        "expires_at": DECIDED_AT + timedelta(minutes=5),
    }


def test_valid_constrained_decision_is_accepted() -> None:
    decision = AuthorizationDecision.model_validate(valid_decision_payload())

    assert decision.outcome.value == "constrain"
    assert decision.allowed_resource_ids == ("runbook:payments-api",)
    assert decision.constraints.require_citations is True
    assert decision.constraints.recommendation_only is True


def test_authorized_resource_is_permitted_before_expiry() -> None:
    decision = AuthorizationDecision.model_validate(valid_decision_payload())

    assert decision.permits_resource("runbook:payments-api", DECIDED_AT)


def test_unlisted_resource_is_not_permitted() -> None:
    decision = AuthorizationDecision.model_validate(valid_decision_payload())

    assert not decision.permits_resource(
        "runbook:restricted-service",
        DECIDED_AT,
    )
    assert not decision.permits_resource("runbook:unknown-service", DECIDED_AT)


def test_denied_decision_permits_no_resource() -> None:
    payload = valid_decision_payload()
    payload["outcome"] = "deny"
    payload["allowed_resource_ids"] = []
    payload["reason_codes"] = ["ACCESS_DENIED"]

    decision = AuthorizationDecision.model_validate(payload)

    assert not decision.permits_resource("runbook:payments-api", DECIDED_AT)


def test_denied_decision_cannot_contain_allowed_resources() -> None:
    payload = valid_decision_payload()
    payload["outcome"] = "deny"

    with pytest.raises(
        ValidationError,
        match="denied decisions cannot contain allowed resources",
    ):
        AuthorizationDecision.model_validate(payload)


def test_allowed_resources_must_be_requested() -> None:
    payload = valid_decision_payload()
    payload["allowed_resource_ids"] = ["runbook:not-requested"]

    with pytest.raises(
        ValidationError,
        match="allowed resources must be a subset of requested resources",
    ):
        AuthorizationDecision.model_validate(payload)


@pytest.mark.parametrize("outcome", ["allow", "constrain"])
def test_permitted_retrieval_requires_an_allowed_resource(outcome: str) -> None:
    payload = valid_decision_payload()
    payload["outcome"] = outcome
    payload["allowed_resource_ids"] = []

    with pytest.raises(
        ValidationError,
        match="permitted retrieval requires at least one allowed resource",
    ):
        AuthorizationDecision.model_validate(payload)


def test_decision_must_expire_after_decision_time() -> None:
    payload = valid_decision_payload()
    payload["expires_at"] = DECIDED_AT

    with pytest.raises(
        ValidationError,
        match="authorization decision must expire after decision time",
    ):
        AuthorizationDecision.model_validate(payload)


def test_expired_decision_permits_no_resource() -> None:
    decision = AuthorizationDecision.model_validate(valid_decision_payload())

    assert decision.permits_resource(
        "runbook:payments-api",
        DECIDED_AT + timedelta(minutes=4),
    )
    assert not decision.permits_resource(
        "runbook:payments-api",
        DECIDED_AT + timedelta(minutes=5),
    )


def test_naive_expiration_check_is_rejected() -> None:
    decision = AuthorizationDecision.model_validate(valid_decision_payload())

    with pytest.raises(
        ValueError,
        match="expiration checks require a timezone-aware timestamp",
    ):
        decision.is_expired(datetime(2026, 7, 19, 18, 6))


@pytest.mark.parametrize("max_evidence_items", [0, 51])
def test_evidence_item_limit_is_bounded(max_evidence_items: int) -> None:
    payload = valid_decision_payload()
    payload["constraints"]["max_evidence_items"] = max_evidence_items

    with pytest.raises(ValidationError):
        AuthorizationDecision.model_validate(payload)


def test_citation_requirement_cannot_be_disabled() -> None:
    payload = valid_decision_payload()
    payload["constraints"]["require_citations"] = False

    with pytest.raises(ValidationError):
        AuthorizationDecision.model_validate(payload)


def test_recommendation_only_constraint_cannot_be_disabled() -> None:
    payload = valid_decision_payload()
    payload["constraints"]["recommendation_only"] = False

    with pytest.raises(ValidationError):
        AuthorizationDecision.model_validate(payload)


def test_production_mutation_operation_is_rejected() -> None:
    payload = valid_decision_payload()
    payload["operation"] = "restart_production_service"

    with pytest.raises(ValidationError):
        AuthorizationDecision.model_validate(payload)


def test_lowercase_reason_code_is_rejected() -> None:
    payload = valid_decision_payload()
    payload["reason_codes"] = ["access_granted"]

    with pytest.raises(ValidationError):
        AuthorizationDecision.model_validate(payload)


def test_unknown_decision_field_is_rejected() -> None:
    payload = valid_decision_payload()
    payload["model_authorized"] = True

    with pytest.raises(ValidationError):
        AuthorizationDecision.model_validate(payload)


def test_decision_collections_are_immutable() -> None:
    decision = AuthorizationDecision.model_validate(valid_decision_payload())

    with pytest.raises(AttributeError):
        decision.allowed_resource_ids.append(  # type: ignore[attr-defined]
            "runbook:another-service"
        )

    assert decision.allowed_resource_ids == ("runbook:payments-api",)


@pytest.mark.parametrize(
    ("constraint_field", "expected_message"),
    [
        (
            "allowed_tenant_ids",
            "permitted retrieval requires an allowed tenant",
        ),
        (
            "allowed_service_ids",
            "permitted retrieval requires an allowed service",
        ),
        (
            "allowed_sensitivities",
            "permitted retrieval requires allowed sensitivities",
        ),
    ],
)
def test_permitted_retrieval_requires_explicit_authorization_scope(
    constraint_field: str,
    expected_message: str,
) -> None:
    payload = valid_decision_payload()
    payload["constraints"][constraint_field] = []

    with pytest.raises(ValidationError, match=expected_message):
        AuthorizationDecision.model_validate(payload)


def test_denied_retrieval_does_not_require_allowed_scope() -> None:
    payload = valid_decision_payload()
    payload["outcome"] = "deny"
    payload["allowed_resource_ids"] = []
    payload["constraints"]["allowed_tenant_ids"] = []
    payload["constraints"]["allowed_service_ids"] = []
    payload["constraints"]["allowed_sensitivities"] = []

    decision = AuthorizationDecision.model_validate(payload)

    assert decision.outcome.value == "deny"
    assert decision.constraints.allowed_tenant_ids == ()
    assert decision.constraints.allowed_service_ids == ()
    assert decision.constraints.allowed_sensitivities == ()
