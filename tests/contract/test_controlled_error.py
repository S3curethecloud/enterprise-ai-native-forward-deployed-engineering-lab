"""Positive and negative contract tests for CT-06."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.contracts import ControlledError

NOW = datetime(2026, 7, 19, 18, 11, tzinfo=UTC)

CONTROLLED_CASES = [
    ("INVALID_REQUEST", "validation", False),
    ("UNSUPPORTED_VERSION", "validation", False),
    ("IDENTITY_REQUIRED", "identity", False),
    ("IDENTITY_EXPIRED", "identity", True),
    ("ACCESS_DENIED", "authorization", False),
    ("SERVICE_UNSUPPORTED", "validation", False),
    ("SOURCE_UNAVAILABLE", "evidence", True),
    ("EVIDENCE_INSUFFICIENT", "evidence", False),
    ("EVIDENCE_CONFLICT", "evidence", False),
    ("POLICY_UNAVAILABLE", "dependency", True),
    ("RESPONSE_INVALID", "response", True),
    ("DEPENDENCY_FAILURE", "dependency", True),
]


def valid_error_payload(
    error_code: str = "ACCESS_DENIED",
    error_category: str = "authorization",
    retryable: bool = False,
) -> dict[str, Any]:
    """Return a valid controlled-error payload."""

    payload: dict[str, Any] = {
        "contract_version": "1.0",
        "request_id": "req-7f31",
        "trace_id": "trace-a812",
        "error_code": error_code,
        "error_category": error_category,
        "safe_message": "The request could not be completed safely.",
        "retryable": retryable,
        "failed_stage": "policy",
        "occurred_at": NOW,
    }

    if error_code == "ACCESS_DENIED":
        payload["policy_outcome"] = {
            "policy_decision_id": "pd-991",
            "outcome": "deny",
        }

    return payload


def test_valid_access_denial_is_accepted() -> None:
    error = ControlledError.model_validate(valid_error_payload())

    assert error.error_code.value == "ACCESS_DENIED"
    assert error.error_category.value == "authorization"
    assert error.retryable is False
    assert error.policy_outcome is not None


@pytest.mark.parametrize(
    ("error_code", "error_category", "retryable"),
    CONTROLLED_CASES,
)
def test_each_controlled_error_mapping_is_accepted(
    error_code: str,
    error_category: str,
    retryable: bool,
) -> None:
    error = ControlledError.model_validate(
        valid_error_payload(
            error_code=error_code,
            error_category=error_category,
            retryable=retryable,
        )
    )

    assert error.error_code.value == error_code
    assert error.error_category.value == error_category
    assert error.retryable is retryable


def test_mismatched_error_category_is_rejected() -> None:
    payload = valid_error_payload()
    payload["error_category"] = "internal"

    with pytest.raises(
        ValidationError,
        match="error category does not match the controlled error code",
    ):
        ControlledError.model_validate(payload)


@pytest.mark.parametrize(
    ("error_code", "error_category", "expected_retryable"),
    CONTROLLED_CASES,
)
def test_mismatched_retryability_is_rejected(
    error_code: str,
    error_category: str,
    expected_retryable: bool,
) -> None:
    payload = valid_error_payload(
        error_code=error_code,
        error_category=error_category,
        retryable=not expected_retryable,
    )

    with pytest.raises(
        ValidationError,
        match="retryable value does not match the controlled error code",
    ):
        ControlledError.model_validate(payload)


def test_access_denial_requires_policy_outcome() -> None:
    payload = valid_error_payload()
    payload.pop("policy_outcome")

    with pytest.raises(
        ValidationError,
        match="access denial requires a policy outcome reference",
    ):
        ControlledError.model_validate(payload)


@pytest.mark.parametrize("retryable", [False, True])
def test_internal_error_requires_explicit_retry_posture(retryable: bool) -> None:
    error = ControlledError.model_validate(
        valid_error_payload(
            error_code="INTERNAL_ERROR",
            error_category="internal",
            retryable=retryable,
        )
    )

    assert error.retryable is retryable


def test_unknown_error_code_is_rejected() -> None:
    payload = valid_error_payload()
    payload["error_code"] = "MODEL_DECIDED_ERROR"

    with pytest.raises(ValidationError):
        ControlledError.model_validate(payload)


def test_unknown_error_field_is_rejected() -> None:
    payload = valid_error_payload()
    payload["stack_trace"] = "sensitive implementation detail"

    with pytest.raises(ValidationError):
        ControlledError.model_validate(payload)


def test_naive_error_timestamp_is_rejected() -> None:
    payload = valid_error_payload()
    payload["occurred_at"] = datetime(2026, 7, 19, 18, 11)

    with pytest.raises(ValidationError):
        ControlledError.model_validate(payload)


def test_controlled_error_is_frozen() -> None:
    error = ControlledError.model_validate(valid_error_payload())

    with pytest.raises(ValidationError):
        error.safe_message = "Changed after validation"
