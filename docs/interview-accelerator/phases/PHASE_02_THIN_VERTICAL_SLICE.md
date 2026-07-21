# Phase 2 — Thin Vertical Slice

## 1. Interview Status

| Dimension | Status |
|---|---|
| Learning guide | Interview-ready |
| Portfolio evidence | Implemented and documented bounded portfolio slice |
| Claim posture | Bounded by the claim-defense section |
| Production claim | Not created by this guide |

## 2. Job-Description Connection

Rapid prototyping, concrete results, custom agent workflows, and moving from experimentation toward operational reality.

## 3. Plain-English Explanation

Build the smallest end-to-end workflow that crosses the important production boundaries and tests the riskiest assumptions.

## 4. Why Enterprises Care

- A broad prototype can hide integration and authority failures.
- A vertical slice produces early evidence across real architectural layers.
- Narrow scope reduces cost and blast radius while increasing learning speed.
- Stable interfaces from the slice can support incremental delivery.

## 5. Reference Workflow

`Validated request → identity and policy context → bounded orchestration → authorized evidence → safe result or abstention → trace and test evidence`

## 6. Architecture and Delivery Decisions

- Select one user, one decision, and one bounded evidence path.
- Include failure and abstention behavior in the first slice.
- Exclude high-risk write actions until their controls are independently proven.
- Treat the slice as production-shaped learning, not production readiness.

## 7. Thirty-Second Core Answer

I use a thin vertical slice to test the riskiest end-to-end path early. It includes one user, one bounded workflow, identity and policy context, retrieval, an orchestrated decision, a safe output, and trace evidence. It is deliberately narrow, but it crosses the real architectural layers so we learn whether the system can work before scaling its breadth.

## 8. Sixty-Second Core Answer

A thin vertical slice is not a throwaway chatbot. It is the smallest end-to-end workflow that exercises the important production boundaries. I define one user and business decision, a small authorized evidence set, typed request and response contracts, deterministic orchestration, explicit failure behavior, and trace evidence. In the incident-diagnostic lab, the slice supports read-only diagnosis and controlled abstention while excluding remediation and external providers. That gives stakeholders something concrete to evaluate and engineers early evidence about contracts, identity propagation, latency, and operability. If it fails, we learn cheaply. If it succeeds, its interfaces become the foundation for incremental expansion instead of a demo that must be rewritten.

## 9. Likely Interview Questions

- What is a thin vertical slice and why would you use one?
- How is a thin slice different from a POC?
- What would you include in the first agent workflow?
- How do you prevent scope explosion?

## 10. Interviewer Follow-Up Challenges

- What was the exact user and decision?
- Which layers were executable?
- What was deliberately excluded?
- What evidence showed the slice was successful?

## 11. Claim Defense

Verified bounded local portfolio slice. It is not an external customer production deployment and does not execute tools or provider calls.

When challenged, identify:

- Your exact role
- Whether the setting was client-facing, professional internal work, or portfolio work
- Stakeholders involved
- Artifacts you personally produced
- What was designed versus implemented
- Local, CI, prototype, pilot, or production status
- Measurable evidence
- Known limitations

## 12. Evidence You Can Name

- Typed request and response boundaries
- Bounded diagnostic scenario
- Explicit safe failure outcomes
- Phase gate and test evidence

## 13. Mock-Agent Retrieval Cues

Route questions containing these ideas to this guide:

`thin vertical slice, prototype, POC, MVP, first use case, reduce scope, rapid delivery, concrete results`

## 14. Answer Construction Rule

Lead with the decision or outcome. Explain the architecture or delivery logic.
Name one concrete artifact or control. State the honest boundary. Stop and let
the interviewer choose the follow-up.

## 15. Rapid Mental Note

**Problem → decision → bounded implementation or approach → evidence → honest limitation.**
