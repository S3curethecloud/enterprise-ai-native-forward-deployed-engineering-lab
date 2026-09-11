# Phase 7 — Typed Enterprise Tools and MCP

## 1. Status

| Dimension | Status |
|---|---|
| Learning guide | Updated with verified Phase 7A evidence |
| Interview review | Evidence-backed for the Phase 7A registry boundary |
| Phase 7A registry implementation | Verified; closure-commit CI pending |
| Phase 7B implementation authority | Not authorized before Phase 7A closure-commit CI |

This document teaches the complete phase and records the implemented Phase 7A
metadata-only registry boundary. It does not implement or enable tool
invocation.

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

- Phase 7A implements a typed, immutable, fail-closed registry for seven
  allowlisted tool definitions.
- Phase 7A implementation commit
  `94eef8f1b7da84cd39d6c608250278603a033f97` passed exact-commit CI run
  [30527591986](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/30527591986).
- No tool request, result, invocation, mock execution, or external capability
  is enabled.
- Every registry entry requires authorization, disables execution, and
  prohibits general shell access.
- Phase 7B requires a separate post-closure authority gate.

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

## Phase 7A Fail-Closed Tool Registry Closure Evidence

Phase 6 closure commit `6e4aa1edbb7c5fd160ca020d777052445fb4249b` passed exact-commit CI run
[29900746310](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/29900746310),
authorizing the gradual start of Phase 7.

Phase 7A implementation commit `94eef8f1b7da84cd39d6c608250278603a033f97` passed
exact-commit CI run
[30527591986](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/30527591986).

Verified Phase 7A evidence:

- Seven governed, typed tool definitions
- Closed `ToolName` allowlist
- Immutable registry metadata
- Explicit capability, side-effect, risk, idempotency, approval, timeout, and
  authorization metadata
- `execution_enabled=False` for every definition
- `general_shell_access=False` for every definition
- 39 focused Phase 7A registry pytest cases passed
- 1,042 complete repository pytest cases passed
- Ruff linting and formatting passed
- Strict MyPy checking passed
- Dependency integrity passed
- Python quality and contract-tests CI job passed
- Local container build and health-verification CI job passed

Phase 7A is metadata-only. It does not implement a tool request or result
envelope, invocation interface, mock execution, policy-decision evaluation,
approval execution, credential access, network access, filesystem access,
general shell access, MCP server, real enterprise integration, provider call,
infrastructure mutation, cloud deployment, or production authority.

Phase 7A closure remains pending until this documentation-only closure commit
passes exact-commit CI. Phase 7B remains unauthorized until that closure gate
passes.

Tool execution remains unauthorized. Real enterprise integrations remain unauthorized.

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
| Phase 7A registry metadata implemented | Yes |
| Phase 7A focused pytest cases | 39 passing |
| Complete repository pytest cases | 1,042 passing |
| Phase 7A exact-commit implementation CI | Passed |
| Phase 7A closure | Pending closure-commit CI |
| Phase 7B implementation authorized | No |
| Tool execution authorized | No |
| Real enterprise integration authorized | No |

### Phase 7B Typed Tool Envelope Evidence

- Phase 7B implementation commit: `fdf784b65d4fb1692297b37969427d0bdc445123`.
- Phase 7B implementation CI run: `30535135636` passed.
- Focused Phase 7B contract tests: 40 passed.
- Complete tools tests: 79 passed.
- Complete repository tests: 1,082 passed.
- Phase 7B closure status: pending closure commit CI.
- Phase 7C status: unauthorized until Phase 7B closure commit passes exact-commit CI.
- Tool invocation remains unauthorized.
- Mock execution remains unauthorized.
- Real enterprise integrations remain unauthorized.
- All tool execution remains unauthorized.

<!-- PHASE 7C CLOSURE EVIDENCE START -->

## Phase 7C Closure Evidence

Phase 7C deterministic local mock tools are implemented and verified.

- Phase 7C implementation commit: `4431ba32b46669c4fb601d014b98715e106b31a4`
- Phase 7C implementation CI run: `30786524852`
- Focused tool tests: 99 passed
- Complete repository tests: 1,102 passed
- Required CI jobs passed:
  - Python quality and contract tests
  - Local container build and health verification

Phase 7C remains bounded to deterministic local mock tools only.

Tool execution remains unauthorized. Real enterprise integrations remain unauthorized. Real provider adapters and provider calls remain unauthorized. Network access, credentials, shell execution, and external system mutation remain unauthorized.

Phase 7D is authorized only after this Phase 7C closure documentation commit passes exact-commit CI.

<!-- PHASE 7C CLOSURE EVIDENCE END -->

<!-- PHASE 7D CLOSURE EVIDENCE START -->

## Phase 7D Fail-Closed Deterministic Dispatcher Closure Evidence

This block is the current authoritative Phase 7D posture. Earlier Phase 7A–7C status statements are retained as historical gate evidence and do not supersede this block.

Phase 7D fail-closed deterministic dispatcher implementation is verified at corrected implementation commit `8d2b0ec68f283a9449fab35963b5ceb6a7c70606`. The initial implementation commit `53e1614199622c12f9f5037d6c378b0ed4904021` is not final Phase 7D evidence because the dispatcher source and test file modes required a subsequent normalization-only commit.

Exact-commit CI run [30794548243](https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab/actions/runs/30794548243) passed against `8d2b0ec68f283a9449fab35963b5ceb6a7c70606`.

Verified Phase 7D evidence:

- `src/incident_diagnostic_api/tools/dispatcher.py` is stored as mode `100644`.
- `tests/tools/test_dispatcher.py` is stored as mode `100644`.
- Focused tool tests: 111 passed.
- Complete repository tests: 1,114 passed.
- Python quality and contract tests: passed.
- Local container build and health verification: passed.
- Registered read-only tools may dispatch only to deterministic local mock results.
- Side-effecting tools fail closed with approval required.
- Real execution-enabled definitions fail closed.
- General shell access fails closed.
- Phase 7D remains bounded to deterministic local dispatch only.

Real tool execution remains unauthorized. Real enterprise integrations remain unauthorized. Real provider adapters and provider calls remain unauthorized. Network access, credentials, shell execution, provider SDK execution, filesystem mutation, infrastructure mutation, cloud deployment, production deployment, and external system mutation remain unauthorized.

This documentation package does not itself close Phase 7D. Until exact-commit CI succeeds for the commit containing this four-file closure package, Phase 7D status remains `CLOSURE_PENDING` and Phase 7E remains unauthorized.

If exact-commit CI succeeds for this documentation commit, Phase 7D becomes `CLOSED`. That closure permits a separate determination of the next Phase 7 capability; it does not itself authorize Phase 7E implementation or any real tool execution.

<!-- PHASE 7D CLOSURE EVIDENCE END -->
