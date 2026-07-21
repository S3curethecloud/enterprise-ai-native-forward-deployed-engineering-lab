# Phase 8 — Deterministic Policy-Based Routing

## 1. Status

| Dimension | Status |
|---|---|
| Learning guide | Drafted |
| Interview review | Pending |
| Enterprise implementation | Not started |
| Implementation authority | Not authorized before interview |

This document teaches the phase. It does not implement or enable the
capability.

## 2. Job-Description Connection

Agent Architecture and Engineering — policy-based routing, authorization, and controlled enterprise decisions.

## 3. Plain-English Explanation

Policy-based routing selects an allowed workflow path using explicit facts such as identity, role, tenant, resource, action, risk, and approval. A deterministic policy service—not the model—produces the authoritative decision.

## 4. Why Enterprises Care

- Enterprise access varies by user, tenant, resource, and action.
- Model outputs are probabilistic and cannot grant authority.
- Decision identifiers and reasons support auditability.
- Fail-closed behavior prevents silent privilege expansion.
- Policy versioning makes decisions reproducible.

## 5. Terminology

| Term | Plain-English meaning |
|---|---|
| PDP | Policy decision point: evaluates policy and returns a decision. |
| PEP | Policy enforcement point: applies the decision to the request. |
| RBAC | Role-based access control. |
| ABAC | Attribute-based access control. |
| ReBAC | Relationship-based access control. |
| Policy-as-code | Versioned, testable policy expressed in machine-readable rules. |
| Decision lineage | Identifier, policy version, inputs, reasons, and time for a decision. |
| Deny by default | Reject operations unless policy explicitly permits them. |
| Authorization expiry | Time after which a decision must be reevaluated. |
| Separation of duties | Splitting sensitive authority across different actors. |

## 6. Reference Workflow

1. PEP collects trusted identity and request attributes.
2. PDP loads the applicable policy version.
3. Policy evaluates subject, resource, action, environment, and risk.
4. PDP returns allow, deny, require-approval, or restricted route.
5. Decision includes identifier, reason codes, and expiry.
6. PEP enforces the result.
7. Runtime records policy lineage.
8. Expired or missing decisions fail closed.
9. Evaluation tests allow and deny correctness.

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

- Model making authorization decisions
- Untrusted attributes
- Stale policy
- Missing tenant filters
- Allow-by-default behavior
- Policy and enforcement drift
- Approval treated as unlimited authority
- Sensitive policy data in logs

## 10. Metrics and Evidence

- Correct allow rate
- Correct deny rate
- False allow rate
- False deny rate
- Missing-decision rate
- Expired-decision rejection
- Policy-evaluation latency
- Policy-version coverage
- Decision trace completeness

## 11. Mental Notes

- Authentication proves identity; authorization grants an action.
- The model may classify context but cannot authorize itself.
- Record policy version and reason codes.
- Missing or expired authority fails closed.
- Policy must be tested like application code.

## 12. JD-Aligned Core Answers

### 30-Second Core Answer

I keep policy routing deterministic and outside the LLM. The policy decision
uses identity, tenant, data classification, requested capability, risk tier,
region, provider capabilities, and approval state to allow, deny, abstain, or
route. Every decision includes a policy version, reason codes, and traceable
evidence.

### 60-Second Core Answer

The model can recommend a next step, but it should never be the authorization
authority. I define a policy request containing subject identity, tenant,
resource scope, data classification, requested model or tool capability,
action risk, region, and current approval state. A deterministic policy engine
returns allow, deny, abstain, require approval, or an eligible route, together
with policy version and reason codes. Routing to another provider cannot bypass
residency or safety constraints, and tool execution cannot inherit authority
from a prompt. I test conflicting rules, missing attributes, expired decisions,
fallback routes, and default denial. This creates a reconstructable decision
boundary suitable for audit and operational support.

### Claim Defense

Design knowledge supported by implemented authorization-before-retrieval and
runtime boundaries; full Phase 8 routing is future work.

Likely interviewer challenge:

- What was your exact role?
- Which artifacts did you personally create?
- Was this architecture, local implementation, pilot, or production?
- Which stakeholders or client environment were involved?
- What measurable evidence supports the claim?
- What remains unimplemented or unverified?

## 13. Shadow-Experience Exercise

Design policies for read-only evidence access, cross-tenant denial, approval-required remediation, and expired authorization. Use synthetic identities and resources; do not connect production IAM.

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

- Approve policy integration authority.
- Define trusted attributes.
- Define PDP and PEP contracts.
- Implement deny-by-default policies.
- Add policy unit and decision-table tests.
- Add decision lineage and expiry.
- Add enforcement integration.
- Add policy telemetry and audit evidence.

## 16. Official References

- https://www.openpolicyagent.org/docs/latest/
- https://csrc.nist.gov/projects/attribute-based-access-control

## 17. Learning Gate

The phase is interview-ready when the learner can:

- Define the important terminology without reading.
- Explain the workflow and authority boundaries.
- Identify at least five failure modes.
- Select meaningful metrics.
- Give the sixty-second answer naturally.
- Complete the shadow exercise honestly.
- Distinguish tutorial knowledge from implementation evidence.

## 17A. Mock-Agent Retrieval Cues

Route questions containing these topics to this phase:

`policy routing, authorization, OPA, allow, deny, reason code, tenant, risk tier, residency, deterministic policy`

The mock agent should answer in this order:

1. Lead with the architectural or delivery decision.
2. Give the 30-second answer unless depth is requested.
3. Expand with the 60-second answer.
4. Use verified evidence only when the claim defense supports it.
5. State the implementation boundary before implying production use.

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
