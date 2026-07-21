# Phase 5D — Permission Filtering Gate

## 1. Gate Purpose

This gate determines whether Phase 5D tenant, service, classification,
resource, source-type, and authority-lineage filtering is locally complete
and ready for an implementation commit.

## 2. Current Gate Decision

```text
LOCAL QUALITY GATE: PASSED
LOCAL AUTHORITY GATE: PASSED
IMPLEMENTATION COMMIT: f3e654da813f4b5bbfd42d5b5cdbc9e14980d1ae
REMOTE IMPLEMENTATION CI: PASSED — RUN 29805548139
PHASE 5D CLOSURE: PENDING CLOSURE-COMMIT CI
PHASE 5E: AUTHORIZED ONLY AFTER CLOSURE-COMMIT CI
```

## 3. Evaluated Scope

This gate evaluates:

- CT-03 retrieval-scope constraints
- Required scope for permitted retrieval
- Explicit authorization input
- Authority-lineage validation
- Source-resource intersection
- Source-type mapping
- Tenant filtering
- Service filtering
- Sensitivity filtering
- Active-lifecycle filtering
- Filter-before-score behavior
- Policy candidate limits
- Controlled abstention
- Fail-closed unsupported source kinds
- Test and capability boundaries

## 4. Prohibited Scope

This gate does not authorize:

- Enterprise data
- Enterprise-source connectors
- Corpus ingestion
- Embeddings
- Vector retrieval
- Hybrid retrieval
- Reranking
- Context construction
- Prompt construction
- External model providers
- Tool execution
- Human approval execution
- Retrieval API routes
- Infrastructure mutation
- Cloud deployment
- Production deployment

## 5. Artifact Gate

Required implementation artifacts exist:

- `src/incident_diagnostic_api/contracts/authorization.py`
- `src/incident_diagnostic_api/retrieval/keyword.py`

Required test artifacts exist:

- `tests/contract/test_authorization_decision.py`
- `tests/contract/test_evidence_item.py`
- `tests/retrieval/test_keyword.py`

Required evidence artifact exists:

- `docs/retrieval/PHASE_5D_PERMISSION_FILTERING_IMPLEMENTATION_AND_EVIDENCE.md`

Artifact gate:

```text
PASSED
```

## 6. CT-03 Authority Gate

Verified:

- Tenant scope is represented in policy constraints
- Service scope is represented in policy constraints
- Sensitivity scope is represented in policy constraints
- Permitted retrieval requires all three scopes
- Permitted retrieval requires an allowed resource
- Denied retrieval may carry empty allowed scopes
- Policy constraints are immutable

Decision:

```text
PASSED
```

## 7. Authority-Lineage Gate

Verified alignment:

- Request identifier
- Trace identifier
- Subject identifier
- Policy-decision identifier
- Policy version
- Expiration
- Decision time
- Retrieval operation
- Policy outcome

Mismatched or denied authority produces controlled abstention.

Decision:

```text
PASSED
```

## 8. Resource and Source-Type Gate

Verified:

- Query source identifiers do not authorize retrieval
- Policy resource identifiers do not independently initiate retrieval
- The effective scope is their intersection
- Runbooks map to CT-03 runbooks
- Service catalogs map to CT-03 service metadata
- Change records fail closed
- Incident history fails closed
- Observability summaries fail closed

Decision:

```text
PASSED
```

## 9. Tenant Gate

Verified:

- Query tenant must be allowed by CT-03
- Chunk tenant must equal query tenant
- A tenant mismatch removes the chunk before scoring
- No cross-tenant fallback occurs

Decision:

```text
PASSED
```

## 10. Service Gate

Verified:

- Query service must be allowed by CT-03
- Chunk service metadata must include the query service
- A service mismatch removes the chunk before scoring
- No cross-service fallback occurs

Decision:

```text
PASSED
```

## 11. Classification Gate

Verified:

- Chunk sensitivity must be allowed by CT-03
- Public, internal, confidential, and restricted remain typed values
- A sensitivity mismatch removes the chunk before scoring
- The retrieval component cannot downgrade classification

Decision:

```text
PASSED
```

## 12. Filter-Before-Score Gate

Verified execution order:

1. Validate authority lineage.
2. Intersect request and policy source scope.
3. Apply source-type mapping.
4. Apply tenant scope.
5. Apply service scope.
6. Apply sensitivity scope.
7. Apply lifecycle scope.
8. Score remaining chunks.
9. Rank remaining candidates.
10. Apply the policy result limit.

A monkeypatch test proves rejected content never reaches the scoring
function.

Decision:

```text
PASSED
```

## 13. Result-Limit and Abstention Gate

Verified:

- Policy maximum overrides a larger query maximum
- Candidate ranks remain contiguous
- Invalid authority produces `AUTHORIZATION_MISSING`
- Empty effective scope produces `NO_AUTHORIZED_SOURCES`
- Empty relevance results produce controlled abstention
- Retrieval does not broaden authority to produce a result

Decision:

```text
PASSED
```

## 14. Test Gate

Verified local results:

```text
Authorization and evidence contract tests: 40 passed
Focused contract and retrieval tests: 126 passed
Keyword tests: 26 passed
Complete repository tests: 776 passed
```

Quality results:

```text
Ruff linting: Passed
Ruff formatting: Passed
Strict mypy checking: Passed
Dependency check: Passed
Git diff check: Passed
```

Decision:

```text
PASSED
```

## 15. Capability-Boundary Gate

Verified absent:

- Provider SDKs
- Provider calls
- Network clients
- Vector stores
- Embedding engines
- Rerankers
- Tool execution
- Shell execution
- Infrastructure clients
- Deployment capability

Decision:

```text
PASSED
```

## 16. Phase 5E Boundary

Phase 5E is:

```text
LOCAL DETERMINISTIC EMBEDDINGS AND VECTOR RETRIEVAL
```

Phase 5E remains unauthorized until:

1. Phase 5D is committed.
2. Remote CI succeeds against the exact Phase 5D implementation commit.
3. Phase 5D implementation evidence records that run.
4. A closure commit is created if required.
5. Closure-commit CI succeeds.
6. Phase 5E authority is explicitly recorded.

## 17. Remote CI Gate

Verified implementation CI:

```text
IMPLEMENTATION COMMIT:
f3e654da813f4b5bbfd42d5b5cdbc9e14980d1ae

CI RUN:
29805548139

STATUS:
COMPLETED

CONCLUSION:
SUCCESS

Run URL:

29805548139

Verified jobs:

Python quality and contract tests: Passed
Local container build and health verification: Passed

The CI run executed the exact Phase 5D implementation commit.

Remaining gate:

PHASE 5D CLOSURE-EVIDENCE COMMIT: REQUIRED
PHASE 5D CLOSURE-COMMIT CI: REQUIRED
PHASE 5E: NOT YET AVAILABLE
```

## 18. Residual Risks

Residual risks include:

- No vector similarity behavior
- No embedding-quality evidence
- No hybrid score fusion
- No reranking evidence
- No context-window construction
- No prompt-injection defense
- No retrieval-contamination defense
- No enterprise identity integration
- No enterprise data integration
- No persistent retrieval store
- No production-scale load evidence

These risks remain outside the Phase 5D claim.

## 19. Final Local Decision

```text
PHASE 5D LOCAL GATE: PASSED
PHASE 5D IMPLEMENTATION COMMIT: f3e654da813f4b5bbfd42d5b5cdbc9e14980d1ae
PHASE 5D IMPLEMENTATION CI: PASSED — RUN 29805548139
PHASE 5D CLOSURE: PENDING CLOSURE-COMMIT CI
PHASE 5E: AUTHORIZED ONLY AFTER CLOSURE-COMMIT CI
ENTERPRISE RETRIEVAL: NOT AUTHORIZED
VECTOR RETRIEVAL: NOT YET AVAILABLE
EXTERNAL PROVIDERS: NOT AUTHORIZED
TOOL EXECUTION: NOT AUTHORIZED
CLOUD DEPLOYMENT: NOT AUTHORIZED
PRODUCTION DEPLOYMENT: NOT AUTHORIZED
```
