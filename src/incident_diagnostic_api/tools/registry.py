"""Fail-closed Phase 7A typed enterprise-tool registry.

This module defines metadata only. It provides no invocation interface and
grants no authority to execute a tool.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

TOOL_CONTRACT_VERSION: Final = "7a.1"
TOOL_REGISTRY_VERSION: Final = "7a.1"


class ToolName(StrEnum):
    """Closed allowlist of enterprise-tool names."""

    JIRA_ISSUE_READ = "jira.issue.read"
    JIRA_ISSUE_COMMENT = "jira.issue.comment"
    SERVICENOW_INCIDENT_READ = "servicenow.incident.read"
    SERVICENOW_INCIDENT_UPDATE = "servicenow.incident.update"
    KUBERNETES_RESOURCE_READ = "kubernetes.resource.read"
    CLOUD_RESOURCE_READ = "cloud.resource.read"
    DATABASE_QUERY_READ = "database.query.read"


class ToolCapability(StrEnum):
    """Business capability exposed by a governed tool definition."""

    TICKET_READ = "ticket_read"
    TICKET_COMMENT = "ticket_comment"
    INCIDENT_READ = "incident_read"
    INCIDENT_UPDATE = "incident_update"
    RESOURCE_READ = "resource_read"
    DATA_QUERY_READ = "data_query_read"


class ToolSideEffect(StrEnum):
    """Expected state-change behavior."""

    NONE = "none"
    APPEND_ONLY = "append_only"
    MUTATING = "mutating"


class ToolRiskTier(StrEnum):
    """Risk classification independent of execution authority."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ToolIdempotencyRequirement(StrEnum):
    """Idempotency contract required before a future invocation."""

    NOT_REQUIRED = "not_required"
    REQUIRED = "required"


class ToolApprovalRequirement(StrEnum):
    """Approval metadata; it does not implement an approval workflow."""

    NONE = "none"
    POLICY_DECISION = "policy_decision"
    HUMAN_APPROVAL = "human_approval"


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """Immutable metadata for one allowlisted enterprise tool."""

    tool_name: ToolName
    capability: ToolCapability
    side_effect: ToolSideEffect
    risk_tier: ToolRiskTier
    idempotency_requirement: ToolIdempotencyRequirement
    approval_requirement: ToolApprovalRequirement
    timeout_seconds: int
    authorization_required: bool = True
    execution_enabled: bool = False
    general_shell_access: bool = False

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        if self.execution_enabled:
            raise ValueError("Phase 7A tool execution must remain disabled")
        if self.general_shell_access:
            raise ValueError("general shell access is prohibited")
        if not self.authorization_required:
            raise ValueError("every Phase 7A tool must require authorization")
        if (
            self.side_effect is ToolSideEffect.NONE
            and self.approval_requirement is ToolApprovalRequirement.HUMAN_APPROVAL
        ):
            raise ValueError("read-only tools must not claim human approval")
        if (
            self.side_effect is not ToolSideEffect.NONE
            and self.approval_requirement is ToolApprovalRequirement.NONE
        ):
            raise ValueError("side-effecting tools must require approval")


@dataclass(frozen=True, slots=True)
class ToolRegistry:
    """Immutable, uniquely keyed collection of tool definitions."""

    version: str
    tools: tuple[ToolDefinition, ...]

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError("registry version must not be empty")
        names = tuple(definition.tool_name for definition in self.tools)
        if len(names) != len(set(names)):
            raise ValueError("tool registry contains duplicate tool names")
        if set(names) != set(ToolName):
            missing = sorted(name.value for name in set(ToolName) - set(names))
            unexpected = sorted(name.value for name in set(names) - set(ToolName))
            raise ValueError(
                "tool registry must exactly match the ToolName allowlist; "
                f"missing={missing}, unexpected={unexpected}"
            )

    def __iter__(self) -> Iterator[ToolDefinition]:
        return iter(self.tools)

    def get(self, tool_name: ToolName) -> ToolDefinition:
        try:
            return self.by_name[tool_name]
        except KeyError as exc:
            raise KeyError(f"tool is not registered: {tool_name}") from exc

    @property
    def by_name(self) -> Mapping[ToolName, ToolDefinition]:
        return MappingProxyType({definition.tool_name: definition for definition in self.tools})


def build_default_tool_registry() -> ToolRegistry:
    """Build the deterministic, non-executable Phase 7A registry."""

    def read_tool(
        tool_name: ToolName,
        capability: ToolCapability,
    ) -> ToolDefinition:
        return ToolDefinition(
            tool_name=tool_name,
            capability=capability,
            side_effect=ToolSideEffect.NONE,
            risk_tier=ToolRiskTier.LOW,
            idempotency_requirement=(ToolIdempotencyRequirement.NOT_REQUIRED),
            approval_requirement=ToolApprovalRequirement.POLICY_DECISION,
            timeout_seconds=10,
        )

    return ToolRegistry(
        version=TOOL_REGISTRY_VERSION,
        tools=(
            read_tool(
                ToolName.JIRA_ISSUE_READ,
                ToolCapability.TICKET_READ,
            ),
            ToolDefinition(
                tool_name=ToolName.JIRA_ISSUE_COMMENT,
                capability=ToolCapability.TICKET_COMMENT,
                side_effect=ToolSideEffect.APPEND_ONLY,
                risk_tier=ToolRiskTier.MEDIUM,
                idempotency_requirement=ToolIdempotencyRequirement.REQUIRED,
                approval_requirement=ToolApprovalRequirement.HUMAN_APPROVAL,
                timeout_seconds=10,
            ),
            read_tool(
                ToolName.SERVICENOW_INCIDENT_READ,
                ToolCapability.INCIDENT_READ,
            ),
            ToolDefinition(
                tool_name=ToolName.SERVICENOW_INCIDENT_UPDATE,
                capability=ToolCapability.INCIDENT_UPDATE,
                side_effect=ToolSideEffect.MUTATING,
                risk_tier=ToolRiskTier.HIGH,
                idempotency_requirement=ToolIdempotencyRequirement.REQUIRED,
                approval_requirement=ToolApprovalRequirement.HUMAN_APPROVAL,
                timeout_seconds=10,
            ),
            read_tool(
                ToolName.KUBERNETES_RESOURCE_READ,
                ToolCapability.RESOURCE_READ,
            ),
            read_tool(
                ToolName.CLOUD_RESOURCE_READ,
                ToolCapability.RESOURCE_READ,
            ),
            read_tool(
                ToolName.DATABASE_QUERY_READ,
                ToolCapability.DATA_QUERY_READ,
            ),
        ),
    )


DEFAULT_TOOL_REGISTRY: Final = build_default_tool_registry()
