# Phase 5J — Retrieval Evaluation and Lifecycle Telemetry Implementation and Evidence

## 1. Purpose

This document records the bounded local implementation of deterministic
retrieval evaluation and lifecycle telemetry for Phase 5J.

Phase 5J completes the currently defined Phase 5 permission-aware RAG scope.
It evaluates synthetic retrieval outcomes and records allowlisted local
lifecycle evidence without adding provider, model, network, tool, API-route,
or infrastructure authority.

## 2. Current Decision

> PHASE 5J LOCAL IMPLEMENTATION: COMPLETE
> PHASE 5J IMPLEMENTATION COMMIT: AUTHORIZED
> PHASE 5J REMOTE CI: PENDING
> PHASE 5J CLOSURE: PENDING
> PHASE 5: NOT YET CLOSED
> PHASE 6: NOT AUTHORIZED

Phase 5J may be committed for exact-commit CI validation. Phase 6
multi-provider abstraction remains unauthorized until the Phase 5J closure
commit passes exact-commit CI and Phase 5 is explicitly closed.

## 3. Prior-Phase Authority

Phase 5I closed after exact-commit CI run
`29852373709` passed against closure commit
`501ee512037943a0960878a296309c5922777e9f`.

That closure authorized bounded Phase 5J retrieval evaluation and lifecycle
telemetry. It did not authorize provider adapters, provider calls, prompt or
model execution, tools, retrieval APIs, external telemetry, cloud resources,
or production deployment.

## 4. Authorized Scope Implemented

Phase 5J implements:

- Versioned deterministic retrieval evaluation
- Explicit synthetic relevance expectations
- Precision at K
- Recall at K
- Reciprocal rank
- Citation-correctness measurement
- Freshness-correctness measurement
- Abstention-correctness measurement
- Query-latency measurement
- Context item and estimated-token measurements
- Explicit evaluation thresholds
- Stable pass/fail evidence
- Allowlisted retrieval lifecycle stages and outcomes
- Immutable hash-linked telemetry events
- A bounded append-only in-memory telemetry store
- Deterministic telemetry-history verification
- Request and trace correlation
- Raw-query, prompt, response, and evidence-content exclusion

## 5. Prohibited Scope

Phase 5J does not implement or authorize:

- External or model-based evaluators
- Semantic or factual-correctness judges
- Provider SDKs or provider calls
- Prompt or model execution
- Learned metrics or classifiers
- Production datasets or enterprise sources
- External telemetry backends
- OpenTelemetry, Prometheus, or cloud monitoring integration
- Network clients
- Tool execution
- Retrieval or telemetry API routes
- Infrastructure mutation
- Cloud or production deployment
- Phase 6 provider adapters

## 6. Artifact Inventory

Phase 5J adds or updates:

- `src/incident_diagnostic_api/retrieval/evaluation.py`
- `src/incident_diagnostic_api/retrieval/__init__.py`
- `tests/retrieval/test_evaluation.py`
- `docs/retrieval/PHASE_5J_RETRIEVAL_EVALUATION_IMPLEMENTATION_AND_EVIDENCE.md`
- `docs/retrieval/PHASE_5J_RETRIEVAL_EVALUATION_GATE.md`
- `docs/interview-accelerator/phases/PHASE_05_PERMISSION_AWARE_RAG.md`

## 7. Versioned Evaluation and Telemetry Contracts

The evaluation version is `retrieval-evaluation-v1`.

The telemetry version is `retrieval-telemetry-v1`.

Both are explicit contract values. Phase 5J does not silently reinterpret
historical evidence under a different evaluator or telemetry schema.

## 8. Synthetic Ground Truth

`RetrievalEvaluationExpectation` records bounded synthetic ground truth:

- Case identifier
- Unique relevant chunk identifiers
- Cutoff K
- Expected retrieval abstention
- Expected citation validity
- Expected freshness validity

An expected abstention cannot simultaneously declare relevant chunks.
Duplicate relevance labels fail validation.

The expectation is local test evidence, not a claim that production relevance
has been labeled or validated.

## 9. Precision at K and Recall at K

Precision at K measures the fraction of the returned top-K candidates that
match labeled relevant chunk identifiers.

Recall at K measures the fraction of all labeled relevant chunks recovered in
the returned top-K candidates.

Candidate order comes from the immutable `RetrievalResult`. Phase 5J does not
rerank, rewrite, or expand retrieval output during evaluation.

## 10. Reciprocal Rank

Reciprocal rank is `1 / rank` for the first labeled relevant candidate.

It is zero when no relevant candidate is returned. The calculation is stable
because candidate ranks are already unique, ordered, and contiguous under the
retrieval contract.

## 11. Citation, Freshness, and Abstention Correctness

Phase 5J consumes the Phase 5I `CitationValidationResult` rather than
reimplementing citation validation.

Citation correctness reflects whether the controlled citation outcome matches
the case expectation. Citation mismatch and integrity-failure evidence are
treated as invalid citation outcomes.

Freshness correctness reflects whether stale-evidence evidence matches the
case expectation.

Abstention correctness compares the retrieval disposition with the explicit
case expectation.

These are deterministic contract checks. They do not establish factual or
semantic correctness.

## 12. Latency and Context-Size Measurements

The evaluation records:

- Non-negative query latency in milliseconds
- Context item count
- Estimated context-token count

These values remain bounded. Phase 5J does not add an external tokenizer,
profiling service, tracing agent, or monitoring backend.

## 13. Explicit Thresholds and Stable Failure Evidence

`RetrievalEvaluationThresholds` defines minimum quality thresholds and maximum
latency and context-size thresholds.

`evaluate_retrieval` evaluates checks in a fixed order and records unique,
stable failed-check identifiers. A passed result cannot contain failed checks,
and a failed result must contain at least one failed check.

Thresholds are local release evidence. They do not authorize deployment.

## 14. Deterministic Evaluation Boundary

Equivalent immutable inputs produce equivalent evaluation results.

Evaluation occurs only after retrieval and citation-validation completion.
Request and trace identifiers must match across both upstream results.

The evaluator does not mutate retrieval candidates, controlled context,
citations, or validated evidence.

## 15. Retrieval Lifecycle Telemetry

Phase 5J defines five allowlisted local stages:

1. Retrieval completed
2. Context constructed
3. Content inspected
4. Citations validated
5. Evaluation completed

Allowlisted outcomes are succeeded, abstained, and failed.

The generic CT-07 `TraceEvent` remains the repository-wide lifecycle trace
contract. Phase 5J telemetry is retrieval-specific measurement evidence and
does not replace or expand CT-07 runtime authority.

## 16. Append-Only Hash Lineage

`InMemoryRetrievalTelemetryStore` maintains isolated per-trace histories.

Each event records:

- Deterministic sequence
- Previous event hash
- Current event hash
- Request and trace identifiers
- Allowlisted stage and outcome
- Optional opaque input and output references
- Allowlisted numeric measurements
- A timezone-aware occurrence timestamp

The first event has sequence zero and no previous hash. Later events link to
the immediately preceding hash. Capacity is checked before mutation.

## 17. Correlation and Content-Exclusion Boundary

A request identifier cannot change within one trace history. Timestamps cannot
move backward. Histories are immutable tuple views and unknown-history reads
do not create storage state.

Telemetry contracts exclude:

- Raw queries
- Evidence content
- Prompts
- Model responses
- Unrestricted payloads

This limits telemetry exposure while retaining bounded lifecycle evidence.

## 18. History Verification

`verify_retrieval_telemetry_history` verifies:

- Non-empty history
- Contiguous sequence
- Stable request and trace correlation
- Previous-hash lineage
- Nondecreasing timestamps
- Deterministic recomputation of every event hash

Tampered hashes, sequences, correlation, ordering, or measurements fail
verification.

## 19. Public API Boundary

Phase 5J adds 18 public retrieval exports covering:

- Evaluation and telemetry versions
- Evaluation expectations, metrics, thresholds, disposition, and result
- Lifecycle stage and outcome
- Telemetry measurement and event contracts
- Bounded telemetry store and capacity error
- Metric calculation and evaluation
- Event hashing and history verification

The complete public retrieval export count is 79 and all exports are unique.

## 20. Local Test Evidence

Verified local evidence:

- Evaluation test functions: 32
- Evaluation pytest cases: 33 passed
- Retrieval tests: 264 passed
- Complete repository tests: 954 passed
- Public retrieval exports: 79
- Ruff linting: Passed
- Ruff formatting: Passed
- Strict mypy: Passed
- Dependency validation: Passed
- Diff whitespace check: Passed

Tests cover metric correctness, cutoff behavior, partial relevance, empty
relevance, stale evidence, citation mismatch, correlation failures, negative
latency, threshold failures, completion ordering, contract invariants,
deterministic hashing, append-only linkage, trace isolation, capacity,
timestamp ordering, content exclusion, tampering, and repeatability.

## 21. Capability-Boundary Evidence

The Phase 5J implementation contains no:

- Provider SDK or provider call
- Model dependency or evaluator
- Network client
- External telemetry dependency
- Dynamic evaluation or execution
- Prompt or model execution
- Tool execution
- Enterprise connector
- API route
- Infrastructure capability

Phase 5J remains local, deterministic, synthetic, bounded, and
dependency-free.

## 22. Residual Risks

Residual risks remain explicit:

- Synthetic relevance labels do not represent production distributions
- Lexical and deterministic metrics do not measure semantic correctness
- Estimated tokens are not provider-tokenizer counts
- In-memory telemetry is not durable production observability
- Hash lineage detects mutation but does not provide external anchoring
- Local latency is not production latency
- Thresholds require future workload-specific calibration
- No model-provider behavior has been evaluated

These limitations prevent claims of enterprise retrieval quality, factual
correctness, production monitoring, or deployment readiness.

## 23. Phase 6 Boundary

Phase 6 is Multi-Provider Abstraction.

Phase 6 remains unauthorized until:

1. The Phase 5J implementation commit passes exact-commit CI.
2. The Phase 5J closure evidence is committed.
3. The Phase 5J closure commit passes exact-commit CI.
4. Phase 5 is explicitly recorded as closed.

No deterministic mock-provider adapter, OpenAI adapter, Anthropic adapter,
Google or Vertex adapter, provider request envelope, provider response
envelope, provider retry, or provider fallback is authorized by Phase 5J.

## 24. Remote CI Requirement

Phase 5J closure requires the exact implementation commit to pass:

- Python quality and contract tests
- Local container build and health verification

The implementation commit and CI run must be recorded before Phase 5J can be
closed. A separate closure commit must then pass exact-commit CI before Phase
6 can become authorized.

## 25. Current Exit Posture

> PHASE 5J LOCAL IMPLEMENTATION: COMPLETE
> LOCAL QUALITY: PASSED
> REMOTE CI: PENDING
> PHASE 5J CLOSURE: PENDING
> PHASE 5: NOT YET CLOSED
> PHASE 6 MULTI-PROVIDER ABSTRACTION: NOT AUTHORIZED

