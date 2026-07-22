"""Positive, negative, and invariant tests for Phase 6A provider contracts."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.providers import (
    PROVIDER_CONTRACT_VERSION,
    ProviderError,
    ProviderErrorCode,
    ProviderModelCapabilities,
    ProviderRequest,
    ProviderResponse,
)

NOW = datetime(2026, 7, 21, 18, 30, tzinfo=UTC)


def capability_payload() -> dict[str, Any]:
    """Return one explicit deterministic mock capability declaration."""

    return {
        "contract_version": "1.0",
        "provider_contract_version": "provider-contract-v1",
        "provider_kind": "local_mock",
        "adapter_id": "local-mock-v1",
        "model_id": "deterministic-model-v1",
        "capabilities": ["text_generation", "structured_output"],
        "maximum_input_tokens": 4096,
        "maximum_output_tokens": 1024,
    }


def request_payload() -> dict[str, Any]:
    """Return one valid provider-neutral request."""

    return {
        "contract_version": "1.0",
        "provider_contract_version": "provider-contract-v1",
        "request_id": "request-601",
        "trace_id": "trace-601",
        "provider_kind": "local_mock",
        "adapter_id": "local-mock-v1",
        "model_id": "deterministic-model-v1",
        "input_text": "Summarize the bounded diagnostic evidence.",
        "requested_capabilities": ["text_generation"],
        "maximum_output_tokens": 256,
        "temperature": 0.0,
        "stop_sequences": ["END"],
        "requested_at": NOW,
    }


def response_payload() -> dict[str, Any]:
    """Return one normalized successful response."""

    return {
        "contract_version": "1.0",
        "provider_contract_version": "provider-contract-v1",
        "request_id": "request-601",
        "trace_id": "trace-601",
        "provider_kind": "local_mock",
        "adapter_id": "local-mock-v1",
        "model_id": "deterministic-model-v1",
        "output_text": "The bounded evidence supports further human review.",
        "finish_reason": "completed",
        "usage": {
            "input_tokens": 7,
            "output_tokens": 9,
            "total_tokens": 16,
        },
        "completed_at": NOW,
    }


def error_payload(
    *,
    code: str = "RATE_LIMITED",
    category: str = "capacity",
    retryable: bool = True,
) -> dict[str, Any]:
    """Return one normalized provider failure."""

    return {
        "contract_version": "1.0",
        "provider_contract_version": "provider-contract-v1",
        "request_id": "request-601",
        "trace_id": "trace-601",
        "provider_kind": "local_mock",
        "adapter_id": "local-mock-v1",
        "model_id": "deterministic-model-v1",
        "error_code": code,
        "error_category": category,
        "safe_message": "The provider request could not be completed.",
        "retryable": retryable,
        "occurred_at": NOW,
    }


def test_contract_version_is_explicit() -> None:
    assert PROVIDER_CONTRACT_VERSION == "provider-contract-v1"


def test_capability_declaration_is_accepted() -> None:
    declaration = ProviderModelCapabilities.model_validate(capability_payload())

    assert declaration.provider_kind.value == "local_mock"
    assert [item.value for item in declaration.capabilities] == [
        "text_generation",
        "structured_output",
    ]


def test_duplicate_capabilities_are_rejected() -> None:
    payload = capability_payload()
    payload["capabilities"] = ["text_generation", "text_generation"]

    with pytest.raises(ValidationError, match="provider capabilities must be unique"):
        ProviderModelCapabilities.model_validate(payload)


def test_empty_capabilities_are_rejected() -> None:
    payload = capability_payload()
    payload["capabilities"] = []

    with pytest.raises(ValidationError):
        ProviderModelCapabilities.model_validate(payload)


def test_request_is_accepted_and_frozen() -> None:
    request = ProviderRequest.model_validate(request_payload())

    assert request.temperature == 0.0
    assert request.requested_capabilities[0].value == "text_generation"

    with pytest.raises(ValidationError):
        request.model_id = "changed-model"


def test_request_requires_text_generation() -> None:
    payload = request_payload()
    payload["requested_capabilities"] = ["structured_output"]

    with pytest.raises(
        ValidationError,
        match="provider request requires text generation capability",
    ):
        ProviderRequest.model_validate(payload)


def test_duplicate_requested_capabilities_are_rejected() -> None:
    payload = request_payload()
    payload["requested_capabilities"] = ["text_generation", "text_generation"]

    with pytest.raises(
        ValidationError,
        match="requested provider capabilities must be unique",
    ):
        ProviderRequest.model_validate(payload)


def test_duplicate_stop_sequences_are_rejected() -> None:
    payload = request_payload()
    payload["stop_sequences"] = ["END", "END"]

    with pytest.raises(
        ValidationError,
        match="provider stop sequences must be unique",
    ):
        ProviderRequest.model_validate(payload)


@pytest.mark.parametrize("temperature", [-0.1, 2.1])
def test_temperature_outside_bounds_is_rejected(temperature: float) -> None:
    payload = request_payload()
    payload["temperature"] = temperature

    with pytest.raises(ValidationError):
        ProviderRequest.model_validate(payload)


def test_unknown_request_field_is_rejected() -> None:
    payload = request_payload()
    payload["api_key"] = "must-not-enter-contract"

    with pytest.raises(ValidationError):
        ProviderRequest.model_validate(payload)


def test_naive_request_timestamp_is_rejected() -> None:
    payload = request_payload()
    payload["requested_at"] = datetime(2026, 7, 21, 18, 30)

    with pytest.raises(ValidationError):
        ProviderRequest.model_validate(payload)


def test_response_is_accepted() -> None:
    response = ProviderResponse.model_validate(response_payload())

    assert response.finish_reason.value == "completed"
    assert response.usage.total_tokens == 16


def test_usage_total_must_equal_components() -> None:
    payload = response_payload()
    payload["usage"]["total_tokens"] = 99

    with pytest.raises(
        ValidationError,
        match="total tokens must equal input tokens plus output tokens",
    ):
        ProviderResponse.model_validate(payload)


def test_empty_response_output_is_rejected() -> None:
    payload = response_payload()
    payload["output_text"] = ""

    with pytest.raises(ValidationError):
        ProviderResponse.model_validate(payload)


ERROR_CASES = [
    ("INVALID_REQUEST", "request", False),
    ("AUTHENTICATION_FAILED", "authentication", False),
    ("ACCESS_DENIED", "authorization", False),
    ("UNSUPPORTED_CAPABILITY", "request", False),
    ("CONTEXT_LIMIT_EXCEEDED", "request", False),
    ("RATE_LIMITED", "capacity", True),
    ("REQUEST_TIMEOUT", "timeout", True),
    ("PROVIDER_UNAVAILABLE", "dependency", True),
    ("RESPONSE_INVALID", "response", False),
    ("INTERNAL_ERROR", "internal", False),
]


@pytest.mark.parametrize(("code", "category", "retryable"), ERROR_CASES)
def test_each_normalized_error_mapping_is_accepted(
    code: str,
    category: str,
    retryable: bool,
) -> None:
    error = ProviderError.model_validate(
        error_payload(code=code, category=category, retryable=retryable)
    )

    assert error.error_code is ProviderErrorCode(code)
    assert error.retryable is retryable


def test_error_category_mismatch_is_rejected() -> None:
    with pytest.raises(
        ValidationError,
        match="provider error category does not match its code",
    ):
        ProviderError.model_validate(error_payload(category="internal"))


def test_error_retryability_mismatch_is_rejected() -> None:
    with pytest.raises(
        ValidationError,
        match="provider error retryability does not match its code",
    ):
        ProviderError.model_validate(error_payload(retryable=False))


def test_unknown_error_field_is_rejected() -> None:
    payload = error_payload()
    payload["raw_provider_response"] = "sensitive provider detail"

    with pytest.raises(ValidationError):
        ProviderError.model_validate(payload)


def test_contracts_serialize_to_normalized_values() -> None:
    serialized = ProviderResponse.model_validate(response_payload()).model_dump(mode="json")

    assert serialized["provider_kind"] == "local_mock"
    assert serialized["finish_reason"] == "completed"
    assert serialized["usage"]["total_tokens"] == 16
