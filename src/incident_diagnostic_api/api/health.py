"""Health and readiness routes shared by local Phase 3 services."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from incident_diagnostic_api.api.models import (
    CapabilityPosture,
    DependencyReadiness,
    HealthResponse,
    ReadinessResponse,
)
from incident_diagnostic_api.core.config import Settings
from incident_diagnostic_api.core.correlation import get_request_correlation_id

router = APIRouter(tags=["service-status"])


def get_app_settings(request: Request) -> Settings:
    """Return the immutable settings bound to this application."""

    settings = getattr(request.app.state, "settings", None)

    if not isinstance(settings, Settings):
        raise RuntimeError("application settings are not initialized")

    return settings


SettingsDependency = Annotated[Settings, Depends(get_app_settings)]
CorrelationDependency = Annotated[str, Depends(get_request_correlation_id)]


def capability_posture(settings: Settings) -> CapabilityPosture:
    """Build an explicit authority posture from fail-closed settings."""

    return CapabilityPosture(
        external_model_enabled=settings.external_model_enabled,
        enterprise_retrieval_enabled=settings.enterprise_retrieval_enabled,
        tool_execution_enabled=settings.tool_execution_enabled,
        infrastructure_mutation_enabled=settings.infrastructure_mutation_enabled,
        cloud_deployment_enabled=settings.cloud_deployment_enabled,
        production_deployment_enabled=settings.production_deployment_enabled,
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Return local service liveness",
)
def health(
    settings: SettingsDependency,
    correlation_id: CorrelationDependency,
) -> HealthResponse:
    """Return liveness without calling an external dependency."""

    return HealthResponse(
        service=settings.service_name,
        status="healthy",
        version=settings.application_version,
        environment=settings.environment,
        checked_at=datetime.now(UTC),
        correlation_id=correlation_id,
        capability_posture=capability_posture(settings),
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Return local service readiness",
)
def readiness(
    settings: SettingsDependency,
    correlation_id: CorrelationDependency,
) -> ReadinessResponse:
    """Return readiness for the authorized local-only foundation."""

    dependencies = (
        DependencyReadiness(
            dependency="configuration",
            status="available",
            detail="Immutable local settings loaded.",
        ),
        DependencyReadiness(
            dependency="executable-contracts",
            status="available",
            detail="CT-01 through CT-07 are importable.",
        ),
        DependencyReadiness(
            dependency="external-model",
            status="not_configured",
            detail="External model access is not authorized in Phase 3.",
        ),
        DependencyReadiness(
            dependency="enterprise-retrieval",
            status="not_configured",
            detail="Enterprise retrieval is not authorized in Phase 3.",
        ),
        DependencyReadiness(
            dependency="tool-execution",
            status="not_configured",
            detail="Tool execution is not authorized in Phase 3.",
        ),
    )

    return ReadinessResponse(
        service=settings.service_name,
        status="ready",
        version=settings.application_version,
        environment=settings.environment,
        checked_at=datetime.now(UTC),
        correlation_id=correlation_id,
        dependencies=dependencies,
        capability_posture=capability_posture(settings),
    )
