# Thin Vertical Slice Interface Contracts

## Document Purpose

This document defines the logical interface contracts for the Citation-Backed Incident Diagnostic Assistant.

The contracts establish explicit boundaries for:

- Diagnostic requests
- Identity context
- Authorization decisions
- Retrieved evidence
- Diagnostic responses
- Controlled errors
- Trace events

These are technology-neutral design contracts. They define information and validation expectations before a programming language, framework, model provider, retrieval engine, or infrastructure platform is selected.

This document does not authorize application runtime, model calls, retrieval implementation, tool execution, infrastructure mutation, or production deployment.

---

## Contract Principles

Every contract must follow these principles:

1. Required fields are explicit.
2. Types are explicit.
3. Enumerations are bounded.
4. Unknown fields are rejected or handled by an approved compatibility rule.
5. Identity is propagated, not inferred from prompt text.
6. Authorization is represented as a deterministic decision.
7. Evidence is distinct from generated text.
8. Citations resolve to retrieved evidence.
9. Recommendations are distinct from executed actions.
10. Errors are structured and non-sensitive.
11. Trace correlation is preserved across boundaries.
12. Contract versions are recorded.
13. Sensitive fields are minimized.
14. Logs use approved representations rather than unrestricted payload copies.
15. Invalid contracts fail closed.

---

## Contract Inventory

| Contract ID | Contract | Producer | Consumer | Primary purpose |
|---|---|---|---|---|
| CT-01 | Diagnostic request | Client interface | Request-validation boundary | Define the requested diagnostic task |
| CT-02 | Identity context | Trusted identity adapter | Policy and workflow boundaries | Carry verified requester identity |
| CT-03 | Authorization decision | Deterministic policy component | Retrieval and workflow boundaries | Allow, deny, or constrain an operation |
| CT-04 | Evidence item | Retrieval boundary | Diagnostic-generation boundary | Represent authorized retrieved evidence |
| CT-05 | Diagnostic response | Workflow boundary | Client interface | Return a cited recommendation or abstention |
| CT-06 | Controlled error | Any bounded component | Upstream caller | Return safe and actionable failure information |
| CT-07 | Trace event | Each lifecycle component | Observability boundary | Reconstruct request behavior |

---

## Versioning Rules

Each contract must contain or inherit a contract version.

The initial documented version is:

```text
1.0
```

Versioning rules:

- Patch-compatible clarification does not change field semantics.
- Adding an optional field requires compatibility review.
- Adding a required field requires a new major contract version.
- Removing or renaming a field requires a new major version.
- Changing an enumeration requires consumer-impact review.
- Producers and consumers must record the version used.
- Unsupported versions must return a controlled error.
- Contract negotiation must never weaken authorization requirements.

---

## Shared Identifier Rules

| Identifier | Rule |
|---|---|
| `request_id` | Unique for each diagnostic request |
| `trace_id` | Stable across the complete request lifecycle |
| `incident_id` | References the enterprise incident without granting mutation rights |
| `service_id` | Resolves to a recognized service catalog entry |
| `evidence_id` | Unique within the request evidence set |
| `source_id` | Identifies an approved source |
| `policy_decision_id` | Identifies one deterministic authorization decision |
| `event_id` | Identifies one trace event |

Identifiers must be treated as opaque values. Their format must not be used as proof of authorization.

---

## CT-01 — Diagnostic Request Contract

### Purpose

The diagnostic request defines a bounded investigation request from an authenticated incident responder.

### Field Contract

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `contract_version` | string | Yes | Must be a supported version |
| `request_id` | string | Yes | Nonempty and unique |
| `trace_id` | string | Yes | Nonempty correlation identifier |
| `incident_id` | string | Yes | Nonempty enterprise incident reference |
| `service_id` | string | Yes | Must resolve to a supported service |
| `environment` | enum | Yes | `development`, `test`, `staging`, or `production` |
| `incident_summary` | string | Yes | Nonempty and length bounded |
| `observed_symptoms` | array[string] | Yes | At least one bounded entry |
| `request_timestamp` | timestamp | Yes | ISO 8601 with timezone |
| `request_type` | enum | Yes | Must equal `diagnostic_recommendation` |
| `alert_ids` | array[string] | No | Bounded collection |
| `deployment_id` | string | No | Opaque reference |
| `error_codes` | array[string] | No | Bounded collection |
| `affected_component` | string | No | Must belong to the service scope |
| `known_start_time` | timestamp | No | ISO 8601 with timezone |
| `existing_ticket_reference` | string | No | Opaque reference |
| `additional_context` | string | No | Untrusted, length-bounded text |

Identity fields are not accepted as self-asserted values in this request. Verified identity arrives through CT-02.

### Valid Example

```json
{
  "contract_version": "1.0",
  "request_id": "req-7f31",
  "trace_id": "trace-a812",
  "incident_id": "INC-10427",
  "service_id": "payments-api",
  "environment": "production",
  "incident_summary": "Elevated payment authorization failures",
  "observed_symptoms": [
    "HTTP 503 rate increased",
    "Dependency timeout alerts firing"
  ],
  "request_timestamp": "2026-07-19T18:30:00Z",
  "request_type": "diagnostic_recommendation",
  "alert_ids": [
    "ALT-8801"
  ],
  "affected_component": "authorization-adapter"
}
```

### Rejection Conditions

The request must be rejected when:

- A required field is absent
- A field has an invalid type
- The contract version is unsupported
- `request_type` requests execution or mutation
- `environment` is outside the enumeration
- A collection exceeds its configured bound
- Required text is empty
- A timestamp is invalid
- Unknown fields violate the compatibility policy
- The request cannot be safely normalized
- The content attempts to supply trusted identity or authorization decisions

---

## CT-02 — Identity Context Contract

### Purpose

The identity context carries verified requester attributes from a trusted identity boundary.

It must not be constructed from free-form user text or model output.

### Field Contract

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `contract_version` | string | Yes | Supported version |
| `subject_id` | string | Yes | Stable verified subject identifier |
| `tenant_id` | string | Yes | Verified tenant or organization boundary |
| `authentication_method` | enum | Yes | Approved enterprise method |
| `authentication_time` | timestamp | Yes | Verified authentication time |
| `session_id` | string | Yes | Trusted session reference |
| `roles` | array[string] | Yes | Verified role claims |
| `groups` | array[string] | Yes | Verified group claims |
| `source_entitlements` | array[string] | Yes | Verified or resolvable entitlement references |
| `assurance_level` | enum | Yes | Approved assurance classification |
| `expires_at` | timestamp | Yes | Identity-context expiration |
| `issuer` | string | Yes | Approved identity issuer |
| `delegation_context` | object | No | Present only for approved delegation |

### Identity Rules

- Expired identity context is invalid.
- The subject identifier cannot be replaced by prompt content.
- Roles and groups are inputs to policy, not direct permission decisions.
- An empty entitlement set does not imply broad access.
- Tenant boundaries must be preserved.
- Delegated identity must identify both delegator and delegate.
- Identity data must be minimized in logs.
- Authentication success does not equal source authorization.

---

## CT-03 — Authorization Decision Contract

### Purpose

The authorization decision records a deterministic allow, deny, or constrain result for a specific subject, resource, and operation.

### Field Contract

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `contract_version` | string | Yes | Supported version |
| `policy_decision_id` | string | Yes | Unique decision identifier |
| `request_id` | string | Yes | Must match the diagnostic request |
| `trace_id` | string | Yes | Must match lifecycle correlation |
| `subject_id` | string | Yes | Must originate from CT-02 |
| `operation` | enum | Yes | Approved bounded operation |
| `resource_ids` | array[string] | Yes | Resources evaluated by policy |
| `outcome` | enum | Yes | `allow`, `deny`, or `constrain` |
| `allowed_resource_ids` | array[string] | Yes | Empty unless explicitly permitted |
| `constraints` | object | Yes | Machine-enforceable restrictions |
| `reason_codes` | array[string] | Yes | Non-sensitive deterministic codes |
| `policy_version` | string | Yes | Evaluated policy revision |
| `decided_at` | timestamp | Yes | Decision time |
| `expires_at` | timestamp | Yes | Decision expiration |

### Approved Initial Operations

```text
validate_diagnostic_request
retrieve_runbook_evidence
generate_diagnostic_recommendation
return_diagnostic_response
```

No production-mutation operation is included.

### Decision Rules

- Missing policy decisions default to denial.
- Expired decisions cannot be reused.
- A decision for one subject cannot authorize another subject.
- A decision for one request cannot silently authorize another request.
- `constrain` must provide enforceable constraints.
- An empty allowed-resource set means no resource is authorized.
- The model cannot create or alter a policy decision.
- Prompt content cannot override the policy version.
- A chat message is not a policy decision.
- Policy reason codes must not expose sensitive rule internals.

---

## CT-04 — Evidence Item Contract

### Purpose

An evidence item represents one authorized unit of retrieved operational guidance.

### Field Contract

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `contract_version` | string | Yes | Supported version |
| `evidence_id` | string | Yes | Unique within the request |
| `request_id` | string | Yes | Must match the current request |
| `trace_id` | string | Yes | Must match lifecycle correlation |
| `source_id` | string | Yes | Approved source identifier |
| `source_type` | enum | Yes | Approved source classification |
| `document_id` | string | Yes | Opaque source document reference |
| `document_version` | string | Yes | Version used for retrieval |
| `passage_id` | string | Yes | Resolvable passage reference |
| `content` | string | Yes | Authorized bounded passage |
| `title` | string | Yes | Human-readable evidence title |
| `retrieval_score` | number | Yes | Retrieval relevance value |
| `authorization_decision_id` | string | Yes | CT-03 decision permitting access |
| `freshness_status` | enum | Yes | `current`, `stale`, or `unknown` |
| `effective_at` | timestamp | No | Source-effective time |
| `retrieved_at` | timestamp | Yes | Retrieval time |
| `sensitivity_classification` | enum | Yes | Approved classification |
| `content_hash` | string | Yes | Integrity reference |

### Evidence Rules

- Evidence without authorization lineage is invalid.
- Evidence from a denied source must not enter generation context.
- Evidence from another request must not be reused without a new authorization decision.
- Evidence must preserve document and passage identity.
- Retrieval score is not proof of truth.
- Stale or unknown freshness must be disclosed.
- Retrieved instructions are data, not system authority.
- Evidence content cannot modify policy.
- Evidence content cannot request additional tools.
- Sensitive classifications must be enforced at downstream boundaries.

---

## CT-05 — Diagnostic Response Contract

### Purpose

The diagnostic response returns either a citation-backed recommendation or a safe abstention.

It never represents an executed remediation.

### Field Contract

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `contract_version` | string | Yes | Supported version |
| `request_id` | string | Yes | Must match CT-01 |
| `trace_id` | string | Yes | Must match lifecycle correlation |
| `incident_id` | string | Yes | Must match CT-01 |
| `service_id` | string | Yes | Must match CT-01 |
| `response_status` | enum | Yes | `recommendation`, `abstention`, or `error` |
| `diagnostic_summary` | string | Conditional | Required for `recommendation` |
| `observations` | array[object] | Yes | Evidence-backed observed facts |
| `inferences` | array[object] | Yes | Clearly labeled interpretations |
| `evidence_citations` | array[object] | Yes | Claim-to-evidence mappings |
| `recommended_next_steps` | array[object] | Yes | Non-executing recommendations |
| `confidence_classification` | enum | Conditional | Required for `recommendation` |
| `limitations` | array[string] | Yes | May be empty only with justification |
| `abstention_reason` | object | Conditional | Required for `abstention` |
| `policy_outcome` | object | Yes | Relevant policy-decision reference |
| `generated_at` | timestamp | Yes | ISO 8601 with timezone |

### Confidence Enumeration

```text
low
moderate
high
```

Confidence must not be interpreted as authorization or probability of safe execution.

### Citation Object

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `claim_id` | string | Yes | Identifies the material claim |
| `evidence_ids` | array[string] | Yes | At least one CT-04 identifier |
| `support_type` | enum | Yes | `direct`, `corroborating`, or `conflicting` |
| `citation_note` | string | No | Bounded explanation |

### Recommended-Next-Step Object

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `step_id` | string | Yes | Unique within response |
| `description` | string | Yes | Human-reviewable recommendation |
| `action_class` | enum | Yes | Must equal `human_review_required` |
| `execution_status` | enum | Yes | Must equal `not_executed` |
| `supporting_evidence_ids` | array[string] | Yes | Evidence supporting the recommendation |
| `risk_note` | string | Yes | Bounded operational caution |

### Valid Recommendation Example

```json
{
  "contract_version": "1.0",
  "request_id": "req-7f31",
  "trace_id": "trace-a812",
  "incident_id": "INC-10427",
  "service_id": "payments-api",
  "response_status": "recommendation",
  "diagnostic_summary": "The observed timeout pattern is consistent with the documented dependency-degradation condition.",
  "observations": [
    {
      "claim_id": "claim-1",
      "text": "The incident reports dependency timeout alerts."
    }
  ],
  "inferences": [
    {
      "claim_id": "claim-2",
      "text": "A degraded downstream dependency is a plausible cause."
    }
  ],
  "evidence_citations": [
    {
      "claim_id": "claim-2",
      "evidence_ids": ["ev-1"],
      "support_type": "direct"
    }
  ],
  "recommended_next_steps": [
    {
      "step_id": "step-1",
      "description": "Have the incident responder verify dependency health using the approved operational procedure.",
      "action_class": "human_review_required",
      "execution_status": "not_executed",
      "supporting_evidence_ids": ["ev-1"],
      "risk_note": "Follow existing incident and change procedures."
    }
  ],
  "confidence_classification": "moderate",
  "limitations": [
    "The slice did not inspect live production telemetry."
  ],
  "policy_outcome": {
    "policy_decision_id": "pd-991",
    "outcome": "allow"
  },
  "generated_at": "2026-07-19T18:30:04Z"
}
```

### Response Rejection Conditions

A response is invalid when:

- Required identifiers do not match the request
- A material claim lacks a valid citation
- A citation references absent evidence
- Evidence lacks authorization lineage
- A recommended step claims execution
- An action class exceeds `human_review_required`
- A confidence value is outside the enumeration
- An abstention lacks a reason
- The response claims production mutation
- The response contains unauthorized content
- The response contract version is unsupported

---

## CT-06 — Controlled Error Contract

### Purpose

The controlled error contract returns bounded failure information without leaking sensitive internal details.

### Field Contract

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `contract_version` | string | Yes | Supported version |
| `request_id` | string | No | Included when safely available |
| `trace_id` | string | Yes | Correlation identifier |
| `error_code` | enum | Yes | Approved bounded code |
| `error_category` | enum | Yes | Approved category |
| `safe_message` | string | Yes | Non-sensitive user-facing explanation |
| `retryable` | boolean | Yes | Explicit retry posture |
| `failed_stage` | enum | Yes | Bounded lifecycle stage |
| `policy_outcome` | object | No | Included for policy-related failure |
| `occurred_at` | timestamp | Yes | ISO 8601 with timezone |

### Initial Error Codes

| Code | Meaning | Retryable default |
|---|---|---:|
| `INVALID_REQUEST` | Request contract failed | No |
| `UNSUPPORTED_VERSION` | Contract version is unsupported | No |
| `IDENTITY_REQUIRED` | Verified identity is absent | No |
| `IDENTITY_EXPIRED` | Identity context expired | Yes |
| `ACCESS_DENIED` | Policy denied the operation | No |
| `SERVICE_UNSUPPORTED` | Service is outside the slice | No |
| `SOURCE_UNAVAILABLE` | Approved evidence source is unavailable | Yes |
| `EVIDENCE_INSUFFICIENT` | Evidence cannot support a diagnosis | No |
| `EVIDENCE_CONFLICT` | Material evidence conflict is unresolved | No |
| `POLICY_UNAVAILABLE` | Policy decision cannot be obtained | Yes |
| `RESPONSE_INVALID` | Generated result failed validation | Yes |
| `DEPENDENCY_FAILURE` | Required bounded dependency failed | Yes |
| `INTERNAL_ERROR` | Safe unspecified failure | Conditional |

Stack traces, credentials, policy internals, raw prompts, and restricted evidence must not appear in `safe_message`.

---

## CT-07 — Trace Event Contract

### Purpose

A trace event records one lifecycle transition without treating logs as the authorization authority.

### Field Contract

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `contract_version` | string | Yes | Supported version |
| `event_id` | string | Yes | Unique event identifier |
| `trace_id` | string | Yes | Lifecycle correlation |
| `request_id` | string | Yes | Diagnostic request reference |
| `event_name` | enum | Yes | Approved event type |
| `component` | string | Yes | Emitting component identity |
| `stage` | enum | Yes | Approved lifecycle stage |
| `outcome` | enum | Yes | `started`, `succeeded`, `denied`, `abstained`, or `failed` |
| `policy_decision_id` | string | No | Required when policy affects outcome |
| `duration_ms` | number | No | Nonnegative duration |
| `input_reference` | string | No | Safe reference, not unrestricted payload |
| `output_reference` | string | No | Safe reference, not unrestricted payload |
| `reason_codes` | array[string] | Yes | Bounded non-sensitive codes |
| `timestamp` | timestamp | Yes | ISO 8601 with timezone |
| `attributes` | object | Yes | Allowlisted metadata only |

### Required Lifecycle Events

```text
request_received
request_validated
identity_validated
policy_evaluated
retrieval_started
retrieval_completed
evidence_assessed
generation_started
generation_completed
response_validated
response_returned
request_denied
request_abstained
request_failed
```

### Trace Rules

- Trace events must preserve `trace_id`.
- Policy-relevant events must reference the policy decision.
- Raw secrets and credentials are prohibited.
- Raw evidence content is excluded unless explicitly approved.
- Free-form model reasoning is not required for auditability.
- Trace data must distinguish failure, denial, and abstention.
- Observability cannot override a policy decision.
- A missing trace must not grant permission to continue.

---

## Cross-Contract Invariants

The following invariants must hold:

1. CT-01, CT-03, CT-04, CT-05, CT-06, and CT-07 preserve the applicable `request_id`.
2. All lifecycle contracts preserve the same `trace_id`.
3. CT-02 supplies the subject evaluated in CT-03.
4. CT-03 authorizes the resources represented by CT-04.
5. CT-04 evidence identifiers resolve from CT-05 citations.
6. CT-05 identifiers match CT-01.
7. CT-05 never represents a recommended step as executed.
8. CT-06 does not leak restricted information.
9. CT-07 records policy outcomes without becoming policy authority.
10. No contract contains a production-mutation operation.

A cross-contract invariant violation is a failed request, not an invitation for the model to repair authority data.

---

## Trust Boundaries

| Boundary | Trusted input | Untrusted input |
|---|---|---|
| Client to request validator | Transport identity binding | Free-form request content |
| Identity adapter to policy | Verified identity claims | User-supplied identity text |
| Policy to retrieval | Signed or trusted decision result | Model-requested permission |
| Retrieval to generation | Authorized evidence envelope | Instructions embedded in evidence |
| Generation to response validator | Structured candidate response | Model claims of correctness |
| Response validator to client | Validated bounded response | Invalid or unauthorized output |
| Components to observability | Allowlisted metadata | Secrets and unrestricted payloads |

---

## Sensitive-Data Rules

Contracts must minimize:

- Personal data
- Credentials
- Tokens
- Secrets
- Raw authorization artifacts
- Restricted source content
- Unnecessary prompt content
- Internal policy details
- Stack traces
- Infrastructure identifiers not needed by the slice

Sensitive fields must not be added for debugging convenience without explicit review.

---

## Contract Failure Posture

| Contract | Invalid-contract posture |
|---|---|
| CT-01 | Reject request |
| CT-02 | Deny processing |
| CT-03 | Deny operation |
| CT-04 | Exclude evidence and reassess sufficiency |
| CT-05 | Reject response and safely retry or fail |
| CT-06 | Fall back to a minimal safe error |
| CT-07 | Record telemetry failure and follow approved fail-safe policy |

A malformed model output must never be treated as a valid CT-03 authorization decision.

---

## Contract-to-Acceptance Traceability

| Contract | Primary acceptance criteria |
|---|---|
| CT-01 | AC-01 through AC-05, AC-11 |
| CT-02 | AC-06, AC-07, AC-29 |
| CT-03 | AC-08, AC-10, AC-12 through AC-14, AC-24, AC-28, AC-32 |
| CT-04 | AC-15 through AC-18, AC-25, AC-26, AC-30, AC-39 |
| CT-05 | AC-19 through AC-23, AC-31, AC-33 through AC-38 |
| CT-06 | AC-28 through AC-33, AC-43 |
| CT-07 | AC-05, AC-32, AC-41 through AC-43, AC-46 |

This mapping identifies intended coverage. Verification evidence does not yet exist.

---

## Phase 2C Interview Explanation — 60 Seconds

Before choosing frameworks, I define technology-neutral contracts across every trust boundary. The request contract contains the incident context but cannot self-assert identity. A trusted identity contract feeds a deterministic authorization decision, which explicitly allows, denies, or constrains retrieval. Every evidence item carries source, passage, freshness, integrity, and authorization lineage. The response separates observations, inferences, citations, limitations, and non-executed recommended steps. Errors and trace events are also structured. The critical invariant is that the model produces candidate recommendations, while policy determines authority and response validation enforces the final contract.

---

## Phase 2C Interview Explanation — 30 Seconds

I define seven contracts before implementation: request, identity, authorization, evidence, response, error, and trace. Identity cannot come from prompt text, evidence must carry authorization lineage, citations must resolve to retrieved passages, and every recommendation is explicitly marked not executed. This makes the boundaries testable and prevents model output from becoming authority.

---

## Phase 2C Completion Gate

Phase 2C passes only when:

- All seven logical contracts are defined.
- Required and optional fields are distinguishable.
- Enumerations are bounded.
- Identity is separated from user-supplied text.
- Authorization is represented as a deterministic decision.
- Evidence includes authorization and citation lineage.
- Recommendations are explicitly non-executing.
- Controlled errors exclude sensitive details.
- Trace events preserve lifecycle correlation.
- Cross-contract invariants are documented.
- Trust boundaries are explicit.
- Contract failures have safe behavior.
- Contract-to-acceptance traceability exists.
- No implementation is claimed.
- No runtime authority is granted.

---

## Current Evidence Status

| Evidence item | Status |
|---|---|
| Contract inventory | Documented |
| CT-01 diagnostic request | Documented |
| CT-02 identity context | Documented |
| CT-03 authorization decision | Documented |
| CT-04 evidence item | Documented |
| CT-05 diagnostic response | Documented |
| CT-06 controlled error | Documented |
| CT-07 trace event | Documented |
| Cross-contract invariants | Documented |
| Executable schemas | Planned |
| Contract tests | Planned |
| Application runtime | Not started |
| Model-provider integration | Not started |
| Retrieval implementation | Not started |
| Tool execution | Not authorized |
| Infrastructure mutation | Not authorized |
| Production deployment | Not authorized |

No executable interface or runtime capability is authorized by this document.
