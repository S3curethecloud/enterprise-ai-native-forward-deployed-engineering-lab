PHASE_5G_CONTEXT_CONSTRUCTION_IMPLEMENTATION_AND_EVIDENCE.md


# Phase 5G — Context Construction and Token Budgets

## 1. Purpose

This document records the locally verified implementation evidence for
Phase 5G.

Phase 5G adds deterministic, whole-chunk context construction over authorized
retrieval results and an immutable synthetic evidence corpus. It enforces
explicit item, per-source, source-diversity, and estimated-token budgets.

It does not construct prompts or call a model.

## 2. Current Decision

> PHASE 5G LOCAL IMPLEMENTATION: COMPLETE
> PHASE 5G IMPLEMENTATION COMMIT: VERIFIED
> PHASE 5G REMOTE CI: PASSED
> PHASE 5G CLOSURE: PENDING
> PHASE 5H: AUTHORIZED ONLY AFTER CLOSURE-COMMIT CI

Phase 5G implementation passed exact-commit CI. This
documentation-only closure commit is authorized. Phase 5G remains
open until the closure commit passes exact-commit CI.

## 3. Prior-Phase Authority

Phase 5F closed after exact-commit CI run
[`29815184214`](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29815184214)
passed against closure commit
`2489a6e54fe5b93484b09b40c5ffd9764075dcee`.

That closure authorized the bounded Phase 5G implementation.

## 4. Authorized Scope Implemented

Phase 5G implements:

- Immutable context-budget contracts
- Whole-chunk context items
- Request, trace, subject, tenant, service, and policy lineage
- Exact candidate-to-citation-to-corpus resolution
- Active-lifecycle and current-freshness checks
- Citation retrieval-time alignment
- Maximum context-item count
- Maximum per-source contribution
- Maximum aggregate token estimate
- Minimum source-diversity requirement
- Stable retrieval-order preservation
- Deterministic context ranks
- Omitted-candidate counts
- Explicit truncation evidence
- Controlled context insufficiency
- Bounded public context exports
- Focused executable tests

## 5. Prohibited Scope

Phase 5G does not implement or authorize:

- Prompt construction
- System or developer prompts
- Prompt-injection detection
- Retrieval-contamination controls
- Content sanitization
- Partial chunk slicing
- External tokenizers
- Provider-specific token counting
- Model-provider calls
- Learned models
- Enterprise data
- Production data
- Tool execution
- Retrieval or context API routes
- Infrastructure mutation
- Cloud deployment
- Production deployment

Phase 5H prompt-injection and retrieval-contamination controls remain
separately gated.

## 6. Artifact Inventory

Implementation artifacts:

- `src/incident_diagnostic_api/retrieval/context.py`
- `src/incident_diagnostic_api/retrieval/__init__.py`
- `tests/retrieval/test_context.py`

Evidence artifacts:

- `docs/retrieval/PHASE_5G_CONTEXT_CONSTRUCTION_IMPLEMENTATION_AND_EVIDENCE.md`
- `docs/retrieval/PHASE_5G_CONTEXT_CONSTRUCTION_GATE.md`
- `docs/interview-accelerator/phases/PHASE_05_PERMISSION_AWARE_RAG.md`

## 7. Context Budget Contract

The immutable `ContextBudget` uses version `context-budget-v1`.

Default limits:

- Maximum items: 10
- Maximum items per source: 3
- Maximum aggregate token estimate: 4096
- Minimum source count: 1

The contract rejects a per-source limit greater than the total item limit and
a minimum source count greater than the total item limit.

## 8. Corpus Token-Estimate Contract

Phase 5G consumes the existing bounded `EvidenceChunk.token_estimate`
metadata.

It does not claim exact provider-token counts. It does not download or invoke
a tokenizer. The estimate is used consistently as versioned synthetic corpus
metadata for deterministic budget decisions.

Provider-specific token accounting remains outside Phase 5G.

## 9. Whole-Chunk Construction

Context construction admits or omits a complete evidence chunk.

It never slices content to force a partial chunk under the budget. This keeps
the context item aligned with the exact content hash and citation recorded by
retrieval.

An item too large for the remaining estimated-token budget is skipped.

## 10. Candidate and Corpus Integrity

Every retrieval candidate is resolved by chunk identifier against the exact
synthetic corpus supplied to the context builder.

The builder compares:

- Source identifier
- Document identifier
- Document version
- Chunk identifier
- Content hash
- Chunk locator
- Active lifecycle
- Current freshness
- Citation retrieval time

A missing chunk, duplicate candidate chunk, mismatch, tombstone, stale
candidate, or inconsistent timestamp produces controlled integrity
insufficiency. Unverified content never enters a context bundle.

## 11. Authority and Lineage Preservation

Phase 5G accepts a typed retrieval result produced by the permission-aware
retrieval boundary. It does not derive authority from context relevance.

The bundle preserves:

- Request identifier
- Trace identifier
- Subject identifier
- Tenant identifier
- Service identifier
- Policy-decision identifier
- Policy version
- Retrieval method and score
- Complete citation
- Content hash

The context builder does not broaden the candidate set. Authorization and
classification trimming remain enforced upstream before retrieval scoring.

## 12. Deterministic Source Diversity

When more than one source is required, Phase 5G selects the highest-ranked
whole chunk that fits from each required distinct source before filling
remaining capacity.

The final selected set is sorted back into ascending retrieval-rank order.

If the required source count is unavailable, construction returns controlled
source-diversity insufficiency. If the required set exists but cannot fit the
estimated-token budget, construction returns budget insufficiency.

## 13. Stable Ordering

Context construction preserves ascending retrieval rank among selected
candidates and assigns contiguous context ranks beginning at one.

Repeated construction with identical inputs returns an equal immutable
result.

## 14. Truncation Evidence

Phase 5G reports:

- Total estimated tokens admitted
- Number of retrieval candidates omitted
- Whether the result was truncated

`truncated` is true exactly when one or more candidates were omitted.

Truncation evidence describes whole-item omission. It does not imply partial
text truncation.

## 15. Controlled Insufficiency

Phase 5G returns explicit insufficiency for:

- Retrieval abstention
- Candidate or corpus integrity failure
- Estimated-token budget exhaustion
- Missing required source diversity

Insufficiency is a typed outcome mutually exclusive with a context bundle.

## 16. Public API Boundary

Phase 5G adds these public retrieval exports:

- `CONTEXT_BUDGET_VERSION`
- `ContextBudget`
- `ContextBundle`
- `ContextConstructionResult`
- `ContextDisposition`
- `ContextInsufficiency`
- `ContextInsufficiencyCode`
- `ContextItem`
- `build_context`

Selection, resolution, and insufficiency-construction helpers remain private.

The public retrieval export count is 42.

## 17. Local Test Evidence

Verified local evidence:

- Context test functions: 21
- Context pytest cases: 22 passed
- Retrieval tests: 179 passed
- Complete repository tests: 869 passed
- Ruff linting: Passed
- Ruff formatting: Passed
- Strict mypy: Passed
- Dependency validation: Passed
- Diff whitespace check: Passed

Tests cover defaults, invalid budgets, complete bundles, lineage, item limits,
estimated-token limits, whole chunks, per-source limits, source diversity,
retrieval abstention, missing chunks, hash and locator mismatches, tombstones,
stale candidates, timestamp mismatch, duplicates, budget exhaustion,
construction time, and repeatability.

## 18. Capability-Boundary Evidence

The Phase 5G implementation contains no:

- Provider SDK
- Tokenizer dependency
- Downloaded model
- Prompt template
- Model call
- Tool call
- Network client
- Managed retrieval service
- Infrastructure capability

Phase 5G remains local, deterministic, synthetic, read-only, and
dependency-free.

## 19. Residual Risks

The token estimate is metadata, not an exact provider-token count.

Context construction trusts the typed retrieval result as the upstream
permission-aware boundary. It preserves and verifies result lineage but does
not independently execute CT-03 policy evaluation.

The diversity-first selection is deterministic, not globally optimized for
semantic utility.

Retrieved content remains untrusted data. Phase 5G does not inspect or
sanitize it for prompt injection because those controls are Phase 5H work.

No production retrieval-quality, model-grounding, latency, or token-cost
claim is made.

## 20. Phase 5H Boundary

Phase 5H is limited to prompt-injection and retrieval-contamination controls
after Phase 5G is separately closed.

Phase 5H is not authorized by this implementation commit.

## 21. Remote CI Requirement

Phase 5G implementation passed exact-commit CI:

- Implementation commit: `369e05e21b61f6e0961111d9cfff4515ca0e27db`
- Exact-commit CI run: [`29817755525`](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29817755525)
- Python quality and contract tests: Passed
- Local container build and health verification: Passed
- CI conclusion: Success

Phase 5G closure still requires this documentation-only closure commit to
pass the same exact-commit CI workflow. Phase 5H remains unauthorized until
that closure CI succeeds.

## 22. Current Exit Posture

> PHASE 5G LOCAL IMPLEMENTATION: COMPLETE
> LOCAL QUALITY: PASSED
> IMPLEMENTATION REMOTE CI: PASSED
> PHASE 5G CLOSURE: PENDING
> PHASE 5H PROMPT-INJECTION AND RETRIEVAL-CONTAMINATION CONTROLS: AUTHORIZED ONLY AFTER CLOSURE-COMMIT CI
