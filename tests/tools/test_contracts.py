"""Positive, negative, and invariant tests for Phase 7B tool envelopes."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.tools import (
    TOOL_CONTRACT_VERSION,
    TOOL_ENVELOPE_VERSION,
    ToolError,
    ToolErrorCode,
    ToolRequest,
    ToolResult,
)

NOW = datetime(2026, 7, 30, 12, 0, tzinfo=UTC)


def request_payload() -> dict[str, Any]:
    return {
        "contract_version": "1.0",
        "tool_contract_version": "7a.1",
        "tool_envelope_version": "tool-envelope-v1",
        "request_id": "request-701",
        "trace_id": "trace-701",
        "tool_name": "jira.issue.read",
        "arguments": {"issue_id": "INC-701", "include_comments": True},
        "idempotency_key": None,
        "requested_at": NOW,
    }


def result_payload() -> dict[str, Any]:
    return {
        "contract_version": "1.0",
        "tool_contract_version": "7a.1",
        "tool_envelope_version": "tool-envelope-v1",
        "request_id": "request-701",
        "trace_id": "trace-701",
        "tool_name": "jira.issue.read",
        "status": "completed",
        "output": {
            "issue_id": "INC-701",
            "summary": "Synthetic incident for contract testing.",
        },
        "completed_at": NOW,
    }


def error_payload(
    *,
    code: str = "REQUEST_TIMEOUT",
    category: str = "timeout",
    retryable: bool = True,
) -> dict[str, Any]:
    return {
        "contract_version": "1.0",
        "tool_contract_version": "7a.1",
        "tool_envelope_version": "tool-envelope-v1",
        "request_id": "request-701",
        "trace_id": "trace-701",
        "tool_name": "jira.issue.read",
        "error_code": code,
        "error_category": category,
        "safe_message": "The tool request could not be completed.",
        "retryable": retryable,
        "occurred_at": NOW,
    }


def test_versions_are_explicit() -> None:
    assert TOOL_CONTRACT_VERSION == "7a.1"
    assert TOOL_ENVELOPE_VERSION == "tool-envelope-v1"


def test_request_is_accepted_and_frozen() -> None:
    request = ToolRequest.model_validate(request_payload())
    assert request.tool_name.value == "jira.issue.read"
    assert request.arguments["issue_id"] == "INC-701"
    with pytest.raises(ValidationError):
        request.trace_id = "changed"


def test_request_serializes_to_normalized_values() -> None:
    serialized = ToolRequest.model_validate(request_payload()).model_dump(mode="json")
    assert serialized["tool_name"] == "jira.issue.read"
    assert serialized["requested_at"] == NOW.isoformat().replace("+00:00", "Z")


@pytest.mark.parametrize(
    "field",
    ["request_id", "trace_id", "tool_name", "arguments", "requested_at"],
)
def test_missing_required_request_field_is_rejected(field: str) -> None:
    payload = request_payload()
    payload.pop(field)
    with pytest.raises(ValidationError):
        ToolRequest.model_validate(payload)


def test_unknown_request_field_is_rejected() -> None:
    payload = request_payload()
    payload["execute"] = True
    with pytest.raises(ValidationError):
        ToolRequest.model_validate(payload)


def test_unregistered_tool_name_is_rejected() -> None:
    payload = request_payload()
    payload["tool_name"] = "shell.execute"
    with pytest.raises(ValidationError):
        ToolRequest.model_validate(payload)


@pytest.mark.parametrize("argument_name", ["UpperCase", "space key", "_private"])
def test_invalid_argument_name_is_rejected(argument_name: str) -> None:
    payload = request_payload()
    payload["arguments"] = {argument_name: "value"}
    with pytest.raises(ValidationError):
        ToolRequest.model_validate(payload)


def test_more_than_32_arguments_are_rejected() -> None:
    payload = request_payload()
    payload["arguments"] = {f"item_{index}": index for index in range(33)}
    with pytest.raises(ValidationError):
        ToolRequest.model_validate(payload)


def test_excessive_argument_depth_is_rejected() -> None:
    payload = request_payload()
    payload["arguments"] = {"a": {"b": {"c": {"d": {"e": "too-deep"}}}}}
    with pytest.raises(ValidationError, match="JSON depth limit"):
        ToolRequest.model_validate(payload)


def test_excessive_argument_nodes_are_rejected() -> None:
    payload = request_payload()
    payload["arguments"] = {"items": list(range(129))}
    with pytest.raises(ValidationError, match="JSON node limit"):
        ToolRequest.model_validate(payload)


def test_oversized_argument_string_is_rejected() -> None:
    payload = request_payload()
    payload["arguments"] = {"query": "x" * 4_001}
    with pytest.raises(ValidationError, match="oversized string"):
        ToolRequest.model_validate(payload)


def test_non_finite_argument_number_is_rejected() -> None:
    payload = request_payload()
    payload["arguments"] = {"score": float("inf")}
    with pytest.raises(ValidationError, match="non-finite"):
        ToolRequest.model_validate(payload)


def test_naive_request_timestamp_is_rejected() -> None:
    payload = request_payload()
    payload["requested_at"] = datetime(2026, 7, 30, 12, 0)
    with pytest.raises(ValidationError):
        ToolRequest.model_validate(payload)


def test_invalid_idempotency_key_is_rejected() -> None:
    payload = request_payload()
    payload["idempotency_key"] = "contains spaces"
    with pytest.raises(ValidationError):
        ToolRequest.model_validate(payload)


def test_result_is_accepted_and_frozen() -> None:
    result = ToolResult.model_validate(result_payload())
    assert result.status.value == "completed"
    assert result.output["issue_id"] == "INC-701"
    with pytest.raises(ValidationError):
        result.output = {}


def test_result_rejects_unknown_status() -> None:
    payload = result_payload()
    payload["status"] = "executing"
    with pytest.raises(ValidationError):
        ToolResult.model_validate(payload)


def test_result_rejects_unregistered_tool() -> None:
    payload = result_payload()
    payload["tool_name"] = "shell.execute"
    with pytest.raises(ValidationError):
        ToolResult.model_validate(payload)


def test_result_rejects_oversized_output() -> None:
    payload = result_payload()
    payload["output"] = {"content": "x" * 4_001}
    with pytest.raises(ValidationError, match="oversized string"):
        ToolResult.model_validate(payload)


def test_result_rejects_unknown_field() -> None:
    payload = result_payload()
    payload["raw_credentials"] = "must-not-enter-contract"
    with pytest.raises(ValidationError):
        ToolResult.model_validate(payload)


ERROR_CASES = [
    ("INVALID_REQUEST", "request", False),
    ("TOOL_NOT_REGISTERED", "request", False),
    ("ACCESS_DENIED", "authorization", False),
    ("APPROVAL_REQUIRED", "approval", False),
    ("REQUEST_TIMEOUT", "timeout", True),
    ("TOOL_UNAVAILABLE", "dependency", True),
    ("RESULT_INVALID", "response", False),
    ("INTERNAL_ERROR", "internal", False),
]


@pytest.mark.parametrize(("code", "category", "retryable"), ERROR_CASES)
def test_each_error_mapping_is_accepted(
    code: str,
    category: str,
    retryable: bool,
) -> None:
    error = ToolError.model_validate(
        error_payload(code=code, category=category, retryable=retryable)
    )
    assert error.error_code is ToolErrorCode(code)
    assert error.retryable is retryable


def test_error_category_mismatch_is_rejected() -> None:
    with pytest.raises(
        ValidationError,
        match="tool error category does not match its code",
    ):
        ToolError.model_validate(error_payload(category="internal"))


def test_error_retryability_mismatch_is_rejected() -> None:
    with pytest.raises(
        ValidationError,
        match="tool error retryability does not match its code",
    ):
        ToolError.model_validate(error_payload(retryable=False))


def test_error_rejects_sensitive_unknown_field() -> None:
    payload = error_payload()
    payload["raw_response"] = "sensitive dependency detail"
    with pytest.raises(ValidationError):
        ToolError.model_validate(payload)


def test_error_safe_message_is_bounded() -> None:
    payload = error_payload()
    payload["safe_message"] = "x" * 501
    with pytest.raises(ValidationError):
        ToolError.model_validate(payload)


def test_wrong_envelope_version_is_rejected() -> None:
    payload = request_payload()
    payload["tool_envelope_version"] = "tool-envelope-v2"
    with pytest.raises(ValidationError):
        ToolRequest.model_validate(payload)


def test_wrong_tool_contract_version_is_rejected() -> None:
    payload = request_payload()
    payload["tool_contract_version"] = "7b.1"
    with pytest.raises(ValidationError):
        ToolRequest.model_validate(payload)


def test_contract_module_exposes_no_invocation_surface() -> None:
    prohibited = {"invoke", "execute", "dispatch", "call_tool"}
    assert prohibited.isdisjoint(set(dir(ToolRequest)))
