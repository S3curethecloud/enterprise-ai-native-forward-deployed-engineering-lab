"""Public contracts for bounded permission-aware retrieval."""

from incident_diagnostic_api.retrieval.corpus import (
    SyntheticEvidenceCorpus,
    calculate_content_hash,
)
from incident_diagnostic_api.retrieval.enums import (
    EvidenceLifecycleStatus,
    EvidenceSourceKind,
    RetrievalAbstentionCode,
    RetrievalDisposition,
    RetrievalMethod,
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

__all__ = [
    "Citation",
    "EvidenceChunk",
    "EvidenceDocument",
    "EvidenceLifecycleStatus",
    "EvidenceSource",
    "EvidenceSourceKind",
    "RetrievalAbstention",
    "RetrievalAbstentionCode",
    "RetrievalCandidate",
    "RetrievalDisposition",
    "RetrievalMethod",
    "RetrievalQuery",
    "RetrievalResult",
    "SyntheticEvidenceCorpus",
    "calculate_content_hash",
    "calculate_keyword_score",
    "retrieve_keywords",
    "tokenize_keywords",
]
