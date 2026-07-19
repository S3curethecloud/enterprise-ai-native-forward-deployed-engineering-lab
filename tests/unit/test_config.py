"""Tests for fail-closed Phase 3 configuration."""

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.core.config import Settings, get_settings

PROHIBITED_CAPABILITIES = [
    "external_model_enabled",
    "enterprise_retrieval_enabled",
    "tool_execution_enabled",
    "infrastructure_mutation_enabled",
    "cloud_deployment_enabled",
    "production_deployment_enabled",
]


def test_prohibited_capabilities_default_to_false() -> None:
    settings = Settings()

    for field_name in PROHIBITED_CAPABILITIES:
        assert getattr(settings, field_name) is False


@pytest.mark.parametrize("field_name", PROHIBITED_CAPABILITIES)
def test_direct_input_cannot_enable_prohibited_capability(
    field_name: str,
) -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate({field_name: True})


@pytest.mark.parametrize("field_name", PROHIBITED_CAPABILITIES)
def test_environment_cannot_enable_prohibited_capability(
    field_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    environment_name = f"CBIDA_{field_name.upper()}"
    monkeypatch.setenv(environment_name, "true")

    with pytest.raises(ValidationError):
        Settings()


@pytest.mark.parametrize("service_name", ["gateway", "runtime", "evidence"])
def test_approved_local_service_names_are_accepted(service_name: str) -> None:
    settings = Settings.model_validate({"service_name": service_name})

    assert settings.service_name == service_name


@pytest.mark.parametrize(
    "invalid_service_name",
    [
        "production-executor",
        "tool-runner",
        "remediation-agent",
    ],
)
def test_unapproved_service_name_is_rejected(
    invalid_service_name: str,
) -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate({"service_name": invalid_service_name})


def test_production_environment_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate({"environment": "production"})


@pytest.mark.parametrize("port", [0, 1023, 65536])
def test_port_outside_local_service_range_is_rejected(port: int) -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate({"port": port})


def test_settings_are_frozen() -> None:
    settings = Settings()

    with pytest.raises(ValidationError):
        settings.environment = "test"


def test_cached_settings_returns_same_instance() -> None:
    get_settings.cache_clear()

    first = get_settings()
    second = get_settings()

    assert first is second

    get_settings.cache_clear()
