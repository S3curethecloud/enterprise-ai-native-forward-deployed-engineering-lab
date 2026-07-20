# Phase 5 — Permission-Aware RAG Design

## 1. Decision

Phase 5A is authorized for design, contract planning, threat modeling,
synthetic-data planning, and test planning.

Executable retrieval is not yet authorized.

Current decision:

- Phase 5A design work: Authorized
- Phase 5B contract implementation: Not yet authorized
- Retrieval execution: Not yet authorized
- External embedding providers: Not authorized
- External model providers: Not authorized
- Enterprise data: Not authorized
- Production data: Not authorized
- Tool execution: Not authorized
- Infrastructure mutation: Not authorized
- Cloud deployment: Not authorized
- Production deployment: Not authorized

## 2. Objective

Retrieve useful evidence without exposing unauthorized information.

The Phase 5 capability must eventually guarantee:

- Authorized evidence is retrievable.
- Unauthorized evidence never enters model context.
- Citations identify source and version.
- Insufficient evidence causes abstention or clarification.
- Retrieval quality and permission correctness are tested independently.
- Retrieved content is treated as untrusted input.
- Evidence freshness and deletion are enforceable.

## 3. Business Workflow

The incident-diagnostic workflow needs evidence from sources such as:

- Service catalog
- Approved runbooks
- Change records
- Incident history
- Deployment metadata
- Observability summaries

The initial implementation will use synthetic local evidence representing those
source types.

It will not connect to enterprise systems.

## 4. Core Authority Principle

Retrieval relevance does not create retrieval authority.

A document may be highly relevant and still be prohibited.

The required order is:

1. Establish trusted identity context.
2. Establish tenant and service scope.
3. evaluate retrieval policy.
4. Restrict eligible sources and records.
5. Perform retrieval within that authorized set.
6. Rerank only authorized candidates.
7. Construct model context only from authorized evidence.
8. Record source and policy lineage.

The model, query text, embedding similarity, and reranker do not grant access.

## 5. Initial Bounded Slice

The first executable retrieval slice should eventually:

1. Accept a validated diagnostic request.
2. Accept validated identity context.
3. Load a versioned synthetic evidence corpus.
4. enforce tenant and service filters.
5. Run deterministic keyword retrieval.
6. Return typed evidence candidates.
7. Return citations containing source and version.
8. Abstain when evidence is insufficient.
9. Emit retrieval evidence and reason codes.

The initial slice will not use embeddings.

Deterministic keyword retrieval comes first so contracts, authorization,
citations, abstention, and evaluation can be proven before semantic-search
complexity is introduced.

## 6. Proposed Subphases

| Subphase | Scope | Authority |
|---|---|---|
| 5A | Design, authority, threat model, and test plan | Authorized |
| 5B | Source, document, chunk, metadata, citation, and result contracts | Pending |
| 5C | Synthetic corpus and deterministic keyword retrieval | Pending |
| 5D | Tenant, service, and classification filtering | Pending |
| 5E | Local deterministic embeddings and vector retrieval | Pending |
| 5F | Hybrid retrieval and reranking | Pending |
| 5G | Context construction and token budgets | Pending |
| 5H | Prompt-injection and retrieval-contamination controls | Pending |
| 5I | Citation validation and controlled abstention | Pending |
| 5J | Retrieval evaluation and lifecycle telemetry | Pending |
| 5K | Runtime API, container, and CI integration | Pending |
| 5L | Tutorial, evidence, gate, and closure | Pending |

## 7. Source Taxonomy

### Service catalog

Purpose:

- Identify service ownership
- Identify environment
- Identify dependencies
- Identify criticality
- Identify approved support contacts

### Runbooks

Purpose:

- Provide approved diagnostic procedures
- Provide known failure signatures
- Provide bounded remediation recommendations
- Identify escalation paths

### Change records

Purpose:

- Identify recent deployments and configuration changes
- Connect incidents to change windows
- Identify change owner and version

### Incident history

Purpose:

- Identify prior similar symptoms
- Identify previously validated root causes
- Identify prior remediation outcomes

### Observability summaries

Purpose:

- Provide bounded metric, log, and trace findings
- Avoid unrestricted raw telemetry ingestion
- Preserve time window and source references

## 8. Proposed Data Model

### Evidence source

Represents the authoritative system or synthetic source collection.

Required concepts:

- Source identifier
- Source type
- Owner
- Authority classification
- Tenant scope
- Service scope
- Freshness policy
- Retention policy
- Version

### Evidence document

Represents one versioned source artifact.

Required concepts:

- Document identifier
- Source identifier
- Version
- Title
- Content
- Tenant identifier
- Service identifiers
- Data classification
- Effective time
- Expiry time
- Content hash
- Ingestion time
- Deletion status

### Evidence chunk

Represents a bounded retrieval unit.

Required concepts:

- Chunk identifier
- Document identifier
- Document version
- Chunk index
- Content
- Content hash
- Token estimate
- Metadata
- Authorization attributes

### Retrieval query

Represents a typed evidence request.

Required concepts:

- Request identifier
- Trace identifier
- Tenant identifier
- Service identifier
- Query text
- Allowed source types
- Time window
- Maximum candidates
- Minimum score
- Policy decision identifier

### Retrieval candidate

Represents one authorized candidate.

Required concepts:

- Chunk identifier
- Document identifier
- Source identifier
- Source version
- Score
- Rank
- Retrieval method
- Content hash
- Citation
- Authorization lineage

### Citation

Represents a verifiable reference.

Required concepts:

- Source identifier
- Document identifier
- Document version
- Chunk identifier
- Content hash
- Locator
- Retrieved time

## 9. Authorization Model

Authorization inputs:

- Subject identifier
- Tenant identifier
- Role
- Service identifier
- Environment
- Source type
- Document classification
- Requested operation
- Policy version
- Current time

Authorization outcomes:

- Allow
- Deny
- Require clarification
- Require approval in a later phase

The initial Phase 5 slice supports allow and deny only.

Any missing, expired, or inconsistent authorization input results in denial.

## 10. Filter-Then-Retrieve Versus Retrieve-Then-Filter

### Filter then retrieve

Restrict the searchable corpus before scoring.

Benefits:

- Unauthorized records are not scored.
- Unauthorized content is less likely to enter caches or intermediate results.
- Easier authority reasoning.

Costs:

- Search infrastructure must support metadata and policy filtering.
- Complex policies may affect performance.

### Retrieve then filter

Search broadly and discard unauthorized results afterward.

Risks:

- Unauthorized material may enter intermediate processing.
- Side-channel information may leak through counts, scores, or latency.
- Rerankers may receive prohibited content.
- Caches may retain unauthorized results.

Phase 5 decision:

Use filter-then-retrieve for the bounded implementation.

Defense in depth may also revalidate candidates after retrieval.

## 11. New Terminology

### Pre-filtering

Applying access and metadata restrictions before similarity or relevance
scoring.

### Post-filtering

Removing disallowed results after initial retrieval.

Post-filtering is defense in depth, not the primary access-control mechanism.

### Security trimming

Restricting search results to content the current identity is authorized to
access.

### Authority-bearing metadata

Metadata used in an authorization decision, such as tenant, service, owner,
classification, and environment.

This metadata must come from trusted ingestion or policy-controlled sources.

### Evidence provenance

The source, version, transformation, and retrieval lineage of evidence.

### Content hash

A deterministic digest used to identify the exact evidence content.

A content hash supports integrity and replay; it does not prove the source is
truthful.

### Tombstone

A record indicating that a document or version has been deleted or invalidated
and must not be returned.

### Freshness window

The maximum acceptable age of evidence for a particular decision.

### Retrieval contamination

Incorrect, malicious, stale, unauthorized, or misleading content entering the
retrieval corpus or result set.

### Retrieval leakage

Unauthorized information exposed through content, metadata, scores, counts,
timing, caches, logs, or error messages.

## 12. Chunking Strategy

The initial deterministic slice should use structure-aware chunks.

Boundaries may follow:

- Headings
- Runbook steps
- Incident sections
- Change-record fields
- Service-catalog records

Each chunk must preserve:

- Parent document
- Document version
- Source
- Section locator
- Authorization attributes
- Content hash

Chunking must not separate content from the metadata required to authorize or
cite it.

## 13. Retrieval Methods

### Deterministic keyword retrieval

First implementation method.

Purpose:

- Prove contracts
- Prove authorization
- Prove citations
- Prove abstention
- Create a reproducible baseline

### Vector retrieval

Later local implementation.

Purpose:

- Improve semantic matching
- Recover evidence with different wording

Requirements:

- Deterministic or versioned embedding model
- Embedding version
- Index version
- Reproducible evaluation
- No external provider initially

### Hybrid retrieval

Later combination of lexical and semantic results.

Requires:

- Score normalization
- Merge strategy
- Duplicate handling
- Versioned configuration
- Evaluation against the keyword baseline

### Reranking

Later second-stage ordering of authorized candidates.

The reranker must never receive unauthorized candidates.

## 14. Context Construction

Context construction is a later subphase.

The context bundle should contain:

- Request summary
- Identity and policy references
- Ordered evidence
- Citation identifiers
- Source versions
- Evidence hashes
- Token estimates
- Truncation evidence
- Insufficiency reasons

The context builder must enforce:

- Maximum evidence count
- Maximum per-source contribution
- Maximum token estimate
- Required source diversity where applicable
- Stable ordering
- No unauthorized evidence
- No tombstoned evidence
- Freshness requirements

## 15. Prompt-Injection Boundary

Retrieved content is untrusted data.

It must not:

- Override system instructions
- Change policy
- Grant tool access
- Change tenant scope
- Request secrets
- Disable evaluation
- Suppress citations
- Alter runtime budgets

Potential controls:

- Source trust classification
- Ingestion scanning
- Instruction-like content detection
- Context labeling
- Model instructions distinguishing data from authority
- Result validation
- Adversarial evaluation
- Human review

Deterministic policy remains authoritative even if retrieved content instructs
otherwise.

## 16. Abstention Model

The workflow should abstain when:

- No authorized evidence exists.
- Evidence is below the relevance threshold.
- Evidence is stale.
- Required source types are missing.
- Sources materially conflict.
- Citation support cannot be established.
- Authorization lineage is missing.
- Retrieval integrity fails.

Abstention evidence should contain:

- Reason code
- Sources searched
- Authorized-source count
- Candidate count
- Missing requirement
- Suggested clarification or escalation

It must not reveal prohibited source names or counts that create leakage.

## 17. Threat Model

| Threat | Initial control |
|---|---|
| Cross-tenant retrieval | Trusted tenant filter before retrieval |
| Service-scope bypass | Required service authorization |
| Malicious document instructions | Treat content as untrusted data |
| Stale evidence | Freshness and expiry checks |
| Deleted evidence returned | Tombstones and deletion tests |
| Citation mismatch | Content hash and locator validation |
| Metadata tampering | Trusted ingestion and immutable models |
| Retrieval-result leakage | Bounded errors and telemetry |
| Cache leakage | Tenant-aware cache keys or no cache initially |
| Reranker exposure | Rerank authorized candidates only |
| Corpus poisoning | Source allowlist and ingestion evidence |
| Denial of service | Candidate, content, and query limits |

## 18. Evaluation Plan

Permission correctness and retrieval quality are separate test dimensions.

### Permission evaluation

Test:

- Correct tenant allow
- Cross-tenant deny
- Correct service allow
- Wrong-service deny
- Classification deny
- Missing policy deny
- Expired policy deny
- Tombstoned-document deny
- No unauthorized metadata leakage

### Retrieval-quality evaluation

Measure:

- Recall at K
- Precision at K
- Mean reciprocal rank
- Citation correctness
- Freshness correctness
- Abstention correctness
- Query latency
- Candidate count
- Context token estimate

### Adversarial evaluation

Test:

- Prompt injection in evidence
- Misleading metadata
- Duplicate documents
- Conflicting sources
- Extremely long chunks
- Malformed timestamps
- Content-hash mismatch
- Unauthorized high-relevance evidence

## 19. Lifecycle Evidence

Proposed retrieval events:

- Retrieval requested
- Retrieval authorized
- Retrieval denied
- Retrieval completed
- Evidence filtered
- Evidence reranked
- Context constructed
- Retrieval abstained
- Retrieval integrity failed

Trace attributes must be allowlisted.

Do not record:

- Raw protected evidence
- Credentials
- Access tokens
- Unbounded query text
- Hidden model reasoning
- Unauthorized source details

## 20. Phase 5A Deliverables

Phase 5A requires:

- This design document
- Subphase inventory
- Authority boundary
- Proposed contracts
- Threat model
- Evaluation plan
- Interview terminology update
- Phase 5A gate decision

Phase 5A does not require executable retrieval.

## 21. Interview-Folder Update Policy

Update the Phase 5 interview tutorial when implementation produces:

- A new defensible term
- A tested tradeoff
- A concrete failure mode
- A measured result
- A stronger mental model
- A new likely interview question
- Inspectable lab evidence

Do not update the tutorial merely because code was written.

Any implementation claim requires test and CI evidence.

New terms identified during Phase 5A:

- Pre-filtering
- Post-filtering
- Security trimming
- Authority-bearing metadata
- Evidence provenance
- Tombstone
- Freshness window
- Retrieval contamination
- Retrieval leakage

## 22. Phase 5A Gate

Phase 5A passes when:

- Scope is synthetic and local.
- Retrieval is read-only.
- Filter-then-retrieve is the primary authority model.
- Proposed evidence contracts preserve authorization and provenance.
- Prompt-injection controls are defined.
- Abstention behavior is defined.
- Permission and quality evaluation are separate.
- No external provider is required.
- No enterprise credential is required.
- No executable capability is prematurely claimed.

## 23. Current Exit Posture

Phase 5A status:

- Design: Drafted
- Authority boundary: Drafted
- Threat model: Drafted
- Evaluation plan: Drafted
- Interview terminology: Identified
- Executable retrieval: Not started
- Phase 5B implementation: Not yet authorized

Next decision:

Review and validate Phase 5A, then decide whether Phase 5B contract
implementation is authorized.
