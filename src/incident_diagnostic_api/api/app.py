"""Reusable FastAPI application factory for local Phase 3 services."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from incident_diagnostic_api.api.contracts import (
    router as contract_validation_router,
)
from incident_diagnostic_api.api.errors import request_validation_error_handler
from incident_diagnostic_api.api.health import router as health_router
from incident_diagnostic_api.core.config import Settings, get_settings
from incident_diagnostic_api.core.correlation import CorrelationIdMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create one local service with explicit immutable settings."""

    resolved_settings = settings if settings is not None else get_settings()

    application = FastAPI(
        title=(f"{resolved_settings.application_name} — {resolved_settings.service_name}"),
        version=resolved_settings.application_version,
        description=(
            "Local Phase 3 service foundation. External models, enterprise "
            "retrieval, tool execution, infrastructure mutation, cloud "
            "deployment, and production deployment are disabled."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    application.state.settings = resolved_settings
    application.add_middleware(CorrelationIdMiddleware)
    application.add_exception_handler(
        RequestValidationError,
        request_validation_error_handler,
    )
    application.include_router(health_router)

    if resolved_settings.service_name == "gateway":
        application.include_router(contract_validation_router)

    return application
