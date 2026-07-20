# Phase 4 — Deterministic Runtime Implementation and Evidence

## 1. Purpose

Phase 4 turns the Phase 3 typed service foundation into a bounded local runtime coordinator.

The runtime now manages:

- Immutable workflow state
- Allowlisted transitions
- Step and retry budgets
- Explicit stop conditions
- Append-only checkpoints
- Optimistic concurrency
- Deterministic replay
- CT-07 runtime trace evidence
- Local FastAPI runtime endpoints

It does not call a model, retrieve enterprise data, invoke tools, execute shell commands, mutate infrastructure, deploy to cloud environments, or access production systems.

## 2. Current Evidence Status

```text
LOCAL IMPLEMENTATION VALIDATED
REMOTE PHASE 4 CI CLOSURE PENDING
```

Local evidence currently shows:

- Ruff linting passes.
- Ruff formatting passes.
- Strict mypy checking passes.
- 686 pytest cases pass.
- Line coverage is 96.95%.
- Branch coverage is 94.33%.
- All prohibited capability flags remain disabled.

Phase 4 closure must remain pending until the Phase 4 CI workflow succeeds against the exact closure commit.

## 3. Delivery-Lifecycle Position

The repository now demonstrates this engineering progression:

```text
Phase 1 — Discovery
    Identify the workflow, stakeholders, data boundaries, risks,
    assumptions, authority limits, and measurable outcomes.

Phase 2 — Thin Vertical Slice
    Reduce the problem to one valuable recommendation-only path
    with written contracts and acceptance criteria.

Phase 3 — Prototype Foundation
    Convert the design into typed FastAPI services, Pydantic
    contracts, deterministic validation, tests, packaging, and CI.

Phase 4 — Deterministic Runtime
    Make workflow state, transitions, budgets, stops, checkpoints,
    replay, concurrency, and runtime evidence explicit.
```

Phase 4 does not replace discovery or the vertical slice. It operationalizes the boundaries derived from them.

## 4. Traceability from Discovery to Runtime

| Earlier evidence | Runtime consequence |
|---|---|
| Recommendation-only authority | No remediation-execution state exists |
| Human review required | Recommendation terminates as `not_executed` |
| Deterministic authorization boundary | Runtime stores policy lineage but cannot create policy decisions |
| Evidence sufficiency requirement | Evidence assessment has explicit states and abstention paths |
| Controlled failure requirements | Denial, failure, abstention, and security stop are terminal |
| Correlation requirements | Workflow, request, trace, checkpoint, and event identifiers remain linked |
| No external credentials | All tests run with local synthetic evidence |
| No production mutation | No tool, shell, infrastructure, cloud, or production route exists |

This is the main architectural lesson: runtime behavior must be derived from approved workflow and authority decisions, not invented by an orchestrator.

## 5. What the Learner Should Understand

After completing this phase, the learner should be able to explain:

1. Why orchestration state must be explicit.
2. Why legal transitions belong in code rather than prompts.
3. Why an orchestrator must not authorize itself.
4. How optimistic concurrency prevents stale writers.
5. How step and retry budgets bound execution.
6. How stop conditions differ from normal terminal transitions.
7. Why checkpoints should be append-only.
8. How deterministic replay supports audit and debugging.
9. How trace events preserve lifecycle evidence.
10. How FastAPI exposes runtime coordination without expanding runtime authority.

## 6. Why Explicit Runtime State Matters

An agent workflow is not merely a sequence of function calls.

Without explicit state, it becomes difficult to answer:

- What stage is the workflow in?
- Which transition was accepted?
- Which transition was rejected?
- How many retries occurred?
- Was policy lineage present?
- Did a stale writer overwrite newer state?
- Why did processing stop?
- Can the workflow history be reconstructed?
- Was any recommendation executed?

The `RuntimeStateRecord` answers these questions with one immutable snapshot.

## 7. Runtime Architecture

```text
FastAPI Runtime Route
        |
        v
Typed API Request Contract
        |
        v
DeterministicRuntimeEngine
        |
        +--> Transition Table
        +--> Step and Retry Budgets
        +--> Stop Evaluator
        +--> CT-07 Trace Builder
        |
        v
Append-Only In-Memory Checkpoint Store
        |
        v
Deterministic Replay Verification
```

The runtime engine coordinates these components. It is not an authorization engine, model provider, retrieval service, or tool executor.

## 8. Runtime State Inventory

| Type | State | Meaning |
|---|---|---|
| Initial | `RECEIVED` | A bounded local workflow record exists |
| Active | `REQUEST_VALIDATING` | CT-01 validation outcome is expected |
| Active | `IDENTITY_VALIDATING` | CT-02 identity outcome is expected |
| Active | `POLICY_EVALUATING` | CT-03 authorization outcome is expected |
| Active | `EVIDENCE_PENDING` | A future evidence outcome is expected |
| Active | `EVIDENCE_ASSESSING` | Evidence sufficiency is being assessed |
| Active | `GENERATION_PENDING` | A future typed generation outcome is expected |
| Active | `RESPONSE_VALIDATING` | CT-05 validation outcome is expected |
| Terminal | `COMPLETED_RECOMMENDATION` | A validated recommendation awaits human review |
| Terminal | `COMPLETED_ABSTENTION` | Evidence or confidence was insufficient |
| Terminal | `COMPLETED_DENIAL` | Identity or deterministic policy denied processing |
| Terminal | `COMPLETED_FAILURE` | A controlled failure ended processing |
| Terminal | `COMPLETED_SECURITY_STOP` | A security containment condition ended processing |

Inventory evidence:

```text
Runtime states: 13
Initial states: 1
Active states: 7
Terminal states: 5
State classifications: 13
```

## 9. State-Machine Rules

The runtime contains:

```text
Transition commands: 27
Authoritative normal transitions: 25
```

A transition is accepted only when the pair below exists in the authoritative table:

```text
(current_state, command)
```

The table returns a typed transition definition containing:

- Source state
- Command
- Target state
- Reason code

If the pair is absent, the runtime raises a controlled `InvalidTransitionError`.

If the current state is terminal, the runtime raises a controlled `TerminalStateTransitionError`.

Neither failure mutates state.

## 10. Runtime Invariants

The executable contracts enforce these invariants:

- State snapshots are immutable.
- `updated_at` cannot precede `created_at`.
- Retry count cannot exceed step count.
- Per-stage retry counts must sum to the total retry count.
- Duplicate per-stage retry counters are prohibited.
- Authorization expiry requires policy-decision lineage.
- The initial state begins at version zero.
- Initial step and retry counters are zero.
- Terminal states cannot resume.
- Every accepted state-changing operation increments the version.
- Stale expected versions fail before mutation.
- Every accepted operation produces checkpoint evidence.
- Replay must reproduce the recorded final state.
- Known runtime reason codes survive JSON transport as typed enums.

## 11. Step Budget

The default step budget is:

```text
Maximum steps: 16
```

Before an accepted state-changing operation, the engine verifies that the workflow has remaining step capacity.

When the budget is exhausted:

- No new checkpoint is appended.
- State does not change.
- A controlled budget error is raised.
- A runtime stop trace can be produced.
- The runtime does not invent additional authority to continue.

## 12. Retry Budget

The default retry limits are:

```text
Maximum total retries: 2
Maximum retries per stage: 1
Maximum CT-07 retry-attempt capacity: 5
```

A retry requires typed evidence:

- Failure classification must be `TRANSIENT`.
- A controlled failure reason code must be supplied.
- Total retry capacity must remain.
- Per-stage retry capacity must remain.
- The state must remain eligible for continuation.

Permanent, security, policy, validation, and terminal failures cannot be relabeled as transient by the orchestrator.

## 13. Stop Conditions

The stop evaluator distinguishes continuation from enforced termination.

Representative stop conditions include:

- Workflow already terminal
- Step budget exhausted
- Retry budget exhausted
- Stage retry budget exhausted
- Authorization expired
- Security containment required

A stop decision contains:

- Stop condition
- Disposition
- Controlled reason code
- Non-sensitive message

Stop evaluation is deterministic and occurs before mutation.

## 14. Policy Authority Boundary

The runtime may preserve:

- `policy_decision_id`
- `authorization_expires_at`

The runtime cannot:

- Produce an allow decision
- Override a deny decision
- Extend authorization expiry
- Infer missing authorization
- Treat model output as policy
- Continue after expired authorization

This implements the separation:

```text
Policy decides.
Runtime coordinates.
Model reasoning, when later authorized, proposes.
```

## 15. Checkpoint Model

Every accepted operation creates a complete immutable checkpoint containing:

- Checkpoint identifier
- Workflow identifier
- Sequence number
- State version
- State hash
- Previous checkpoint hash
- Checkpoint hash
- Creation timestamp
- Complete runtime snapshot

The first checkpoint is the genesis checkpoint.

Genesis rules:

- Sequence is zero.
- State version is zero.
- No previous checkpoint hash exists.

Later checkpoints require a previous checkpoint hash.

## 16. Why Append-Only Checkpoints Matter

Append-only history provides:

- Change evidence
- Concurrency protection
- Replay input
- Incident-debugging context
- Audit lineage
- Tamper-evident hash linkage

Phase 4 uses an in-memory store intentionally. PostgreSQL, Redis, distributed locking, and durable recovery are not claimed by this phase.

## 17. Optimistic Concurrency

Every state-changing API request supplies:

```text
expected_state_version
```

The engine compares it with the latest recorded version.

If they differ:

```text
HTTP 409
VERSION_CONFLICT
No state mutation
No checkpoint append
```

This prevents a stale client from overwriting a newer workflow state.

## 18. Deterministic Replay

Replay performs these checks:

1. Load checkpoint history.
2. Verify sequence continuity.
3. Verify workflow lineage.
4. Recalculate state hashes.
5. Recalculate checkpoint hashes.
6. Verify previous-hash linkage.
7. Reconstruct transitions.
8. Confirm every reconstructed transition is authoritative.
9. Confirm the final replayed state matches the final checkpoint.

Successful replay produces:

- Verified status
- `REPLAY_VERIFIED`
- Checkpoint count
- Reconstructed steps
- Final state
- Final state version
- Final checkpoint hash

Replay verifies recorded behavior. It does not rerun providers, retrieval, tools, or side effects.

## 19. Runtime Trace Evidence

Phase 4 adds three allowlisted CT-07 event names:

```text
runtime_transition_applied
runtime_retry_scheduled
runtime_stop_enforced
```

These names expand observability vocabulary only.

They do not grant:

- Provider authority
- Retrieval authority
- Tool authority
- Policy authority
- Infrastructure authority
- Production authority

Runtime traces preserve:

- Event identifier
- Request identifier
- Trace identifier
- Lifecycle stage
- Outcome
- Policy lineage when supplied
- Input and output references
- Reason codes
- Retry attempt
- Timestamp
- Allowlisted attributes

## 20. Deterministic Runtime Engine

`DeterministicRuntimeEngine` coordinates:

- Workflow creation
- Current-state reads
- Transition application
- Retry scheduling
- Checkpoint history
- Replay verification
- Budget enforcement
- Stop enforcement
- Trace generation

The engine uses:

- Immutable Pydantic contracts
- An authoritative transition table
- An application-scoped in-memory checkpoint store
- An `RLock` for local thread coordination
- Optimistic state versions

It exposes no model, retrieval, tool, shell, infrastructure, cloud, or production method.

## 21. FastAPI Runtime Boundary

The runtime service exposes six Phase 4 paths:

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/runtime/workflows` | Create genesis state and evidence |
| `GET` | `/v1/runtime/workflows/{workflow_id}` | Read the latest immutable state |
| `POST` | `/v1/runtime/workflows/{workflow_id}/transitions` | Apply one allowlisted transition |
| `POST` | `/v1/runtime/workflows/{workflow_id}/retries` | Schedule one bounded transient retry |
| `GET` | `/v1/runtime/workflows/{workflow_id}/checkpoints` | Read append-only history |
| `GET` | `/v1/runtime/workflows/{workflow_id}/replay` | Replay and verify history |

The runtime service also retains:

- `/health`
- `/ready`

## 22. Service Isolation

The service route inventory is:

```text
Gateway:
  /health
  /ready
  /v1/contracts/diagnostic-request/validate
  /v1/contracts/diagnostic-response/validate

Runtime:
  /health
  /ready
  six /v1/runtime routes

Evidence:
  /health
  /ready
```

Only the runtime application receives an application-scoped `DeterministicRuntimeEngine`.

The gateway and evidence applications do not receive runtime state or runtime routes.

## 23. Controlled HTTP Failures

The runtime API returns allowlisted errors for:

- Missing workflow
- Version conflict
- Invalid transition
- Enforced stop
- Budget exhaustion
- Replay-integrity failure
- Controlled internal runtime failure

Representative behavior:

| Condition | HTTP status | Error code |
|---|---:|---|
| Missing workflow | `404` | `WORKFLOW_NOT_FOUND` |
| Stale state version | `409` | `VERSION_CONFLICT` |
| Illegal transition | `409` | `INVALID_TRANSITION` |
| Stop enforced | `409` | `EXECUTION_STOPPED` |
| Budget exhausted | `409` | `BUDGET_EXHAUSTED` |
| Replay divergence | `500` | `REPLAY_INTEGRITY_FAILURE` |

Error messages are controlled and non-sensitive.

## 24. Local Tutorial

Start the runtime service directly:

```bash
python -m uvicorn \
  incident_diagnostic_api.services.runtime:app \
  --host 127.0.0.1 \
  --port 8001
```

In another terminal, verify health:

```bash
curl --fail \
  http://127.0.0.1:8001/health
```

Verify readiness:

```bash
curl --fail \
  http://127.0.0.1:8001/ready
```

Inspect OpenAPI:

```text
http://127.0.0.1:8001/docs
```

This direct local tutorial does not require Docker, a provider credential, enterprise data, or production access.

## 25. Example Workflow Creation

Example request:

```bash
curl \
  --request POST \
  --header 'Content-Type: application/json' \
  --header 'X-Correlation-ID: tutorial-runtime-101' \
  --data '{
    "record": {
      "workflow_id": "workflow-tutorial-101",
      "request_id": "request-tutorial-101",
      "trace_id": "trace-tutorial-101",
      "state": "received",
      "state_version": 0,
      "step_count": 0,
      "retry_count": 0,
      "stage_retry_counts": [],
      "reason_codes": ["RUNTIME_CREATED"],
      "created_at": "2026-07-19T18:30:00Z",
      "updated_at": "2026-07-19T18:30:00Z",
      "policy_decision_id": null,
      "authorization_expires_at": null,
      "request_reference": null,
      "identity_reference": null,
      "evidence_reference": null,
      "response_reference": null,
      "error_reference": null
    },
    "event_id": "event-tutorial-0",
    "timestamp": "2026-07-19T18:30:00Z"
  }' \
  http://127.0.0.1:8001/v1/runtime/workflows
```

The response contains:

- Genesis snapshot
- Genesis checkpoint
- CT-07 `request_received` trace event

## 26. Example Transition

```bash
curl \
  --request POST \
  --header 'Content-Type: application/json' \
  --data '{
    "expected_state_version": 0,
    "command": "begin_request_validation",
    "event_id": "event-tutorial-1",
    "timestamp": "2026-07-19T18:30:01Z",
    "context": null,
    "duration_ms": 1.2
  }' \
  http://127.0.0.1:8001/v1/runtime/workflows/workflow-tutorial-101/transitions
```

Expected state:

```text
request_validating
```

Expected state version:

```text
1
```

Expected CT-07 event:

```text
runtime_transition_applied
```

## 27. Example Read and Replay

Read current state:

```bash
curl --fail \
  http://127.0.0.1:8001/v1/runtime/workflows/workflow-tutorial-101
```

Read checkpoint history:

```bash
curl --fail \
  http://127.0.0.1:8001/v1/runtime/workflows/workflow-tutorial-101/checkpoints
```

Replay the workflow:

```bash
curl --fail \
  http://127.0.0.1:8001/v1/runtime/workflows/workflow-tutorial-101/replay
```

A verified replay proves that recorded local state evolution matches the authoritative transition table and hash chain.

## 28. Test Strategy

Phase 4 uses four test layers:

| Layer | Purpose |
|---|---|
| Unit | Configuration, correlation, defensive branches, primitive behavior |
| Contract | CT-01 through CT-07 invariants |
| Runtime | States, transitions, budgets, stops, checkpoints, replay, traces, engine |
| Integration | FastAPI services, runtime routes, isolation, controlled failures |

Current test evidence:

```text
Unit test functions: 26
Contract test functions: 99
Integration test functions: 39
Runtime test functions: 124
Collected pytest cases: 686
```

Parameterized tests explain why collected cases exceed function counts.

## 29. Quality Evidence

Current local evidence:

```text
Ruff lint: passed
Ruff format check: passed
Strict mypy: passed
Pytest: 686 passed
Line coverage: 96.95%
Branch coverage: 94.33%
Dependency check: previously validated and retained
```

Coverage is evidence of exercised code paths. It is not proof of production readiness, security certification, or operational resilience.

## 30. CI Evidence

The ongoing repository workflow is:

```text
.github/workflows/phase4-ci.yml
```

It retains:

- Hash-locked development dependency installation
- Dependency integrity checking
- Ruff linting
- Ruff formatting verification
- Strict mypy checking
- Pytest with branch coverage
- Coverage artifact upload
- Docker Compose validation
- Container build
- Isolated service startup
- No-host-port verification
- Internal-network verification
- Container runtime restriction checks
- Health and readiness checks
- Logs and cleanup

The coverage artifact is named:

```text
phase4-coverage
```

Remote CI evidence remains pending until this phase is committed and the exact commit succeeds.

## 31. Prototype Usefulness

This runtime prototype is useful because it allows a client and engineering team to evaluate:

- Whether workflow stages are understandable
- Whether the transition model matches the business process
- Whether failure behavior is predictable
- Whether retries are appropriately bounded
- Whether policy authority stays external
- Whether evidence is sufficient for debugging
- Whether stale concurrent writes fail safely
- Whether workflow history can be replayed
- Whether service boundaries are correctly isolated

It reduces risk before adding costly or sensitive integrations.

## 32. What the Prototype Does Not Prove

This phase does not prove:

- Model quality
- Retrieval quality
- Enterprise authorization integration
- Tool safety
- Human approval execution
- Durable database recovery
- Distributed concurrency
- Multi-instance coordination
- Cloud scalability
- Production security
- Production reliability
- Regulatory compliance
- Autonomous remediation

Those require later explicitly authorized phases and separate evidence.

## 33. Interview Explanation — 60 Seconds

I implemented the agent runtime as a deterministic state machine rather than allowing an LLM or framework to control workflow behavior implicitly. The runtime has thirteen typed states, twenty-five authoritative transitions, immutable Pydantic snapshots, step and retry budgets, explicit stop conditions, optimistic concurrency, append-only hash-linked checkpoints, deterministic replay, and CT-07 trace events. I then exposed only those coordination capabilities through a runtime-specific FastAPI service. The gateway and evidence services do not receive runtime authority. Most importantly, the runtime preserves policy-decision lineage but cannot authorize itself, and it has no model, retrieval, tool, shell, infrastructure, cloud, or production integration. That gives the team a testable orchestration foundation before higher-risk capabilities are introduced.

## 34. Interview Explanation — 30 Seconds

I built a bounded deterministic runtime with typed states, allowlisted transitions, budgets, stop conditions, optimistic concurrency, append-only checkpoints, replay, and trace evidence. FastAPI exposes those capabilities only on the runtime service. The runtime can preserve an external policy decision, but it cannot create or override authorization, call models, retrieve enterprise data, execute tools, or mutate production systems.

## 35. Phase 4 Gate Mapping

| Gate requirement | Current local evidence |
|---|---|
| Every legal transition tested | Authoritative transition tests pass |
| Illegal transitions fail deterministically | Negative transition tests pass |
| Invalid transitions do not mutate state | Engine and API tests pass |
| Terminal states cannot resume | Terminal-transition tests pass |
| Step budgets enforced | Budget tests pass |
| Retry budgets enforced | Retry and stop tests pass |
| Checkpoint after accepted transition | Engine/checkpoint tests pass |
| Deterministic replay | Replay and engine tests pass |
| Version conflict without mutation | Checkpoint, engine, and API tests pass |
| Trace correlation preserved | CT-07 runtime trace tests pass |
| Recommendation remains not executed | CT-05 authority invariant remains enforced |
| Runtime cannot authorize itself | Policy lineage is input-only |
| No provider credentials | Tests use local synthetic inputs |
| Prohibited capabilities disabled | All six capability flags are false |
| Tutorial matches executable behavior | Commands, routes, counts, and limits are evidence-derived |

## 36. Residual Risks

Current residual risks include:

- Checkpoints are process-local and in memory.
- Restarting the service loses local workflow history.
- The engine is not a distributed coordinator.
- No durable database transaction protects checkpoints.
- No enterprise identity or policy service is connected.
- No provider or retrieval dependency exists.
- No approved tool registry exists.
- No human approval execution exists.
- Remote Phase 4 CI closure evidence is pending.

These limitations are intentional and must remain visible.

## 37. Prohibited Claims

Do not claim that Phase 4 provides:

- A production agent
- Live enterprise orchestration
- Model-provider integration
- Enterprise retrieval
- RAG
- Tool execution
- Shell execution
- Autonomous remediation
- Infrastructure mutation
- Cloud deployment
- Production deployment
- Distributed durability
- Regulatory certification
- SOC 2 compliance

The correct claim is:

```text
Phase 4 provides a typed, deterministic, locally tested runtime
coordination foundation with explicit authority boundaries.
```

## 38. Exit Posture

Current posture:

```text
LOCAL PHASE 4 IMPLEMENTATION: VALIDATED
REMOTE PHASE 4 CI: PENDING
PHASE 4 CLOSURE: NOT YET RECORDED
NEXT PHASE: NOT YET AUTHORIZED
```

Phase 4 can close only after:

1. The implementation and gate documents pass structural validation.
2. The exact authorized files are reviewed and staged.
3. The Phase 4 commit is pushed.
4. The Phase 4 CI workflow succeeds against that exact commit.
5. The CI run identifier and commit SHA are recorded.
6. Closure documentation is committed and its CI run succeeds.
