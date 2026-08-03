"""Deterministic local Phase 7C tool mocks without real execution authority."""

from __future__ import annotations

from typing import Final

from pydantic import JsonValue

from incident_diagnostic_api.contracts.common import ShortText, Timestamp
from incident_diagnostic_api.tools.contracts import (
    EXPECTED_TOOL_ERROR_CATEGORIES,
    EXPECTED_TOOL_ERROR_RETRYABILITY,
    ToolError,
    ToolErrorCode,
    ToolOutput,
    ToolRequest,
    ToolResult,
)

MOCK_TOOL_RUNTIME_VERSION: Final = "7c.1"


def build_deterministic_mock_tool_result(
    request: ToolRequest,
    *,
    completed_at: Timestamp,
) -> ToolResult:
    """Return a deterministic local result envelope without contacting a system."""

    if completed_at < request.requested_at:
        raise ValueError("completed_at must not precede requested_at")

    return ToolResult(
        request_id=request.request_id,
        trace_id=request.trace_id,
        tool_name=request.tool_name,
        output=_build_mock_output(request),
        completed_at=completed_at,
    )


def build_deterministic_mock_tool_error(
    request: ToolRequest,
    *,
    error_code: ToolErrorCode,
    safe_message: ShortText,
    occurred_at: Timestamp,
) -> ToolError:
    """Return a normalized deterministic local error envelope."""

    if occurred_at < request.requested_at:
        raise ValueError("occurred_at must not precede requested_at")

    return ToolError(
        request_id=request.request_id,
        trace_id=request.trace_id,
        tool_name=request.tool_name,
        error_code=error_code,
        error_category=EXPECTED_TOOL_ERROR_CATEGORIES[error_code],
        safe_message=safe_message,
        retryable=EXPECTED_TOOL_ERROR_RETRYABILITY[error_code],
        occurred_at=occurred_at,
    )


def _build_mock_output(request: ToolRequest) -> ToolOutput:
    argument_names: list[JsonValue] = [str(name) for name in sorted(request.arguments)]

    output: dict[str, JsonValue] = {
        "mock_runtime_version": MOCK_TOOL_RUNTIME_VERSION,
        "tool_name": request.tool_name.value,
        "execution_mode": "deterministic_local_mock",
        "real_execution": False,
        "network_access": False,
        "credential_access": False,
        "argument_count": len(argument_names),
        "argument_names": argument_names,
    }

    if request.idempotency_key is not None:
        output["idempotency_key"] = request.idempotency_key

    return output
