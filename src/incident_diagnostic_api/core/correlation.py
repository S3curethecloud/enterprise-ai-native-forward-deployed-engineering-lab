"""Validated correlation-ID generation and propagation."""

import re
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

CORRELATION_HEADER = "X-Correlation-ID"
CORRELATION_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")


def resolve_correlation_id(candidate: str | None) -> str:
    """Return a validated client ID or a newly generated local ID."""

    if candidate is not None:
        normalized = candidate.strip()

        if CORRELATION_PATTERN.fullmatch(normalized):
            return normalized

    return f"corr-{uuid4().hex}"


def get_request_correlation_id(request: Request) -> str:
    """Return the correlation ID assigned by middleware."""

    correlation_id = getattr(request.state, "correlation_id", None)

    if not isinstance(correlation_id, str):
        raise RuntimeError("correlation middleware did not assign an identifier")

    return correlation_id


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Attach one validated correlation ID to request state and response."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        correlation_id = resolve_correlation_id(request.headers.get(CORRELATION_HEADER))
        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers[CORRELATION_HEADER] = correlation_id

        return response
