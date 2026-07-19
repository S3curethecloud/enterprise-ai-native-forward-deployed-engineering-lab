"""Static tests for the Phase 3 local container-packaging boundary."""

from pathlib import Path
from typing import Any

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE_PATH = REPOSITORY_ROOT / "Dockerfile"
COMPOSE_PATH = REPOSITORY_ROOT / "compose.yaml"

EXPECTED_SERVICES = {"gateway", "runtime", "evidence"}
EXPECTED_EXPOSED_PORTS = {
    "gateway": "8000",
    "runtime": "8001",
    "evidence": "8002",
}
PROHIBITED_CAPABILITIES = {
    "EXTERNAL_MODEL_ENABLED",
    "ENTERPRISE_RETRIEVAL_ENABLED",
    "TOOL_EXECUTION_ENABLED",
    "INFRASTRUCTURE_MUTATION_ENABLED",
    "CLOUD_DEPLOYMENT_ENABLED",
    "PRODUCTION_DEPLOYMENT_ENABLED",
}


def load_compose() -> dict[str, Any]:
    """Load the Compose definition as structured test data."""

    document = yaml.safe_load(COMPOSE_PATH.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


def test_dockerfile_uses_bounded_python_base() -> None:
    dockerfile = DOCKERFILE_PATH.read_text(encoding="utf-8")

    assert "FROM python:3.12-slim" in dockerfile
    assert "COPY requirements/runtime.lock" in dockerfile
    assert "--require-hashes" in dockerfile
    assert "--no-deps" in dockerfile


def test_dockerfile_runs_as_non_root() -> None:
    dockerfile = DOCKERFILE_PATH.read_text(encoding="utf-8")

    assert "USER 10001:10001" in dockerfile
    assert "appuser" in dockerfile
    assert "appgroup" in dockerfile


def test_dockerfile_defaults_to_gateway_only() -> None:
    dockerfile = DOCKERFILE_PATH.read_text(encoding="utf-8")

    assert "incident_diagnostic_api.services.gateway:app" in dockerfile
    assert "127.0.0.1:8000/health" in dockerfile


def test_compose_defines_only_bounded_services() -> None:
    services = load_compose()["services"]

    assert set(services) == EXPECTED_SERVICES


def test_compose_ports_are_internal_only() -> None:
    services = load_compose()["services"]

    for service_name, expected_port in EXPECTED_EXPOSED_PORTS.items():
        service = services[service_name]

        assert service["expose"] == [expected_port]
        assert "ports" not in service


def test_compose_services_use_restricted_runtime_controls() -> None:
    services = load_compose()["services"]

    for service in services.values():
        assert service["user"] == "10001:10001"
        assert service["read_only"] is True
        assert service["cap_drop"] == ["ALL"]
        assert "no-new-privileges:true" in service["security_opt"]
        assert service["restart"] == "no"
        assert service["init"] is True


def test_compose_capabilities_are_explicitly_disabled() -> None:
    services = load_compose()["services"]

    for service in services.values():
        environment = service["environment"]

        assert set(environment) == PROHIBITED_CAPABILITIES
        assert all(str(environment[name]).lower() == "false" for name in PROHIBITED_CAPABILITIES)


def test_compose_uses_an_internal_network() -> None:
    document = load_compose()

    assert document["networks"]["diagnostic-local"]["internal"] is True

    for service in document["services"].values():
        assert service["networks"] == ["diagnostic-local"]


def test_compose_health_checks_are_service_specific() -> None:
    services = load_compose()["services"]

    for service_name, container_port in EXPECTED_EXPOSED_PORTS.items():
        health_command = " ".join(services[service_name]["healthcheck"]["test"])

        assert f"127.0.0.1:{container_port}/health" in health_command
