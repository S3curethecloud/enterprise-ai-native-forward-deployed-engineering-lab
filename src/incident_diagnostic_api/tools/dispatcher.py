"""Fail-closed Phase 7D dispatcher for deterministic local tool mocks."""

from __future__ import annotations

from typing import Final

from incident_diagnostic_api.contracts.common import Timestamp
from incident_diagnostic_api.tools.contracts import (
    ToolError,
    ToolErrorCode,
    ToolRequest,
    ToolResult,
)
from incident_diagnostic_api.tools.mock import (
    build_deterministic_mock_tool_error,
    build_deterministic_mock_tool_result,
)
from incident_diagnostic_api.tools.registry import (
    DEFAULT_TOOL_REGISTRY,
    ToolApprovalRequirement,
    ToolRegistry,
    ToolSideEffect,
)

TOOL_DISPATCHER_VERSION: Final = "7d.1"

type ToolDispatchOutcome = ToolResult | ToolError


def dispatch_deterministic_local_tool_request(
    request: ToolRequest,
    *,
    completed_at: Timestamp,
    registry: ToolRegistry = DEFAULT_TOOL_REGISTRY,
) -> ToolDispatchOutcome:
    """Dispatch only to deterministic local mocks and fail closed otherwise."""

    try:
        definition = registry.get(request.tool_name)
    except KeyError:
        return build_deterministic_mock_tool_error(
            request,
            error_code=ToolErrorCode.TOOL_NOT_REGISTERED,
            safe_message="tool is not registered",
            occurred_at=completed_at,
        )

    if definition.general_shell_access:
        return build_deterministic_mock_tool_error(
            request,
            error_code=ToolErrorCode.ACCESS_DENIED,
            safe_message="general shell access is prohibited",
            occurred_at=completed_at,
        )

    if definition.execution_enabled:
        return build_deterministic_mock_tool_error(
            request,
            error_code=ToolErrorCode.ACCESS_DENIED,
            safe_message="real tool execution is prohibited",
            occurred_at=completed_at,
        )

    if definition.side_effect is not ToolSideEffect.NONE:
        return build_deterministic_mock_tool_error(
            request,
            error_code=ToolErrorCode.APPROVAL_REQUIRED,
            safe_message="side-effecting tool dispatch requires a later approval phase",
            occurred_at=completed_at,
        )

    if definition.approval_requirement is ToolApprovalRequirement.HUMAN_APPROVAL:
        return build_deterministic_mock_tool_error(
            request,
            error_code=ToolErrorCode.APPROVAL_REQUIRED,
            safe_message="human approval workflow is not implemented",
            occurred_at=completed_at,
        )

    return build_deterministic_mock_tool_result(
        request,
        completed_at=completed_at,
    )
