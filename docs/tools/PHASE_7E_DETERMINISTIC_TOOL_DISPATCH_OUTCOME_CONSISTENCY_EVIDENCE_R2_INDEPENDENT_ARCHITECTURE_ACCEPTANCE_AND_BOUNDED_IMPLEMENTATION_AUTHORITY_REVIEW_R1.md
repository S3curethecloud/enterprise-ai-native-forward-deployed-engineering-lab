# Phase 7E — Deterministic Tool Dispatch Outcome Consistency Evidence R2 Independent Architecture Acceptance and Bounded Implementation Authority Review R1

## 1. Review Purpose

This document records the independent adversarial review of the Phase 7E R2 architecture candidate:

```text
PHASE_7E_R2_ARCHITECTURE_COMMIT=
46021b03f7cd0f58b9ed1dfdec5c47ea1c42c87d

PHASE_7E_R2_ARCHITECTURE_TREE=
4f2e97bc3cc9ba94b6198b7230ad4a0de3206140
```

The review attacks the actual R2 semantics rather than accepting the R2 A1–A11 resolution labels at face value.

Its purpose is to determine whether the corrected architecture is sufficiently precise, truthful, bounded, and implementable to grant source-code mutation authority within the proposed four-file implementation boundary.

This review does not implement Phase 7E.

## 2. Review Authority

```text
CANDIDATE_REVISION=R2
REVIEW_REVISION=R1
REVIEW_AUTHORITY=READ_ONLY_ARCHITECTURE_AND_AUTHORITY_EVALUATION
REVIEW_RECORD_MATERIALIZATION_AUTHORITY=DOCUMENTATION_ONLY_SINGLE_FILE

SOURCE_CODE_MUTATION_AUTHORITY=NONE
TEST_MUTATION_AUTHORITY=NONE
EXPORT_MUTATION_AUTHORITY=NONE
DISPATCHER_MUTATION_AUTHORITY=NONE
MOCK_MUTATION_AUTHORITY=NONE
REGISTRY_MUTATION_AUTHORITY=NONE
TOOL_CONTRACT_MUTATION_AUTHORITY=NONE
TRACE_MUTATION_AUTHORITY=NONE
POLICY_MUTATION_AUTHORITY=NONE
APPROVAL_MUTATION_AUTHORITY=NONE
EVIDENCE_PERSISTENCE_AUTHORITY=NONE
NETWORK_AUTHORITY=NONE
CREDENTIAL_AUTHORITY=NONE
REAL_TOOL_EXECUTION_AUTHORITY=NONE
EXTERNAL_MUTATION_AUTHORITY=NONE
```

The only repository mutation permitted by this review gate is this review record.

## 3. Exact Review Prerequisite

The R2 architecture documentation commit passed exact-commit CI before this review began.

```text
R2_ARCHITECTURE_COMMIT=
46021b03f7cd0f58b9ed1dfdec5c47ea1c42c87d

R2_ARCHITECTURE_TREE=
4f2e97bc3cc9ba94b6198b7230ad4a0de3206140

R2_ARCHITECTURE_PARENT=
046b7eead6238392840e6a49eb5f39157832c426

R2_ARCHITECTURE_CI_RUN=34635977281
R2_ARCHITECTURE_CI_WORKFLOW=Phase_4_CI
R2_ARCHITECTURE_CI_RUN_NUMBER=41
R2_ARCHITECTURE_CI_HEAD_SHA=46021b03f7cd0f58b9ed1dfdec5c47ea1c42c87d
R2_ARCHITECTURE_CI_STATUS=COMPLETED
R2_ARCHITECTURE_CI_CONCLUSION=SUCCESS

PYTHON_QUALITY_AND_CONTRACT_TESTS=SUCCESS
LOCAL_CONTAINER_BUILD_AND_HEALTH_VERIFICATION=SUCCESS
```

`main` was verified at the exact R2 architecture commit before review materialization.

No pre-review repository drift was observed.

## 4. Review Object

R2 candidate file:

```text
docs/tools/PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_OUTCOME_CONSISTENCY_EVIDENCE_ARCHITECTURE_AND_AUTHORITY_GATE_R2.md
```

R2 commit boundary from its parent:

```text
COMMITS=1
FILES_CHANGED=1
ADDITIONS=1365
DELETIONS=0
```

The R2 architecture is therefore a documentation-only candidate, not an implementation artifact.

## 5. Repository Surfaces Independently Reviewed

The independent review cross-checked the R2 semantics against the live implementation and downstream authority boundaries, including:

```text
src/incident_diagnostic_api/tools/contracts.py
src/incident_diagnostic_api/tools/registry.py
src/incident_diagnostic_api/tools/mock.py
src/incident_diagnostic_api/tools/dispatcher.py
src/incident_diagnostic_api/tools/__init__.py
src/incident_diagnostic_api/contracts/common.py
src/incident_diagnostic_api/contracts/trace.py
src/incident_diagnostic_api/runtime/traces.py
tests/tools/test_mock.py
tests/tools/test_dispatcher.py
docs/interview-accelerator/phases/PHASE_08_POLICY_BASED_ROUTING.md
docs/interview-accelerator/phases/PHASE_09_HUMAN_APPROVAL.md
```

The review specifically tested whether R2 can truthfully implement its claimed outcome-consistency evidence without reopening closed Phase 7D files or importing Phase 8/9/CT-07 authority.

## 6. Independent Review Decision

```text
PHASE_7E_R2_ARCHITECTURE_ACCEPTANCE_R1=FAIL
PHASE_7E_R2_IMPLEMENTATION_AUTHORITY_R1=WITHHELD

PHASE_7E_R2_HIGH_LEVEL_DIRECTION=ACCEPTED
PHASE_7E_R2_NARROWED_OUTCOME_CONSISTENCY_SEMANTICS=ACCEPTED_IN_DIRECTION
PHASE_7E_R2_ARCHITECTURE_CORRECTION_REQUIRED=YES

PHASE_7E_SOURCE_CODE_MUTATION_AUTHORITY=NONE
PHASE_7E_TEST_MUTATION_AUTHORITY=NONE
PHASE_7E_EXPORT_MUTATION_AUTHORITY=NONE
PHASE_7E_IMPLEMENTATION_AUTHORITY=NONE
PHASE_7E_REAL_TOOL_EXECUTION_AUTHORITY=NONE
```

R2 successfully corrects the principal R1 provenance defects and preserves downstream authority boundaries.

However, independent review found new implementation-blocking ambiguities in the evidence minimization and outcome-admissibility truth conditions.

The defects are bounded and repairable without reopening Phase 7D, but they must be corrected at the architecture level before implementation authority may be granted.

This is a rejection for bounded semantic correction, not a rejection of the Phase 7E capability direction.

## 7. R2-A1 — Unreachable Normal Registry-Miss State

### Review result

```text
R2_A1_RESOLUTION_VALID=PASS
```

R2 correctly removes `NOT_REGISTERED` as a normal evidence state.

Current repository facts remain:

- `ToolRequest.tool_name` is a closed `ToolName`.
- Valid `ToolRegistry` construction requires exactly the complete `ToolName` set.
- A valid request plus valid registry therefore resolves the request tool definition.

R2 correctly refuses to reopen Phase 7D merely to make its defensive `KeyError -> TOOL_NOT_REGISTERED` branch normally reachable.

### Disposition

`ACCEPTED`.

## 8. R2-A2 — Dispatcher Producer Provenance

### Review result

```text
R2_A2_RESOLUTION_VALID=PASS
```

R2 correctly removes the claim that a supplied outcome proves which dispatcher produced it.

The repository publicly exposes `ToolResult`, `ToolError`, `build_deterministic_mock_tool_result`, and `build_deterministic_mock_tool_error`.

Therefore typed outcomes can exist without going through the Phase 7D dispatcher.

R2 correctly treats `evaluated_dispatch_semantics_version` as evaluation context only rather than producer provenance.

### Disposition

`ACCEPTED`.

## 9. R2-A3 — Registry Producer Provenance

### Review result

```text
R2_A3_RESOLUTION_VALID=PASS
```

R2 correctly distinguishes:

```text
evaluated_registry_version
registry_declared_*
```

from historical producer provenance.

The supplied registry is evaluation context only.

R2 does not claim that the supplied registry was historically used to produce the supplied outcome.

### Disposition

`ACCEPTED`, subject to the separate R2-F1 minimization defect concerning the registry version value itself.

## 10. R2-A4 — Controlled Evidence-Construction Error Model

### Review result

```text
R2_A4_ERROR_MODEL_SUFFICIENT=PASS_IN_DIRECTION_WITH_R3_EXTENSION_REQUIRED
```

R2 materially improves R1 by defining a closed controlled error namespace:

```text
IDENTITY_MISMATCH
VERSION_MISMATCH
TEMPORAL_INVERSION
REGISTRY_OUTCOME_CONTRADICTION
OUTCOME_SHAPE_CONTRADICTION
```

This is consistent with the repository precedent of a dedicated controlled evidence-generation exception rather than arbitrary exceptions becoming public behavior.

However, R2-F1 below introduces a valid-input evaluation-context problem that R2 does not currently assign an explicit controlled disposition.

R3 must either:

1. remove the unbounded registry-version value from evidence, or
2. define a bounded registry-version evidence type and a deterministic controlled failure semantic for a valid `ToolRegistry` whose version cannot be represented safely.

This does not invalidate the error-model direction; it prevents the current model from being implementation-complete.

## 11. R2-A5 — Immutability Scope

### Review result

```text
R2_A5_IMMUTABILITY_SCOPE_TRUTHFUL=PASS
```

The live `ContractModel` is configured with `frozen=True` and `extra="forbid"`.

R2 now explicitly limits the claim to:

```text
FROZEN_IN_PROCESS_CONTRACT_VALUE=YES
```

and rejects stronger unsupported claims:

```text
DURABLE_IMMUTABILITY=NO
APPEND_ONLY_STORAGE=NO
TAMPER_EVIDENCE=NO
CRYPTOGRAPHIC_INTEGRITY=NO
DIGITAL_SIGNATURE=NO
PERSISTENCE=NO
```

### Disposition

`ACCEPTED`.

## 12. R2-A6 — Registry Declarations Versus Policy / Approval Decisions

### Review result

```text
R2_A6_REGISTRY_DECLARATION_NAMES_NONAUTHORITATIVE=PASS
```

R2 correctly namespaces registry metadata as `registry_declared_*` and explicitly forbids fields that would imply Phase 8 or Phase 9 authority.

R2 does not convert registry metadata into an authorization result.

R2 does not convert `APPROVAL_REQUIRED` into evidence that a trusted approval exists.

### Disposition

`ACCEPTED`.

## 13. R2-A7 — CT-07 Non-Drift

### Review result

```text
R2_A7_CT07_NON_DRIFT=PASS
```

CT-07 continues to own the repository-wide lifecycle `TraceEvent` contract, stage/event mappings, lifecycle correlation, runtime trace generation, and policy-decision lineage where applicable.

R2 does not add CT-07 event names, stage mappings, runtime trace mutation, or a competing global trace chain.

Request/trace identifiers in Phase 7E are correlation inherited from tool envelopes, not lifecycle-trace authority.

### Disposition

`ACCEPTED`.

## 14. R2-A8 — Phase 8 Non-Drift

### Review result

```text
R2_A8_PHASE8_NON_DRIFT=PASS
```

The live Phase 8 design owns:

```text
PDP
PEP
ALLOW
DENY
REQUIRE_APPROVAL
restricted routing
policy decision identifier
policy version
reason codes
expiry
enforcement
policy lineage
```

R2 does not implement or emulate those semantics.

A successful Phase 7E evidence value is explicitly not authorization.

### Disposition

`ACCEPTED`.

## 15. R2-A9 — Phase 9 Non-Drift

### Review result

```text
R2_A9_PHASE9_NON_DRIFT=PASS
```

The live Phase 9 design continues to own trusted approval, approver identity, scope, expiry, revocation, separation of duties, revalidation, one-time execution identity, and approval-to-execution lineage.

R2 does not claim that `ToolErrorCode.APPROVAL_REQUIRED` establishes any Phase 9 object or approval.

### Disposition

`ACCEPTED`.

## 16. R2-F1 — `evaluated_registry_version` Is Not Bounded by the Current Registry Contract

Severity: `BLOCKING`

### R2 proposal

R2 proposes:

```python
evaluated_registry_version: str
```

and describes the evidence object as bounded/content-minimized.

### Repository fact

The live `ToolRegistry.version` type is plain `str`.

Its constructor validates only:

```python
if not self.version.strip():
    raise ValueError("registry version must not be empty")
```

There is no maximum length, allowlisted pattern, or evidence-safe type bound.

A valid `ToolRegistry` can therefore contain, for example:

```text
an arbitrarily long version string
whitespace-surrounded content
free-form text
secret-looking content
payload-like content
```

while still satisfying the current registry constructor.

### Consequence

A Phase 7E builder implemented literally from R2 could copy an unbounded valid-registry string into a record that claims to be content-minimized and bounded.

That contradicts the Phase 7E evidence contract.

This defect exists even though the registry version is not claimed as producer provenance.

### Required R3 correction

R3 must choose and freeze one of these semantics:

```text
OPTION_A=REMOVE_EVALUATED_REGISTRY_VERSION_FROM_THE_INITIAL_EVIDENCE_CONTRACT
```

or:

```text
OPTION_B=DEFINE_A_PHASE_7E_LOCAL_BOUNDED_REGISTRY_VERSION_EVIDENCE_TYPE_AND_CONTROLLED_REJECTION
```

If Option B is selected, the correction must remain within Phase 7E and must not mutate `registry.py` merely to satisfy the evidence layer.

The controlled failure must be deterministic and non-sensitive.

Preferred architecture-level semantics are equivalent to:

```text
VALID_TOOL_REGISTRY_DOES_NOT_AUTOMATICALLY_MEAN_EVIDENCE_SAFE_REGISTRY_VERSION
UNBOUNDED_REGISTRY_VERSION_COPY=PROHIBITED
REGISTRY_VERSION_VALUE_LOGGING_AUTHORITY=BOUNDED_ONLY
```

### Review disposition

```text
R2_A10_CONTENT_MINIMIZATION=FAIL
R2_F1_UNBOUNDED_REGISTRY_VERSION=BLOCKING
```

## 17. R2-F2 — Outcome Admissibility Matrix Is Incomplete for the Current Valid Phase 7D Domain

Severity: `BLOCKING`

### R2 claim

R2 claims consistency against bounded Phase 7D dispatch semantics.

It explicitly states that:

- side-effecting definitions are consistent with `APPROVAL_REQUIRED`, and
- read-only definitions eligible for local result completion are not consistent with fabricated `APPROVAL_REQUIRED` merely because their registry metadata says `POLICY_DECISION`.

### Repository fact

The live Phase 7D dispatcher has these branches:

```text
registry miss -> TOOL_NOT_REGISTERED
general_shell_access -> ACCESS_DENIED
execution_enabled -> ACCESS_DENIED
side_effect != NONE -> APPROVAL_REQUIRED
approval_requirement == HUMAN_APPROVAL -> APPROVAL_REQUIRED
otherwise -> deterministic local ToolResult
```

But current valid registry construction independently enforces:

```text
registry contains every ToolName
execution_enabled == False
general_shell_access == False
side_effect == NONE cannot use HUMAN_APPROVAL
```

Therefore, over valid current request/registry objects, the normal Phase 7D disposition domain is much narrower:

```text
SIDE_EFFECT_NONE -> ToolResult
SIDE_EFFECT_NON_NONE -> ToolError(APPROVAL_REQUIRED)
```

The public typed error contract and public mock-error builder can nevertheless construct normalized errors for:

```text
INVALID_REQUEST
TOOL_NOT_REGISTERED
ACCESS_DENIED
APPROVAL_REQUIRED
REQUEST_TIMEOUT
TOOL_UNAVAILABLE
RESULT_INVALID
INTERNAL_ERROR
```

### Consequence

R2 does not freeze whether a typed-but-non-Phase-7D-normal error such as:

```text
REQUEST_TIMEOUT
TOOL_UNAVAILABLE
RESULT_INVALID
INTERNAL_ERROR
ACCESS_DENIED
TOOL_NOT_REGISTERED
```

is accepted or rejected by `build_deterministic_tool_outcome_evidence` when paired with a valid current registry.

Merely validating code/category/retryability mapping is insufficient to establish consistency with Phase 7D dispatch semantics.

Two conforming implementations could therefore disagree while both claiming compliance with R2.

That is an unacceptable ambiguity for an evidence primitive.

### Required R3 correction

R3 must define an explicit complete admissibility matrix for the current contract version.

Preferred current semantics:

```text
IF registry_definition.side_effect == NONE:
    ONLY ToolResult IS ADMISSIBLE

IF registry_definition.side_effect != NONE:
    ONLY ToolError(error_code=APPROVAL_REQUIRED) IS ADMISSIBLE

TOOL_NOT_REGISTERED=NORMAL_ADMISSIBILITY_NO
ACCESS_DENIED=NORMAL_ADMISSIBILITY_NO
INVALID_REQUEST=NORMAL_ADMISSIBILITY_NO
REQUEST_TIMEOUT=NORMAL_ADMISSIBILITY_NO
TOOL_UNAVAILABLE=NORMAL_ADMISSIBILITY_NO
RESULT_INVALID=NORMAL_ADMISSIBILITY_NO
INTERNAL_ERROR=NORMAL_ADMISSIBILITY_NO
```

The architecture should state that a future dispatcher version which legitimately introduces additional normal outcomes requires a new Phase 7E evidence-semantic version or a separately reviewed compatibility change.

### Review disposition

```text
R2_OUTCOME_ADMISSIBILITY_MATRIX=FAIL_INCOMPLETE
R2_F2_ERROR_DISPOSITION_DOMAIN=BLOCKING
```

## 18. R2-F3 — Successful Result Consistency Truth Condition Is Not Exact Enough

Severity: `BLOCKING`

### R2 language

R2 says implementation should verify that a supplied successful result is:

> structurally consistent with the deterministic Phase 7C local mock result semantics

and tests should reject an invalid deterministic-local "shape."

### Repository fact

The Phase 7C mock result is deterministic and has exact value semantics derived from the request:

```text
mock_runtime_version=7c.1
tool_name=<exact request tool name>
execution_mode=deterministic_local_mock
real_execution=false
network_access=false
credential_access=false
argument_count=<exact request argument count>
argument_names=<exact sorted request argument names>
idempotency_key=<exact request value when present>
```

The public `ToolResult` contract permits callers to construct other bounded JSON outputs.

### Consequence

The phrase "structurally consistent" does not unambiguously establish whether Phase 7E must reject a supplied result whose keys are plausible but whose deterministic values are false, for example:

```text
real_execution=true
network_access=true
wrong mock_runtime_version
wrong tool_name in output payload
wrong argument_count
wrong argument_names
wrong idempotency_key
```

The Phase 7E evidence object may intentionally omit these raw values, but the evaluator's truth condition still must be exact enough to prevent fabricated outcomes from being certified as consistent.

### Required R3 correction

R3 must freeze the successful-result predicate.

Preferred semantics:

```text
EXPECTED_RESULT=
build_deterministic_mock_tool_result(
    request,
    completed_at=outcome.completed_at,
)

SUPPLIED_RESULT_IS_CONSISTENT=
    supplied_outcome == EXPECTED_RESULT
```

The evaluator may transiently compare typed values in process.

It must not copy raw argument values, raw output values, or the raw idempotency-key value into `ToolOutcomeEvidence`.

Calling the deterministic Phase 7C mock builder for comparison does not add real execution authority and does not require mutating `mock.py`.

The Phase 7D dispatcher itself must remain uncalled by the evidence builder.

If R3 chooses a narrower comparison than exact typed equality, it must enumerate every value-level invariant that participates in consistency; "shape" alone is insufficient.

### Review disposition

```text
R2_RESULT_CONSISTENCY_PREDICATE=FAIL_UNDERSPECIFIED
R2_F3_FABRICATED_RESULT_ACCEPTANCE_RISK=BLOCKING
```

## 19. R2-F4 — Error Safe-Message Participation in the Consistency Claim Is Ambiguous

Severity: `HIGH / BLOCKING UNTIL CLAIM IS FROZEN`

### R2 content-minimization decision

R2 correctly prohibits copying:

```text
ToolError.safe_message
```

into `ToolOutcomeEvidence`.

### Ambiguity

R2 does not explicitly state whether `safe_message`:

1. participates in the consistency predicate but is omitted from evidence storage, or
2. is deliberately outside the consistency predicate.

Because public mock-error construction accepts caller-supplied `safe_message`, two otherwise identical `ToolError` values can differ in that field.

### Consequence

The current Phase 7E claim says the supplied typed tool outcome is internally consistent with the request and evaluated dispatch semantics.

If arbitrary `safe_message` values are ignored, that claim may be read more broadly than the actual predicate.

If exact dispatcher text is required, R2 does not currently specify the expected text or comparison rule.

### Required R3 correction

R3 must choose one explicit meaning.

Preferred least-coupled option:

```text
SAFE_MESSAGE_STORED_IN_EVIDENCE=NO
SAFE_MESSAGE_INCLUDED_IN_CONSISTENCY_CLAIM=NO
```

and narrow the claim to:

> selected typed control fields of the supplied outcome are consistent with the current Phase 7D disposition rules.

Alternative:

```text
SAFE_MESSAGE_STORED_IN_EVIDENCE=NO
SAFE_MESSAGE_TRANSIENTLY_VALIDATED=YES
```

with an exact deterministic comparison rule.

The architecture must not leave this implicit.

### Review disposition

```text
R2_ERROR_SAFE_MESSAGE_SEMANTICS=FAIL_AMBIGUOUS
```

## 20. R2-A10 — Content Minimization Overall Decision

R2 materially improves minimization by excluding raw arguments, raw outputs, raw idempotency values, secrets, arbitrary exception text, and `ToolError.safe_message` from the evidence record.

Argument/output field-name metadata is bounded by the existing `ToolArgumentName` contract and may remain metadata rather than payload evidence.

However R2-F1 prevents full acceptance because `evaluated_registry_version` is not bounded by the source registry contract.

```text
R2_A10_CONTENT_MINIMIZATION=FAIL_BLOCKING_R2_F1
```

## 21. R2-A11 — Exact Four-File Implementation Boundary

R2 proposes:

```text
src/incident_diagnostic_api/tools/evidence.py
src/incident_diagnostic_api/tools/__init__.py
tests/tools/test_evidence.py
docs/tools/PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_EVIDENCE_IMPLEMENTATION_AND_EVIDENCE.md
```

Independent review finds that this boundary remains technically sufficient for the corrected narrow capability.

The newly discovered defects can be resolved without modifying:

```text
dispatcher.py
mock.py
registry.py
contracts.py
trace.py
runtime/traces.py
```

For example:

- a Phase 7E-local bounded registry-version evidence type can live in `evidence.py`, or the registry-version field can be omitted;
- the exact admissibility matrix can live in `evidence.py`;
- deterministic result equality can use the existing public Phase 7C mock builder without modifying it;
- tests can be implemented in `tests/tools/test_evidence.py`;
- public exports can be added through the existing `tools/__init__.py` candidate surface.

Therefore:

```text
R2_A11_FOUR_FILE_BOUNDARY_TECHNICALLY_SUFFICIENT=PASS
R2_A11_FOUR_FILE_BOUNDARY_IMPLEMENTATION_AUTHORITY=NONE
```

Technical sufficiency is not authority.

Because the architecture truth conditions remain defective, the boundary is not activated for implementation by this review.

## 22. Full R2 Acceptance Matrix

```text
R2_A1_RESOLUTION_VALID=PASS
R2_A2_RESOLUTION_VALID=PASS
R2_A3_RESOLUTION_VALID=PASS
R2_A4_ERROR_MODEL_SUFFICIENT=PASS_IN_DIRECTION_R3_EXTENSION_REQUIRED
R2_A5_IMMUTABILITY_SCOPE_TRUTHFUL=PASS
R2_A6_REGISTRY_DECLARATION_NAMES_NONAUTHORITATIVE=PASS
R2_A7_CT07_NON_DRIFT=PASS
R2_A8_PHASE8_NON_DRIFT=PASS
R2_A9_PHASE9_NON_DRIFT=PASS
R2_A10_CONTENT_MINIMIZATION=FAIL
R2_A11_FOUR_FILE_BOUNDARY_SUFFICIENT=PASS_TECHNICALLY_NOT_AUTHORIZED

R2_PROVENANCE_CLAIMS_DO_NOT_EXCEED_INPUT_EVIDENCE=PASS
R2_NO_UNREACHABLE_NORMAL_REGISTRY_MISS_STATE=PASS
R2_NO_REAL_EXECUTION_AUTHORITY=PASS

R2_F1_UNBOUNDED_REGISTRY_VERSION=BLOCKING
R2_F2_ERROR_DISPOSITION_DOMAIN=BLOCKING
R2_F3_RESULT_CONSISTENCY_PREDICATE=BLOCKING
R2_F4_ERROR_SAFE_MESSAGE_SEMANTICS=BLOCKING_UNTIL_FROZEN
```

## 23. Why Implementation Authority Is Withheld

The implementation boundary itself is not the problem.

The problem is that R2 does not yet define one unique, bounded truth function from valid inputs to either:

```text
ToolOutcomeEvidence
```

or:

```text
ToolOutcomeEvidenceError
```

A security-relevant evidence primitive must not permit materially different implementations to disagree about whether the same valid typed outcome is consistent.

R2-F1 through R2-F4 leave that possibility open.

Therefore implementation authority cannot be granted safely from R2 as written.

## 24. Required R3 Semantic Correction

R3 should preserve all accepted R2 corrections and make only the additional bounded semantic repairs required by this review.

R3 must not reopen the already-corrected R1 provenance direction.

Minimum R3 requirements:

```text
R3_PRESERVE_OUTCOME_CONSISTENCY_DIRECTION=YES
R3_PRESERVE_NO_PRODUCER_PROVENANCE=YES
R3_PRESERVE_REGISTRY_DECLARED_NAMESPACE=YES
R3_PRESERVE_CT07_NON_DRIFT=YES
R3_PRESERVE_PHASE8_NON_DRIFT=YES
R3_PRESERVE_PHASE9_NON_DRIFT=YES
R3_PRESERVE_NO_PERSISTENCE=YES
R3_PRESERVE_NO_NETWORK=YES
R3_PRESERVE_NO_CREDENTIALS=YES
R3_PRESERVE_NO_REAL_EXECUTION=YES

R3_BOUND_OR_REMOVE_EVALUATED_REGISTRY_VERSION=REQUIRED
R3_COMPLETE_OUTCOME_ADMISSIBILITY_MATRIX=REQUIRED
R3_FREEZE_EXACT_RESULT_CONSISTENCY_PREDICATE=REQUIRED
R3_FREEZE_SAFE_MESSAGE_PARTICIPATION_SEMANTICS=REQUIRED
R3_RECONFIRM_CONTROLLED_ERROR_MAPPING=REQUIRED
R3_RECONFIRM_FOUR_FILE_BOUNDARY=REQUIRED
```

## 25. Historical Preservation

R1 architecture remains historical evidence.

R1 independent review remains historical evidence.

R2 architecture remains historical evidence of the first narrowed outcome-consistency design.

This R2 review must not rewrite any of them.

```text
R1_ARCHITECTURE_HISTORY_PRESERVED=YES
R1_REVIEW_HISTORY_PRESERVED=YES
R2_ARCHITECTURE_HISTORY_PRESERVED=YES
R2_ARCHITECTURE_REWRITTEN=NO
R2_ARCHITECTURE_DELETED=NO
```

A future R3 architecture should supersede R2 only for future implementation consideration.

## 26. Exact Implementation Authority Decision

```text
PHASE_7E_R2_ARCHITECTURE_ACCEPTANCE=FAIL
PHASE_7E_R2_ARCHITECTURE_STATUS=REJECTED_FOR_IMPLEMENTATION_PENDING_BOUNDED_R3_CORRECTION

PHASE_7E_IMPLEMENTATION=NOT_STARTED
PHASE_7E_IMPLEMENTATION_AUTHORITY=NONE
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
PHASE_7E_REAL_TOOL_EXECUTION_AUTHORITY=NONE
PHASE_7E_EXTERNAL_MUTATION_AUTHORITY=NONE
```

No source implementation may begin from this R2 review.

## 27. Honest Current Claim

The strongest valid claim after this review is:

> Phase 7E's R2 architecture successfully removes the R1 producer-provenance overclaims, unreachable normal registry-miss evidence state, ambiguous policy/approval field names, and durable-immutability overclaim while preserving CT-07 and Phase 8/9 authority boundaries. Independent R2 review nevertheless withholds implementation authority because the initial narrowed design still leaves an unbounded registry-version evidence value and does not fully freeze the valid Phase 7D outcome-admissibility and exact result/error consistency predicates.

## 28. Next Disciplined Gate

```text
NEXT_GATE=
PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_OUTCOME_CONSISTENCY_EVIDENCE_
R2_REJECTION_
BOUNDED_R3_SEMANTIC_CORRECTION_AND_
COMPLETE_STANDALONE_REPLACEMENT_ARCHITECTURE_PREPARATION
```

That next gate must remain strictly documentation-only.

Its job is to preserve every accepted R2 correction while resolving only R2-F1 through R2-F4 into one complete standalone R3 architecture candidate.

It must not implement source code, tests, exports, routes, persistence, policy, approval, network access, credentials, provider integrations, or real tool execution.

The R3 documentation commit must pass exact-commit CI before a subsequent independent R3 architecture acceptance and bounded implementation-authority review may occur.
