# Phase 5F — Hybrid Retrieval and Deterministic Reranking Gate

## 1. Gate Purpose

This gate determines whether the bounded Phase 5F implementation may be
committed for exact-commit CI validation.

## 2. Current Gate Decision

> PHASE 5F LOCAL IMPLEMENTATION: PASSED
> PHASE 5F IMPLEMENTATION COMMIT: AUTHORIZED
> PHASE 5F REMOTE CI: REQUIRED
> PHASE 5F CLOSURE: PENDING
> PHASE 5G: NOT AUTHORIZED

Phase 5F is locally complete but is not closed.

## 3. Evaluated Scope

This gate evaluates:

- Hybrid configuration
- Score normalization
- Reciprocal-rank evidence
- Weighted score fusion
- Candidate union
- Deduplication
- Deterministic reranking
- Threshold handling
- Policy and query limits
- Citation preservation
- Abstention behavior
- Public exports
- Tests
- Capability boundaries
- Interview-learning updates

## 4. Prohibited Scope

This gate does not authorize:

- Learned rerankers
- Cross-encoder models
- Provider reranking
- External embedding providers
- Enterprise sources
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

## 5. Artifact Gate

Required implementation artifacts:

- `src/incident_diagnostic_api/retrieval/hybrid.py`
- `src/incident_diagnostic_api/retrieval/__init__.py`

Required test artifact:

- `tests/retrieval/test_hybrid.py`

Required evidence artifacts:

- `docs/retrieval/PHASE_5F_HYBRID_RETRIEVAL_IMPLEMENTATION_AND_EVIDENCE.md`
- `docs/retrieval/PHASE_5F_HYBRID_RETRIEVAL_GATE.md`
- `docs/interview-accelerator/phases/PHASE_05_PERMISSION_AWARE_RAG.md`

Decision: Passed locally.

## 6. Configuration Gate

The configuration must:

- Be immutable
- Be explicitly versioned
- Use weights between zero and one
- Require weights to sum to one
- Require a positive reciprocal-rank constant

Verified version: `hybrid-fusion-v1`.

Decision: Passed locally.

## 7. Normalization Gate

Each retrieval method must be normalized independently.

The normalizer must:

- Return an empty map for no candidates
- Divide scores by the method maximum
- Preserve zero-only scores as zero
- Reject duplicate chunk identifiers

Decision: Passed locally.

## 8. Reciprocal-Rank Gate

Reciprocal-rank evidence must:

- Reward earlier ranks
- Support candidates present in one or both methods
- Normalize two first-place ranks to one
- Normalize one first-place rank to one-half
- Reject nonpositive ranks
- Reject a nonpositive rank constant

Decision: Passed locally.

## 9. Fusion Formula Gate

The default formula must remain:

`H = 0.45K + 0.45V + 0.10R`

Every normalized input must remain between zero and one.

The fused result must remain between zero and one.

Decision: Passed locally.

## 10. Deduplication Gate

Keyword and vector candidates must be unioned by chunk identifier.

A chunk returned by both methods must appear only once in the hybrid output.

Decision: Passed locally.

## 11. Authority Gate

Hybrid retrieval must not create new authorization.

Every hybrid candidate must originate from a keyword or vector candidate
that already passed the shared CT-03 security boundary.

Decision: Passed locally.

## 12. Reranking Gate

Hybrid candidates must be ordered by:

1. Descending hybrid score
2. Source identifier
3. Document identifier
4. Chunk identifier

Equal fused scores must use stable identifier ordering.

Decision: Passed locally.

## 13. Threshold and Limit Gate

The original query threshold must apply after fusion.

The final candidate limit must be the smaller of:

- Query maximum candidates
- Policy maximum evidence items

Decision: Passed locally.

## 14. Citation and Lineage Gate

Every hybrid candidate must preserve:

- Request identifier
- Trace identifier
- Policy-decision identifier
- Source identifier
- Document identifier
- Document version
- Chunk identifier
- Citation
- Content hash

The output method must be `HYBRID`.

Decision: Passed locally.

## 15. Abstention Gate

Hybrid abstention precedence must remain:

1. Authorization missing
2. No authorized sources
3. Integrity failure
4. No relevant evidence

A final-threshold miss must produce controlled abstention.

Decision: Passed locally.

## 16. Test Gate

Verified local evidence:

- Hybrid test functions: 30
- Hybrid pytest cases: 33 passed
- Retrieval tests: 157 passed
- Complete repository tests: 847 passed
- Ruff linting: Passed
- Ruff formatting: Passed
- Strict mypy checking: Passed
- Dependency validation: Passed
- Diff validation: Passed

Decision: Passed locally.

## 17. Public API Gate

Required exports:

- `HybridRetrievalConfig`
- `calculate_hybrid_score`
- `calculate_reciprocal_rank_score`
- `normalize_candidate_scores`
- `retrieve_hybrid`

Verified public retrieval exports: 33.

Private abstention selection must remain unexported.

Decision: Passed locally.

## 18. Capability-Boundary Gate

The implementation contains no:

- Learned reranker
- Cross encoder
- External provider
- Downloaded model
- Managed vector-database client
- Network client
- Tool executor
- Subprocess execution
- Socket use
- Terraform capability
- Kubernetes capability

Decision: Passed locally.

## 19. Interview-Learning Gate

The interview guide must explain:

- Hybrid retrieval
- Score normalization
- Weighted fusion
- Reciprocal-rank fusion
- Candidate deduplication
- Deterministic reranking
- Stable tie-breaking
- Policy limits after fusion
- Weak-winner normalization risk
- Learned versus deterministic reranking
- Honest Phase 5F boundaries

Decision: Pending interview-guide update.

## 20. Phase 5G Boundary

Phase 5G may eventually implement bounded context construction and token
budgets.

Phase 5G remains unauthorized until:

1. Phase 5F is committed.
2. Exact-commit CI passes.
3. Phase 5F evidence is recorded.
4. Phase 5F closure is separately validated.
5. Phase 5G authority is explicitly granted.

Phase 5G does not inherit authority for:

- Provider calls
- Prompt execution
- Tool execution
- Enterprise sources
- Production data
- Cloud deployment
- Production deployment

## 21. Remote CI Gate

Required remote jobs:

- Python quality and contract tests
- Local container build and health verification

Current status:

- Implementation commit: Pending
- Exact-commit CI run: Pending
- Remote CI conclusion: Pending
- Phase 5F closure: Pending

## 22. Residual Risks

Known limitations include:

- Static fusion weights
- Maximum-score normalization may elevate weak winners
- No learned calibration
- No production evaluation dataset
- No enterprise corpus
- No latency measurement
- No cost measurement
- No retrieval telemetry

These limitations remain documented and bounded.

## 23. Final Local Decision

> PHASE 5F LOCAL GATE: PASSED
> PHASE 5F IMPLEMENTATION COMMIT: AUTHORIZED
> PHASE 5F CLOSURE: PENDING
> PHASE 5G: NOT AUTHORIZED
> LEARNED RERANKING: NOT AUTHORIZED
> CONTEXT CONSTRUCTION: NOT AUTHORIZED
> PRODUCTION DEPLOYMENT: NOT AUTHORIZED
