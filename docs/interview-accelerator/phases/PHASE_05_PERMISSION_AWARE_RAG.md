# Phase 5 — Permission-Aware RAG and Context Engineering

## 1. Status

| Dimension | Status |
|---|---|
| Learning guide | Updated through verified Phase 5D permission filtering |
| Interview review | Pending |
| Enterprise implementation | Phase 5D implementation verified; closure-commit CI pending |
| Implementation authority | Phase 5D closure commit only; Phase 5E authorized only after closure-commit CI |

Phase 5C closed after exact-commit CI run
[`29795787216`](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29795787216)
passed against closure commit
`0e757ab896d61a29ec520e614bd4276a1291e9cc`.

Phase 5D implemented tenant, service, classification, resource,
source-type, lifecycle, and policy-lineage filtering before keyword
scoring. Exact-commit CI run
[`29805548139`](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29805548139)
passed against implementation commit
`f3e654da813f4b5bbfd42d5b5cdbc9e14980d1ae`. Phase 5D closure-commit CI
remains pending.

Phase 5E local deterministic embeddings and vector retrieval becomes
authorized only after the Phase 5D closure commit passes exact-commit CI.
External embeddings, managed vector databases, enterprise sources,
production data, hybrid retrieval, reranking, context construction,
external providers, tools, retrieval API routes, cloud deployment, and
production deployment remain unauthorized.

## 2. Job-Description Connection

Agent Architecture and Engineering — retrieval, context engineering, grounding, and enterprise data controls.

## 3. Plain-English Explanation

A permission-aware RAG pipeline finds evidence relevant to a request while enforcing the requesting identity's access rights. It assembles bounded context, generates a response, and preserves citations so the result can be checked.

## 4. Why Enterprises Care

- Enterprise knowledge is distributed across many systems.
- Relevant evidence may be sensitive or tenant-scoped.
- Model knowledge may be stale or unsupported.
- Users need evidence, not only fluent answers.
- Access rules must apply before evidence reaches the model.

## 5. Terminology

| Term | Plain-English meaning |
|---|---|
| RAG | Retrieval-augmented generation: retrieve evidence and use it as generation context. |
| Embedding | A numeric representation used for semantic similarity. |
| Chunk | A bounded unit of source content prepared for retrieval. |
| Metadata | Structured facts such as source, tenant, owner, date, and classification. |
| Vector search | Approximate semantic search over embeddings. |
| Keyword search | Search based on exact words or lexical relevance. |
| Hybrid search | Combination of semantic and keyword retrieval. |
| Reranking | A second-stage model or algorithm that reorders candidates. |
| Grounding | Constraining claims to supplied evidence. |
| Citation | A reference connecting a claim to supporting evidence. |
| Context engineering | Managing the complete information environment used by a model step. |
| Access-control filter | A deterministic restriction based on identity and resource policy. |
| Abstention | A controlled decision not to answer when evidence is insufficient. |
| Pre-filtering | Applying access and metadata restrictions before relevance scoring. |
| Post-filtering | Removing prohibited candidates after retrieval as defense in depth. |
| Security trimming | Restricting results to evidence the current identity may access. |
| Authority-bearing metadata | Trusted metadata used to make authorization decisions. |
| Evidence provenance | Source, version, transformation, and retrieval lineage. |
| Content hash | Deterministic evidence identifier supporting integrity and replay. |
| Tombstone | A record marking evidence as deleted or invalidated. |
| Freshness window | Maximum acceptable evidence age for a decision. |
| Retrieval contamination | Malicious, stale, misleading, or unauthorized corpus content. |
| Retrieval leakage | Unauthorized information exposed through content or side channels. |

## 6. Reference Workflow

1. Validate request and identity context.
2. Evaluate service and data-source authorization.
3. Construct a retrieval query.
4. Apply tenant, resource, and classification filters.
5. Run keyword, vector, or hybrid retrieval.
6. Rerank authorized candidates.
7. Assemble bounded context with source identifiers.
8. Request structured generation.
9. Validate response schema and citations.
10. Evaluate groundedness and retrieval quality.
11. Return recommendation or controlled abstention.

## 7. Connection to the Incident-Diagnostic Lab

Phases 0–4 provide discovery, a thin slice, typed contracts, service
boundaries, deterministic state, budgets, stops, checkpoints, replay,
lifecycle traces, tests, containers, and CI evidence.

This phase describes how the next capability would connect to those
existing boundaries after implementation authority is restored.

Current repository status:

- The phase is not implemented.
- No external capability is enabled by this tutorial.
- The Phase 4 runtime remains the latest executable boundary.
- Post-interview work requires a new design and implementation gate.

## 8. Authority and Security Boundaries

- Models do not grant access.
- Missing authority fails closed.
- Inputs and outputs require typed validation.
- Sensitive data must be minimized and redacted.
- Every external dependency needs timeout and error behavior.
- High-risk side effects remain separately controlled.
- Evidence must distinguish facts, inference, and uncertainty.
- Audit records must not contain secrets or hidden reasoning.

## 9. Important Risks

- Cross-tenant retrieval
- Prompt injection in retrieved content
- Stale or deleted evidence
- Unsupported claims
- Incorrect citations
- Low recall
- Context-window overflow
- Sensitive data in telemetry
- Retrieval poisoning

## 10. Metrics and Evidence

- Retrieval recall
- Retrieval precision
- Ranking quality
- Citation correctness
- Groundedness
- Access-filter correctness
- Abstention correctness
- p95 retrieval latency
- Cost per grounded response

## 11. Mental Notes

- RAG is an evidence pipeline, not a vector database.
- Apply authorization before model context construction.
- More context is not automatically better context.
- Citations must support the actual claim.
- Abstention is a valid safe outcome.

## 11A. Phase 5A Design Discoveries

### Filter timing is a security decision

Filter-then-retrieve restricts the searchable corpus before scoring.

Retrieve-then-filter searches broadly and removes prohibited results later.

The Phase 5 design selects filter-then-retrieve as the primary authority
model. Post-filtering may be used as defense in depth.

### Relevance does not create authority

A highly relevant document may still be prohibited.

Embedding similarity, keyword score, reranking score, and model preference do
not grant access.

### Authorization metadata must be trusted

Tenant, service, environment, classification, and ownership metadata affect
access decisions. They must come from controlled ingestion or policy sources.

### Deletion must reach retrieval

A tombstone records that evidence has been removed or invalidated. Retrieval,
indexes, caches, rerankers, and context construction must respect it.

### Freshness is decision-specific

A runbook may remain useful for months, while deployment or incident evidence
may become stale within minutes. Freshness belongs to the source and decision
model rather than one universal timeout.

### Leakage includes side channels

Retrieval leakage can occur through:

- Content
- Titles
- Metadata
- Candidate counts
- Scores
- Timing
- Caches
- Logs
- Error messages

### Content hashes support integrity, not truth

A content hash identifies exact bytes and supports replay. It does not prove
the source is accurate, authoritative, or safe.

### Updated mental model

> Authorize the searchable evidence set, retrieve and rank within it,
> revalidate candidates, preserve provenance, enforce freshness and deletion,
> then construct bounded context or abstain.

## 12. Sixty-Second Interview Answer

> I would build RAG as a permission-aware evidence pipeline. Identity and policy filter sources before retrieval results enter model context. I would combine lexical and semantic retrieval where useful, rerank candidates, preserve source identifiers, validate citations, and measure recall, groundedness, access correctness, latency, and cost. If evidence is insufficient, the workflow should abstain.

## 13. Shadow-Experience Exercise

Design a read-only evidence pipeline for the incident-diagnostic workflow. Use synthetic runbooks, change records, and service metadata. Demonstrate access filtering, citation validation, and abstention without connecting enterprise systems.

Required disclosure:

> This is a portfolio learning or design exercise. It is not evidence
> of a production client deployment unless separately supported by a
> real professional example.

## 14. Interview Questions

- What business problem does this capability solve?
- Which component has decision authority?
- What is the most dangerous failure mode?
- What evidence would be required before release?
- How would you measure usefulness and safety?
- How would this design change in a regulated environment?
- What would remain human-controlled?
- What would you prototype first?
- What would make the prototype production-ready?
- Which assumptions require client validation?

## 15. Post-Interview Implementation Backlog

- Approve Phase 5 implementation authority.
- Define source and identity contracts.
- Create synthetic evaluation corpus.
- Implement ingestion and deletion behavior.
- Implement filtered hybrid retrieval.
- Implement reranking and context assembly.
- Add prompt-injection controls.
- Add citation and groundedness evaluation.
- Add retrieval telemetry.

## 16. Official References

- https://platform.openai.com/docs/guides/retrieval
- https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview

## 17. Learning Gate

The phase is interview-ready when the learner can:

- Define the important terminology without reading.
- Explain the workflow and authority boundaries.
- Identify at least five failure modes.
- Select meaningful metrics.
- Give the sixty-second answer naturally.
- Complete the shadow exercise honestly.
- Distinguish tutorial knowledge from implementation evidence.

## 18. Exit Posture

| Dimension | Status |
|---|---|
| Terminology documented | Yes |
| Architecture documented | Yes |
| Risks documented | Yes |
| Metrics documented | Yes |
| Interview answer drafted | Yes |
| Enterprise capability implemented | No |
| Implementation authorized | No |

## Phase 5B Implementation-Derived Concepts

### Outcome Exclusivity

Outcome exclusivity means a retrieval response must represent exactly one
result shape:

- Authorized, ranked evidence candidates, or
- An explicit abstention

It cannot represent both simultaneously.

Mental note: a secure retrieval contract should make ambiguous success
impossible to represent.

### Provenance Alignment

Provenance alignment means a candidate and its citation must identify the
same:

- Source
- Document
- Document version
- Chunk

The candidate must also preserve the request, trace, and policy-decision
lineage established by the authorized query.

Mental note: a citation is trustworthy only when its evidence identity and
authorization lineage remain aligned.

### Contiguous Ranking

Contiguous ranking means candidate ranks are unique, ordered, one-based,
and have no gaps.

Valid ranking:

```text
1, 2, 3
```

Invalid rankings include `2`, `1, 1`, and `1, 3`.

Mental note: retrieval ranking is evidence, so its ordering must be
deterministic and structurally valid.

### Honest Phase 5B Interview Statement

In Phase 5B, I implemented the immutable contract layer for
permission-aware retrieval. The contracts enforce source allowlisting,
live policy lineage, citation provenance, lifecycle integrity, ranked
candidate results, and explicit abstention.

I did not implement a corpus, embeddings, search execution, reranking,
context construction, provider calls, or retrieval API routes.

## Phase 5B Verified Evidence

Phase 5B implementation evidence:

- Implementation commit: `efd62671b27e725d2936a2c7ae3a1a0d24b06ca6`
- Exact-commit CI run: [`29780263857`](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29780263857)
- Retrieval contract tests: 37 passed
- Complete repository tests: 723 passed
- CI quality job: Passed
- CI container job: Passed

Phase 5B implemented and verified the immutable contract layer only.

Next bounded work:

Phase 5C — Synthetic corpus and deterministic keyword retrieval

Phase 5C remains local, synthetic, deterministic, and read-only.
It does not authorize enterprise sources, vector retrieval,
embeddings, reranking, provider calls, tools, retrieval API routes,
cloud deployment, or production deployment.

## Phase 5C Implementation-Derived Concepts

### Lexical Retrieval

Lexical retrieval finds evidence through explicit token overlap between the
query and evidence text.

In this lab, the score is the number of unique query tokens found in a
chunk divided by the number of unique query tokens.

Mental note: lexical retrieval matches words. Semantic retrieval attempts
to match meaning. Phase 5C implements lexical retrieval only.

### Content-Addressed Integrity

Content-addressed integrity binds evidence content to a deterministic
SHA-256 hash.

When a document or chunk enters the synthetic corpus, its declared hash
must match the hash calculated from its exact UTF-8 content. A mismatch is
rejected.

Mental note: the hash detects content changes. It does not prove who
created the evidence and is not a digital signature.

### Stable Tie-Breaking

Stable tie-breaking gives equally scored candidates a deterministic order.

Phase 5C orders equal scores using source identifier, document identifier,
chunk index, and chunk identifier. Corpus insertion order therefore does
not change the result.

Mental note: deterministic retrieval requires both deterministic scores
and deterministic handling of ties.

### Source Scope Before Scoring

Phase 5C removes non-allowlisted source identifiers, non-allowlisted source
kinds, and tombstoned chunks before keyword scoring.

Mental note: evidence outside the authorized source scope should never
become a scored candidate.

This was the Phase 5C boundary. Phase 5D now applies tenant, service,
classification, resource, source-type, lifecycle, and policy-lineage
controls before scoring.

### Cite-or-Abstain Behavior

Phase 5C either returns ranked candidates with citations or returns an
explicit abstention.

It abstains when authority has expired, no source is authorized, the query
contains no searchable terms, or no evidence meets the configured score
threshold.

Mental note: no acceptable evidence is a controlled outcome, not a reason
to fabricate context.

### Honest Phase 5C Interview Statement

In Phase 5C, I implemented deterministic read-only keyword retrieval over
an immutable synthetic corpus. I added SHA-256 content-integrity checks,
normalized lexical scoring, source allowlisting before scoring, tombstone
exclusion, stable tie-breaking, citations, and explicit abstention.

The local evidence is 23 corpus tests, 16 keyword tests, 76 total retrieval
tests, and 762 repository tests.

Phase 5C passed exact-commit CI run [`29795504565`](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29795504565) against
implementation commit `8cee3d71676440824b700c62359c162a98cb2b8e`. Phase 5C closed after exact-commit CI run
[`29795787216`](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29795787216)
passed against closure commit
`0e757ab896d61a29ec520e614bd4276a1291e9cc`.

I did not implement enterprise retrieval, tenant or service filtering,
classification filtering, embeddings, vector search, hybrid retrieval,
reranking, context construction, provider calls, tools, or retrieval API
routes.

## Phase 5C Verified Evidence

- Implementation commit: `8cee3d71676440824b700c62359c162a98cb2b8e`
- Exact-commit CI run: [`29795504565`](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29795504565)
- Corpus tests: 23 passed
- Keyword tests: 16 passed
- Retrieval tests: 76 passed
- Complete repository tests: 762 passed
- CI quality job: Passed
- CI container job: Passed

Current bounded work:

Phase 5D — Implementation commit and exact-commit CI evidence

Enterprise retrieval, vectors, embeddings, hybrid retrieval,
reranking, context construction, providers, tools, cloud deployment,
and production deployment remain unauthorized.

## Phase 5D Implementation-Derived Concepts

### Policy-Derived Retrieval Scope

A retrieval query describes what the caller wants to search. It does not
grant permission.

Phase 5D requires a separate CT-03 authorization decision containing the
permitted resources, tenants, services, source types, classifications,
policy lineage, expiration, and maximum evidence count.

Mental note: the query carries intent; the policy decision carries
authority.

### Security Trimming

Security trimming removes evidence that the requesting identity is not
permitted to search.

Phase 5D applies resource, source-type, tenant, service, sensitivity, and
lifecycle checks before relevance scoring.

Mental note: unauthorized evidence should not merely be hidden after
ranking. It should never enter the scorer.

### Effective-Scope Intersection

The effective retrieval scope is the intersection of the sources requested
by the query and the resources allowed by policy.

If either side excludes a source, that source is not searchable.

Mental note: retrieval uses the narrowest valid scope. It does not combine
request and policy scope into a broader union.

### Authority Lineage

Authority lineage binds retrieval to the policy decision created for the
same request, trace, subject, policy version, operation, and time window.

A mismatch causes controlled abstention.

Mental note: possessing a structurally valid decision is insufficient. The
decision must belong to this exact retrieval operation.

### Classification Filtering

Classification filtering compares evidence sensitivity with the
classifications explicitly permitted by policy.

The retrieval component cannot downgrade restricted evidence or infer
permission from relevance.

Mental note: relevance answers “is this useful?” Authorization answers
“may this identity access it?” Authorization is evaluated first.

### Fail-Closed Source Mapping

Phase 5D explicitly maps:

- Runbook evidence to the CT-03 runbook source type
- Service-catalog evidence to the CT-03 service-metadata source type

Change records, incident history, and observability summaries have no
Phase 5D policy mapping and therefore fail closed.

Mental note: an unknown mapping is a denial condition, not implicit
permission.

### Policy-Controlled Result Limits

The candidate limit is the smaller of the query maximum and the policy
maximum.

Mental note: caller preferences can narrow a policy limit, but they cannot
increase it.

### Honest Phase 5D Interview Statement

In Phase 5D, I connected deterministic keyword retrieval to a separate
CT-03 authorization decision so the retrieval query could not authorize
itself. I extended the policy contract with tenant, service, and
classification scope, validated request and policy lineage, intersected
requested sources with permitted resources, mapped supported source types,
and applied security trimming before keyword scoring.

I also added executable evidence that rejected content never reaches the
scoring function, unsupported source kinds fail closed, denied or
mismatched authority produces controlled abstention, and policy limits
override larger query limits.

The local evidence is 40 authorization and evidence contract tests, 126
focused contract and retrieval tests, 26 keyword tests, and 776 repository
tests. Ruff, formatting, strict type checking, dependency validation, and
the capability-boundary check pass locally.

Phase 5D passed exact-commit CI run
[`29805548139`](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29805548139)
against implementation commit
`f3e654da813f4b5bbfd42d5b5cdbc9e14980d1ae`. The Phase 5D closure commit
and its exact-commit CI evidence remain pending.

I did not implement enterprise data integration, embeddings, vector
retrieval, hybrid retrieval, reranking, context construction, provider
calls, tools, retrieval API routes, cloud deployment, or production
deployment.

## Phase 5D Verified Implementation Evidence

- Implementation commit: `f3e654da813f4b5bbfd42d5b5cdbc9e14980d1ae`
- Exact-commit CI run: [`29805548139`](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29805548139)
- Authorization and evidence contract tests: 40 passed
- Focused contract and retrieval tests: 126 passed
- Keyword tests: 26 passed
- Complete repository tests: 776 passed
- CI quality job: Passed
- CI container job: Passed

Phase 5D implementation evidence is verified. Phase 5D closure still
requires the closure commit to pass exact-commit CI.

Next bounded work after closure-commit CI:

Phase 5E — Local deterministic embeddings and vector retrieval

Phase 5E is limited to local deterministic embeddings and local vector
retrieval over synthetic evidence. External embedding providers, managed
vector databases, enterprise sources, production data, hybrid retrieval,
reranking, context construction, provider calls, tools, retrieval API
routes, cloud deployment, and production deployment remain unauthorized.
