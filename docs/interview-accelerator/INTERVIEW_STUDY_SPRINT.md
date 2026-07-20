# Interview Study Sprint — July 20–22, 2026

## 1. Objective

Prepare to discuss the AI Native Engineer role at 3:00 PM PDT on
July 22, 2026.

This sprint prioritizes explanation, architectural judgment, client
communication, and honest use of the lab as evidence.

It does not attempt to create thirteen production implementations in two days.

## 2. Success Criteria

Before the interview, the learner should be able to:

- Deliver a concise professional introduction
- Explain the target role through seven memorable pillars
- Walk through the repository from discovery to deterministic orchestration
- Draw a compound AI architecture without notes
- Explain RAG, tools, policies, evaluation, and observability
- Compare major model-provider integration concerns
- Explain the cloud-native path from API to production
- Adapt an agent workflow to finance, healthcare, and retail
- Lead a short simulated client-discovery conversation
- Explain tradeoffs instead of naming technologies without context
- Distinguish implemented evidence from design exercises
- Answer experience questions without inventing production experience

## 3. Priority Model

Use three priority levels.

| Priority | Meaning |
|---|---|
| P0 | Must be explainable before the interview |
| P1 | Important supporting depth |
| P2 | Learn after the interview if time expires |

### P0 topics

- Client discovery and ambiguity
- Agent versus workflow versus compound AI system
- RAG and context engineering
- Orchestration and state
- Provider abstraction
- Policy authority
- Tool safety
- Evaluation
- Observability
- Docker, Kubernetes, CI/CD, Terraform, and Helm
- Prototype versus production
- The lab's implemented evidence
- Honest shadow-experience framing

### P1 topics

- Human approval
- Serverless systems
- Event-driven architecture
- Agent and tool registries
- Stream-based architecture
- Domain adaptation
- Production incident handling
- Reusable enterprise patterns

### P2 topics

- Product-specific command memorization
- Framework-specific APIs
- Detailed provider pricing
- Advanced Kubernetes administration
- Full infrastructure implementation
- Full retrieval or tool implementation

## 4. July 20 — Foundation and Story

### Session 1 — Job-description compression

Target duration: 60 minutes.

Learn the seven pillars:

1. Discover the business problem.
2. Design a controlled agent workflow.
3. Integrate models, retrieval, policies, and tools.
4. Deliver through cloud-native engineering.
5. Measure accuracy, latency, safety, and cost.
6. Operate and debug the workflow.
7. Build client trust and reusable patterns.

Deliverable:

Explain the entire job in sixty seconds without reading.

### Session 2 — Existing lab evidence

Target duration: 75 minutes.

Review:

- Phase 1 discovery artifacts
- Phase 2 thin vertical slice
- Phase 3 FastAPI and Pydantic foundation
- Phase 4 deterministic runtime
- State transitions
- Budgets and stops
- Checkpoints and replay
- Trace evidence
- CI and container evidence
- Explicit authority exclusions

Deliverable:

Give a three-minute repository walkthrough that clearly separates implemented
behavior from planned behavior.

### Session 3 — Client discovery

Target duration: 75 minutes.

Practice:

- Identifying stakeholders
- Mapping the current workflow
- Finding the actual decision that needs support
- Defining risk and authority boundaries
- Selecting a thin vertical slice
- Writing acceptance criteria
- Defining success measures
- Recording assumptions

Deliverable:

Lead a ten-minute simulated discovery conversation for an incident-diagnostic
assistant.

### Session 4 — RAG and context engineering

Target duration: 90 minutes.

Learn:

- Retrieval-augmented generation
- Embeddings
- Chunking
- Metadata
- Hybrid search
- Reranking
- Context assembly
- Grounding
- Citation validation
- Access filtering
- Prompt-injection defenses
- Retrieval evaluation
- Abstention

Deliverable:

Explain a permission-aware evidence-retrieval pipeline from query to citation.

### Session 5 — End-of-day recall

Target duration: 30 minutes.

Without notes:

- Recite the seven pillars.
- Draw the lab architecture.
- Explain RAG in sixty seconds.
- Explain why Phase 4 contains no model.
- State three risks and three controls.

## 5. July 21 Morning — Architecture and Measurement

### Session 1 — Multi-provider abstraction

Target duration: 75 minutes.

Compare:

- OpenAI
- Anthropic
- Vertex AI
- Open-source models

Focus on:

- Common request contracts
- Provider adapters
- Capability differences
- Structured output
- Tool calling
- Streaming
- Safety settings
- Rate limits
- Timeouts
- Retries
- Failover
- Token and cost accounting
- Observability
- Vendor lock-in

Deliverable:

Draw a provider-neutral interface with provider-specific adapters.

### Session 2 — Evaluation and EvalOps

Target duration: 90 minutes.

Learn:

- Golden datasets
- Task success
- Retrieval recall and precision
- Groundedness
- Citation correctness
- Tool-selection accuracy
- Policy compliance
- Safety
- Latency percentiles
- Cost per successful task
- Regression testing
- Human review
- Model-based graders
- Online and offline evaluation

Deliverable:

Create an evaluation scorecard for the incident-diagnostic workflow.

### Session 3 — Observability

Target duration: 75 minutes.

Learn:

- Logs
- Metrics
- Traces
- Spans
- Correlation identifiers
- Context propagation
- Dashboards
- Alerts
- Service-level indicators
- Service-level objectives
- Sensitive-data redaction

Deliverable:

Explain how one request can be traced across gateway, runtime, retrieval,
provider, and tool boundaries.

## 6. July 21 Afternoon — Enterprise Controls and Cloud

### Session 4 — Policy, tools, and approval

Target duration: 90 minutes.

Learn the control sequence:

1. A model or workflow proposes an action.
2. Typed application code validates the proposal.
3. Deterministic policy evaluates identity, scope, resource, and operation.
4. Human approval is requested when required.
5. Approval scope and expiry are revalidated.
6. The tool executes with least privilege.
7. Results and side effects are validated.
8. Evidence is recorded.

Deliverable:

Explain why the model is never the authorization authority.

### Session 5 — Cloud-native delivery

Target duration: 105 minutes.

Learn:

- Containers
- Images
- Microservices
- Kubernetes Pods
- Deployments
- Services
- Health and readiness
- Serverless
- Queues
- Event streams
- CI/CD
- Terraform
- Helm
- Secrets
- Scaling
- Rollback
- Monitoring

Deliverable:

Explain how the local FastAPI prototype could move toward controlled cloud
deployment after the appropriate implementation gates.

### Session 6 — Prototype versus production

Target duration: 60 minutes.

Compare:

| Prototype question | Production question |
|---|---|
| Does the idea work? | Can the organization operate it safely? |
| Can one path succeed? | Are failures controlled across all important paths? |
| Does it run locally? | Can it scale, recover, and roll back? |
| Does the output look useful? | Is quality measured continuously? |
| Can a developer inspect it? | Can operators observe and support it? |
| Is access simulated? | Are identity and policy integrated? |
| Is state in memory? | Is state durable, recoverable, and governed? |

Deliverable:

Give a sixty-second answer explaining why a prototype is valuable but not
production evidence.

## 7. July 21 Evening — Bonus Knowledge and Stories

### Session 7 — Compound AI systems

Target duration: 60 minutes.

Mental model:

A compound AI system combines:

- One or more models
- Retrieval
- Context construction
- Deterministic orchestration
- Policies
- Tools
- State
- Memory
- Evaluation
- Observability
- Infrastructure
- Human governance

Deliverable:

Explain why enterprise agents are systems rather than prompts.

### Session 8 — Registries and streams

Target duration: 60 minutes.

Learn:

- Agent registry
- Tool registry
- Model registry
- Capability metadata
- Versioning
- Discovery
- Ownership
- Policy attachment
- Event streams
- Producers
- Consumers
- Topics
- Ordering
- Delivery guarantees
- Idempotency
- Replay
- Event sourcing

Deliverable:

Explain when registry-based or stream-based architecture becomes useful.

### Session 9 — Domain adaptation

Target duration: 75 minutes.

Prepare one scenario each for:

- Finance
- Healthcare
- Retail

For every scenario identify:

- User
- Decision
- Evidence
- Policy
- Risk
- Approval
- Metric
- Failure response

Deliverable:

Explain what changes across domains and what architectural controls remain
constant.

### Session 10 — Story preparation

Target duration: 75 minutes.

Prepare four honest stories:

1. Ambiguous request to bounded use case
2. Typed contracts and validation
3. Deterministic orchestration and failure controls
4. CI failure diagnosis and remediation

Use this structure:

- Situation
- Goal
- Constraints
- Decision
- Action
- Evidence
- Result
- Limitation
- Next production step

## 8. July 22 Morning — Retrieval Practice

### Session 1 — Closed-notes architecture

Target duration: 45 minutes.

Draw:

- Client or user
- Gateway
- Runtime
- Policy
- Retrieval
- Provider abstraction
- Tool boundary
- Evaluation
- Observability
- Checkpoint store
- Human approval

For each boundary explain:

- Input contract
- Output contract
- Authority
- Failure mode
- Evidence emitted

### Session 2 — Rapid definitions

Target duration: 45 minutes.

Explain each term in no more than two sentences:

- Agent
- Agentic workflow
- Compound AI
- Orchestration
- RAG
- Context engineering
- Embedding
- Reranking
- Grounding
- Policy routing
- Tool invocation
- Evaluation harness
- Observability
- Microservice
- Serverless
- Event-driven architecture
- CI/CD
- Infrastructure as code
- Terraform
- Helm
- Kubernetes
- Agent registry

### Session 3 — Mock interview

Target duration: 75 minutes.

Practice:

- Five architecture questions
- Five client-engagement questions
- Five operational questions
- Three experience-gap questions
- Three domain questions
- Questions for the interviewer

Record unclear or overlong answers for final review.

## 9. July 22 Final Review

### 1:30–2:00 PM PDT

Review only:

- Seven pillars
- Three strongest stories
- Architecture diagram
- Key metrics
- Authority boundaries
- Questions for the interviewer

### 2:00–2:30 PM PDT

Practice:

- Thirty-second introduction
- Sixty-second lab explanation
- One architecture tradeoff
- One client-ambiguity story
- One CI-debugging story

### 2:30–3:00 PM PDT

Stop studying.

- Prepare the interview environment.
- Check audio, camera, power, and network.
- Open the resume and job description.
- Keep a one-page mental-note sheet available.
- Enter the interview calm and early.

## 10. Experience-Gap Response

Do not apologize for not implementing Phases 5–17 before the interview.

Use an answer such as:

> I separated verified implementation from architectural planning. In the lab,
> I built and tested the discovery, contract, container, CI, and deterministic
> orchestration foundations. For retrieval, provider abstraction, tools,
> evaluation, observability, and production deployment, I created explicit
> designs and implementation gates rather than adding uncontrolled integrations.
> That reflects how I approach enterprise systems: establish contracts,
> authority, failure behavior, and evidence before expanding capability.

## 11. Questions for the Interviewer

Prepare questions such as:

- How does the team divide responsibility between forward-deployed engineers,
  platform teams, and client engineering teams?
- What typically separates a successful prototype from an engagement that
  reaches operational adoption?
- How are model, retrieval, and tool evaluations incorporated into delivery?
- How does the organization manage provider choice and multi-provider
  abstraction?
- What authority boundaries are expected for tool-executing workflows?
- How are reusable patterns brought back from client engagements without
  carrying client-specific assumptions?
- What would excellent performance look like during the first ninety days?

## 12. Sprint Gate

The sprint is complete when:

- All P0 topics can be explained without reading.
- The architecture can be drawn from memory.
- Four honest evidence-backed stories are prepared.
- The learner can distinguish design from implementation.
- At least one mock interview is completed.
- The final review stops by 2:30 PM PDT on July 22.
