# Phase 12 — Enterprise Integration and Code-With Session

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

Client Engagement — workshops, POCs, code-with sessions, stakeholder trust, ambiguity, and adoption.

## 3. Plain-English Explanation

Forward-deployed engineering combines technical delivery with structured client collaboration. The engineer turns incomplete requirements into shared decisions, a bounded prototype, measurable evidence, and an adoption roadmap.

## 4. Why Enterprises Care

- Clients often know symptoms but not the correct technical problem.
- AI requests can hide workflow, data, authority, and adoption risks.
- Shared artifacts reduce misunderstanding.
- Code-with sessions transfer ownership.
- Trust increases when maturity and limitations are communicated honestly.

## 5. Terminology

| Term | Plain-English meaning |
|---|---|
| Stakeholder | A person or group affected by or responsible for the workflow. |
| Discovery workshop | A structured session that produces shared problem evidence. |
| Decision decomposition | Breaking a broad workflow into specific decisions. |
| Assumption register | A versioned list of unverified beliefs and validation plans. |
| POC | A bounded experiment answering a feasibility question. |
| Prototype | An early working artifact used to test value or design. |
| Code-with session | Collaborative implementation with client engineers. |
| Acceptance criterion | A testable condition for success. |
| Adoption | Sustained use, trust, ownership, and improvement. |
| Roadmap | A sequenced plan connecting outcomes, capabilities, dependencies, and risks. |

## 6. Reference Workflow

1. Identify stakeholders and decision owners.
2. Map the current workflow.
3. Identify delays, errors, handoffs, and evidence.
4. Decompose the target decision.
5. Inventory data and integration sources.
6. Define authority and risk.
7. Record assumptions.
8. Define measurable success.
9. Choose the smallest valuable slice.
10. Agree on explicit exclusions.
11. Prototype and review evidence.
12. Run code-with and handoff activities.
13. Update the roadmap from results.

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

- Technology-first discovery
- Unclear decision ownership
- Hidden stakeholder conflict
- Unverified data access
- POC without acceptance criteria
- Prototype presented as production
- Client dependency on the delivery team
- Executive and engineering language mismatch
- Adoption ignored until launch

## 10. Metrics and Evidence

- Workshop decisions completed
- Assumptions validated
- Time to bounded prototype
- Acceptance criteria passed
- User task time
- Human correction rate
- Client engineer participation
- Handoff readiness
- Adoption and satisfaction

## 11. Mental Notes

- Start with the decision, not the model.
- Ambiguity should become artifacts and questions.
- A POC must answer a specific question.
- A prototype reduces uncertainty; it does not prove production readiness.
- Code-with is both engineering and knowledge transfer.

## 12. JD-Aligned Core Answers

### 30-Second Core Answer

I use code-with sessions to turn architecture decisions into shared working
software. Before the session, I agree on the use case, interfaces, data and
identity prerequisites, success criteria, and rollback boundary. During it,
client engineers build and test the slice with me so ownership transfers rather
than remaining with an external prototype team.

### 60-Second Core Answer

For enterprise integration, I combine advisory work with hands-on delivery. I
first map existing APIs, identity, data, event, network, CI/CD, support, and
governance constraints. We define a bounded integration contract and prepare a
code-with session around one thin slice. In the session, we implement the
adapter or workflow together, run contract and failure tests, capture decisions,
and document how to operate and extend it. I make unresolved assumptions and
ownership explicit, including who supports the interface, rotates credentials,
reviews policy, and handles incidents. The outcome is not only code; it is
client capability, trusted adoption, and a prioritized roadmap based on evidence
from their environment.

### Claim Defense

Use real professional collaboration examples where available. The lab provides
the integration playbook, not proof of an Accenture client session.

Likely interviewer challenge:

- What was your exact role?
- Which artifacts did you personally create?
- Was this architecture, local implementation, pilot, or production?
- Which stakeholders or client environment were involved?
- What measurable evidence supports the claim?
- What remains unimplemented or unverified?

## 13. Shadow-Experience Exercise

Facilitate the simulated incident-diagnostic discovery workshop in the shadow-scenario guide. Produce a stakeholder map, current workflow, decision decomposition, assumptions, success measures, slice, exclusions, and follow-up roadmap.

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

- Create reusable workshop agenda.
- Create discovery question bank.
- Create POC decision template.
- Create code-with exercise.
- Create adoption and handoff checklist.
- Practice executive and engineering readouts.
- Run a recorded mock workshop.

## 16. Official References

- https://www.gov.uk/service-manual/agile-delivery/how-the-discovery-phase-works

## 17. Learning Gate

The phase is interview-ready when the learner can:

- Define the terminology without reading.
- Explain the workflow and authority boundaries.
- Identify at least five failure modes.
- Select meaningful metrics.
- Give the sixty-second answer naturally.
- Complete the shadow exercise honestly.
- Distinguish tutorial knowledge from implementation evidence.

## 17A. Mock-Agent Retrieval Cues

Route questions containing these topics to this phase:

`client workshop, code-with, enterprise integration, stakeholder, adoption, trusted advisor, ecosystem partner`

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
