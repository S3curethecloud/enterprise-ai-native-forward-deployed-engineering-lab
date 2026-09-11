# Phase 7E — Deterministic Tool Dispatch Outcome Consistency Evidence Architecture and Authority Gate R2

## 1. Purpose

This document is the complete standalone R2 replacement architecture for Phase 7E.

It resolves findings A1–A11 from the independent R1 architecture review while preserving the high-level Phase 7E direction: add a deterministic, content-minimized tool-domain evidence primitive without adding policy, approval, persistence, provider, network, credential, shell, filesystem, or real tool-execution authority.

This document is architecture and authority evidence only.

It does not implement Phase 7E.

## 2. Historical Lineage and Supersession

Phase 7D is canonically closed.

The first Phase 7E architecture candidate was preserved by:

```text
PHASE_7E_R1_ARCHITECTURE_COMMIT=
3124d373e1cf8445a0cb00c78a1edff1303ba445

PHASE_7E_R1_ARCHITECTURE_CI_RUN=34633962087
PHASE_7E_R1_ARCHITECTURE_CI_CONCLUSION=SUCCESS
```

The independent R1 review was preserved by:

```text
PHASE_7E_R1_REVIEW_COMMIT=
046b7eead6238392840e6a49eb5f39157832c426

PHASE_7E_R1_REVIEW_CI_RUN=34634892579
PHASE_7E_R1_REVIEW_CI_CONCLUSION=SUCCESS
```

R1 was rejected for implementation because its evidence semantics exceeded what its proposed inputs could prove.

R1 and its review remain historical repository evidence and must not be rewritten or deleted.

This R2 document supersedes R1 only for future Phase 7E architecture and implementation consideration.

```text
R1_ARCHITECTURE_HISTORY_PRESERVED=YES
R1_REVIEW_HISTORY_PRESERVED=YES
R1_REWRITTEN=NO
R1_DELETED=NO
R2_SUPERSEDES_R1_FOR_FUTURE_IMPLEMENTATION_CONSIDERATION=YES
REPOSITORY_HISTORY_REWRITE_AUTHORITY=NONE
```

## 3. Current Gate Authority

```text
GATE_REVISION=R2
GATE_TYPE=BOUNDED_SEMANTIC_CORRECTION_AND_STANDALONE_REPLACEMENT_ARCHITECTURE_PREPARATION
GATE_REPOSITORY_EFFECT=DOCUMENTATION_ONLY_SINGLE_FILE

SOURCE_CODE_MUTATION_AUTHORITY=NONE
TEST_MUTATION_AUTHORITY=NONE
EXPORT_MUTATION_AUTHORITY=NONE
DISPATCHER_MUTATION_AUTHORITY=NONE
MOCK_MUTATION_AUTHORITY=NONE
REGISTRY_MUTATION_AUTHORITY=NONE
TOOL_CONTRACT_MUTATION_AUTHORITY=NONE
API_ROUTE_AUTHORITY=NONE
POLICY_AUTHORITY=NONE
APPROVAL_AUTHORITY=NONE
EVIDENCE_PERSISTENCE_AUTHORITY=NONE
NETWORK_AUTHORITY=NONE
CREDENTIAL_AUTHORITY=NONE
FILESYSTEM_RUNTIME_AUTHORITY=NONE
PROVIDER_INTEGRATION_AUTHORITY=NONE
REAL_TOOL_EXECUTION_AUTHORITY=NONE
EXTERNAL_MUTATION_AUTHORITY=NONE
```

## 4. R2 Architecture Decision

The selected Phase 7E capability is:

```text
PHASE_7E_SELECTED_CAPABILITY=
DETERMINISTIC_TOOL_DISPATCH_OUTCOME_CONSISTENCY_EVIDENCE
```

The Phase 7E capability evaluates whether a validated `ToolRequest` and a supplied `ToolResult | ToolError` are mutually consistent with each other and with the supplied valid `ToolRegistry` under the bounded Phase 7D local-dispatch safety semantics.

If the inputs are consistent, Phase 7E returns a frozen in-process, content-minimized evidence value.

If the inputs are inconsistent, Phase 7E raises a controlled, bounded evidence-construction error and returns no evidence value.

Phase 7E does not prove which function produced the supplied outcome.

Phase 7E does not prove which registry instance was historically used by any producer.

Phase 7E does not prove that a real enterprise tool executed.

## 5. Exact Claim Boundary

The strongest claim Phase 7E is designed to establish is:

> The supplied typed tool outcome is internally consistent with the supplied typed request and the evaluated registry declarations under the documented Phase 7E consistency rules.

Phase 7E is not designed to establish:

```text
DISPATCH_PRODUCER_PROVENANCE
REGISTRY_PRODUCER_PROVENANCE
REAL_EXECUTION_PROVENANCE
NETWORK_EXECUTION_PROVENANCE
CREDENTIAL_USE_PROVENANCE
POLICY_AUTHORIZATION
HUMAN_APPROVAL
DURABLE_EVIDENCE_PERSISTENCE
TAMPER_EVIDENCE
```

Explicit posture:

```text
EVIDENCE_SCOPE=OUTCOME_CONSISTENCY_ONLY
DISPATCH_PRODUCER_PROVENANCE=NOT_ESTABLISHED
REGISTRY_PRODUCER_PROVENANCE=NOT_ESTABLISHED
REAL_EXECUTION=NOT_ESTABLISHED_AND_NOT_AUTHORIZED
POLICY_DECISION=NOT_ESTABLISHED
HUMAN_APPROVAL=NOT_ESTABLISHED
PERSISTENCE=NOT_ESTABLISHED
```

## 6. Why R2 Uses Outcome Consistency Rather Than Producer Provenance

The current public Phase 7 package exposes typed `ToolResult` and `ToolError` contracts.

It also publicly exposes deterministic mock result/error builders.

A valid `ToolResult` or `ToolError` can therefore exist without being produced by `dispatch_deterministic_local_tool_request`.

The current outcome contracts do not carry a cryptographic receipt, dispatcher identity, registry receipt, or producer binding.

Therefore:

```text
VALID_TYPED_OUTCOME != PROOF_OF_DISPATCHER_PRODUCTION
VALID_TYPED_OUTCOME != PROOF_OF_REGISTRY_PROVENANCE
```

R2 intentionally refuses to manufacture provenance by copying current code-version constants into fields that would be interpreted as historical producer facts.

A future separately governed phase may introduce authoritative dispatch receipts if the project later requires producer provenance.

That future work is outside Phase 7E R2.

## 7. Existing Phase 7 Progression

Phase 7 currently progresses as follows:

```text
Phase 7A -> governed typed tool registry metadata
Phase 7B -> bounded typed request/result/error envelopes
Phase 7C -> deterministic local mock result/error construction
Phase 7D -> fail-closed deterministic local dispatcher
Phase 7E -> deterministic outcome-consistency evidence
```

Phase 7E adds reviewable evidence without adding execution authority.

## 8. Architectural Flow

Existing bounded tool path:

```text
ToolRequest
    |
    v
Phase 7D deterministic local dispatcher
    |
    +--> ToolResult
    |
    +--> ToolError
```

Phase 7E accepts already-existing typed values:

```text
Validated ToolRequest
        +
Supplied ToolResult | ToolError
        +
Supplied valid ToolRegistry
        |
        v
Phase 7E deterministic consistency evaluator
        |
        +--> CONSISTENT
        |       |
        |       v
        |   ToolOutcomeEvidence
        |
        +--> INCONSISTENT
                |
                v
        ToolOutcomeEvidenceError
```

The evaluator must not call the Phase 7D dispatcher.

The evaluator must not retry tool dispatch.

The evaluator must not convert an inconsistent outcome into a consistent one.

## 9. R2 Proposed Contract Namespace

R1's unimplemented `ToolDispatchEvidence` architecture name is superseded.

No runtime `ToolDispatchEvidence` release occurred, so R2 may begin the corrected runtime contract at `7e.1` without implying compatibility with an implemented R1 object.

Proposed runtime names:

```text
TOOL_OUTCOME_EVIDENCE_VERSION=7e.1
ToolOutcomeKind
ToolOutcomeConsistencyStatus
ToolOutcomeEvidence
ToolOutcomeEvidenceErrorCode
ToolOutcomeEvidenceError
build_deterministic_tool_outcome_evidence
```

Exact Python syntax may be refined during a separately authorized implementation preparation/review, but the semantics in this R2 document must not be weakened without a new architecture decision.

## 10. Proposed Evidence Contract

Architecture-level contract:

```python
TOOL_OUTCOME_EVIDENCE_VERSION = "7e.1"

class ToolOutcomeKind(StrEnum):
    RESULT = "result"
    ERROR = "error"

class ToolOutcomeConsistencyStatus(StrEnum):
    CONSISTENT = "consistent"

class ToolOutcomeEvidence(VersionedContract):
    tool_outcome_evidence_version: Literal["7e.1"]

    request_id: OpaqueIdentifier
    trace_id: OpaqueIdentifier
    tool_name: ToolName

    tool_contract_version: OpaqueIdentifier
    tool_envelope_version: OpaqueIdentifier

    evaluated_registry_version: str
    evaluated_dispatch_semantics_version: OpaqueIdentifier

    registry_declared_capability: ToolCapability
    registry_declared_side_effect: ToolSideEffect
    registry_declared_risk_tier: ToolRiskTier
    registry_declared_idempotency_requirement: ToolIdempotencyRequirement
    registry_declared_approval_requirement: ToolApprovalRequirement
    registry_declared_timeout_seconds: int
    registry_declared_authorization_required: bool
    registry_declared_execution_enabled: bool
    registry_declared_general_shell_access: bool

    outcome_kind: ToolOutcomeKind
    consistency_status: Literal[ToolOutcomeConsistencyStatus.CONSISTENT]

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

### 10.1 `evaluated_dispatch_semantics_version`

This field means only:

> the Phase 7D local-dispatch rule version against which Phase 7E evaluated consistency.

It must not mean:

> the dispatcher version that produced the supplied outcome.

The implementation must document and test this distinction.

### 10.2 `evaluated_registry_version`

This field means only:

> the version string of the supplied valid registry against which the evidence builder evaluated the outcome.

It must not mean:

> the registry version historically used by the function that produced the supplied outcome.

### 10.3 Registry-declared field namespace

Every registry-derived field uses a `registry_declared_` prefix.

These fields are metadata declarations, not evaluated policy or approval decisions.

## 11. Proposed Builder Interface

```python
def build_deterministic_tool_outcome_evidence(
    request: ToolRequest,
    outcome: ToolDispatchOutcome,
    *,
    registry: ToolRegistry = DEFAULT_TOOL_REGISTRY,
) -> ToolOutcomeEvidence:
    ...
```

The builder is a pure in-process consistency evaluator.

The builder may:

- Read validated fields from `request`.
- Read validated fields from `outcome`.
- Resolve `request.tool_name` in the supplied valid `registry`.
- Read registry declarations for the resolved tool.
- Compare request/outcome identity and version lineage.
- Compare timestamps.
- Compare result/error shape against bounded Phase 7D consistency rules.
- Produce content-minimized field-name metadata.
- Raise a controlled Phase 7E evidence error.

The builder must not:

- Call `dispatch_deterministic_local_tool_request`.
- Invoke a tool.
- Retry a tool.
- Make a policy decision.
- Satisfy an approval requirement.
- Generate an approval record.
- Generate credentials.
- Read credentials.
- Persist evidence.
- Read the current clock.
- Generate a UUID.
- Use randomness.
- Read environment state.
- Read or write runtime files.
- Open sockets.
- Spawn subprocesses.
- Import provider SDKs.
- Contact Jira, ServiceNow, Kubernetes, cloud providers, or databases.
- Perform external mutation.

## 12. A1 Resolution — Remove the Unreachable Normal Registry-Miss Evidence State

R1 proposed:

```text
registry_resolution=registered|not_registered
```

R2 removes that normal evidence-state dimension.

Repository facts:

- `ToolRequest.tool_name` is a closed `ToolName`.
- A valid `ToolRegistry` must contain exactly the complete `ToolName` set.

Therefore a valid `ToolRequest` plus valid `ToolRegistry` has a definition for the request tool name.

R2 rule:

```text
NORMAL_NOT_REGISTERED_EVIDENCE_STATE=REMOVED
TOOL_NOT_REGISTERED_EVIDENCE_REQUIREMENT=REMOVED
PHASE_7D_REOPEN_TO_MAKE_REGISTRY_MISS_REACHABLE=NO
```

If `registry.get(request.tool_name)` nevertheless raises `KeyError` because an invalid or corrupted object bypassed normal construction, the evidence builder must return no evidence and raise a controlled `REGISTRY_OUTCOME_CONTRADICTION` error.

It must not manufacture a `not_registered` evidence record.

A later registry-contract version may reconsider this if legitimate partial/dynamic registries are introduced.

```text
A1_UNREACHABLE_REGISTRY_MISS=RESOLVED
```

## 13. A2 Resolution — Remove Unsupported Dispatcher Producer Provenance

R2 does not contain:

```text
tool_dispatcher_version_as_actual_producer
producer_dispatcher_id
producer_dispatch_receipt
```

R2 may contain:

```text
evaluated_dispatch_semantics_version
```

That field is explicitly evaluation context only.

It says which closed Phase 7D rule set the evidence builder used to determine consistency.

It does not say which function produced the outcome.

```text
A2_DISPATCHER_PROVENANCE_OVERCLAIM=RESOLVED
```

## 14. A3 Resolution — Distinguish Evaluated Registry Context From Registry Producer Provenance

R2 does not assert that the supplied registry produced or governed the original outcome.

The evidence record uses:

```text
evaluated_registry_version
registry_declared_*
```

The word `evaluated` identifies consistency-evaluation context.

The word `declared` identifies registry metadata.

Neither word establishes historical provenance.

```text
A3_REGISTRY_BINDING_OVERCLAIM=RESOLVED
```

## 15. A4 Resolution — Closed Controlled Evidence-Construction Error Model

R2 defines a dedicated bounded failure namespace.

Architecture-level model:

```python
class ToolOutcomeEvidenceErrorCode(StrEnum):
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    VERSION_MISMATCH = "VERSION_MISMATCH"
    TEMPORAL_INVERSION = "TEMPORAL_INVERSION"
    REGISTRY_OUTCOME_CONTRADICTION = "REGISTRY_OUTCOME_CONTRADICTION"
    OUTCOME_SHAPE_CONTRADICTION = "OUTCOME_SHAPE_CONTRADICTION"

@dataclass(frozen=True, slots=True)
class ToolOutcomeEvidenceError(Exception):
    code: ToolOutcomeEvidenceErrorCode
    message: str
```

The error message must be controlled, deterministic, and non-sensitive.

The public semantic error categories are closed.

The builder must not expose:

- Raw argument values.
- Raw output values.
- Raw idempotency-key values.
- Arbitrary caught exception strings.
- Credentials or tokens.
- Environment values.
- Hidden reasoning.

### 15.1 Error-code meaning

`IDENTITY_MISMATCH`

- `request_id` mismatch.
- `trace_id` mismatch.
- `tool_name` mismatch.

`VERSION_MISMATCH`

- Request and outcome `tool_contract_version` differ.
- Request and outcome `tool_envelope_version` differ.

`TEMPORAL_INVERSION`

- Outcome timestamp precedes request timestamp.

`REGISTRY_OUTCOME_CONTRADICTION`

- Registry resolution unexpectedly fails despite valid-contract assumptions.
- Registry declarations imply a Phase 7D fail-closed disposition while a supplied result claims completion.
- Registry declarations imply a read-only local-result path while a supplied error claims a Phase 7D approval disposition.

`OUTCOME_SHAPE_CONTRADICTION`

- Result/error fields contradict their outcome kind.
- A supplied result does not satisfy the selected deterministic local result consistency rules.
- A supplied error does not satisfy the selected normalized error consistency rules.

Pydantic construction errors for malformed input objects occur before Phase 7E because the builder accepts already-validated typed objects. Phase 7E does not wrap arbitrary unvalidated payload parsing.

```text
A4_CONTROLLED_ERROR_CONTRACT=RESOLVED
```

## 16. A5 Resolution — Scope Immutability Precisely

`ToolOutcomeEvidence` is intended to inherit the repository's frozen `VersionedContract` behavior.

That supports only an in-process frozen value after successful validation.

R2 explicitly does not claim durable immutability.

```text
FROZEN_IN_PROCESS_CONTRACT_VALUE=YES
DURABLE_IMMUTABILITY=NO
APPEND_ONLY_STORAGE=NO
TAMPER_EVIDENCE=NO
CRYPTOGRAPHIC_INTEGRITY=NO
DIGITAL_SIGNATURE=NO
PERSISTENCE=NO
```

A caller may serialize or copy the value under later authority, but Phase 7E itself does not provide durable storage or integrity guarantees.

```text
A5_IMMUTABILITY_SCOPE=RESOLVED
```

## 17. A6 Resolution — Registry Declarations Are Not Policy or Approval Decisions

R2 removes ambiguous unqualified registry fields.

Required semantic names include:

```text
registry_declared_risk_tier
registry_declared_approval_requirement
registry_declared_authorization_required
registry_declared_execution_enabled
registry_declared_general_shell_access
```

Phase 7E must not emit:

```text
ALLOW
DENY
POLICY_ALLOW
POLICY_DENY
policy_decision_id
policy_version_used
policy_expiry
approval_id
approver_identity
approval_valid
approval_expiry
execution_authorized
```

`registry_declared_approval_requirement=POLICY_DECISION` means only that the Phase 7A registry declaration says a policy decision is required before a future authorized invocation.

It does not mean a policy engine evaluated the request.

`registry_declared_approval_requirement=HUMAN_APPROVAL` means only that the registry declaration requires a future trusted approval workflow.

It does not mean an approval request or approval exists.

```text
A6_POLICY_APPROVAL_FIELD_SEMANTICS=RESOLVED
```

## 18. A7 Resolution — Preserve CT-07 as Lifecycle-Trace Authority

CT-07 `TraceEvent` remains the repository-wide lifecycle trace contract.

Phase 7E does not:

```text
add CT-07 event names
modify CT-07 stage mappings
modify runtime trace generation
modify CT-07 policy-decision lineage
persist CT-07 events
create a second global trace chain
claim lifecycle-trace authority
```

Phase 7E evidence is tool-domain evidence only.

A later separately governed integration may reference Phase 7E evidence from a CT-07 event or evidence-service record.

That integration does not exist in Phase 7E.

```text
A7_CT07_NON_DRIFT=PRESERVED
```

## 19. A8 Resolution — Preserve Phase 8 Policy Authority

Phase 8 remains the owner of authoritative deterministic policy routing.

Phase 8 owns concepts such as:

```text
PDP
PEP
subject identity
trusted policy attributes
tenant/resource/action policy
ALLOW
DENY
REQUIRE_APPROVAL
restricted route
policy decision identifier
policy version
reason codes
expiry
enforcement
policy lineage
```

Phase 7E may inspect registry declarations that mention authorization or approval requirements.

Phase 7E may not determine whether a user, service, tenant, or workload is actually authorized.

A successful Phase 7E consistency record is not policy authorization.

A successful Phase 7D local mock result plus a successful Phase 7E evidence record is not policy authorization.

```text
A8_PHASE8_NON_DRIFT=PRESERVED
```

## 20. A9 Resolution — Preserve Phase 9 Trusted Approval and Execution Authority

Phase 9 remains the owner of trusted human approval and later trusted execution controls.

Phase 9 owns concepts such as:

```text
approver identity
approver role
approval scope
approval expiry
revocation
separation of duties
revalidation
approval evidence snapshot
one-time execution identity
approval-to-execution lineage
```

`ToolErrorCode.APPROVAL_REQUIRED` remains a normalized fail-closed Phase 7 tool error.

It is not evidence that:

- Phase 8 returned `REQUIRE_APPROVAL`.
- A Phase 9 approval request exists.
- A human reviewed evidence.
- A human approved the action.
- Execution may proceed.

```text
A9_PHASE9_NON_DRIFT=PRESERVED
```

## 21. A10 Resolution — Preserve Content Minimization and Clarify Field-Name Metadata

Phase 7E may record bounded metadata only.

Allowed content:

- Request ID.
- Trace ID.
- Tool name.
- Tool contract/envelope versions after equality validation.
- Evaluated registry version.
- Evaluated dispatch-semantics version.
- Registry-declared metadata.
- Outcome kind.
- Consistency status.
- Result status or normalized error code/category/retryability.
- Whether an idempotency key was present.
- Sorted argument field names.
- Sorted output field names for successful results.
- Request timestamp.
- Outcome timestamp.

Disallowed content:

```text
raw argument values
raw output values
raw idempotency-key value
ToolError.safe_message
arbitrary exception text
credentials
access tokens
refresh tokens
client secrets
provider keys
environment variables
filesystem content
complete prompts
complete model responses
hidden reasoning
```

### 21.1 Field-name metadata clarification

`argument_names` and `output_names` are metadata describing the names of bounded typed fields.

They are not payload evidence.

They remain bounded by the existing `ToolArgumentName` contract.

Their inclusion does not authorize future logging of arbitrary argument values, output values, nested payload content, or secrets.

### 21.2 Deterministic ordering

Argument/output field names must be emitted in stable sorted order.

Identical validated inputs and evaluation context must produce equal evidence values.

```text
A10_CONTENT_MINIMIZATION=PRESERVED
```

## 22. A11 Resolution — Reconfirm the Exact Four-File Future Implementation Boundary

Because R2 adopts the narrower outcome-consistency semantics, the original bounded four-file implementation surface remains sufficient.

If a later gate grants implementation authority, the exact candidate boundary is:

```text
src/incident_diagnostic_api/tools/evidence.py
src/incident_diagnostic_api/tools/__init__.py
tests/tools/test_evidence.py
docs/tools/PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_EVIDENCE_IMPLEMENTATION_AND_EVIDENCE.md
```

The existing implementation-evidence documentation path is retained for stable Phase 7E repository continuity even though R2 narrows the runtime semantics to outcome-consistency evidence.

No additional file is implicitly authorized.

Explicitly outside the future bounded implementation candidate:

```text
src/incident_diagnostic_api/tools/dispatcher.py
src/incident_diagnostic_api/tools/mock.py
src/incident_diagnostic_api/tools/registry.py
src/incident_diagnostic_api/tools/contracts.py
src/incident_diagnostic_api/contracts/trace.py
src/incident_diagnostic_api/runtime/traces.py
API routes
database schemas
migrations
persistence adapters
provider adapters
network clients
policy engine
approval service
MCP server
cloud infrastructure
production deployment
```

If implementation preparation discovers that one of these closed surfaces must change, implementation must stop and return to boundary review.

```text
A11_IMPLEMENTATION_BOUNDARY=RECONFIRMED
```

## 23. Resolution Matrix

```text
A1_UNREACHABLE_REGISTRY_MISS=RESOLVED
A2_DISPATCHER_PROVENANCE_OVERCLAIM=RESOLVED
A3_REGISTRY_BINDING_OVERCLAIM=RESOLVED
A4_CONTROLLED_ERROR_CONTRACT=RESOLVED
A5_IMMUTABILITY_SCOPE=RESOLVED
A6_POLICY_APPROVAL_FIELD_SEMANTICS=RESOLVED
A7_CT07_NON_DRIFT=PRESERVED
A8_PHASE8_NON_DRIFT=PRESERVED
A9_PHASE9_NON_DRIFT=PRESERVED
A10_CONTENT_MINIMIZATION=PRESERVED
A11_IMPLEMENTATION_BOUNDARY=RECONFIRMED
```

This resolution matrix is an R2 architecture claim only until this exact documentation commit passes CI and a later independent R2 acceptance review confirms the resolutions.

## 24. Detailed Consistency Invariants

### 24.1 Request/outcome identity

The request and outcome must have identical:

```text
request_id
trace_id
tool_name
```

Any mismatch raises:

```text
IDENTITY_MISMATCH
```

The builder must not rewrite or choose an identifier from one object as authoritative.

### 24.2 Tool contract and envelope version equality

The request and outcome must have identical:

```text
tool_contract_version
tool_envelope_version
```

Any mismatch raises:

```text
VERSION_MISMATCH
```

The evidence object records a single contract/envelope version only after equality succeeds.

### 24.3 Temporal monotonicity

For `ToolResult`:

```text
outcome_at=completed_at
```

For `ToolError`:

```text
outcome_at=occurred_at
```

Required:

```text
outcome_at >= requested_at
```

Violation raises:

```text
TEMPORAL_INVERSION
```

The builder must not read the current clock or repair timestamps.

### 24.4 Registry resolution

For valid current contracts, `registry.get(request.tool_name)` must resolve.

An unexpected failure returns no evidence and raises:

```text
REGISTRY_OUTCOME_CONTRADICTION
```

R2 does not create a `NOT_REGISTERED` evidence object.

### 24.5 Registry safety declarations

The builder records the supplied registry definition exactly under `registry_declared_*` names.

It must not mutate or normalize those declarations into policy decisions.

### 24.6 Result consistency

A supplied `ToolResult` is eligible for a Phase 7E consistency record only if all of the following hold:

```text
registry_declared_side_effect == NONE
registry_declared_execution_enabled == False
registry_declared_general_shell_access == False
registry_declared_approval_requirement != HUMAN_APPROVAL
```

Because current valid `ToolDefinition` construction already prohibits `execution_enabled=True` and `general_shell_access=True`, those fields should normally remain false. Phase 7E records them as declarations but does not treat defensive unreachable states as normal result states.

The result must also retain `status=COMPLETED` as required by the existing typed contract.

R2 implementation should verify that the successful result is structurally consistent with the deterministic Phase 7C local mock result semantics for the same request and outcome timestamp without copying raw result values into the evidence object.

A result that contradicts the expected bounded local-result shape raises:

```text
OUTCOME_SHAPE_CONTRADICTION
```

A result that contradicts registry safety declarations raises:

```text
REGISTRY_OUTCOME_CONTRADICTION
```

This consistency check does not prove the Phase 7C mock builder or Phase 7D dispatcher actually produced the supplied result.

### 24.7 Error consistency

For `ToolError`:

- Existing typed `ToolError` construction already enforces deterministic code/category/retryability mapping.
- Phase 7E must preserve the supplied normalized `error_code`, `error_category`, and `retryable` values.
- Phase 7E must not copy `safe_message`.
- `result_status` and `output_names` must be absent/empty in the evidence object.

For current valid registry declarations:

- Side-effecting definitions are consistent with Phase 7D `APPROVAL_REQUIRED` fail-closed outcomes.
- Read-only definitions that are eligible for deterministic local mock completion are not consistent with a fabricated Phase 7D `APPROVAL_REQUIRED` outcome merely because the registry declares `POLICY_DECISION`.

That distinction preserves the existing Phase 7D behavior without claiming Phase 8 authorization.

A registry/error disposition contradiction raises:

```text
REGISTRY_OUTCOME_CONTRADICTION
```

### 24.8 Result/error exclusivity

A successful evidence value must represent exactly one supplied outcome type.

For result evidence:

```text
outcome_kind=RESULT
result_status=COMPLETED
error_code=None
error_category=None
retryable=None
```

For error evidence:

```text
outcome_kind=ERROR
result_status=None
error_code=<supplied normalized code>
error_category=<supplied normalized category>
retryable=<supplied normalized value>
output_names=()
```

Any shape contradiction returns no evidence.

## 25. Determinism Requirements

Identical validated:

```text
request
outcome
registry
```

must produce equal `ToolOutcomeEvidence` values.

Phase 7E must not depend on:

```text
current time
randomness
UUID generation
process identity
host identity
environment variables
filesystem state
network state
external service state
mutable invocation history
```

No synthetic evidence ID is required in Phase 7E R2 because generating a new identity would introduce either caller-supplied provenance ambiguity or nondeterministic ID generation that is not necessary for the bounded goal.

A later persistence phase may assign durable record identity under separate authority.

## 26. Security Boundary

Phase 7E implementation, if later authorized, must not introduce runtime use of:

```text
requests
httpx
boto3
kubernetes client SDKs
jira client SDKs
servicenow client SDKs
database client execution
socket
subprocess
paramiko
open(...)
exec(...)
eval(...)
credential reads
secret reads
provider calls
network calls
external mutations
```

Static tests must continue to enforce prohibited runtime surfaces for the Phase 7 tool package.

## 27. Policy and Approval Non-Authority Examples

### 27.1 Read-only tool with registry-declared policy requirement

Example declaration:

```text
tool_name=jira.issue.read
registry_declared_side_effect=NONE
registry_declared_approval_requirement=POLICY_DECISION
registry_declared_authorization_required=true
```

If a supplied result is otherwise consistent with the Phase 7D deterministic local mock semantics, Phase 7E may produce a consistency record.

That record means:

> the supplied outcome is consistent with the current bounded Phase 7 tool semantics.

It does not mean:

> an enterprise authorization decision allowed Jira access.

No real Jira access occurs.

### 27.2 Side-effecting tool

Example declaration:

```text
tool_name=jira.issue.comment
registry_declared_side_effect=APPEND_ONLY
registry_declared_approval_requirement=HUMAN_APPROVAL
```

A supplied Phase 7D-style `APPROVAL_REQUIRED` error may be consistent.

That consistency record does not mean:

> a Phase 9 approval request exists.

It means only:

> the current Phase 7 tool boundary failed closed rather than producing a successful side effect.

## 28. CT-07 Non-Duplication Rule

Phase 7E must not add fields solely to mirror CT-07 lifecycle-trace semantics.

Phase 7E does not need:

```text
lifecycle_stage
trace_event_name
trace_event_id
policy_decision_id
input_reference
output_reference
runtime_state
runtime_transition
```

Request/trace IDs are retained only as identity correlation inherited from the existing tool envelopes.

They do not make `ToolOutcomeEvidence` a CT-07 event.

## 29. Future Implementation Test Requirements

If a later gate grants implementation authority, tests must include at least the following.

### 29.1 Version and contract tests

- Evidence version is explicit.
- Evidence object is frozen after construction.
- Unknown evidence fields fail validation.
- Request/outcome tool-contract versions must match.
- Request/outcome envelope versions must match.

### 29.2 Identity tests

- Request ID mismatch -> `IDENTITY_MISMATCH`.
- Trace ID mismatch -> `IDENTITY_MISMATCH`.
- Tool-name mismatch -> `IDENTITY_MISMATCH`.
- Builder does not repair identities.

### 29.3 Temporal tests

- Equal request/outcome timestamps are accepted if existing contracts permit them.
- Later outcome timestamp is accepted.
- Earlier outcome timestamp -> `TEMPORAL_INVERSION`.
- No current-clock read is required.

### 29.4 Registry tests

- Every current allowlisted tool resolves in a valid default registry.
- There is no normal `NOT_REGISTERED` evidence state.
- Registry declarations are copied only under `registry_declared_*` semantics.
- Evaluated registry version is clearly evaluation context.
- Evidence does not emit policy or approval decision IDs.

### 29.5 Read-only result tests

For every current read-only tool:

- A deterministic Phase 7C-style local result is consistent.
- The evidence records result metadata, not raw output values.
- Sorted output field names are deterministic.
- Registry-declared policy requirement is preserved as declaration only.
- No `ALLOW` or execution authorization is emitted.

### 29.6 Side-effecting error tests

For current Jira comment and ServiceNow update tools:

- Phase 7D-style `APPROVAL_REQUIRED` error is consistent.
- Evidence records normalized code/category/retryability.
- `safe_message` is absent.
- `output_names=()`.
- No approval ID or approver identity exists.

### 29.7 Contradiction tests

- Side-effecting registry definition + successful result -> `REGISTRY_OUTCOME_CONTRADICTION`.
- Read-only local-result path + fabricated `APPROVAL_REQUIRED` outcome -> `REGISTRY_OUTCOME_CONTRADICTION`.
- Result with invalid deterministic-local shape -> `OUTCOME_SHAPE_CONTRADICTION`.
- Version mismatch -> `VERSION_MISMATCH`.

### 29.8 Content-minimization tests

Evidence must not contain:

- Argument values.
- Output values.
- Idempotency-key value.
- Error safe message.
- Credentials.
- Secrets.
- Tokens.
- Environment content.
- Hidden reasoning.

Field-name metadata may be present only in bounded sorted form.

### 29.9 Determinism tests

Repeated construction from identical validated inputs must produce equal evidence values.

Tests must show no dependency on:

- clock
- UUID
- randomness
- environment
- filesystem runtime state
- network
- subprocess
- provider SDK

### 29.10 Regression tests

- All Phase 7A–7D tests remain green.
- Complete tools test suite remains green.
- Complete repository suite remains green.
- Ruff lint passes.
- Ruff format passes.
- Strict MyPy passes.
- Dependency integrity passes.
- Required container verification remains green.

## 30. Evidence Required From a Future Implementation Gate

A future authorized implementation gate must record:

```text
exact implementation commit SHA
exact implementation tree SHA
exact implementation file boundary
focused Phase 7E test count
complete Phase 7 tool test count
complete repository test count
Ruff lint result
Ruff format result
strict MyPy result
dependency integrity result
Python quality and contract-tests job result
local container build/health-verification job result
exact GitHub Actions run ID
exact CI head SHA
prohibited runtime-surface verification
known limitations
```

An implementation commit passing CI would not itself close Phase 7E.

A later documentation-only closure package would need to record the exact implementation evidence and itself pass exact-commit CI before Phase 7E could be declared closed.

## 31. Explicit Non-Goals

Phase 7E R2 is not:

- A dispatcher receipt protocol.
- A cryptographic provenance protocol.
- A policy engine.
- A policy enforcement point.
- A human approval system.
- A tool executor.
- A retry engine.
- A live Jira integration.
- A live ServiceNow integration.
- A Kubernetes integration.
- A cloud-provider integration.
- A database execution layer.
- An MCP server.
- A credential broker.
- A network gateway.
- An evidence database.
- An append-only audit store.
- A tamper-evident ledger.
- A global observability system.
- A production deployment capability.

## 32. Honest Claim Boundary After Future Implementation

If a future implementation passes its exact-commit tests and CI, but before Phase 7E closure, the strongest valid claim would be:

> Phase 7E implements a deterministic local consistency evaluator that produces a frozen, content-minimized evidence value when supplied typed tool request/outcome values are consistent with the evaluated registry declarations and bounded Phase 7D semantics. It does not establish dispatcher or registry producer provenance, real enterprise execution, policy authorization, human approval, durable persistence, or tamper evidence.

No stronger claim is authorized by this architecture.

## 33. R2 Implementation Boundary Candidate

The future implementation boundary is now architecturally reconfirmed but not authorized:

```text
CANDIDATE_IMPLEMENTATION_FILE_1=src/incident_diagnostic_api/tools/evidence.py
CANDIDATE_IMPLEMENTATION_FILE_2=src/incident_diagnostic_api/tools/__init__.py
CANDIDATE_IMPLEMENTATION_FILE_3=tests/tools/test_evidence.py
CANDIDATE_IMPLEMENTATION_FILE_4=docs/tools/PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_EVIDENCE_IMPLEMENTATION_AND_EVIDENCE.md

CANDIDATE_IMPLEMENTATION_FILE_COUNT=4
IMPLEMENTATION_BOUNDARY_STATUS=ARCHITECTURALLY_RECONFIRMED_PENDING_INDEPENDENT_R2_ACCEPTANCE
```

This R2 gate itself does not grant mutation authority for those files.

## 34. R2 Authority Decision

```text
PHASE_7E_R2_ARCHITECTURE=PREPARED
PHASE_7E_R2_ARCHITECTURE_ACCEPTANCE=PENDING_INDEPENDENT_REVIEW
PHASE_7E_R2_IMPLEMENTATION=NOT_STARTED
PHASE_7E_R2_IMPLEMENTATION_AUTHORITY=NONE

PHASE_7E_SOURCE_CODE_MUTATION_AUTHORITY=NONE
PHASE_7E_TEST_MUTATION_AUTHORITY=NONE
PHASE_7E_EXPORT_MUTATION_AUTHORITY=NONE
PHASE_7E_DISPATCHER_MUTATION_AUTHORITY=NONE
PHASE_7E_MOCK_MUTATION_AUTHORITY=NONE
PHASE_7E_REGISTRY_MUTATION_AUTHORITY=NONE
PHASE_7E_TOOL_CONTRACT_MUTATION_AUTHORITY=NONE
PHASE_7E_TRACE_MUTATION_AUTHORITY=NONE
PHASE_7E_POLICY_AUTHORITY=NONE
PHASE_7E_APPROVAL_AUTHORITY=NONE
PHASE_7E_EVIDENCE_PERSISTENCE_AUTHORITY=NONE
PHASE_7E_NETWORK_AUTHORITY=NONE
PHASE_7E_CREDENTIAL_AUTHORITY=NONE
PHASE_7E_EXTERNAL_MUTATION_AUTHORITY=NONE
PHASE_7E_REAL_TOOL_EXECUTION_AUTHORITY=NONE
```

## 35. R2 Acceptance Conditions

Before implementation authority may even be considered, an independent R2 review must verify:

```text
R2_A1_RESOLUTION_VALID=PASS
R2_A2_RESOLUTION_VALID=PASS
R2_A3_RESOLUTION_VALID=PASS
R2_A4_ERROR_MODEL_SUFFICIENT=PASS
R2_A5_IMMUTABILITY_SCOPE_TRUTHFUL=PASS
R2_A6_REGISTRY_DECLARATION_NAMES_NONAUTHORITATIVE=PASS
R2_A7_CT07_NON_DRIFT=PASS
R2_A8_PHASE8_NON_DRIFT=PASS
R2_A9_PHASE9_NON_DRIFT=PASS
R2_A10_CONTENT_MINIMIZATION=PASS
R2_A11_FOUR_FILE_BOUNDARY_SUFFICIENT=PASS
R2_PROVENANCE_CLAIMS_DO_NOT_EXCEED_INPUT_EVIDENCE=PASS
R2_NO_UNREACHABLE_NORMAL_STATE=PASS
R2_NO_REAL_EXECUTION_AUTHORITY=PASS
```

The independent review must attack the R2 semantics rather than merely confirming that A1–A11 labels exist.

## 36. R2 Documentation CI Requirement

This R2 architecture has no accepted canonical effect for future implementation consideration until its exact documentation commit passes the repository CI workflow.

Required evidence:

```text
R2_ARCHITECTURE_COMMIT=<exact sha>
R2_ARCHITECTURE_CI_RUN=<exact run id>
R2_ARCHITECTURE_CI_HEAD_SHA=<same exact sha>
R2_ARCHITECTURE_CI_STATUS=COMPLETED
R2_ARCHITECTURE_CI_CONCLUSION=SUCCESS
```

If exact-commit CI fails, no implementation-authority review may proceed from this R2 artifact until the documentation failure is corrected under a separately visible commit.

## 37. Current Posture Before R2 Independent Acceptance

```text
PHASE_7D=CLOSED

PHASE_7E_R1_ARCHITECTURE=REJECTED_FOR_IMPLEMENTATION
PHASE_7E_R1_HISTORY=PRESERVED
PHASE_7E_R1_REVIEW=CANONICALLY_VERIFIED

PHASE_7E_R2_CAPABILITY=
DETERMINISTIC_TOOL_DISPATCH_OUTCOME_CONSISTENCY_EVIDENCE

PHASE_7E_R2_ARCHITECTURE=PREPARED
PHASE_7E_R2_ACCEPTANCE=PENDING
PHASE_7E_IMPLEMENTATION=NOT_STARTED
PHASE_7E_IMPLEMENTATION_AUTHORITY=NONE
REAL_TOOL_EXECUTION_AUTHORITY=NONE
```

## 38. Next Disciplined Gate

Only after the exact R2 architecture documentation commit succeeds in CI should the chain advance to:

```text
NEXT_GATE=
PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_OUTCOME_CONSISTENCY_EVIDENCE_
R2_INDEPENDENT_ARCHITECTURE_ACCEPTANCE_AND_
BOUNDED_IMPLEMENTATION_AUTHORITY_REVIEW
```

That next gate must independently verify all R2 corrections, provenance limitations, consistency invariants, controlled failure semantics, content minimization, CT-07 separation, Phase 8/9 non-drift, and the exact four-file candidate implementation boundary.

Until such a review explicitly passes and grants bounded authority:

```text
PHASE_7E_IMPLEMENTATION_AUTHORITY=NONE
```
