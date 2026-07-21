"""Tests for deterministic local Phase 5E embeddings."""

from math import isclose, sqrt

import pytest

from incident_diagnostic_api.retrieval.embeddings import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_VERSION,
    cosine_similarity,
    embed_text,
)


def vector_magnitude(vector: tuple[float, ...]) -> float:
    """Return the Euclidean magnitude of a test vector."""

    return sqrt(sum(value * value for value in vector))


def test_embedding_version_is_explicit() -> None:
    assert EMBEDDING_VERSION == "deterministic-feature-hash-v1"


def test_embedding_dimension_is_fixed() -> None:
    assert EMBEDDING_DIMENSIONS == 256
    assert len(embed_text("payment queue")) == 256


def test_embedding_is_deterministic() -> None:
    assert embed_text("payment queue") == embed_text("payment queue")


def test_embedding_is_case_normalized() -> None:
    assert embed_text("Payment QUEUE") == embed_text("payment queue")


def test_embedding_is_token_order_independent() -> None:
    assert embed_text("payment queue") == embed_text("queue payment")


def test_embedding_uses_unique_tokens() -> None:
    assert embed_text("payment payment queue") == embed_text("payment queue")


def test_empty_token_stream_returns_zero_vector() -> None:
    assert embed_text("!!!") == (0.0,) * EMBEDDING_DIMENSIONS


def test_nonempty_embedding_is_unit_normalized() -> None:
    vector = embed_text("payment queue worker")

    assert isclose(vector_magnitude(vector), 1.0)


def test_identical_vectors_have_unit_similarity() -> None:
    vector = embed_text("payment queue worker")

    assert isclose(cosine_similarity(vector, vector), 1.0)


def test_partial_overlap_scores_above_unrelated_text() -> None:
    query = embed_text("payment queue worker")
    partial = embed_text("payment worker")
    unrelated = embed_text("database latency")

    assert cosine_similarity(query, partial) > cosine_similarity(
        query,
        unrelated,
    )


def test_cosine_similarity_is_symmetric() -> None:
    left = embed_text("payment queue")
    right = embed_text("queue worker")

    assert isclose(
        cosine_similarity(left, right),
        cosine_similarity(right, left),
    )


def test_zero_vector_similarity_is_zero() -> None:
    zero = (0.0,) * EMBEDDING_DIMENSIONS
    vector = embed_text("payment queue")

    assert cosine_similarity(zero, vector) == 0.0
    assert cosine_similarity(vector, zero) == 0.0


def test_opposite_vectors_have_negative_unit_similarity() -> None:
    left = (1.0,) + (0.0,) * (EMBEDDING_DIMENSIONS - 1)
    right = (-1.0,) + (0.0,) * (EMBEDDING_DIMENSIONS - 1)

    assert isclose(cosine_similarity(left, right), -1.0)


def test_left_dimension_mismatch_is_rejected() -> None:
    right = embed_text("payment")

    with pytest.raises(
        ValueError,
        match="left vector does not match",
    ):
        cosine_similarity((1.0,), right)


def test_right_dimension_mismatch_is_rejected() -> None:
    left = embed_text("payment")

    with pytest.raises(
        ValueError,
        match="right vector does not match",
    ):
        cosine_similarity(left, (1.0,))
