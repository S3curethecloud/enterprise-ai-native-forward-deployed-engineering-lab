"""Tests for validated correlation-ID handling."""

import re

import pytest

from incident_diagnostic_api.core.correlation import (
    CORRELATION_PATTERN,
    resolve_correlation_id,
)


@pytest.mark.parametrize(
    "candidate",
    [
        "client-trace-101",
        "req/trace:101",
        "tenant.service_request-1",
        "A",
        "x" * 128,
    ],
)
def test_valid_client_correlation_id_is_preserved(candidate: str) -> None:
    assert resolve_correlation_id(candidate) == candidate


def test_outer_whitespace_is_removed_from_valid_identifier() -> None:
    assert resolve_correlation_id("  client-trace-101  ") == "client-trace-101"


@pytest.mark.parametrize(
    "candidate",
    [
        None,
        "",
        " ",
        "contains spaces",
        "header\ninjection",
        "header\rinjection",
        "../relative",
        "identifier?query=true",
        "x" * 129,
    ],
)
def test_invalid_candidate_is_replaced(candidate: str | None) -> None:
    resolved = resolve_correlation_id(candidate)

    assert resolved.startswith("corr-")
    assert CORRELATION_PATTERN.fullmatch(resolved)


def test_generated_correlation_ids_are_unique() -> None:
    generated = {resolve_correlation_id(None) for _ in range(100)}

    assert len(generated) == 100


def test_generated_identifier_matches_bounded_contract() -> None:
    resolved = resolve_correlation_id(None)

    assert len(resolved) <= 128
    assert re.fullmatch(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$", resolved)
