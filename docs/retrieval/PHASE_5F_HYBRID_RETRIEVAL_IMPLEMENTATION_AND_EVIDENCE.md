# Phase 5F — Hybrid Retrieval and Deterministic Reranking

## 1. Purpose

This document records the locally verified implementation evidence for
Phase 5F.

Phase 5F combines the bounded keyword and vector retrieval paths, normalizes
their scores, deduplicates evidence by chunk identity, applies transparent
weighted fusion and reciprocal-rank evidence, and returns deterministically
reranked candidates.

## 2. Current Decision

> PHASE 5F LOCAL IMPLEMENTATION: COMPLETE
> PHASE 5F IMPLEMENTATION COMMIT: AUTHORIZED
> PHASE 5F REMOTE CI: PENDING
> PHASE 5F CLOSURE: PENDING
> PHASE 5G: NOT AUTHORIZED

Phase 5F may be committed for exact-commit CI validation.

## 3. Authorized Scope Implemented

Phase 5F implements:

- Versioned hybrid-retrieval configuration
- Explicit keyword, vector, and rank weights
- Per-method maximum-score normalization
- Normalized reciprocal-rank evidence
- Transparent weighted fusion
- Keyword and vector candidate union
- Deduplication by chunk identifier
- Deterministic hybrid scoring
- Stable hybrid reranking
- Hybrid candidate method classification
- Citation preservation
- Policy-controlled result limits
- Query-controlled result limits
- Final hybrid threshold enforcement
- Controlled hybrid abstention
- Public bounded hybrid exports
- Focused primitive and execution tests

## 4. Prohibited Scope

Phase 5F does not implement or authorize:

- Learned rerankers
- Cross-encoder models
- Provider reranking
- External embedding providers
- Downloaded models
- Enterprise evidence sources
- Production data
- Managed vector databases
- Context construction
- Prompt assembly
- Model-provider calls
- Tool execution
- Retrieval API routes
- Infrastructure mutation
- Cloud deployment
- Production deployment

## 5. Artifact Inventory

Implementation artifacts:

- `src/incident_diagnostic_api/retrieval/hybrid.py`
- `src/incident_diagnostic_api/retrieval/__init__.py`

Test artifact:

- `tests/retrieval/test_hybrid.py`

Evidence artifacts:

- `docs/retrieval/PHASE_5F_HYBRID_RETRIEVAL_IMPLEMENTATION_AND_EVIDENCE.md`
- `docs/retrieval/PHASE_5F_HYBRID_RETRIEVAL_GATE.md`
- `docs/interview-accelerator/phases/PHASE_05_PERMISSION_AWARE_RAG.md`

## 6. Configuration Contract

The configuration version is:

- `hybrid-fusion-v1`

Default values:

- Keyword weight: 0.45
- Vector weight: 0.45
- Reciprocal-rank weight: 0.10
- Reciprocal-rank constant: 60

Configuration invariants:

- Every weight is between zero and one
- The three weights sum to one
- The rank constant is positive
- The configuration version is supported
- The configuration is immutable

## 7. Score Normalization

Keyword overlap scores and vector cosine scores occupy the same nominal
zero-to-one range but may have different distributions.

Phase 5F normalizes each method independently by its maximum observed
candidate score:

- Highest keyword candidate becomes 1.0
- Other keyword scores are divided by the keyword maximum
- Highest vector candidate becomes 1.0
- Other vector scores are divided by the vector maximum
- An empty candidate set produces an empty normalized map
- A zero-only candidate set remains zero
- Duplicate chunk identifiers are rejected

Normalization occurs before fusion.

## 8. Reciprocal-Rank Evidence

Reciprocal-rank evidence rewards candidates that appear near the top of one
or both component retrieval lists.

For each available rank:

- Rank evidence is `1 / (constant + rank)`
- Keyword and vector rank evidence are added
- The sum is normalized by the maximum possible two-method first-place score
- A first-place result in both methods produces 1.0
- A first-place result in one method produces 0.5
- Missing ranks produce no evidence
- Invalid nonpositive ranks are rejected

The rank signal is deterministic and transparent.

## 9. Hybrid Scoring Formula

The default score is:

- 45% normalized keyword score
- 45% normalized vector score
- 10% normalized reciprocal-rank score

The formula is:

`H = 0.45K + 0.45V + 0.10R`

Where:

- `H` is the hybrid score
- `K` is the normalized keyword score
- `V` is the normalized vector score
- `R` is normalized reciprocal-rank evidence

Every input must remain between zero and one.

The final score is bounded between zero and one.

## 10. Candidate Union and Deduplication

Phase 5F creates maps keyed by chunk identifier for keyword and vector
candidates.

The candidate universe is the set union of those identifiers.

Each evidence chunk appears at most once in the hybrid output, even when it
appears in both component methods.

The candidate retains:

- Request lineage
- Trace lineage
- Policy-decision lineage
- Source identifier
- Document identifier
- Document version
- Chunk identifier
- Freshness
- Citation
- Content hash

The output method is `HYBRID`.

## 11. Execution Order

Hybrid retrieval performs these steps:

1. Resolve the versioned fusion configuration.
2. Create a component query with a zero component threshold.
3. Execute keyword retrieval.
4. Execute vector retrieval.
5. Collect both candidate sets.
6. Normalize keyword scores.
7. Normalize vector scores.
8. Union candidates by chunk identity.
9. Calculate reciprocal-rank evidence.
10. Calculate the weighted hybrid score.
11. Apply the original query threshold.
12. Sort deterministically.
13. Apply the smaller query or policy result limit.
14. Return cited candidates or an explicit abstention.

The validated execution order is:

- Retrieve
- Normalize
- Fuse
- Rerank
- Limit

## 12. Authority Preservation

Keyword and vector retrieval continue to enforce the shared Phase 5D
security boundary before their respective scoring operations.

Hybrid retrieval does not grant new access.

It combines only candidates returned by already-authorized component
retrieval paths.

The query, keyword score, vector score, normalized score, reciprocal rank,
and fused score cannot authorize evidence.

## 13. Deterministic Reranking

Hybrid candidates are sorted by:

1. Descending hybrid score
2. Source identifier
3. Document identifier
4. Chunk identifier

Reciprocal rank may legitimately distinguish candidates with equal component
scores.

When the rank weight is explicitly zero and fused scores are equal, stable
identifiers determine the order.

## 14. Threshold and Limit Behavior

The original query threshold is applied to the final hybrid score.

Component retrieval uses a zero component threshold so a positive candidate
from either retrieval path can participate in fusion.

Final candidate count is the smaller of:

- Query maximum candidates
- Policy maximum evidence items

Caller preferences may narrow policy limits but cannot enlarge them.

## 15. Abstention Behavior

Hybrid retrieval abstains when both component paths return no candidates.

Abstention precedence is fail-closed:

1. Authorization missing
2. No authorized sources
3. Integrity failure
4. No relevant evidence

Hybrid retrieval also abstains when no fused candidate meets the original
query threshold.

## 16. Verified Baseline

For the bounded synthetic query `payment queue`:

- Candidate 1: `chunk-a`
- Candidate 1 score: 1.000000
- Candidate 2: `chunk-b`
- Candidate 2 score: approximately 0.583195
- Duplicate chunks: zero
- Output method: `HYBRID`

This baseline is deterministic for the verified configuration and corpus.

## 17. Public API Boundary

Phase 5F publicly exports:

- `HybridRetrievalConfig`
- `calculate_hybrid_score`
- `calculate_reciprocal_rank_score`
- `normalize_candidate_scores`
- `retrieve_hybrid`

Internal abstention selection remains private.

The complete public retrieval export inventory contains 33 names.

## 18. Local Test Evidence

Local verification produced:

- Hybrid test functions: 30
- Hybrid pytest cases: 33 passed
- Retrieval tests: 157 passed
- Complete repository tests: 847 passed
- Ruff linting: Passed
- Ruff formatting: Passed
- Strict mypy checking: Passed
- Dependency validation: Passed
- Diff validation: Passed

Tests cover:

- Configuration defaults
- Configuration immutability
- Version rejection
- Weight validation
- Weight-sum validation
- Rank-constant validation
- Score normalization
- Duplicate rejection
- Reciprocal-rank behavior
- Transparent weighted scoring
- Ranked hybrid candidates
- Verified baseline scores
- Candidate deduplication
- Citation lineage
- Repeatability
- Empty-query abstention
- Mismatched-authority abstention
- Tenant filtering
- Query limits
- Policy limits
- Custom weights
- Final threshold behavior
- Stable tie-breaking

## 19. Capability-Boundary Evidence

A source scan found no:

- Learned reranker
- Cross-encoder dependency
- External provider SDK
- Downloaded model
- Managed vector-database client
- Network client
- Tool executor
- Subprocess execution
- Socket use
- Terraform capability
- Kubernetes capability

Phase 5F remains local, deterministic, synthetic, read-only, and
dependency-free.

## 20. Residual Risks

Maximum-score normalization makes each method’s strongest observed candidate
equal to one, even when the absolute component score is weak.

This can overstate weak relative winners in small candidate sets.

Additional residual risks include:

- Static fusion weights
- No learned relevance calibration
- No production evaluation dataset
- No query-class-specific weighting
- No distribution-aware score calibration
- No enterprise corpus
- No operational telemetry
- No latency or cost measurement
- No persistent index
- No provider comparison

These limitations require Phase 5J evaluation and remain documented.

## 21. Remote CI Requirement

Phase 5F closure requires the exact implementation commit to pass:

- Python quality and contract tests
- Local container build and health verification

The implementation commit and CI run must be recorded before Phase 5F can
be closed.

## 22. Current Exit Posture

> PHASE 5F LOCAL IMPLEMENTATION: COMPLETE
> LOCAL QUALITY: PASSED
> REMOTE CI: PENDING
> PHASE 5F CLOSURE: PENDING
> PHASE 5G CONTEXT CONSTRUCTION AND TOKEN BUDGETS: NOT AUTHORIZED
