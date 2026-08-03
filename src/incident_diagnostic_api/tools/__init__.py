"""Public Phase 7 tool contracts, mocks, and fail-closed dispatcher."""

from incident_diagnostic_api.tools.contracts import (
    EXPECTED_TOOL_ERROR_CATEGORIES,
    EXPECTED_TOOL_ERROR_RETRYABILITY,
    TOOL_ENVELOPE_VERSION,
    ToolError,
    ToolErrorCategory,
    ToolErrorCode,
    ToolRequest,
    ToolResult,
    ToolResultStatus,
)
from incident_diagnostic_api.tools.dispatcher import (
    TOOL_DISPATCHER_VERSION,
    ToolDispatchOutcome,
    dispatch_deterministic_local_tool_request,
)
from incident_diagnostic_api.tools.mock import (
    MOCK_TOOL_RUNTIME_VERSION,
    build_deterministic_mock_tool_error,
    build_deterministic_mock_tool_result,
)
from incident_diagnostic_api.tools.registry import (
    DEFAULT_TOOL_REGISTRY,
    TOOL_CONTRACT_VERSION,
    TOOL_REGISTRY_VERSION,
    ToolApprovalRequirement,
    ToolCapability,
    ToolDefinition,
    ToolIdempotencyRequirement,
    ToolName,
    ToolRegistry,
    ToolRiskTier,
    ToolSideEffect,
    build_default_tool_registry,
)

__all__ = [
    "DEFAULT_TOOL_REGISTRY",
    "EXPECTED_TOOL_ERROR_CATEGORIES",
    "EXPECTED_TOOL_ERROR_RETRYABILITY",
    "MOCK_TOOL_RUNTIME_VERSION",
    "TOOL_CONTRACT_VERSION",
    "TOOL_DISPATCHER_VERSION",
    "TOOL_ENVELOPE_VERSION",
    "TOOL_REGISTRY_VERSION",
    "ToolApprovalRequirement",
    "ToolCapability",
    "ToolDefinition",
    "ToolDispatchOutcome",
    "ToolError",
    "ToolErrorCategory",
    "ToolErrorCode",
    "ToolIdempotencyRequirement",
    "ToolName",
    "ToolRegistry",
    "ToolRequest",
    "ToolResult",
    "ToolResultStatus",
    "ToolRiskTier",
    "ToolSideEffect",
    "build_default_tool_registry",
    "build_deterministic_mock_tool_error",
    "build_deterministic_mock_tool_result",
    "dispatch_deterministic_local_tool_request",
]
