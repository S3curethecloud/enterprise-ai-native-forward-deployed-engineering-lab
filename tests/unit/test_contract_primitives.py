"""Tests for the shared executable contract primitives."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.contracts import (
    Environment,
    OpaqueIdentifier,
    PolicyOperation,
    RequestType,
    VersionedContract,
)


class IdentifierFixture(VersionedContract):
    """Minimal fixture used to exercise the shared identifier type."""

    identifier: OpaqueIdentifier


def test_supported_contract_version_is_applied_by_default() -> None:
    fixture = IdentifierFixture(identifier="req-123")

    assert fixture.contract_version == "1.0"


def test_unsupported_contract_version_is_rejected() -> None:
    with pytest.raises(ValidationError):
        IdentifierFixture(
            contract_version="2.0",  # type: ignore[arg-type]
            identifier="req-123",
        )


@pytest.mark.parametrize(
    "identifier",
    [
        "req-123",
        "INC-10427",
        "tenant/service:resource_1.0",
    ],
)
def test_valid_opaque_identifiers_are_accepted(identifier: str) -> None:
    fixture = IdentifierFixture(identifier=identifier)

    assert fixture.identifier == identifier


@pytest.mark.parametrize(
    "identifier",
    [
        "",
        " ",
        "contains spaces",
        "../relative-path",
        "identifier?query=true",
        "x" * 129,
    ],
)
def test_invalid_opaque_identifiers_are_rejected(identifier: str) -> None:
    with pytest.raises(ValidationError):
        IdentifierFixture(identifier=identifier)


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        IdentifierFixture(
            identifier="req-123",
            unexpected="value",  # type: ignore[call-arg]
        )


def test_contract_instances_are_frozen() -> None:
    fixture = IdentifierFixture(identifier="req-123")

    with pytest.raises(ValidationError):
        fixture.identifier = "req-456"


def test_required_enumerations_have_expected_values() -> None:
    assert Environment.PRODUCTION.value == "production"
    assert RequestType.DIAGNOSTIC_RECOMMENDATION.value == "diagnostic_recommendation"
    assert PolicyOperation.RETRIEVE_RUNBOOK_EVIDENCE.value == "retrieve_runbook_evidence"


def test_aware_timestamp_fixture_is_timezone_aware() -> None:
    timestamp = datetime(2026, 7, 19, 18, 30, tzinfo=UTC)

    assert timestamp.utcoffset() is not None
