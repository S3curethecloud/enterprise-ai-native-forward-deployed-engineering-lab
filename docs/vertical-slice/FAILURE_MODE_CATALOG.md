# Thin Vertical Slice Failure-Mode Catalog

## Document Purpose

This document defines the anticipated failure modes for the Citation-Backed Incident Diagnostic Assistant and the required safe behavior for each failure.

The catalog converts abstract risk statements into testable operational scenarios.

It defines:

- Failure conditions
- Detection signals
- Required system responses
- Prohibited fallback behavior
- Evidence requirements
- Severity and release consequences
- Recovery expectations
- Ownership boundaries

This document specifies future behavior. It does not claim that failure detection, recovery logic, model integration, retrieval, tools, infrastructure, or deployment currently exist.

---

## Source Documents

This catalog derives its scope from:

- `docs/discovery/RISK_AND_AUTHORITY_MATRIX.md`
- `docs/vertical-slice/VERTICAL_SLICE_DEFINITION.md`
- `docs/vertical-slice/ACCEPTANCE_CRITERIA.md`
- `docs/vertical-slice/INTERFACE_CONTRACTS.md`
- `docs/vertical-slice/SYSTEM_BOUNDARIES.md`

A failure response must not exceed the authority defined in those documents.

---

## Failure-Handling Principles

The slice must follow these rules:

1. Fail closed when identity or authorization cannot be established.
2. Abstain when evidence cannot support a reliable recommendation.
3. Reject malformed contracts at their receiving boundary.
4. Preserve request and trace correlation during failure.
5. Distinguish denial, abstention, dependency failure, and internal error.
6. Never invent missing identity, policy, evidence, or approval.
7. Never broaden access as a recovery strategy.
8. Never execute remediation as a fallback.
9. Use bounded retries only for approved transient failures.
10. Prevent retry loops from expanding scope or cost without limit.
11. Return non-sensitive reason codes.
12. Retain evidence sufficient to diagnose the failure.
13. Protect restricted content in logs and errors.
14. Escalate through existing human procedures when necessary.
15. Test failure behavior before production-readiness claims.

---

## Failure Classification

| Classification | Meaning | Default response |
|---|---|---|
| Validation failure | An input or output violates its contract | Reject |
| Authentication failure | Verified identity is absent, invalid, or expired | Deny |
| Authorization failure | A requested operation or resource is not permitted | Deny |
| Evidence failure | Evidence is unavailable, inadequate, stale, or conflicting | Abstain or controlled failure |
| Model failure | Model invocation or candidate output is unusable | Bounded retry or controlled failure |
| Dependency failure | An external required component is unavailable or invalid | Safe degradation or controlled failure |
| Security failure | An attack, leakage, or boundary violation is detected | Stop, contain, and record |
| Observability failure | Required trace or telemetry cannot be recorded | Apply approved operational rule |
| Human-process failure | Required ownership or review cannot be established | Stop promotion or escalate |
| Governance failure | Scope, approval, or evidence requirements are unmet | Block release |

---

## Severity Definitions

| Severity | Meaning | Release consequence |
|---|---|---|
| Critical | Unauthorized access, mutation, secret exposure, or authority compromise | Immediate release block |
| High | Core safety, identity, policy, evidence, or trace control fails | Release block |
| Medium | Quality or dependency degradation with bounded safe behavior | Correct before applicable gate |
| Low | Noncritical usability or diagnostic limitation | Track and prioritize |

Severity describes potential impact. It does not replace incident-classification procedures.

---

## Failure-Mode Catalog

| ID | Severity | Failure condition | Detection signal | Required response | Prohibited fallback |
|---|---|---|---|---|---|
| FM-01 | High | Required request field is missing | CT-01 schema failure | Reject with `INVALID_REQUEST` | Guess the missing value |
| FM-02 | High | Request field has invalid type or enumeration | CT-01 schema failure | Reject with bounded field error | Coerce unsafe values silently |
| FM-03 | Medium | Unsupported contract version is received | Version check failure | Reject with `UNSUPPORTED_VERSION` | Process using assumed semantics |
| FM-04 | High | Request identifier is absent or unusable | Admission validation failure | Reject before processing | Generate identity or authority context from content |
| FM-05 | High | Verified identity context is missing | CT-02 absent | Deny with `IDENTITY_REQUIRED` | Trust a name or email in prompt text |
| FM-06 | High | Identity context is expired | Expiration check | Deny or require reauthentication | Reuse expired identity |
| FM-07 | Critical | Identity subject and request binding do not match | Binding verification failure | Stop and record security event | Substitute another subject |
| FM-08 | Critical | Tenant context conflicts across contracts | Tenant-invariant failure | Stop and isolate request | Select the broader tenant |
| FM-09 | High | Policy service is unavailable | Policy call timeout or failure | Deny or safely abstain | Fail open |
| FM-10 | High | Policy decision is missing | CT-03 absent | Deny operation | Infer permission from role name |
| FM-11 | High | Policy decision is expired | CT-03 expiration failure | Obtain a new decision or deny | Reuse the stale decision |
| FM-12 | Critical | Policy decision belongs to another subject or request | Cross-contract invariant failure | Stop and record security event | Rebind the decision |
| FM-13 | Critical | Model output attempts to grant authorization | Output-content or schema detection | Reject output | Treat the model statement as policy |
| FM-14 | Critical | Chat message is presented as approval authority | Approval-origin validation failure | Reject approval claim | Treat “approved” text as authorization |
| FM-15 | High | Requested service is unsupported | Service-catalog lookup failure | Return `SERVICE_UNSUPPORTED` | Search unrelated sources |
| FM-16 | High | No eligible source exists for the requester | Empty authorized-source set | Deny retrieval and abstain | Retrieve from a broadly accessible credential |
| FM-17 | Critical | Retrieval returns content from a denied source | Authorization-lineage mismatch | Discard content, stop response, record incident | Redact and continue using derived information |
| FM-18 | Critical | Evidence belongs to another tenant or request | Evidence-envelope invariant failure | Discard, stop, and record security event | Reassociate evidence locally |
| FM-19 | High | Evidence source is unavailable | Source timeout or dependency error | Return bounded failure or abstention | Invent source content |
| FM-20 | Medium | Retrieval returns no relevant evidence | Empty result after authorized retrieval | Abstain with `EVIDENCE_INSUFFICIENT` | Produce an uncited diagnosis |
| FM-21 | High | Evidence is materially stale | Freshness rule failure | Disclose and abstain when required | Present stale guidance as current |
| FM-22 | High | Authorized sources materially conflict | Conflict detector or evaluator | Disclose conflict and abstain if unresolved | Select the most convenient source silently |
| FM-23 | Critical | Retrieved content contains prompt injection | Injection detection or adversarial test | Treat it as data and ignore instructions | Change policy, tools, or system behavior |
| FM-24 | Critical | Retrieved content requests another protected source | Cross-source escalation attempt | Reject request and preserve current scope | Expand retrieval permissions |
| FM-25 | High | Evidence item lacks source or passage identity | CT-04 validation failure | Exclude evidence | Create a synthetic citation |
| FM-26 | High | Evidence lacks authorization-decision lineage | CT-04 validation failure | Exclude evidence and reassess sufficiency | Assume the source was authorized |
| FM-27 | High | Evidence integrity reference does not match | Hash or integrity check failure | Reject evidence and record failure | Use potentially modified content |
| FM-28 | Medium | Model provider is unavailable | Provider timeout or error | Apply bounded retry, then controlled failure | Retry indefinitely |
| FM-29 | Medium | Model provider rate-limits the request | Provider response code | Back off within retry budget or fail safely | Create unbounded concurrent retries |
| FM-30 | High | Model response is malformed | CT-05 schema failure | Reject, bounded retry, or fail | Return raw output |
| FM-31 | High | Material claim lacks citation | Citation-validation failure | Reject candidate response | Return the claim as general knowledge |
| FM-32 | Critical | Citation references evidence not retrieved for the request | Citation-lineage failure | Reject response and record security signal | Resolve the citation from an unrestricted source |
| FM-33 | High | Model fabricates a source, passage, or quotation | Citation-resolution failure | Reject response | Preserve fabricated citation with disclaimer |
| FM-34 | High | Response conceals insufficient evidence | Evaluation or response-rule failure | Reject and convert to abstention | Increase confidence language |
| FM-35 | High | Response conceals material evidence conflict | Conflict-disclosure failure | Reject or abstain | Present one source as unanimous |
| FM-36 | Critical | Response claims an action was executed | Execution-status validation failure | Reject response | Rephrase execution as success |
| FM-37 | Critical | Workflow attempts to invoke a production mutation | Capability or policy violation | Block invocation and record security event | Ask the model whether it is safe |
| FM-38 | Critical | Credential, token, or secret appears in output | Secret-detection control | Block output and initiate security handling | Mask partially and continue without review |
| FM-39 | High | Sensitive evidence appears in telemetry | Log-sanitization detection | Stop affected logging path and contain evidence | Retain it for debugging convenience |
| FM-40 | High | Trace identifiers are inconsistent across stages | Trace-invariant failure | Fail response or mark request incomplete under approved rule | Invent a reconstructed trace after the fact |
| FM-41 | High | Required policy decision is absent from trace | Trace review failure | Block evidence claim and investigate | Treat application logs as authorization proof |
| FM-42 | Medium | Observability platform is temporarily unavailable | Telemetry-export failure | Buffer within bounds or apply approved fail-safe rule | Disable controls to preserve throughput |
| FM-43 | Medium | Retry budget is exhausted | Retry counter reaches limit | Return controlled failure | Reset counter and continue indefinitely |
| FM-44 | High | Duplicate request may cause inconsistent results | Duplicate-request detection | Mark duplicate and apply idempotency rule | Treat duplicate as new authority |
| FM-45 | High | Response validator is unavailable | Required dependency failure | Stop response delivery | Return unvalidated model output |
| FM-46 | Medium | Response exceeds size or latency bound | Contract or SLO measurement | Truncate only by approved rule or fail safely | Remove citations to reduce size |
| FM-47 | High | Human reviewer or accountable owner is unavailable | Ownership check failure | Escalate or stop applicable workflow | Let the model self-approve |
| FM-48 | Critical | Proposed scope introduces write-capable tool access | Boundary-change review | Block until separately governed | Treat it as a minor configuration change |
| FM-49 | High | Evaluation dataset or configuration version is unknown | Evidence-package validation failure | Mark evaluation invalid | Report an unversioned score |
| FM-50 | High | A production-readiness claim lacks required evidence | Governance-gate failure | Reject the claim and block promotion | Accept demonstration screenshots |

---

## Retry Policy

Retries are permitted only when:

- The failure is classified as transient.
- The operation remains authorized.
- The request and trace identifiers remain unchanged.
- The authorization decision remains valid.
- The retry does not broaden resource scope.
- The retry budget is explicit.
- Backoff is bounded.
- Duplicate effects are controlled.
- Each attempt is observable.
- Exhaustion returns a controlled failure.

Retries are prohibited for:

- Access denial
- Invalid identity
- Unsupported service
- Unsupported contract version
- Prohibited production action
- Prompt-based authorization attempts
- Unauthorized source access
- Contractually invalid request content that requires user correction

---

## Default-Deny Cases

The workflow must default to denial when:

- Identity is missing or invalid.
- Tenant context is unresolved.
- Policy is unavailable.
- A policy decision is missing or expired.
- Resource authorization is unresolved.
- A source has unknown eligibility.
- A requested operation is not enumerated.
- A constraint cannot be enforced.
- Approval provenance is invalid.
- A component requests authority not present in its contract.

Default denial must not be converted into a recommendation to bypass the control.

---

## Mandatory-Abstention Cases

The workflow must abstain when:

- No sufficient authorized evidence is available.
- Material evidence is stale beyond the approved threshold.
- Material sources conflict without a resolution rule.
- Valid citations cannot be produced.
- Diagnostic confidence cannot be expressed under the approved scheme.
- The request exceeds the supported diagnostic scope.
- A safe recommendation cannot be separated from execution.
- Required limitations cannot be determined.

An abstention must remain traceable and useful without exposing restricted information.

---

## Security-Containment Cases

The workflow must stop and initiate the approved security-handling path when it detects:

- Cross-tenant content
- Unauthorized-source disclosure
- Credential or secret exposure
- Replayed authorization from another subject
- Evidence-integrity failure suggesting tampering
- Attempted production mutation
- Policy bypass
- Approval spoofing
- Persistent prompt-injection success
- Restricted data in telemetry

This document identifies the requirement; it does not define or activate an enterprise incident-response process.

---

## Degraded Modes

Permitted degraded behavior may include:

- Returning a controlled dependency error
- Returning a safe abstention
- Using fewer authorized sources when sufficiency remains satisfied
- Buffering allowlisted telemetry within an approved bound
- Deferring the request for later retry
- Returning evidence without a diagnosis only if a future contract explicitly allows it

Prohibited degraded behavior includes:

- Disabling authorization
- Using broader credentials
- Removing citations
- Returning raw model output
- Using unapproved sources
- Executing remediation
- Hiding a dependency failure
- Claiming full service when controls are impaired

---

## Failure Evidence Requirements

Each exercised failure case must retain:

| Evidence | Requirement |
|---|---|
| Test identifier | Unique and versioned |
| Failure-mode identifier | One or more `FM-*` references |
| Request fixture | Sanitized and reproducible |
| Expected outcome | Defined before execution |
| Actual outcome | Captured after execution |
| Contract version | Recorded |
| Policy version | Recorded where applicable |
| Dataset version | Recorded where applicable |
| Trace identifier | Recorded |
| Relevant trace events | Retained |
| Error or abstention code | Retained |
| Sensitive-data review | Completed |
| Pass or fail result | Explicit |
| Defect reference | Required for failure |
| Reviewer | Recorded where human judgment applies |

---

## Recovery Evidence Requirements

A failure is not considered operationally handled until evidence shows:

1. The failure was detected.
2. The system entered the required safe state.
3. Unauthorized behavior did not occur.
4. Correlation data was retained.
5. Retry behavior respected its budget.
6. Recovery did not broaden authority.
7. Normal processing resumed only after prerequisites recovered.
8. The failure did not produce a misleading success response.
9. The test result and limitations were recorded.

---

## Failure Ownership

| Failure area | Primary owner | Required collaborator |
|---|---|---|
| Request contract | AI platform engineering | Client integration owner |
| Identity | Enterprise identity owner | Security |
| Authorization | Policy owner | Security and data owner |
| Evidence access | Data owner | Retrieval engineering |
| Evidence quality | Service owner | Incident operations |
| Model output | AI engineering | Domain reviewers |
| Response validation | AI platform engineering | Security |
| Dependency reliability | Platform operations | Component owner |
| Telemetry | Observability owner | Security |
| Human workflow | Incident operations | Service owner |
| Governance gate | Release authority | Risk and engineering |

The model is not an owner for any failure category.

---

## Failure-to-Acceptance Mapping

| Failure range | Primary acceptance coverage |
|---|---|
| FM-01–FM-04 | AC-01–AC-05 |
| FM-05–FM-08 | AC-06, AC-07, AC-29 |
| FM-09–FM-14 | AC-10, AC-14, AC-24, AC-28, AC-32 |
| FM-15–FM-27 | AC-08–AC-20, AC-25, AC-26, AC-30, AC-39 |
| FM-28–FM-37 | AC-19–AC-23, AC-31, AC-33–AC-38 |
| FM-38–FM-46 | AC-27, AC-40–AC-46 |
| FM-47–FM-50 | AC-47–AC-50 |

The mapping establishes planned coverage, not verified behavior.

---

## Phase 2E Interview Explanation — 60 Seconds

I create a failure-mode catalog before implementation so unhappy paths are part of the architecture rather than late operational surprises. For this slice, I define fifty cases across request validation, identity, policy, evidence, prompt injection, model output, citations, telemetry, dependencies, human ownership, and governance. Each case has a severity, detection signal, required safe response, and explicitly prohibited fallback. Identity and policy uncertainty fail closed, insufficient evidence causes abstention, and transient retries are bounded without expanding scope. Critical failures such as cross-tenant evidence, secret exposure, fabricated authorization, or production mutation block release regardless of aggregate quality.

---

## Phase 2E Interview Explanation — 30 Seconds

I define failure behavior before coding. Identity and authorization failures deny access, evidence failures cause abstention, model and dependency retries are bounded, and cross-tenant leakage or production mutation blocks release. Every failure maps to a detection signal, safe response, prohibited fallback, owner, test, and retained evidence.

---

## Phase 2E Completion Gate

Phase 2E passes only when:

- Fifty bounded failure modes are documented.
- Each failure has a severity.
- Each failure has a detection signal.
- Each failure has a required response.
- Each failure prohibits unsafe fallback.
- Retryable and non-retryable cases are distinguishable.
- Default-deny cases are explicit.
- Mandatory-abstention cases are explicit.
- Security-containment cases are explicit.
- Degraded modes preserve controls.
- Failure evidence requirements are documented.
- Recovery evidence requirements are documented.
- Failure ownership is assigned.
- Failure modes map to acceptance criteria.
- Critical failures block release.
- No failure response grants production authority.
- No runtime capability is claimed.

---

## Current Evidence Status

| Evidence item | Status |
|---|---|
| Failure classification | Documented |
| Severity definitions | Documented |
| Fifty failure modes | Documented |
| Retry policy | Documented |
| Default-deny behavior | Documented |
| Mandatory abstention | Documented |
| Security containment | Documented |
| Degraded modes | Documented |
| Failure evidence contract | Documented |
| Recovery evidence contract | Documented |
| Failure tests | Planned |
| Failure-injection harness | Planned |
| Application runtime | Not started |
| Model-provider integration | Not started |
| Retrieval implementation | Not started |
| Tool execution | Not authorized |
| Infrastructure mutation | Not authorized |
| Production deployment | Not authorized |

No failure-handling implementation or executable authority is authorized by this document.
