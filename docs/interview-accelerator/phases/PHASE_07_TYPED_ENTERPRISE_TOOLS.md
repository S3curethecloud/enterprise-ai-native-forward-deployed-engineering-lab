# Phase 7 — Typed Enterprise Tools and MCP

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

Agent Architecture and Engineering — controlled tool invocation and enterprise integration.

## 3. Plain-English Explanation

A typed tool is an external capability exposed through a strict input and output contract. A model may request the tool, but deterministic code, policy, and approval controls decide whether it executes.

## 4. Why Enterprises Care

- Tools connect model reasoning to real enterprise systems.
- Tool side effects can create material business risk.
- Typed contracts make requests testable and auditable.
- Least privilege limits consequences.
- MCP-style discovery can standardize capability exposure.

## 5. Terminology

| Term | Plain-English meaning |
|---|---|
| Tool registry | A governed catalog of tool contracts, ownership, risk, and policy. |
| Function calling | A model-output format representing a requested function and arguments. |
| MCP | Model Context Protocol: a protocol for exposing context and tools through standardized interfaces. |
| JSON Schema | A machine-readable definition of allowed data shape. |
| Idempotency | Repeating an operation does not produce additional unintended effects. |
| Side effect | A change outside the running process, such as creating a ticket or restarting a service. |
| Least privilege | Granting only the minimum authority needed for one operation. |
| Compensating action | An action intended to counteract a completed side effect. |
| Sandbox | An execution environment with restricted access and resources. |
| Allowlist | An explicit set of permitted tools or operations. |

## 6. Reference Workflow

1. Model proposes a tool request.
2. Application validates tool name and arguments.
3. Registry resolves an approved version.
4. Policy evaluates identity, resource, action, and risk.
5. Human approval is requested when required.
6. Scoped credentials are issued or selected.
7. Tool executes with timeout and idempotency key.
8. Output is validated.
9. Side effect and evidence are recorded.
10. Failure triggers a controlled stop or compensation path.

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

- Prompt-injected tool requests
- Excessive permissions
- Argument manipulation
- Duplicate side effects
- Unbounded retries
- Sensitive outputs
- Tool-result poisoning
- Credential leakage
- Unsafe general shell access

## 10. Metrics and Evidence

- Tool-selection accuracy
- Argument-validity rate
- Authorization correctness
- Approval rate
- Execution success
- Duplicate-side-effect rate
- Timeout rate
- Result-validation rate
- Cost and latency per tool

## 11. Mental Notes

- Function calling is a request format, not authorization.
- Every side effect needs a risk classification.
- Never expose unrestricted shell access.
- Retry rules depend on idempotency.
- Tool outputs are untrusted inputs to later steps.

## 12. JD-Aligned Core Answers

### 30-Second Core Answer

I expose tools as narrow typed business capabilities, not arbitrary code or
shell access. Each tool has a validated input and output contract, identity and
policy requirements, timeout and idempotency behavior, side-effect class, and
audit evidence. The agent can request a tool, but deterministic controls decide
whether and how it executes.

### 60-Second Core Answer

For enterprise tool use, I create a registry of narrow capabilities such as
read incident, create ticket draft, or request remediation approval. Every
tool declares a versioned schema, required identity and policy context,
read-versus-write risk, timeout, retry safety, idempotency key, expected errors,
and evidence fields. MCP can provide a consistent discovery and invocation
interface, but it does not replace authorization. The orchestrator proposes a
typed request, the policy layer verifies it, high-risk actions obtain approval,
and the execution gateway uses a dedicated least-privilege identity. I test
schema violations, replay, timeout, partial failure, duplicate invocation, and
compensation. General operating-system access and unregistered tools remain
prohibited.

### Claim Defense

Enterprise architecture knowledge and future lab phase. Do not claim this lab
currently executes MCP or enterprise tools.

Likely interviewer challenge:

- What was your exact role?
- Which artifacts did you personally create?
- Was this architecture, local implementation, pilot, or production?
- Which stakeholders or client environment were involved?
- What measurable evidence supports the claim?
- What remains unimplemented or unverified?

## 13. Shadow-Experience Exercise

Model a ticket-creation tool and a read-only service-catalog tool. Keep execution mocked. Demonstrate schema rejection, policy denial, idempotency, approval requirements, and evidence records.

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

- Approve tool implementation authority.
- Define registry and side-effect classifications.
- Implement read-only mock tools first.
- Add identity and policy integration.
- Add approval contracts.
- Add scoped credential handling.
- Add idempotency and timeout behavior.
- Add tool evaluation and trace evidence.

## 16. Official References

- https://modelcontextprotocol.io/docs/
- https://json-schema.org/learn/getting-started-step-by-step

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

`tools, MCP, function calling, schema, idempotency, timeout, least privilege, enterprise API, tool registry`

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
