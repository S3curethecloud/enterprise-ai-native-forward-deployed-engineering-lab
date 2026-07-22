"""Tests for the deterministic, network-free Phase 6B local mock provider."""

from datetime import UTC, datetime, timedelta

import pytest

from incident_diagnostic_api.providers import (
    MOCK_ADAPTER_ID,
    MOCK_MODEL_ID,
    MOCK_PROVIDER_VERSION,
    DeterministicMockProvider,
    ProviderError,
    ProviderErrorCode,
    ProviderFinishReason,
    ProviderKind,
    ProviderRequest,
    ProviderResponse,
    estimate_mock_tokens,
)

REQUESTED_AT = datetime(2026, 7, 21, 19, 0, tzinfo=UTC)
COMPLETED_AT = REQUESTED_AT + timedelta(seconds=1)


def build_request(**changes: object) -> ProviderRequest:
    """Build one valid request for the fixed deterministic mock identity."""

    values: dict[str, object] = {
        "request_id": "request-602",
        "trace_id": "trace-602",
        "provider_kind": ProviderKind.LOCAL_MOCK,
        "adapter_id": MOCK_ADAPTER_ID,
        "model_id": MOCK_MODEL_ID,
        "input_text": "Summarize this bounded synthetic evidence.",
        "requested_capabilities": ("text_generation",),
        "maximum_output_tokens": 16,
        "temperature": 0.0,
        "requested_at": REQUESTED_AT,
    }
    values.update(changes)
    return ProviderRequest.model_validate(values)


def generate(**changes: object) -> ProviderResponse | ProviderError:
    """Generate one deterministic result from the default request."""

    return DeterministicMockProvider().generate(
        request=build_request(**changes),
        completed_at=COMPLETED_AT,
    )


def assert_error(
    result: ProviderResponse | ProviderError,
    code: ProviderErrorCode,
) -> ProviderError:
    """Assert and return one normalized mock-provider error."""

    assert isinstance(result, ProviderError)
    assert result.error_code is code
    assert result.safe_message
    return result


def test_mock_version_and_identity_are_explicit() -> None:
    assert MOCK_PROVIDER_VERSION == "deterministic-local-mock-v1"
    assert MOCK_ADAPTER_ID == "local-mock-v1"
    assert MOCK_MODEL_ID == "deterministic-model-v1"


def test_mock_declares_only_supported_capabilities() -> None:
    declaration = DeterministicMockProvider().capabilities

    assert declaration.provider_kind is ProviderKind.LOCAL_MOCK
    assert [item.value for item in declaration.capabilities] == [
        "text_generation",
        "structured_output",
    ]


def test_valid_request_returns_correlated_response() -> None:
    result = generate()

    assert isinstance(result, ProviderResponse)
    assert result.request_id == "request-602"
    assert result.trace_id == "trace-602"
    assert result.provider_kind is ProviderKind.LOCAL_MOCK
    assert result.adapter_id == MOCK_ADAPTER_ID
    assert result.model_id == MOCK_MODEL_ID
    assert result.completed_at == COMPLETED_AT


def test_output_is_repeatable() -> None:
    first = generate()
    second = generate()

    assert isinstance(first, ProviderResponse)
    assert first == second


def test_different_input_produces_different_output() -> None:
    first = generate(input_text="first bounded input")
    second = generate(input_text="second bounded input")

    assert isinstance(first, ProviderResponse)
    assert isinstance(second, ProviderResponse)
    assert first.output_text != second.output_text


def test_usage_is_deterministic_and_consistent() -> None:
    request = build_request()
    result = DeterministicMockProvider().generate(
        request=request,
        completed_at=COMPLETED_AT,
    )

    assert isinstance(result, ProviderResponse)
    assert result.usage.input_tokens == estimate_mock_tokens(request.input_text)
    assert result.usage.output_tokens == estimate_mock_tokens(result.output_text)
    assert result.usage.total_tokens == (result.usage.input_tokens + result.usage.output_tokens)


def test_output_limit_is_enforced() -> None:
    result = generate(maximum_output_tokens=1)

    assert isinstance(result, ProviderResponse)
    assert result.finish_reason is ProviderFinishReason.OUTPUT_LIMIT
    assert result.usage.output_tokens == 1


def test_stop_sequence_is_enforced() -> None:
    result = generate(stop_sequences=("deterministic",))

    assert isinstance(result, ProviderResponse)
    assert result.finish_reason is ProviderFinishReason.STOP_SEQUENCE
    assert "deterministic" not in result.output_text


def test_stop_sequence_cannot_remove_entire_output() -> None:
    result = generate(stop_sequences=("mock-",))

    assert_error(result, ProviderErrorCode.RESPONSE_INVALID)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("provider_kind", ProviderKind.OPENAI),
        ("adapter_id", "another-adapter"),
        ("model_id", "another-model"),
    ],
)
def test_mismatched_identity_returns_safe_error(field: str, value: object) -> None:
    result = generate(**{field: value})

    error = assert_error(result, ProviderErrorCode.INVALID_REQUEST)
    assert error.retryable is False


def test_completion_before_request_returns_safe_error() -> None:
    result = DeterministicMockProvider().generate(
        request=build_request(),
        completed_at=REQUESTED_AT - timedelta(microseconds=1),
    )

    assert_error(result, ProviderErrorCode.INVALID_REQUEST)


def test_nonzero_temperature_returns_safe_error() -> None:
    result = generate(temperature=0.1)

    assert_error(result, ProviderErrorCode.INVALID_REQUEST)


@pytest.mark.parametrize("capability", ["streaming", "tool_calling"])
def test_unsupported_execution_capability_returns_safe_error(
    capability: str,
) -> None:
    result = generate(
        requested_capabilities=("text_generation", capability),
    )

    error = assert_error(result, ProviderErrorCode.UNSUPPORTED_CAPABILITY)
    assert error.retryable is False


def test_input_limit_returns_context_error() -> None:
    result = generate(input_text=" ".join("x" for _ in range(513)))

    assert_error(result, ProviderErrorCode.CONTEXT_LIMIT_EXCEEDED)


def test_output_limit_above_mock_capability_returns_error() -> None:
    result = generate(maximum_output_tokens=257)

    assert_error(result, ProviderErrorCode.INVALID_REQUEST)


def test_errors_preserve_request_correlation() -> None:
    result = generate(temperature=1.0)

    error = assert_error(result, ProviderErrorCode.INVALID_REQUEST)
    assert error.request_id == "request-602"
    assert error.trace_id == "trace-602"
    assert error.occurred_at == COMPLETED_AT


def test_provider_is_stateless() -> None:
    provider = DeterministicMockProvider()

    assert not hasattr(provider, "__dict__")
    assert provider.capabilities == provider.capabilities
