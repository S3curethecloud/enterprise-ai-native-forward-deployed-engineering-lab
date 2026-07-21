# Phase 6 — Multi-Provider AI Abstraction

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

AI Platform Integration — abstraction layers across OpenAI, Anthropic, Vertex AI, and open-source models.

## 3. Plain-English Explanation

A provider abstraction gives the application a stable interface while provider adapters handle authentication, request formats, streaming, tool calls, errors, usage, and provider-specific features.

## 4. Why Enterprises Care

- Applications should not be tightly coupled to one SDK.
- Providers differ in capability, cost, latency, and governance.
- Organizations may require regional or workload-specific routing.
- Fallback and comparison require consistent evidence.
- Central policy and telemetry reduce duplicated integration logic.

## 5. Terminology

| Term | Plain-English meaning |
|---|---|
| Provider adapter | Code translating a shared application contract into one provider's API. |
| Capability metadata | Facts describing whether a model supports tools, vision, structured output, or other features. |
| Model routing | Selecting an approved model from task, policy, quality, latency, and cost inputs. |
| Fallback | A controlled alternative when the preferred provider is unavailable or unsuitable. |
| Structured output | Model output constrained to a defined schema. |
| Streaming | Incremental delivery of model response events. |
| Rate limit | Provider restriction on request or token volume. |
| Token accounting | Recording input and output units used by a model. |
| Circuit breaker | A control that temporarily stops calls to a failing dependency. |
| Open-source serving | Operating model weights through self-managed or managed inference infrastructure. |

## 6. Reference Workflow

1. Runtime requests a capability, not an arbitrary model.
2. Policy determines allowed providers and regions.
3. Router evaluates capability, health, quality, latency, and cost.
4. Shared request is passed to a provider adapter.
5. Adapter translates authentication and request format.
6. Provider response or stream is normalized.
7. Usage, latency, safety, and errors are recorded.
8. Structured output is validated.
9. Fallback occurs only under explicit rules.
10. Evaluation compares provider behavior over time.

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

- Lowest-common-denominator abstraction
- Hidden provider differences
- Unsafe fallback
- Inconsistent safety controls
- Regional data-policy violations
- Retry storms
- Cost spikes
- Provider-specific error leakage
- Unmeasured routing

## 10. Metrics and Evidence

- Task success by provider and model
- Structured-output validity
- Tool-call correctness
- p50 and p95 latency
- Error rate
- Fallback rate
- Cost per successful task
- Safety-policy compliance
- Provider availability

## 11. Mental Notes

- Normalize common operations, not every capability.
- Routing requires policy and evaluation evidence.
- Fallback must preserve data and safety requirements.
- Open-source models add infrastructure ownership.
- Provider abstraction is an operational boundary, not only a class interface.

## 12. JD-Aligned Core Answers

### 30-Second Core Answer

I would place a capability-aware abstraction between the agent workflow and
model providers. The application uses a common request and response envelope,
while adapters declare supported models, structured output, tool calling,
regions, limits, and normalized errors. I would prove the contract first with
a deterministic mock provider before enabling any real provider call.

### 60-Second Core Answer

I avoid both hard-coding one provider and pretending all providers are
identical. The abstraction defines stable application-facing envelopes for
messages, context, structured-output requirements, tool declarations, usage,
latency, and errors. Each adapter publishes explicit capability metadata for
model families, context limits, regions, data-handling constraints, structured
output, and tool calling. Routing then uses policy, capability, evaluation,
latency, and cost evidence rather than brand preference. I would start with a
deterministic local mock that passes the complete contract suite, then gate real
OpenAI, Anthropic, or Vertex adapters independently. Retries and fallbacks are
bounded, and a fallback cannot weaken residency, safety, or authorization
requirements.

### Claim Defense

Architecture and next authorized lab phase. Real provider adapters and calls
are not yet implemented in this repository.

Likely interviewer challenge:

- What was your exact role?
- Which artifacts did you personally create?
- Was this architecture, local implementation, pilot, or production?
- Which stakeholders or client environment were involved?
- What measurable evidence supports the claim?
- What remains unimplemented or unverified?

## 13. Shadow-Experience Exercise

Design adapters for OpenAI, Anthropic, Vertex AI, and an open-source endpoint. Use mocked providers to compare normalized errors, usage, latency, and structured-output validation without sending external requests.

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

- Approve provider-integration authority.
- Define shared capability and request contracts.
- Implement mocked provider conformance tests.
- Implement provider adapters separately.
- Add secrets and regional policy controls.
- Add routing evaluation.
- Add timeouts, circuit breakers, and bounded fallback.
- Add usage and cost telemetry.

## 16. Official References

- https://platform.openai.com/docs/
- https://docs.anthropic.com/
- https://cloud.google.com/vertex-ai/generative-ai/docs

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

`multi-provider, OpenAI, Anthropic, Claude, Vertex, provider adapter, model routing, fallback, abstraction layer`

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
