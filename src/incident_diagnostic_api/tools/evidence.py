"""Deterministic Phase 7E tool-outcome consistency evidence without execution authority."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated, Final, Literal, Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import (
    OpaqueIdentifier,
    Timestamp,
    VersionedContract,
)
from incident_diagnostic_api.tools.contracts import (
    EXPECTED_TOOL_ERROR_CATEGORIES,
    EXPECTED_TOOL_ERROR_RETRYABILITY,
    TOOL_ENVELOPE_VERSION,
    ToolArgumentName,
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
)
from incident_diagnostic_api.tools.mock import build_deterministic_mock_tool_result
from incident_diagnostic_api.tools.registry import (
    DEFAULT_TOOL_REGISTRY,
    TOOL_CONTRACT_VERSION,
    ToolApprovalRequirement,
    ToolCapability,
    ToolIdempotencyRequirement,
    ToolName,
    ToolRegistry,
    ToolRiskTier,
    ToolSideEffect,
)

TOOL_OUTCOME_EVIDENCE_VERSION: Final[Literal["7e.1"]] = "7e.1"

ToolArgumentNames = Annotated[tuple[ToolArgumentName, ...], Field(max_length=32)]


class ToolOutcomeKind(StrEnum):
    """Closed outcome kinds represented by Phase 7E evidence."""

    RESULT = "result"
    ERROR = "error"


class ToolOutcomeConsistencyStatus(StrEnum):
    """Only consistent inputs may produce a Phase 7E evidence value."""

    CONSISTENT = "consistent"


class ToolOutcomeEvidence(VersionedContract):
    """Minimized in-process evidence for one deterministic consistency evaluation."""

    tool_outcome_evidence_version: Literal["7e.1"] = TOOL_OUTCOME_EVIDENCE_VERSION
    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    tool_name: ToolName
    tool_contract_version: Literal["7a.1"] = TOOL_CONTRACT_VERSION
    tool_envelope_version: Literal["tool-envelope-v1"] = TOOL_ENVELOPE_VERSION
    evaluated_dispatch_semantics_version: Literal["7d.1"] = TOOL_DISPATCHER_VERSION
    registry_declared_capability: ToolCapability
    registry_declared_side_effect: ToolSideEffect
    registry_declared_risk_tier: ToolRiskTier
    registry_declared_idempotency_requirement: ToolIdempotencyRequirement
    registry_declared_approval_requirement: ToolApprovalRequirement
    registry_declared_timeout_seconds: Annotated[int, Field(gt=0)]
    registry_declared_authorization_required: bool
    registry_declared_execution_enabled: bool
    registry_declared_general_shell_access: bool
    outcome_kind: ToolOutcomeKind
    consistency_status: Literal[ToolOutcomeConsistencyStatus.CONSISTENT] = (
        ToolOutcomeConsistencyStatus.CONSISTENT
    )
    result_status: ToolResultStatus | None = None
    error_code: ToolErrorCode | None = None
    error_category: ToolErrorCategory | None = None
    retryable: bool | None = None
    idempotency_key_present: bool
    argument_names: ToolArgumentNames
    output_names: ToolArgumentNames
    requested_at: Timestamp
    outcome_at: Timestamp

    @model_validator(mode="after")
    def validate_internal_consistency(self) -> Self:
        """Reject directly constructed evidence with contradictory control metadata."""

        if not self.registry_declared_authorization_required:
            raise ValueError("registry declaration must require authorization")
        if self.registry_declared_execution_enabled:
            raise ValueError("registry declaration must keep real execution disabled")
        if self.registry_declared_general_shell_access:
            raise ValueError("registry declaration must prohibit general shell access")
        if (
            self.registry_declared_side_effect is ToolSideEffect.NONE
            and self.registry_declared_approval_requirement
            is ToolApprovalRequirement.HUMAN_APPROVAL
        ):
            raise ValueError("read-only registry declaration cannot require human approval")
        if (
            self.registry_declared_side_effect is not ToolSideEffect.NONE
            and self.registry_declared_approval_requirement is ToolApprovalRequirement.NONE
        ):
            raise ValueError("side-effecting registry declaration must require approval")

        self._validate_names(self.argument_names, field_name="argument_names")
        self._validate_names(self.output_names, field_name="output_names")

        if self.outcome_kind is ToolOutcomeKind.RESULT:
            self._validate_result_shape()
        else:
            self._validate_error_shape()

        return self

    @staticmethod
    def _validate_names(names: tuple[str, ...], *, field_name: str) -> None:
        if names != tuple(sorted(set(names))):
            raise ValueError(f"{field_name} must be unique and sorted")

    def _validate_result_shape(self) -> None:
        if self.registry_declared_side_effect is not ToolSideEffect.NONE:
            raise ValueError("result evidence requires a read-only registry declaration")
        if self.result_status is not ToolResultStatus.COMPLETED:
            raise ValueError("result evidence requires COMPLETED status")
        if self.error_code is not None or self.error_category is not None:
            raise ValueError("result evidence cannot contain error metadata")
        if self.retryable is not None:
            raise ValueError("result evidence cannot contain retryability metadata")

        expected_output_names = {
            "argument_count",
            "argument_names",
            "credential_access",
            "execution_mode",
            "mock_runtime_version",
            "network_access",
            "real_execution",
            "tool_name",
        }
        if self.idempotency_key_present:
            expected_output_names.add("idempotency_key")
        if self.output_names != tuple(sorted(expected_output_names)):
            raise ValueError("result evidence output_names do not match Phase 7C semantics")

    def _validate_error_shape(self) -> None:
        if self.registry_declared_side_effect is ToolSideEffect.NONE:
            raise ValueError("error evidence requires a side-effecting registry declaration")
        if self.result_status is not None:
            raise ValueError("error evidence cannot contain result status")
        if self.error_code is not ToolErrorCode.APPROVAL_REQUIRED:
            raise ValueError("error evidence requires APPROVAL_REQUIRED")
        if self.error_category is not ToolErrorCategory.APPROVAL:
            raise ValueError("APPROVAL_REQUIRED must use the approval category")
        if self.retryable is not False:
            raise ValueError("APPROVAL_REQUIRED evidence must be non-retryable")
        if self.output_names:
            raise ValueError("error evidence cannot contain output names")


class ToolOutcomeEvidenceErrorCode(StrEnum):
    """Closed non-sensitive failure codes for Phase 7E construction."""

    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    VERSION_MISMATCH = "VERSION_MISMATCH"
    TEMPORAL_INVERSION = "TEMPORAL_INVERSION"
    REGISTRY_OUTCOME_CONTRADICTION = "REGISTRY_OUTCOME_CONTRADICTION"
    OUTCOME_SHAPE_CONTRADICTION = "OUTCOME_SHAPE_CONTRADICTION"


_ERROR_MESSAGES: Final[dict[ToolOutcomeEvidenceErrorCode, str]] = {
    ToolOutcomeEvidenceErrorCode.IDENTITY_MISMATCH: (
        "tool outcome identity does not match the request"
    ),
    ToolOutcomeEvidenceErrorCode.VERSION_MISMATCH: (
        "tool outcome contract versions do not match the request"
    ),
    ToolOutcomeEvidenceErrorCode.TEMPORAL_INVERSION: (
        "tool outcome timestamp precedes the request timestamp"
    ),
    ToolOutcomeEvidenceErrorCode.REGISTRY_OUTCOME_CONTRADICTION: (
        "tool outcome contradicts the current valid-registry dispatch disposition"
    ),
    ToolOutcomeEvidenceErrorCode.OUTCOME_SHAPE_CONTRADICTION: (
        "tool outcome control fields contradict deterministic Phase 7 semantics"
    ),
}


@dataclass(frozen=True, slots=True)
class ToolOutcomeEvidenceError(Exception):
    """Controlled non-sensitive failure raised for inconsistent Phase 7E inputs."""

    code: ToolOutcomeEvidenceErrorCode
    message: str

    def __str__(self) -> str:
        """Return the controlled Phase 7E failure description."""

        return self.message


def _failure(code: ToolOutcomeEvidenceErrorCode) -> ToolOutcomeEvidenceError:
    return ToolOutcomeEvidenceError(code=code, message=_ERROR_MESSAGES[code])


def _validate_identity(request: ToolRequest, outcome: ToolDispatchOutcome) -> None:
    if (
        outcome.request_id != request.request_id
        or outcome.trace_id != request.trace_id
        or outcome.tool_name is not request.tool_name
    ):
        raise _failure(ToolOutcomeEvidenceErrorCode.IDENTITY_MISMATCH)


def _validate_versions(request: ToolRequest, outcome: ToolDispatchOutcome) -> None:
    if (
        outcome.tool_contract_version != request.tool_contract_version
        or outcome.tool_envelope_version != request.tool_envelope_version
    ):
        raise _failure(ToolOutcomeEvidenceErrorCode.VERSION_MISMATCH)


def _outcome_at(outcome: ToolDispatchOutcome) -> Timestamp:
    if isinstance(outcome, ToolResult):
        return outcome.completed_at
    return outcome.occurred_at


def _validate_registry_safety(
    *,
    authorization_required: bool,
    execution_enabled: bool,
    general_shell_access: bool,
    side_effect: ToolSideEffect,
    approval_requirement: ToolApprovalRequirement,
) -> None:
    if not authorization_required or execution_enabled or general_shell_access:
        raise _failure(ToolOutcomeEvidenceErrorCode.REGISTRY_OUTCOME_CONTRADICTION)
    if (
        side_effect is ToolSideEffect.NONE
        and approval_requirement is ToolApprovalRequirement.HUMAN_APPROVAL
    ):
        raise _failure(ToolOutcomeEvidenceErrorCode.REGISTRY_OUTCOME_CONTRADICTION)
    if (
        side_effect is not ToolSideEffect.NONE
        and approval_requirement is ToolApprovalRequirement.NONE
    ):
        raise _failure(ToolOutcomeEvidenceErrorCode.REGISTRY_OUTCOME_CONTRADICTION)


def _validate_result(
    request: ToolRequest,
    outcome: ToolResult,
) -> tuple[ToolResultStatus, tuple[ToolArgumentName, ...]]:
    expected = build_deterministic_mock_tool_result(
        request,
        completed_at=outcome.completed_at,
    )
    if outcome != expected:
        raise _failure(ToolOutcomeEvidenceErrorCode.OUTCOME_SHAPE_CONTRADICTION)
    return outcome.status, tuple(sorted(outcome.output))


def _validate_error(
    outcome: ToolError,
) -> tuple[ToolErrorCode, ToolErrorCategory, bool]:
    if outcome.error_code is not ToolErrorCode.APPROVAL_REQUIRED:
        raise _failure(ToolOutcomeEvidenceErrorCode.REGISTRY_OUTCOME_CONTRADICTION)
    if (
        outcome.error_category
        is not EXPECTED_TOOL_ERROR_CATEGORIES[ToolErrorCode.APPROVAL_REQUIRED]
        or outcome.retryable
        is not EXPECTED_TOOL_ERROR_RETRYABILITY[ToolErrorCode.APPROVAL_REQUIRED]
    ):
        raise _failure(ToolOutcomeEvidenceErrorCode.OUTCOME_SHAPE_CONTRADICTION)
    return outcome.error_code, outcome.error_category, outcome.retryable


def build_deterministic_tool_outcome_evidence(
    request: ToolRequest,
    outcome: ToolDispatchOutcome,
    *,
    registry: ToolRegistry = DEFAULT_TOOL_REGISTRY,
) -> ToolOutcomeEvidence:
    """Evaluate one supplied typed outcome without invoking a dispatcher or real tool."""

    _validate_identity(request, outcome)
    _validate_versions(request, outcome)

    outcome_at = _outcome_at(outcome)
    if outcome_at < request.requested_at:
        raise _failure(ToolOutcomeEvidenceErrorCode.TEMPORAL_INVERSION)

    try:
        definition = registry.get(request.tool_name)
    except KeyError as exc:
        raise _failure(ToolOutcomeEvidenceErrorCode.REGISTRY_OUTCOME_CONTRADICTION) from exc

    _validate_registry_safety(
        authorization_required=definition.authorization_required,
        execution_enabled=definition.execution_enabled,
        general_shell_access=definition.general_shell_access,
        side_effect=definition.side_effect,
        approval_requirement=definition.approval_requirement,
    )

    result_status: ToolResultStatus | None = None
    error_code: ToolErrorCode | None = None
    error_category: ToolErrorCategory | None = None
    retryable: bool | None = None
    output_names: tuple[ToolArgumentName, ...] = ()

    if definition.side_effect is ToolSideEffect.NONE:
        if not isinstance(outcome, ToolResult):
            raise _failure(ToolOutcomeEvidenceErrorCode.REGISTRY_OUTCOME_CONTRADICTION)
        result_status, output_names = _validate_result(request, outcome)
        outcome_kind = ToolOutcomeKind.RESULT
    else:
        if not isinstance(outcome, ToolError):
            raise _failure(ToolOutcomeEvidenceErrorCode.REGISTRY_OUTCOME_CONTRADICTION)
        error_code, error_category, retryable = _validate_error(outcome)
        outcome_kind = ToolOutcomeKind.ERROR

    return ToolOutcomeEvidence(
        request_id=request.request_id,
        trace_id=request.trace_id,
        tool_name=request.tool_name,
        registry_declared_capability=definition.capability,
        registry_declared_side_effect=definition.side_effect,
        registry_declared_risk_tier=definition.risk_tier,
        registry_declared_idempotency_requirement=definition.idempotency_requirement,
        registry_declared_approval_requirement=definition.approval_requirement,
        registry_declared_timeout_seconds=definition.timeout_seconds,
        registry_declared_authorization_required=definition.authorization_required,
        registry_declared_execution_enabled=definition.execution_enabled,
        registry_declared_general_shell_access=definition.general_shell_access,
        outcome_kind=outcome_kind,
        result_status=result_status,
        error_code=error_code,
        error_category=error_category,
        retryable=retryable,
        idempotency_key_present=request.idempotency_key is not None,
        argument_names=tuple(sorted(request.arguments)),
        output_names=output_names,
        requested_at=request.requested_at,
        outcome_at=outcome_at,
    )
