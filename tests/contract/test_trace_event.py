"""Positive and negative contract tests for CT-07."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.contracts import TraceEvent

NOW = datetime(2026, 7, 19, 18, 12, tzinfo=UTC)

FIXED_EVENT_STAGES = [
    ("request_received", "admission"),
    ("request_validated", "admission"),
    ("identity_validated", "identity"),
    ("policy_evaluated", "policy"),
    ("retrieval_started", "retrieval"),
    ("retrieval_completed", "retrieval"),
    ("evidence_assessed", "evidence_assessment"),
    ("generation_started", "generation"),
    ("generation_completed", "generation"),
    ("response_validated", "response_validation"),
    ("response_returned", "response_delivery"),
]


def valid_trace_payload() -> dict[str, Any]:
    """Return a valid policy-evaluation trace event."""

    return {
        "contract_version": "1.0",
        "event_id": "event-104",
        "trace_id": "trace-a812",
        "request_id": "req-7f31",
        "event_name": "policy_evaluated",
        "component": "local-policy-boundary",
        "stage": "policy",
        "outcome": "succeeded",
        "policy_decision_id": "pd-991",
        "duration_ms": 2.4,
        "input_reference": "request:req-7f31",
        "output_reference": "decision:pd-991",
        "reason_codes": ["AUTHORIZED_SERVICE_SCOPE"],
        "timestamp": NOW,
        "attributes": {
            "tenant_id": "tenant-a",
            "service_id": "payments-api",
            "contract_name": "CT-03",
            "contract_version_used": "1.0",
        },
    }


def test_valid_trace_event_is_accepted() -> None:
    event = TraceEvent.model_validate(valid_trace_payload())

    assert event.event_name.value == "policy_evaluated"
    assert event.stage.value == "policy"
    assert event.policy_decision_id == "pd-991"
    assert event.attributes.tenant_id == "tenant-a"


@pytest.mark.parametrize(("event_name", "stage"), FIXED_EVENT_STAGES)
def test_fixed_event_stage_mapping_is_accepted(
    event_name: str,
    stage: str,
) -> None:
    payload = valid_trace_payload()
    payload["event_name"] = event_name
    payload["stage"] = stage

    if event_name != "policy_evaluated":
        payload["policy_decision_id"] = None

    event = TraceEvent.model_validate(payload)

    assert event.event_name.value == event_name
    assert event.stage.value == stage


@pytest.mark.parametrize(("event_name", "expected_stage"), FIXED_EVENT_STAGES)
def test_fixed_event_stage_mismatch_is_rejected(
    event_name: str,
    expected_stage: str,
) -> None:
    payload = valid_trace_payload()
    payload["event_name"] = event_name
    payload["stage"] = "generation" if expected_stage != "generation" else "admission"

    with pytest.raises(
        ValidationError,
        match="trace event does not match its lifecycle stage",
    ):
        TraceEvent.model_validate(payload)


def test_policy_evaluation_requires_decision_identifier() -> None:
    payload = valid_trace_payload()
    payload["policy_decision_id"] = None

    with pytest.raises(
        ValidationError,
        match="policy evaluation requires a policy decision identifier",
    ):
        TraceEvent.model_validate(payload)


def test_policy_denial_requires_decision_identifier() -> None:
    payload = valid_trace_payload()
    payload["event_name"] = "request_denied"
    payload["outcome"] = "denied"
    payload["policy_decision_id"] = None

    with pytest.raises(
        ValidationError,
        match="policy denial requires a policy decision identifier",
    ):
        TraceEvent.model_validate(payload)


def test_identity_denial_does_not_fabricate_policy_decision() -> None:
    payload = valid_trace_payload()
    payload["event_name"] = "request_denied"
    payload["stage"] = "identity"
    payload["outcome"] = "denied"
    payload["policy_decision_id"] = None
    payload["reason_codes"] = ["IDENTITY_REQUIRED"]

    event = TraceEvent.model_validate(payload)

    assert event.policy_decision_id is None
    assert event.stage.value == "identity"


def test_negative_duration_is_rejected() -> None:
    payload = valid_trace_payload()
    payload["duration_ms"] = -0.01

    with pytest.raises(ValidationError):
        TraceEvent.model_validate(payload)


def test_retry_attempt_above_five_is_rejected() -> None:
    payload = valid_trace_payload()
    payload["attributes"]["retry_attempt"] = 6

    with pytest.raises(ValidationError):
        TraceEvent.model_validate(payload)


def test_evidence_count_above_fifty_is_rejected() -> None:
    payload = valid_trace_payload()
    payload["attributes"]["evidence_count"] = 51

    with pytest.raises(ValidationError):
        TraceEvent.model_validate(payload)


@pytest.mark.parametrize(
    "prohibited_attribute",
    [
        "raw_prompt",
        "raw_evidence",
        "credential",
        "access_token",
        "chain_of_thought",
    ],
)
def test_unallowlisted_trace_attribute_is_rejected(
    prohibited_attribute: str,
) -> None:
    payload = valid_trace_payload()
    payload["attributes"][prohibited_attribute] = "sensitive-value"

    with pytest.raises(ValidationError):
        TraceEvent.model_validate(payload)


def test_unknown_top_level_trace_field_is_rejected() -> None:
    payload = valid_trace_payload()
    payload["authorization_override"] = True

    with pytest.raises(ValidationError):
        TraceEvent.model_validate(payload)


def test_unknown_event_name_is_rejected() -> None:
    payload = valid_trace_payload()
    payload["event_name"] = "production_restarted"

    with pytest.raises(ValidationError):
        TraceEvent.model_validate(payload)


def test_lowercase_reason_code_is_rejected() -> None:
    payload = valid_trace_payload()
    payload["reason_codes"] = ["authorized_service_scope"]

    with pytest.raises(ValidationError):
        TraceEvent.model_validate(payload)


def test_naive_trace_timestamp_is_rejected() -> None:
    payload = valid_trace_payload()
    payload["timestamp"] = datetime(2026, 7, 19, 18, 12)

    with pytest.raises(ValidationError):
        TraceEvent.model_validate(payload)


def test_trace_reason_codes_are_immutable() -> None:
    event = TraceEvent.model_validate(valid_trace_payload())

    with pytest.raises(AttributeError):
        event.reason_codes.append("ANOTHER_REASON")  # type: ignore[attr-defined]

    assert event.reason_codes == ("AUTHORIZED_SERVICE_SCOPE",)


def test_trace_attributes_are_frozen() -> None:
    event = TraceEvent.model_validate(valid_trace_payload())

    with pytest.raises(ValidationError):
        event.attributes.tenant_id = "tenant-b"
