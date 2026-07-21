# Accenture AI Native Software Engineering — JD Requirement Map

## Document Purpose

This document maps the target AI Native Software Engineering Senior Manager/Associate Director job requirements to concrete tutorial phases, implementation artifacts, tests, evidence, and interview demonstrations.

The purpose is to prevent the lab from becoming a generic agent demo.

A job requirement is considered covered only when the repository contains:

1. A concept explanation
2. A working or intentionally simulated implementation
3. A test or validation procedure
4. An evidence artifact
5. An interview-ready explanation

## Source Position

Target opportunity:

- Role: AI Native Software Engineering Senior Manager/Associate Director
- Job family: Forward-Deployed Engineer
- Job number referenced by the public posting: R00325181
- Interview scheduling may reference a related requisition number
- Source reviewed: Accenture public careers posting
- Source review date: July 18, 2026

This repository is an independent tutorial and portfolio project. It is not an Accenture product, client engagement, or official training resource.

## Role Mission

The role combines five responsibilities:

1. Embed with enterprise clients and operate under ambiguity.
2. Design and implement enterprise agentic workflows.
3. Integrate AI systems with existing client platforms.
4. Move prototypes into secure and supportable production services.
5. Convert project learning into reusable patterns and roadmaps.

## Coverage Status Definitions

| Status | Meaning |
|---|---|
| Planned | Requirement is mapped but no tutorial artifact exists |
| Documented | Concept and architecture are written |
| Implemented | Working code or configuration exists |
| Tested | Expected behavior is verified |
| Evidence-recorded | Test result and decision evidence are preserved |
| Complete | Documentation, implementation, tests, evidence, and interview explanation exist |

## Requirement Traceability Matrix

| ID | JD capability | Lab phase | Required implementation | Required validation | Required evidence | Initial status |
|---|---|---:|---|---|---|---|
| JD-01 | Operate under ambiguous client requirements | 1 | Structured discovery workflow | Workshop-output review | Discovery package | Documented |
| JD-02 | Embed with clients as technologist and advisor | 1, 12 | Stakeholder and code-with exercises | Facilitation checklist | Workshop and code-with records | Planned |
| JD-03 | Define high-value agent use cases | 1, 2 | Use-case prioritization matrix | Scope review | Prioritized use case | Documented |
| JD-04 | Rapidly prototype an agent workflow | 2, 3 | Thin vertical-slice API | Acceptance tests | Prototype evidence | Documented |
| JD-05 | Design enterprise-ready agents | 4 | Explicit runtime state and execution graph | State-transition tests | Runtime decision trace | Planned |
| JD-06 | Implement retrieval and context engineering | 5 | Permission-aware RAG pipeline | Retrieval and ACL tests | Retrieval evidence | Planned |
| JD-07 | Implement orchestration | 4 | Deterministic state-machine workflow | Transition, retry, and stop tests | Workflow trace | Planned |
| JD-08 | Implement policy-based routing | 8 | External deterministic policy service | Allow, deny, approval tests | Policy decision records | Planned |
| JD-09 | Implement controlled tool invocation | 7 | Typed enterprise tool registry | Contract and side-effect tests | Tool-call evidence | Planned |
| JD-10 | Build evaluation harnesses | 10 | Layered evaluation runner | Golden and adversarial datasets | Evaluation report | Planned |
| JD-11 | Provide lifecycle observability | 11 | Logs, metrics, traces, and correlation IDs | End-to-end trace test | Trace reconstruction | Planned |
| JD-12 | Abstract multiple AI providers | 6 | Common provider interface and adapters | Provider contract tests | Provider comparison report | Planned |
| JD-13 | Preserve provider-specific capabilities | 6 | Capability metadata and routing constraints | Capability-routing tests | Routing decision evidence | Planned |
| JD-14 | Use APIs and microservices | 3 | FastAPI service boundaries | API and contract tests | OpenAPI and test report | Planned |
| JD-15 | Use containers | 3, 13 | Docker images and Compose environment | Container health tests | Image and runtime evidence | Planned |
| JD-16 | Deploy to Kubernetes | 13 | Kubernetes manifests and Helm chart | Deployment and readiness tests | Cluster deployment evidence | Planned |
| JD-17 | Use serverless patterns | 13 | Optional event-driven serverless adapter | Event-processing tests | Serverless comparison record | Planned |
| JD-18 | Use event-driven architecture | 3, 12 | Domain event envelope and event bus | Delivery and idempotency tests | Event replay evidence | Planned |
| JD-19 | Implement CI/CD | 13, 14 | Automated quality and release workflow | Pipeline execution | Pipeline evidence | Planned |
| JD-20 | Use infrastructure as code | 13 | Terraform and Helm | Validate and plan checks | IaC evidence | Planned |
| JD-21 | Monitor and debug production behavior | 11, 14 | Diagnostic dashboard and runbook | Failure-injection exercise | Incident evidence package | Planned |
| JD-22 | Tailor workflows to enterprise domains | 17 | Healthcare, finance, and retail packs | Domain-boundary tests | Domain design records | Planned |
| JD-23 | Lead technical workshops | 1 | Guided discovery workshop | Workshop rubric | Workshop output | Documented |
| JD-24 | Conduct POCs | 2, 3 | Thin vertical-slice prototype | Acceptance criteria | POC decision report | Documented |
| JD-25 | Conduct code-with sessions | 12 | Guided typed-tool extension | Pairing exercise validation | Code-with artifact | Planned |
| JD-26 | Measure agent accuracy | 10 | Task and component evaluators | Golden dataset | Accuracy evidence | Planned |
| JD-27 | Measure latency | 10, 11 | Timing instrumentation | p50 and p95 tests | Latency report | Planned |
| JD-28 | Measure safety | 10 | Adversarial and authorization suite | Safety test execution | Safety report | Planned |
| JD-29 | Measure cost effectiveness | 6, 10, 11 | Token and task-cost accounting | Provider/workflow comparison | Cost-per-successful-task report | Planned |
| JD-30 | Create reusable patterns | 16 | Pattern packages | Pattern completeness review | Reusable pattern catalog | Planned |
| JD-31 | Produce technical documentation | All | Phase tutorials and decision records | Documentation checks | Versioned documentation | Documented |
| JD-32 | Influence client roadmaps | 1, 16 | Phased delivery and adoption roadmap | Roadmap review | Client-style roadmap | Documented |
| JD-33 | Design compound AI systems | 4–11 | Runtime, RAG, model, tool, policy, and evidence layers | End-to-end system tests | Compound-system trace | Planned |
| JD-34 | Use orchestration or registry patterns | 4, 7 | Runtime graph and tool registry | Registration and routing tests | Registry evidence | Planned |
| JD-35 | Optimize modularity and efficiency | 3, 6, 10 | Replaceable adapters and bounded workflows | Performance comparison | Architecture decision record | Planned |
| JD-36 | Deploy progressively into operational reality | 14, 15 | Readiness gate and staged release controls | Promotion and rollback tests | Release evidence package | Planned |

## Job Responsibility to Tutorial Outcome

### Agent Architecture and Engineering

The lab must demonstrate:

- Explicit agent state
- Deterministic workflow transitions
- Retrieval
- Context construction
- Tool selection
- Policy evaluation
- Human approval
- Execution
- Result verification
- Evaluation
- Observability

Required phases:

```text
Phase 4 → Phase 5 → Phase 7 → Phase 8 → Phase 9 → Phase 10 → Phase 11
```

### AI Platform Integration

The lab must demonstrate:

- Common request and response envelopes
- Provider adapters
- Capability metadata
- Provider-specific constraints
- Policy-aware routing
- Normalized errors
- Bounded retries
- Evaluation-based selection

Required phase:

```text
Phase 6
```

### Cloud-Native Engineering

The lab must demonstrate:

- FastAPI services
- REST/OpenAPI contracts
- Microservice boundaries
- Docker
- Kubernetes
- Helm
- Terraform
- CI/CD
- Event-driven processing
- Logs, metrics, and traces
- Debugging and rollback

Required phases:

```text
Phase 3 → Phase 11 → Phase 12 → Phase 13 → Phase 14
```

### Domain-Specific Workflows

The common runtime will be adapted without pretending that every industry has the same workflow.

Planned domain packs:

| Domain | Example workflow | Required boundary |
|---|---|---|
| Healthcare | Clinical-intake drafting | Clinician remains final authority |
| Finance | Payment-exception investigation | Segregation of duties |
| Retail | Order and refund exception | Refund authorization limits |

Required phase:

```text
Phase 17
```

### Client Engagement

The lab must teach:

- Workflow-first discovery
- Stakeholder mapping
- Data-source identification
- Risk and authority boundaries
- Thin vertical-slice selection
- Acceptance criteria
- POC planning
- Code-with facilitation
- Client ownership and knowledge transfer

Required phases:

```text
Phase 1 → Phase 2 → Phase 12
```

### Measure and Improve

The lab must separately evaluate:

- Retrieval quality
- Generation quality
- Citation support
- Tool selection
- Tool arguments
- Authorization behavior
- Side effects
- Task completion
- Safety
- Latency
- Cost
- Reliability
- Escalation
- Trace completeness

Required phases:

```text
Phase 10 → Phase 11 → Phase 14
```

### Knowledge Sharing

Each reusable pattern must contain:

1. Problem
2. Applicability
3. When not to use it
4. Architecture
5. Contracts
6. Reference implementation
7. Security boundaries
8. Failure modes
9. Tests
10. Evaluation criteria
11. Deployment guidance
12. Interview explanation

Required phase:

```text
Phase 16
```

## Qualification Coverage

### Cloud-Native Engineering Experience

Demonstrated through:

- APIs
- Microservices
- Containers
- Kubernetes
- Serverless comparison
- Events
- CI/CD
- Terraform
- Helm
- Monitoring
- Debugging

### Agentic-System Depth

Demonstrated through:

- Explicit runtime state
- RAG
- Context engineering
- Tool invocation
- Policy routing
- Human approval
- Evaluation
- Observability
- Progressive autonomy

### Multi-Provider AI Platforms

Demonstrated through:

- OpenAI adapter
- Anthropic adapter
- Google/Vertex adapter
- Deterministic local mock provider
- Capability-aware routing
- Provider evaluation

Provider credentials and external calls are not required for the initial local phases.

### Programming

Primary lab language:

```text
Python
```

Supporting technologies:

```text
SQL
YAML
JSON
Bash
HCL
```

### Production Delivery

Demonstrated through:

- CI/CD
- Infrastructure as code
- Readiness and health checks
- Monitoring
- Failure injection
- Debugging
- Runbooks
- Rollback
- Release evidence

### Client Communication

Demonstrated through:

- Discovery guide
- Workshop exercise
- Architecture decision records
- POC recommendation
- Code-with exercise
- Executive summary
- Phased adoption roadmap

## Required Evidence Package

The final lab must produce:

```text
evidence/
├── discovery/
├── prototype/
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
└── reusable-patterns/
```

Evidence is generated only when its corresponding phase is implemented. Empty evidence directories must not be used to imply completion.

## Interview Demonstration Standard

For every major requirement, the learner must be able to answer:

1. What business problem does this component solve?
2. Why is it a separate responsibility?
3. What did I implement?
4. How did I test it?
5. What evidence proves its behavior?
6. What can fail?
7. How does the system fail safely?
8. What trade-off did I make?
9. What would change in a real client environment?
10. What should not be delegated to the model?

## Completion Gate

The JD is not considered fully covered until every requirement in the traceability matrix is marked Complete.

A requirement may not be marked Complete based only on:

- A diagram
- A README statement
- An empty directory
- A placeholder test
- A mocked success response without failure validation
- A conceptual claim without an artifact
- A deployed endpoint without evaluation or evidence

## Current Status

| Deliverable | Status |
|---|---|
| Phase 0 JD-aligned tutorial foundation | Complete |
| Phase 1 client discovery package | Complete |
| Phase 2 thin vertical-slice package | Complete |
| Phase 3 cloud-native prototype foundation | Complete |
| Phase 3 executable contracts | 7 of 7 implemented and tested |
| Phase 3 local quality gates | Passed |
| Phase 3 dependency integrity | Passed |
| Phase 3 container execution | Passed in CI |
| Phase 3 quality execution | Passed in CI |
| Phase 3 CI run | 29706949782 |
| Phase 3 evidence commit | f94d90b3b03b70cb5102945e0dc32d3badef15c2 |
| Phase 4 deterministic runtime | Complete |
| Phase 4 implementation commit | d65a465c57707aac1a144f69b40c2856e5f3d40e |
| Phase 4 CI run | [29724059742](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29724059742) |
| Phase 4 CI quality job | Passed |
| Phase 4 CI container job | Passed |
| Phase 4 runtime states | 13 of 13 classified |
| Phase 4 authoritative transitions | 25 of 25 implemented and tested |
| Phase 4 local test suite | 686 passing |
| Phase 4 line coverage | 96.95% |
| Phase 4 branch coverage | 94.33% |
| Phase 5 overall | In progress |
| Phase 5A RAG design | Complete |
| Phase 5A evidence commit | 5b7907bf1bf8aa96c163d034baf183de3e600587 |
| Phase 5A CI run | [29768908988](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29768908988) |
| Phase 5B typed retrieval contracts | Complete |
| Phase 5B implementation commit | efd62671b27e725d2936a2c7ae3a1a0d24b06ca6 |
| Phase 5B CI run | [29780263857](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29780263857) |
| Phase 5B retrieval contract tests | 37 passing |
| Complete local test suite | 723 passing |
| Phase 5C synthetic corpus and deterministic keyword retrieval | Complete |
| Phase 5C implementation commit | 8cee3d71676440824b700c62359c162a98cb2b8e |
| Phase 5C CI run | [29795504565](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29795504565) |
| Phase 5C retrieval tests | 76 passing |
| Complete local test suite | 762 passing |
| Phase 5D tenant, service, and classification filtering | Complete |
| Phase 5D closure commit | bdc235b7936186baedeec1181938f57977150b35 |
| Phase 5D closure CI run | [29807419438](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29807419438) |
| Phase 5E local deterministic embeddings and vector retrieval | Complete |
| Phase 5E implementation commit | fa02cb90e62c5a1279b1ec7b025d54375fba72f3 |
| Phase 5E CI run | [29810229699](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29810229699) |
| Phase 5E closure commit | 573b8c196ae46dd272fcb90c6695cbcc6af87bfd |
| Phase 5E closure CI run | [29811114122](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29811114122) |
| Phase 5E embedding tests | 15 passing |
| Phase 5E vector tests | 23 passing |
| Phase 5E retrieval tests | 124 passing |
| Complete local test suite | 814 passing |
| Phase 5F hybrid retrieval and reranking | Complete |
| Phase 5F implementation commit | ec0dca55d934d2324a514956aadfb3c8daf341bc |
| Phase 5F CI run | [29813776046](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29813776046) |
| Phase 5F closure commit | 2489a6e54fe5b93484b09b40c5ffd9764075dcee |
| Phase 5F closure CI run | [29815184214](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29815184214) |
| Phase 5F hybrid pytest cases | 33 passing |
| Phase 5F retrieval tests | 157 passing |
| Complete local test suite | 847 passing |
| Phase 5G context construction and token budgets | Complete |
| Phase 5G implementation commit | 369e05e21b61f6e0961111d9cfff4515ca0e27db |
| Phase 5G CI run | [29817755525](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29817755525) |
| Phase 5G closure commit | 3851259a94474cab6b4d167b84cca56278e1a3b3 |
| Phase 5G closure CI run | [29818951742](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29818951742) |
| Phase 5G context pytest cases | 22 passing |
| Phase 5G retrieval tests | 179 passing |
| Complete local test suite | 869 passing |
| Phase 5H prompt-injection and retrieval-contamination controls | Complete |
| Phase 5H implementation commit | 2c1a812bbba005345c3f394011a9b1c3580ce995 |
| Phase 5H CI run | [29820773913](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29820773913) |
| Phase 5H closure commit | f72e2a5230517597a641e8994cff4a72612bc833 |
| Phase 5H closure CI run | [29822375893](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29822375893) |
| Phase 5H content-control pytest cases | 26 passing |
| Phase 5H retrieval tests | 205 passing |
| Complete local test suite | 895 passing |
| Phase 5I citation validation and controlled abstention | Implementation verified; closure-commit CI pending |
| Phase 5I implementation commit | f4d3c2079535699374e3ff08a1f955f8f26321f9 |
| Phase 5I CI run | [29848371644](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29848371644) |
| Phase 5I citation-validation pytest cases | 26 passing |
| Phase 5I retrieval tests | 231 passing |
| Complete local test suite | 921 passing |
| Phase 5J retrieval evaluation and lifecycle telemetry | Authorized only after Phase 5I closure-commit CI |
| Enterprise retrieval | Not authorized |
| External embeddings and managed vector services | Not authorized |
| JD requirements mapped | 36 of 36 |
| JD requirements documented | 7 of 36 |
| JD requirements implemented | 0 of 36 |
| JD requirements complete | 0 of 36 |
| Local validation runtime authority | Bounded deterministic coordination only |
| Agent runtime authority | Local state coordination; no provider, retrieval, or tool authority |
| External provider access | None |
| Enterprise retrieval authority | None |
| Tool execution authority | None |
| Production infrastructure mutation | None |

JD requirements implemented remains zero because the repository now contains bounded runtime coordination and synthetic permission-aware keyword retrieval components, but it does not yet complete an end-to-end agent workflow, enterprise POC, external provider integration, enterprise retrieval capability, tool capability, or other entire JD requirement.

## Next Authorized Work After Closure-Commit CI

```text
Phase 5J — Retrieval Evaluation and Lifecycle Telemetry
```

Phase 5H closed after exact-commit CI run
29822375893
passed against closure commit
f72e2a5230517597a641e8994cff4a72612bc833.

Phase 5I implemented deterministic all-or-nothing citation validation over
retained synthetic evidence. It added exact source-document-chunk
resolution, content-hash and complete-content checks, locator,
lifecycle, temporal, TTL, and document-expiry validation, immutable
validation evidence, and five controlled abstention reasons.

Phase 5I passed exact-commit CI run
29848371644
against implementation commit
f4d3c2079535699374e3ff08a1f955f8f26321f9.

Phase 5J becomes authorized only after the Phase 5I closure commit passes
exact-commit CI. Its scope remains limited to bounded local retrieval
evaluation and lifecycle telemetry over synthetic evidence.

Enterprise sources, production data, external evaluators, external
telemetry services, model providers, prompt or model execution, tool
execution, retrieval or context API routes, infrastructure mutation,
cloud deployment, and production deployment remain unauthorized.
