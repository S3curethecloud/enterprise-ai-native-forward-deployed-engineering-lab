"""Contract tests for Phase 7E deterministic tool-outcome consistency evidence."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from pydantic import JsonValue, ValidationError

from incident_diagnostic_api.tools.contracts import ToolErrorCode, ToolRequest, ToolResult
from incident_diagnostic_api.tools.dispatcher import ToolDispatchOutcome
from incident_diagnostic_api.tools.evidence import (
    TOOL_OUTCOME_EVIDENCE_VERSION,
    ToolOutcomeConsistencyStatus,
    ToolOutcomeEvidence,
    ToolOutcomeEvidenceError,
    ToolOutcomeEvidenceErrorCode,
    ToolOutcomeKind,
    build_deterministic_tool_outcome_evidence,
)
from incident_diagnostic_api.tools.mock import (
    build_deterministic_mock_tool_error,
    build_deterministic_mock_tool_result,
)
from incident_diagnostic_api.tools.registry import (
    ToolName,
    ToolRegistry,
    build_default_tool_registry,
)

REQUESTED_AT = datetime(2026, 9, 11, 12, 0, tzinfo=UTC)
OUTCOME_AT = REQUESTED_AT + timedelta(seconds=3)

READ_ONLY_TOOLS = (
    ToolName.JIRA_ISSUE_READ,
    ToolName.SERVICENOW_INCIDENT_READ,
    ToolName.KUBERNETES_RESOURCE_READ,
    ToolName.CLOUD_RESOURCE_READ,
    ToolName.DATABASE_QUERY_READ,
)
SIDE_EFFECTING_TOOLS = (
    ToolName.JIRA_ISSUE_COMMENT,
    ToolName.SERVICENOW_INCIDENT_UPDATE,
)
NON_APPROVAL_ERROR_CODES = tuple(
    code for code in ToolErrorCode if code is not ToolErrorCode.APPROVAL_REQUIRED
)


def build_request(
    tool_name: ToolName,
    *,
    idempotency_key: str | None = "idempotency_phase7e_0001",
) -> ToolRequest:
    return ToolRequest(
        request_id="request_phase7e_0001",
        trace_id="trace_phase7e_0001",
        tool_name=tool_name,
        arguments={
            "resource_id": "INC-123",
            "tenant_id": "TENANT-1",
        },
        idempotency_key=idempotency_key,
        requested_at=REQUESTED_AT,
    )


def assert_evidence_error(
    expected_code: ToolOutcomeEvidenceErrorCode,
    request: ToolRequest,
    outcome: ToolDispatchOutcome,
    *,
    registry: ToolRegistry | None = None,
) -> ToolOutcomeEvidenceError:
    with pytest.raises(ToolOutcomeEvidenceError) as captured:
        if registry is None:
            build_deterministic_tool_outcome_evidence(request, outcome)
        else:
            build_deterministic_tool_outcome_evidence(
                request,
                outcome,
                registry=registry,
            )
    assert captured.value.code is expected_code
    return captured.value


def test_tool_outcome_evidence_version_is_explicit() -> None:
    assert TOOL_OUTCOME_EVIDENCE_VERSION == "7e.1"


@pytest.mark.parametrize("tool_name", READ_ONLY_TOOLS)
def test_every_read_only_tool_accepts_only_exact_phase7c_result(
    tool_name: ToolName,
) -> None:
    request = build_request(tool_name)
    result = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)

    evidence = build_deterministic_tool_outcome_evidence(request, result)

    assert evidence.outcome_kind is ToolOutcomeKind.RESULT
    assert evidence.consistency_status is ToolOutcomeConsistencyStatus.CONSISTENT
    assert evidence.result_status is not None
    assert evidence.error_code is None
    assert evidence.error_category is None
    assert evidence.retryable is None
    assert evidence.idempotency_key_present is True
    assert evidence.argument_names == ("resource_id", "tenant_id")
    assert evidence.output_names == (
        "argument_count",
        "argument_names",
        "credential_access",
        "execution_mode",
        "idempotency_key",
        "mock_runtime_version",
        "network_access",
        "real_execution",
        "tool_name",
    )
    assert evidence.evaluated_dispatch_semantics_version == "7d.1"


@pytest.mark.parametrize("tool_name", SIDE_EFFECTING_TOOLS)
def test_every_side_effecting_tool_accepts_approval_required_control_error(
    tool_name: ToolName,
) -> None:
    request = build_request(tool_name)
    error = build_deterministic_mock_tool_error(
        request,
        error_code=ToolErrorCode.APPROVAL_REQUIRED,
        safe_message="approval is required",
        occurred_at=OUTCOME_AT,
    )

    evidence = build_deterministic_tool_outcome_evidence(request, error)

    assert evidence.outcome_kind is ToolOutcomeKind.ERROR
    assert evidence.result_status is None
    assert evidence.error_code is ToolErrorCode.APPROVAL_REQUIRED
    assert evidence.error_category is not None
    assert evidence.retryable is False
    assert evidence.output_names == ()


@pytest.mark.parametrize("tool_name", READ_ONLY_TOOLS)
@pytest.mark.parametrize("error_code", tuple(ToolErrorCode))
def test_read_only_tools_reject_every_typed_error_code(
    tool_name: ToolName,
    error_code: ToolErrorCode,
) -> None:
    request = build_request(tool_name)
    error = build_deterministic_mock_tool_error(
        request,
        error_code=error_code,
        safe_message="typed error does not establish Phase 7D admissibility",
        occurred_at=OUTCOME_AT,
    )

    assert_evidence_error(
        ToolOutcomeEvidenceErrorCode.REGISTRY_OUTCOME_CONTRADICTION,
        request,
        error,
    )


@pytest.mark.parametrize("tool_name", SIDE_EFFECTING_TOOLS)
@pytest.mark.parametrize("error_code", NON_APPROVAL_ERROR_CODES)
def test_side_effecting_tools_reject_every_nonapproval_error_code(
    tool_name: ToolName,
    error_code: ToolErrorCode,
) -> None:
    request = build_request(tool_name)
    error = build_deterministic_mock_tool_error(
        request,
        error_code=error_code,
        safe_message="typed error does not establish Phase 7D admissibility",
        occurred_at=OUTCOME_AT,
    )

    assert_evidence_error(
        ToolOutcomeEvidenceErrorCode.REGISTRY_OUTCOME_CONTRADICTION,
        request,
        error,
    )


@pytest.mark.parametrize("tool_name", SIDE_EFFECTING_TOOLS)
def test_side_effecting_tools_reject_typed_results(tool_name: ToolName) -> None:
    request = build_request(tool_name)
    result = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)

    assert_evidence_error(
        ToolOutcomeEvidenceErrorCode.REGISTRY_OUTCOME_CONTRADICTION,
        request,
        result,
    )


def test_registry_version_is_neither_evidence_nor_evaluation_input() -> None:
    request = build_request(ToolName.JIRA_ISSUE_READ)
    result = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)
    base = build_default_tool_registry()
    registry_a = ToolRegistry(version="registry-version-a", tools=base.tools)
    registry_b = ToolRegistry(
        version="free-form-secret-looking-value-that-must-not-be-copied",
        tools=base.tools,
    )

    evidence_a = build_deterministic_tool_outcome_evidence(
        request,
        result,
        registry=registry_a,
    )
    evidence_b = build_deterministic_tool_outcome_evidence(
        request,
        result,
        registry=registry_b,
    )

    assert evidence_a == evidence_b
    serialized_keys = evidence_a.model_dump().keys()
    assert all("registry_version" not in key for key in serialized_keys)


def test_registry_version_is_not_interpolated_into_controlled_errors() -> None:
    request = build_request(ToolName.JIRA_ISSUE_COMMENT)
    invalid_for_side_effect = build_deterministic_mock_tool_result(
        request,
        completed_at=OUTCOME_AT,
    )
    base = build_default_tool_registry()
    secret_like_version = "secret-like-registry-version-value"
    registry = ToolRegistry(version=secret_like_version, tools=base.tools)

    error = assert_evidence_error(
        ToolOutcomeEvidenceErrorCode.REGISTRY_OUTCOME_CONTRADICTION,
        request,
        invalid_for_side_effect,
        registry=registry,
    )

    assert secret_like_version not in str(error)


@pytest.mark.parametrize(
    "field,value",
    [
        ("request_id", "different_request"),
        ("trace_id", "different_trace"),
        ("tool_name", ToolName.CLOUD_RESOURCE_READ),
    ],
)
def test_identity_mismatch_fails_closed(field: str, value: object) -> None:
    request = build_request(ToolName.JIRA_ISSUE_READ)
    result = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)
    mismatched = result.model_copy(update={field: value})

    assert_evidence_error(
        ToolOutcomeEvidenceErrorCode.IDENTITY_MISMATCH,
        request,
        mismatched,
    )


def test_tool_contract_version_mismatch_is_defense_in_depth() -> None:
    request = build_request(ToolName.JIRA_ISSUE_READ)
    result = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)
    bypassed = result.model_copy(update={"tool_contract_version": "future"})

    assert_evidence_error(
        ToolOutcomeEvidenceErrorCode.VERSION_MISMATCH,
        request,
        bypassed,
    )


def test_tool_envelope_version_mismatch_is_defense_in_depth() -> None:
    request = build_request(ToolName.JIRA_ISSUE_READ)
    result = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)
    bypassed = result.model_copy(update={"tool_envelope_version": "future"})

    assert_evidence_error(
        ToolOutcomeEvidenceErrorCode.VERSION_MISMATCH,
        request,
        bypassed,
    )


def test_temporal_inversion_fails_closed_before_result_comparison() -> None:
    request = build_request(ToolName.JIRA_ISSUE_READ)
    result = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)
    bypassed = result.model_copy(update={"completed_at": REQUESTED_AT - timedelta(seconds=1)})

    assert_evidence_error(
        ToolOutcomeEvidenceErrorCode.TEMPORAL_INVERSION,
        request,
        bypassed,
    )


def mutated_result_output(case: str) -> tuple[ToolRequest, dict[str, JsonValue]]:
    request = build_request(ToolName.JIRA_ISSUE_READ)
    expected = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)
    output = dict(expected.output)

    if case == "mock_runtime_version":
        output["mock_runtime_version"] = "wrong"
    elif case == "tool_name":
        output["tool_name"] = "wrong.tool"
    elif case == "execution_mode":
        output["execution_mode"] = "wrong_mode"
    elif case == "real_execution":
        output["real_execution"] = True
    elif case == "network_access":
        output["network_access"] = True
    elif case == "credential_access":
        output["credential_access"] = True
    elif case == "argument_count":
        output["argument_count"] = 999
    elif case == "argument_names":
        wrong_names: list[JsonValue] = ["different_argument"]
        output["argument_names"] = wrong_names
    elif case == "idempotency_key":
        output["idempotency_key"] = "different_key"
    elif case == "missing_idempotency_key":
        output.pop("idempotency_key")
    elif case == "extra_output_key":
        output["unexpected_field"] = "unexpected"
    elif case == "missing_output_key":
        output.pop("execution_mode")
    else:
        raise AssertionError(f"unsupported test mutation: {case}")

    return request, output


@pytest.mark.parametrize(
    "case",
    [
        "mock_runtime_version",
        "tool_name",
        "execution_mode",
        "real_execution",
        "network_access",
        "credential_access",
        "argument_count",
        "argument_names",
        "idempotency_key",
        "missing_idempotency_key",
        "extra_output_key",
        "missing_output_key",
    ],
)
def test_exact_result_equality_rejects_every_control_mutation(case: str) -> None:
    request, output = mutated_result_output(case)
    fabricated = ToolResult(
        request_id=request.request_id,
        trace_id=request.trace_id,
        tool_name=request.tool_name,
        output=output,
        completed_at=OUTCOME_AT,
    )

    assert_evidence_error(
        ToolOutcomeEvidenceErrorCode.OUTCOME_SHAPE_CONTRADICTION,
        request,
        fabricated,
    )


def test_exact_result_equality_rejects_unexpected_idempotency_key() -> None:
    request = build_request(ToolName.JIRA_ISSUE_READ, idempotency_key=None)
    expected = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)
    output = dict(expected.output)
    output["idempotency_key"] = "unexpected_key"
    fabricated = ToolResult(
        request_id=request.request_id,
        trace_id=request.trace_id,
        tool_name=request.tool_name,
        output=output,
        completed_at=OUTCOME_AT,
    )

    assert_evidence_error(
        ToolOutcomeEvidenceErrorCode.OUTCOME_SHAPE_CONTRADICTION,
        request,
        fabricated,
    )


def test_safe_message_is_outside_consistency_claim_and_evidence() -> None:
    request = build_request(ToolName.JIRA_ISSUE_COMMENT)
    first = build_deterministic_mock_tool_error(
        request,
        error_code=ToolErrorCode.APPROVAL_REQUIRED,
        safe_message="first presentation-safe message",
        occurred_at=OUTCOME_AT,
    )
    second = build_deterministic_mock_tool_error(
        request,
        error_code=ToolErrorCode.APPROVAL_REQUIRED,
        safe_message="second presentation-safe message",
        occurred_at=OUTCOME_AT,
    )

    first_evidence = build_deterministic_tool_outcome_evidence(request, first)
    second_evidence = build_deterministic_tool_outcome_evidence(request, second)

    assert first_evidence == second_evidence
    assert "safe_message" not in first_evidence.model_dump()


def test_safe_message_is_not_interpolated_into_controlled_error() -> None:
    request = build_request(ToolName.JIRA_ISSUE_READ)
    sensitive_marker = "presentation-text-marker"
    error = build_deterministic_mock_tool_error(
        request,
        error_code=ToolErrorCode.INTERNAL_ERROR,
        safe_message=sensitive_marker,
        occurred_at=OUTCOME_AT,
    )

    controlled = assert_evidence_error(
        ToolOutcomeEvidenceErrorCode.REGISTRY_OUTCOME_CONTRADICTION,
        request,
        error,
    )

    assert sensitive_marker not in str(controlled)


def test_direct_contract_rejects_unknown_fields_and_wrong_version() -> None:
    request = build_request(ToolName.JIRA_ISSUE_READ)
    result = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)
    evidence = build_deterministic_tool_outcome_evidence(request, result)

    unknown_payload: dict[str, Any] = evidence.model_dump()
    unknown_payload["unexpected"] = True
    with pytest.raises(ValidationError):
        ToolOutcomeEvidence.model_validate(unknown_payload)

    version_payload: dict[str, Any] = evidence.model_dump()
    version_payload["tool_outcome_evidence_version"] = "7e.2"
    with pytest.raises(ValidationError):
        ToolOutcomeEvidence.model_validate(version_payload)

    assert evidence.model_config["frozen"] is True


def test_direct_contract_rejects_incompatible_result_error_shape() -> None:
    request = build_request(ToolName.JIRA_ISSUE_READ)
    result = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)
    evidence = build_deterministic_tool_outcome_evidence(request, result)
    payload: dict[str, Any] = evidence.model_dump()
    payload["error_code"] = ToolErrorCode.APPROVAL_REQUIRED

    with pytest.raises(ValidationError, match="result evidence cannot contain error metadata"):
        ToolOutcomeEvidence.model_validate(payload)


def test_direct_contract_rejects_name_cardinality_expansion() -> None:
    request = build_request(ToolName.JIRA_ISSUE_READ)
    result = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)
    evidence = build_deterministic_tool_outcome_evidence(request, result)
    payload: dict[str, Any] = evidence.model_dump()
    payload["argument_names"] = tuple(f"a{index}" for index in range(33))

    with pytest.raises(ValidationError):
        ToolOutcomeEvidence.model_validate(payload)


def test_direct_contract_rejects_unsorted_or_duplicate_names() -> None:
    request = build_request(ToolName.JIRA_ISSUE_READ)
    result = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)
    evidence = build_deterministic_tool_outcome_evidence(request, result)
    payload: dict[str, Any] = evidence.model_dump()
    payload["argument_names"] = ("tenant_id", "resource_id")

    with pytest.raises(ValidationError, match="argument_names must be unique and sorted"):
        ToolOutcomeEvidence.model_validate(payload)


def test_direct_contract_rejects_result_output_name_drift() -> None:
    request = build_request(ToolName.JIRA_ISSUE_READ)
    result = build_deterministic_mock_tool_result(request, completed_at=OUTCOME_AT)
    evidence = build_deterministic_tool_outcome_evidence(request, result)
    payload: dict[str, Any] = evidence.model_dump()
    payload["output_names"] = ()

    with pytest.raises(ValidationError, match="output_names do not match"):
        ToolOutcomeEvidence.model_validate(payload)


def test_evidence_module_does_not_call_dispatcher_or_import_prohibited_surfaces() -> None:
    source = Path("src/incident_diagnostic_api/tools/evidence.py").read_text()

    assert "dispatch_deterministic_local_tool_request" not in source
    assert "registry.version" not in source

    prohibited = (
        "import requests",
        "import httpx",
        "import boto3",
        "import kubernetes",
        "import subprocess",
        "import socket",
        "import paramiko",
        "import jira",
        "import servicenow",
        "open(",
        "exec(",
        "eval(",
    )
    for token in prohibited:
        assert token not in source
