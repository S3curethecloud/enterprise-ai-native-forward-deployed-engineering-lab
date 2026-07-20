"""Integration tests for local service health and readiness."""

from typing import Literal

import pytest
from fastapi.testclient import TestClient

from incident_diagnostic_api.api.app import create_app
from incident_diagnostic_api.api.models import (
    HealthResponse,
    ReadinessResponse,
)
from incident_diagnostic_api.core.config import Settings
from incident_diagnostic_api.core.correlation import CORRELATION_PATTERN

ServiceName = Literal["gateway", "runtime", "evidence"]

SERVICE_CASES: list[tuple[ServiceName, int]] = [
    ("gateway", 8000),
    ("runtime", 8001),
    ("evidence", 8002),
]


def create_test_client(
    service_name: ServiceName,
    port: int,
) -> TestClient:
    """Create an isolated local-only service client."""

    settings = Settings(
        environment="test",
        service_name=service_name,
        port=port,
    )

    return TestClient(create_app(settings))


@pytest.mark.parametrize(("service_name", "port"), SERVICE_CASES)
def test_health_is_valid_for_each_service(
    service_name: ServiceName,
    port: int,
) -> None:
    with create_test_client(service_name, port) as client:
        response = client.get(
            "/health",
            headers={"X-Correlation-ID": f"{service_name}-health-101"},
        )

    assert response.status_code == 200
    health = HealthResponse.model_validate(response.json())

    assert health.service == service_name
    assert health.status == "healthy"
    assert health.environment == "test"
    assert health.correlation_id == f"{service_name}-health-101"
    assert response.headers["X-Correlation-ID"] == health.correlation_id


@pytest.mark.parametrize(("service_name", "port"), SERVICE_CASES)
def test_readiness_is_valid_for_each_service(
    service_name: ServiceName,
    port: int,
) -> None:
    with create_test_client(service_name, port) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    readiness = ReadinessResponse.model_validate(response.json())

    assert readiness.service == service_name
    assert readiness.status == "ready"
    assert readiness.environment == "test"
    assert all(dependency.status != "unavailable" for dependency in readiness.dependencies)


@pytest.mark.parametrize(("service_name", "port"), SERVICE_CASES)
def test_prohibited_capabilities_are_false_for_each_service(
    service_name: ServiceName,
    port: int,
) -> None:
    with create_test_client(service_name, port) as client:
        response = client.get("/ready")

    posture = ReadinessResponse.model_validate(response.json()).capability_posture

    assert posture.external_model_enabled is False
    assert posture.enterprise_retrieval_enabled is False
    assert posture.tool_execution_enabled is False
    assert posture.infrastructure_mutation_enabled is False
    assert posture.cloud_deployment_enabled is False
    assert posture.production_deployment_enabled is False


@pytest.mark.parametrize(
    "invalid_correlation_id",
    [
        "",
        "contains spaces",
        "../relative",
        "x" * 129,
    ],
)
def test_invalid_correlation_id_is_replaced(
    invalid_correlation_id: str,
) -> None:
    with create_test_client("gateway", 8000) as client:
        response = client.get(
            "/health",
            headers={"X-Correlation-ID": invalid_correlation_id},
        )

    correlation_id = response.headers["X-Correlation-ID"]

    assert correlation_id != invalid_correlation_id
    assert correlation_id.startswith("corr-")
    assert CORRELATION_PATTERN.fullmatch(correlation_id)


def test_missing_correlation_id_is_generated_and_returned() -> None:
    with create_test_client("gateway", 8000) as client:
        response = client.get("/health")

    correlation_id = response.headers["X-Correlation-ID"]

    assert correlation_id.startswith("corr-")
    assert response.json()["correlation_id"] == correlation_id


@pytest.mark.parametrize(("service_name", "port"), SERVICE_CASES)
def test_openapi_contains_only_authorized_routes(
    service_name: ServiceName,
    port: int,
) -> None:
    with create_test_client(service_name, port) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200

    expected_paths = {"/health", "/ready"}

    if service_name == "gateway":
        expected_paths.update(
            {
                "/v1/contracts/diagnostic-request/validate",
                "/v1/contracts/diagnostic-response/validate",
            }
        )

    if service_name == "runtime":
        expected_paths.update(
            {
                "/v1/runtime/workflows",
                "/v1/runtime/workflows/{workflow_id}",
                "/v1/runtime/workflows/{workflow_id}/transitions",
                "/v1/runtime/workflows/{workflow_id}/retries",
                "/v1/runtime/workflows/{workflow_id}/checkpoints",
                "/v1/runtime/workflows/{workflow_id}/replay",
            }
        )

    assert set(response.json()["paths"]) == expected_paths


@pytest.mark.parametrize(
    "unauthorized_path",
    [
        "/diagnose",
        "/retrieve",
        "/tools",
        "/execute",
        "/remediate",
        "/deploy",
    ],
)
def test_unauthorized_runtime_routes_do_not_exist(
    unauthorized_path: str,
) -> None:
    with create_test_client("gateway", 8000) as client:
        response = client.post(unauthorized_path)

    assert response.status_code == 404
