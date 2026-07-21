"""Versioned deterministic local embeddings for synthetic evidence."""

from hashlib import sha256
from math import sqrt
from typing import Final

from incident_diagnostic_api.retrieval.keyword import tokenize_keywords

EMBEDDING_VERSION: Final[str] = "deterministic-feature-hash-v1"
EMBEDDING_DIMENSIONS: Final[int] = 256

EmbeddingVector = tuple[float, ...]


def embed_text(text: str) -> EmbeddingVector:
    """Return a normalized deterministic feature-hash vector."""

    values = [0.0] * EMBEDDING_DIMENSIONS

    for token in tokenize_keywords(text):
        digest = sha256(f"{EMBEDDING_VERSION}:{token}".encode()).digest()
        dimension = int.from_bytes(digest[:8], "big") % EMBEDDING_DIMENSIONS
        direction = 1.0 if digest[8] % 2 == 0 else -1.0
        values[dimension] += direction

    magnitude = sqrt(sum(value * value for value in values))

    if magnitude == 0.0:
        return tuple(values)

    return tuple(value / magnitude for value in values)


def cosine_similarity(
    left: EmbeddingVector,
    right: EmbeddingVector,
) -> float:
    """Return cosine similarity for equal fixed-dimensional vectors."""

    if len(left) != EMBEDDING_DIMENSIONS:
        raise ValueError("left vector does not match the embedding dimension")

    if len(right) != EMBEDDING_DIMENSIONS:
        raise ValueError("right vector does not match the embedding dimension")

    left_magnitude = sqrt(sum(value * value for value in left))
    right_magnitude = sqrt(sum(value * value for value in right))

    if left_magnitude == 0.0 or right_magnitude == 0.0:
        return 0.0

    dot_product = sum(
        left_value * right_value
        for left_value, right_value in zip(
            left,
            right,
            strict=True,
        )
    )
    similarity = dot_product / (left_magnitude * right_magnitude)

    return max(-1.0, min(1.0, similarity))
