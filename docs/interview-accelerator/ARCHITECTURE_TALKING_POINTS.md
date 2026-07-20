# AI-Native Architecture Talking Points

## 1. Purpose

This guide provides concise explanations for architecture interviews.

Use it to practice:

- Thirty-second answers
- Sixty-second answers
- Three-minute architecture walkthroughs
- Tradeoff discussions
- Whiteboard explanations
- Client-facing explanations

## 2. Architecture in One Sentence

A governed compound AI workflow combines typed APIs, identity, deterministic
orchestration, policy, permission-aware retrieval, model-provider adapters,
controlled tools, evaluation, observability, durable state, and human approval.

## 3. Architecture Layers

| Layer | Responsibility |
|---|---|
| Experience | User interface, channel, or client application |
| Gateway | Authentication context, request validation, correlation, rate control |
| Runtime | State, transitions, budgets, retries, stops, checkpoints |
| Policy | Deterministic authorization and routing |
| Retrieval | Authorized evidence discovery and context construction |
| Provider abstraction | Controlled access to model providers |
| Tools | Typed external capabilities and side effects |
| Human control | Review, approval, escalation, and override |
| Evaluation | Quality, safety, latency, and cost measurement |
| Observability | Logs, metrics, traces, and operational evidence |
| Platform | Containers, Kubernetes, CI/CD, secrets, storage, and networking |

## 4. End-to-End Request Walkthrough

Explain the workflow in this order:

1. A user submits a diagnostic request.
2. The gateway validates the request and establishes correlation.
3. Identity context identifies the user, tenant, role, and service scope.
4. Deterministic policy evaluates whether processing is allowed.
5. The runtime records the state and enforces budgets.
6. Retrieval finds only evidence the identity may access.
7. Context engineering selects and organizes relevant evidence.
8. A provider adapter sends a structured request to an approved model.
9. The model produces a recommendation or abstention.
10. Response validation checks schema, citations, and invariants.
11. Evaluation records quality, policy, safety, latency, and cost.
12. Trace evidence records the lifecycle.
13. A human reviews the recommendation.
14. No remediation executes unless a later trusted-execution boundary is
    separately authorized.

## 5. Thirty-Second Architecture Answer

> I would design the agent as a compound system rather than a model call. A
> typed gateway validates requests, a deterministic runtime controls state and
> failure behavior, policy controls authority, permission-aware retrieval
> supplies evidence, and provider adapters isolate model integrations. Tools
> remain behind typed authorization and approval boundaries. Evaluation and
> telemetry measure quality, safety, latency, and cost across the lifecycle.

## 6. Sixty-Second Architecture Answer

> The workflow begins with identity, validation, and correlation at the API
> boundary. A deterministic runtime owns state, legal transitions, budgets,
> retries, checkpoints, and stop conditions. Policy evaluates whether the
> identity may access the service and data. Retrieval then finds authorized
> evidence, which is reranked and assembled into bounded context. A provider
> adapter invokes an approved model using a structured-output contract. The
> result is checked for schema validity, citations, policy compliance, and
> unsupported claims. Tools are separate typed capabilities and cannot execute
> merely because the model requested them. Every step emits evaluation and
> trace evidence. High-risk outcomes require human review, and production
> mutation remains outside the initial diagnostic slice.

## 7. Three-Minute Architecture Walkthrough

### Business boundary

Start with:

- User
- Decision
- Evidence
- Risk
- Success measure

Do not start with the model.

### Admission boundary

Explain:

- Authentication context
- Request validation
- Correlation
- Rate limits
- Idempotency
- Controlled errors

### Runtime boundary

Explain:

- Immutable state
- Legal transitions
- Step budget
- Retry budget
- Stop conditions
- Checkpoints
- Concurrency
- Replay

Lab evidence:

- Thirteen states
- Twenty-five transitions
- Sixteen-step maximum
- Two total retries
- One retry per stage
- Five terminal states
- Append-only checkpoints
- Optimistic version checks
- Deterministic replay

### Authority boundary

Explain:

- Identity does not equal authorization.
- The model is not a policy engine.
- Policy uses explicit attributes.
- Denial is fail-closed.
- Approval has scope and expiry.
- Tools receive least-privilege credentials.

### Evidence boundary

Explain:

- Source access
- Ingestion
- Chunking
- Metadata
- Retrieval
- Filtering
- Reranking
- Context assembly
- Citation validation
- Freshness
- Deletion

### Model boundary

Explain:

- Provider adapter
- Capability selection
- Structured output
- Timeout
- Error normalization
- Usage
- Cost
- Safety settings
- Model and prompt version

### Tool boundary

Explain:

- Registry
- Typed contract
- Side-effect class
- Authorization
- Approval
- Idempotency
- Timeout
- Result validation
- Audit evidence

### Measurement boundary

Explain:

- Retrieval quality
- Groundedness
- Citation correctness
- Task success
- Tool correctness
- Policy compliance
- Latency
- Safety
- Cost

### Operations boundary

Explain:

- Logs
- Metrics
- Traces
- Alerts
- SLOs
- Runbooks
- Rollback
- Incident response
- Ownership

## 8. Whiteboard Drawing Order

Draw components in this sequence:

1. User
2. Gateway
3. Runtime
4. Policy
5. Retrieval
6. Provider adapter
7. Tool boundary
8. Human approval
9. Evaluation
10. Observability
11. Durable stores
12. Cloud platform

For every arrow, be ready to state:

- Input
- Output
- Identity
- Authority
- Timeout
- Failure behavior
- Evidence

## 9. Why FastAPI

Plain English:

FastAPI provides an HTTP service boundary for typed Python applications.

Usefulness:

- Request validation
- Response validation
- Dependency injection
- OpenAPI
- Async support
- Controlled errors
- Test clients
- Clear endpoint contracts

Interview answer:

> I use FastAPI to make service boundaries executable and inspectable. It
> exposes the HTTP contract, while Pydantic enforces the data invariants. The
> framework does not provide enterprise authority by itself; identity, policy,
> state, telemetry, and operational controls still need explicit design.

## 10. Why Pydantic

Plain English:

Pydantic converts data expectations into executable validation rules.

Usefulness:

- Typed contracts
- Required fields
- Enum restrictions
- Numeric bounds
- Timestamp validation
- Immutable models
- Unknown-field rejection
- Nested validation
- JSON Schema

Interview answer:

> Pydantic lets me move contract assumptions into code. Invalid states and
> payloads fail at the boundary instead of flowing deeper into the workflow.
> That is especially useful for agent systems because model and tool outputs
> are untrusted until validated.

## 11. Why Deterministic Orchestration

A model should not own:

- Workflow authority
- State version
- Retry count
- Step budget
- Authorization
- Approval
- Terminal-state rules

Interview answer:

> I use probabilistic models for interpretation and generation, but
> deterministic software for authority and lifecycle control. That makes
> transitions, retries, stops, checkpoints, and failures testable.

## 12. RAG Talking Points

### Weak explanation

> RAG puts documents in a vector database and sends them to an LLM.

### Strong explanation

> RAG is an evidence pipeline. It governs source access, ingestion, chunking,
> metadata, indexing, query construction, retrieval, policy filtering,
> reranking, context assembly, citations, freshness, deletion, and evaluation.

### Key tradeoffs

| Decision | Tradeoff |
|---|---|
| Small chunks | Precise retrieval but less context |
| Large chunks | More context but lower retrieval precision |
| Vector search | Semantic matching but approximate results |
| Keyword search | Exact terms but weaker semantic matching |
| Hybrid search | Better coverage but more complexity |
| More context | More evidence but higher cost and distraction |
| Aggressive reranking | Better selection but added latency |
| Low abstention | More answers but more unsupported claims |

## 13. Context Engineering Talking Points

Context includes:

- Instructions
- User request
- Identity
- Policy decision
- Runtime state
- Retrieved evidence
- Tool definitions
- Tool results
- Output schema
- Token budget
- Safety constraints

Interview answer:

> Prompt engineering focuses on the instruction. Context engineering manages
> the complete information environment available at a workflow step, including
> identity, policy, state, evidence, tools, schemas, and budget.

## 14. Multi-Provider Talking Points

### Why use multiple providers

- Capability
- Availability
- Regional control
- Cost
- Latency
- Governance
- Negotiating leverage
- Risk reduction

### What to normalize

- Request contract
- Response envelope
- Errors
- Usage
- Latency
- Tracing
- Timeouts
- Retry categories

### What not to erase

- Tool behavior
- Structured-output guarantees
- Streaming
- Safety controls
- Context limits
- Data governance
- Unique model capabilities

Interview answer:

> The abstraction should reduce application coupling without pretending the
> providers are identical. Capability metadata and evaluation results need to
> remain visible to routing.

## 15. Policy Routing Talking Points

Policy inputs:

- Subject
- Role
- Tenant
- Resource
- Action
- Data classification
- Risk
- Environment
- Approval
- Time

Policy outputs:

- Allow
- Deny
- Require approval
- Restricted route
- Reason code
- Decision identifier
- Expiry

Interview answer:

> The model may classify context or recommend a route, but an external
> deterministic policy service makes the authorization decision and records
> its lineage.

## 16. Tool-Use Talking Points

Tool execution sequence:

1. Model proposes.
2. Schema validates.
3. Policy authorizes.
4. Human approves when required.
5. Current state is revalidated.
6. Scoped credentials are issued.
7. Tool executes.
8. Result validates.
9. Evidence records.
10. Failure stops safely.

Interview answer:

> Function calling is only a request format. Enterprise tool use requires
> identity, authorization, least privilege, idempotency, timeout, side-effect
> controls, result validation, and audit evidence.

## 17. Evaluation Talking Points

Measure separately:

| Layer | Example metrics |
|---|---|
| Retrieval | Recall, precision, ranking, access correctness |
| Generation | Groundedness, citation correctness, task quality |
| Policy | Allow and deny correctness |
| Tools | Selection, arguments, execution outcome |
| Safety | Prohibited behavior and data leakage |
| Performance | p50, p95, p99 latency |
| Cost | Cost per successful task |
| End to end | Accepted outcome and human correction |

Interview answer:

> A plausible answer is not enough. I want component metrics and end-to-end
> task success so I can identify whether a regression came from retrieval,
> generation, policy, tools, or infrastructure.

## 18. Observability Talking Points

Logs answer:

- What event occurred?

Metrics answer:

- How much, how often, or how fast?

Traces answer:

- How did this request travel through the system?

Profiles answer:

- Which code consumed the resources?

Interview answer:

> For an agent workflow, I correlate admission, policy, retrieval, model,
> tool, validation, and delivery spans under one trace. I record references and
> reason codes, not credentials, raw protected data, or hidden reasoning.

## 19. Docker and Kubernetes Talking Points

Docker:

- Packages the application
- Creates repeatable images
- Defines runtime user and dependencies
- Supports local and CI execution

Kubernetes:

- Schedules containers
- Maintains desired replicas
- Routes service traffic
- Manages rollout and recovery
- Applies configuration and policy
- Supports autoscaling

Mental note:

> Docker packages. Kubernetes orchestrates.

## 20. Terraform and Helm Talking Points

Terraform:

- Provisions infrastructure
- Uses providers and resources
- Creates a plan
- Applies desired state
- Tracks infrastructure state

Helm:

- Packages Kubernetes manifests
- Templates environment-specific values
- Manages releases
- Supports upgrades and rollback

Mental note:

> Terraform builds the environment. Helm installs the Kubernetes application.

## 21. Serverless Talking Points

Use when:

- Work is event-driven
- Load is intermittent
- Steps are short-lived
- Managed scaling is valuable

Consider:

- Cold starts
- Execution limits
- State
- Networking
- Observability
- Cost
- Vendor coupling

## 22. Event-Driven Talking Points

Benefits:

- Loose coupling
- Asynchronous work
- Independent scaling
- Replay
- Multiple consumers

Risks:

- Duplicates
- Ordering
- Schema evolution
- Poison messages
- Backpressure
- Delayed failure
- Harder debugging

Interview answer:

> Event-driven does not remove coordination; it changes coordination. I need
> idempotent consumers, correlation, schema governance, dead-letter handling,
> and observable delivery semantics.

## 23. Agent Registry Talking Points

An agent registry records:

- Identity
- Version
- Owner
- Purpose
- Contract
- Allowed tools
- Required policy
- Data classification
- Evaluation status
- Deployment status

Interview answer:

> A registry is valuable when many teams create capabilities. It supports
> discovery, ownership, policy attachment, compatibility, evaluation evidence,
> and lifecycle governance.

## 24. Prototype Versus Production

| Prototype | Production |
|---|---|
| Tests feasibility | Supports an operational commitment |
| Exercises a thin path | Covers important failure paths |
| May use local state | Requires durability and recovery |
| May use synthetic data | Requires governed data access |
| Demonstrates value | Measures continuing value |
| Developer-operated | Has operational ownership |
| Limited threat model | Security-reviewed |
| Manual release | Controlled release and rollback |
| Small load | Capacity and scaling evidence |

Interview answer:

> A prototype reduces uncertainty. Production readiness requires evidence that
> the organization can secure, operate, observe, recover, and improve the
> system under real constraints.

## 25. Client-Workshop Talking Points

Open with:

> What decision or workflow outcome are we trying to improve?

Then ask:

- Who performs it?
- What evidence do they use?
- Where is time lost?
- What can go wrong?
- Who has authority?
- What must remain human?
- How will success be measured?
- What is the smallest valuable slice?

Close with:

- Shared problem statement
- Current workflow
- Assumptions
- Risks
- Initial slice
- Acceptance criteria
- Owners
- Next decision

## 26. Tradeoff Vocabulary

Use phrases such as:

- The benefit is...
- The corresponding cost is...
- This optimizes for...
- This introduces...
- The failure mode is...
- I would mitigate that by...
- I would measure...
- I would defer...
- The authority remains with...
- The evidence required is...

Avoid presenting every technology as universally correct.

## 27. Honest Lab Boundary

Implemented:

- Discovery
- Thin vertical slice
- Typed FastAPI and Pydantic contracts
- Deterministic runtime
- Budgets and stops
- Checkpoints and replay
- CT-07 traces
- CI and containers

Not implemented:

- External model providers
- Enterprise retrieval
- Tool execution
- Human approval execution
- Kubernetes
- Terraform for this application
- Helm
- Cloud deployment
- Production deployment

## 28. Closing Interview Position

> My differentiator is the combination of production infrastructure,
> regulated cloud, security and identity, client-facing architecture, and
> hands-on AI platform engineering. I approach agent systems as governed
> distributed systems: models add reasoning capability, while contracts,
> orchestration, policy, evaluation, observability, and cloud operations make
> the workflow trustworthy and supportable.

## 29. Learning Gate

This guide passes when the learner can:

- Draw the architecture without notes.
- Explain every boundary.
- State who has authority at every step.
- Explain RAG beyond vector search.
- Explain provider abstraction tradeoffs.
- Explain tool execution safely.
- Define evaluation and observability signals.
- Distinguish a prototype from production.
- Connect the architecture to real professional evidence.
- State the lab's limitations without weakening the overall story.
