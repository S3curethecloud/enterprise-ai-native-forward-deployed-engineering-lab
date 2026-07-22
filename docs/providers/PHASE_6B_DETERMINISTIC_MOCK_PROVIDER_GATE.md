# Phase 6B — Deterministic Local Mock Provider Gate

## 1. Gate Purpose

This gate determines whether the bounded Phase 6B local mock-provider
implementation is complete enough for exact-commit CI validation.

## 2. Current Gate Decision

> PHASE 6B LOCAL IMPLEMENTATION: PASSED
> PHASE 6B IMPLEMENTATION COMMIT: AUTHORIZED
> PHASE 6B REMOTE CI: REQUIRED
> PHASE 6B CLOSURE: PENDING
> PHASE 6: NOT YET CLOSED
> PHASE 7: NOT AUTHORIZED
> REAL PROVIDER ADAPTERS OR CALLS: NOT AUTHORIZED

## 3. Prior-Phase Authority Gate

Phase 6A evidence commit `0314605bdba27a41022c578c2bf424615e1cbee8`
passed exact-commit CI run `29891756010`.

PASS: one deterministic local mock provider was authorized.

## 4. Artifact Gate

Required Phase 6B artifacts:

- Deterministic mock implementation
- Bounded mock exports
- Mock behavior and boundary tests
- Implementation evidence
- Local gate

PASS: the Phase 6B artifact set is explicit and bounded.

## 5. Identity Gate

Required fixed identity:

- Provider: `local_mock`
- Adapter: `local-mock-v1`
- Model: `deterministic-model-v1`

PASS: mismatched identities fail closed.

## 6. Capability Gate

Supported:

- Text generation
- Structured output

Unsupported:

- Streaming
- Tool calling

PASS: unsupported execution capabilities return normalized safe errors.

## 7. Input Gate

Required enforcement:

- Validated provider request
- Exact identity
- Temperature zero
- Supported capabilities
- Maximum 512 estimated input tokens
- Maximum 256 output tokens
- Explicit completion time

PASS: the local mock input boundary fails closed.

## 8. Determinism Gate

Prohibited nondeterminism:

- Current clock reads
- Random values
- UUID generation
- Environment input
- Mutable provider state

PASS: identical inputs and timestamps produce identical results.

## 9. Output Gate

Required output behavior:

- Hash-derived synthetic output
- No complete-input echo
- Bounded token estimate
- Deterministic output limit
- Deterministic stop-sequence handling
- Frozen normalized response

PASS: mock output is bounded and repeatable.

## 10. Error Gate

Required normalized errors:

- Invalid request
- Unsupported capability
- Context limit exceeded
- Response invalid

Required properties:

- Safe message
- Deterministic category
- Deterministic retryability
- Preserved correlation

PASS: mock failure behavior uses Phase 6A error contracts.

## 11. Statelessness Gate

The mock must contain no mutable instance state or invocation history.

PASS: the concrete mock has no instance dictionary.

## 12. Test Gate

Verified evidence:

- Mock test functions: 17
- Mock pytest cases: 20 passed
- Provider pytest cases: 49 passed
- Complete repository tests: 1,003 passed
- Ruff: Passed
- Formatting: Passed
- Strict mypy: Passed
- Dependency validation: Passed

PASS: success, error, limit, capability, correlation, and determinism paths execute.

## 13. Execution-Capability Gate

Prohibited capabilities:

- Real-provider SDK
- Network client
- Credential access
- Environment access
- Filesystem access
- Subprocess or dynamic execution
- Streaming execution
- Tool execution
- Routing, fallback, or retry execution

PASS: only bounded in-process deterministic mock generation exists.

## 14. Public API Gate

Required exports:

- Mock identity and version constants
- Mock limits
- Concrete deterministic mock
- Result type alias
- Deterministic token estimator

PASS: no real-provider adapter or generic provider router is exported.

## 15. Honest-Limitations Gate

The implementation must not claim:

- Real provider integration
- Real tokenizer fidelity
- Provider semantic equivalence
- Operational retry or fallback
- Production readiness

PASS: the mock is described as deterministic local contract evidence only.

## 16. Phase 6 Closure Gate

Phase 6 remains open until the exact Phase 6B implementation commit passes CI
and the Phase 6 closure evidence is committed and verified.

Phase 7 remains unauthorized. Real provider adapters and calls remain
unauthorized.

PASS: later authority remains fail-closed.

## 17. Remote CI Gate

Required jobs:

- Python quality and contract tests
- Local container build and health verification

Current status:

- Implementation commit: Pending
- Exact-commit CI run: Pending
- Remote CI conclusion: Pending
- Phase 6B closure: Pending

## 18. Final Local Decision

> PHASE 6B LOCAL GATE: PASSED
> PHASE 6B IMPLEMENTATION COMMIT: AUTHORIZED
> PHASE 6B CLOSURE: PENDING
> PHASE 6: NOT YET CLOSED
> PHASE 7: NOT AUTHORIZED
> REAL PROVIDER ADAPTERS: NOT AUTHORIZED
> PROVIDER CALLS: NOT AUTHORIZED
> PRODUCTION DEPLOYMENT: NOT AUTHORIZED
