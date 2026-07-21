# Phase 5C — Synthetic Corpus and Keyword Retrieval Gate

## 1. Gate Purpose

This gate determines whether the bounded Phase 5C implementation is ready
for an implementation commit and exact-commit CI validation.

## 2. Current Gate Decision

```text
LOCAL IMPLEMENTATION GATE: PASSED
REMOTE CI GATE: PENDING
PHASE 5C CLOSURE: PENDING
PHASE 5D: NOT AUTHORIZED
```

## 3. Evaluated Scope

This gate evaluates:

- Immutable synthetic corpus behavior
- Corpus integrity validation
- Deterministic keyword tokenization
- Deterministic lexical scoring
- Source identifier and kind allowlisting
- Tombstone exclusion
- Stable ranking
- Explicit abstention
- Read-only behavior
- Public exports
- Tests and evidence

## 4. Prohibited Scope

This gate does not authorize:

- Enterprise sources
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
- Provider calls
- Tools
- Retrieval API routes
- Network access
- Infrastructure mutation
- Cloud deployment
- Production deployment

## 5. Artifact Gate

| Artifact | Result |
|---|---|
| `retrieval/corpus.py` | Passed |
| `retrieval/keyword.py` | Passed |
| Retrieval public exports | Passed |
| `test_corpus.py` | Passed |
| `test_keyword.py` | Passed |
| Implementation evidence | Passed |

## 6. Corpus Gate

Passed evidence:

- Corpus collections are immutable and bounded.
- Source identifiers are unique.
- Document identifiers are unique.
- Chunk identifiers are unique.
- Documents reference existing sources.
- Chunks reference existing documents.
- Metadata lineage remains aligned.
- Lifecycle metadata remains aligned.
- Document content hashes are validated.
- Chunk content hashes are validated.
- Unknown fields are rejected.

## 7. Keyword Gate

Passed evidence:

- Tokenization is normalized.
- Duplicate query terms do not inflate scores.
- Empty token sets score zero.
- Scores represent unique token overlap.
- Scores remain bounded from zero to one.
- No stochastic component exists.

## 8. Source-Scope Gate

Before scoring, the implementation checks:

- Allowed source identifiers
- Allowed source kinds
- Active lifecycle state

Passed evidence:

- Non-allowlisted source identifiers abstain.
- Non-allowlisted source kinds abstain.
- Tombstoned evidence is excluded.

This is not the Phase 5D tenant, service, and classification filter.

## 9. Ranking Gate

Passed evidence:

- Higher scores rank first.
- Candidate limits are enforced.
- Minimum scores are enforced.
- Equal scores use stable metadata ordering.
- Ranks are one-based and contiguous.
- Repeated execution produces the same serialized result.

## 10. Abstention Gate

Passed evidence:

- Expired authority produces `AUTHORIZATION_MISSING`.
- Punctuation-only queries produce `NO_RELEVANT_EVIDENCE`.
- Missing authorized sources produce `NO_AUTHORIZED_SOURCES`.
- Evidence below the threshold produces `NO_RELEVANT_EVIDENCE`.
- Abstentions contain no candidate evidence.
- Request and trace correlation are preserved.

## 11. Read-Only Gate

Passed evidence:

- The corpus is not mutated.
- The query is not mutated.
- Evidence metadata is not mutated.
- Retrieval performs no external write.
- Retrieval performs no tool invocation.

## 12. Public API Gate

Observed public retrieval exports:

```text
18
```

New Phase 5C exports:

- `SyntheticEvidenceCorpus`
- `calculate_content_hash`
- `tokenize_keywords`
- `calculate_keyword_score`
- `retrieve_keywords`

## 13. Test Gate

Observed local evidence:

```text
Corpus tests: 23 passed
Keyword tests: 16 passed
All retrieval tests: 76 passed
Complete repository tests: 762 passed
```

Quality evidence:

- Ruff lint passed.
- Ruff format passed.
- Mypy passed.
- Dependency validation passed.
- Git diff validation passed.

## 14. Capability-Boundary Gate

The capability scan detected no implementation for:

- Vector databases
- Embeddings
- Reranking
- External model providers
- Network clients
- Subprocess execution
- Cloud SDKs
- Kubernetes
- Terraform

Result:

```text
PASS
```

## 15. Phase 5D Boundary

Phase 5D remains responsible for:

- Tenant filtering
- Service filtering
- Classification filtering
- Cross-scope rejection tests
- Filter-order evidence

Phase 5C does not claim those controls.

## 16. Residual Risks

Phase 5C does not establish:

- Enterprise data connectivity
- Production retrieval quality
- Semantic relevance
- Freshness enforcement
- Complete permission filtering
- Context safety
- Runtime API behavior
- Production scalability
- Compliance certification

## 17. Remote CI Gate

Pending requirements:

1. Commit the exact Phase 5C scope.
2. Synchronize the commit to remote `main`.
3. Execute CI against that exact commit.
4. Require quality and container jobs to pass.
5. Record the implementation commit and CI run.
6. Close Phase 5C separately.
7. Authorize Phase 5D explicitly.

## 18. Final Local Decision

```text
PHASE 5C LOCAL IMPLEMENTATION GATE: PASSED
PHASE 5C IMPLEMENTATION COMMIT: AUTHORIZED
PHASE 5C REMOTE CI: REQUIRED
PHASE 5C CLOSURE: PENDING
PHASE 5D: NOT AUTHORIZED
ENTERPRISE RETRIEVAL: NOT AUTHORIZED
VECTOR RETRIEVAL: NOT AUTHORIZED
```
