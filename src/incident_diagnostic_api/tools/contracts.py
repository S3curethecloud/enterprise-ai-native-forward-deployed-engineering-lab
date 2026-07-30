"""Typed Phase 7B tool envelopes without invocation or execution authority."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any, Final, Literal, Self

from pydantic import Field, JsonValue, StringConstraints, field_validator, model_validator

from incident_diagnostic_api.contracts.common import (
    OpaqueIdentifier,
    ShortText,
    Timestamp,
    VersionedContract,
)
from incident_diagnostic_api.tools.registry import TOOL_CONTRACT_VERSION, ToolName

TOOL_ENVELOPE_VERSION: Final[Literal["tool-envelope-v1"]] = "tool-envelope-v1"

ToolArgumentName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=80,
        pattern=r"^[a-z][a-z0-9_]*$",
    ),
]
type ToolArguments = Annotated[
    dict[ToolArgumentName, JsonValue],
    Field(max_length=32),
]
type ToolOutput = Annotated[
    dict[ToolArgumentName, JsonValue],
    Field(max_length=32),
]

MAX_JSON_DEPTH: Final = 4
MAX_JSON_NODES: Final = 128
MAX_JSON_STRING_LENGTH: Final = 4_000


class ToolResultStatus(StrEnum):
    """Normalized successful tool-result disposition."""

    COMPLETED = "completed"


class ToolErrorCategory(StrEnum):
    """Bounded categories for normalized tool failures."""

    REQUEST = "request"
    AUTHORIZATION = "authorization"
    APPROVAL = "approval"
    TIMEOUT = "timeout"
    DEPENDENCY = "dependency"
    RESPONSE = "response"
    INTERNAL = "internal"


class ToolErrorCode(StrEnum):
    """Tool-independent, non-sensitive error codes."""

    INVALID_REQUEST = "INVALID_REQUEST"
    TOOL_NOT_REGISTERED = "TOOL_NOT_REGISTERED"
    ACCESS_DENIED = "ACCESS_DENIED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    REQUEST_TIMEOUT = "REQUEST_TIMEOUT"
    TOOL_UNAVAILABLE = "TOOL_UNAVAILABLE"
    RESULT_INVALID = "RESULT_INVALID"
    INTERNAL_ERROR = "INTERNAL_ERROR"


EXPECTED_TOOL_ERROR_CATEGORIES: Final[dict[ToolErrorCode, ToolErrorCategory]] = {
    ToolErrorCode.INVALID_REQUEST: ToolErrorCategory.REQUEST,
    ToolErrorCode.TOOL_NOT_REGISTERED: ToolErrorCategory.REQUEST,
    ToolErrorCode.ACCESS_DENIED: ToolErrorCategory.AUTHORIZATION,
    ToolErrorCode.APPROVAL_REQUIRED: ToolErrorCategory.APPROVAL,
    ToolErrorCode.REQUEST_TIMEOUT: ToolErrorCategory.TIMEOUT,
    ToolErrorCode.TOOL_UNAVAILABLE: ToolErrorCategory.DEPENDENCY,
    ToolErrorCode.RESULT_INVALID: ToolErrorCategory.RESPONSE,
    ToolErrorCode.INTERNAL_ERROR: ToolErrorCategory.INTERNAL,
}

EXPECTED_TOOL_ERROR_RETRYABILITY: Final[dict[ToolErrorCode, bool]] = {
    ToolErrorCode.INVALID_REQUEST: False,
    ToolErrorCode.TOOL_NOT_REGISTERED: False,
    ToolErrorCode.ACCESS_DENIED: False,
    ToolErrorCode.APPROVAL_REQUIRED: False,
    ToolErrorCode.REQUEST_TIMEOUT: True,
    ToolErrorCode.TOOL_UNAVAILABLE: True,
    ToolErrorCode.RESULT_INVALID: False,
    ToolErrorCode.INTERNAL_ERROR: False,
}


def _validate_bounded_json(value: dict[str, JsonValue], *, field_name: str) -> None:
    """Reject deeply nested, oversized, or non-finite JSON payloads."""

    nodes = 0

    def visit(item: Any, depth: int) -> None:
        nonlocal nodes
        nodes += 1

        if nodes > MAX_JSON_NODES:
            raise ValueError(f"{field_name} exceeds the JSON node limit")
        if depth > MAX_JSON_DEPTH:
            raise ValueError(f"{field_name} exceeds the JSON depth limit")
        if isinstance(item, str) and len(item) > MAX_JSON_STRING_LENGTH:
            raise ValueError(f"{field_name} contains an oversized string")
        if isinstance(item, float) and (item != item or item in (float("inf"), float("-inf"))):
            raise ValueError(f"{field_name} contains a non-finite number")
        if isinstance(item, dict):
            for key, nested in item.items():
                if not isinstance(key, str):
                    raise ValueError(f"{field_name} keys must be strings")
                visit(nested, depth + 1)
        elif isinstance(item, list):
            for nested in item:
                visit(nested, depth + 1)

    visit(value, 0)


class ToolRequest(VersionedContract):
    """Validated tool-request envelope without invocation authority."""

    tool_contract_version: Literal["7a.1"] = TOOL_CONTRACT_VERSION
    tool_envelope_version: Literal["tool-envelope-v1"] = TOOL_ENVELOPE_VERSION
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    tool_name: ToolName
    arguments: ToolArguments
    idempotency_key: OpaqueIdentifier | None = None
    requested_at: Timestamp

    @field_validator("arguments")
    @classmethod
    def validate_arguments(
        cls,
        value: dict[str, JsonValue],
    ) -> dict[str, JsonValue]:
        """Apply deterministic bounds without interpreting tool semantics."""

        _validate_bounded_json(value, field_name="tool arguments")
        return value


class ToolResult(VersionedContract):
    """Normalized successful tool-result envelope without an executor."""

    tool_contract_version: Literal["7a.1"] = TOOL_CONTRACT_VERSION
    tool_envelope_version: Literal["tool-envelope-v1"] = TOOL_ENVELOPE_VERSION
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    tool_name: ToolName
    status: Literal[ToolResultStatus.COMPLETED] = ToolResultStatus.COMPLETED
    output: ToolOutput
    completed_at: Timestamp

    @field_validator("output")
    @classmethod
    def validate_output(
        cls,
        value: dict[str, JsonValue],
    ) -> dict[str, JsonValue]:
        """Treat future tool output as bounded, untrusted structured data."""

        _validate_bounded_json(value, field_name="tool output")
        return value


class ToolError(VersionedContract):
    """Normalized non-sensitive tool-failure envelope."""

    tool_contract_version: Literal["7a.1"] = TOOL_CONTRACT_VERSION
    tool_envelope_version: Literal["tool-envelope-v1"] = TOOL_ENVELOPE_VERSION
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    tool_name: ToolName
    error_code: ToolErrorCode
    error_category: ToolErrorCategory
    safe_message: ShortText
    retryable: bool
    occurred_at: Timestamp

    @model_validator(mode="after")
    def validate_error_invariants(self) -> Self:
        """Enforce deterministic category and retry mappings."""

        if self.error_category is not EXPECTED_TOOL_ERROR_CATEGORIES[self.error_code]:
            raise ValueError("tool error category does not match its code")
        if self.retryable is not EXPECTED_TOOL_ERROR_RETRYABILITY[self.error_code]:
            raise ValueError("tool error retryability does not match its code")
        return self
