        # Phase 12 — Client Engagement and Code-With Delivery

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

        ## 12. Sixty-Second Interview Answer

        > I begin by mapping stakeholders, the current workflow, the decision, evidence, authority, risk, and success measures. I then choose a thin slice with explicit exclusions and acceptance criteria. I review evidence frequently and use code-with sessions to expose integration constraints and build client ownership. The roadmap advances only when the prototype answers its intended question.

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
