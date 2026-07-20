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

## 12. Sixty-Second Interview Answer

> I treat model tool calls as proposals. Typed code validates the schema, a registry resolves the approved capability, policy checks identity and scope, and high-risk operations require scoped human approval. Execution uses least privilege, timeout, idempotency, result validation, and audit evidence. The model never receives general credentials or unrestricted shell access.

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
