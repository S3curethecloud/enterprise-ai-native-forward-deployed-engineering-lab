"""Positive and negative contract tests for CT-02."""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from pydantic import ValidationError

from incident_diagnostic_api.contracts import IdentityContext

AUTHENTICATED_AT = datetime(2026, 7, 19, 18, 0, tzinfo=UTC)


def valid_identity_payload() -> dict[str, Any]:
    """Return an isolated valid CT-02 payload."""

    return {
        "contract_version": "1.0",
        "subject_id": "user-1042",
        "tenant_id": "tenant-a",
        "authentication_method": "oidc",
        "authentication_time": AUTHENTICATED_AT,
        "session_id": "session-881",
        "roles": ["incident-responder"],
        "groups": ["payments-operations"],
        "source_entitlements": ["runbook:payments-api"],
        "assurance_level": "elevated",
        "expires_at": AUTHENTICATED_AT + timedelta(hours=1),
        "issuer": "enterprise-idp",
    }


def valid_delegation_payload() -> dict[str, Any]:
    """Return a valid delegation bound to the identity subject."""

    return {
        "delegator_subject_id": "incident-commander",
        "delegate_subject_id": "user-1042",
        "reason": "Temporary incident-response delegation",
        "expires_at": AUTHENTICATED_AT + timedelta(minutes=30),
    }


def test_valid_identity_context_is_accepted() -> None:
    identity = IdentityContext.model_validate(valid_identity_payload())

    assert identity.subject_id == "user-1042"
    assert identity.authentication_method.value == "oidc"
    assert identity.roles == ("incident-responder",)
    assert identity.source_entitlements == ("runbook:payments-api",)


@pytest.mark.parametrize(
    "required_field",
    [
        "subject_id",
        "tenant_id",
        "authentication_method",
        "authentication_time",
        "session_id",
        "roles",
        "groups",
        "source_entitlements",
        "assurance_level",
        "expires_at",
        "issuer",
    ],
)
def test_missing_required_identity_field_is_rejected(required_field: str) -> None:
    payload = valid_identity_payload()
    payload.pop(required_field)

    with pytest.raises(ValidationError):
        IdentityContext.model_validate(payload)


def test_unknown_identity_field_is_rejected() -> None:
    payload = valid_identity_payload()
    payload["prompt_supplied_role"] = "administrator"

    with pytest.raises(ValidationError):
        IdentityContext.model_validate(payload)


def test_naive_authentication_time_is_rejected() -> None:
    payload = valid_identity_payload()
    payload["authentication_time"] = datetime(2026, 7, 19, 18, 0)

    with pytest.raises(ValidationError):
        IdentityContext.model_validate(payload)


def test_expiration_before_authentication_is_rejected() -> None:
    payload = valid_identity_payload()
    payload["expires_at"] = AUTHENTICATED_AT - timedelta(seconds=1)

    with pytest.raises(
        ValidationError,
        match="identity context must expire after authentication",
    ):
        IdentityContext.model_validate(payload)


def test_expiration_boundary_is_deterministic() -> None:
    identity = IdentityContext.model_validate(valid_identity_payload())

    assert not identity.is_expired(AUTHENTICATED_AT)
    assert not identity.is_expired(AUTHENTICATED_AT + timedelta(minutes=59))
    assert identity.is_expired(AUTHENTICATED_AT + timedelta(hours=1))


def test_naive_expiration_check_is_rejected() -> None:
    identity = IdentityContext.model_validate(valid_identity_payload())

    with pytest.raises(
        ValueError,
        match="expiration checks require a timezone-aware timestamp",
    ):
        identity.is_expired(datetime(2026, 7, 19, 18, 30))


def test_valid_delegation_is_accepted() -> None:
    payload = valid_identity_payload()
    payload["delegation_context"] = valid_delegation_payload()

    identity = IdentityContext.model_validate(payload)

    assert identity.delegation_context is not None
    assert identity.delegation_context.delegate_subject_id == identity.subject_id


def test_delegated_subject_must_match_identity_subject() -> None:
    payload = valid_identity_payload()
    delegation = valid_delegation_payload()
    delegation["delegate_subject_id"] = "another-user"
    payload["delegation_context"] = delegation

    with pytest.raises(
        ValidationError,
        match="delegated subject must match identity subject",
    ):
        IdentityContext.model_validate(payload)


def test_delegation_cannot_outlive_identity() -> None:
    payload = valid_identity_payload()
    delegation = valid_delegation_payload()
    delegation["expires_at"] = AUTHENTICATED_AT + timedelta(hours=2)
    payload["delegation_context"] = delegation

    with pytest.raises(
        ValidationError,
        match="delegation cannot outlive identity context",
    ):
        IdentityContext.model_validate(payload)


def test_more_than_one_hundred_roles_are_rejected() -> None:
    payload = valid_identity_payload()
    payload["roles"] = [f"role-{index}" for index in range(101)]

    with pytest.raises(ValidationError):
        IdentityContext.model_validate(payload)


def test_identity_collections_are_immutable() -> None:
    identity = IdentityContext.model_validate(valid_identity_payload())

    with pytest.raises(AttributeError):
        identity.roles.append("administrator")  # type: ignore[attr-defined]

    assert identity.roles == ("incident-responder",)
