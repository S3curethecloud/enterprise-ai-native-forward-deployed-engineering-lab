# Claim, Evidence, and Authority Rules

## Purpose

This document prevents the tutorial, repository, automated tests, documentation, and interview materials from claiming more maturity or authority than the available evidence supports.

It governs:

- Capability status
- Implementation claims
- Test evidence
- Deployment claims
- Production-readiness claims
- Runtime authority
- Model authority
- Tool authority
- Human approval
- Phase completion
- Interview explanations

## Governing Principle

A capability is represented by its strongest verified evidence—not by its planned architecture, filename, directory, README description, or future roadmap position.

The repository must never convert:

- Planned into implemented
- Implemented into tested
- Tested into evidence-recorded
- Evidence-recorded into deployed
- Deployed into production-ready
- Production-ready into externally adopted
- Simulated into live
- Recommendation into authorization
- Model output into authoritative fact
- Portfolio work into client delivery

## Evidence Maturity Model

| Level | Name | Required proof | Permitted statement |
|---:|---|---|---|
| 0 | Planned | Roadmap or design note | “This capability is planned.” |
| 1 | Documented | Reviewed architecture or contract | “This capability is documented.” |
| 2 | Implemented | Working code or configuration | “This capability is implemented locally.” |
| 3 | Tested | Passing relevant tests | “This behavior passed the defined tests.” |
| 4 | Evidence-recorded | Preserved test result and interpretation | “This behavior is evidence-recorded.” |
| 5 | Deployed | Verified accessible runtime | “This capability is deployed in the named environment.” |
| 6 | Production-ready | Readiness gate and operational evidence | “This version passed the defined production-readiness gate.” |
| 7 | Staged production | Controlled approved rollout | “This capability is enabled for the named rollout stage.” |
| 8 | External customer production | Explicit customer and operating evidence | “This capability operates in the verified customer context.” |

A higher level requires every relevant lower-level requirement.

## Status Is Capability-Specific

A system may be deployed while an individual capability remains planned.

Example:

- API service: deployed
- Retrieval: tested
- Approval workflow: documented
- Production remediation: prohibited

The repository must not apply the highest system-level status to every component.

## Protected Terms

The following terms require explicit evidence.

### Implemented

Requires working code or configuration for the named capability.

### Tested

Requires identified tests, execution output, and an expected result.

### Evidence-recorded

Requires preserved evidence that can be reviewed after the test session.

### Deployed

Requires a named environment, version, endpoint or runtime identifier, and verification.

### Production-ready

Requires completion of the Phase 14 readiness gate. A successful deployment alone is insufficient.

### Production

Requires a named operating context, ownership, support model, monitoring, incident handling, rollback, and approved release stage.

### External customer production

Requires explicit evidence of customer use. Never infer it from a public endpoint or portfolio deployment.

### Autonomous

Requires defined authority, action scope, safeguards, operational evidence, and approved rollout stage. Do not use it for recommendation-only workflows.

### Secure

Use only with the named controls and tests. Prefer:

- “Identity-aware”
- “Policy-controlled”
- “Permission-filtered”
- “Least-privilege”
- “Tested against the defined security cases”

### Enterprise-grade

Avoid as a standalone claim. Name the actual properties:

- Typed contracts
- Identity boundaries
- Policy enforcement
- Evaluation
- Observability
- Reliability
- Runbooks
- Rollback
- Evidence

## Source-of-Truth Order

When sources disagree, use this order:

1. Current executable behavior
2. Current automated or manual test results
3. Evidence record from the current version
4. Versioned contracts and policy
5. Architecture decision records
6. Phase documentation
7. README summary
8. Roadmap
9. Interview narrative

An interview statement must never override repository evidence.

## Claim Record

Every material capability must eventually have a claim record.

Minimum schema:

```yaml
claim_id: CLAIM-EXAMPLE-001
capability: permission-aware-retrieval
version: 0.1.0
maturity_level: 3
status: tested
environment: local
implementation:
  files:
    - services/retrieval/example.py
validation:
  tests:
    - tests/retrieval/test_permissions.py
evidence:
  records:
    - evidence/retrieval/example-result.json
limitations:
  - synthetic data only
  - no external identity provider
prohibited_claims:
  - external customer production
  - regulated certification
approved_by: null
recorded_at: null
```

The example is a future contract. It does not indicate that the listed files or capability currently exist.

## Evidence Record Requirements

Each evidence record must identify:

- Evidence ID
- Capability
- Phase
- Version or commit
- Environment
- Preconditions
- Command or procedure
- Expected result
- Actual result
- Pass, fail, or blocked status
- Interpretation
- Known limitations
- Timestamp
- Evidence producer
- Relevant artifact paths

## Evidence Must Include Failure Behavior

Success-only evidence is incomplete for:

- Identity
- Authorization
- Retrieval permissions
- Tool validation
- Idempotency
- Approval
- Policy
- Retry behavior
- Cross-tenant isolation
- Rollback
- Release gates

For these capabilities, evidence must include at least one approved path and one denied or failure path.

## Evidence Integrity Rules

Evidence must not be:

- Fabricated
- Backdated
- Silently edited after review
- Generated from a different version without disclosure
- Presented without limitations
- Reused for a materially different environment
- Treated as immutable unless integrity controls prove it
- Produced solely by model self-assessment

If evidence is regenerated, preserve the relationship between the previous and current records.

## Evidence Directory Rules

Planned structure:

```text
evidence/
├── discovery/
├── prototype/
├── runtime/
├── retrieval/
├── providers/
├── tools/
├── policy/
├── approval/
├── evaluation/
├── observability/
├── integration/
├── deployment/
├── readiness/
├── rollout/
└── patterns/
```

Directories must be created only when their phase produces real evidence.

An empty directory, placeholder file, or `.gitkeep` is not evidence.

## Authority Model

Authority is separated across trusted components.

| Decision or action | Authority |
|---|---|
| Authenticate user | Identity provider |
| Validate request | Gateway and deterministic code |
| Coordinate steps | Agent runtime |
| Retrieve evidence | Retrieval service under access policy |
| Generate diagnosis | Model using authorized evidence |
| Validate output schema | Deterministic code |
| Select permitted tool candidates | Runtime and tool registry |
| Authorize tool use | Deterministic policy engine |
| Approve consequential action | Authorized human |
| Execute approved action | Trusted tool service |
| Verify operational result | Independent tool or monitoring service |
| Record evidence | Evidence service |
| Promote release | Release authority |
| Roll back release | Platform operator under procedure |

No single component should silently accumulate all authority.

## Model Authority

The model may:

- Summarize
- Extract
- Classify
- Compare
- Rank
- Generate
- Recommend
- Propose structured parameters
- Identify uncertainty
- Abstain

The model may not:

- Authenticate
- Authorize
- Approve
- Issue credentials
- Retrieve secrets
- Change policy
- Expand its own permissions
- Execute unrestricted commands
- Modify evidence history
- Certify its own correctness
- Promote a release
- Disable safeguards

## Runtime Authority

The runtime may:

- Maintain state
- Coordinate approved steps
- Enforce budgets
- Call registered services
- Pause for approval
- Stop safely
- Record events

The runtime may not:

- Authorize itself
- Invent user identity
- Bypass policy
- Convert recommendations into approval
- Use unregistered tools
- Release a hold
- Modify policy decisions
- Hide failed steps

## Tool Authority

A tool must have:

- A narrow purpose
- A typed contract
- Validated parameters
- A defined identity
- Least-privilege permissions
- A side-effect classification
- A timeout
- Retry behavior
- Idempotency where required
- Result validation
- Audit evidence
- An owner
- A version

A tool must not expose unrestricted operating-system, database, cloud, or network authority to the model.

## Policy Authority

The policy engine evaluates trusted:

- Subject
- Tenant
- Role or attributes
- Action
- Resource
- Environment
- Risk tier
- Approval state
- Policy version

It returns:

```text
ALLOW
DENY
APPROVAL_REQUIRED
```

The policy engine must not accept model-generated identity or approval as trusted fact.

## Human Approval

Approval is required for defined consequential actions.

Approval must be bound to:

```text
approver identity
+ requesting identity
+ incident
+ action
+ parameters
+ target resource
+ environment
+ policy version
+ expiration
```

Approval must be:

- Explicit
- Attributable
- Time-bound
- Non-replayable
- Stored in trusted state
- Verified before execution

Slack, Teams, email, or a web page may present the approval request. The communication interface is not the authorization authority.

## Data Authority

Each source must have:

- An owner
- A classification
- A version or freshness indicator
- An access-control mechanism
- A retention rule
- A deletion rule where applicable
- A statement of whether it is authoritative or advisory

Model-generated content is advisory unless an authorized human or system explicitly promotes it through a governed process.

## Identity Rules

The lab must distinguish:

- Human identity
- Workload identity
- Provider credential
- Tool credential
- Tenant
- Session
- Role
- Group
- Approval identity

Do not place raw credentials in:

- Prompts
- Model context
- Source documents
- Logs
- Traces
- Evidence records
- Repository files

## Synthetic Data Rule

Until explicitly changed by a later approved phase:

- All incidents are synthetic.
- All runbooks are synthetic.
- All logs are synthetic.
- All identities are synthetic.
- All approvals are simulated.
- All remediation targets are simulated.
- No external customer or production data is permitted.

Synthetic data does not eliminate the need to test authorization and isolation.

## Simulation Rule

A simulated capability must be labeled.

Safe terms:

- Simulated remediation
- Mock provider
- Synthetic identity
- Reference implementation
- Local test environment
- Production-shaped control

Prohibited substitutions:

- Simulated remediation → production remediation
- Mock provider → live provider integration
- Synthetic identity → enterprise SSO
- Local deployment → customer production
- Reference pattern → implemented client platform

## Phase Completion Authority

A phase may be marked complete only when:

1. Required artifacts exist.
2. Validation commands pass.
3. Failure behavior is tested where required.
4. Evidence is preserved.
5. Limitations are documented.
6. Status documents are updated.
7. No prohibited claim appears.
8. The user or designated custodian accepts the gate.

The assistant may recommend phase completion. It must not silently declare a failed or incomplete phase complete.

## Git and Version Rules

Each phase commit must:

- Contain only the intended phase scope
- Use a descriptive commit message
- Avoid unrelated generated files
- Pass `git diff --check`
- Preserve evidence and limitations
- Update status truthfully

A commit proves that files were preserved. It does not independently prove that their claims are correct.

## Planned Commit Convention

```text
Phase 0: establish JD-aligned tutorial foundation
Phase 1: add client discovery package
Phase 2: define thin vertical slice
Phase 3: add cloud-native prototype foundation
```

Later commit messages must reflect actual completed scope.

## Interview Claim Rules

For an experience question:

1. Use one real primary project.
2. State what was personally designed, implemented, tested, deployed, or operated.
3. State the actual environment.
4. State one verified result.
5. State a limitation when material.

For a hypothetical question:

1. Answer the architecture directly.
2. Use “I would.”
3. Do not imply it was deployed.
4. Add a verified proof point only when clearly separate.

For a behavioral question:

1. Use one verified story.
2. Do not combine employers or projects.
3. Invent no client, metric, team size, deadline, or result.

## Safe Interview Language

- “I designed the architecture and implementation plan.”
- “I implemented and tested the component locally.”
- “I deployed this as an independent portfolio runtime.”
- “This was a production-shaped reference implementation.”
- “I would not describe it as external customer production.”
- “My closest direct experience is…”
- “I have working familiarity with that platform.”
- “The same architecture applies, but the implementation context differs.”

## Prohibited Interview Language Without Evidence

- “We deployed it for multiple enterprise clients.”
- “It is used broadly in production.”
- “The agent operates autonomously.”
- “The system is fully secure.”
- “The pipeline guarantees accuracy.”
- “The control plane governs customer workloads.”
- “Every change automatically triggers the complete evaluation suite.”
- “The model authorizes the action.”
- “The orchestrator decides whether the user has permission.”
- “Human approval makes unrestricted tools safe.”

## Documentation Rules

Every tutorial document must distinguish:

- Current behavior
- Planned behavior
- Example contract
- Expected future output
- Actual verified output

Use explicit labels:

```text
Current
Planned
Example
Expected
Verified
Limitation
Prohibited
```

Do not place expected output under a heading that implies it was observed.

## Diagram Rules

A diagram communicates architecture or sequence. It does not prove implementation.

Diagrams must not:

- Mark planned components as live
- Show authority that contradicts the written boundary
- Hide policy or approval for consequential actions
- Show the model connecting directly to unrestricted infrastructure
- Imply external customer production without evidence

## README Rules

The README may summarize:

- Purpose
- Planned phases
- Current status
- Verified capabilities
- How to run implemented phases
- Known limitations

The README must not get ahead of the evidence documents.

## Automated Assistant Rules

Any assistant continuing this repository must:

1. Inspect current files and Git status before proposing changes.
2. Preserve existing user work.
3. Work one authorized phase at a time.
4. Validate before declaring completion.
5. Never infer implementation from a roadmap.
6. Never infer deployment from code.
7. Never infer production readiness from deployment.
8. Never infer customer use from a public endpoint.
9. Keep models and orchestration outside authorization authority.
10. Stop and report a failed gate instead of bypassing it.
11. Provide exact commands and expected results.
12. Avoid duplicate files and overlapping sources of truth.

## Phase 0 Authority Posture

### Currently allowed

- Documentation
- JD mapping
- Tutorial sequencing
- Client-scenario definition
- Architecture diagrams
- Requirement and acceptance-criteria definition
- Evidence-contract planning
- Authority-boundary planning

### Currently prohibited

- Application runtime
- Model-provider calls
- Agent execution
- Tool execution
- Production credentials
- Secret retrieval
- Infrastructure mutation
- Live approval
- Production deployment
- External customer data
- Claims of implemented or tested runtime capability

## Phase 0E Completion Gate

Phase 0E passes when:

- Evidence levels are defined.
- Protected terms are defined.
- Component authority is separated.
- Model, runtime, tool, policy, approval, data, and identity rules exist.
- Simulation and synthetic-data boundaries are explicit.
- Phase-completion authority is explicit.
- Interview and documentation claim rules are explicit.
- Automated assistant continuation rules are explicit.
- Current authority remains documentation-only.

## Phase 0 Closure Requirements

Phase 0 can close only after:

1. Phase 0A–0E validations pass.
2. README status is updated.
3. Roadmap status is updated.
4. JD map status is updated.
5. The complete staged diff is reviewed.
6. The Phase 0 foundation is committed.
7. The commit is pushed.
8. The remote commit is verified.

## Next Authorized Phase After Closure

```text
Phase 1 — Client Discovery Under Ambiguity
```

Phase 1 authorizes discovery artifacts only. It does not authorize runtime implementation.

## Final Principle

The strongest valid claim is the one supported by reproducible evidence and explicit limitations.

No model, agent, assistant, document, test name, deployment, or roadmap may grant itself authority or maturity that the governing evidence does not support.
