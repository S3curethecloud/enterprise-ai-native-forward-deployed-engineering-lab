# Supplemental Guide — Compound AI, Agent Registries, and Event Streams

## 1. Status

| Dimension | Status |
|---|---|
| Learning guide | Drafted |
| Interview review | Pending |
| Enterprise implementation | Not started |
| Implementation authority | Supplemental interview learning only |

This document teaches the phase. It does not implement or enable the
capability.

## 2. Job-Description Connection

Bonus qualifications — enterprise agentic engineering, compound AI systems, orchestration frameworks, registries, streams, the AI-native paradigm, and multi-industry delivery.

## 3. Plain-English Explanation

A compound AI system combines models with retrieval, rules, policies, state, tools, evaluation, observability, infrastructure, humans, and enterprise integrations. Registries govern available capabilities, while streams distribute lifecycle events.

## 4. Why Enterprises Care

- A model alone cannot satisfy enterprise requirements.
- Many teams need discovery, ownership, versioning, and governance.
- Long-running workflows benefit from durable events and replay.
- Reusable control planes reduce duplicated integration.
- AI-native engineering must retain cloud-native discipline.

## 5. Terminology

| Term | Plain-English meaning |
|---|---|
| Compound AI | A system using multiple interacting AI and software components. |
| Orchestration framework | A tool for defining and running workflow state and transitions. |
| Agent registry | A governed catalog of agent capabilities and lifecycle metadata. |
| Tool registry | A governed catalog of external capabilities. |
| Model registry | A catalog of approved model versions and evidence. |
| Control plane | Management layer for policy, registry, configuration, and lifecycle. |
| Data plane | Runtime path that processes actual requests. |
| Event stream | An ordered or partitioned sequence of events consumed over time. |
| Event sourcing | Using an event history as the source for reconstructing state. |
| Consumer group | Consumers coordinating work from a stream. |
| AI-native | Architecture blending model capabilities with cloud-native engineering. |

## 6. Reference Workflow

1. Register approved models, agents, and tools.
2. Attach owners, contracts, policy, and evaluation status.
3. Runtime discovers only authorized capabilities.
4. Control plane distributes versioned configuration.
5. Data plane processes the workflow.
6. Lifecycle events are published to a governed stream.
7. Audit, evaluation, security, cost, and observability consume events.
8. Idempotent consumers handle duplicates.
9. Replay reconstructs behavior.
10. Governance deprecates unsafe or obsolete versions.

## 7. Connection to the Incident-Diagnostic Lab

Phases 0–4 provide discovery, a thin slice, typed contracts, service
boundaries, deterministic state, budgets, stops, checkpoints, replay,
lifecycle traces, tests, containers, and CI evidence.

This phase describes a future capability or delivery practice. It does
not change the executable repository boundary.

Current status:

- The phase is not implemented.
- No external capability is enabled.
- Phase 4 remains the latest executable implementation.
- Post-interview work requires a new design and implementation gate.

## 8. Authority and Security Boundaries

- Models do not grant access or execution authority.
- Missing authority fails closed.
- Inputs and outputs require typed validation.
- Sensitive data must be minimized.
- External dependencies require timeout and failure behavior.
- High-risk actions remain human-controlled.
- Evidence must distinguish facts, inference, and uncertainty.
- Documentation must distinguish professional, portfolio, and simulated work.

## 9. Important Risks

- Registry metadata drift
- Unowned capabilities
- Schema incompatibility
- Unauthorized discovery
- Duplicate or out-of-order events
- Sensitive stream payloads
- Framework lock-in
- Control-plane compromise
- Unmeasured agent versions

## 10. Metrics and Evidence

- Registered capability ownership
- Contract compatibility
- Evaluation status coverage
- Deprecated-version usage
- Event delivery latency
- Duplicate processing
- Replay correctness
- Policy attachment coverage
- Capability adoption and reuse

## 11. Mental Notes

- A compound system is more than a model call.
- Framework APIs matter less than workflow guarantees.
- A registry is a governance control plane.
- Streams require idempotency and schema evolution.
- AI-native extends cloud-native; it does not replace it.

## 12. Sixty-Second Interview Answer

> I view enterprise agents as compound systems. Models provide reasoning, while retrieval, state, policy, tools, evaluation, observability, infrastructure, and humans make the workflow useful and governable. At scale, registries provide ownership, contracts, policy, and evaluation metadata, while event streams decouple audit, telemetry, evaluation, security, and recovery consumers.

## 13. Shadow-Experience Exercise

Design a control-plane registry for the incident-diagnostic agent, its tools, and provider adapters. Define lifecycle events and consumers for audit, evaluation, security, cost, and replay. Label the work as architecture, not production implementation.

Required disclosure:

> This is a learning, architecture, or portfolio exercise. It is not a
> production client deployment unless separately supported by a real
> professional example.

## 14. Interview Questions

- What business problem does this phase solve?
- Which responsibilities belong to software, models, humans, and operators?
- What is the most dangerous failure mode?
- What evidence is required before release?
- Which metrics demonstrate value?
- How does the design change in a regulated environment?
- Which tradeoff would you discuss with a client?
- What would you prototype first?
- What separates the prototype from production?
- What can be reused across clients?

## 15. Post-Interview Implementation Backlog

- Define capability metadata and ownership.
- Define registry API and lifecycle.
- Define event schemas and sensitive-data rules.
- Select delivery and ordering semantics.
- Implement idempotent consumers.
- Integrate policy and evaluation status.
- Add deprecation and compatibility controls.
- Test replay and governance failure modes.

## 16. Official References

- https://opentelemetry.io/docs/concepts/context-propagation/
- https://kafka.apache.org/documentation/

## 17. Learning Gate

The phase is interview-ready when the learner can:

- Define the terminology without reading.
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
