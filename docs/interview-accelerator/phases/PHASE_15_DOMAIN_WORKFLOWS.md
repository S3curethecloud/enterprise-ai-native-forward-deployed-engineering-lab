        # Phase 15 — Domain-Specific Workflows

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

        Domain-Specific Workflows — tailoring agent applications to finance, healthcare, retail, and other enterprise domains.

        ## 3. Plain-English Explanation

        Domain adaptation preserves reusable architecture while changing the users, decisions, evidence, terminology, regulations, authority, risk thresholds, approvals, and success measures.

        ## 4. Why Enterprises Care

        - A generic workflow may ignore domain-specific harm.
- Data sensitivity and authority vary by industry.
- Users interpret explanations through domain terminology.
- Metrics must reflect the actual decision.
- Regulation and operational practice shape acceptable automation.

        ## 5. Terminology

        | Term | Plain-English meaning |
|---|---|
| Domain | A field with specialized users, workflows, data, rules, and risks. |
| Control objective | The outcome a governance or security control must achieve. |
| Data classification | A category representing sensitivity and handling rules. |
| Provenance | Evidence of where information came from and how it changed. |
| Segregation of duties | Division of sensitive steps across different actors. |
| Minimum necessary | Access limited to information needed for the purpose. |
| Human judgment | A decision retained for a qualified person. |
| Domain metric | A measure tied to the field's actual outcome. |

        ## 6. Reference Workflow

        1. Identify domain stakeholders and decision owners.
2. Map the current domain workflow.
3. Identify authoritative evidence.
4. Classify data and access.
5. Identify regulatory and organizational controls.
6. Assess failure consequences.
7. Define required human judgment.
8. Adapt contracts, policy, evaluation, and telemetry.
9. Prototype with representative synthetic cases.
10. Validate with domain experts.

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

        - Generic architecture ignoring domain harm
- Incorrect regulatory assumptions
- Unauthorized sensitive-data access
- Model output treated as professional judgment
- Unrepresentative evaluation cases
- Domain terminology errors
- Missing provenance
- Automation bias

        ## 10. Metrics and Evidence

        - Domain task success
- Expert correction rate
- Policy compliance
- Data-access correctness
- Evidence provenance
- Safety escalation
- Decision time
- User adoption
- Domain-specific cost of error

        ## 11. Mental Notes

        - Preserve control patterns; adapt domain facts.
- Domain experts validate meaning and harm.
- Healthcare is the strongest direct domain evidence in the résumé.
- Finance and retail claims must match real experience.
- Human judgment boundaries vary by domain.

        ## 12. Sixty-Second Interview Answer

        > I start with the reusable controls—identity, policy, evidence, orchestration, evaluation, observability, and human governance—then adapt them to the domain's users, data, decisions, regulations, failure consequences, and metrics. Healthcare may emphasize PHI and clinician sign-off, finance segregation of duties and audit lineage, and retail latency, inventory freshness, fraud, and cost.

        ## 13. Shadow-Experience Exercise

        Complete the finance, healthcare, and retail scenarios. For each, identify user, decision, evidence, identity, policy, risk, approval, metric, and safe failure behavior.

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

        - Choose implementation domain after interview.
- Engage domain experts.
- Create domain data and authority model.
- Create representative evaluation dataset.
- Adapt contracts and terminology.
- Define domain safety and escalation.
- Run expert review.
- Document reusable and domain-specific elements.

        ## 16. Official References

        - https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html
- https://www.nist.gov/itl/ai-risk-management-framework

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
