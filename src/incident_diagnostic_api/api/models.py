"""Typed API models for local service health and readiness."""

from typing import Literal

from pydantic import AwareDatetime

from incident_diagnostic_api.contracts.common import (
    ContractModel,
    OpaqueIdentifier,
    ShortText,
)

ServiceName = Literal["gateway", "runtime", "evidence"]
HealthStatus = Literal["healthy"]
ReadinessStatus = Literal["ready", "not_ready"]
DependencyStatus = Literal["available", "unavailable", "not_configured"]


class CapabilityPosture(ContractModel):
    """Explicit fail-closed authority posture exposed by every service."""

    external_model_enabled: Literal[False] = False
    enterprise_retrieval_enabled: Literal[False] = False
    tool_execution_enabled: Literal[False] = False
    infrastructure_mutation_enabled: Literal[False] = False
    cloud_deployment_enabled: Literal[False] = False
    production_deployment_enabled: Literal[False] = False


class DependencyReadiness(ContractModel):
    """One bounded dependency-readiness result."""

    dependency: OpaqueIdentifier
    status: DependencyStatus
    detail: ShortText


class HealthResponse(ContractModel):
    """Liveness response for one local service."""

    service: ServiceName
    status: HealthStatus
    version: OpaqueIdentifier
    environment: Literal["local", "test"]
    checked_at: AwareDatetime
    correlation_id: OpaqueIdentifier
    capability_posture: CapabilityPosture


class ReadinessResponse(ContractModel):
    """Readiness response with explicit local dependencies."""

    service: ServiceName
    status: ReadinessStatus
    version: OpaqueIdentifier
    environment: Literal["local", "test"]
    checked_at: AwareDatetime
    correlation_id: OpaqueIdentifier
    dependencies: tuple[DependencyReadiness, ...]
    capability_posture: CapabilityPosture
