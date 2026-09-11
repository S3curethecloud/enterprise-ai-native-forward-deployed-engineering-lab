# Phase 7E — Deterministic Tool Dispatch Evidence Architecture and Authority Gate

## 1. Gate Purpose

This gate determines what Phase 7E should be before any Phase 7E implementation begins.

It defines the selected capability, its value, interfaces, invariants, failure model, evidence requirements, implementation boundary, and authority boundary.

This document is architecture and authority evidence only. It does not implement Phase 7E.

## 2. Canonical Prior State

Phase 7D is canonically closed.

Verified prior evidence:

- Phase 7D corrected implementation commit: `8d2b0ec68f283a9449fab35963b5ceb6a7c70606`
- Phase 7D corrected implementation CI run: `30794548243`
- Phase 7D documentation closure commit: `3fe514b6f719e988ada3bef86af31f003fef7f39`
- Phase 7D documentation closure CI run: `34632778968`
- Phase 7D documentation closure CI result: `SUCCESS`
- Focused Phase 7D tool tests: 111 passed
- Complete repository tests at Phase 7D implementation verification: 1,114 passed

Phase 7D provides a fail-closed deterministic local dispatcher. Registered read-only tools may return deterministic local mock results. Side-effecting tools fail closed with `APPROVAL_REQUIRED`. Real execution-enabled definitions and general shell access fail closed with `ACCESS_DENIED`.

Real tool execution, real enterprise integrations, real provider calls, tool credentials, network access, shell execution, filesystem mutation, infrastructure mutation, cloud deployment, production deployment, and external system mutation remain unauthorized.

## 3. Current Gate Decision

> PHASE 7D: CLOSED
> PHASE 7E CAPABILITY: DETERMINED
> PHASE 7E SELECTED CAPABILITY: DETERMINISTIC TOOL DISPATCH EVIDENCE
> PHASE 7E ARCHITECTURE STATUS: DOCUMENTED CANDIDATE
> PHASE 7E IMPLEMENTATION STATUS: NOT STARTED
> PHASE 7E IMPLEMENTATION AUTHORITY: NONE
> REAL TOOL EXECUTION AUTHORITY: NONE
> POLICY AUTHORITY: UNCHANGED
> HUMAN APPROVAL AUTHORITY: UNCHANGED
> EVIDENCE PERSISTENCE AUTHORITY: NONE

The selected Phase 7E capability is a typed, deterministic, content-minimized evidence envelope derived from a validated `ToolRequest`, its Phase 7D `ToolResult | ToolError`, and the relevant tool-registry metadata.

The evidence object describes what the Phase 7D dispatcher did. It does not authorize what the dispatcher may do.

## 4. Why This Capability Is Next

Phase 7A established governed tool metadata.

Phase 7B established typed request, result, and error envelopes.

Phase 7C established deterministic local mock behavior.

Phase 7D established fail-closed deterministic local dispatch.

The next missing tool-layer capability is evidence that can answer, without inspecting hidden process state:

- Which validated tool request was evaluated?
- Which tool identity and registry version were relevant?
- Which dispatcher version produced the outcome?
- Was the tool registered?
- What side-effect, risk, and approval metadata applied?
- Did the dispatcher produce a deterministic local mock result or a fail-closed error?
- Which normalized error code and category applied?
- Did the outcome preserve request and trace identity?
- Did any prohibited execution surface become enabled?

This capability improves auditability and later integration readiness without granting policy, approval, network, credential, or real execution authority.

## 5. Alternatives Considered

### 5.1 Policy wrapper around dispatcher admission — not selected

Phase 8 owns deterministic policy routing and the `ALLOW`, `DENY`, and `APPROVAL_REQUIRED` authorization decision.

Implementing a policy wrapper in Phase 7E would collapse the tool-registry/dispatcher boundary into policy authority and would preempt Phase 8.

Disposition: `DEFER_TO_PHASE_8`.

### 5.2 Human-approval placeholder contract — not selected

Phase 9 owns trusted consequential-action approval.

A Phase 7E approval contract would risk creating an untrusted placeholder that later appears authoritative.

Disposition: `DEFER_TO_PHASE_9`.

### 5.3 Dry-run execution plan — not selected

A dry-run execution plan introduces action-planning semantics before deterministic policy and trusted approval are established.

It is not required to prove the current deterministic local tool boundary.

Disposition: `DEFER`.

### 5.4 Tool capability exposure API — not selected

An API route would create a new externally callable surface and is unnecessary to establish the next internal tool-layer invariant.

Disposition: `DEFER`.

### 5.5 Deterministic tool dispatch evidence — selected

This capability is directly downstream of Phase 7D, adds no new execution authority, preserves the Phase 8 and Phase 9 responsibility boundaries, and creates a reusable evidence primitive for later runtime and evidence-service integration.

Disposition: `SELECTED_FOR_PHASE_7E`.

## 6. Business and Engineering Value

Phase 7E should make the tool layer easier to review, test, explain, and integrate.

Value:

- Security reviewers can inspect why a dispatch attempt completed locally or failed closed.
- Developers can verify that tool identity, registry metadata, dispatcher version, and outcome remain correlated.
- Auditors can distinguish local mock completion from real enterprise execution.
- Future policy work can consume a clean tool boundary without inheriting implicit dispatcher state.
- Future evidence-service work can persist a bounded record rather than raw tool payloads.
- Interview demonstrations gain an evidence-backed explanation of controlled tool invocation without claiming live enterprise integration.

## 7. Architectural Boundary

Current Phase 7D flow:

```text
ToolRequest
  -> ToolRegistry lookup
  -> Phase 7D deterministic dispatcher
  -> ToolResult | ToolError
```

Selected Phase 7E flow:

```text
ToolRequest
  + ToolResult | ToolError
  + ToolRegistry metadata
  -> deterministic evidence builder
  -> ToolDispatchEvidence
```

Explicitly not part of Phase 7E:

```text
ToolDispatchEvidence -X-> policy authorization
ToolDispatchEvidence -X-> human approval
ToolDispatchEvidence -X-> credential issuance
ToolDispatchEvidence -X-> provider call
ToolDispatchEvidence -X-> network call
ToolDispatchEvidence -X-> real tool execution
ToolDispatchEvidence -X-> evidence persistence
ToolDispatchEvidence -X-> production mutation
```

Phase 7E is observational and validating. It is not authoritative for permission or execution.

## 8. Relationship to Existing Repository Evidence

CT-07 `TraceEvent` remains the repository-wide lifecycle trace contract.

Phase 7E must not replace CT-07, expand the CT-07 lifecycle event allowlist, or redefine repository-wide observability.

Phase 7E is tool-domain evidence only. A later authorized integration phase may reference a Phase 7E evidence object from a lifecycle trace or evidence-service record.

Phase 7E must also remain distinct from Phase 5J retrieval-specific telemetry. Domain-specific evidence must not silently become a second global tracing system.

## 9. Proposed Phase 7E Contract

The following is an architecture contract, not implemented code.

```python
TOOL_DISPATCH_EVIDENCE_VERSION = "7e.1"

class ToolRegistryResolution(StrEnum):
    REGISTERED = "registered"
    NOT_REGISTERED = "not_registered"

class ToolDispatchOutcomeKind(StrEnum):
    RESULT = "result"
    ERROR = "error"

class ToolDispatchEvidence(VersionedContract):
    tool_dispatch_evidence_version: Literal["7e.1"]

    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    tool_name: ToolName

    tool_contract_version: OpaqueIdentifier
    tool_envelope_version: OpaqueIdentifier
    tool_registry_version: OpaqueIdentifier
    tool_dispatcher_version: OpaqueIdentifier

    registry_resolution: ToolRegistryResolution

    capability: ToolCapability | None
    side_effect: ToolSideEffect | None
    risk_tier: ToolRiskTier | None
    approval_requirement: ToolApprovalRequirement | None
    authorization_required: bool | None
    execution_enabled: bool | None
    general_shell_access: bool | None

    outcome_kind: ToolDispatchOutcomeKind
    result_status: ToolResultStatus | None
    error_code: ToolErrorCode | None
    error_category: ToolErrorCategory | None
    retryable: bool | None

    idempotency_key_present: bool
    argument_names: tuple[ToolArgumentName, ...]
    output_names: tuple[ToolArgumentName, ...]

    requested_at: Timestamp
    outcome_at: Timestamp
```

The exact syntax may be refined during an independently authorized implementation review, but the semantics and authority boundary defined here must not be weakened without a new architecture decision.

## 10. Content-Minimization Rule

The Phase 7E evidence object must not copy raw tool payload content.

It may contain:

- Request identity
- Trace identity
- Tool identity
- Version identifiers
- Registry metadata
- Outcome classification
- Normalized error code/category/retryability
- Whether an idempotency key was present
- Sorted argument field names
- Sorted output field names
- Request and outcome timestamps

It must not contain:

- Raw argument values
- Raw output values
- Raw idempotency-key value
- Credentials
- Tokens
- Secrets
- Provider keys
- Environment variables
- Filesystem content
- Arbitrary exception text
- Hidden reasoning
- Complete model prompts or responses

`ToolError.safe_message` should not be copied into Phase 7E evidence. The normalized error code and category are sufficient for the initial evidence contract.

## 11. Proposed Builder Interface

The planned implementation interface is:

```python
def build_deterministic_tool_dispatch_evidence(
    request: ToolRequest,
    outcome: ToolDispatchOutcome,
    *,
    registry: ToolRegistry = DEFAULT_TOOL_REGISTRY,
) -> ToolDispatchEvidence:
    ...
```

The builder must be a pure in-process function.

It must not:

- Call the Phase 7D dispatcher itself
- Retry dispatch
- Change the supplied outcome
- Authorize a tool
- Approve a tool
- Generate credentials
- Persist evidence
- Read the current clock
- Generate a UUID
- Read environment state
- Read or write files
- Open sockets
- Spawn subprocesses
- Import provider SDKs

The outcome timestamp must be derived from the existing `ToolResult.completed_at` or `ToolError.occurred_at`. No new runtime time source is required.

## 12. Contract Invariants

### 12.1 Identity preservation

The request and outcome must have identical:

- `request_id`
- `trace_id`
- `tool_name`

Mismatch is invalid evidence and must fail closed.

### 12.2 Version lineage

The evidence must record the exact:

- Tool contract version
- Tool envelope version
- Registry version
- Dispatcher version
- Phase 7E evidence version

Version values must be derived from validated source objects or version constants, not caller-supplied free text.

### 12.3 Registry resolution

If the tool is found in the supplied registry:

- `registry_resolution = registered`
- Registry metadata fields must exactly reflect that definition.

If registry lookup fails:

- `registry_resolution = not_registered`
- Definition-derived metadata fields must be absent.
- The supplied outcome must be `ToolErrorCode.TOOL_NOT_REGISTERED`.

A missing registry definition must never be converted into a successful result.

### 12.4 Successful-result consistency

A `ToolResult` is valid Phase 7E evidence only when the registry definition is consistent with the closed Phase 7D safety boundary:

- `side_effect == NONE`
- `execution_enabled == False`
- `general_shell_access == False`
- approval requirement is not `HUMAN_APPROVAL`

The builder does not grant permission. These checks only prevent contradictory evidence from being created for a supplied result.

### 12.5 Error consistency

For `ToolError`:

- `outcome_kind = error`
- `result_status` must be absent.
- `output_names` must be empty.
- Error code, category, and retryability must exactly match the validated `ToolError`.

For `ToolResult`:

- `outcome_kind = result`
- `result_status = completed`
- Error code, category, and retryability must be absent.

### 12.6 Temporal consistency

`outcome_at` must not precede `requested_at`.

No current-clock comparison is required.

### 12.7 Deterministic ordering

`argument_names` and `output_names` must use stable deterministic ordering.

Identical validated request, outcome, and registry inputs must produce equal evidence objects.

## 13. Independent Verification, Not Second Authorization

The evidence builder may verify that the supplied outcome is consistent with the closed Phase 7D dispatcher rules.

This is not a second policy engine.

It must not emit `ALLOW`, `DENY`, or a policy decision identifier.

It must not interpret user identity, tenant membership, resource policy, environment policy, approval state, or policy version as authorization facts.

Those semantics remain Phase 8 responsibility.

`APPROVAL_REQUIRED` in a Phase 7D `ToolError` remains a fail-closed dispatcher disposition indicating that the side-effecting path cannot proceed in the current phase. It must not be represented as evidence that a trusted policy engine evaluated the request or that a human approval exists.

## 14. Failure Model

### FM-7E-01 — Request/outcome identity mismatch

Expected behavior: reject evidence construction with a controlled invariant error.

Must not: rewrite identifiers or choose one side as authoritative.

### FM-7E-02 — Outcome timestamp precedes request timestamp

Expected behavior: reject evidence construction.

Must not: repair timestamps or read the current clock.

### FM-7E-03 — Registry miss paired with non-`TOOL_NOT_REGISTERED` outcome

Expected behavior: reject contradictory evidence.

Must not: infer missing metadata.

### FM-7E-04 — Successful result contradicts registry safety metadata

Examples:

- Side-effecting definition with successful result
- `execution_enabled=True` with successful result
- `general_shell_access=True` with successful result
- Human-approval definition with successful result

Expected behavior: reject evidence construction.

Must not: reinterpret the result as authorized.

### FM-7E-05 — Error metadata contradiction

Expected behavior: rely on existing typed `ToolError` invariants and reject malformed or inconsistent error evidence.

### FM-7E-06 — Evidence builder failure

Expected behavior: report a controlled evidence-construction failure.

Must not:

- Re-run the dispatcher
- Convert an error into success
- Create a side effect
- Persist a partial record as if complete

Phase 7E does not yet define evidence-criticality policy for a live execution path because no live execution path is authorized.

### FM-7E-07 — Sensitive payload leakage

Expected behavior: tests must prove raw argument values, output values, idempotency keys, credentials, and arbitrary error text are absent from the evidence model.

### FM-7E-08 — Nondeterministic evidence

Expected behavior: identical validated inputs must produce equal evidence.

Clock reads, UUID generation, randomness, environment access, network access, and mutable history are prohibited.

## 15. Security Boundary

Phase 7E must preserve all existing prohibitions.

No Phase 7E implementation may introduce:

- `requests`
- `httpx`
- `boto3`
- Kubernetes client SDKs
- Jira client SDKs
- ServiceNow client SDKs
- Database client execution
- `socket`
- `subprocess`
- `paramiko`
- General `open(...)` filesystem access for runtime behavior
- `exec(...)`
- `eval(...)`
- Credential reads
- Secret reads
- Network calls
- Provider calls
- External mutations

Static tests should continue to enforce prohibited imports and calls for the Phase 7 tool package.

## 16. Authority Matrix

| Component | Phase 7E authority | Phase 7E non-authority |
|---|---|---|
| Model | None added | Cannot authorize, approve, or execute tools |
| Runtime | None added | No new tool or policy authority |
| Tool registry | Supplies immutable tool metadata | Does not authorize execution |
| Phase 7D dispatcher | Existing deterministic local mock dispatch only | No real execution, policy, or approval authority |
| Phase 7E evidence builder | Validate and describe supplied dispatch facts | Cannot alter outcome, authorize, approve, execute, persist, or retry |
| Policy engine | None implemented by Phase 7E | Phase 8 remains owner of authorization decisions |
| Human approval | None implemented by Phase 7E | Phase 9 remains owner of trusted approval |
| Evidence service | No new persistence integration | No durable tool-evidence write authority in Phase 7E |
| Tool service | No real tool execution | No external side effects |

## 17. Proposed Future Implementation File Boundary

If a later gate explicitly grants bounded Phase 7E implementation authority, the preferred initial file boundary is:

```text
src/incident_diagnostic_api/tools/evidence.py
src/incident_diagnostic_api/tools/__init__.py
tests/tools/test_evidence.py
docs/tools/PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_EVIDENCE_IMPLEMENTATION_AND_EVIDENCE.md
```

The initial Phase 7E implementation should not require modification of:

```text
src/incident_diagnostic_api/tools/dispatcher.py
src/incident_diagnostic_api/tools/mock.py
src/incident_diagnostic_api/tools/registry.py
src/incident_diagnostic_api/tools/contracts.py
```

If implementation review determines one of those closed surfaces must change, that expansion must be separately justified before mutation.

No API route, evidence-service persistence adapter, database schema, migration, network client, provider adapter, policy engine, or approval service is part of the proposed initial Phase 7E implementation boundary.

## 18. Future Implementation Test Requirements

A later authorized Phase 7E implementation must include evidence for at least these cases.

### Successful deterministic local mock paths

- Every registered read-only tool produces a valid Phase 7E evidence object when paired with its valid Phase 7D result.
- Request, trace, tool, contract, registry, dispatcher, and evidence versions are preserved.
- Argument and output field names are stable and sorted.
- Raw argument and output values are absent.

### Fail-closed paths

- Side-effecting Jira comment produces evidence for `APPROVAL_REQUIRED`.
- Side-effecting ServiceNow update produces evidence for `APPROVAL_REQUIRED`.
- A registry definition with real execution enabled cannot produce accepted successful-result evidence.
- A registry definition with general shell access cannot produce accepted successful-result evidence.
- Registry lookup failure is represented only with `TOOL_NOT_REGISTERED`.

### Invariant failures

- Request ID mismatch fails.
- Trace ID mismatch fails.
- Tool-name mismatch fails.
- Time inversion fails.
- Result/error field contradictions fail.

### Determinism and minimization

- Repeated construction from identical inputs yields equal evidence.
- No current-clock, UUID, random, environment, filesystem, network, subprocess, or provider dependency is required.
- Raw idempotency-key values are never copied.
- Arbitrary safe-message or exception text is not copied.

### Regression

- All Phase 7A–7D tests remain green.
- Complete repository tests remain green.
- Ruff linting passes.
- Ruff formatting passes.
- Strict MyPy passes.
- Dependency validation passes.
- Both required CI jobs pass against the exact implementation commit.

## 19. Evidence Required Before Phase 7E May Close

A later implementation gate must preserve:

- Exact implementation commit SHA
- Exact GitHub Actions run ID for that commit
- Focused Phase 7E test count
- Complete tools test count
- Complete repository test count
- Ruff result
- Formatting result
- Strict MyPy result
- Dependency-integrity result
- Python quality and contract-tests job result
- Local container build and health-verification job result
- Exact implementation file boundary
- Confirmed absence of prohibited execution surfaces
- Known limitations

A documentation-only closure commit must then record the verified implementation evidence and itself pass exact-commit CI before Phase 7E may be marked closed.

## 20. Phase 7E Definition of Done

Phase 7E will be eligible for closure only when a separately authorized implementation proves that:

1. A typed Phase 7E evidence contract exists.
2. The evidence builder is pure and deterministic.
3. Request/outcome identity mismatches fail closed.
4. Registry metadata is represented exactly when available.
5. Registry misses cannot be laundered into success.
6. Successful-result evidence cannot contradict Phase 7D safety metadata.
7. Result and error evidence are mutually consistent.
8. Temporal inversion fails closed.
9. Raw tool argument/output values are not copied into the evidence record.
10. No credentials, secrets, provider SDKs, network, shell, filesystem mutation, or external mutation are introduced.
11. CT-07 remains the repository-wide lifecycle trace contract.
12. Phase 8 policy authority remains untouched.
13. Phase 9 human-approval authority remains untouched.
14. All prior Phase 7 tests remain green.
15. Exact-commit CI passes for the implementation commit.
16. Closure documentation is committed and passes exact-commit CI.

## 21. Explicit Non-Goals

Phase 7E is not:

- A policy engine
- An approval service
- An executor
- An MCP server
- A live Jira integration
- A live ServiceNow integration
- A Kubernetes integration
- A cloud API integration
- A database query executor
- A credential broker
- A network gateway
- An evidence database
- A global observability platform
- A production deployment feature

## 22. Honest Claim Boundary

After architecture acceptance but before implementation, the strongest valid claim is:

> Phase 7E deterministic tool-dispatch evidence is architecturally defined. Implementation has not started, and no new runtime or execution authority has been granted.

After a future implementation commit passes its gate but before closure documentation CI, the strongest claim may become:

> The Phase 7E deterministic local evidence builder is implemented and tested at the named commit; Phase 7E closure remains pending.

No Phase 7E state permits a claim of real enterprise tool execution unless a later separately governed phase explicitly implements and verifies that capability.

## 23. Implementation Authority Decision

This architecture gate does not grant implementation authority.

```text
PHASE_7E_ARCHITECTURE_DETERMINATION=SELECTED
PHASE_7E_SELECTED_CAPABILITY=DETERMINISTIC_TOOL_DISPATCH_EVIDENCE
PHASE_7E_IMPLEMENTATION=NOT_STARTED
PHASE_7E_IMPLEMENTATION_AUTHORITY=NONE
PHASE_7E_REPOSITORY_SOURCE_MUTATION_AUTHORITY=NONE
PHASE_7E_TEST_MUTATION_AUTHORITY=NONE
PHASE_7E_API_ROUTE_AUTHORITY=NONE
PHASE_7E_POLICY_AUTHORITY=NONE
PHASE_7E_APPROVAL_AUTHORITY=NONE
PHASE_7E_EVIDENCE_PERSISTENCE_AUTHORITY=NONE
PHASE_7E_NETWORK_AUTHORITY=NONE
PHASE_7E_CREDENTIAL_AUTHORITY=NONE
PHASE_7E_EXTERNAL_MUTATION_AUTHORITY=NONE
```

## 24. Next Disciplined Gate

After this architecture-and-authority artifact is independently reviewed and its exact documentation commit passes CI, the next gate should be:

```text
NEXT_GATE=
PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_EVIDENCE_
INDEPENDENT_ARCHITECTURE_ACCEPTANCE_AND_
BOUNDED_IMPLEMENTATION_AUTHORITY_REVIEW
```

That review must determine whether the proposed contract, invariants, minimization rules, failure behavior, test requirements, and four-file future implementation boundary are safe and sufficient.

It may grant bounded implementation authority only if the architecture is accepted without collapsing Phase 8 policy authority, Phase 9 approval authority, CT-07 lifecycle tracing, or the prohibition on real tool execution.

Until that separate authority review passes, Phase 7E implementation remains unauthorized.
