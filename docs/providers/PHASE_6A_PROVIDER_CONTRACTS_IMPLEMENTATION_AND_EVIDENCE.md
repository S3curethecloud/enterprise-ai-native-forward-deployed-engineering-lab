# Phase 6A — Provider-Neutral Contracts Implementation and Evidence

## 1. Purpose

This document records the bounded local implementation of provider-neutral
contracts for the first slice of Phase 6 multi-provider abstraction.

Phase 6A establishes immutable request, response, capability, usage, and error
contracts. It does not create a provider adapter, call a model, transmit a
prompt, load credentials, route between providers, or authorize external
network access.

## 2. Current Decision

> PHASE 6A LOCAL IMPLEMENTATION: COMPLETE
> PHASE 6A IMPLEMENTATION COMMIT: AUTHORIZED
> PHASE 6A REMOTE CI: PENDING
> PHASE 6A CLOSURE: PENDING
> PHASE 6B MOCK PROVIDER: NOT AUTHORIZED
> REAL PROVIDER ADAPTERS OR CALLS: NOT AUTHORIZED

Phase 6A may be committed for exact-commit CI validation.

## 3. Prior-Phase Authority

Phase 5J closed after exact-commit CI run `29866079305` passed against
closure commit `4d7922863d015131456b053512458b35d16a57e4`.

That closure completed Phase 5 permission-aware RAG and authorized the
initial bounded Phase 6 scope:

- Common provider request and response contracts
- Capability metadata
- Normalized errors
- A later deterministic local mock provider
- Contract tests

It did not authorize OpenAI, Anthropic, Google, Vertex, Bedrock, or other real
provider adapters or calls.

## 4. Implemented Scope

Phase 6A implements:

- Versioned provider-neutral contracts
- Four declared provider identities
- Four declared provider capabilities
- Immutable request envelopes
- Immutable successful-response envelopes
- Explicit capability declarations
- Normalized token-usage evidence
- Normalized finish reasons
- Ten normalized provider error codes
- Deterministic error-category mappings
- Deterministic retryability mappings
- Positive, negative, boundary, serialization, and immutability tests

Provider identities in a contract are declarations only. They do not prove
that an adapter exists or that provider access is configured.

## 5. Prohibited Scope

Phase 6A contains no:

- Provider protocol or adapter interface
- Provider execution method
- Deterministic mock-provider execution
- OpenAI adapter or call
- Anthropic adapter or call
- Google or Vertex adapter or call
- Bedrock adapter or call
- Provider SDK
- HTTP or other network client
- Credential or secret field
- Raw provider response field
- Prompt execution
- Streaming execution
- Tool invocation
- Provider routing or fallback
- Retry execution
- API route
- Infrastructure mutation
- Cloud or production deployment

## 6. Artifact Inventory

| Artifact | Purpose |
|---|---|
| `src/incident_diagnostic_api/providers/contracts.py` | Provider-neutral contracts and invariants |
| `src/incident_diagnostic_api/providers/__init__.py` | Bounded Phase 6A public exports |
| `tests/providers/test_contracts.py` | Positive, negative, and invariant tests |
| `tests/providers/__init__.py` | Provider-test package marker |

## 7. Contract Version

The provider contract version is:

```text
provider-contract-v1
```

This version is distinct from the repository-wide executable-contract version
and allows provider-boundary evolution to remain explicit.

## 8. Provider Identity Boundary

The contract recognizes four provider identities:

- `local_mock`
- `openai`
- `anthropic`
- `google_vertex`

Only identity metadata is represented. No identity has an executable adapter
in Phase 6A.

## 9. Capability Metadata

The bounded capability vocabulary is:

- `text_generation`
- `structured_output`
- `streaming`
- `tool_calling`

Every model declaration must contain at least one unique capability.
Provider requests must explicitly request text generation and cannot contain
duplicate capability values.

Capability declaration does not grant runtime authority.

## 10. Request Contract

`ProviderRequest` records:

- Request and trace correlation
- Provider, adapter, and model identity
- Bounded input text
- Requested capabilities
- Maximum output tokens
- Bounded temperature
- Bounded unique stop sequences
- An aware request timestamp

Unknown fields are rejected. API keys, authorization headers, credentials,
and secrets cannot enter the contract.

## 11. Response and Usage Contracts

`ProviderResponse` represents only a normalized successful response. It
records correlation, provider identity, bounded output text, a normalized
finish reason, normalized usage, and an aware completion timestamp.

`ProviderUsage` requires:

```text
total_tokens = input_tokens + output_tokens
```

This invariant prevents inconsistent usage evidence from being accepted.

## 12. Normalized Error Contract

Ten provider-independent error codes cover request, authentication,
authorization, unsupported capability, context limit, capacity, timeout,
dependency, response, and internal failures.

Each error code maps deterministically to one category and one retryability
posture. A caller cannot relabel a non-retryable error as retryable or change
its category.

Errors contain a bounded safe message. Raw provider payloads and sensitive
implementation details are excluded.

## 13. Immutability and Fail-Closed Validation

All provider contracts inherit the repository's frozen, extra-forbid,
validation-on-default contract posture.

The implementation rejects:

- Unknown fields
- Duplicate capabilities
- Missing text-generation capability
- Duplicate stop sequences
- Invalid temperature or token bounds
- Naive timestamps
- Empty output
- Inconsistent usage totals
- Incorrect error categories
- Incorrect retryability
- Sensitive or raw-provider fields

## 14. Local Test Evidence

Verified local evidence:

- Provider test functions: 19
- Provider pytest cases: 29 passed
- Complete repository tests: 983 passed
- Ruff linting: Passed
- Ruff formatting: Passed
- Strict mypy: Passed
- Dependency validation: Passed
- Diff whitespace validation: Passed

## 15. Capability-Boundary Evidence

Static inspection confirmed:

- No provider SDK import
- No network-client import
- No subprocess import
- No dynamic execution
- No provider invocation interface
- No provider execution function
- No credential-bearing field
- No raw-provider-response field

Phase 6A remains local, deterministic, contract-only, and dependency-free.

## 16. Honest Limitations

Phase 6A does not demonstrate provider portability in operation. It defines
the common language that later adapters must satisfy.

It does not prove:

- Authentication against any provider
- Real model compatibility
- Provider-specific structured-output fidelity
- Tool-call translation
- Streaming behavior
- Retry or fallback safety
- Cost or latency behavior
- Regional availability
- Production readiness

## 17. Phase 6B Boundary

Phase 6B is limited to a deterministic local mock provider and its contract
tests. It must not add network access, provider SDKs, real credentials, or
real provider calls.

Phase 6B remains unauthorized until the exact Phase 6A implementation commit
passes remote CI and that evidence is recorded.

## 18. Remote CI Requirement

Phase 6A requires the exact implementation commit to pass:

- Python quality and contract tests
- Local container build and health verification

Current status:

- Implementation commit: Pending
- Exact-commit CI run: Pending
- Remote CI conclusion: Pending
- Phase 6A closure: Pending

## 19. Current Exit Posture

> PHASE 6A LOCAL GATE: PASSED
> LOCAL QUALITY: PASSED
> REMOTE CI: PENDING
> PHASE 6A CLOSURE: PENDING
> PHASE 6B DETERMINISTIC LOCAL MOCK PROVIDER: NOT AUTHORIZED
> REAL PROVIDER ADAPTERS AND CALLS: NOT AUTHORIZED
