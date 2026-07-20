        # Phase 9 — Human Approval and Trusted Execution

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

        Enterprise agent governance — human review, approval, separation of duties, and controlled execution.

        ## 3. Plain-English Explanation

        Human approval is a scoped, recorded authorization for a specific action under specific conditions. It is not an unlimited button that transfers all responsibility to a person.

        ## 4. Why Enterprises Care

        - High-risk actions need accountable human judgment.
- Approvers need evidence and understandable consequences.
- Scope and expiry prevent approval reuse.
- Separation of duties reduces self-approval risk.
- Revalidation protects against changed state.

        ## 5. Terminology

        | Term | Plain-English meaning |
|---|---|
| Human in the loop | A workflow intentionally pauses for human judgment. |
| Approval scope | The exact resource, action, parameters, and environment authorized. |
| Approval expiry | The time after which approval is no longer valid. |
| Four-eyes control | A sensitive action requires review by a second person. |
| Separation of duties | Requesting, approving, and executing are assigned to distinct roles. |
| Revalidation | Checking current state and authority immediately before execution. |
| Revocation | Withdrawal of previously granted approval. |
| Escalation | Routing a decision to a more appropriate authority. |
| Nonrepudiation | Evidence connecting an accountable actor to an action. |

        ## 6. Reference Workflow

        1. Workflow creates a bounded recommendation.
2. System calculates action risk.
3. Approval request includes evidence, scope, and consequence.
4. Authorized approver reviews the request.
5. Decision records identity, time, scope, reason, and expiry.
6. Runtime resumes only from the expected state and version.
7. Policy and current state are revalidated.
8. Execution occurs with scoped authority.
9. Outcome and approval lineage are recorded.
10. Expired, revoked, or mismatched approval stops the workflow.

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

        - Approval fatigue
- Rubber-stamp behavior
- Self-approval
- Approval reuse
- Missing evidence
- Changed state after approval
- Unclear consequences
- Unauthorized approver
- Sensitive data exposure in the approval view

        ## 10. Metrics and Evidence

        - Approval response time
- Approval and denial rate
- Expired-approval rate
- Revocation rate
- Self-approval rejection
- Post-approval state-conflict rate
- Human override rate
- Incident rate after approval

        ## 11. Mental Notes

        - Human review is a control, not a substitute for system design.
- Approval must bind resource, action, parameters, and expiry.
- Revalidate policy and state before execution.
- High-risk actions may require two distinct people.
- Record what evidence the approver saw.

        ## 12. Sixty-Second Interview Answer

        > I model approval as a typed, scoped, expiring authorization. The approver sees the recommendation, evidence, consequence, and exact action. The decision records identity and reason. Before execution, the runtime rechecks state version, policy, approval scope, and expiry. Self-approval, stale approval, and changed-state execution fail closed.

        ## 13. Shadow-Experience Exercise

        Design an approval record for a production rollback while keeping execution disabled. Test wrong approver, expired approval, changed workflow version, revoked approval, and missing evidence.

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

        - Approve approval-workflow implementation.
- Define approver identity and role model.
- Define approval request and decision contracts.
- Add scope, expiry, and revocation.
- Add separation-of-duties rules.
- Add pause and resume checkpoints.
- Add pre-execution revalidation.
- Add approval telemetry and audit history.

        ## 16. Official References

        - https://csrc.nist.gov/glossary/term/separation_of_duty

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
