"""Deterministic, network-free local mock provider for Phase 6B."""

from hashlib import sha256
from typing import Final

from incident_diagnostic_api.contracts.common import Timestamp
from incident_diagnostic_api.providers.contracts import (
    EXPECTED_ERROR_CATEGORIES,
    EXPECTED_ERROR_RETRYABILITY,
    ProviderCapability,
    ProviderError,
    ProviderErrorCode,
    ProviderFinishReason,
    ProviderKind,
    ProviderModelCapabilities,
    ProviderRequest,
    ProviderResponse,
    ProviderUsage,
)

MOCK_PROVIDER_VERSION: Final[str] = "deterministic-local-mock-v1"
MOCK_ADAPTER_ID: Final[str] = "local-mock-v1"
MOCK_MODEL_ID: Final[str] = "deterministic-model-v1"
MOCK_MAXIMUM_INPUT_TOKENS: Final[int] = 512
MOCK_MAXIMUM_OUTPUT_TOKENS: Final[int] = 256

type MockProviderResult = ProviderResponse | ProviderError


def estimate_mock_tokens(text: str) -> int:
    """Return the documented deterministic whitespace-token estimate."""

    return max(1, len(text.split()))


def _error(
    *,
    request: ProviderRequest,
    code: ProviderErrorCode,
    safe_message: str,
    occurred_at: Timestamp,
) -> ProviderError:
    """Build one normalized error without provider-sensitive detail."""

    return ProviderError(
        request_id=request.request_id,
        trace_id=request.trace_id,
        provider_kind=request.provider_kind,
        adapter_id=request.adapter_id,
        model_id=request.model_id,
        error_code=code,
        error_category=EXPECTED_ERROR_CATEGORIES[code],
        safe_message=safe_message,
        retryable=EXPECTED_ERROR_RETRYABILITY[code],
        occurred_at=occurred_at,
    )


def _deterministic_output(input_text: str) -> str:
    """Return stable synthetic output derived from bounded request content."""

    digest = sha256(f"{MOCK_PROVIDER_VERSION}:{input_text}".encode()).hexdigest()[:16]
    return f"mock-{digest} deterministic response"


def _bounded_output(
    *,
    output: str,
    maximum_output_tokens: int,
) -> tuple[str, ProviderFinishReason]:
    """Apply the request output-token limit using the mock estimator."""

    tokens = output.split()

    if len(tokens) <= maximum_output_tokens:
        return output, ProviderFinishReason.COMPLETED

    return (
        " ".join(tokens[:maximum_output_tokens]),
        ProviderFinishReason.OUTPUT_LIMIT,
    )


def _apply_stop_sequences(
    *,
    output: str,
    stop_sequences: tuple[str, ...],
) -> tuple[str | None, ProviderFinishReason]:
    """Stop at the earliest declared sequence without returning empty output."""

    offsets = [offset for sequence in stop_sequences if (offset := output.find(sequence)) >= 0]

    if not offsets:
        return output, ProviderFinishReason.COMPLETED

    stopped = output[: min(offsets)].rstrip()

    if not stopped:
        return None, ProviderFinishReason.STOP_SEQUENCE

    return stopped, ProviderFinishReason.STOP_SEQUENCE


class DeterministicMockProvider:
    """Stateless local mock implementing one fixed provider configuration."""

    __slots__ = ()

    @property
    def capabilities(self) -> ProviderModelCapabilities:
        """Return the immutable fixed mock capability declaration."""

        return ProviderModelCapabilities(
            provider_kind=ProviderKind.LOCAL_MOCK,
            adapter_id=MOCK_ADAPTER_ID,
            model_id=MOCK_MODEL_ID,
            capabilities=(
                ProviderCapability.TEXT_GENERATION,
                ProviderCapability.STRUCTURED_OUTPUT,
            ),
            maximum_input_tokens=MOCK_MAXIMUM_INPUT_TOKENS,
            maximum_output_tokens=MOCK_MAXIMUM_OUTPUT_TOKENS,
        )

    def generate(
        self,
        *,
        request: ProviderRequest,
        completed_at: Timestamp,
    ) -> MockProviderResult:
        """Return deterministic local output or one normalized safe error."""

        identity_matches = (
            request.provider_kind is ProviderKind.LOCAL_MOCK
            and request.adapter_id == MOCK_ADAPTER_ID
            and request.model_id == MOCK_MODEL_ID
        )

        if not identity_matches:
            return _error(
                request=request,
                code=ProviderErrorCode.INVALID_REQUEST,
                safe_message="The request does not target the local mock provider.",
                occurred_at=completed_at,
            )

        if completed_at < request.requested_at:
            return _error(
                request=request,
                code=ProviderErrorCode.INVALID_REQUEST,
                safe_message="The completion timestamp cannot precede the request.",
                occurred_at=completed_at,
            )

        if request.temperature != 0.0:
            return _error(
                request=request,
                code=ProviderErrorCode.INVALID_REQUEST,
                safe_message="The deterministic mock requires temperature zero.",
                occurred_at=completed_at,
            )

        supported = set(self.capabilities.capabilities)
        requested = set(request.requested_capabilities)

        if not requested.issubset(supported):
            return _error(
                request=request,
                code=ProviderErrorCode.UNSUPPORTED_CAPABILITY,
                safe_message="The local mock does not support a requested capability.",
                occurred_at=completed_at,
            )

        input_tokens = estimate_mock_tokens(request.input_text)

        if input_tokens > self.capabilities.maximum_input_tokens:
            return _error(
                request=request,
                code=ProviderErrorCode.CONTEXT_LIMIT_EXCEEDED,
                safe_message="The request exceeds the local mock input limit.",
                occurred_at=completed_at,
            )

        if request.maximum_output_tokens > self.capabilities.maximum_output_tokens:
            return _error(
                request=request,
                code=ProviderErrorCode.INVALID_REQUEST,
                safe_message="The request exceeds the local mock output limit.",
                occurred_at=completed_at,
            )

        raw_output = _deterministic_output(request.input_text)
        stopped_output, stop_reason = _apply_stop_sequences(
            output=raw_output,
            stop_sequences=request.stop_sequences,
        )

        if stopped_output is None:
            return _error(
                request=request,
                code=ProviderErrorCode.RESPONSE_INVALID,
                safe_message="A stop sequence removed the entire mock response.",
                occurred_at=completed_at,
            )

        output, limit_reason = _bounded_output(
            output=stopped_output,
            maximum_output_tokens=request.maximum_output_tokens,
        )
        finish_reason = (
            ProviderFinishReason.STOP_SEQUENCE
            if stop_reason is ProviderFinishReason.STOP_SEQUENCE
            else limit_reason
        )
        output_tokens = estimate_mock_tokens(output)

        return ProviderResponse(
            request_id=request.request_id,
            trace_id=request.trace_id,
            provider_kind=request.provider_kind,
            adapter_id=request.adapter_id,
            model_id=request.model_id,
            output_text=output,
            finish_reason=finish_reason,
            usage=ProviderUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
            ),
            completed_at=completed_at,
        )
