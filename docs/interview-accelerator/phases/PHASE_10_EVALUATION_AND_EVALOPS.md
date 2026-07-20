        # Phase 10 — Evaluation and EvalOps

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

        Measure and Improve — accuracy, latency, safety, cost, evaluation harnesses, and evidence-based release decisions.

        ## 3. Plain-English Explanation

        Evaluation measures whether the workflow behaves as intended. EvalOps makes datasets, rubrics, runs, thresholds, regressions, and release evidence repeatable across versions.

        ## 4. Why Enterprises Care

        - Plausible output is not proof of correct behavior.
- Model and retrieval changes can create regressions.
- Components fail in different ways.
- Quality must be balanced with latency, safety, and cost.
- Release decisions need reproducible evidence.

        ## 5. Terminology

        | Term | Plain-English meaning |
|---|---|
| Golden dataset | Versioned cases with expected behavior or review criteria. |
| Rubric | Rules used to score an output. |
| Groundedness | Degree to which claims are supported by supplied evidence. |
| Hallucination | Unsupported or fabricated model content. |
| Regression | Previously acceptable behavior becoming worse after a change. |
| Offline evaluation | Evaluation against prepared datasets before or outside live traffic. |
| Online evaluation | Measurement on live or production-like workflow behavior. |
| Model-based grader | A model used to score output under a defined rubric. |
| Human evaluation | Review performed by qualified people. |
| Release gate | A threshold that must pass before promotion. |
| EvalOps | Operational discipline for versioned and repeatable evaluation. |

        ## 6. Reference Workflow

        1. Define the business outcome.
2. Decompose component and end-to-end behaviors.
3. Create versioned cases and expected results.
4. Define metrics, rubrics, and thresholds.
5. Run retrieval, generation, policy, and tool evaluations.
6. Measure latency, safety, and cost.
7. Record model, prompt, data, and configuration versions.
8. Compare candidate with baseline.
9. Review failures and uncertainty.
10. Allow or block release based on evidence.
11. Monitor online behavior for drift.

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

        - Unrepresentative test set
- Data leakage into evaluation
- Subjective rubric
- Uncalibrated model grader
- Average scores hiding critical failures
- Ignoring policy and tool behavior
- Optimizing one metric at the expense of users
- No version lineage
- Testing only happy paths

        ## 10. Metrics and Evidence

        - Task success
- Retrieval recall and precision
- Groundedness
- Citation correctness
- Tool-selection accuracy
- Policy compliance
- Safety violation rate
- p50, p95, and p99 latency
- Token and infrastructure cost
- Cost per successful task
- Human correction rate

        ## 11. Mental Notes

        - Evaluate components and the complete workflow.
- A high average cannot excuse a critical safety failure.
- Version datasets, rubrics, prompts, models, and policies.
- Use human review to calibrate model-based graders.
- Release evidence should be reproducible.

        ## 12. Sixty-Second Interview Answer

        > I treat evaluation as release engineering. I define versioned cases and thresholds for retrieval, groundedness, citations, tools, policy, safety, latency, and cost. I record model, prompt, dataset, and configuration lineage, compare candidates to a baseline, calibrate model graders with human review, and fail the release when required evidence is missing.

        ## 13. Shadow-Experience Exercise

        Create a synthetic incident dataset with supported diagnosis, insufficient evidence, policy denial, invalid citations, timeout, and unsafe tool-request cases. Score the current deterministic parts and design the future model evaluation.

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

        - Define end-to-end task taxonomy.
- Create versioned golden dataset.
- Define component metrics.
- Implement retrieval evaluation.
- Implement response and citation evaluation.
- Calibrate model graders.
- Add latency, safety, and cost reports.
- Add CI release thresholds.
- Add online drift monitoring.

        ## 16. Official References

        - https://platform.openai.com/docs/guides/evals
- https://cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview

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
