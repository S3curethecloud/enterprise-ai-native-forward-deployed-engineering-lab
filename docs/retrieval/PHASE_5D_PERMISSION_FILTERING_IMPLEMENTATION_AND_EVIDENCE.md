# Phase 5D — Permission Filtering Implementation and Evidence

## 1. Purpose

This document records the locally verified implementation evidence for
Phase 5D tenant, service, classification, resource, source-type, and policy
lineage filtering.

Phase 5D extends deterministic keyword retrieval without granting the
retrieval component independent authorization authority.

## 2. Current Decision

```text
PHASE 5D LOCAL IMPLEMENTATION: PASSED
PHASE 5D IMPLEMENTATION COMMIT: AUTHORIZED
PHASE 5D REMOTE CI: PENDING
PHASE 5D CLOSURE: PENDING
PHASE 5E: NOT AUTHORIZED
```

Phase 5D cannot close until remote CI succeeds against its exact
implementation commit.

## 3. Authorized Scope Implemented

Phase 5D implemented:

- Explicit tenant scope in CT-03 policy constraints
- Explicit service scope in CT-03 policy constraints
- Explicit sensitivity scope in CT-03 policy constraints
- Required retrieval scope for allow and constrain decisions
- CT-03 authorization as an explicit retrieval input
- Request and policy lineage validation
- Source-resource intersection
- Source-type mapping
- Tenant filtering
- Service filtering
- Sensitivity filtering
- Active-lifecycle filtering
- Filtering before keyword scoring
- Policy-controlled maximum evidence count
- Controlled abstention for invalid or mismatched authority
- Fail-closed handling for unsupported source kinds
- Contract and retrieval tests

## 4. Prohibited Scope

Phase 5D does not implement or authorize:

- Enterprise evidence sources
- Corpus ingestion
- External databases
- Embeddings
- Vector retrieval
- Hybrid retrieval
- Reranking
- Context construction
- Prompt construction
- Model-provider calls
- Tool execution
- Human approval execution
- Retrieval API routes
- Infrastructure mutation
- Cloud deployment
- Production deployment

## 5. Artifact Inventory

Modified implementation artifacts:

- `src/incident_diagnostic_api/contracts/authorization.py`
- `src/incident_diagnostic_api/retrieval/keyword.py`

Modified test artifacts:

- `tests/contract/test_authorization_decision.py`
- `tests/contract/test_evidence_item.py`
- `tests/retrieval/test_keyword.py`

Evidence and gate artifacts:

- `docs/retrieval/PHASE_5D_PERMISSION_FILTERING_IMPLEMENTATION_AND_EVIDENCE.md`
- `docs/retrieval/PHASE_5D_PERMISSION_FILTERING_GATE.md`

Interview-learning artifact:

- `docs/interview-accelerator/phases/PHASE_05_PERMISSION_AWARE_RAG.md`

## 6. CT-03 Authority Extension

`PolicyConstraints` now carries these bounded retrieval scopes:

- `allowed_tenant_ids`
- `allowed_service_ids`
- `allowed_sensitivities`

A permitted retrieval decision must contain at least one allowed tenant,
service, sensitivity, and resource.

A denied decision may keep these allowed scopes empty.

The retrieval component consumes the decision. It does not create,
expand, or override policy authority.

## 7. Authority-Lineage Gate

Retrieval requires alignment across:

- Request identifier
- Trace identifier
- Subject identifier
- Policy-decision identifier
- Policy version
- Authorization expiration
- Authorization decision time
- Retrieval operation
- Policy outcome

A mismatch results in controlled abstention with
`AUTHORIZATION_MISSING`.

## 8. Resource Intersection

The effective source scope is the intersection of:

- Source identifiers requested by `RetrievalQuery`
- Resource identifiers permitted by `AuthorizationDecision`

A source requested by the query but absent from the policy decision is
not searchable.

A source permitted by policy but absent from the request is also not
searched.

## 9. Source-Type Mapping

The bounded Phase 5D mapping is:

| Evidence source kind | CT-03 source type |
|---|---|
| `runbook` | `runbook` |
| `service_catalog` | `service_metadata` |

These evidence kinds have no Phase 5D CT-03 mapping and therefore fail
closed:

- `change_record`
- `incident_history`
- `observability_summary`

## 10. Tenant, Service, and Classification Filtering

A chunk is eligible only when:

- Its tenant equals the query tenant
- The query tenant is allowed by CT-03
- Its service set contains the query service
- The query service is allowed by CT-03
- Its sensitivity is allowed by CT-03
- Its source identifier is in the effective resource intersection
- Its source kind is requested and mapped to an allowed CT-03 source type
- Its lifecycle status is active

All checks occur before keyword scoring.

## 11. Filter-Before-Score Evidence

The implementation calls `_authorized_active_chunks()` before constructing
`scored_chunks`.

A monkeypatch test replaces `calculate_keyword_score()` with a function
that raises immediately.

When tenant scope rejects the corpus, retrieval abstains without invoking
the scorer. This provides executable evidence that unauthorized content
does not enter relevance scoring.

## 12. Policy Result Limit

The final candidate count is bounded by the smaller of:

- `RetrievalQuery.max_candidates`
- `PolicyConstraints.max_evidence_items`

The query cannot enlarge the evidence count beyond the policy maximum.

## 13. Controlled Abstention

Phase 5D returns controlled abstention when:

- Authority lineage is inconsistent
- Authority is expired
- The policy outcome is denied
- No source remains after permission filtering
- No authorized evidence meets the keyword threshold

The retrieval component does not broaden scope to avoid abstention.

## 14. Local Test Evidence

Local Phase 5D evidence:

```text
Authorization and evidence contract tests: 40 passed
Focused contract and retrieval tests: 126 passed
Keyword tests: 26 passed
Complete repository tests: 776 passed
Ruff linting: Passed
Ruff formatting: Passed
Strict mypy checking: Passed
Dependency check: Passed
Git diff check: Passed
```

## 15. Capability-Boundary Evidence

The Phase 5D source boundary contains no:

- Provider SDK
- External network client
- Vector database
- Embedding implementation
- Reranker
- Tool executor
- Shell execution
- Infrastructure client
- Cloud deployment logic

Phase 5D remains local, synthetic, deterministic, read-only, and
fail-closed.

## 16. Residual Risks

The following remain deliberately unresolved:

- Local deterministic embeddings
- Vector-retrieval quality
- Hybrid score fusion
- Reranking quality
- Context-window construction
- Token budgeting
- Prompt-injection controls
- Retrieval-contamination controls
- Citation verification
- Retrieval telemetry
- Runtime API integration
- Enterprise identity-provider integration
- Enterprise data-source integration
- Persistent storage
- Production-scale performance

These are later gated concerns and are not Phase 5D claims.

## 17. Remote CI Requirement

Phase 5D closure requires:

1. An exact implementation commit.
2. A remote Phase 4 CI run against that exact commit.
3. Successful Python quality and contract-test execution.
4. Successful container build and health verification.
5. Recorded commit and run identifiers.
6. A separate closure commit if closure evidence changes tracked files.

Until that evidence exists:

```text
PHASE 5D REMOTE CI: PENDING
PHASE 5D CLOSURE: PENDING
PHASE 5E: NOT AUTHORIZED
```

## 18. Current Exit Posture

```text
PHASE 5D LOCAL GATE: PASSED
PHASE 5D IMPLEMENTATION COMMIT: AUTHORIZED
PHASE 5D REMOTE CI: REQUIRED
PHASE 5D CLOSURE: PENDING
PHASE 5E LOCAL EMBEDDINGS AND VECTOR RETRIEVAL: NOT AUTHORIZED
ENTERPRISE RETRIEVAL: NOT AUTHORIZED
EXTERNAL PROVIDERS: NOT AUTHORIZED
TOOL EXECUTION: NOT AUTHORIZED
CLOUD DEPLOYMENT: NOT AUTHORIZED
PRODUCTION DEPLOYMENT: NOT AUTHORIZED
```
