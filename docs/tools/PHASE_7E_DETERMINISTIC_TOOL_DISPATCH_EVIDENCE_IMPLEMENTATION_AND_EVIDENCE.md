# Phase 7E — Deterministic Tool Dispatch Outcome Consistency Evidence Implementation and Evidence R1

## 1. Purpose

This document records the first bounded implementation candidate for the accepted Phase 7E R3 architecture.

Selected capability:

```text
PHASE_7E_SELECTED_CAPABILITY=
DETERMINISTIC_TOOL_DISPATCH_OUTCOME_CONSISTENCY_EVIDENCE
```

The implementation remains local, deterministic, in-process, and non-executing.

It does not establish dispatcher producer provenance, registry producer provenance, real execution provenance, policy authorization, human approval, durable persistence, tamper evidence, or cryptographic producer identity.

## 2. Exact Authority Chain

R3 architecture:

```text
R3_ARCHITECTURE_COMMIT=
c908b7043cd32721c0f85734c08610c626233e31

R3_ARCHITECTURE_TREE=
3cdcebe8164c52b93f81fb40d71380681836daca

R3_ARCHITECTURE_CI_RUN=34646764628
R3_ARCHITECTURE_CI_STATUS=COMPLETED
R3_ARCHITECTURE_CI_CONCLUSION=SUCCESS
```

R3 independent acceptance review:

```text
R3_REVIEW_COMMIT=
5f69482d06c07f6e58c8e097ca8f270c68bf1c49

R3_REVIEW_TREE=
0a13025588152750653588331be3726b109e9850

R3_REVIEW_CI_RUN=34647526627
R3_REVIEW_CI_STATUS=COMPLETED
R3_REVIEW_CI_CONCLUSION=SUCCESS
```

The implementation gate began only after run `34647526627` succeeded at the exact review SHA and `main` was verified at that same review commit.

```text
IMPLEMENTATION_AUTHORITY=BOUNDED
IMPLEMENTATION_AUTHORITY_SOURCE=R3_INDEPENDENT_ARCHITECTURE_ACCEPTANCE_R1
IMPLEMENTATION_PARENT_SHA=5f69482d06c07f6e58c8e097ca8f270c68bf1c49
```

## 3. Exact Four-File Boundary

The accepted implementation boundary is exactly:

```text
src/incident_diagnostic_api/tools/evidence.py
src/incident_diagnostic_api/tools/__init__.py
tests/tools/test_evidence.py
docs/tools/PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_EVIDENCE_IMPLEMENTATION_AND_EVIDENCE.md
```

```text
AUTHORIZED_IMPLEMENTATION_FILE_COUNT=4
FIFTH_FILE_AUTHORITY=NONE
```

No existing Phase 7A–7D implementation file is modified.

## 4. Implemented Runtime Namespace

The implementation introduces:

```text
TOOL_OUTCOME_EVIDENCE_VERSION=7e.1
ToolOutcomeKind
ToolOutcomeConsistencyStatus
ToolOutcomeEvidence
ToolOutcomeEvidenceErrorCode
ToolOutcomeEvidenceError
build_deterministic_tool_outcome_evidence
```

The public namespace is exported through `incident_diagnostic_api.tools`.

## 5. Evidence Contract

`ToolOutcomeEvidence` is a frozen Pydantic contract inheriting the repository-wide `VersionedContract` behavior.

It uses exact current versions:

```text
tool_outcome_evidence_version=7e.1
tool_contract_version=7a.1
tool_envelope_version=tool-envelope-v1
evaluated_dispatch_semantics_version=7d.1
```

The evidence contract carries only minimized control metadata:

```text
request_id
trace_id
tool_name
tool_contract_version
tool_envelope_version
evaluated_dispatch_semantics_version
registry_declared_capability
registry_declared_side_effect
registry_declared_risk_tier
registry_declared_idempotency_requirement
registry_declared_approval_requirement
registry_declared_timeout_seconds
registry_declared_authorization_required
registry_declared_execution_enabled
registry_declared_general_shell_access
outcome_kind
consistency_status
result_status
error_code
error_category
retryable
idempotency_key_present
argument_names
output_names
requested_at
outcome_at
```

`argument_names` and `output_names` are each bounded to at most 32 entries and must be unique and sorted.

The contract enforces mutually exclusive result/error evidence shapes and rejects direct construction that contradicts current Phase 7 registry safety declarations.

## 6. Deterministic Truth Function

The builder implements the accepted R3 order:

```text
1. request/outcome identity equality
2. request/outcome contract/envelope version equality
3. temporal monotonicity
4. registry definition resolution
5. registry safety declaration validation
6. current valid-registry admissibility matrix
7A. exact Phase 7C ToolResult equality for read-only outcomes
7B. APPROVAL_REQUIRED normalized control-field validation for side-effecting outcomes
8. minimized evidence construction
```

No evidence object is returned when any required check fails.

## 7. Current Valid-Registy Admissibility Matrix

The implemented normal domain is exactly:

```text
SIDE_EFFECT_NONE -> ToolResult
SIDE_EFFECT_NON_NONE -> ToolError(APPROVAL_REQUIRED)
```

The following error codes are not accepted as normal current Phase 7E-consistent outcomes:

```text
INVALID_REQUEST
TOOL_NOT_REGISTERED
ACCESS_DENIED
REQUEST_TIMEOUT
TOOL_UNAVAILABLE
RESULT_INVALID
INTERNAL_ERROR
```

`APPROVAL_REQUIRED` is accepted only for a side-effecting registry definition.

## 8. Exact Successful Result Predicate

For a read-only tool, the builder computes:

```python
expected = build_deterministic_mock_tool_result(
    request,
    completed_at=outcome.completed_at,
)
```

and requires:

```python
outcome == expected
```

This rejects key-shape-only or subset-equivalent fabricated results.

The comparison covers the complete current deterministic Phase 7C result, including:

```text
request identity
trace identity
tool identity
status
timestamp
mock_runtime_version
tool_name output
execution_mode
real_execution
network_access
credential_access
argument_count
argument_names
idempotency_key presence/value
```

Raw values are used only transiently for comparison and are not copied into Phase 7E evidence.

## 9. Error Consistency Predicate

For a side-effecting tool, the builder requires:

```text
error_code=APPROVAL_REQUIRED
error_category=APPROVAL
retryable=false
```

`ToolError.safe_message` is intentionally excluded from both the consistency claim and evidence record.

Two otherwise equal admissible error outcomes that differ only in `safe_message` produce equal Phase 7E evidence.

## 10. Controlled Failure Model

Implemented error codes:

```text
IDENTITY_MISMATCH
VERSION_MISMATCH
TEMPORAL_INVERSION
REGISTRY_OUTCOME_CONTRADICTION
OUTCOME_SHAPE_CONTRADICTION
```

Each code maps to a fixed non-sensitive message.

Controlled errors do not interpolate:

```text
raw request arguments
raw output values
raw idempotency-key values
registry.version
ToolError.safe_message
credentials
tokens
secrets
environment values
arbitrary caught exception text
hidden reasoning
```

## 11. Registry-Version Minimization

The implementation never reads, stores, hashes, truncates, emits, or incorporates `registry.version` into evidence equality.

Two valid registries with identical declarations but different free-form version strings produce equal evidence for identical request/outcome inputs.

```text
REGISTRY_VERSION_STORED_IN_EVIDENCE=NO
REGISTRY_VERSION_DERIVATIVE_STORED_IN_EVIDENCE=NO
REGISTRY_VERSION_IN_TRUTH_FUNCTION=NO
```

## 12. Version-Mismatch Reachability Clarification

The current `ToolRequest`, `ToolResult`, and `ToolError` contracts use fixed literal versions.

Therefore:

```text
NORMAL_VALID_INPUT_VERSION_MISMATCH_REACHABLE=NO
VERSION_MISMATCH_CHECK_CLASSIFICATION=DEFENSE_IN_DEPTH
VERSION_MISMATCH_NORMAL_EVIDENCE_STATE=NO
```

The focused tests exercise this defensive branch only through Pydantic `model_copy(update=...)` validation bypass and must not be interpreted as a normal valid-input state.

## 13. Evidence-Builder Provenance Limitation

A standalone in-process `ToolOutcomeEvidence` value does not prove that the builder produced it.

The implementation therefore records:

```text
EVIDENCE_BUILDER_PROVENANCE=NOT_ESTABLISHED
DIRECT_CONSTRUCTION_PROVES_EVALUATION=NO
DURABLE_PRODUCER_IDENTITY=NO
CRYPTOGRAPHIC_BUILDER_RECEIPT=NO
```

The supported claim is about the deterministic behavior of `build_deterministic_tool_outcome_evidence` when invoked with the documented typed inputs.

## 14. Content Minimization

The evidence contract does not store:

```text
registry.version
raw argument values
raw output values
raw idempotency-key value
ToolError.safe_message
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

Allowed request/output names remain bounded metadata only.

## 15. CT-07 Non-Drift

The implementation does not modify or generate CT-07 lifecycle events.

It does not add event names, alter lifecycle stage mappings, create a second trace chain, or claim lifecycle trace authority.

```text
CT07_MUTATION=NONE
CT07_AUTHORITY=UNCHANGED
```

## 16. Phase 8 Non-Drift

The implementation does not emit or establish:

```text
ALLOW
DENY
REQUIRE_APPROVAL policy decision
policy_decision_id
policy version result
policy expiry
policy enforcement authorization
```

Registry approval metadata remains declarative only.

```text
PHASE8_POLICY_AUTHORITY=UNCHANGED
```

## 17. Phase 9 Non-Drift

The implementation does not create or establish:

```text
approval request
approval identity
approver identity
approval scope
approval expiry
revocation
revalidation
trusted execution authority
```

`APPROVAL_REQUIRED` means only that the supplied side-effecting error matches the current Phase 7D fail-closed disposition.

```text
PHASE9_APPROVAL_AUTHORITY=UNCHANGED
```

## 18. No Real Execution

The implementation does not introduce:

```text
requests
httpx
boto3
kubernetes client SDK
Jira client SDK
ServiceNow client SDK
database execution
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
external mutation
```

The only existing runtime behavior invoked is the deterministic local Phase 7C result builder used as the exact comparison oracle.

```text
REAL_TOOL_EXECUTION=NOT_ESTABLISHED_AND_NOT_AUTHORIZED
NETWORK_ACCESS=NOT_AUTHORIZED
CREDENTIAL_ACCESS=NOT_AUTHORIZED
EXTERNAL_MUTATION=NOT_AUTHORIZED
```

## 19. Focused Test Coverage

`tests/tools/test_evidence.py` covers:

```text
explicit 7e.1 evidence version
all five current read-only tools
both current side-effecting tools
all typed error codes on every read-only tool
all non-APPROVAL_REQUIRED errors on every side-effecting tool
side-effecting ToolResult rejection
registry.version exclusion from evidence and errors
identity mismatch rejection
version mismatch defense-in-depth
outcome timestamp monotonicity
exact-result mutation rejection
unexpected/missing idempotency behavior
safe_message exclusion and equality behavior
unknown evidence field rejection
wrong evidence-version rejection
frozen contract posture
result/error direct-construction invariants
name-cardinality bound
unique/sorted metadata names
output-name shape invariants
absence of dispatcher invocation
absence of prohibited runtime surfaces
```

## 20. Required Repository Validation

This implementation candidate is not accepted as tested or evidence-recorded merely because the four files are committed.

The exact implementation commit must pass repository CI including:

```text
Ruff linting
Ruff formatting
strict MyPy
full tests with branch coverage
dependency integrity
local container build
container isolation checks
health verification
```

The exact CI run must be bound to the exact implementation commit SHA.

## 21. Post-Materialization Evidence Fields

The commit containing this document establishes the implementation candidate identity.

The following are not self-referentially embedded before the commit exists and must be verified from the resulting Git object and CI run:

```text
IMPLEMENTATION_COMMIT=<verify after commit creation>
IMPLEMENTATION_TREE=<verify after commit creation>
IMPLEMENTATION_PARENT=5f69482d06c07f6e58c8e097ca8f270c68bf1c49
IMPLEMENTATION_CI_RUN=<verify after CI trigger>
IMPLEMENTATION_CI_HEAD_SHA=<must equal exact implementation commit>
IMPLEMENTATION_CI_STATUS=<verify>
IMPLEMENTATION_CI_CONCLUSION=<verify>
```

This avoids rewriting the implementation candidate merely to make it contain its own Git identity.

## 22. Known Limitations

```text
DISPATCH_PRODUCER_PROVENANCE=NOT_ESTABLISHED
REGISTRY_PRODUCER_PROVENANCE=NOT_ESTABLISHED
EVIDENCE_BUILDER_PROVENANCE=NOT_ESTABLISHED
REAL_EXECUTION_PROVENANCE=NOT_ESTABLISHED
POLICY_DECISION=NOT_ESTABLISHED
HUMAN_APPROVAL=NOT_ESTABLISHED
PERSISTENCE=NOT_ESTABLISHED
DURABLE_IMMUTABILITY=NO
TAMPER_EVIDENCE=NO
CRYPTOGRAPHIC_INTEGRITY=NO
DIGITAL_SIGNATURE=NO
PRODUCTION_DEPLOYMENT=NO
```

The registry-declared timeout remains upstream declaration metadata and is not independently upper-bounded by Phase 7E.

## 23. Current Gate Posture

At file preparation time:

```text
PHASE_7D=CLOSED
PHASE_7E_R3_ARCHITECTURE=ACCEPTED
PHASE_7E_BOUNDED_IMPLEMENTATION_AUTHORITY=GRANTED
PHASE_7E_IMPLEMENTATION_CANDIDATE=PREPARED
PHASE_7E_IMPLEMENTATION_CI=PENDING_COMMIT_AND_EXACT_RUN
PHASE_7E_CLOSURE=NOT_AUTHORIZED
```

The implementation gate does not close Phase 7E.

## 24. Success Condition

This R1 implementation gate succeeds only if:

```text
exact four-file boundary is preserved
implementation commit has exact review commit as parent
focused Phase 7E tests pass
all prior Phase 7 tests remain green
full repository tests remain green
Ruff lint passes
Ruff format passes
strict MyPy passes
dependency integrity passes
container build and health verification pass
CI run head SHA equals the implementation commit
no prohibited runtime surface is introduced
```

If exact-commit CI fails, the implementation gate is not accepted and no closure authority follows.

## 25. Next Gate After Successful Exact-Commit CI

A successful implementation CI run permits only a separate implementation acceptance / closure-authority determination.

It does not itself close Phase 7E.

```text
NEXT_GATE=
PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_OUTCOME_CONSISTENCY_EVIDENCE_
IMPLEMENTATION_R1_
EXACT_COMMIT_CI_AND_INDEPENDENT_IMPLEMENTATION_ACCEPTANCE_REVIEW
```

## 26. Post-Materialization Corrected Implementation Evidence

The placeholders in Section 21 are historical pre-materialization placeholders. The authoritative post-materialization implementation lineage is now:

```text
ORIGINAL_IMPLEMENTATION_COMMIT=af5f32f7d6397405ba31f66068cf6036e7ffc50d
ORIGINAL_IMPLEMENTATION_TREE=23bbb0cb2ed52b16c4ff50f91d3fb274a8500e44
ORIGINAL_IMPLEMENTATION_PARENT=5f69482d06c07f6e58c8e097ca8f270c68bf1c49
ORIGINAL_IMPLEMENTATION_CI_RUN=34648808597
ORIGINAL_IMPLEMENTATION_CI_STATUS=COMPLETED
ORIGINAL_IMPLEMENTATION_CI_CONCLUSION=FAILURE
ORIGINAL_IMPLEMENTATION_CI_FAILURE_CLASS=RUFF_FORMAT_NONCONFORMANCE

CORRECTED_IMPLEMENTATION_COMMIT=1deb0d83de122c77db9585d5815a8fb64d13d979
CORRECTED_IMPLEMENTATION_TREE=02dd52694bb8b4d2973c7abc95ef8aa54afecab6
CORRECTED_IMPLEMENTATION_PARENT=af5f32f7d6397405ba31f66068cf6036e7ffc50d
CORRECTED_IMPLEMENTATION_CI_RUN=34656904707
CORRECTED_IMPLEMENTATION_CI_HEAD_SHA=1deb0d83de122c77db9585d5815a8fb64d13d979
CORRECTED_IMPLEMENTATION_CI_STATUS=COMPLETED
CORRECTED_IMPLEMENTATION_CI_CONCLUSION=SUCCESS
```

The formatting correction changed only:

```text
src/incident_diagnostic_api/tools/evidence.py
tests/tools/test_evidence.py
```

and introduced no semantic change.

The corrected exact-commit CI established:

```text
DEPENDENCY_INTEGRITY=PASS
RUFF_LINT=PASS
RUFF_FORMAT=PASS
STRICT_MYPY=PASS
MYPY_SOURCE_FILE_COUNT=110
COMPLETE_REPOSITORY_TEST_COUNT=1207
COMPLETE_REPOSITORY_TESTS=PASS
TOTAL_BRANCH_COVERAGE=93.90_PERCENT
PYTHON_QUALITY_AND_CONTRACT_TESTS_JOB=SUCCESS
LOCAL_CONTAINER_BUILD_AND_HEALTH_VERIFICATION_JOB=SUCCESS
NO_HOST_PORTS=PASS
INTERNAL_NETWORK_ISOLATION=PASS
CONTAINER_RUNTIME_RESTRICTIONS=PASS
HEALTH_VERIFICATION=PASS
READINESS_VERIFICATION=PASS
COVERAGE_ARTIFACT_ID=10285546847
COVERAGE_ARTIFACT_SHA256=f09b56a5884eb592f8004c548610a2498b08a81a47b32cdbbe083d0a81ec09ea
```

## 27. Independent Acceptance Gap Remediation R1

The independent corrected-implementation acceptance review withheld acceptance for three evidence-completeness gaps while finding the runtime semantics and authority boundaries sound.

This bounded remediation changes only:

```text
tests/tools/test_evidence.py
docs/tools/PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_EVIDENCE_IMPLEMENTATION_AND_EVIDENCE.md
```

It does not modify production source code, exports, dispatcher semantics, mock semantics, registry semantics, tool contracts, CT-07, policy, approval, persistence, network, credential, provider, shell, or real-tool-execution surfaces.

The test remediation adds exactly:

```text
1. repeated identical typed request/outcome/registry evaluation must return exactly equal ToolOutcomeEvidence values
2. direct ToolOutcomeEvidence construction with 33 output_names entries must fail validation
```

These additions close the two missing minimum test obligations identified by the independent review:

```text
IA_1_DETERMINISM_TEST=REMEDIATED_IN_CANDIDATE
IA_2_OUTPUT_NAME_CARDINALITY_TEST=REMEDIATED_IN_CANDIDATE
```

The current exact pre-remediation test collection derived from the fixed parametrization matrices is:

```text
PRE_REMEDIATION_FOCUSED_PHASE_7E_TEST_COUNT=93
PRE_REMEDIATION_COMPLETE_PHASE_7_TOOL_TEST_COUNT=203
```

The bounded remediation adds exactly two non-parameterized Phase 7E cases, therefore the candidate collection is:

```text
REMEDIATION_CANDIDATE_FOCUSED_PHASE_7E_TEST_COUNT=95
REMEDIATION_CANDIDATE_COMPLETE_PHASE_7_TOOL_TEST_COUNT=205
```

These candidate counts must remain consistent with the remediated test source and are subject to exact-commit CI before acceptance.

## 28. Remediation Authority and Pending Exact-CI Evidence

The remediation authority is limited to test-and-evidence completeness only.

```text
REMEDIATION_RUNTIME_SEMANTIC_CHANGE_AUTHORITY=NONE
REMEDIATION_ARCHITECTURE_CHANGE_AUTHORITY=NONE
REMEDIATION_EVIDENCE_PY_MUTATION_AUTHORITY=NONE
REMEDIATION_TOOLS_INIT_MUTATION_AUTHORITY=NONE
REMEDIATION_DISPATCHER_MUTATION_AUTHORITY=NONE
REMEDIATION_MOCK_MUTATION_AUTHORITY=NONE
REMEDIATION_REGISTRY_MUTATION_AUTHORITY=NONE
REMEDIATION_CONTRACT_MUTATION_AUTHORITY=NONE
REMEDIATION_POLICY_AUTHORITY=NONE
REMEDIATION_APPROVAL_AUTHORITY=NONE
REMEDIATION_NETWORK_AUTHORITY=NONE
REMEDIATION_CREDENTIAL_AUTHORITY=NONE
REMEDIATION_PERSISTENCE_AUTHORITY=NONE
REMEDIATION_REAL_TOOL_EXECUTION_AUTHORITY=NONE
```

This document intentionally does not self-embed the remediation commit SHA/tree or its future CI run before those objects exist.

```text
REMEDIATION_COMMIT=VERIFY_AFTER_MATERIALIZATION
REMEDIATION_TREE=VERIFY_AFTER_MATERIALIZATION
REMEDIATION_PARENT=1deb0d83de122c77db9585d5815a8fb64d13d979
REMEDIATION_EXACT_CI_RUN=VERIFY_AFTER_TRIGGER
REMEDIATION_EXACT_CI_HEAD_SHA=MUST_EQUAL_REMEDIATION_COMMIT
REMEDIATION_EXACT_CI_STATUS=VERIFY
REMEDIATION_EXACT_CI_CONCLUSION=VERIFY
```

Successful remediation CI is necessary but does not itself close Phase 7E.

## 29. Post-Remediation Gate Posture

At remediation-candidate preparation time:

```text
PHASE_7D=CLOSED
PHASE_7E_R3_ARCHITECTURE=ACCEPTED
PHASE_7E_CORRECTED_RUNTIME_IMPLEMENTATION=UNCHANGED
PHASE_7E_CORRECTED_IMPLEMENTATION_CI=PASS
PHASE_7E_INDEPENDENT_IMPLEMENTATION_ACCEPTANCE=WITHHELD_PENDING_GAP_REMEDIATION
PHASE_7E_REMEDIATION_CANDIDATE=PREPARED
PHASE_7E_REMEDIATION_EXACT_CI=PENDING
PHASE_7E_CLOSURE=NOT_AUTHORIZED
PHASE_8_ADVANCEMENT_AUTHORITY=NONE
```

Only after the remediation commit passes exact-commit CI may the independent implementation acceptance review be repeated.

```text
NEXT_GATE=
PHASE_7E_DETERMINISTIC_TOOL_DISPATCH_OUTCOME_CONSISTENCY_EVIDENCE_
CORRECTED_IMPLEMENTATION_R1_
GAP_REMEDIATION_R1_
EXACT_COMMIT_CI_AND_REPEAT_INDEPENDENT_IMPLEMENTATION_ACCEPTANCE_REVIEW
```
