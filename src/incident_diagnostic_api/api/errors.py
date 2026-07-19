"""Deterministic API exception handling using CT-06."""

from datetime import UTC, datetime

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from incident_diagnostic_api.contracts import (
    ControlledError,
    ErrorCategory,
    ErrorCode,
    LifecycleStage,
)
from incident_diagnostic_api.core.correlation import get_request_correlation_id


async def request_validation_error_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Return a bounded error without reflecting invalid request content."""

    if not isinstance(exception, RequestValidationError):
        raise TypeError("handler requires RequestValidationError")

    controlled_error = ControlledError(
        trace_id=get_request_correlation_id(request),
        error_code=ErrorCode.INVALID_REQUEST,
        error_category=ErrorCategory.VALIDATION,
        safe_message="The request does not satisfy the required contract.",
        retryable=False,
        failed_stage=LifecycleStage.ADMISSION,
        occurred_at=datetime.now(UTC),
    )

    return JSONResponse(
        status_code=422,
        content=controlled_error.model_dump(mode="json"),
    )
