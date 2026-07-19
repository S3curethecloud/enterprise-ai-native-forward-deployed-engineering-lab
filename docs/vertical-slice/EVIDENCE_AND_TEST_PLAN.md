# Thin Vertical Slice Evidence and Test Plan

## Document Purpose

This document defines how the Citation-Backed Incident Diagnostic Assistant will eventually be tested and how claims about its behavior must be supported.

The plan connects:

- Slice requirements
- Acceptance criteria
- Interface contracts
- System boundaries
- Failure modes
- Test families
- Datasets
- Test environments
- Evidence artifacts
- Review ownership
- Promotion decisions

This is an evidence design, not an implementation or completed evaluation report.

No application runtime, model integration, retrieval pipeline, tool execution, infrastructure mutation, or production deployment is authorized by this document.

---

## Source Documents

The plan is governed by:

- `docs/governance/CLAIM_EVIDENCE_AND_AUTHORITY_RULES.md`
- `docs/discovery/SUCCESS_MEASURES.md`
- `docs/vertical-slice/VERTICAL_SLICE_DEFINITION.md`
- `docs/vertical-slice/ACCEPTANCE_CRITERIA.md`
- `docs/vertical-slice/INTERFACE_CONTRACTS.md`
- `docs/vertical-slice/SYSTEM_BOUNDARIES.md`
- `docs/vertical-slice/FAILURE_MODE_CATALOG.md`

A test result cannot expand the authority granted by these sources.

---

## Evidence Principles

1. Every material claim must identify its evidence.
2. Evidence must be reproducible or independently reviewable.
3. Passing examples must not conceal failing examples.
4. P0 safety failures must be reported individually.
5. Aggregate scores must not average away critical failures.
6. Test inputs, configurations, and expected outputs must be versioned.
7. Human judgments must use a documented rubric.
8. Model-assisted evaluation must not be the only judge of model behavior.
9. Test and production evidence must remain distinguishable.
10. Screenshots are supplementary, not primary proof.
11. Absence of detected failure is not proof of impossibility.
12. Documentation proves design maturity, not runtime maturity.
13. Synthetic evidence must be labeled synthetic.
14. Results must record known limitations.
15. Failed evidence gates block the corresponding claim.

---

## Evidence Maturity Levels

| Level | Name | Meaning |
|---|---|---|
| EV-0 | Proposed | Behavior or control has only been described |
| EV-1 | Reviewed | Design has been reviewed against requirements |
| EV-2 | Locally demonstrated | Behavior runs locally with retained output |
| EV-3 | Repeatedly tested | Automated tests pass across defined datasets |
| EV-4 | Integrated | Behavior is verified across real component boundaries |
| EV-5 | Operationally exercised | Failure, recovery, observability, and ownership are exercised |
| EV-6 | Release-evidenced | Promotion requirements pass in the target release environment |

During Phase 2, artifacts may reach EV-0 or EV-1 only.

---

## Claim Classes

| Claim class | Example | Minimum future evidence |
|---|---|---|
| Design claim | Authorization is separated from generation | Reviewed architecture and contract |
| Implementation claim | Request schema is enforced | Executable test and source revision |
| Integration claim | Identity context reaches policy correctly | Integration test and trace |
| Quality claim | Recommendations are evidence-grounded | Versioned evaluation dataset and report |
| Security claim | Unauthorized sources are denied | Negative and adversarial tests |
| Reliability claim | Dependency failure is handled safely | Failure-injection evidence |
| Operational claim | Behavior can be reconstructed | Trace and runbook evidence |
| Production-readiness claim | Slice is ready for staged release | Complete readiness evidence package |
| Business-outcome claim | Investigation time improved | Approved baseline and comparative measurement |

A lower evidence class cannot support a higher-maturity claim.

---

## Test-Level Model

| Level | Test level | Primary purpose |
|---|---|---|
| TL-01 | Static validation | Validate documents, schemas, configuration, and policy syntax |
| TL-02 | Unit testing | Verify isolated deterministic behavior |
| TL-03 | Contract testing | Verify producers and consumers enforce interfaces |
| TL-04 | Component testing | Verify one bounded runtime component |
| TL-05 | Integration testing | Verify behavior across component boundaries |
| TL-06 | End-to-end testing | Verify the complete thin-slice workflow |
| TL-07 | Evaluation testing | Measure retrieval and generated behavior |
| TL-08 | Adversarial testing | Exercise attacks and authority violations |
| TL-09 | Failure-injection testing | Exercise outages, invalid dependencies, and recovery |
| TL-10 | Operational exercise | Verify ownership, evidence, support, and rollback behavior |

---

## Planned Test Suites

| Suite ID | Test suite | Primary coverage | Required level |
|---|---|---|---|
| TS-01 | Request validation | CT-01, AC-01–AC-05, FM-01–FM-04 | TL-02, TL-03 |
| TS-02 | Identity propagation | CT-02, AC-06–AC-07, FM-05–FM-08 | TL-03, TL-05 |
| TS-03 | Authorization enforcement | CT-03, AC-08–AC-14, FM-09–FM-18 | TL-02, TL-05, TL-08 |
| TS-04 | Permission-aware retrieval | CT-04, AC-15–AC-18, FM-16–FM-27 | TL-04, TL-05, TL-07 |
| TS-05 | Evidence sufficiency | AC-19–AC-20, FM-19–FM-22 | TL-07 |
| TS-06 | Citation validation | CT-04, CT-05, AC-15–AC-21, FM-25–FM-33 | TL-03, TL-07 |
| TS-07 | Response validation | CT-05, AC-21–AC-23, AC-31–AC-38 | TL-02, TL-03 |
| TS-08 | Prompt-injection resistance | BD-07–BD-09, AC-25–AC-26, FM-23–FM-24 | TL-08 |
| TS-09 | Sensitive-data protection | AC-09, AC-27, AC-42, FM-17–FM-18, FM-38–FM-39 | TL-08 |
| TS-10 | Dependency resilience | AC-28–AC-30, FM-19, FM-28–FM-30, FM-42–FM-45 | TL-09 |
| TS-11 | Abstention behavior | AC-19–AC-20, AC-33, FM-20–FM-22, FM-34–FM-35 | TL-06, TL-07 |
| TS-12 | Recommendation boundary | AC-12–AC-14, AC-22–AC-24, FM-13–FM-14, FM-36–FM-37 | TL-06, TL-08 |
| TS-13 | Lifecycle observability | CT-07, AC-32, AC-41–AC-46, FM-39–FM-43 | TL-05, TL-10 |
| TS-14 | Human usefulness | AC-34–AC-38, AC-47 | TL-07 |
| TS-15 | Repeatability and regression | AC-44, AC-48–AC-49 | TL-07 |
| TS-16 | Scope and authority review | AC-13–AC-14, AC-24, AC-50, FM-47–FM-50 | TL-01, TL-10 |

---

## Dataset Inventory

| Dataset ID | Dataset | Purpose | Expected content |
|---|---|---|---|
| DS-01 | Valid diagnostic requests | Verify core successful path | Supported services with complete fields |
| DS-02 | Invalid request corpus | Verify schema rejection | Missing, malformed, oversized, and unsupported fields |
| DS-03 | Identity boundary corpus | Verify identity handling | Valid, expired, missing, mismatched, and delegated contexts |
| DS-04 | Authorization matrix | Verify resource isolation | Subjects, roles, resources, operations, and expected decisions |
| DS-05 | Authorized runbook corpus | Verify retrieval and citations | Versioned synthetic or approved runbook passages |
| DS-06 | Evidence-insufficiency corpus | Verify abstention | Sparse, irrelevant, or empty evidence |
| DS-07 | Evidence-conflict corpus | Verify conflict handling | Materially conflicting approved passages |
| DS-08 | Stale-evidence corpus | Verify freshness behavior | Current, stale, and unknown-freshness passages |
| DS-09 | Injection corpus | Verify instruction isolation | Direct and indirect prompt-injection samples |
| DS-10 | Citation challenge set | Verify claim-to-evidence lineage | Supported, unsupported, and fabricated citations |
| DS-11 | Prohibited-action corpus | Verify recommendation-only boundary | Requests to restart, deploy, modify, or approve |
| DS-12 | Sensitive-data corpus | Verify redaction and non-disclosure | Synthetic credentials and classified markers |
| DS-13 | Dependency-failure scenarios | Verify degraded behavior | Timeouts, invalid responses, and service outages |
| DS-14 | Diagnostic-quality set | Verify usefulness and grounding | Labeled incident-and-evidence cases |
| DS-15 | Regression suite | Prevent behavioral regression | Stable representative subset of prior datasets |

---

## Dataset Governance

Every dataset must record:

- Dataset identifier
- Version
- Purpose
- Owner
- Source
- Creation method
- Synthetic or real classification
- Data sensitivity
- Allowed environments
- Expected outcomes
- Labeling method
- Reviewer qualifications
- Known limitations
- Retention requirement
- Approval status

A dataset must not include production data merely because it is realistic.

---

## Dataset Partitioning

Where statistical evaluation applies, datasets must be separated into:

- Development set
- Evaluation set
- Regression set
- Adversarial set
- Holdout set where justified

Rules:

- Evaluation cases must not be copied into prompts as examples.
- Holdout cases must be protected from tuning leakage.
- Regression cases must retain stable expected outcomes.
- Adversarial cases must remain separately reportable.
- Safety cases must not be diluted by ordinary cases.
- Duplicate or near-duplicate cases must be detected.

---

## Test Environment Classes

| Environment | Purpose | Permitted data | Production authority |
|---|---|---|---|
| Local development | Component development and unit tests | Synthetic data | None |
| Local integration | Contract and workflow integration | Synthetic or approved test data | None |
| Shared test | Multi-component validation | Approved nonproduction data | None |
| Security test | Adversarial and failure testing | Controlled test fixtures | None |
| Pre-release | Release-candidate evidence | Approved release-test data | None unless separately governed |
| Production | Future staged operation | Separately approved | Not authorized in Phase 2 |

Passing locally does not prove production readiness.

---

## Evidence Artifact Inventory

| Artifact ID | Evidence artifact | Produced by | Supports |
|---|---|---|---|
| EA-01 | Schema-validation report | TS-01 and TS-07 | Request and response enforcement |
| EA-02 | Contract-test report | TS-01–TS-07 | Interface compatibility |
| EA-03 | Identity-propagation trace | TS-02 | Identity boundary |
| EA-04 | Policy-decision report | TS-03 | Deterministic authorization |
| EA-05 | Retrieval-access report | TS-04 | Source isolation |
| EA-06 | Citation-lineage report | TS-06 | Evidence grounding |
| EA-07 | Abstention evaluation | TS-05 and TS-11 | Safe insufficient-evidence behavior |
| EA-08 | Prompt-injection report | TS-08 | Instruction isolation |
| EA-09 | Sensitive-data report | TS-09 | Leakage prevention |
| EA-10 | Dependency-failure report | TS-10 | Safe degradation and recovery |
| EA-11 | Recommendation-boundary report | TS-12 | No execution authority |
| EA-12 | Lifecycle trace package | TS-13 | Reconstruction and observability |
| EA-13 | Human-usefulness report | TS-14 | Workflow value |
| EA-14 | Regression report | TS-15 | Repeatable behavior |
| EA-15 | Authority-review record | TS-16 | Scope and capability boundary |
| EA-16 | Consolidated gate report | All applicable suites | Phase or release decision |

---

## Required Test Record

Every test execution must record:

| Field | Required |
|---|---:|
| `test_run_id` | Yes |
| `test_case_id` | Yes |
| `suite_id` | Yes |
| `dataset_id` | Conditional |
| `dataset_version` | Conditional |
| `source_revision` | Yes |
| `contract_versions` | Yes |
| `policy_version` | Conditional |
| `model_provider` | Conditional |
| `model_version` | Conditional |
| `retrieval_configuration` | Conditional |
| `test_environment` | Yes |
| `expected_outcome` | Yes |
| `actual_outcome` | Yes |
| `result` | Yes |
| `trace_id` | Conditional |
| `failure_mode_ids` | Conditional |
| `artifact_references` | Yes |
| `executed_at` | Yes |
| `reviewer` | Conditional |
| `known_limitations` | Yes |

Conditional fields are required whenever the tested behavior depends on that field.

---

## Test Result Definitions

| Result | Meaning |
|---|---|
| Pass | Actual outcome satisfies the predefined expected outcome |
| Fail | Actual outcome violates the expected outcome |
| Blocked | A prerequisite prevents execution |
| Invalid | Test evidence is incomplete, corrupted, or not reproducible |
| Not applicable | Excluded through documented review |
| Inconclusive | Evidence cannot support a pass or fail decision |

Blocked, invalid, and inconclusive tests are not passes.

---

## Human-Evaluation Plan

Human evaluation must use a documented rubric covering:

- Diagnostic usefulness
- Evidence relevance
- Citation correctness
- Observation-versus-inference clarity
- Limitation disclosure
- Recommendation scope
- Operational clarity
- Unsafe implication
- Appropriate abstention
- Overall trustworthiness

Human reviewers must:

- Have relevant domain knowledge
- Receive consistent instructions
- Review blinded samples where practical
- Record independent judgments
- Disclose conflicts of interest
- Resolve material disagreement through an approved process
- Avoid treating fluency as correctness

---

## Automated-Evaluation Plan

Automated evaluation may measure:

- Schema validity
- Identifier consistency
- Citation resolution
- Evidence overlap
- Retrieval precision and recall
- Grounded-claim rate
- Abstention classification
- Latency
- Token usage
- Cost
- Trace completeness
- Prohibited phrase or action patterns
- Secret-detection results

Automated evaluation must not independently authorize release when human or governance review is required.

---

## Adversarial-Test Plan

Adversarial testing must include:

- User-supplied prompt injection
- Indirect injection in retrieved documents
- Requests to ignore authorization
- Requests to reveal restricted sources
- Cross-tenant resource identifiers
- Fabricated approval statements
- Role and identity spoofing
- Citation fabrication pressure
- Requests to conceal limitations
- Requests to execute production actions
- Encoded or obfuscated malicious instructions
- Oversized and malformed inputs
- Secret extraction attempts
- Retry-based scope escalation
- Conflicting system and evidence instructions

Every successful boundary violation is reported individually.

---

## Failure-Injection Plan

Failure injection must exercise:

- Identity-provider timeout
- Policy-service timeout
- Policy invalid response
- Evidence-source timeout
- Evidence-source malformed response
- Empty retrieval
- Model-provider timeout
- Model rate limiting
- Malformed model output
- Response-validator failure
- Trace-export failure
- Partial dependency recovery
- Retry exhaustion
- Duplicate request
- Stale authorization decision

Recovery must be tested separately from detection.

---

## Metric Reporting Rules

Reports must:

- State the dataset and configuration versions
- Report numerator and denominator
- Separate P0 failures
- Include confidence intervals when statistically appropriate
- Report latency percentiles rather than averages alone
- Separate abstention correctness from general task success
- Separate citation presence from citation correctness
- Separate retrieval relevance from source authorization
- Report cost per completed and attempted request
- Disclose excluded and invalid test cases
- Identify known limitations

No single composite score may represent overall safety.

---

## Gate Rules

A gate passes only when:

1. Required suites have executed.
2. Required artifacts exist.
3. Evidence is versioned.
4. P0 criteria pass.
5. Critical failure cases pass.
6. Exceptions have explicit approval.
7. Known limitations are disclosed.
8. Results are independently reviewable.
9. The tested revision matches the proposed revision.
10. Authority has not expanded beyond the approved scope.

A gate must fail when required evidence is missing.

---

## Evidence Retention Structure

Future evidence should follow a predictable structure:

```text
evidence/
├── runs/
│   └── <test-run-id>/
│       ├── manifest.json
│       ├── results/
│       ├── traces/
│       ├── reports/
│       └── failures/
├── datasets/
│   └── manifests/
├── reviews/
└── gates/
```

This is a planned repository structure. The directories must not be created empty to imply that evidence exists.

---

## Claim-to-Evidence Matrix

| Claim | Minimum evidence | Current status |
|---|---|---|
| Request validation works | EA-01 with executable tests | Not implemented |
| Identity is preserved | EA-03 with integration trace | Not implemented |
| Authorization is deterministic | EA-04 with positive and negative cases | Not implemented |
| Retrieval is permission-aware | EA-05 with cross-user isolation tests | Not implemented |
| Responses are citation-backed | EA-06 with labeled challenge set | Not implemented |
| Insufficient evidence causes abstention | EA-07 with labeled cases | Not implemented |
| Prompt injection cannot expand authority | EA-08 with adversarial cases | Not implemented |
| Sensitive data is protected | EA-09 with controlled fixtures | Not implemented |
| Dependency failure is safe | EA-10 with failure injection | Not implemented |
| Recommendations do not execute | EA-11 plus authority review | Not implemented |
| Lifecycle behavior is reconstructable | EA-12 with trace review | Not implemented |
| Responders find results useful | EA-13 with approved human rubric | Not evaluated |
| Behavior resists regression | EA-14 across stable dataset | Not implemented |
| Scope has not expanded | EA-15 with architecture review | Documented only |
| Slice is ready for promotion | EA-16 with complete prerequisites | Not authorized |

---

## Evidence Review Ownership

| Evidence area | Primary reviewer |
|---|---|
| Contracts | AI platform engineering |
| Identity | Enterprise identity owner |
| Authorization | Security and policy owner |
| Retrieval access | Data owner and security |
| Evidence quality | Service owner |
| Diagnostic quality | Incident-domain reviewers |
| Adversarial results | Security |
| Failure injection | Platform operations |
| Traces | Observability owner |
| Human usefulness | Incident operations |
| Gate package | Designated release authority |

The system being evaluated cannot approve its own evidence.

---

## Phase 2F Interview Explanation — 60 Seconds

I design the evidence plan before implementation so every future claim has a defined proof requirement. The plan separates static, unit, contract, integration, end-to-end, evaluation, adversarial, failure-injection, and operational testing. It defines sixteen suites, fifteen governed datasets, and sixteen evidence artifacts covering identity, deterministic authorization, permission-aware retrieval, citations, abstention, prompt injection, sensitive-data protection, resilience, observability, and human usefulness. Every run records its source, dataset, policy, contract, model, retrieval configuration, environment, expected result, actual result, and limitations. P0 and critical failures remain individually visible and cannot be hidden by an aggregate score.

---

## Phase 2F Interview Explanation — 30 Seconds

I map every claim to a versioned test and retained artifact before coding. The plan covers contracts, identity, policy, retrieval, citations, abstention, adversarial testing, failure injection, traces, and human usefulness. Missing evidence blocks the claim, and critical safety failures cannot be averaged away.

---

## Phase 2F Completion Gate

Phase 2F passes only when:

- Evidence principles are explicit.
- Evidence maturity levels are defined.
- Claim classes have minimum evidence requirements.
- Ten test levels are defined.
- Sixteen test suites are mapped.
- Fifteen planned datasets are governed.
- Test environments remain nonproduction.
- Sixteen evidence artifacts are identified.
- Required test-record fields are explicit.
- Human and automated evaluation roles are separated.
- Adversarial and failure-injection plans exist.
- Metric-reporting rules prevent misleading aggregation.
- Gate rules block missing evidence.
- Claims map to minimum evidence.
- Review ownership is assigned.
- Current implementation claims remain zero.
- No executable authority is granted.

---

## Current Evidence Status

| Evidence item | Status |
|---|---|
| Evidence principles | Documented |
| Evidence maturity model | Documented |
| Test-level model | Documented |
| Test-suite plan | Documented |
| Dataset plan | Documented |
| Environment classes | Documented |
| Evidence-artifact inventory | Documented |
| Human-evaluation plan | Documented |
| Automated-evaluation plan | Documented |
| Adversarial-test plan | Documented |
| Failure-injection plan | Documented |
| Gate rules | Documented |
| Test fixtures | Not created |
| Executable tests | Not created |
| Evaluation results | Not available |
| Application runtime | Not started |
| Model-provider integration | Not started |
| Retrieval implementation | Not started |
| Tool execution | Not authorized |
| Infrastructure mutation | Not authorized |
| Production deployment | Not authorized |

No test result, implementation result, production-readiness result, or executable authority is claimed by this document.
