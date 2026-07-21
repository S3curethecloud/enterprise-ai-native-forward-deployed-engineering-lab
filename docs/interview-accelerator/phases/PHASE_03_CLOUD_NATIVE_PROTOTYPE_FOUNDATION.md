# Phase 3 — Cloud-Native Prototype Foundation

## 1. Interview Status

| Dimension | Status |
|---|---|
| Learning guide | Interview-ready |
| Portfolio evidence | Implemented and exact-commit CI verified |
| Claim posture | Bounded by the claim-defense section |
| Production claim | Not created by this guide |

## 2. Job-Description Connection

Python, APIs, microservices, Docker, CI/CD, health checks, cloud-native systems, and net-new platform engineering.

## 3. Plain-English Explanation

Create production-shaped service and delivery foundations before introducing probabilistic model behavior.

## 4. Why Enterprises Care

- Unstructured prototypes accumulate hidden dependencies and cannot be integrated safely.
- Strict contracts reduce ambiguity between services and teams.
- Health, readiness, isolation, and CI evidence are required for supportable systems.
- A production-shaped prototype makes later cloud deployment incremental.

## 5. Reference Workflow

`Contract models → bounded FastAPI services → separate identities → health and readiness → locked dependencies → container isolation → CI quality and runtime verification`

## 6. Architecture and Delivery Decisions

- Use fail-closed validation and forbid unknown contract fields.
- Separate gateway, runtime, and evidence service identities.
- Lock dependencies and verify the installed environment.
- Call the foundation production-shaped, not production-ready.

## 7. Thirty-Second Core Answer

I make the prototype production-shaped from the beginning: strict Python and Pydantic contracts, bounded FastAPI services, separate identities, health and readiness checks, locked dependencies, isolated containers, and CI quality gates. That does not make it production-ready, but it prevents the prototype from depending on hidden local behavior that cannot survive integration.

## 8. Sixty-Second Core Answer

For an AI-native prototype, I establish cloud-native engineering discipline before adding probabilistic behavior. I use strict Pydantic models, fail-closed validation, correlation identifiers, separate gateway, runtime, and evidence service identities, health and readiness endpoints, hash-locked dependencies, and Docker isolation. CI runs linting, formatting, strict typing, tests, image builds, service startup, and runtime restriction checks. In this lab those controls are executable and CI verified. The distinction I make is that this is a production-shaped foundation, not a production deployment. Production still requires workload-specific scaling, secrets, infrastructure, SLOs, threat modeling, and operational ownership, but the prototype already teaches us how the platform will be integrated and supported.

## 9. Likely Interview Questions

- How do you make an AI prototype enterprise-ready?
- What cloud-native foundations do you establish first?
- What belongs in CI for an agent platform?
- How do you distinguish production-shaped from production-ready?

## 10. Interviewer Follow-Up Challenges

- Which services and identities did you create?
- What exactly did CI validate?
- Was the system deployed to cloud production?
- What would still block production release?

## 11. Claim Defense

Verified local and GitHub Actions portfolio evidence. Use separate professional examples for production cloud deployments and customer environments.

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

- Strict Pydantic contracts and FastAPI boundaries
- Health and readiness endpoints
- Hash-locked development dependencies
- Docker and Compose isolation
- CI quality, container build, startup, and health evidence

## 13. Mock-Agent Retrieval Cues

Route questions containing these ideas to this guide:

`cloud native, FastAPI, Pydantic, microservices, Docker, CI/CD, prototype, production-shaped, APIs`

## 14. Answer Construction Rule

Lead with the decision or outcome. Explain the architecture or delivery logic.
Name one concrete artifact or control. State the honest boundary. Stop and let
the interviewer choose the follow-up.

## 15. Rapid Mental Note

**Problem → decision → bounded implementation or approach → evidence → honest limitation.**
