"""Local-only endpoints for executable contract validation."""

from typing import Any

from fastapi import APIRouter

from incident_diagnostic_api.contracts import (
    ControlledError,
    DiagnosticRequest,
    DiagnosticResponse,
)

router = APIRouter(
    prefix="/v1/contracts",
    tags=["contract-validation"],
)

CONTROLLED_VALIDATION_RESPONSE: dict[int | str, dict[str, Any]] = {
    422: {
        "model": ControlledError,
        "description": "CT-06 controlled contract-validation failure.",
    }
}


@router.post(
    "/diagnostic-request/validate",
    response_model=DiagnosticRequest,
    responses=CONTROLLED_VALIDATION_RESPONSE,
    summary="Validate a CT-01 diagnostic request",
)
def validate_diagnostic_request(
    request: DiagnosticRequest,
) -> DiagnosticRequest:
    """Return a request only after deterministic CT-01 validation."""

    return request


@router.post(
    "/diagnostic-response/validate",
    response_model=DiagnosticResponse,
    responses=CONTROLLED_VALIDATION_RESPONSE,
    summary="Validate a CT-05 diagnostic response",
)
def validate_diagnostic_response(
    response: DiagnosticResponse,
) -> DiagnosticResponse:
    """Return a response only after deterministic CT-05 validation."""

    return response
