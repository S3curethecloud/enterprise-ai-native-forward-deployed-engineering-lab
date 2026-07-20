# Shadow-Experience Scenarios

## 1. Purpose

These scenarios simulate forward-deployed AI engineering decisions.

They are designed to:

- Turn terminology into practical judgment
- Practice client conversations
- Connect existing professional experience to AI-native architecture
- Fill knowledge gaps without fabricating employment history
- Prepare concise interview explanations

A shadow scenario is a learning exercise, not a client engagement or
production deployment.

## 2. Required Disclosure

When discussing a scenario, label it accurately:

> This was a portfolio design exercise based on my professional experience in
> cloud, security, regulated systems, and AI platform architecture. It was not
> a production client deployment.

Never remove that distinction to make an answer sound stronger.

## 3. Scenario Structure

Every scenario contains:

## 1. Client context
## 2. Ambiguous request
## 3. Discovery questions
## 4. Proposed thin slice
## 5. Architecture
## 6. Authority boundary
## 7. Risks
## 8. Evaluation
## 9. Observability
## 10. Production requirements
## 11. Connection to real experience
## 12. Interview talking point

## 4. Scenario A — Financial Incident-Diagnostic Agent

### Evidence classification

> SIMULATED FINANCE CLIENT
> PORTFOLIO ARCHITECTURE EXERCISE
> NOT A PRODUCTION CLIENT DEPLOYMENT
Client context

A financial-services company experiences payment-service incidents. Engineers
search monitoring tools, runbooks, change records, ticket history, and service
ownership systems before recommending remediation.

The organization wants an agent to reduce diagnosis time.

Ambiguous request

Build an autonomous agent that finds the problem and fixes it.

Discovery questions
Who currently diagnoses incidents?
Which decisions consume the most time?
Which evidence sources are authoritative?
Which systems contain customer or transaction data?
How are engineers authorized?
Which actions change production?
Which actions require two-person approval?
What is the cost of an incorrect recommendation?
How is a recommendation reviewed?
What does successful diagnosis mean?
What evidence must be retained?
Bounded thin slice

The initial workflow should:

Validate the incident request.
validate identity and service scope.
Retrieve authorized read-only evidence.
Produce a citation-backed diagnostic summary.
Recommend a remediation.
Mark the recommendation not_executed.
Record trace and evaluation evidence.

It should not execute remediation.

Architecture
FastAPI gateway validates the request.
Deterministic runtime controls workflow state.
Identity context identifies tenant, user, and service scope.
Policy service evaluates read access.
Retrieval queries approved evidence sources.
Reranker prioritizes relevant evidence.
Provider adapter requests a structured diagnosis.
Response validator checks schema and citations.
Evaluation records groundedness and citation support.
Trace events connect the lifecycle.
Human engineer reviews the recommendation.
Authority boundary

The model may:

Summarize
Compare evidence
Identify hypotheses
Recommend next steps
Abstain

The model may not:

Grant data access
Change entitlements
Execute a rollback
Modify production
Approve its recommendation
Hide missing evidence
Finance controls
Segregation of duties
Strong identity
Service and tenant scoping
Read-only initial access
Immutable evidence
Approval lineage
Change-ticket linkage
Data retention
Nonrepudiation
Deny-by-default policy
Evaluation

Measure:

Diagnosis accuracy
Evidence recall
Citation correctness
Unsupported-claim rate
Abstention correctness
Time to useful recommendation
Policy-denial correctness
Cost per reviewed diagnosis
Observability

Trace:

Request admission
Identity validation
Policy decision
Retrieval query
Evidence count
Generation
Response validation
Human review
Final disposition

Do not log:

Credentials
Raw transaction data
Full protected evidence
Hidden model reasoning
Production requirements

Before deployment:

Integrate enterprise identity.
Integrate real policy enforcement.
Conduct threat modeling.
Build evaluation datasets.
Validate retention.
Add durable checkpoints.
Add telemetry backend.
Define SLOs.
Create runbooks.
Test disaster recovery.
Complete security and model-risk review.
Connection to real experience

Transferable evidence:

AT&T carrier-grade incident response
Fault isolation
Secure routing
Change management
Root-cause analysis
Identity and access controls
Accounting education
Audit and evidence orientation
Phase 4 deterministic runtime
Interview talking point

I have not represented this as a finance-client deployment. I used my
production incident, identity, audit, and deterministic-runtime experience to
model how a financial institution could introduce AI safely. The key design
decision was recommendation-only scope: the model can analyze authorized
evidence, but production mutation remains behind policy and human control.

## 5. Scenario B — Healthcare Intake and Charting Assistant
Evidence classification
> PROFESSIONAL HEALTHCARE EXPERIENCE
> PLUS PORTFOLIO AI ARCHITECTURE
> VERIFY DEPLOYMENT DETAILS BEFORE CLAIMING PRODUCTION AI USE
Client context

A behavioral-health organization wants to reduce documentation burden during
patient intake and clinical chart preparation.

Ambiguous request

Use AI to automate intake and write the chart.

Discovery questions
Which staff members perform intake?
Which information is patient-provided?
Which information comes from the EHR?
What requires clinical judgment?
Where is patient consent recorded?
What is the minimum necessary access?
Who may review and sign a chart?
What happens when the model is uncertain?
How are corrections recorded?
How long is data retained?
Which integrations use FHIR?
Bounded thin slice

The initial workflow should:

Capture or transcribe an authorized intake.
Extract structured draft fields.
Cite the source segment for each material fact.
Flag uncertainty or missing information.
Generate a chart draft.
Require clinician review and sign-off.
Record the approved correction history.
Prohibit autonomous diagnosis or treatment.
Architecture
Patient and clinician identity boundaries
Consent and purpose checks
Encrypted intake storage
Transcription service
Structured extraction
Clinical terminology normalization
EHR/FHIR adapter
Draft-generation provider
Validation
Clinician approval
Audit events
Evaluation and monitoring
Authority boundary

The assistant may:

Transcribe
Structure information
Draft documentation
Identify missing fields
Cite source statements

The assistant may not:

Make an autonomous diagnosis
Prescribe treatment
Sign the chart
Override the clinician
Access unrelated records
reuse PHI for an unrelated purpose
Healthcare controls
HIPAA-aligned handling
Minimum-necessary access
Consent
Encryption
Identity
Purpose limitation
Clinical review
Audit trail
Correction lineage
Retention and deletion
Safe escalation
Evaluation

Measure:

Field-extraction accuracy
Source support
Omission rate
Unsupported clinical statements
Clinician correction rate
Time saved
Review duration
Safety-event rate
PHI leakage
Cost per signed draft
Connection to real experience

Direct and adjacent evidence:

TruMind Psychiatry
HIPAA-aligned AWS and Azure architecture
EHR and healthcare applications
Identity and secure data flows
Zero trust
Terraform
Monitoring
AI-assisted psychiatry intake portfolio
EHR/FHIR integration patterns
Interview talking point

Healthcare is my strongest regulated-domain example. I would treat the AI
output as a draft, preserve source provenance, enforce minimum-necessary
access, and require clinician sign-off. My healthcare cloud experience gives
me the identity, segmentation, encryption, monitoring, and audit foundation;
I would state separately which AI components were portfolio architecture and
which were deployed professionally.

## 6. Scenario C — Retail Returns and Inventory Assistant
Evidence classification
> SIMULATED RETAIL CLIENT
> PORTFOLIO DESIGN EXERCISE
NO DIRECT RETAIL DELIVERY CLAIM
Client context

A retailer wants an assistant that helps store associates determine whether an
item can be returned and whether a replacement is available.

Ambiguous request

Give associates an AI agent that handles returns.

Discovery questions
What return policies apply?
Do policies differ by product, channel, geography, or customer tier?
Which data is authoritative?
What customer data is required?
Which fraud signals may be used?
Who can approve an exception?
Can the system issue refunds?
How fresh must inventory be?
What happens when services are unavailable?
Which outcomes should be measured?
Bounded thin slice

The initial workflow should:

Validate the associate and store.
Retrieve the current return policy.
Retrieve order and product context.
Retrieve inventory availability.
Explain the standard policy outcome.
Recommend an exception route when needed.
Require approval for refunds or overrides.
Record the evidence used.
Architecture
Associate identity
Customer-data minimization
Policy retrieval
Order API
Product catalog
Inventory API
Fraud-policy boundary
Deterministic routing
Explanation generation
Supervisor approval
Audit event
Authority boundary

The assistant may explain policy and recommend a route.

It may not:

Override fraud controls
Issue an unauthorized refund
expose unrelated customer data
invent inventory
ignore policy version
approve its own exception
Retail priorities
Low latency
Inventory freshness
Seasonal scale
Cost per interaction
Clear associate experience
Offline degradation
Fraud controls
Customer privacy
Evaluation

Measure:

Correct policy selection
Inventory freshness
Exception-routing accuracy
Supervisor override rate
Customer-data exposure
p95 latency
Cost per interaction
Associate completion time
Connection to real experience

Transferable evidence:

APIs
Identity
Policy controls
Distributed systems
High availability
Incident response
Cloud architecture
Agent workflow design
Interview talking point

Retail is a design exercise rather than a direct industry claim. I would
reuse the same control pattern—identity, authoritative evidence, policy,
deterministic routing, approval, and telemetry—but optimize more heavily for
latency, inventory freshness, seasonal scale, and interaction cost.

## 7. Scenario D — Multi-Provider AI Gateway
Evidence classification
> ARCHITECTURE AND PORTFOLIO SCENARIO
> PROVIDER-SPECIFIC IMPLEMENTATION MUST BE VERIFIED
Client context

An enterprise uses several model providers and wants to reduce application
coupling while retaining provider choice.

Ambiguous request

Build one API so every model is interchangeable.

Discovery questions
Which providers and models are approved?
Which capabilities are required?
Where may data be processed?
Which workloads are sensitive?
What are the latency and cost targets?
Is fallback allowed?
Which safety settings are mandatory?
How is provider performance evaluated?
What happens when a provider is unavailable?
Which provider-specific features must remain visible?
Proposed architecture
Provider-neutral request contract
Capability requirements
Deterministic router
Policy evaluation
OpenAI adapter
Anthropic adapter
Vertex AI adapter
Open-source serving adapter
Normalized usage and telemetry
Error classification
Evaluation store
Cost ledger
Circuit breaker
Fallback rules
Common contract

Normalize:

Messages
Structured-output requirement
Tool definitions
Timeout
Maximum output
Trace context
Data classification

Normalize results:

Content
Structured data
Tool requests
Usage
Latency
Finish reason
Provider
Model
Safety result
Error category
Preserve provider differences

Do not erase:

Tool semantics
Safety configuration
context limits
streaming events
regional features
data-governance options
model-specific capabilities
Evaluation

Compare:

Task success
Groundedness
Structured-output validity
Tool-call correctness
Latency
Cost
Safety
Availability
Interview talking point

I would not promise complete interchangeability. I would normalize the
stable operational contract—identity, policy inputs, request shape,
telemetry, usage, timeouts, and errors—while exposing capability metadata and
preserving provider-specific behavior. Evaluation and policy should drive
routing.

## 8. Scenario E — Tool-Executing Remediation Workflow
Evidence classification
> DESIGN EXERCISE
> CURRENT LAB TOOL EXECUTION REMAINS UNAUTHORIZED
Client context

An operations team wants the incident assistant to restart a service or roll
back a deployment.

Ambiguous request

Let the agent fix incidents automatically.

Risk decomposition

Separate actions:

Action	Risk
Read service metadata	Low
Read logs	Low to moderate
Create a draft ticket	Moderate
Submit a ticket	Moderate
Restart a test service	Moderate
Restart production	High
Roll back production	High
Change access policy	Critical
Trusted execution sequence
Model recommends an action.
Output is validated against a typed schema.
Identity and policy are evaluated.
Required approval is collected.
Approval scope and expiry are checked.
Current state is revalidated.
Tool executes with scoped credentials.
Result is validated.
Evidence is recorded.
Failure triggers a controlled stop.
Tool contract

Include:

Tool identifier
Version
Input schema
Output schema
Side-effect class
Required role
Required approval
Timeout
Retry policy
Idempotency key
Audit fields
Interview talking point

I separate recommendation, authorization, and execution. The model can
request a tool but cannot grant itself credentials or approval. Typed code
validates the request, deterministic policy evaluates authority, and
high-risk actions require scoped, expiring approval plus post-action
evidence.

## 9. Scenario F — Agent Registry and Event Stream
Evidence classification
> BONUS-KNOWLEDGE ARCHITECTURE EXERCISE
> NO PRODUCTION REGISTRY CLAIM
Client context

A large enterprise has many teams creating agents and tools. Capabilities are
difficult to discover, ownership is unclear, and lifecycle events are
inconsistent.

Agent registry

Record:

Agent identifier
Version
Owner
Business purpose
Input contract
Output contract
Required identity
Allowed data
Allowed tools
Policy reference
Evaluation status
Deployment status
Deprecation status
Tool registry

Record:

Tool identifier
Version
Owner
Side effects
Input schema
Output schema
Required scopes
Approval rules
Idempotency
Reliability status
Event stream

Publish lifecycle events such as:

Request admitted
Policy evaluated
Retrieval completed
Tool requested
Approval granted
Tool completed
Workflow stopped
Evaluation completed

Consumers may include:

Audit
Observability
Evaluation
Cost accounting
Security analytics
Workflow recovery
Architecture risks
Stale registry metadata
Schema incompatibility
Duplicate events
Event ordering
Unauthorized consumers
Sensitive event payloads
Orphaned ownership
Unreviewed agent versions
Interview talking point

A registry is a governance and discovery control plane, while the stream
carries lifecycle facts to decoupled consumers. I would require versioned
contracts, ownership, policy metadata, evaluation status, idempotent
consumers, schema evolution, and strict payload minimization.

## 10. Scenario G — Forward-Deployed Discovery Workshop
Evidence classification
> SIMULATED CLIENT WORKSHOP
> BASED ON REAL CLIENT-FACING ARCHITECTURE PRACTICES
Workshop objective

Reduce an ambiguous AI request into a valuable, measurable, low-risk slice.

Opening

Before selecting a model or framework, I would like to understand the
decision we are improving, the people involved, the evidence they use, and
the consequences of a wrong action.

Workshop sequence
Identify stakeholders.
Map the current workflow.
Identify decisions and handoffs.
Inventory evidence sources.
Identify identity and authority.
Identify failure consequences.
Record assumptions.
Define success measures.
Choose the initial slice.
Agree on exclusions.
Define acceptance criteria.
Assign owners and next steps.
Difficult client statement

We need autonomous remediation in six weeks.

Trusted-advisor response

We can design toward greater automation, but I would first separate diagnosis,
recommendation, approval, and execution. A read-only diagnostic slice can
validate evidence quality and workflow value without introducing production
mutation. The results will tell us where automation is justified and which
controls are required.

Interview talking point

Forward-deployed work requires making ambiguity visible. I use workshops to
produce concrete artifacts—workflow, decision, evidence, risk, assumptions,
success measures, and a bounded slice—so engineering begins from shared
decisions rather than untested expectations.

## 11. Scenario Comparison
Scenario	Strongest real foundation	Primary learning gap
Finance incident agent	Carrier operations, identity, audit	Direct finance AI delivery
Healthcare charting	Healthcare cloud and security	Verify AI deployment maturity
Retail returns	APIs, policy, distributed systems	Direct retail delivery
Multi-provider gateway	Multi-cloud and AI architecture	Provider-specific implementation proof
Tool remediation	Identity, policy, orchestration	Executable tool integration
Registry and streams	Control planes and events	Production agent registry
Discovery workshop	Client-facing architecture	Prepare measurable workshop outcomes
## 12. Shadow-Experience Interview Formula

Use:

This was a [portfolio design exercise or implemented lab], not a production
client deployment. I used my experience in [real professional domains] to
model [specific architecture]. The key decision was [tradeoff]. I validated
[implemented evidence], while [unimplemented capability] remains a future
gated step.

## 13. Learning Gate

The scenarios are interview-ready when:

Every scenario is labeled accurately.
Each has a clear user and decision.
Each separates recommendation from authority.
Each includes evaluation and observability.
Domain-specific controls are identifiable.
Production requirements are explicit.
The learner can explain three scenarios without notes.
No scenario is presented as employment history.
