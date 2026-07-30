"""Contract tests for the non-executable Phase 7A tool registry."""

from dataclasses import FrozenInstanceError

import pytest

from incident_diagnostic_api.tools.registry import (
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


@pytest.fixture
def registry() -> ToolRegistry:
    return build_default_tool_registry()


def test_contract_and_registry_versions_are_explicit() -> None:
    assert TOOL_CONTRACT_VERSION == "7a.1"
    assert TOOL_REGISTRY_VERSION == "7a.1"


def test_registry_contains_exactly_the_allowlisted_tools(
    registry: ToolRegistry,
) -> None:
    assert len(registry.tools) == 7
    assert {item.tool_name for item in registry.tools} == set(ToolName)


def test_registry_order_is_deterministic(registry: ToolRegistry) -> None:
    assert [item.tool_name for item in registry.tools] == list(ToolName)


@pytest.mark.parametrize("tool_name", list(ToolName))
def test_every_allowlisted_tool_is_resolvable(
    registry: ToolRegistry,
    tool_name: ToolName,
) -> None:
    assert registry.get(tool_name).tool_name is tool_name


@pytest.mark.parametrize("tool_name", list(ToolName))
def test_every_tool_requires_authorization(
    registry: ToolRegistry,
    tool_name: ToolName,
) -> None:
    assert registry.get(tool_name).authorization_required is True


@pytest.mark.parametrize("tool_name", list(ToolName))
def test_every_tool_is_non_executable(
    registry: ToolRegistry,
    tool_name: ToolName,
) -> None:
    assert registry.get(tool_name).execution_enabled is False


@pytest.mark.parametrize("tool_name", list(ToolName))
def test_no_tool_has_general_shell_access(
    registry: ToolRegistry,
    tool_name: ToolName,
) -> None:
    assert registry.get(tool_name).general_shell_access is False


def test_registry_lookup_mapping_is_read_only(registry: ToolRegistry) -> None:
    with pytest.raises(TypeError):
        registry.by_name[ToolName.JIRA_ISSUE_READ] = registry.tools[0]  # type: ignore[index]


def test_tool_definition_is_immutable(registry: ToolRegistry) -> None:
    with pytest.raises(FrozenInstanceError):
        registry.tools[0].execution_enabled = True  # type: ignore[misc]


def test_duplicate_tool_names_are_rejected(registry: ToolRegistry) -> None:
    duplicate = (*registry.tools[:-1], registry.tools[0])
    with pytest.raises(ValueError, match="duplicate"):
        ToolRegistry(version=TOOL_REGISTRY_VERSION, tools=duplicate)


def test_incomplete_allowlist_is_rejected(registry: ToolRegistry) -> None:
    with pytest.raises(ValueError, match="exactly match"):
        ToolRegistry(version=TOOL_REGISTRY_VERSION, tools=registry.tools[:-1])


def test_non_positive_timeout_is_rejected() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        ToolDefinition(
            tool_name=ToolName.JIRA_ISSUE_READ,
            capability=ToolCapability.TICKET_READ,
            side_effect=ToolSideEffect.NONE,
            risk_tier=ToolRiskTier.LOW,
            idempotency_requirement=ToolIdempotencyRequirement.NOT_REQUIRED,
            approval_requirement=ToolApprovalRequirement.POLICY_DECISION,
            timeout_seconds=0,
        )


def test_execution_cannot_be_enabled() -> None:
    with pytest.raises(ValueError, match="execution"):
        ToolDefinition(
            tool_name=ToolName.JIRA_ISSUE_READ,
            capability=ToolCapability.TICKET_READ,
            side_effect=ToolSideEffect.NONE,
            risk_tier=ToolRiskTier.LOW,
            idempotency_requirement=ToolIdempotencyRequirement.NOT_REQUIRED,
            approval_requirement=ToolApprovalRequirement.POLICY_DECISION,
            timeout_seconds=10,
            execution_enabled=True,
        )


def test_general_shell_access_cannot_be_enabled() -> None:
    with pytest.raises(ValueError, match="shell"):
        ToolDefinition(
            tool_name=ToolName.JIRA_ISSUE_READ,
            capability=ToolCapability.TICKET_READ,
            side_effect=ToolSideEffect.NONE,
            risk_tier=ToolRiskTier.LOW,
            idempotency_requirement=ToolIdempotencyRequirement.NOT_REQUIRED,
            approval_requirement=ToolApprovalRequirement.POLICY_DECISION,
            timeout_seconds=10,
            general_shell_access=True,
        )


def test_side_effecting_tool_cannot_omit_approval() -> None:
    with pytest.raises(ValueError, match="require approval"):
        ToolDefinition(
            tool_name=ToolName.JIRA_ISSUE_COMMENT,
            capability=ToolCapability.TICKET_COMMENT,
            side_effect=ToolSideEffect.APPEND_ONLY,
            risk_tier=ToolRiskTier.MEDIUM,
            idempotency_requirement=ToolIdempotencyRequirement.REQUIRED,
            approval_requirement=ToolApprovalRequirement.NONE,
            timeout_seconds=10,
        )
