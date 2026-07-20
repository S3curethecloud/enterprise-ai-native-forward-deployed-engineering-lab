# Post-Interview Implementation Resumption

## 1. Purpose

This document defines how to resume enterprise portfolio implementation after
the July 22, 2026 interview.

The interview-learning track does not replace the original engineering
roadmap. It preserves and enriches the knowledge needed to implement it.

## 2. Current Boundary

Current executable implementation:

- Phases 0–4 complete
- Phase 4 deterministic runtime complete
- Phase 4 closure CI passed
- Phases 5–17 implementation not started

Current learning status:

- Phase 5–17 tutorials drafted
- Terminology map drafted
- Experience-gap bridge drafted
- Shadow scenarios drafted
- Architecture talking points drafted
- Mock-interview guide drafted

## 3. Resumption Rule

Implementation does not resume automatically when the interview ends.

Before changing executable code:

1. Review the Phase 4 closure.
2. Review the Phase 5 tutorial.
3. Confirm the target Phase 5 scope.
4. Write a Phase 5 implementation design.
5. Define Phase 5 authority.
6. Define exclusions.
7. Define contracts.
8. Define tests and evidence.
9. Approve the implementation gate.
10. Change code only after those decisions are recorded.

## 4. Status Separation

Learning status and implementation status remain independent.

| Condition | Learning status | Implementation status |
|---|---|---|
| Tutorial exists | Drafted | Not started |
| Tutorial reviewed | Interview-ready | Not started |
| Design approved | Interview-ready | Authorized |
| Code added | Interview-ready | In progress |
| Local gates pass | Interview-ready | Locally validated |
| Exact-commit CI passes | Interview-ready | CI validated |
| Closure evidence recorded | Interview-ready | Complete |

## 5. Phase 5 Resumption

Phase 5 should implement permission-aware RAG and context engineering.

Initial authorized slice should remain read-only.

Candidate flow:

1. Validated diagnostic request
2. Validated identity context
3. Deterministic retrieval authorization
4. Synthetic evidence retrieval
5. Evidence reranking
6. Bounded context construction
7. Citation-backed structured result
8. Controlled abstention
9. Retrieval and response evaluation
10. Lifecycle trace evidence

Initial exclusions:

- Production data
- Cross-tenant retrieval
- Unrestricted document ingestion
- External tool execution
- Production mutation
- Autonomous remediation
- Unreviewed provider fallback
- Hidden access-policy decisions

## 6. Phase 5 Required Design Artifacts

Create:

- Retrieval source contract
- Document and chunk contract
- Metadata and classification contract
- Retrieval query contract
- Retrieval result contract
- Citation contract
- Context bundle contract
- Access-decision contract
- Evaluation case contract
- Retrieval trace contract
- Threat model
- Implementation gate

## 7. Phase 5 Required Tests

Test:

- Authorized retrieval
- Unauthorized source denial
- Cross-tenant denial
- Missing identity
- Missing policy decision
- Expired authorization
- Metadata-filter correctness
- Retrieval ordering
- Citation support
- Insufficient-evidence abstention
- Prompt-injection evidence
- Stale source
- Deleted source
- Context budget
- Sensitive telemetry redaction
- Deterministic failure behavior

## 8. Phase 5 Evidence Gate

Phase 5 is not complete until:

- Contracts are executable.
- Access filtering fails closed.
- Synthetic evaluation data is versioned.
- Retrieval metrics are reported.
- Citation validation is tested.
- Prompt-injection behavior is tested.
- No cross-tenant evidence is returned.
- No production credentials are required.
- Local quality gates pass.
- Container gates pass.
- Exact-commit CI passes.
- Documentation matches executable behavior.

## 9. Later-Phase Resumption

After Phase 5 closes:

- Phase 6 adds provider abstraction.
- Phase 7 adds typed tools.
- Phase 8 adds deterministic policy routing.
- Phase 9 adds human approval.
- Phase 10 adds model and workflow EvalOps.
- Phase 11 adds telemetry export and operational dashboards.
- Phase 12 adds a reusable code-with engagement exercise.
- Phase 13 adds executable cloud-native deployment artifacts.
- Phase 14 adds production-readiness evidence.
- Phase 15 adds a selected domain adaptation.
- Phase 16 adds reusable compound-system control-plane patterns.
- Phase 17 packages reusable assets, documentation, and client roadmaps.

Every phase receives:

- Design
- Authority
- Contracts
- Tests
- Local evidence
- CI evidence
- Closure
- Updated maturity claims

## 10. Repository Reuse Policy

Preserve:

- Interview tutorials
- Mental notes
- Shadow scenarios
- Official references
- Post-interview backlogs

Convert useful tutorial content into:

- Design inputs
- Acceptance criteria
- Threat-model questions
- Test cases
- Evaluation cases
- Operational requirements

Do not copy tutorial statements into maturity claims without executable
evidence.

## 11. Commit Policy

Keep commits separated by purpose:

- Tutorial content
- Design and authority
- Implementation
- CI remediation
- Closure evidence

Avoid combining unrelated phases or capability grants.

## 12. Final Resumption Decision

Current decision:

- Interview learning remains authorized.
- Phase 5 implementation remains unauthorized.
- No later implementation is authorized.
- Post-interview work begins with a Phase 5 design review.
