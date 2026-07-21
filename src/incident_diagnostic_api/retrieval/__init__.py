"""Public contracts for bounded permission-aware retrieval."""

from incident_diagnostic_api.retrieval.corpus import (
    SyntheticEvidenceCorpus,
    calculate_content_hash,
)
from incident_diagnostic_api.retrieval.embeddings import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_VERSION,
    EmbeddingVector,
    cosine_similarity,
    embed_text,
)
from incident_diagnostic_api.retrieval.enums import (
    EvidenceLifecycleStatus,
    EvidenceSourceKind,
    RetrievalAbstentionCode,
    RetrievalDisposition,
    RetrievalMethod,
)
from incident_diagnostic_api.retrieval.hybrid import (
    HybridRetrievalConfig,
    calculate_hybrid_score,
    calculate_reciprocal_rank_score,
    normalize_candidate_scores,
    retrieve_hybrid,
)
from incident_diagnostic_api.retrieval.keyword import (
    calculate_keyword_score,
    retrieve_keywords,
    tokenize_keywords,
)
from incident_diagnostic_api.retrieval.models import (
    Citation,
    EvidenceChunk,
    EvidenceDocument,
    EvidenceSource,
    RetrievalAbstention,
    RetrievalCandidate,
    RetrievalQuery,
    RetrievalResult,
)
from incident_diagnostic_api.retrieval.vector import (
    VECTOR_INDEX_VERSION,
    SyntheticVectorIndex,
    VectorIndexEntry,
    build_vector_index,
    retrieve_vectors,
)

__all__ = [
    "EMBEDDING_DIMENSIONS",
    "EMBEDDING_VERSION",
    "VECTOR_INDEX_VERSION",
    "Citation",
    "EmbeddingVector",
    "EvidenceChunk",
    "EvidenceDocument",
    "EvidenceLifecycleStatus",
    "EvidenceSource",
    "EvidenceSourceKind",
    "HybridRetrievalConfig",
    "RetrievalAbstention",
    "RetrievalAbstentionCode",
    "RetrievalCandidate",
    "RetrievalDisposition",
    "RetrievalMethod",
    "RetrievalQuery",
    "RetrievalResult",
    "SyntheticEvidenceCorpus",
    "SyntheticVectorIndex",
    "VectorIndexEntry",
    "build_vector_index",
    "calculate_content_hash",
    "calculate_hybrid_score",
    "calculate_keyword_score",
    "calculate_reciprocal_rank_score",
    "cosine_similarity",
    "embed_text",
    "normalize_candidate_scores",
    "retrieve_hybrid",
    "retrieve_keywords",
    "retrieve_vectors",
    "tokenize_keywords",
]
