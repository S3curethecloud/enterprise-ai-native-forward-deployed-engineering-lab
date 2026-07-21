# AI-Native Engineer Interview Accelerator

## Interview-Day Canonical Routing

For tomorrow's mock and live interview preparation, use this source order:

1. [`PHASE_00_17_JD_ALIGNED_CORE_ANSWERS.md`](PHASE_00_17_JD_ALIGNED_CORE_ANSWERS.md)
2. [`MOCK_AGENT_OPERATING_PROMPT.md`](MOCK_AGENT_OPERATING_PROMPT.md)
3. The matching canonical phase guide below
4. [`INTERVIEW_DAY_RAPID_REVIEW.md`](INTERVIEW_DAY_RAPID_REVIEW.md)
5. Experience and shadow-scenario guides for defensible examples

The canonical phases are:

| Phase | Interview guide |
|---|---|
| 0 — JD decomposition and foundation | [`PHASE_00_JD_DECOMPOSITION_AND_FOUNDATION.md`](phases/PHASE_00_JD_DECOMPOSITION_AND_FOUNDATION.md) |
| 1 — Client discovery under ambiguity | [`PHASE_01_CLIENT_DISCOVERY_UNDER_AMBIGUITY.md`](phases/PHASE_01_CLIENT_DISCOVERY_UNDER_AMBIGUITY.md) |
| 2 — Thin vertical slice | [`PHASE_02_THIN_VERTICAL_SLICE.md`](phases/PHASE_02_THIN_VERTICAL_SLICE.md) |
| 3 — Cloud-native prototype foundation | [`PHASE_03_CLOUD_NATIVE_PROTOTYPE_FOUNDATION.md`](phases/PHASE_03_CLOUD_NATIVE_PROTOTYPE_FOUNDATION.md) |
| 4 — Agent runtime and orchestration | [`PHASE_04_AGENT_RUNTIME_AND_ORCHESTRATION.md`](phases/PHASE_04_AGENT_RUNTIME_AND_ORCHESTRATION.md) |
| 5 — Permission-aware RAG | [`PHASE_05_PERMISSION_AWARE_RAG.md`](phases/PHASE_05_PERMISSION_AWARE_RAG.md) |
| 6 — Multi-provider abstraction | [`PHASE_06_MULTI_PROVIDER_ABSTRACTION.md`](phases/PHASE_06_MULTI_PROVIDER_ABSTRACTION.md) |
| 7 — Typed enterprise tools | [`PHASE_07_TYPED_ENTERPRISE_TOOLS.md`](phases/PHASE_07_TYPED_ENTERPRISE_TOOLS.md) |
| 8 — Deterministic policy routing | [`PHASE_08_POLICY_BASED_ROUTING.md`](phases/PHASE_08_POLICY_BASED_ROUTING.md) |
| 9 — Human approval and trusted execution | [`PHASE_09_HUMAN_APPROVAL.md`](phases/PHASE_09_HUMAN_APPROVAL.md) |
| 10 — Evaluation and EvalOps | [`PHASE_10_EVALUATION_AND_EVALOPS.md`](phases/PHASE_10_EVALUATION_AND_EVALOPS.md) |
| 11 — Lifecycle observability | [`PHASE_11_LIFECYCLE_OBSERVABILITY.md`](phases/PHASE_11_LIFECYCLE_OBSERVABILITY.md) |
| 12 — Enterprise integration and code-with | [`PHASE_12_CLIENT_ENGAGEMENT.md`](phases/PHASE_12_CLIENT_ENGAGEMENT.md) |
| 13 — Cloud-native deployment | [`PHASE_13_CLOUD_NATIVE_DELIVERY.md`](phases/PHASE_13_CLOUD_NATIVE_DELIVERY.md) |
| 14 — Production-readiness gate | [`PHASE_14_PRODUCTION_READINESS.md`](phases/PHASE_14_PRODUCTION_READINESS.md) |
| 15 — Staged release and controlled autonomy | [`PHASE_15_STAGED_RELEASE_AND_CONTROLLED_AUTONOMY.md`](phases/PHASE_15_STAGED_RELEASE_AND_CONTROLLED_AUTONOMY.md) |
| 16 — Reusable enterprise patterns | [`PHASE_16_REUSABLE_ENTERPRISE_PATTERNS.md`](phases/PHASE_16_REUSABLE_ENTERPRISE_PATTERNS.md) |
| 17 — Domain adaptation packs | [`PHASE_17_DOMAIN_ADAPTATION_PACKS.md`](phases/PHASE_17_DOMAIN_ADAPTATION_PACKS.md) |

Supplemental knowledge:

- [`SUPPLEMENT_COMPOUND_AI_AND_AGENT_REGISTRY.md`](phases/SUPPLEMENT_COMPOUND_AI_AND_AGENT_REGISTRY.md)

Every canonical guide contains a 30-second answer, a 60-second answer, claim
defense, and mock-agent routing cues. Interview learning can describe future
architecture, but only verified evidence can support “I implemented” claims.

## 1. Purpose

This directory converts Phases 5–17 of the lab into a documentation-only
learning track for interview preparation.

The immediate target is the AI Native Engineer interview scheduled for:

```text
July 22, 2026
3:00 PM Pacific Daylight Time
```

The track explains the terminology, architecture, engineering decisions,
enterprise controls, client-engagement practices, and operational concerns
contained in the target job description.

It does not implement the remaining phases.

## 2. Current Engineering Baseline

The repository has completed:

Phase 0 — JD decomposition and tutorial foundation
Phase 1 — Client discovery
Phase 2 — Thin vertical slice
Phase 3 — Cloud-native prototype foundation
Phase 4 — Deterministic runtime and orchestration

Phase 4 closure evidence:

Evidence	Value
Implementation commit	d65a465c57707aac1a144f69b40c2856e5f3d40e
Implementation CI run	29724059742
Closure commit	7ad0ddd82f66034388f740de835b21e964b4fe2b
Closure CI run	29727308021
Python tests	686 passed
Line coverage	96.95%
Branch coverage	94.33%
CI quality job	Passed
CI container job	Passed

The implemented runtime provides:

Typed immutable workflow state
Thirteen classified runtime states
Twenty-five authoritative transitions
Step and retry budgets
Explicit stop conditions
Append-only in-memory checkpoints
Optimistic concurrency
Deterministic replay
CT-07 runtime trace events
Runtime-only FastAPI endpoints
Controlled errors
Unit, contract, runtime, and integration tests
## 3. Temporary Roadmap Pivot

Until the interview is complete, Phases 5–17 are an interview-learning track.

Allowed work:

Markdown tutorials
Terminology explanations
Architecture diagrams
Design exercises
Interview questions and answers
Mental-note summaries
Simulated client workshops
Honest shadow-experience scenarios
Post-interview implementation plans
Links to authoritative references

Prohibited work:

External model calls
Provider credentials
Enterprise retrieval
Vector-database integration
Tool execution
Human approval execution
Infrastructure mutation
Cloud deployment
Production deployment
Claims that a documented capability is implemented
Claims of professional experience that did not occur

No Python source, API route, container definition, dependency lock, CI workflow,
infrastructure definition, or executable integration should be changed as part
of this interview-learning track.

## 4. Two Independent Status Dimensions

Every remaining phase has two separate statuses.

Status dimension	Meaning
Learning status	Whether the tutorial has been authored and reviewed
Implementation status	Whether the capability has been built, tested, and evidenced

A completed tutorial does not make an implementation complete.

The allowed values are:

Learning status
Not started
Drafted
Reviewed
Interview-ready
Implementation status
Not started
Authorized
In progress
Locally validated
CI validated
Complete

During the interview-learning track:

Phases 5–17 learning status may advance.
Phases 5–17 implementation status remains NOT STARTED.
## 5. Phase-by-Phase Interview Curriculum

| Phase | Learning topic | Learning status | Implementation status |
|---:|---|---|---|
| 5 | Permission-aware RAG and context engineering | Drafted | Not started |
| 6 | Multi-provider abstraction | Drafted | Not started |
| 7 | Typed enterprise tools and MCP | Drafted | Not started |
| 8 | Deterministic policy routing | Drafted | Not started |
| 9 | Human approval and trusted execution | Drafted | Not started |
| 10 | Evaluation and EvalOps | Drafted | Not started |
| 11 | Lifecycle observability | Drafted | Not started |
| 12 | Client engagement and code-with delivery | Drafted | Not started |
| 13 | Cloud-native delivery | Drafted | Not started |
| 14 | Production readiness | Drafted | Not started |
| 15 | Domain-specific workflows | Drafted | Not started |
| 16 | Compound AI and bonus qualifications | Drafted | Not started |
| 17 | Reusable patterns and interview synthesis | Drafted | Not started |

## 6. Phase 5 — Permission-Aware RAG

Learn:

Retrieval-augmented generation
Context engineering
Embeddings
Chunking
Metadata
Vector search
Keyword search
Hybrid retrieval
Query rewriting
Reranking
Context-window management
Grounding
Citations
Access-control filtering
Tenant isolation
Retrieval evaluation
Prompt-injection risks
Abstention when evidence is insufficient

Interview outcome:

Explain how an enterprise agent finds relevant evidence without exposing
unauthorized data or presenting unsupported statements as facts.

## 7. Phase 6 — Multi-Provider Abstraction

Learn:

OpenAI, Anthropic, Vertex AI, and open-source model roles
Provider adapters
Provider-neutral request and response contracts
Capability discovery
Model routing
Fallbacks
Timeouts
Retry rules
Rate limits
Streaming
Structured output
Tool-call normalization
Token accounting
Cost accounting
Safety-setting normalization
Provider-specific differences
Vendor lock-in tradeoffs

Interview outcome:

Explain how a stable application interface can support multiple model providers
without pretending that all provider capabilities are identical.

## 8. Phase 7 — Typed Enterprise Tools and MCP

Learn:

Tool contracts
JSON Schema
Function calling
Model Context Protocol
Tool registries
Capability discovery
Least privilege
Input validation
Output validation
Idempotency
Timeouts
Retry safety
Side-effect classification
Audit records
Secrets management
Sandboxing
Allowlisting
Compensating actions
Tool-result trust boundaries

Interview outcome:

Explain how a model may request a tool while deterministic application code
retains authority over whether and how the tool executes.

## 9. Phase 8 — Deterministic Policy Routing

Learn:

Policy decision points
Policy enforcement points
Attribute-based access control
Role-based access control
Tenant and resource scope
Data classification
Deterministic routing
Deny-by-default behavior
Policy versioning
Decision lineage
Authorization expiry
Fail-closed behavior
Separation between model recommendations and policy authority

Interview outcome:

Explain why an LLM may provide context to a policy decision but must not grant
itself access or execution authority.

## 10. Phase 9 — Human Approval and Trusted Execution

Learn:

Human-in-the-loop workflows
Approval gates
Separation of duties
Four-eyes control
Approval scope
Approval expiry
Revocation
Evidence presented to approvers
Approval identity
Audit trails
Duplicate submission protection
Timeout behavior
Revalidation before execution
Recommendation versus execution

Interview outcome:

Explain how a recommendation becomes an authorized action without treating a
human click as an unlimited or permanent grant.

## 11. Phase 10 — Evaluation and EvalOps

Learn:

Task success
Exact-match accuracy
Semantic quality
Retrieval recall and precision
Groundedness
Citation correctness
Tool-selection accuracy
Policy compliance
Safety
Latency
Token consumption
Cost per task
Golden datasets
Test cases
Rubrics
Model-based graders
Human evaluation
Regression testing
Online versus offline evaluation
Quality thresholds
Evaluation versioning

Interview outcome:

Explain how to determine whether an agent is useful, safe, fast, and
cost-effective—and how to detect regressions before release.

## 12. Phase 11 — Lifecycle Observability

Learn:

Structured logs
Metrics
Traces
Spans
Correlation identifiers
Context propagation
Model-call telemetry
Retrieval telemetry
Tool-call telemetry
Policy-decision telemetry
Latency breakdowns
Error classification
Dashboards
Alerts
Service-level indicators
Service-level objectives
Distributed debugging
Sensitive-data redaction

Interview outcome:

Explain how to reconstruct what happened across an agent workflow without
logging prompts, credentials, protected data, or hidden reasoning.

Official foundation:

OpenTelemetry describes traces, metrics, logs, and baggage as related
telemetry signals.
A trace represents the path of a request through an application.
Context propagation connects activity across process and service boundaries.

References:

https://opentelemetry.io/docs/concepts/signals/
https://opentelemetry.io/docs/concepts/signals/traces/
https://opentelemetry.io/docs/concepts/context-propagation/
## 13. Phase 12 — Client Engagement

Learn:

Stakeholder discovery
Problem framing
Current-state mapping
Use-case prioritization
Decision decomposition
Risk and authority workshops
Success measures
Acceptance criteria
Proofs of concept
Prototypes
Code-with sessions
Architecture decision records
Assumption registers
Managing ambiguity
Communicating tradeoffs
Building trust
Adoption planning
Executive versus engineering communication

Interview outcome:

Explain how to move from an ambiguous client request to a bounded,
measurable, low-risk workflow and how to collaborate while building it.

## 14. Phase 13 — Cloud-Native Delivery

Learn:

APIs
Microservices
Containers
Docker images
Kubernetes Pods
Deployments
Services
Configuration
Secrets
Health and readiness probes
Horizontal scaling
Serverless functions
Event-driven architectures
Queues
Streams
CI/CD
Infrastructure as code
Terraform
Helm
Environment promotion
Rollback
Supply-chain security

Interview outcome:

Explain how an agentic workflow moves from a local service to a repeatable,
observable, scalable deployment.

Official foundation:

Kubernetes Pods are the smallest deployable computing units.
Deployments declaratively manage application workloads.
Services provide stable network access to groups of Pods.
Terraform configuration declaratively describes desired infrastructure.
CI/CD automates tests and builds in response to repository events.

References:

https://kubernetes.io/docs/concepts/workloads/pods/
https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
https://kubernetes.io/docs/concepts/services-networking/service/
https://developer.hashicorp.com/terraform/docs/glossary
## 15. Phase 14 — Production Readiness

Learn:

Reliability
Availability
Resilience
Fault isolation
Backpressure
Circuit breakers
Bulkheads
Rate limiting
Graceful degradation
Disaster recovery
Backup and restore
Capacity planning
Security reviews
Threat modeling
Incident response
Runbooks
Rollback
On-call ownership
Change management
Compliance evidence
Cost controls

Interview outcome:

Explain the difference between a successful prototype and a system an
enterprise can safely operate.

## Supplemental Topic — Domain-Specific Workflow Knowledge (Canonical Phase 17)

Learn how the same architecture changes across:

Finance
Entitlements
Segregation of duties
Transaction evidence
Auditability
Model risk
Regulatory retention
Human approval
Nonrepudiation
Healthcare
Protected health information
Minimum-necessary access
Consent
Clinical safety
Evidence provenance
Human clinical judgment
Audit trails
Data retention
Retail
Product catalogs
Inventory
Customer identity
Personalization
Returns
Fraud
Seasonal scaling
Cost and latency sensitivity

Interview outcome:

Explain which architectural controls remain universal and which must be
adapted to a domain's data, risks, workflows, and regulations.

## Supplemental Topic — Compound AI and Agent Registries

Learn:

Compound AI systems
Agent architectures
Orchestration frameworks
State machines
Graph workflows
Agent registries
Tool registries
Model registries
Event streams
Stream processing
Event sourcing
Workflow engines
Control planes
Data planes
AI-native architecture
Cloud-native plus generative-model architecture
Modularity
Performance
Efficiency
Reusability
Multi-industry adaptation

Interview outcome:

Explain that an enterprise agent is not merely a prompt. It is a compound
system combining models with retrieval, tools, policies, state, evaluation,
observability, infrastructure, and human governance.

## Supplemental Topic — Reusable Pattern Knowledge (Canonical Phase 16)

Learn:

Reference architectures
Reusable adapters
Contract libraries
Policy patterns
Evaluation templates
Observability conventions
Runbook templates
Architecture decision records
Client roadmaps
Adoption maturity models
Knowledge-sharing sessions
Internal accelerators
Post-engagement handoff

Interview outcome:

Explain how lessons from one engagement can become governed, reusable assets
without copying client data, secrets, or client-specific assumptions.

## 19. Seven JD Pillars

The complete job description can be remembered through seven pillars:

Discover the correct business problem.
Design a controlled agent workflow.
Integrate models, retrieval, policies, and tools through typed boundaries.
Deliver it through cloud-native engineering.
Measure quality, safety, latency, and cost.
Operate, observe, and debug it in real environments.
Earn client trust and turn lessons into reusable patterns.
## 20. Honest Shadow-Experience Policy

A shadow-experience scenario is a documented simulation used to practice
engineering judgment.

It must identify:

Category	Required meaning
Implemented evidence	Behavior that exists and is tested in this repository
Design exercise	Architecture that was reasoned about but not implemented
Simulated client context	A fictional workshop or enterprise scenario
Production requirements	Additional work required before real deployment
Personal experience	Only experience the learner can truthfully claim

Approved phrasing:

In my portfolio lab, I modeled the engineering decisions for a bounded
enterprise incident-diagnostic workflow. I implemented its typed contracts
and deterministic orchestration boundary, then documented how retrieval,
provider abstraction, tools, evaluation, observability, and cloud deployment
would be added under explicit controls.

Prohibited phrasing:

I deployed this solution for an enterprise client.

The learning track creates knowledge and interview practice. It does not create
professional employment history or production deployment experience.

## 21. Standard Tutorial Structure

Every canonical Phase 0–17 tutorial must contain:

Purpose
Connection to the job description
Plain-English explanation
Terminology
Enterprise usefulness
Architecture
Connection to the incident-diagnostic lab
Security and authority boundaries
Design choices and tradeoffs
Failure modes
Metrics and evidence
What the learner must understand
Mental notes
Interview questions
Thirty-second explanation
Sixty-second explanation
Shadow-experience scenario
Post-interview implementation backlog
Official references
Learning gate
## 22. Interview Study Order

The numeric phase order remains the implementation roadmap order.

The interview study order is intentionally different:

Phase 12 — Client engagement
Phase 5 — RAG and context engineering
Phase 6 — Multi-provider abstraction
Phase 10 — Evaluation
Phase 11 — Observability
Phase 13 — Cloud-native delivery
Phase 16 — Compound AI and bonus knowledge
Phase 7 — Tools
Phase 8 — Policy routing
Phase 9 — Human approval
Phase 14 — Production readiness
Phase 15 — Domain workflows
Phase 17 — Reusable patterns and synthesis

This order prioritizes the topics most likely to connect the candidate's
technical knowledge with the role's client-facing responsibilities.

## 23. Interview Gate

The learning track is interview-ready when the learner can:

Explain the seven JD pillars without reading
Draw the compound AI architecture from memory
Explain discovery through production operations
Explain RAG without describing it as only a vector database
Explain orchestration without describing it as only an agent framework
Explain why policy authority remains deterministic
Explain how tools are validated and controlled
Compare OpenAI, Anthropic, Vertex AI, and open-source integration concerns
Define accuracy, latency, safety, and cost measures
Explain logs, metrics, traces, and correlation
Explain Docker, Kubernetes, serverless, events, CI/CD, Terraform, and Helm
Adapt the workflow to finance, healthcare, and retail
Lead a simulated discovery conversation
Describe the lab honestly
Distinguish implemented evidence from future architecture
Give concise thirty-second and sixty-second answers
## 24. Post-Interview Resumption

After the interview:

Preserve this directory as a reusable learning asset.
Return to the implementation roadmap at Phase 6 after the interview.
Review Phase 6 authority before changing executable code.
Convert the Phase 6 tutorial into an implementation design.
Implement and validate Phase 6 under a separate gate.
Continue through Phase 17 without treating tutorial completion as
implementation evidence.
## 25. Current Decision
PHASE 4: COMPLETE
INTERVIEW LEARNING TRACK: AUTHORIZED
PHASES 5–17 DOCUMENTATION: AUTHORIZED
PHASES 5–17 IMPLEMENTATION: NOT AUTHORIZED
NEXT DELIVERABLE: INTERVIEW STUDY SPRINT

