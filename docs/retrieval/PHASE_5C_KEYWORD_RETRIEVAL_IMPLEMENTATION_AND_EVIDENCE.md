# Phase 5C — Synthetic Corpus and Keyword Retrieval Evidence

## 1. Purpose

Phase 5C implements deterministic read-only keyword retrieval over
immutable synthetic evidence.

It does not implement enterprise retrieval, semantic retrieval, vector
retrieval, embeddings, hybrid retrieval, or reranking.

## 2. Current Decision

```text
PHASE 5C LOCAL IMPLEMENTATION: COMPLETE
PHASE 5C REMOTE CI: PENDING
PHASE 5C CLOSURE: PENDING
PHASE 5D: NOT AUTHORIZED
```

## 3. Authorized Scope Implemented

Phase 5C implements:

- Immutable bounded synthetic corpus
- Source, document, and chunk lineage validation
- SHA-256 content-integrity validation
- Deterministic keyword tokenization
- Deterministic overlap scoring
- Source identifier and source-kind allowlisting
- Tombstone exclusion
- Authorization-expiry abstention
- Minimum-score enforcement
- Maximum-candidate enforcement
- Stable deterministic tie-breaking
- Citation construction
- Explicit abstention
- Unit and contract tests

## 4. Prohibited Scope

Phase 5C does not implement or authorize:

- Enterprise evidence sources
- Production data
- External ingestion
- Tenant filtering
- Service filtering
- Classification filtering
- Vector retrieval
- Embeddings
- Hybrid retrieval
- Reranking
- Context construction
- Prompt construction
- Model-provider calls
- Tool execution
- Retrieval API routes
- Network access
- Infrastructure mutation
- Cloud deployment
- Production deployment

Tenant, service, and classification filtering remain Phase 5D work.

## 5. Artifact Inventory

Source artifacts:

- `src/incident_diagnostic_api/retrieval/corpus.py`
- `src/incident_diagnostic_api/retrieval/keyword.py`
- `src/incident_diagnostic_api/retrieval/__init__.py`

Test artifacts:

- `tests/retrieval/test_corpus.py`
- `tests/retrieval/test_keyword.py`

## 6. Synthetic Corpus Contract

`SyntheticEvidenceCorpus` provides an immutable bounded collection of:

- Evidence sources
- Evidence documents
- Evidence chunks

The contract requires:

- Unique source identifiers
- Unique document identifiers
- Unique chunk identifiers
- Every document to reference a corpus source
- Every chunk to reference a corpus document
- Source, document, and chunk metadata alignment
- Document and chunk lifecycle alignment
- Valid SHA-256 content hashes

## 7. Content-Addressed Integrity

`calculate_content_hash` computes a deterministic SHA-256 hash over the
exact UTF-8 evidence content.

The corpus rejects a document or chunk when its declared hash does not
match its content.

This detects silent evidence modification inside the bounded synthetic
corpus. It is not a digital-signature or external trust service.

## 8. Keyword Normalization

`tokenize_keywords`:

- Applies Unicode-aware case folding
- Extracts lowercase ASCII alphanumeric tokens
- Removes duplicate tokens
- Sorts tokens deterministically

Equivalent text therefore produces the same normalized token tuple.

## 9. Keyword Scoring

`calculate_keyword_score` uses:

```text
unique matching query tokens / unique query tokens
```

The score is deterministic and bounded from zero to one.

It is a lexical overlap score. It is not semantic similarity,
probabilistic relevance, an embedding score, or a reranker score.

## 10. Pre-Scoring Source Scope

Before scoring, Phase 5C limits eligible chunks to:

- Allowed source identifiers
- Allowed source kinds
- Active lifecycle status

This is a narrow source-scope boundary.

Phase 5C does not claim the tenant, service, or classification filtering
reserved for Phase 5D.

## 11. Deterministic Ranking

Eligible candidates are ordered by:

1. Descending keyword score
2. Source identifier
3. Document identifier
4. Chunk index
5. Chunk identifier

This creates stable tie-breaking independent of corpus insertion order.

Accepted candidates receive contiguous one-based ranks.

## 12. Explicit Abstention

Phase 5C returns an abstention when:

- Execution authority has expired
- A query contains no searchable keywords
- No active source is authorized
- No evidence meets the relevance threshold

An abstention preserves request and trace correlation and returns no
candidate evidence.

## 13. Read-Only Behavior

Retrieval does not mutate:

- The synthetic corpus
- Evidence metadata
- The retrieval query
- Authorization lineage

The same corpus, query, and completion time produce the same serialized
result.

## 14. Local Test Evidence

Observed results:

```text
Corpus tests: 23 passed
Keyword retrieval tests: 16 passed
All retrieval tests: 76 passed
Complete repository tests: 762 passed
Ruff lint: passed
Ruff format: passed
Mypy: passed
Dependency check: passed
Git diff check: passed
```

## 15. Capability-Boundary Evidence

The Phase 5C capability scan found no dependency or implementation for:

- Vector databases
- Embedding frameworks
- Reranking frameworks
- External model providers
- HTTP clients
- Socket access
- Subprocess execution
- Cloud SDKs
- Kubernetes
- Terraform

Result:

```text
PASS: no vector, provider, network, tool, or infrastructure capability
detected
```

## 16. Residual Risks

Phase 5C intentionally leaves these capabilities unresolved:

- Tenant isolation enforcement
- Service-scope enforcement
- Classification enforcement
- Freshness evaluation
- Vector relevance
- Hybrid ranking
- Reranking
- Context assembly
- Prompt-injection controls
- Retrieval evaluation datasets
- Runtime API integration
- Enterprise connectivity
- Production operation

These boundaries do not fail Phase 5C. They prevent overstating its
maturity.

## 17. Remote CI Requirement

Phase 5C remains open until:

1. The exact authorized implementation scope is committed.
2. The commit is synchronized to remote `main`.
3. CI runs against that exact commit.
4. Both quality and container jobs succeed.
5. The implementation commit and CI run are recorded.
6. Phase 5C is closed separately.
7. Phase 5D receives explicit authorization.

## 18. Current Exit Posture

```text
PHASE 5A: COMPLETE
PHASE 5B: COMPLETE
PHASE 5C LOCAL IMPLEMENTATION: COMPLETE
PHASE 5C REMOTE CI: PENDING
PHASE 5C CLOSURE: PENDING
PHASE 5D: NOT AUTHORIZED
ENTERPRISE RETRIEVAL: NOT AUTHORIZED
VECTOR RETRIEVAL: NOT AUTHORIZED
```
