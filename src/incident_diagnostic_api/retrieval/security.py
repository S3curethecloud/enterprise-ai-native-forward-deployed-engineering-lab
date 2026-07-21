"""Shared fail-closed authorization controls for retrieval methods."""

from typing import Final

from incident_diagnostic_api.contracts import AuthorizationDecision
from incident_diagnostic_api.contracts.common import Timestamp
from incident_diagnostic_api.contracts.enums import (
    PolicyOperation,
    PolicyOutcome,
    SourceType,
)
from incident_diagnostic_api.retrieval.corpus import SyntheticEvidenceCorpus
from incident_diagnostic_api.retrieval.enums import (
    EvidenceLifecycleStatus,
    EvidenceSourceKind,
    RetrievalAbstentionCode,
    RetrievalDisposition,
)
from incident_diagnostic_api.retrieval.models import (
    EvidenceChunk,
    RetrievalAbstention,
    RetrievalQuery,
    RetrievalResult,
)

_SOURCE_TYPE_BY_KIND: Final[dict[EvidenceSourceKind, SourceType]] = {
    EvidenceSourceKind.RUNBOOK: SourceType.RUNBOOK,
    EvidenceSourceKind.SERVICE_CATALOG: SourceType.SERVICE_METADATA,
}


def authorization_matches_query(
    *,
    authorization: AuthorizationDecision,
    query: RetrievalQuery,
    completed_at: Timestamp,
) -> bool:
    """Return whether CT-03 authority matches this retrieval request."""

    return (
        authorization.operation is PolicyOperation.RETRIEVE_RUNBOOK_EVIDENCE
        and authorization.outcome
        in {
            PolicyOutcome.ALLOW,
            PolicyOutcome.CONSTRAIN,
        }
        and authorization.request_id == query.request_id
        and authorization.trace_id == query.trace_id
        and authorization.subject_id == query.subject_id
        and authorization.policy_decision_id == query.policy_decision_id
        and authorization.policy_version == query.policy_version
        and authorization.expires_at == query.authorization_expires_at
        and authorization.decided_at <= query.requested_at
        and completed_at < authorization.expires_at
    )


def authorized_active_chunks(
    corpus: SyntheticEvidenceCorpus,
    query: RetrievalQuery,
    authorization: AuthorizationDecision,
) -> tuple[EvidenceChunk, ...]:
    """Apply CT-03 security trimming before retrieval scoring."""

    allowed_source_ids = frozenset(query.allowed_source_ids) & frozenset(
        authorization.allowed_resource_ids
    )
    allowed_source_kinds = frozenset(query.allowed_source_kinds)
    allowed_source_types = frozenset(authorization.constraints.allowed_source_types)
    allowed_tenant_ids = frozenset(authorization.constraints.allowed_tenant_ids)
    allowed_service_ids = frozenset(authorization.constraints.allowed_service_ids)
    allowed_sensitivities = frozenset(authorization.constraints.allowed_sensitivities)

    return tuple(
        chunk
        for chunk in corpus.chunks
        if chunk.source_id in allowed_source_ids
        and chunk.source_kind in allowed_source_kinds
        and _SOURCE_TYPE_BY_KIND.get(chunk.source_kind) in allowed_source_types
        and query.tenant_id in allowed_tenant_ids
        and chunk.tenant_id == query.tenant_id
        and query.service_id in allowed_service_ids
        and query.service_id in chunk.service_ids
        and chunk.sensitivity in allowed_sensitivities
        and chunk.lifecycle_status is EvidenceLifecycleStatus.ACTIVE
    )


def build_abstention_result(
    *,
    query: RetrievalQuery,
    code: RetrievalAbstentionCode,
    safe_message: str,
    sources_searched: int,
    authorized_source_count: int,
    completed_at: Timestamp,
) -> RetrievalResult:
    """Return one explicit, correlated abstention result."""

    abstention = RetrievalAbstention(
        request_id=query.request_id,
        trace_id=query.trace_id,
        code=code,
        reason_codes=(code.value,),
        sources_searched=sources_searched,
        authorized_source_count=authorized_source_count,
        candidate_count=0,
        safe_message=safe_message,
        occurred_at=completed_at,
    )

    return RetrievalResult(
        request_id=query.request_id,
        trace_id=query.trace_id,
        query=query,
        disposition=RetrievalDisposition.ABSTENTION,
        candidates=(),
        abstention=abstention,
        completed_at=completed_at,
    )
