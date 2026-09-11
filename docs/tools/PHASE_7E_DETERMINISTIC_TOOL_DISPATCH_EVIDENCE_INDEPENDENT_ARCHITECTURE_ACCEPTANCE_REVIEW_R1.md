# Phase 7E — Deterministic Tool Dispatch Evidence Independent Architecture Acceptance and Bounded Implementation Authority Review R1

## 1. Review Purpose

This is an independent adversarial review of the Phase 7E architecture candidate preserved by commit `3124d373e1cf8445a0cb00c78a1edff1303ba445`.

The review determines whether the candidate is sufficiently precise and truthful to grant bounded Phase 7E source-code implementation authority.

The review does not implement Phase 7E, does not amend the candidate in place, and does not authorize any real tool execution or enterprise integration.

## 2. Review Authority

```text
REVIEW_REVISION=R1
REVIEW_AUTHORITY=READ_ONLY_ARCHITECTURE_AND_AUTHORITY_EVALUATION
REVIEW_RECORD_MATERIALIZATION_AUTHORITY=DOCUMENTATION_ONLY_SINGLE_FILE
SOURCE_CODE_MUTATION_AUTHORITY=NONE
TEST_MUTATION_AUTHORITY=NONE
API_ROUTE_MUTATION_AUTHORITY=NONE
POLICY_MUTATION_AUTHORITY=NONE
APPROVAL_MUTATION_AUTHORITY=NONE
REAL_TOOL_EXECUTION_AUTHORITY=NONE
NETWORK_AUTHORITY=NONE
CREDENTIAL_AUTHORITY=NONE
EXTERNAL_MUTATION_AUTHORITY=NONE
```

The only repository mutation permitted by this gate is this review record.

## 3. Review Object

Architecture candidate:

```text
CANDIDATE_COMMIT=3124d373e1cf8445a0cb00c78a1edff1303ba445
CANDIDATE_TREE=1c1e9147eed6bdf44f457f81ebf8d13ee1357333
CANDIDATE_PARENT=3fe514b6f719e988ada3bef86af31f003fef7f39
CANDIDATE_FILE=docs/tools/PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_EVIDENCE_ARCHITECTURE_AND_AUTHORITY_GATE.md
CANDIDATE_FILES_CHANGED=1
CANDIDATE_ADDITIONS=658
CANDIDATE_DELETIONS=0
```

Prerequisite exact-commit CI:

```text
CANDIDATE_CI_RUN=34633962087
CANDIDATE_CI_WORKFLOW=Phase_4_CI
CANDIDATE_CI_HEAD_SHA=3124d373e1cf8445a0cb00c78a1edff1303ba445
CANDIDATE_CI_STATUS=COMPLETED
CANDIDATE_CI_CONCLUSION=SUCCESS
```

The CI success establishes that the documentation candidate did not break the repository validation pipeline. It does not independently establish that the architecture semantics are correct.

## 4. Repository Surfaces Independently Reviewed

The review considered the live candidate together with the current Phase 7 and downstream authority surfaces:

```text
src/incident_diagnostic_api/tools/contracts.py
src/incident_diagnostic_api/tools/registry.py
src/incident_diagnostic_api/tools/mock.py
src/incident_diagnostic_api/tools/dispatcher.py
src/incident_diagnostic_api/tools/__init__.py
tests/tools/test_dispatcher.py
src/incident_diagnostic_api/contracts/common.py
src/incident_diagnostic_api/contracts/trace.py
src/incident_diagnostic_api/runtime/traces.py
docs/interview-accelerator/phases/PHASE_08_POLICY_BASED_ROUTING.md
docs/interview-accelerator/phases/PHASE_09_HUMAN_APPROVAL.md
docs/governance/CLAIM_EVIDENCE_AND_AUTHORITY_RULES.md
docs/scenario/CLIENT_SCENARIO_AND_SYSTEM_BOUNDARY.md
```

## 5. Independent Review Decision

```text
PHASE_7E_ARCHITECTURE_ACCEPTANCE_R1=FAIL
PHASE_7E_IMPLEMENTATION_AUTHORITY_R1=WITHHELD
PHASE_7E_SOURCE_CODE_AUTHORITY=NONE
PHASE_7E_TEST_MUTATION_AUTHORITY=NONE
PHASE_7E_FOUR_FILE_IMPLEMENTATION_BOUNDARY=NOT_YET_ACCEPTED
PHASE_7E_REAL_EXECUTION_AUTHORITY=NONE
```

The selected high-level direction remains sound: Phase 7E should add a deterministic, content-minimized tool-domain evidence primitive rather than policy, approval, or real execution.

The R1 architecture is nevertheless not safe to implement as written because it overstates provenance that its proposed inputs cannot establish and includes one registry-resolution branch that cannot occur through the current valid typed interfaces.

This is an architecture rejection for correction, not a rejection of the Phase 7E evidence direction.

## 6. Finding A1 — `NOT_REGISTERED` Evidence Branch Is Unreachable Through Valid Current Contracts

Severity: `BLOCKING`

### Candidate claim

The R1 architecture proposes:

```text
registry_resolution = registered | not_registered
```

and requires a registry-miss evidence path paired with `TOOL_NOT_REGISTERED`.

### Repository fact

`ToolRequest.tool_name` is typed as the closed `ToolName` enumeration.

`ToolRegistry.__post_init__` requires the registry tool-name set to exactly equal the complete `ToolName` allowlist. A valid `ToolRegistry` therefore cannot omit one allowed `ToolName` and cannot contain an unknown name.

The Phase 7D dispatcher retains a defensive `KeyError -> TOOL_NOT_REGISTERED` branch, but the current Phase 7D tests do not establish a valid typed path that reaches it.

### Consequence

A Phase 7E contract must not elevate a defensive but unreachable branch into a required evidence state.

Doing so would create tests that either cannot be expressed through valid public contracts or would require invalid-object construction/test doubles that do not represent normal repository behavior.

### Required correction

For the current bounded Phase 7E contract:

```text
REMOVE registry_resolution=NOT_REGISTERED AS A NORMAL EVIDENCE STATE
DO_NOT REQUIRE TOOL_NOT_REGISTERED EVIDENCE CONSTRUCTION
DO_NOT REOPEN PHASE_7D TO MAKE THE BRANCH REACHABLE
```

If the repository later changes the tool-name or registry model so a legitimate runtime registry miss can occur, that capability can be reconsidered under a separate contract/version gate.

## 7. Finding A2 — Dispatcher Producer Provenance Cannot Be Established From the Proposed Builder Inputs

Severity: `BLOCKING`

### Candidate claim

The R1 architecture states that evidence should identify which dispatcher version produced the outcome and proposes:

```text
tool_dispatcher_version
```

The builder inputs are:

```python
request: ToolRequest
outcome: ToolDispatchOutcome
registry: ToolRegistry
```

### Repository fact

`ToolResult` and `ToolError` are public typed contracts.

The package also publicly exports:

```text
build_deterministic_mock_tool_result
build_deterministic_mock_tool_error
```

Those functions construct valid `ToolResult` and `ToolError` values directly without going through `dispatch_deterministic_local_tool_request`.

Therefore a structurally valid outcome is not proof that Phase 7D produced it.

### Consequence

A Phase 7E builder that stamps the current `TOOL_DISPATCHER_VERSION` would transform a code constant into a producer-provenance claim that is not supported by the supplied evidence.

That would violate the repository rule that claims must not exceed the evidence actually available.

### Required correction

The preferred bounded correction is:

```text
REMOVE producer-provenance semantics from the initial Phase 7E contract
REMOVE tool_dispatcher_version AS A CLAIM OF THE ACTUAL OUTCOME PRODUCER
NARROW THE CAPABILITY TO OUTCOME-CONSISTENCY EVIDENCE
```

A later phase may establish actual dispatcher provenance only if it introduces an authoritative receipt/record at the dispatch point under a separately approved boundary.

## 8. Finding A3 — Supplied Registry Is Not Bound to the Registry That Produced the Outcome

Severity: `BLOCKING`

### Candidate claim

R1 says the evidence should identify the relevant tool-registry metadata and registry version.

### Repository fact

Both the Phase 7D dispatcher and the proposed R1 evidence builder can receive a `ToolRegistry` value.

A caller can construct a valid `ToolRegistry` with the required complete tool-name set while varying allowed metadata such as risk tier, side-effect classification, approval requirement, timeout, or version subject to registry invariants.

`ToolResult` and `ToolError` do not carry a registry identity or registry-version receipt binding them to the registry used when the outcome was produced.

### Consequence

Given only `request + outcome + supplied registry`, Phase 7E can evaluate consistency against the supplied registry, but it cannot prove that this was the registry used by the dispatcher that produced the outcome.

### Required correction

R2 must use semantics such as:

```text
evaluated_registry_version
registry_declared_capability
registry_declared_side_effect
registry_declared_risk_tier
registry_declared_approval_requirement
registry_declared_authorization_required
registry_declared_execution_enabled
registry_declared_general_shell_access
```

These fields describe the registry against which the evidence builder evaluated the supplied outcome. They must not be described as historical producer provenance.

## 9. Finding A4 — Controlled Evidence-Construction Failure Contract Is Underspecified

Severity: `HIGH`

### Candidate claim

R1 repeatedly requires a controlled invariant failure for identity mismatch, temporal inversion, registry contradiction, and other invalid combinations.

### Repository precedent

The runtime trace layer uses a dedicated frozen controlled exception type (`TraceGenerationError`) rather than allowing arbitrary exception behavior to become the public evidence-generation contract.

### Consequence

Without a Phase 7E error contract, implementation may drift between raw `ValueError`, Pydantic validation failures, assertion failures, or free-form exceptions.

That weakens deterministic caller behavior and makes the failure model less auditable.

### Required correction

R2 must define the semantic error surface before implementation. A preferred bounded model is:

```text
ToolOutcomeEvidenceError
ToolOutcomeEvidenceErrorCode
```

with a small closed reason-code set covering at minimum:

```text
IDENTITY_MISMATCH
TEMPORAL_INVERSION
REGISTRY_OUTCOME_CONTRADICTION
OUTCOME_SHAPE_CONTRADICTION
```

The exact Python names may be refined, but the error categories must be closed, deterministic, non-sensitive, and testable.

## 10. Finding A5 — “Immutable Evidence” Overstates Current Integrity and Durability

Severity: `HIGH`

### Candidate claim

R1 describes the proposed record as typed and immutable.

### Repository fact

`VersionedContract` inherits the repository's frozen Pydantic `ContractModel`, so an instance can be immutable in-process after construction.

However Phase 7E explicitly does not include evidence persistence, append-only storage, integrity hashing, signature, durable lineage, or tamper-evidence.

The governance doctrine prohibits treating evidence as immutable unless integrity controls prove that property.

### Consequence

The word `immutable` is acceptable only when explicitly scoped to the in-memory contract value. It must not imply immutable evidence history, durable provenance, or tamper-evident storage.

### Required correction

R2 must use language equivalent to:

```text
FROZEN_IN_PROCESS_CONTRACT_VALUE=YES
DURABLE_IMMUTABILITY=NO
TAMPER_EVIDENCE=NO
PERSISTENCE=NO
```

## 11. Finding A6 — Registry Declarations Must Not Be Confused With Policy or Approval Decisions

Severity: `HIGH`

### Candidate risk

R1 proposes unqualified fields such as:

```text
risk_tier
approval_requirement
authorization_required
```

while a valid read-only Phase 7D tool currently has registry metadata that requires authorization / a policy decision even though Phase 7D only performs deterministic local mock dispatch and no Phase 8 policy engine is implemented.

### Downstream authority fact

Phase 8 owns the authoritative deterministic policy decision and its decision lineage.

Phase 9 owns trusted human approval and execution revalidation.

### Consequence

Unqualified Phase 7E field names can be misread by a later consumer as evaluated authorization or approval state rather than registry-declared metadata.

### Required correction

R2 must namespace or otherwise semantically qualify registry-derived fields, for example:

```text
registry_declared_risk_tier
registry_declared_approval_requirement
registry_declared_authorization_required
```

Phase 7E must not emit:

```text
ALLOW
DENY
policy_decision_id
approval_id
approver_identity
approval_valid
execution_authorized
```

## 12. Finding A7 — CT-07 Separation Is Correct and Must Be Preserved

Severity: `PASS / NON-BLOCKING`

R1 correctly states that CT-07 `TraceEvent` remains the repository-wide lifecycle trace contract.

The reviewed CT-07 implementation already owns lifecycle event names, stages, outcomes, policy-decision lineage where applicable, request/trace correlation, and runtime trace generation.

Phase 7E should remain tool-domain evidence and must not:

```text
add CT-07 event names
change CT-07 stage mappings
change runtime trace authority
create a second global trace chain
claim lifecycle persistence
```

Disposition: `ACCEPT_AS_WRITTEN`.

## 13. Finding A8 — Phase 8 Non-Drift Boundary Is Correct in Direction

Severity: `PASS WITH REQUIRED FIELD-NAMING CORRECTION`

Phase 8 explicitly owns deterministic policy-based routing, PDP/PEP semantics, allow/deny/require-approval decisions, decision identifiers, policy version, reasons, expiry, enforcement, and policy lineage.

R1 correctly rejects a Phase 7E policy wrapper.

Phase 7E may evaluate whether supplied tool metadata/outcome values are structurally consistent. It may not decide whether a subject is authorized to use a tool.

Disposition: `ACCEPT_DIRECTION`; A6 naming correction remains mandatory.

## 14. Finding A9 — Phase 9 Non-Drift Boundary Is Correct

Severity: `PASS`

Phase 9 explicitly owns trusted human approval, approver identity, action scope, expiry, revocation, separation of duties, revalidation, and approval-to-execution lineage.

R1 correctly rejects an approval placeholder as the Phase 7E capability.

`ToolErrorCode.APPROVAL_REQUIRED` in Phase 7D/7E remains a fail-closed local dispatcher outcome. It is not evidence of a Phase 8 policy decision and is not evidence that a Phase 9 approval request or approval exists.

Disposition: `ACCEPT_AS_WRITTEN`.

## 15. Finding A10 — Content Minimization Direction Is Accepted With One Clarification

Severity: `PASS WITH CLARIFICATION`

R1 correctly excludes:

```text
raw argument values
raw output values
raw idempotency-key values
credentials
tokens
secrets
environment variables
arbitrary exception text
hidden reasoning
complete prompts/responses
```

It also correctly avoids copying `ToolError.safe_message` into the initial evidence object.

R2 should state that argument/output field names are metadata, not payload evidence, and remain bounded by the existing `ToolArgumentName` contract. Their presence does not authorize later logging of arbitrary payload content.

Disposition: `ACCEPT_DIRECTION`.

## 16. Finding A11 — Proposed Four-File Boundary Is Conditionally Viable Only for the Narrowed Semantics

Severity: `BLOCKING UNTIL R2`

R1 proposes eventual implementation in exactly:

```text
src/incident_diagnostic_api/tools/evidence.py
src/incident_diagnostic_api/tools/__init__.py
tests/tools/test_evidence.py
docs/tools/PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_EVIDENCE_IMPLEMENTATION_AND_EVIDENCE.md
```

### Review result

That four-file boundary is sufficient for a pure, deterministic **outcome-consistency evidence** contract/builder exported from the existing tool package.

It is not sufficient to establish strong historical dispatcher provenance under the R1 semantics without either:

- changing a closed Phase 7D producer surface, or
- adding a new authoritative wrapper/receipt-producing dispatch path whose authority would require separate review.

### Required correction

Preferred R2:

```text
KEEP_FOUR_FILE_BOUNDARY=CANDIDATE
NARROW_PROVENANCE_CLAIM=REQUIRED
DISPATCHER_PY_MUTATION=NONE
MOCK_PY_MUTATION=NONE
REGISTRY_PY_MUTATION=NONE
CONTRACTS_PY_MUTATION=NONE
```

If R2 instead chooses true dispatch-producer provenance, the four-file boundary must be reopened and independently reviewed before implementation.

## 17. Preferred R2 Semantic Correction

The review recommends the minimal non-drift correction rather than reopening Phase 7D.

Preferred capability name:

```text
Phase 7E — Deterministic Tool Dispatch Outcome Consistency Evidence
```

or an equivalent name that does not imply producer provenance beyond what the contract proves.

Preferred evidence scope:

```text
EVIDENCE_SCOPE=OUTCOME_CONSISTENCY_ONLY
DISPATCH_PRODUCER_PROVENANCE=NOT_ESTABLISHED
REGISTRY_PRODUCER_PROVENANCE=NOT_ESTABLISHED
REAL_EXECUTION=NOT_ESTABLISHED_AND_NOT_AUTHORIZED
```

R2 should:

1. Preserve request/outcome identity checks.
2. Preserve temporal monotonicity checks.
3. Preserve deterministic ordering and content minimization.
4. Remove normal `NOT_REGISTERED` evidence state from the current valid contract.
5. Remove or rename dispatcher-version fields so they cannot assert unsupported producer provenance.
6. Namespace all supplied-registry metadata as registry declarations/evaluation context.
7. Define a bounded controlled error type and reason-code set.
8. Explicitly scope immutability to a frozen in-process contract value.
9. Preserve CT-07 as the lifecycle-trace authority.
10. Preserve Phase 8 as policy-decision authority.
11. Preserve Phase 9 as trusted approval/execution authority.
12. Preserve the prohibition on persistence, network, credentials, provider SDKs, shell, filesystem mutation, and external mutation.
13. Retain the exact four-file implementation boundary only if the narrowed semantics are adopted.

## 18. Alternative R2 Path — True Dispatcher Provenance

A more invasive alternative would preserve the stronger `dispatch evidence` meaning by establishing an authoritative receipt at the dispatch point.

That path is not authorized by this review.

It would require a new architecture decision addressing at least:

```text
dispatch producer binding
registry-version binding
receipt identity
receipt construction authority
atomicity between dispatch outcome and receipt
closed Phase 7D surface mutation or authoritative wrapper
new regression boundary
```

This alternative would reopen the implementation boundary and should not be selected merely to preserve the R1 name.

## 19. Implementation Authority Decision

Because A1, A2, A3, A4, A5, A6, and A11 require architecture correction, R1 does not grant source-code authority.

```text
PHASE_7E_ARCHITECTURE_R1=REJECTED_FOR_IMPLEMENTATION
PHASE_7E_HIGH_LEVEL_EVIDENCE_DIRECTION=RETAINED
PHASE_7E_R2_ARCHITECTURE_CORRECTION_REQUIRED=YES
PHASE_7E_IMPLEMENTATION_AUTHORITY=NONE
PHASE_7E_SOURCE_CODE_MUTATION_AUTHORITY=NONE
PHASE_7E_TEST_MUTATION_AUTHORITY=NONE
PHASE_7E_EXPORT_MUTATION_AUTHORITY=NONE
PHASE_7E_DISPATCHER_MUTATION_AUTHORITY=NONE
PHASE_7E_MOCK_MUTATION_AUTHORITY=NONE
PHASE_7E_REGISTRY_MUTATION_AUTHORITY=NONE
PHASE_7E_TOOL_CONTRACT_MUTATION_AUTHORITY=NONE
PHASE_7E_POLICY_AUTHORITY=NONE
PHASE_7E_APPROVAL_AUTHORITY=NONE
PHASE_7E_EVIDENCE_PERSISTENCE_AUTHORITY=NONE
PHASE_7E_NETWORK_AUTHORITY=NONE
PHASE_7E_CREDENTIAL_AUTHORITY=NONE
PHASE_7E_EXTERNAL_MUTATION_AUTHORITY=NONE
```

The R1 architecture candidate remains preserved in repository history as the reviewed candidate. This review does not rewrite or delete it.

## 20. Required Evidence Before Any Phase 7E Implementation Authority May Be Granted

A corrected R2 architecture must be independently reviewable and must explicitly resolve every blocking/high R1 finding.

Minimum acceptance evidence:

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

The corrected architecture documentation commit must itself pass exact-commit CI before a subsequent bounded implementation-authority decision may take effect.

## 21. Honest Current Claim

The strongest valid repository claim after this R1 review is:

> Phase 7E remains an evidence-oriented design direction, but the first deterministic tool-dispatch-evidence architecture candidate did not pass independent acceptance. Implementation authority remains withheld pending an R2 semantic correction that removes unsupported provenance claims and unreachable states while preserving the Phase 8, Phase 9, and CT-07 boundaries.

## 22. Next Disciplined Gate

```text
NEXT_GATE=
PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_EVIDENCE_
R1_REJECTION_
BOUNDED_R2_SEMANTIC_CORRECTION_AND_
COMPLETE_STANDALONE_REPLACEMENT_ARCHITECTURE_PREPARATION
```

That next gate must remain documentation-only.

It should produce a complete standalone R2 architecture candidate that supersedes R1 for future implementation consideration while preserving R1 and this review as historical evidence.

It must not implement source code, tests, exports, routes, persistence, policy, approval, network access, credentials, provider integrations, or real tool execution.
