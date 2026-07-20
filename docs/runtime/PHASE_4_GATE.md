# Phase 4 — Deterministic Runtime Gate

## 1. Purpose

This gate evaluates whether the bounded Phase 4 deterministic runtime satisfies its approved implementation criteria.

It distinguishes:

- Local executable evidence
- Remote CI evidence
- Authority boundaries
- Residual risks
- Closure status

## 2. Gate Decision

```text
LOCAL IMPLEMENTATION GATE: PASSED
REMOTE CI GATE: PENDING
PHASE 4 CLOSURE: PENDING
NEXT PHASE: NOT AUTHORIZED
```

Phase 4 is not yet closed because the Phase 4 implementation commit and its exact remote CI evidence have not yet been recorded.

## 3. Authorized Scope

Phase 4 authorizes:

- Typed local runtime state
- Deterministic state transitions
- Step and retry budgets
- Explicit stop conditions
- Recommendation, abstention, denial, failure, and security-stop terminal states
- In-memory append-only checkpoints
- Optimistic concurrency
- Deterministic replay
- CT-07 runtime trace events
- Local synthetic typed outcomes
- Runtime-specific FastAPI integration
- Unit, contract, runtime, and integration tests
- Tutorial and gate evidence
- CI validation

## 4. Prohibited Scope

Phase 4 does not authorize:

- External model calls
- Model-provider credentials
- Enterprise retrieval
- Data ingestion
- Embeddings
- Vector databases
- Tool execution
- General shell access
- Human approval execution
- Infrastructure mutation
- Cloud deployment
- Production deployment
- Production credentials
- Autonomous remediation
- LLM authorization decisions
- Orchestrator authorization decisions

## 5. Artifact Inventory

### Runtime design and evidence

- `docs/runtime/PHASE_4_RUNTIME_STATE_AND_TRANSITION_DESIGN.md`
- `docs/runtime/PHASE_4_IMPLEMENTATION_AND_EVIDENCE.md`
- `docs/runtime/PHASE_4_GATE.md`

### Runtime implementation

- `src/incident_diagnostic_api/runtime/__init__.py`
- `src/incident_diagnostic_api/runtime/enums.py`
- `src/incident_diagnostic_api/runtime/models.py`
- `src/incident_diagnostic_api/runtime/errors.py`
- `src/incident_diagnostic_api/runtime/transitions.py`
- `src/incident_diagnostic_api/runtime/budgets.py`
- `src/incident_diagnostic_api/runtime/stops.py`
- `src/incident_diagnostic_api/runtime/checkpoints.py`
- `src/incident_diagnostic_api/runtime/replay.py`
- `src/incident_diagnostic_api/runtime/traces.py`
- `src/incident_diagnostic_api/runtime/engine.py`

### Runtime API

- `src/incident_diagnostic_api/api/runtime_models.py`
- `src/incident_diagnostic_api/api/runtime_errors.py`
- `src/incident_diagnostic_api/api/runtime.py`
- `src/incident_diagnostic_api/api/app.py`

### Contract extension

- `src/incident_diagnostic_api/contracts/enums.py`

### Runtime tests

- `tests/runtime/__init__.py`
- `tests/runtime/test_state_contract.py`
- `tests/runtime/test_transitions.py`
- `tests/runtime/test_budgets.py`
- `tests/runtime/test_stops.py`
- `tests/runtime/test_checkpoints.py`
- `tests/runtime/test_replay.py`
- `tests/runtime/test_traces.py`
- `tests/runtime/test_engine.py`

### Integration tests

- `tests/integration/test_runtime_api.py`
- `tests/integration/test_service_status.py`

### CI

- `.github/workflows/phase4-ci.yml`

The superseded ongoing workflow path is removed:

```text
.github/workflows/phase3-ci.yml
```

Historical Phase 3 CI evidence remains recorded in the Phase 3 documentation and Git history.

## 6. Runtime Inventory Gate

| Item | Expected | Observed | Status |
|---|---:|---:|---|
| Runtime states | 13 | 13 | Passed |
| Initial states | 1 | 1 | Passed |
| Active states | 7 | 7 | Passed |
| Terminal states | 5 | 5 | Passed |
| State classifications | 13 | 13 | Passed |
| Transition commands | 27 | 27 | Passed |
| Authoritative transitions | 25 | 25 | Passed |
| Runtime reason codes | 33 | 33 | Passed |
| CT-07 runtime event names | 3 | 3 | Passed |

## 7. State and Transition Gate

| Requirement | Evidence | Status |
|---|---|---|
| Every legal transition tested | Parameterized transition-table tests | Passed |
| Representative illegal transitions rejected | Negative transition tests | Passed |
| Invalid transition does not mutate state | Engine and API assertions | Passed |
| Terminal states cannot resume | Terminal-state transition tests | Passed |
| State classifications complete | All 13 states classified | Passed |
| State snapshots immutable | Pydantic frozen-contract tests | Passed |
| JSON reason-code round trip preserved | Runtime normalization evidence | Passed |

## 8. Budget and Stop Gate

Default limits:

```text
Maximum steps: 16
Maximum total retries: 2
Maximum stage retries: 1
```

| Requirement | Evidence | Status |
|---|---|---|
| Step budget enforced | Budget and engine tests | Passed |
| Total retry budget enforced | Budget, stop, and engine tests | Passed |
| Stage retry budget enforced | Budget and stop tests | Passed |
| Only transient failures retry | Typed retry-contract tests | Passed |
| Authorization expiry stops coordination | Stop-condition tests | Passed |
| Terminal workflow remains stopped | Stop-condition tests | Passed |
| Stop occurs before mutation | Engine checkpoint assertions | Passed |

## 9. Checkpoint Gate

| Requirement | Evidence | Status |
|---|---|---|
| Genesis checkpoint recorded | Engine-start tests | Passed |
| Accepted transitions checkpointed | Engine/checkpoint tests | Passed |
| Accepted retries checkpointed | Engine/retry tests | Passed |
| Checkpoint sequence continuous | Checkpoint tests | Passed |
| State version aligned | Contract validation | Passed |
| State hash recorded | Hash tests | Passed |
| Previous hash linked | Chain tests | Passed |
| History append-only | Store tests | Passed |
| Missing workflow controlled | Store and API tests | Passed |

Phase 4 checkpoints remain intentionally in memory.

No durable persistence claim is made.

## 10. Concurrency Gate

| Requirement | Evidence | Status |
|---|---|---|
| Expected version required | Typed API and engine signatures | Passed |
| Stale version rejected | Engine and API tests | Passed |
| Conflict returns controlled error | HTTP 409 integration test | Passed |
| Version conflict does not mutate | State/checkpoint assertions | Passed |
| Local engine coordination locked | Application-scoped engine implementation | Passed |

This is local optimistic concurrency.

Distributed concurrency is not claimed.

## 11. Replay Gate

| Requirement | Evidence | Status |
|---|---|---|
| Checkpoint sequence verified | Replay tests | Passed |
| Workflow lineage verified | Replay tests | Passed |
| State hashes recalculated | Replay tests | Passed |
| Checkpoint hashes recalculated | Replay tests | Passed |
| Previous-hash linkage verified | Replay tests | Passed |
| Transitions reconstructed | Replay tests | Passed |
| Reconstructed transitions allowlisted | Replay tests | Passed |
| Final state reproduced | Replay and engine tests | Passed |
| Divergence fails closed | Replay-integrity tests | Passed |

Replay verifies recorded local state. It does not repeat side effects.

## 12. Trace Gate

Phase 4 CT-07 event names:

```text
runtime_transition_applied
runtime_retry_scheduled
runtime_stop_enforced
```

| Requirement | Evidence | Status |
|---|---|---|
| Transition trace generated | Runtime trace tests | Passed |
| Retry trace generated | Runtime trace tests | Passed |
| Stop trace generated | Runtime trace tests | Passed |
| Request identifier preserved | Trace assertions | Passed |
| Trace identifier preserved | Trace assertions | Passed |
| Policy lineage preserved when supplied | Engine and trace tests | Passed |
| Retry attempt bounded | CT-07 and budget alignment | Passed |
| Attributes allowlisted | CT-07 contract tests | Passed |

The new event names provide observability vocabulary only.

## 13. Runtime API Gate

The runtime service exposes:

```text
POST /v1/runtime/workflows
GET  /v1/runtime/workflows/{workflow_id}
POST /v1/runtime/workflows/{workflow_id}/transitions
POST /v1/runtime/workflows/{workflow_id}/retries
GET  /v1/runtime/workflows/{workflow_id}/checkpoints
GET  /v1/runtime/workflows/{workflow_id}/replay
```

| Requirement | Evidence | Status |
|---|---|---|
| Workflow creation succeeds | Integration test | Passed |
| Current state can be read | Integration test | Passed |
| Legal transition succeeds | Integration test | Passed |
| Typed transient retry succeeds | Integration test | Passed |
| Checkpoint history available | Integration test | Passed |
| Replay evidence available | Integration test | Passed |
| Missing workflow controlled | HTTP 404 test | Passed |
| Stale version controlled | HTTP 409 test | Passed |
| Invalid transition controlled | HTTP 409 test | Passed |
| Correlation ID returned | Integration test | Passed |

## 14. Service-Isolation Gate

| Service | Authorized non-health routes |
|---|---|
| Gateway | CT-01 and CT-05 validation |
| Runtime | Six deterministic runtime routes |
| Evidence | None |

Evidence:

- Only the runtime application owns a `DeterministicRuntimeEngine`.
- Gateway runtime-route requests return `404`.
- Evidence runtime-route requests return `404`.
- Runtime routes are absent from gateway OpenAPI.
- Runtime routes are absent from evidence OpenAPI.

Status:

```text
PASSED
```

## 15. Local Quality Evidence

```text
Ruff lint: passed
Ruff format check: passed
Strict mypy: passed
Pytest: 686 passed
Line coverage: 96.95%
Branch coverage: 94.33%
```

Test-function inventory:

```text
Unit: 26
Contract: 99
Integration: 39
Runtime: 124
```

Collected test cases exceed function counts because parameterized tests produce multiple cases.

## 16. CI Gate

Workflow:

```text
.github/workflows/phase4-ci.yml
```

Required jobs:

- Python quality and contract tests
- Local container build and health verification

Required quality gates:

- Hash-locked dependency installation
- Dependency integrity
- Ruff lint
- Ruff formatting
- Strict mypy
- Pytest with branch coverage
- Coverage artifact upload

Required container gates:

- Compose validation
- Image build
- Isolated startup
- No host ports
- Internal network isolation
- Runtime restrictions
- Health checks
- Readiness checks
- Status and logs
- Cleanup

Current CI decision:

```text
PENDING EXECUTION AGAINST THE PHASE 4 IMPLEMENTATION COMMIT
```

No CI run identifier or commit SHA is claimed yet.

## 17. Authority Gate

All runtime service capability flags are:

```text
external_model_enabled: false
enterprise_retrieval_enabled: false
tool_execution_enabled: false
infrastructure_mutation_enabled: false
cloud_deployment_enabled: false
production_deployment_enabled: false
```

Source inspection found no prohibited provider, retrieval, tool, shell, infrastructure, or deployment integration in the runtime boundary.

Status:

```text
PASSED
```

## 18. Original Phase 4 Gate Evaluation

| Original requirement | Decision |
|---|---|
| Every legal transition has a test | Passed |
| Illegal transitions fail deterministically | Passed |
| Invalid transitions do not mutate state | Passed |
| Terminal states cannot resume | Passed |
| Step budgets enforced | Passed |
| Retry budgets enforced | Passed |
| Checkpoints follow accepted transitions | Passed |
| Recorded workflows replay deterministically | Passed |
| Version conflicts fail without mutation | Passed |
| Trace evidence preserves correlation | Passed |
| Recommendation remains `not_executed` | Passed |
| Runtime cannot authorize itself | Passed |
| Tests need no provider credentials | Passed |
| External models disabled | Passed |
| Enterprise retrieval disabled | Passed |
| Tool execution disabled | Passed |
| Infrastructure mutation disabled | Passed |
| Cloud and production deployment disabled | Passed |
| Tutorial matches behavior | Passed locally |
| Exact remote CI evidence recorded | Pending |

## 19. Residual Risks

- Checkpoint state is process-local.
- Runtime history is lost when the process restarts.
- No PostgreSQL or Redis persistence exists.
- No distributed lock exists.
- No multi-instance coordination exists.
- No enterprise identity integration exists.
- No external policy service is connected.
- No provider integration exists.
- No enterprise retrieval exists.
- No tool registry or execution exists.
- No human approval execution exists.
- No cloud or production deployment exists.
- Phase 4 remote CI evidence is pending.

## 20. Required Evidence Before Closure

Phase 4 closure requires:

1. Final local quality checks pass.
2. Documentation structure checks pass.
3. Authorized-scope review passes.
4. Phase 4 files are staged intentionally.
5. The Phase 4 implementation commit is pushed.
6. The `Phase 4 CI` workflow succeeds.
7. The workflow head SHA equals the implementation commit.
8. The CI run ID and URL are recorded.
9. Closure documentation is synchronized.
10. Closure CI succeeds on the closure commit.

## 21. Next Authorized Work

```text
NONE
```

No later phase is authorized by this gate.

A later phase may begin only after:

- Phase 4 closure evidence is recorded.
- The roadmap is updated.
- The next scope is explicitly authorized.

## 22. Prohibited Maturity Claims

Do not describe this phase as:

- Ready for production use
- Production-deployed
- Enterprise-integrated
- Provider-integrated
- Retrieval-enabled
- Tool-enabled
- Autonomous
- Durable
- Distributed
- Certified against SOC 2
- Regulator-certified

The supported statement is:

```text
The locally validated Phase 4 implementation provides a typed,
deterministic runtime coordination foundation. Remote CI closure
evidence remains pending.
```

## 23. Final Maturity Statement

```text
PHASE 4 LOCAL GATE: PASSED
PHASE 4 REMOTE CI GATE: PENDING
PHASE 4 CLOSURE: PENDING
NEXT PHASE: NOT AUTHORIZED
```
