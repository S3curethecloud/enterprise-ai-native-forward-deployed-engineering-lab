# Phase 6B — Deterministic Local Mock Provider Implementation and Evidence

## 1. Purpose

This document records the bounded local Phase 6B implementation of one
deterministic mock provider over the Phase 6A provider-neutral contracts.

The mock exists to prove contract behavior without contacting or simulating
the operational details of a real provider.

## 2. Current Decision

> PHASE 6B LOCAL IMPLEMENTATION: COMPLETE
> PHASE 6B IMPLEMENTATION COMMIT: AUTHORIZED
> PHASE 6B REMOTE CI: PENDING
> PHASE 6B CLOSURE: PENDING
> PHASE 6: NOT YET CLOSED
> PHASE 7: NOT AUTHORIZED
> REAL PROVIDER ADAPTERS OR CALLS: NOT AUTHORIZED

Phase 6B may be committed for exact-commit CI validation.

## 3. Prior-Phase Authority

Phase 6A evidence commit `0314605bdba27a41022c578c2bf424615e1cbee8`
passed exact-commit CI run `29891756010`.

That evidence closed Phase 6A and authorized one deterministic, local,
credential-free, network-free mock provider. It did not authorize real
provider adapters, SDKs, credentials, or calls.

## 4. Implemented Scope

Phase 6B implements:

- One stateless `DeterministicMockProvider`
- A fixed local mock provider identity
- A fixed adapter identity
- A fixed model identity
- An immutable capability declaration
- Deterministic whitespace-token estimates
- Input and output-token limit enforcement
- Temperature-zero enforcement
- Capability enforcement
- Deterministic hash-derived synthetic output
- Stop-sequence enforcement
- Output-limit enforcement
- Request and trace correlation preservation
- Normalized successful responses
- Normalized safe errors
- Repeatability tests

## 5. Prohibited Scope

Phase 6B contains no:

- OpenAI adapter or call
- Anthropic adapter or call
- Google or Vertex adapter or call
- Bedrock adapter or call
- Provider SDK
- Network client
- Credential access
- Environment-variable access
- Filesystem access
- Subprocess execution
- Randomness
- Current-clock access
- Mutable provider state
- Streaming execution
- Tool execution
- Routing
- Fallback
- Retry execution
- API route
- Infrastructure or production deployment

## 6. Artifact Inventory

| Artifact | Purpose |
|---|---|
| `src/incident_diagnostic_api/providers/mock.py` | Stateless deterministic mock behavior |
| `src/incident_diagnostic_api/providers/__init__.py` | Bounded mock-provider exports |
| `tests/providers/test_mock.py` | Mock-provider behavior and boundary tests |

The Phase 6A contracts and tests remain unchanged.

## 7. Mock Version and Identity

The implementation version is:

```text
deterministic-local-mock-v1
```

The fixed identities are:

- Provider kind: `local_mock`
- Adapter: `local-mock-v1`
- Model: `deterministic-model-v1`

Requests targeting another provider, adapter, or model return a normalized
`INVALID_REQUEST` error.

## 8. Capability Declaration

The mock declares only:

- `text_generation`
- `structured_output`

It does not declare or execute:

- `streaming`
- `tool_calling`

Requests for an unsupported capability fail closed with
`UNSUPPORTED_CAPABILITY`.

## 9. Deterministic Input Boundary

The mock accepts only validated `ProviderRequest` objects and additionally
enforces:

- Exact local mock identity
- Completion time not earlier than request time
- Temperature exactly `0.0`
- Requested capabilities are a subset of declared capabilities
- Estimated input tokens do not exceed 512
- Requested output tokens do not exceed 256

## 10. Deterministic Output

The response is synthetic and derived from:

```text
SHA-256(mock-version + bounded-input-text)
```

Only a bounded digest fragment enters the mock output. The complete input is
not echoed.

Identical validated inputs and explicit timestamps produce identical response
objects. The implementation reads no clock, random source, environment,
filesystem, network, or mutable state.

## 11. Token Estimation and Limits

The mock uses a documented deterministic whitespace-token estimate:

```text
max(1, number of whitespace-separated tokens)
```

This is local test evidence, not a claim of parity with any real provider
tokenizer.

The fixed limits are:

- Maximum estimated input tokens: 512
- Maximum output tokens: 256

An output exceeding the request limit is truncated deterministically and
records the normalized `output_limit` finish reason.

## 12. Stop-Sequence Behavior

The mock selects the earliest matching declared stop sequence. A non-empty
prefix returns with the normalized `stop_sequence` finish reason.

If a stop sequence would remove the entire mock response, the mock returns
`RESPONSE_INVALID` rather than emitting an invalid empty response.

## 13. Normalized Error Behavior

The mock returns Phase 6A `ProviderError` objects for:

- Identity mismatch
- Invalid completion time
- Nonzero temperature
- Unsupported capability
- Input-context limit
- Output-limit configuration error
- Empty response after stop enforcement

Errors preserve request and trace identifiers and contain safe messages only.

## 14. Correlation and Immutability

Every response and error preserves:

- `request_id`
- `trace_id`
- `provider_kind`
- `adapter_id`
- `model_id`

The provider has no instance dictionary or mutable state. Returned contracts
remain frozen under the Phase 6A contract posture.

## 15. Public API Boundary

Phase 6B adds these bounded exports:

- `MOCK_ADAPTER_ID`
- `MOCK_MAXIMUM_INPUT_TOKENS`
- `MOCK_MAXIMUM_OUTPUT_TOKENS`
- `MOCK_MODEL_ID`
- `MOCK_PROVIDER_VERSION`
- `DeterministicMockProvider`
- `MockProviderResult`
- `estimate_mock_tokens`

No generic real-provider protocol, router, retry engine, or adapter registry is
exported.

## 16. Local Test Evidence

Verified local evidence:

- Mock test functions: 17
- Mock pytest cases: 20 passed
- Provider pytest cases: 49 passed
- Complete repository tests: 1,003 passed
- Ruff linting: Passed
- Ruff formatting: Passed
- Strict mypy: Passed
- Dependency validation: Passed
- Diff whitespace validation: Passed

## 17. Capability-Boundary Evidence

Static and executable checks confirmed:

- No real-provider import
- No provider SDK
- No network capability
- No environment or credential access
- No filesystem or subprocess capability
- No dynamic execution
- No current-clock or random input
- No mutable provider state
- No streaming execution
- No tool execution
- No complete-input echo

## 18. Honest Limitations

The deterministic mock does not emulate real provider quality or behavior.
It does not prove:

- Real model access
- Provider authentication
- Real tokenizer equivalence
- Real structured-output differences
- Streaming translation
- Tool-call translation
- Rate-limit behavior
- Provider latency or cost
- Retry or fallback safety
- Cross-provider semantic equivalence
- Production readiness

## 19. Phase 6 Closure Boundary

Phase 6 closure requires the exact Phase 6B implementation commit to pass
remote CI and the bounded Phase 6 evidence to be recorded consistently.

Phase 7 typed enterprise tools remains unauthorized until Phase 6 is
separately closed by an exact-commit evidence gate.

Real provider adapters and calls remain unauthorized after this mock-provider
implementation.

## 20. Remote CI Requirement

Required remote jobs:

- Python quality and contract tests
- Local container build and health verification

Current status:

- Implementation commit: Pending
- Exact-commit CI run: Pending
- Remote CI conclusion: Pending
- Phase 6B closure: Pending

## 21. Current Exit Posture

> PHASE 6B LOCAL GATE: PASSED
> LOCAL QUALITY: PASSED
> REMOTE CI: PENDING
> PHASE 6B CLOSURE: PENDING
> PHASE 6: NOT YET CLOSED
> PHASE 7 TYPED ENTERPRISE TOOLS: NOT AUTHORIZED
> REAL PROVIDER ADAPTERS AND CALLS: NOT AUTHORIZED
