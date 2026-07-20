# AI Native Engineer Mock Interview

## 1. Purpose

This guide tests whether the learner can explain the target role using:

- Direct professional experience
- Transferable production experience
- Inspectable portfolio evidence
- Clearly labeled architecture exercises
- Honest limitations

Do not memorize every sentence. Practice the structure and evidence.

## 2. Answer Structure

For architecture questions, use:

1. Business outcome
2. User and decision
3. Architecture
4. Authority boundary
5. Failure modes
6. Metrics
7. Tradeoff
8. Evidence

For experience questions, use:

1. Situation
2. Task
3. Constraints
4. Decision
5. Action
6. Evidence
7. Result
8. Limitation
9. Next step

## 3. Opening Introduction

### Question

Tell me about yourself.

### Target answer

> I am a cloud, security, and AI platform architect with more than fifteen
> years across carrier-grade infrastructure, regulated healthcare, enterprise
> cloud, cybersecurity, and AI platform delivery. My production foundation is
> reliability, identity, networking, incident response, and controlled change.
> Since 2021, my work has focused increasingly on governed GenAI and agentic
> systems, including RAG, orchestration, evaluation, policy, APIs,
> observability, and cloud-native delivery. I also build independent platforms
> and labs so the implementation evidence is inspectable. What attracts me to
> this role is the combination of hands-on engineering, client discovery, and
> turning prototypes into operationally supportable systems.

## 4. Role Understanding

### Question 1

What is an AI Native Engineer?

Strong answer should include:

- Client problem discovery
- Compound AI systems
- Cloud-native delivery
- Evaluation
- Operations
- Trust and adoption

### Question 2

What makes forward-deployed engineering different?

Strong answer should include:

- Work close to clients
- Incomplete requirements
- Mixed architecture and implementation
- Fast feedback
- Client environment constraints
- Knowledge transfer
- Trusted-advisor behavior

### Question 3

How do you operate under ambiguity?

Strong answer should include:

- Stakeholders
- Current workflow
- Decision decomposition
- Evidence
- Risk
- Assumptions
- Success measures
- Thin slice

### Question 4

Why do AI prototypes fail to reach production?

Strong answer should include:

- No workflow ownership
- Poor data access
- No evaluation
- Missing authority controls
- Weak observability
- No operational owner
- No rollback
- Unclear value
- Adoption ignored

## 5. Agent Architecture

### Question 5

What is an enterprise agent?

Strong answer:

> A compound system in which models contribute interpretation and generation,
> while deterministic software controls identity, state, policy, retrieval,
> tools, evaluation, observability, and human governance.

### Question 6

What should remain deterministic?

Strong answer should include:

- Authorization
- State versions
- Legal transitions
- Budgets
- Retries
- Stops
- Approval validity
- Tool execution controls
- Audit lineage

### Question 7

How would you architect an incident-diagnostic agent?

Cover:

- Gateway
- Identity
- Runtime
- Policy
- Retrieval
- Provider adapter
- Validation
- Evaluation
- Traces
- Human review
- Recommendation-only initial scope

### Question 8

Why use a state machine?

Cover:

- Explicit lifecycle
- Legal transitions
- Testability
- Recovery
- Budgets
- Stop conditions
- Checkpoints
- Replay
- Auditability

### Question 9

How do you stop an agent from running indefinitely?

Cover:

- Step budget
- Retry budget
- Per-stage budget
- Deadline
- Terminal states
- Approval timeout
- Dependency timeout
- Cost limit
- Safe abstention

## 6. RAG and Context Engineering

### Question 10

Explain RAG without using buzzwords.

Target answer:

> RAG finds evidence relevant to the current request, filters it according to
> access policy, ranks and assembles it into bounded context, asks a model to
> produce a structured response, and preserves citations so the answer can be
> checked.

### Question 11

What is context engineering?

Cover:

- Instructions
- Request
- Identity
- Policy
- State
- Evidence
- Tools
- Output schema
- Token budget
- Safety constraints

### Question 12

How do you prevent cross-tenant retrieval?

Cover:

- Trusted tenant identity
- Metadata filters
- Source authorization
- Pre-retrieval or retrieval-time enforcement
- Negative tests
- Traceable policy decisions
- Fail closed

### Question 13

How do you evaluate retrieval?

Cover:

- Recall
- Precision
- Ranking
- Access correctness
- Citation support
- Freshness
- Latency
- Cost
- Representative queries

### Question 14

How do you handle insufficient evidence?

Cover:

- Thresholds
- Missing-source reasons
- Abstention
- Escalation
- Request for more evidence
- No fabricated certainty

## 7. Multi-Provider Platforms

### Question 15

How would you build a multi-provider abstraction?

Cover:

- Shared typed contract
- Provider adapters
- Capability metadata
- Policy
- Routing
- Error normalization
- Usage
- Telemetry
- Evaluation
- Fallback rules

### Question 16

Why not hide every provider difference?

Cover:

- Different tools
- Structured-output guarantees
- Safety controls
- Streaming
- Regions
- Context limits
- Governance
- Unique capabilities

### Question 17

How would you select between OpenAI, Claude, Vertex AI, and open-source models?

Cover:

- Task quality
- Capability
- Data policy
- Region
- Latency
- Cost
- Availability
- Operational ownership
- Evaluation evidence

### Question 18

What additional responsibility comes with open-source models?

Cover:

- License
- Serving
- GPU capacity
- Scaling
- Patching
- Batching
- Version rollout
- Safety
- Monitoring
- Cost utilization

## 8. Policy, Tools, and Approval

### Question 19

Can the model make an authorization decision?

Target answer:

> No. The model may classify context or recommend a route, but a deterministic
> policy service evaluates trusted identity, resource, action, environment, and
> risk attributes. The enforcement point applies the decision and records its
> lineage.

### Question 20

What is the difference between authentication and authorization?

Target answer:

> Authentication establishes who or what the actor is. Authorization decides
> whether that actor may perform a specific action on a specific resource under
> the current conditions.

### Question 21

How do you secure tool invocation?

Cover:

- Registry
- Allowlist
- Schema
- Policy
- Least privilege
- Approval
- Timeout
- Idempotency
- Result validation
- Evidence

### Question 22

Is function calling the same as tool execution?

Target answer:

> No. Function calling is a structured model-output format. Execution is a
> separate application decision requiring validation, identity, authorization,
> credentials, side-effect controls, and evidence.

### Question 23

How would human approval work?

Cover:

- Evidence presented
- Authorized approver
- Scope
- Reason
- Expiry
- Revocation
- Separation of duties
- Revalidation
- Audit lineage

## 9. Evaluation and Observability

### Question 24

How do you know an agent is accurate?

Cover:

- Define task-specific correctness
- Golden cases
- Component metrics
- End-to-end outcomes
- Human review
- Confidence intervals where appropriate
- Failure categories
- Regression comparison

### Question 25

Which metrics matter?

Cover:

- Task success
- Retrieval
- Groundedness
- Citations
- Policy
- Tools
- Safety
- Latency
- Cost
- Human correction

### Question 26

What is EvalOps?

Target answer:

> EvalOps is the operational discipline for versioning datasets, rubrics,
> evaluators, runs, thresholds, comparisons, regressions, and release evidence.

### Question 27

Explain logs, metrics, and traces.

Target answer:

> Logs record discrete events. Metrics quantify behavior over time. Traces
> connect the operations performed for one request across service boundaries.

### Question 28

What should not be logged?

Cover:

- Credentials
- Tokens
- Raw PHI or protected records
- Unbounded prompts
- Raw retrieved evidence
- Hidden reasoning
- Secrets
- Unnecessary personal data

### Question 29

How do evaluation and observability interact?

Cover:

- Shared correlation
- Version lineage
- Online quality
- Drift
- Failure analysis
- Cost
- Release comparison

## 10. Cloud-Native Engineering

### Question 30

What is the difference between Docker and Kubernetes?

Target answer:

> Docker packages and runs containers. Kubernetes schedules and manages
> containerized workloads, replicas, networking, rollout, and recovery.

### Question 31

What are health, readiness, and liveness?

Cover:

- Health as general service condition
- Readiness for receiving traffic
- Liveness for restart decisions
- Dependency behavior
- Avoid restart loops

### Question 32

When would you use microservices?

Cover:

- Bounded responsibility
- Ownership
- Independent scaling
- Release cadence
- Failure isolation
- Distributed-system cost

### Question 33

When would you use serverless?

Cover:

- Event-driven
- Intermittent
- Short-lived
- Managed scaling
- Cold starts
- Limits
- State
- Cost

### Question 34

Explain event-driven architecture.

Cover:

- Producers
- Consumers
- Events
- Queues or streams
- Decoupling
- Idempotency
- Ordering
- Dead-letter handling
- Replay
- Observability

### Question 35

What is the difference between Terraform and Helm?

Target answer:

> Terraform declaratively provisions infrastructure and records its state.
> Helm packages and releases templated Kubernetes resources.

### Question 36

What would your CI/CD gates include?

Cover:

- Dependency integrity
- Lint and formatting
- Types
- Unit and contract tests
- Evaluation
- Security scanning
- Container validation
- Infrastructure validation
- Deployment verification
- Rollback evidence

## 11. Production Readiness

### Question 37

What separates a prototype from production?

Cover:

- Operational owner
- Identity
- Security
- Evaluation
- SLO
- Scaling
- Recovery
- Telemetry
- Runbooks
- Rollback
- Cost
- Adoption

### Question 38

How do you handle provider failure?

Cover:

- Timeout
- Circuit breaker
- Bounded retry
- Policy-controlled fallback
- Queue or abstention
- User-visible status
- Evidence
- No unsafe provider substitution

### Question 39

How do you control cost?

Cover:

- Model routing
- Token budgets
- Context limits
- Caching
- Batching
- Retrieval limits
- Step budgets
- Cost telemetry
- Cost per successful task
- Release thresholds

### Question 40

How would you debug a quality incident?

Cover:

- Identify affected version
- Trace request
- Separate retrieval, model, policy, tool, and infrastructure
- Reproduce with checkpoint or case
- Compare baseline
- Contain
- Roll back
- Add regression case

## 12. Domain Questions

### Question 41

How would your design change for healthcare?

Cover:

- PHI
- Minimum necessary
- Consent
- Clinical review
- Provenance
- Audit
- FHIR
- No autonomous clinical judgment

### Question 42

How would it change for finance?

Cover:

- Entitlements
- Segregation of duties
- Audit
- Transaction evidence
- Approval
- Model risk
- Retention
- Nonrepudiation

### Question 43

How would it change for retail?

Cover:

- Catalog and inventory freshness
- Customer privacy
- Fraud
- Seasonal scale
- Low latency
- Interaction cost
- Exception approval

### Question 44

Which domain experience is strongest?

Honest answer:

> Healthcare is my strongest explicit regulated-domain experience. My finance
> connection includes accounting education, identity, audit, segregation of
> duties, and production controls, but I would not claim finance AI delivery
> without a specific engagement. Retail is an architecture exercise unless
> supported by separate experience.

## 13. Bonus Questions

### Question 45

What is a compound AI system?

Cover:

- Models
- Retrieval
- State
- Policy
- Tools
- Evaluation
- Observability
- Infrastructure
- Humans

### Question 46

What is an agent registry?

Cover:

- Discovery
- Owner
- Version
- Contract
- Tools
- Policy
- Data classification
- Evaluation
- Deployment status
- Deprecation

### Question 47

What is a stream-based agent architecture?

Cover:

- Lifecycle events
- Producers
- Consumers
- Partitions
- Ordering
- Idempotency
- Replay
- Schema evolution
- Audit and evaluation consumers

### Question 48

What does AI-native mean?

Target answer:

> AI-native architecture makes model capability a core part of the workflow
> while retaining cloud-native discipline. It optimizes context, model choice,
> evaluation, tools, and human governance without discarding APIs, identity,
> reliability, observability, deployment, rollback, or ownership.

### Question 49

How do you avoid framework lock-in?

Cover:

- Typed domain contracts
- Explicit state
- Provider adapters
- Tool schemas
- Evaluation datasets
- Trace conventions
- Separate orchestration semantics from framework API

## 14. Experience-Gap Questions

### Question 50

The role asks for seven years of AI-platform experience. Do you have that?

Honest answer:

> My direct AI platform architecture experience dates from approximately 2021,
> so I describe it as about five years rather than seven. I also bring more
> than fifteen years of adjacent cloud, security, integration, and production
> operations. I do not relabel those earlier years as AI experience, but they
> materially strengthen how I design identity, reliability, observability, and
> governance for AI platforms.

### Question 51

Do you have ten years of programming?

Honest answer:

> My career combines architecture, operations, security, and hands-on
> engineering. My current implementation work is in Python, FastAPI, Pydantic,
> testing, SQL, and API contracts. Earlier roles were more infrastructure and
> security focused, so I would rather demonstrate the systems and code I can
> explain than inflate a language-specific duration.

### Question 52

Have you deployed agents to production?

Answer requirements:

- Name only a real deployed system.
- State users and environment.
- State your operational responsibility.
- Separate architecture, POC, portfolio, and production.
- If production scope is limited, say so directly.

Safe answer:

> My strongest production depth is in carrier-grade infrastructure, regulated
> cloud, security, and operations. My AI work includes client-facing governed
> architecture and hands-on RAG, orchestration, evaluation, policy, and
> platform builds. I distinguish which examples were production deployments,
> which were prototypes, and which were independent portfolio systems.

### Question 53

Why should we consider you if a duration requirement is short?

Target answer:

> I would not claim years I do not have. The value I bring is the combination
> of current AI platform depth with mature production, cloud, identity,
> security, regulated-system, incident, and client architecture experience.
> That combination directly addresses the difficult part of enterprise agents:
> moving from useful model behavior to controlled operational systems.

## 15. Lab Walkthrough Questions

### Question 54

Why did you stop implementation after Phase 4?

Target answer:

> Phase 4 established the deterministic control plane: state, transitions,
> budgets, stops, checkpoints, concurrency, replay, traces, API boundaries,
> tests, containers, and CI. Before the interview I froze implementation and
> converted later phases into learning guides. That preserves verified evidence
> and avoids adding rushed provider, retrieval, tool, or deployment claims.

### Question 55

What is implemented?

Cover:

- Discovery
- Thin slice
- FastAPI
- Pydantic
- Seven contracts
- Runtime
- Tests
- Containers
- CI

### Question 56

What is not implemented?

Cover:

- Providers
- Enterprise RAG
- Tools
- Human approval execution
- Kubernetes
- Terraform for the lab
- Helm
- Cloud
- Production

### Question 57

What would you implement next?

Target answer:

> After the interview I would return to Phase 5 with a permission-aware RAG
> design. I would begin with synthetic evidence, identity and source contracts,
> access-filter tests, retrieval evaluation, citation validation, and explicit
> prompt-injection controls before connecting enterprise data.

## 16. Behavioral Questions

### Question 58

Tell me about an incident you handled.

Use:

- AT&T production example
- Impact
- Detection
- Fault isolation
- Communication
- Safe change
- Recovery
- Root cause
- Prevention

### Question 59

Tell me about regulated architecture.

Use:

- TruMind
- Healthcare
- Identity
- Segmentation
- Encryption
- Terraform
- Monitoring
- Audit evidence
- AI-ready trust boundaries

### Question 60

Tell me about influencing a roadmap.

Use:

- Client-facing Mansi example
- Competing stakeholders
- Risk
- Technical sequence
- Evidence
- Decision
- Adoption

### Question 61

Tell me about a failed CI run.

Use:

- Phase 3 dependency-lock failure
- Container health failure
- Root cause
- Remediation
- Exact-commit CI evidence
- Documentation correction

### Question 62

Tell me about changing course.

Use:

- Phase 4 completion
- Interview deadline
- Decision to freeze code
- Preserve evidence
- Create docs-only accelerator
- Post-interview resumption plan

## 17. Questions for the Interviewer

Ask three to five:

- How do forward-deployed engineers divide responsibility with platform teams
  and client engineers?
- What usually prevents a successful POC from reaching operational adoption?
- How are retrieval, model, tool, and end-to-end evaluations incorporated into
  release decisions?
- How does the team approach multi-provider architecture?
- What authority boundaries are expected for tool-executing agents?
- How are reusable patterns brought back from engagements?
- What would strong performance look like during the first ninety days?
- How is travel typically distributed across discovery, build, and operational
  phases?

## 18. Scoring Rubric

Score each answer from zero to three.

| Score | Meaning |
|---:|---|
| 0 | Unable to answer |
| 1 | Terminology without architecture or evidence |
| 2 | Clear architecture with some tradeoffs |
| 3 | Clear outcome, controls, tradeoffs, metrics, and truthful evidence |

Interview-ready target:

- No P0 question below 2
- Architecture questions average at least 2.5
- No fabricated experience
- Answers generally under two minutes unless asked for depth

## 19. Final Mock Sequence

Run this ninety-minute simulation:

1. Five-minute introduction
2. Ten-minute experience discussion
3. Twenty-minute architecture design
4. Fifteen-minute RAG and providers
5. Fifteen-minute policy, tools, and approval
6. Ten-minute evaluation and observability
7. Ten-minute cloud and production
8. Five-minute candidate questions

## 20. Mock Interview Gate

The mock is complete when:

- At least forty questions have been answered aloud.
- The architecture can be drawn without notes.
- The four core stories include measurable evidence.
- Duration gaps are answered honestly.
- Production and portfolio work are clearly separated.
- Three questions for the interviewer are prepared.
- Weak answers have been rewritten and repeated.
