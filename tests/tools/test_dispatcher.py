"""Contract tests for the fail-closed Phase 7D deterministic dispatcher."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from incident_diagnostic_api.tools.contracts import ToolErrorCode, ToolRequest, ToolResult
from incident_diagnostic_api.tools.dispatcher import (
    TOOL_DISPATCHER_VERSION,
    dispatch_deterministic_local_tool_request,
)
from incident_diagnostic_api.tools.registry import (
    ToolName,
    build_default_tool_registry,
)

REQUESTED_AT = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)
COMPLETED_AT = REQUESTED_AT + timedelta(seconds=3)


def build_request(tool_name: ToolName) -> ToolRequest:
    return ToolRequest(
        request_id="request_phase7d_0001",
        trace_id="trace_phase7d_0001",
        tool_name=tool_name,
        arguments={"resource_id": "INC-123"},
        requested_at=REQUESTED_AT,
    )


def test_dispatcher_version_is_explicit() -> None:
    assert TOOL_DISPATCHER_VERSION == "7d.1"


@pytest.mark.parametrize(
    "tool_name",
    [
        ToolName.JIRA_ISSUE_READ,
        ToolName.SERVICENOW_INCIDENT_READ,
        ToolName.KUBERNETES_RESOURCE_READ,
        ToolName.CLOUD_RESOURCE_READ,
        ToolName.DATABASE_QUERY_READ,
    ],
)
def test_read_only_tools_dispatch_to_deterministic_local_mock(
    tool_name: ToolName,
) -> None:
    request = build_request(tool_name)

    outcome = dispatch_deterministic_local_tool_request(
        request,
        completed_at=COMPLETED_AT,
    )

    assert isinstance(outcome, ToolResult)
    assert outcome.request_id == request.request_id
    assert outcome.trace_id == request.trace_id
    assert outcome.tool_name is tool_name
    assert outcome.output["execution_mode"] == "deterministic_local_mock"
    assert outcome.output["real_execution"] is False
    assert outcome.output["network_access"] is False
    assert outcome.output["credential_access"] is False


@pytest.mark.parametrize(
    "tool_name",
    [
        ToolName.JIRA_ISSUE_COMMENT,
        ToolName.SERVICENOW_INCIDENT_UPDATE,
    ],
)
def test_side_effecting_tools_fail_closed_until_later_approval_phase(
    tool_name: ToolName,
) -> None:
    outcome = dispatch_deterministic_local_tool_request(
        build_request(tool_name),
        completed_at=COMPLETED_AT,
    )

    assert not isinstance(outcome, ToolResult)
    assert outcome.error_code is ToolErrorCode.APPROVAL_REQUIRED
    assert outcome.retryable is False


def test_dispatcher_preserves_error_identity_on_fail_closed_path() -> None:
    request = build_request(ToolName.JIRA_ISSUE_COMMENT)

    outcome = dispatch_deterministic_local_tool_request(
        request,
        completed_at=COMPLETED_AT,
    )

    assert not isinstance(outcome, ToolResult)
    assert outcome.request_id == request.request_id
    assert outcome.trace_id == request.trace_id
    assert outcome.tool_name is request.tool_name


def test_dispatcher_rejects_completion_before_request_time() -> None:
    with pytest.raises(ValueError, match="occurred_at"):
        dispatch_deterministic_local_tool_request(
            build_request(ToolName.JIRA_ISSUE_COMMENT),
            completed_at=REQUESTED_AT - timedelta(seconds=1),
        )


def test_dispatcher_uses_registry_metadata_for_every_allowlisted_tool() -> None:
    registry = build_default_tool_registry()

    for definition in registry:
        outcome = dispatch_deterministic_local_tool_request(
            build_request(definition.tool_name),
            completed_at=COMPLETED_AT,
            registry=registry,
        )

        if definition.side_effect.value == "none":
            assert isinstance(outcome, ToolResult)
        else:
            assert not isinstance(outcome, ToolResult)
            assert outcome.error_code is ToolErrorCode.APPROVAL_REQUIRED


def test_dispatcher_module_does_not_import_prohibited_runtime_surfaces() -> None:
    source = Path("src/incident_diagnostic_api/tools/dispatcher.py").read_text()

    prohibited = {
        "requests",
        "httpx",
        "boto3",
        "kubernetes",
        "subprocess",
        "socket",
        "paramiko",
        "servicenow",
        "jira",
        "open(",
        "exec(",
        "eval(",
    }

    assert prohibited.isdisjoint(source.split())
