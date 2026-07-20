"""Bounded enumerations for Phase 5 retrieval contracts."""

from enum import StrEnum


class EvidenceSourceKind(StrEnum):
    """Synthetic evidence-source categories supported by Phase 5."""

    RUNBOOK = "runbook"
    SERVICE_CATALOG = "service_catalog"
    CHANGE_RECORD = "change_record"
    INCIDENT_HISTORY = "incident_history"
    OBSERVABILITY_SUMMARY = "observability_summary"


class EvidenceLifecycleStatus(StrEnum):
    """Lifecycle state of a versioned evidence artifact."""

    ACTIVE = "active"
    TOMBSTONED = "tombstoned"


class RetrievalMethod(StrEnum):
    """Bounded retrieval methods planned by the Phase 5 design."""

    KEYWORD = "keyword"
    VECTOR = "vector"
    HYBRID = "hybrid"


class RetrievalDisposition(StrEnum):
    """Possible top-level outcomes of a retrieval request."""

    CANDIDATES = "candidates"
    ABSTENTION = "abstention"


class RetrievalAbstentionCode(StrEnum):
    """Controlled reasons for returning no retrieval context."""

    NO_AUTHORIZED_SOURCES = "NO_AUTHORIZED_SOURCES"
    NO_RELEVANT_EVIDENCE = "NO_RELEVANT_EVIDENCE"
    EVIDENCE_STALE = "EVIDENCE_STALE"
    REQUIRED_SOURCE_MISSING = "REQUIRED_SOURCE_MISSING"
    EVIDENCE_CONFLICT = "EVIDENCE_CONFLICT"
    AUTHORIZATION_MISSING = "AUTHORIZATION_MISSING"
    INTEGRITY_FAILURE = "INTEGRITY_FAILURE"
