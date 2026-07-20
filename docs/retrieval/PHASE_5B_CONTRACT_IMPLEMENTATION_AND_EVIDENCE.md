# Phase 5B — Typed Retrieval Contracts: Implementation and Evidence

## 1. Purpose

Phase 5B implements the immutable contract boundary for future
permission-aware retrieval.

It does not implement retrieval execution.

## 2. Current Decision

```text
PHASE 5B LOCAL IMPLEMENTATION: COMPLETE
REMOTE CI EVIDENCE: PASSED
PHASE 5B CLOSURE: COMPLETE
```

## 3. Authorized Scope

Phase 5B authorized only:

- Retrieval enumerations
- Immutable evidence-source contracts
- Immutable evidence-document contracts
- Immutable evidence-chunk contracts
- Authorized retrieval-query contracts
- Citation and provenance contracts
- Ranked retrieval-candidate contracts
- Explicit abstention contracts
- Mutually exclusive retrieval-result contracts
- Contract validation tests
- Interview-guide updates derived from implementation

## 4. Prohibited Scope

Phase 5B did not authorize or implement:

- Evidence ingestion
- A document corpus
- Enterprise data access
- Keyword search execution
- Vector search execution
- Embedding generation
- Reranking
- Context construction
- Prompt construction
- Provider calls
- Retrieval API routes
- Tool execution
- Network access
- Infrastructure mutation
- Cloud deployment
- Production deployment

## 5. Artifact Inventory

Runtime contract artifacts:

```text
src/incident_diagnostic_api/retrieval/__init__.py
src/incident_diagnostic_api/retrieval/enums.py
src/incident_diagnostic_api/retrieval/models.py
```

Test artifacts:

```text
tests/retrieval/__init__.py
tests/retrieval/test_contracts.py
```

## 6. Enumeration Inventory

| Enumeration | Members |
|---|---:|
| Evidence source kinds | 5 |
| Evidence lifecycle statuses | 2 |
| Retrieval methods | 3 |
| Retrieval dispositions | 2 |
| Retrieval abstention codes | 7 |

The retrieval-method enumeration describes allowable contract values. It
does not provide keyword, vector, or hybrid retrieval behavior.

## 7. Contract Inventory

Phase 5B implements eight immutable contracts:

- EvidenceSource
- EvidenceDocument
- EvidenceChunk
- RetrievalQuery
- Citation
- RetrievalCandidate
- RetrievalAbstention
- RetrievalResult

## 8. Contract Invariants

The contracts enforce:

- Source ownership and tenant metadata
- Explicit service scope
- Explicit sensitivity classification
- Document version and content integrity
- Active-versus-tombstoned lifecycle consistency
- Valid effective, ingestion, expiry, and tombstone timelines
- Live authorization at query creation
- Complete and ordered optional time windows
- Bounded candidate counts
- Citation-to-candidate provenance alignment
- Candidate-to-query policy lineage
- Candidate source allowlisting
- Ordered and contiguous candidate ranks
- Candidate-versus-abstention outcome exclusivity
- Request and trace correlation
- Immutable fields and collections
- Rejection of unknown fields

## 9. Outcome Exclusivity

A retrieval result has exactly one outcome shape:

- A non-empty ordered candidate collection with no abstention, or
- An empty candidate collection with one explicit abstention

This prevents ambiguous results that simultaneously claim success and
failure.

## 10. Provenance Alignment

A candidate must preserve the same:

- Source identifier
- Document identifier
- Document version
- Chunk identifier

as its citation.

The candidate must also preserve the request, trace, and policy-decision
lineage established by the query.

## 11. Contiguous Ranking

Accepted candidate ranks must be:

- Unique
- Ordered
- One-based
- Contiguous

For three candidates, the only accepted rank sequence is:

```text
1, 2, 3
```

Sequences such as `2`, `1, 1`, or `1, 3` fail validation.

## 12. Local Quality Evidence

Local validation produced:

- Ruff lint: passed
- Ruff format: passed
- Mypy: passed
- Retrieval contract tests: 37 passed
- Complete repository tests: 723 passed
- Git diff check: passed

## 13. Authority-Boundary Evidence

The Phase 5B source and tests contain no implementation dependency or
capability for:

- External model providers
- Vector databases
- Embedding frameworks
- Reranking frameworks
- HTTP clients
- Socket access
- Subprocess execution
- Cloud SDKs
- Kubernetes
- Terraform

Result:

```text
PASS: no provider, vector-store, network, tool, or infrastructure
capability detected
```

## 14. Security Posture

Phase 5B is fail-closed because:

- Retrieval authority must be represented explicitly.
- Authorization expiry is validated.
- Candidate sources must appear in the query allowlist.
- Citation lineage cannot silently diverge.
- Unknown fields are rejected.
- Invalid outcomes cannot be represented as valid results.
- Missing or unsuitable evidence can be represented as abstention.
- The contract layer has no authority to retrieve or execute anything.

## 15. Remote CI Evidence

Recorded implementation evidence:

- Implementation commit: `efd62671b27e725d2936a2c7ae3a1a0d24b06ca6`
- Exact-commit CI run: [`29780263857`](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29780263857)
- CI conclusion: Success
- Python quality and contract tests: Passed
- Local container build and health verification: Passed
- CI head SHA matched the Phase 5B implementation commit
- Remote synchronization: Passed

## 16. Current Exit Posture

```text
PHASE 5A: COMPLETE
PHASE 5B LOCAL IMPLEMENTATION: COMPLETE
PHASE 5B REMOTE CI: PASSED
PHASE 5B CLOSURE: COMPLETE
PHASE 5C: AUTHORIZED AFTER CLOSURE-COMMIT CI
PHASE 5C SCOPE: SYNTHETIC CORPUS AND DETERMINISTIC KEYWORD RETRIEVAL
ENTERPRISE RETRIEVAL: NOT AUTHORIZED
VECTOR RETRIEVAL: NOT AUTHORIZED
```
