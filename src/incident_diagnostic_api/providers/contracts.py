"""Provider-neutral contracts for bounded Phase 6 multi-provider abstraction."""

from enum import StrEnum
from typing import Annotated, Final, Literal, Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    BoundedText,
    ContractModel,
    OpaqueIdentifier,
    ShortText,
    Timestamp,
    VersionedContract,
)

PROVIDER_CONTRACT_VERSION: Final[Literal["provider-contract-v1"]] = "provider-contract-v1"

TokenLimit = Annotated[int, Field(ge=1, le=1_000_000)]
OutputTokenLimit = Annotated[int, Field(ge=1, le=65_536)]
Temperature = Annotated[float, Field(ge=0.0, le=2.0)]
TokenCount = Annotated[int, Field(ge=0, le=10_000_000)]


class ProviderKind(StrEnum):
    """Provider identities understood by the neutral contract boundary."""

    LOCAL_MOCK = "local_mock"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_VERTEX = "google_vertex"


class ProviderCapability(StrEnum):
    """Capabilities that a provider model must declare explicitly."""

    TEXT_GENERATION = "text_generation"
    STRUCTURED_OUTPUT = "structured_output"
    STREAMING = "streaming"
    TOOL_CALLING = "tool_calling"


class ProviderFinishReason(StrEnum):
    """Normalized successful completion reasons."""

    COMPLETED = "completed"
    OUTPUT_LIMIT = "output_limit"
    STOP_SEQUENCE = "stop_sequence"


class ProviderErrorCategory(StrEnum):
    """Bounded categories for normalized provider failures."""

    REQUEST = "request"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CAPACITY = "capacity"
    TIMEOUT = "timeout"
    DEPENDENCY = "dependency"
    RESPONSE = "response"
    INTERNAL = "internal"


class ProviderErrorCode(StrEnum):
    """Provider-independent, non-sensitive error codes."""

    INVALID_REQUEST = "INVALID_REQUEST"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    ACCESS_DENIED = "ACCESS_DENIED"
    UNSUPPORTED_CAPABILITY = "UNSUPPORTED_CAPABILITY"
    CONTEXT_LIMIT_EXCEEDED = "CONTEXT_LIMIT_EXCEEDED"
    RATE_LIMITED = "RATE_LIMITED"
    REQUEST_TIMEOUT = "REQUEST_TIMEOUT"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    RESPONSE_INVALID = "RESPONSE_INVALID"
    INTERNAL_ERROR = "INTERNAL_ERROR"


Capabilities = Annotated[
    tuple[ProviderCapability, ...],
    Field(min_length=1, max_length=len(ProviderCapability)),
]

StopSequences = Annotated[
    tuple[ShortText, ...],
    Field(max_length=8),
]


class ProviderModelCapabilities(VersionedContract):
    """Explicit bounded capability declaration for one provider model."""

    provider_contract_version: Literal["provider-contract-v1"] = PROVIDER_CONTRACT_VERSION
    provider_kind: ProviderKind
    adapter_id: OpaqueIdentifier
    model_id: OpaqueIdentifier
    capabilities: Capabilities
    maximum_input_tokens: TokenLimit
    maximum_output_tokens: OutputTokenLimit

    @model_validator(mode="after")
    def validate_capabilities(self) -> Self:
        """Reject ambiguous duplicate capability declarations."""

        if len(self.capabilities) != len(set(self.capabilities)):
            raise ValueError("provider capabilities must be unique")

        return self


class ProviderRequest(VersionedContract):
    """Provider-neutral text-generation request without execution authority."""

    provider_contract_version: Literal["provider-contract-v1"] = PROVIDER_CONTRACT_VERSION
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    provider_kind: ProviderKind
    adapter_id: OpaqueIdentifier
    model_id: OpaqueIdentifier
    input_text: BoundedText
    requested_capabilities: Capabilities
    maximum_output_tokens: OutputTokenLimit
    temperature: Temperature = 0.0
    stop_sequences: StopSequences = Field(default_factory=tuple)
    requested_at: Timestamp

    @model_validator(mode="after")
    def validate_requested_capabilities(self) -> Self:
        """Require unique capabilities and the base generation capability."""

        if len(self.requested_capabilities) != len(set(self.requested_capabilities)):
            raise ValueError("requested provider capabilities must be unique")

        if ProviderCapability.TEXT_GENERATION not in self.requested_capabilities:
            raise ValueError("provider request requires text generation capability")

        if len(self.stop_sequences) != len(set(self.stop_sequences)):
            raise ValueError("provider stop sequences must be unique")

        return self


class ProviderUsage(ContractModel):
    """Normalized token-accounting evidence supplied with a response."""

    input_tokens: TokenCount
    output_tokens: TokenCount
    total_tokens: TokenCount

    @model_validator(mode="after")
    def validate_total(self) -> Self:
        """Require the normalized total to equal its components."""

        if self.total_tokens != self.input_tokens + self.output_tokens:
            raise ValueError("total tokens must equal input tokens plus output tokens")

        return self


class ProviderResponse(VersionedContract):
    """Normalized successful provider response envelope."""

    provider_contract_version: Literal["provider-contract-v1"] = PROVIDER_CONTRACT_VERSION
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    provider_kind: ProviderKind
    adapter_id: OpaqueIdentifier
    model_id: OpaqueIdentifier
    output_text: BoundedText
    finish_reason: ProviderFinishReason
    usage: ProviderUsage
    completed_at: Timestamp


EXPECTED_ERROR_CATEGORIES: dict[ProviderErrorCode, ProviderErrorCategory] = {
    ProviderErrorCode.INVALID_REQUEST: ProviderErrorCategory.REQUEST,
    ProviderErrorCode.AUTHENTICATION_FAILED: ProviderErrorCategory.AUTHENTICATION,
    ProviderErrorCode.ACCESS_DENIED: ProviderErrorCategory.AUTHORIZATION,
    ProviderErrorCode.UNSUPPORTED_CAPABILITY: ProviderErrorCategory.REQUEST,
    ProviderErrorCode.CONTEXT_LIMIT_EXCEEDED: ProviderErrorCategory.REQUEST,
    ProviderErrorCode.RATE_LIMITED: ProviderErrorCategory.CAPACITY,
    ProviderErrorCode.REQUEST_TIMEOUT: ProviderErrorCategory.TIMEOUT,
    ProviderErrorCode.PROVIDER_UNAVAILABLE: ProviderErrorCategory.DEPENDENCY,
    ProviderErrorCode.RESPONSE_INVALID: ProviderErrorCategory.RESPONSE,
    ProviderErrorCode.INTERNAL_ERROR: ProviderErrorCategory.INTERNAL,
}

EXPECTED_ERROR_RETRYABILITY: dict[ProviderErrorCode, bool] = {
    ProviderErrorCode.INVALID_REQUEST: False,
    ProviderErrorCode.AUTHENTICATION_FAILED: False,
    ProviderErrorCode.ACCESS_DENIED: False,
    ProviderErrorCode.UNSUPPORTED_CAPABILITY: False,
    ProviderErrorCode.CONTEXT_LIMIT_EXCEEDED: False,
    ProviderErrorCode.RATE_LIMITED: True,
    ProviderErrorCode.REQUEST_TIMEOUT: True,
    ProviderErrorCode.PROVIDER_UNAVAILABLE: True,
    ProviderErrorCode.RESPONSE_INVALID: False,
    ProviderErrorCode.INTERNAL_ERROR: False,
}


class ProviderError(VersionedContract):
    """Normalized non-sensitive provider failure envelope."""

    provider_contract_version: Literal["provider-contract-v1"] = PROVIDER_CONTRACT_VERSION
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    provider_kind: ProviderKind
    adapter_id: OpaqueIdentifier
    model_id: OpaqueIdentifier
    error_code: ProviderErrorCode
    error_category: ProviderErrorCategory
    safe_message: ShortText
    retryable: bool
    occurred_at: Timestamp

    @model_validator(mode="after")
    def validate_error_invariants(self) -> Self:
        """Enforce deterministic category and retry mappings."""

        if self.error_category is not EXPECTED_ERROR_CATEGORIES[self.error_code]:
            raise ValueError("provider error category does not match its code")

        if self.retryable is not EXPECTED_ERROR_RETRYABILITY[self.error_code]:
            raise ValueError("provider error retryability does not match its code")

        return self
