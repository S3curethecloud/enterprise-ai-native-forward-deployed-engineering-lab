"""Focused tests for defensive branches and local CLI behavior."""

import asyncio
from typing import Any

import pytest
import uvicorn
from fastapi import FastAPI, Request

from incident_diagnostic_api import main
from incident_diagnostic_api.api.errors import (
    request_validation_error_handler,
)
from incident_diagnostic_api.api.health import get_app_settings
from incident_diagnostic_api.core.correlation import (
    get_request_correlation_id,
)
from incident_diagnostic_api.services.gateway import app as gateway_app


def request_scope(application: FastAPI | None = None) -> dict[str, Any]:
    """Return the minimum HTTP scope needed by defensive unit tests."""

    scope: dict[str, Any] = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 50000),
        "server": ("testserver", 80),
        "root_path": "",
    }

    if application is not None:
        scope["app"] = application

    return scope


def test_error_handler_rejects_wrong_exception_type() -> None:
    request = Request(request_scope())

    with pytest.raises(
        TypeError,
        match="handler requires RequestValidationError",
    ):
        asyncio.run(
            request_validation_error_handler(
                request,
                RuntimeError("wrong exception"),
            )
        )


def test_missing_application_settings_fail_closed() -> None:
    application = FastAPI()
    request = Request(request_scope(application))

    with pytest.raises(
        RuntimeError,
        match="application settings are not initialized",
    ):
        get_app_settings(request)


def test_missing_correlation_middleware_state_fails_closed() -> None:
    request = Request(request_scope())

    with pytest.raises(
        RuntimeError,
        match="correlation middleware did not assign an identifier",
    ):
        get_request_correlation_id(request)


def test_local_cli_runs_gateway_with_bounded_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_run(application: Any, **kwargs: Any) -> None:
        captured["application"] = application
        captured.update(kwargs)

    monkeypatch.setattr(uvicorn, "run", fake_run)

    main.run()

    assert captured["application"] is gateway_app
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 8000
    assert captured["reload"] is False
    assert captured["workers"] == 1
