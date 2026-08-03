"""Contract tests for deterministic local Phase 7C tool mocks."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from incident_diagnostic_api.tools.contracts import (
    EXPECTED_TOOL_ERROR_CATEGORIES,
    EXPECTED_TOOL_ERROR_RETRYABILITY,
    ToolErrorCode,
    ToolRequest,
    ToolResultStatus,
)
from incident_diagnostic_api.tools.mock import (
    MOCK_TOOL_RUNTIME_VERSION,
    build_deterministic_mock_tool_error,
    build_deterministic_mock_tool_result,
)
from incident_diagnostic_api.tools.registry import ToolName

REQUESTED_AT = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)
COMPLETED_AT = REQUESTED_AT + timedelta(seconds=2)


def build_request(
    *,
    tool_name: ToolName = ToolName.JIRA_ISSUE_READ,
) -> ToolRequest:
    return ToolRequest(
        request_id="request_phase7c_0001",
        trace_id="trace_phase7c_0001",
        tool_name=tool_name,
        arguments={"issue_key": "INC-123", "include_comments": False},
        idempotency_key="idem_phase7c_0001",
        requested_at=REQUESTED_AT,
    )


@pytest.mark.parametrize("tool_name", list(ToolName))
def test_mock_result_preserves_request_identity(tool_name: ToolName) -> None:
    request = build_request(tool_name=tool_name)

    result = build_deterministic_mock_tool_result(
        request,
        completed_at=COMPLETED_AT,
    )

    assert result.request_id == request.request_id
    assert result.trace_id == request.trace_id
    assert result.tool_name is tool_name
    assert result.status is ToolResultStatus.COMPLETED
    assert result.completed_at == COMPLETED_AT


def test_mock_result_is_deterministic() -> None:
    request = build_request()

    first = build_deterministic_mock_tool_result(
        request,
        completed_at=COMPLETED_AT,
    )
    second = build_deterministic_mock_tool_result(
        request,
        completed_at=COMPLETED_AT,
    )

    assert first == second


def test_mock_result_declares_fail_closed_runtime_boundary() -> None:
    result = build_deterministic_mock_tool_result(
        build_request(),
        completed_at=COMPLETED_AT,
    )

    assert result.output["mock_runtime_version"] == MOCK_TOOL_RUNTIME_VERSION
    assert result.output["execution_mode"] == "deterministic_local_mock"
    assert result.output["real_execution"] is False
    assert result.output["network_access"] is False
    assert result.output["credential_access"] is False
    assert result.output["argument_names"] == ["include_comments", "issue_key"]


def test_mock_result_rejects_completion_before_request_time() -> None:
    with pytest.raises(ValueError, match="completed_at"):
        build_deterministic_mock_tool_result(
            build_request(),
            completed_at=REQUESTED_AT - timedelta(seconds=1),
        )


@pytest.mark.parametrize("error_code", list(ToolErrorCode))
def test_mock_error_uses_contract_error_mappings(error_code: ToolErrorCode) -> None:
    request = build_request()

    error = build_deterministic_mock_tool_error(
        request,
        error_code=error_code,
        safe_message="safe deterministic mock failure",
        occurred_at=COMPLETED_AT,
    )

    assert error.request_id == request.request_id
    assert error.trace_id == request.trace_id
    assert error.tool_name is request.tool_name
    assert error.error_category is EXPECTED_TOOL_ERROR_CATEGORIES[error_code]
    assert error.retryable is EXPECTED_TOOL_ERROR_RETRYABILITY[error_code]


def test_mock_error_rejects_occurrence_before_request_time() -> None:
    with pytest.raises(ValueError, match="occurred_at"):
        build_deterministic_mock_tool_error(
            build_request(),
            error_code=ToolErrorCode.REQUEST_TIMEOUT,
            safe_message="safe deterministic mock failure",
            occurred_at=REQUESTED_AT - timedelta(seconds=1),
        )


def test_mock_module_does_not_import_prohibited_integration_surfaces() -> None:
    source = Path("src/incident_diagnostic_api/tools/mock.py").read_text()

    prohibited = {
        "requests",
        "httpx",
        "boto3",
        "kubernetes",
        "subprocess",
        "socket",
        "paramiko",
        "jira",
        "servicenow",
        "open(",
    }

    assert prohibited.isdisjoint(source.split())
