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
| JD-04 | Rapidly prototype an agent workflow | 2, 3 | Thin vertical-slice API | Acceptance tests | Prototype evidence | Planned |
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
| JD-24 | Conduct POCs | 2, 3 | Thin vertical-slice prototype | Acceptance criteria | POC decision report | Planned |
| JD-25 | Conduct code-with sessions | 12 | Guided typed-tool extension | Pairing exercise validation | Code-with artifact | Planned |
| JD-26 | Measure agent accuracy | 10 | Task and component evaluators | Golden dataset | Accuracy evidence | Planned |
| JD-27 | Measure latency | 10, 11 | Timing instrumentation | p50 and p95 tests | Latency report | Planned |
| JD-28 | Measure safety | 10 | Adversarial and authorization suite | Safety test execution | Safety report | Planned |
| JD-29 | Measure cost effectiveness | 6, 10, 11 | Token and task-cost accounting | Provider/workflow comparison | Cost-per-successful-task report | Planned |
| JD-30 | Create reusable patterns | 16 | Pattern packages | Pattern completeness review | Reusable pattern catalog | Planned |
| JD-31 | Produce technical documentation | All | Phase tutorials and decision records | Documentation checks | Versioned documentation | Planned |
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
| Phase 1A current-state workflow | Complete |
| Phase 1B stakeholder map | Complete |
| Phase 1C data-source inventory | Complete |
| Phase 1D decision decomposition | Complete |
| Phase 1E risk and authority matrix | Complete |
| Phase 1F assumption register | Complete |
| Phase 1G success measures | Complete |
| Phase 1 discovery package | Complete |
| JD requirements mapped | 36 of 36 |
| JD requirements documented | 4 of 36 |
| JD requirements implemented | 0 of 36 |
| JD requirements complete | 0 of 36 |
| Runtime authority | None |
| External provider access | None |
| Tool execution authority | None |
| Production infrastructure mutation | None |

## Next Phase

```text
Phase 2 — Thin Vertical Slice

Phase 2 will define the recommendation-only use case, requirements, contracts, acceptance criteria, exclusions, and threat boundary. It will not implement the application runtime.
```
