# Phase 8 — Deterministic Policy-Based Routing Architecture and Authority Gate R4

## 1. Purpose

This document defines the complete standalone R4 replacement architecture for:

```text
PHASE_8_SELECTED_CAPABILITY=
DETERMINISTIC_POLICY_BASED_ROUTING
```

R4 resolves the remaining R3 authority-input findings:

```text
R3_F1_CALLER_SUPPLIED_POLICY_SUBSTITUTION
R3_F2_UNRESOLVED_INITIAL_POLICY_CONTENT
R3_F3_CALLER_SUPPLIED_REGISTRY_SUBSTITUTION
R3_F4_MISSING_CANONICAL_REGISTRY_CONTROL_IDENTITY
```

R4 preserves all accepted R3 semantics, including:

```text
ALLOW
DENY
APPROVAL_REQUIRED

PDP_PEP_SEPARATION

CT02_TRUSTED_IDENTITY

CT01_ENVIRONMENT_IS_REQUEST_ASSERTION

EXACT_TOOL_REQUEST_CONTENT_BINDING

EXACT_POLICY_DECISION_RECOMPUTATION

RULESET_CONTENT_HASHING

RESOURCE_LEVEL_TOOL_AUTHORIZATION_NOT_ESTABLISHED

TRUSTED_RESOURCE_ENVIRONMENT_NOT_ESTABLISHED

PHASE9_SEPARATION

NO_REAL_EXECUTION
```

R4 remains architecture only.

```text
PHASE_8_IMPLEMENTED=NO
R4_RUNTIME_EFFECT=NONE

R4_REPOSITORY_MATERIALIZATION_AUTHORITY=NONE
R4_IMPLEMENTATION_AUTHORITY=NONE
```

---

# 2. Historical candidate lineage

R1, R2, and R3 were conversational candidates only.

```text
R1_CANONICAL=NO
R1_MATERIALIZED=NO

R2_CANONICAL=NO
R2_MATERIALIZED=NO

R3_CANONICAL=NO
R3_MATERIALIZED=NO
```

R4 supersedes R3 for future Phase 8 architecture consideration.

No prior repository history is rewritten.

---

# 3. Exact preparation anchor

```text
R4_PREPARATION_ANCHOR_COMMIT=
b3baf6f0d8648e70ea2bd69c70d68de3787d1a5a

R4_PREPARATION_ANCHOR_TREE=
43bd5f7d6a4130ae33088c829077573bc8b4f6cb

R4_PREPARATION_ANCHOR_PARENT=
27a2473234c414e2fc9ce1acfd79a1f9bdbb43b4

ANCHOR_SUBJECT=
Record Phase 7E closure evidence
```

Phase 7E remains closed.

R4 does not reopen Phase 7.

---

# 4. R4 authority

```text
GATE_REVISION=R4

GATE_TYPE=
CANONICAL_AUTHORITY_INPUT_CORRECTION_AND_
COMPLETE_STANDALONE_REPLACEMENT_ARCHITECTURE_PREPARATION

REPOSITORY_EFFECT=NONE

ARCHITECTURE_PREPARATION_AUTHORITY=YES

DOCUMENTATION_MATERIALIZATION_AUTHORITY=NONE
SOURCE_MUTATION_AUTHORITY=NONE
TEST_MUTATION_AUTHORITY=NONE
RUNTIME_MUTATION_AUTHORITY=NONE

POLICY_ADMINISTRATION_AUTHORITY=NONE
HUMAN_APPROVAL_AUTHORITY=NONE
REAL_TOOL_EXECUTION_AUTHORITY=NONE

NETWORK_AUTHORITY=NONE
CREDENTIAL_AUTHORITY=NONE
PRODUCTION_AUTHORITY=NONE
```

---

# Part I — Canonical authority model

## 5. Authority chain

R4 freezes the initial authority-bearing path as:

```text
CT-01 VALIDATED REQUEST CONTEXT
             +
CT-02 TRUSTED IDENTITY
             +
PHASE 7 TOOL REQUEST
             +
CANONICAL LOCAL PHASE 8 RULESET
             +
CANONICAL PHASE 7 DEFAULT TOOL REGISTRY
             |
             v
          PHASE 8 PDP
             |
             v
      TOOL POLICY DECISION
             |
             v
          PHASE 8 PEP
             |
      +------+------+
      |             |
     DENY      APPROVAL_REQUIRED
      |             |
   NO ROUTE     PHASE 9 BOUNDARY

              ALLOW
                |
                v
      LOCAL MOCK DISPATCH
           ELIGIBILITY
```

The requester does not choose:

```text
policy rules
registry declarations
policy version
risk classification
side-effect classification
approval requirement
```

---

# 6. Canonical verdict algebra

Exactly:

```text
ALLOW
DENY
APPROVAL_REQUIRED
```

No fourth authorization verdict exists.

---

# 7. Canonical routes

```text
DENY
    <-> NO_ROUTE

ALLOW
    <-> LOCAL_MOCK_DISPATCH_ELIGIBLE

APPROVAL_REQUIRED
    <-> PHASE_9_APPROVAL_BOUNDARY
```

---

# Part II — Canonical Phase 8 policy source

## 8. Selected policy authority model

R4 selects:

```text
PHASE8_INITIAL_POLICY_SOURCE=
LOCAL_CANONICAL_IMMUTABLE_RULESET
```

The initial authority-bearing policy path must not accept a caller-selected ruleset.

```text
CALLER_SUPPLIED_POLICY_AUTHORITY=NO
MODEL_SUPPLIED_POLICY_AUTHORITY=NO
AGENT_SUPPLIED_POLICY_AUTHORITY=NO
REQUEST_SUPPLIED_POLICY_AUTHORITY=NO
```

---

# 9. Exact policy version

```text
PHASE_8_INITIAL_POLICY_VERSION=
phase8-tool-policy-v1
```

This identifies the semantic generation of the local policy.

---

# 10. Exact synthetic identity vocabulary

R4 deliberately uses the existing lab's synthetic identity vocabulary:

```text
SYNTHETIC_TENANT=
tenant-a

SYNTHETIC_REQUIRED_ROLE=
incident-responder

SYNTHETIC_REQUIRED_GROUP=
payments-operations

SYNTHETIC_MINIMUM_ASSURANCE=
ELEVATED
```

These values are lab policy constants.

They are not production IAM mappings.

---

# 11. Exact initial canonical ruleset

The R4 initial policy contains exactly seven rules.

| Rule ID | Tool | Tenant | Role | Group | Minimum assurance |
|---|---|---|---|---|---|
| `phase8-jira-issue-read-v1` | `jira.issue.read` | `tenant-a` | `incident-responder` | `payments-operations` | `ELEVATED` |
| `phase8-jira-issue-comment-v1` | `jira.issue.comment` | `tenant-a` | `incident-responder` | `payments-operations` | `ELEVATED` |
| `phase8-servicenow-incident-read-v1` | `servicenow.incident.read` | `tenant-a` | `incident-responder` | `payments-operations` | `ELEVATED` |
| `phase8-servicenow-incident-update-v1` | `servicenow.incident.update` | `tenant-a` | `incident-responder` | `payments-operations` | `ELEVATED` |
| `phase8-kubernetes-resource-read-v1` | `kubernetes.resource.read` | `tenant-a` | `incident-responder` | `payments-operations` | `ELEVATED` |
| `phase8-cloud-resource-read-v1` | `cloud.resource.read` | `tenant-a` | `incident-responder` | `payments-operations` | `ELEVATED` |
| `phase8-database-query-read-v1` | `database.query.read` | `tenant-a` | `incident-responder` | `payments-operations` | `ELEVATED` |

No eighth rule is authorized.

---

# 12. Canonical ruleset builder

Conceptual builder:

```python
def build_phase8_initial_tool_policy_ruleset(
) -> ToolPolicyRuleSet:
    return ToolPolicyRuleSet(
        policy_version="phase8-tool-policy-v1",
        rules=(
            ToolPolicyRule(
                rule_id="phase8-jira-issue-read-v1",
                tool_name=ToolName.JIRA_ISSUE_READ,
                allowed_tenant_ids=("tenant-a",),
                required_roles_any=("incident-responder",),
                required_groups_any=("payments-operations",),
                minimum_assurance_level=(
                    AssuranceLevel.ELEVATED
                ),
            ),
            ToolPolicyRule(
                rule_id="phase8-jira-issue-comment-v1",
                tool_name=ToolName.JIRA_ISSUE_COMMENT,
                allowed_tenant_ids=("tenant-a",),
                required_roles_any=("incident-responder",),
                required_groups_any=("payments-operations",),
                minimum_assurance_level=(
                    AssuranceLevel.ELEVATED
                ),
            ),
            ToolPolicyRule(
                rule_id=(
                    "phase8-servicenow-incident-read-v1"
                ),
                tool_name=(
                    ToolName.SERVICENOW_INCIDENT_READ
                ),
                allowed_tenant_ids=("tenant-a",),
                required_roles_any=("incident-responder",),
                required_groups_any=("payments-operations",),
                minimum_assurance_level=(
                    AssuranceLevel.ELEVATED
                ),
            ),
            ToolPolicyRule(
                rule_id=(
                    "phase8-servicenow-incident-update-v1"
                ),
                tool_name=(
                    ToolName.SERVICENOW_INCIDENT_UPDATE
                ),
                allowed_tenant_ids=("tenant-a",),
                required_roles_any=("incident-responder",),
                required_groups_any=("payments-operations",),
                minimum_assurance_level=(
                    AssuranceLevel.ELEVATED
                ),
            ),
            ToolPolicyRule(
                rule_id=(
                    "phase8-kubernetes-resource-read-v1"
                ),
                tool_name=(
                    ToolName.KUBERNETES_RESOURCE_READ
                ),
                allowed_tenant_ids=("tenant-a",),
                required_roles_any=("incident-responder",),
                required_groups_any=("payments-operations",),
                minimum_assurance_level=(
                    AssuranceLevel.ELEVATED
                ),
            ),
            ToolPolicyRule(
                rule_id="phase8-cloud-resource-read-v1",
                tool_name=ToolName.CLOUD_RESOURCE_READ,
                allowed_tenant_ids=("tenant-a",),
                required_roles_any=("incident-responder",),
                required_groups_any=("payments-operations",),
                minimum_assurance_level=(
                    AssuranceLevel.ELEVATED
                ),
            ),
            ToolPolicyRule(
                rule_id="phase8-database-query-read-v1",
                tool_name=ToolName.DATABASE_QUERY_READ,
                allowed_tenant_ids=("tenant-a",),
                required_roles_any=("incident-responder",),
                required_groups_any=("payments-operations",),
                minimum_assurance_level=(
                    AssuranceLevel.ELEVATED
                ),
            ),
        ),
    )
```

---

# 13. Canonical ruleset object

```python
DEFAULT_PHASE8_TOOL_POLICY_RULESET: Final = (
    build_phase8_initial_tool_policy_ruleset()
)
```

Because the policy contract is frozen and collection fields are tuples, the resulting object is immutable at the contract-object level.

R4 does not claim process-memory tamper resistance.

---

# Part III — Exact canonical ruleset content identity

## 14. Ruleset hash domain

```text
phase8-tool-policy-ruleset-v1
```

---

# 15. Ruleset normalization

Each rule is normalized using:

```text
rule_id
tool_name
sorted allowed_tenant_ids
sorted required_roles_any
sorted required_groups_any
minimum_assurance_level
```

Rules are ordered by:

```text
tool_name.value ascending
```

---

# 16. Canonical ruleset hash algorithm

```python
def hash_tool_policy_ruleset(
    rules: ToolPolicyRuleSet,
) -> ContentHash:
    ...
```

Serialization remains:

```python
json.dumps(
    payload,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=True,
)
```

then UTF-8 SHA-256.

---

# 17. Frozen expected initial ruleset hash

For the exact R4 rule content above:

```text
R4_EXPECTED_INITIAL_POLICY_RULESET_HASH=
2b8d6ca8dbbc67e105a8e96d657eeb8451dbc4295b7ff40f2b467e65ad839e8d
```

Future implementation must independently recompute this value.

If:

```text
hash_tool_policy_ruleset(
    DEFAULT_PHASE8_TOOL_POLICY_RULESET
)
!=
R4_EXPECTED_INITIAL_POLICY_RULESET_HASH
```

the evaluator must fail closed.

---

# 18. Policy authority mismatch

New controlled evaluator condition:

```text
CANONICAL_POLICY_SOURCE_MISMATCH
```

Effect:

```text
NO_POLICY_DECISION
```

No fallback ruleset is permitted.

---

# Part IV — Canonical Phase 7 registry authority

## 19. Selected registry source

For the initial Phase 8 slice:

```text
PHASE8_TOOL_REGISTRY_SOURCE=
PHASE7_DEFAULT_TOOL_REGISTRY
```

Specifically:

```python
DEFAULT_TOOL_REGISTRY
```

from the existing Phase 7A registry module.

---

# 20. No caller registry substitution

Normal authority-bearing Phase 8 interfaces must not expose:

```python
registry: ToolRegistry = ...
```

as a caller-selected parameter.

Therefore:

```text
CALLER_SUPPLIED_REGISTRY_AUTHORITY=NO
MODEL_SUPPLIED_REGISTRY_AUTHORITY=NO
AGENT_SUPPLIED_REGISTRY_AUTHORITY=NO
REQUEST_SUPPLIED_REGISTRY_AUTHORITY=NO
```

---

# 21. Registry canonicality vs authorization

The registry remains:

```text
CAPABILITY_AND_CONTROL_DECLARATION
```

It does not itself become policy authority.

Phase 8 merely designates the existing local `DEFAULT_TOOL_REGISTRY` as the only initial source whose declarations the PDP may consume.

```text
REGISTRY_IS_PDP=NO
REGISTRY_IS_POLICY_DECISION=NO
```

---

# Part V — Canonical registry control identity

## 22. Registry-control hash domain

```text
phase8-phase7-registry-controls-v1
```

---

# 23. Policy-relevant registry fields

For each tool, the control hash includes exactly:

```text
tool_name
capability
side_effect
risk_tier
idempotency_requirement
approval_requirement
timeout_seconds
authorization_required
execution_enabled
general_shell_access
```

The tools are ordered by:

```text
tool_name.value ascending
```

---

# 24. Registry version treatment

The free-form:

```text
ToolRegistry.version
```

is excluded from the content hash.

The closed Phase 7:

```text
TOOL_CONTRACT_VERSION=
7a.1
```

is included as a domain-level field.

---

# 25. Registry control hash

Conceptual function:

```python
def hash_tool_registry_controls(
    registry: ToolRegistry,
) -> ContentHash:
    normalized_tools = [
        {
            "tool_name": definition.tool_name.value,
            "capability": definition.capability.value,
            "side_effect": definition.side_effect.value,
            "risk_tier": definition.risk_tier.value,
            "idempotency_requirement": (
                definition.idempotency_requirement.value
            ),
            "approval_requirement": (
                definition.approval_requirement.value
            ),
            "timeout_seconds": (
                definition.timeout_seconds
            ),
            "authorization_required": (
                definition.authorization_required
            ),
            "execution_enabled": (
                definition.execution_enabled
            ),
            "general_shell_access": (
                definition.general_shell_access
            ),
        }
        for definition in sorted(
            registry.tools,
            key=lambda item: item.tool_name.value,
        )
    ]

    payload = {
        "hash_domain":
            "phase8-phase7-registry-controls-v1",
        "tool_contract_version":
            TOOL_CONTRACT_VERSION,
        "tools":
            normalized_tools,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
```

---

# 26. Frozen expected canonical registry hash

For the current exact Phase 7 default registry control surface:

```text
R4_EXPECTED_PHASE7_REGISTRY_CONTROL_HASH=
9ef9033c4501c41bb76bc8e39e3dc023633d4e67161ad3676ec2d5d24ae8af8f
```

Future implementation must independently recompute this value from:

```python
DEFAULT_TOOL_REGISTRY
```

before any policy decision.

---

# 27. Registry authority mismatch

If:

```text
hash_tool_registry_controls(
    DEFAULT_TOOL_REGISTRY
)
!=
R4_EXPECTED_PHASE7_REGISTRY_CONTROL_HASH
```

then:

```text
CANONICAL_REGISTRY_SOURCE_MISMATCH
NO_POLICY_DECISION
```

No alternate registry is selected.

---

# Part VI — Existing Phase 7 registry semantics frozen for Phase 8

## 28. Current control disposition

The Phase 8 canonical registry authority therefore retains the existing distinctions:

### Read-only tools

```text
jira.issue.read
servicenow.incident.read
kubernetes.resource.read
cloud.resource.read
database.query.read
```

remain:

```text
side_effect=NONE
risk_tier=LOW
approval_requirement=POLICY_DECISION
execution_enabled=False
general_shell_access=False
```

### Consequential tools

```text
jira.issue.comment
```

remains:

```text
side_effect=APPEND_ONLY
risk_tier=MEDIUM
approval_requirement=HUMAN_APPROVAL
```

and:

```text
servicenow.incident.update
```

remains:

```text
side_effect=MUTATING
risk_tier=HIGH
approval_requirement=HUMAN_APPROVAL
```

Both remain non-executable.

---

# Part VII — Trusted and nontrusted contextual inputs

## 29. CT-02 remains trusted identity

Trusted Phase 8 identity inputs remain:

```text
subject_id
tenant_id
session_id
issuer
roles
groups
assurance_level
authentication_time
expires_at
delegation_context
```

---

# 30. CT-01 remains request context

CT-01 remains:

```text
VALIDATED_REQUEST_CONTEXT
```

not authoritative resource truth.

Its environment remains:

```text
request_asserted_environment
```

and does not influence an `ALLOW`.

---

# 31. Resource authorization remains deferred

```text
RESOURCE_LEVEL_TOOL_AUTHORIZATION=
NOT_ESTABLISHED

TRUSTED_RESOURCE_ENVIRONMENT=
NOT_ESTABLISHED
```

---

# Part VIII — Exact tool-request binding

## 32. Tool-request content hash preserved

R4 preserves the R3 domain:

```text
phase8-tool-request-v1
```

and the deterministic content hash over the complete validated `ToolRequest`.

It includes:

```text
tool_contract_version
tool_envelope_version
request_id
trace_id
tool_name
arguments
idempotency_key
requested_at
```

---

# 33. Argument semantics nonclaim

```text
EXACT_TOOL_REQUEST_CONTENT_BOUND=YES

TOOL_ARGUMENT_SEMANTIC_AUTHORIZATION=
NOT_ESTABLISHED
```

The hash binds the exact action request without making arbitrary arguments trusted authorization attributes.

---

# Part IX — Public PDP authority surface

## 34. R4 public PDP interface

The authority-bearing interface becomes:

```python
def evaluate_tool_policy(
    policy_request: ToolPolicyEvaluationRequest,
    *,
    diagnostic_request: DiagnosticRequest,
    identity: IdentityContext,
    tool_request: ToolRequest,
    policy_decision_id: OpaqueIdentifier,
    decided_at: Timestamp,
) -> ToolPolicyDecision:
    ...
```

Critically absent:

```text
rules parameter
registry parameter
policy-version parameter
```

---

# 35. Canonical PDP sources

Internally the PDP must use exactly:

```python
rules = DEFAULT_PHASE8_TOOL_POLICY_RULESET
registry = DEFAULT_TOOL_REGISTRY
```

No normal runtime override exists.

---

# 36. Pre-evaluation canonical source verification

Before evaluating the request, the PDP requires:

```text
current_ruleset_hash
==
R4_EXPECTED_INITIAL_POLICY_RULESET_HASH
```

and:

```text
current_registry_control_hash
==
R4_EXPECTED_PHASE7_REGISTRY_CONTROL_HASH
```

Failure returns no decision.

---

# 37. Internal/test-only helpers

An implementation may use private pure helpers for unit testing, but those helpers:

```text
MUST_NOT_BE_EXPORTED_AS_RUNTIME_AUTHORITY_SURFACES

MUST_NOT_BE_USED_BY_API_OR_RUNTIME_INTEGRATION

MUST_NOT_ALLOW_CALLER_POLICY_SELECTION

MUST_NOT_ALLOW_CALLER_REGISTRY_SELECTION
```

A test seam is not an authorization interface.

---

# Part X — Policy truth function

## 38. Policy ordering preserved

After structural and canonical-source validation:

```text
1. identity expiration
2. matching canonical tool rule
3. tenant membership
4. role requirement
5. group requirement
6. assurance requirement
7. canonical registry human-approval requirement
8. canonical registry side-effect classification
9. canonical registry risk tier
10. ALLOW
```

---

# 39. Read-only allow

A tool may reach:

```text
ALLOW
```

only when:

```text
canonical rule matches
tenant-a matches
incident-responder role matches
payments-operations group matches
assurance >= ELEVATED

canonical registry says:
side_effect=NONE
risk_tier=LOW
approval_requirement in {
    NONE,
    POLICY_DECISION,
}
```

Result:

```text
ROUTE=
LOCAL_MOCK_DISPATCH_ELIGIBLE
```

---

# 40. Consequential-tool disposition

For:

```text
jira.issue.comment
servicenow.incident.update
```

a valid synthetic policy match does not produce `ALLOW`.

The canonical Phase 7 declarations force:

```text
APPROVAL_REQUIRED
```

and:

```text
ROUTE=
PHASE_9_APPROVAL_BOUNDARY
```

No Phase 9 approval is created.

---

# Part XI — Exact decision lineage

## 41. Required decision content identities

Every valid R4 decision carries:

```text
policy_version
ruleset_content_hash
registry_control_content_hash
tool_request_content_hash
```

---

# 42. Meaning of each identity

```text
policy_version
=
policy semantic generation

ruleset_content_hash
=
exact canonical Phase 8 rule content

registry_control_content_hash
=
exact canonical Phase 7 control declarations

tool_request_content_hash
=
exact validated ToolRequest content
```

None proves producer provenance.

---

# 43. Decision contract addition

R4 adds:

```python
registry_control_content_hash: ContentHash
```

to the R3 `ToolPolicyDecision`.

All other accepted R3 fields remain preserved.

---

# 44. Required decision hash invariants

For every decision:

```text
decision.ruleset_content_hash
==
R4_EXPECTED_INITIAL_POLICY_RULESET_HASH

decision.registry_control_content_hash
==
R4_EXPECTED_PHASE7_REGISTRY_CONTROL_HASH
```

Any other value makes the decision invalid for R4 enforcement.

---

# Part XII — Public PEP authority surface

## 45. R4 PEP interface

```python
def enforce_tool_policy_decision(
    decision: ToolPolicyDecision,
    *,
    policy_request: ToolPolicyEvaluationRequest,
    diagnostic_request: DiagnosticRequest,
    identity: IdentityContext,
    tool_request: ToolRequest,
    enforced_at: Timestamp,
) -> PolicyEnforcementOutcome:
    ...
```

Critically absent:

```text
rules parameter
registry parameter
```

---

# 46. PEP canonical sources

The PEP independently uses:

```python
DEFAULT_PHASE8_TOOL_POLICY_RULESET
DEFAULT_TOOL_REGISTRY
```

No caller-selected authority input is accepted.

---

# 47. PEP canonical-source verification

Before enforcement:

```text
hash_tool_policy_ruleset(
    DEFAULT_PHASE8_TOOL_POLICY_RULESET
)
==
R4_EXPECTED_INITIAL_POLICY_RULESET_HASH
```

and:

```text
hash_tool_registry_controls(
    DEFAULT_TOOL_REGISTRY
)
==
R4_EXPECTED_PHASE7_REGISTRY_CONTROL_HASH
```

must both pass.

Otherwise:

```text
NO_ELIGIBLE_ROUTE
```

---

# Part XIII — PEP exact semantic recomputation

## 48. R3 recomputation control preserved

The PEP reconstructs the exact policy request and calls:

```python
expected_decision = evaluate_tool_policy(
    expected_policy_request,
    diagnostic_request=diagnostic_request,
    identity=identity,
    tool_request=tool_request,
    policy_decision_id=decision.policy_decision_id,
    decided_at=decision.decided_at,
)
```

Then:

```text
decision == expected_decision
```

is mandatory.

---

# 49. What exact recomputation now proves

With R4 canonical inputs, exact recomputation establishes:

> The supplied decision is exactly the decision produced by the frozen Phase 8 semantics from the exact request, trusted identity, exact tool request, canonical local Phase 8 policy rules, and canonical Phase 7 registry control declarations.

This is materially stronger than R3.

---

# 50. What exact recomputation still does not prove

R4 still does not claim:

```text
historical PDP producer provenance
digital signature
trusted hardware execution
process-memory tamper resistance
external policy issuer
nonrepudiation
```

---

# Part XIV — Controlled canonical-source failures

## 51. Evaluation error additions

R4 adds:

```python
CANONICAL_POLICY_SOURCE_MISMATCH
CANONICAL_REGISTRY_SOURCE_MISMATCH
```

to the closed evaluation error domain.

Both produce:

```text
NO_POLICY_DECISION
```

---

# 52. Enforcement error additions

R4 adds:

```python
CANONICAL_POLICY_SOURCE_MISMATCH
CANONICAL_REGISTRY_SOURCE_MISMATCH
```

to the closed enforcement error domain.

Both produce:

```text
NO_ELIGIBLE_ROUTE
```

---

# Part XV — No authority from content hash alone

## 53. Core R4 doctrine

R4 formally freezes:

```text
CONTENT_HASH_MATCH
IS_NOT
AUTHORITY
```

Authority requires both:

```text
content identity
+
designation as canonical source
```

Therefore:

```text
CALLER_SUPPLIED_RULESET_WITH_VALID_HASH=
NOT_ADMISSIBLE

CALLER_SUPPLIED_REGISTRY_WITH_VALID_HASH=
NOT_ADMISSIBLE
```

---

# 54. Policy source designation

The architecture-designated source is:

```text
DEFAULT_PHASE8_TOOL_POLICY_RULESET
```

and no other R4 ruleset.

---

# 55. Registry source designation

The architecture-designated registry is:

```text
DEFAULT_TOOL_REGISTRY
```

and no other R4 registry.

---

# Part XVI — Change control implications

## 56. Future rule change

Any future change to:

```text
tenant
role
group
assurance requirement
tool rule presence
rule ID
```

changes the canonical ruleset hash.

That change therefore requires:

```text
separate architecture authority
+
separate implementation authority
+
new exact tests
+
new decision lineage expectations
```

It may not silently retain the existing R4 authority identity.

---

# 57. Future Phase 7 registry change

Any future policy-relevant change to:

```text
capability
side effect
risk tier
idempotency requirement
approval requirement
timeout
authorization requirement
execution-enabled state
general-shell state
```

changes the canonical registry control hash.

Existing R4 enforcement must fail closed until architecture compatibility is reviewed.

---

# 58. Free-form registry version

A change only to:

```text
ToolRegistry.version
```

does not automatically create authorization significance because that free-form value remains outside the R4 control hash.

If a later architecture wants registry version to carry authority semantics, that requires explicit design.

---

# Part XVII — Synthetic policy result matrix

## 59. Canonical synthetic identity

For the existing synthetic identity:

```text
tenant_id=tenant-a
roles=(incident-responder,)
groups=(payments-operations,)
assurance_level=ELEVATED
```

and an otherwise coherent request:

| Tool | Canonical Phase 8 result |
|---|---|
| `jira.issue.read` | `ALLOW` |
| `jira.issue.comment` | `APPROVAL_REQUIRED` |
| `servicenow.incident.read` | `ALLOW` |
| `servicenow.incident.update` | `APPROVAL_REQUIRED` |
| `kubernetes.resource.read` | `ALLOW` |
| `cloud.resource.read` | `ALLOW` |
| `database.query.read` | `ALLOW` |

`ALLOW` remains local-mock eligibility only.

---

# 60. Other tenant

Any identity with:

```text
tenant_id != tenant-a
```

receives:

```text
DENY
TENANT_NOT_ALLOWED
```

---

# 61. Missing role

If:

```text
incident-responder
```

is absent:

```text
DENY
ROLE_REQUIREMENT_NOT_MET
```

---

# 62. Missing group

If:

```text
payments-operations
```

is absent:

```text
DENY
GROUP_REQUIREMENT_NOT_MET
```

---

# 63. Insufficient assurance

If assurance is below:

```text
ELEVATED
```

then:

```text
DENY
ASSURANCE_REQUIREMENT_NOT_MET
```

---

# Part XVIII — Decision lifetime preserved

## 64. Positive decision TTL

```text
PHASE_8_DECISION_TTL_SECONDS=60
```

For `ALLOW` and `APPROVAL_REQUIRED`:

```text
expires_at =
min(
    decided_at + 60 seconds,
    effective_identity_expires_at,
)
```

---

# 65. Denial TTL

For `DENY`:

```text
expires_at =
decided_at + 60 seconds
```

No positive authority is granted.

---

# Part XIX — Phase boundaries

## 66. Phase 7 non-drift

R4 does not mutate the Phase 7 registry.

It only consumes its current canonical declaration object.

---

# 67. Phase 7D non-drift

R4 does not call the dispatcher.

Initial Phase 8 still ends at:

```text
ELIGIBLE_FOR_LOCAL_MOCK_DISPATCH
```

---

# 68. Phase 7E non-drift

Phase 7E remains consistency evidence.

Its historical:

```text
REGISTRY_PRODUCER_PROVENANCE=
NOT_ESTABLISHED
```

is not rewritten.

R4 solves a different problem by designating a local canonical registry source for Phase 8 authorization evaluation.

---

# 69. Phase 9 non-drift

`APPROVAL_REQUIRED` does not establish approval.

Phase 9 remains separate.

---

# Part XX — External policy systems

## 70. No external PDP

R4 does not authorize:

```text
OPA
Cedar
AWS Verified Permissions
Azure authorization services
Google IAM evaluation
Okta authorization
remote PDP
remote policy store
```

---

# 71. No dynamic policy administration

R4 does not authorize:

```text
runtime policy creation
runtime policy modification
runtime policy deletion
model-authored policy promotion
agent-authored policy promotion
remote policy download
dynamic policy override
```

---

# Part XXI — Required future tests

## 72. Canonical policy source tests

Mandatory:

```text
builder returns exact seven rules

all exact rule IDs match architecture

all exact tool names match architecture

all allowed tenants equal (tenant-a,)

all required roles equal (incident-responder,)

all required groups equal (payments-operations,)

all minimum assurance values equal ELEVATED

canonical ruleset object frozen

canonical ruleset hash exactly equals:
2b8d6ca8dbbc67e105a8e96d657eeb8451dbc4295b7ff40f2b467e65ad839e8d
```

---

# 73. Policy substitution adversarial tests

Mandatory:

```text
caller cannot pass alternate rules to public PDP

caller cannot pass alternate rules to public PEP

permissive alternate rule set cannot influence public evaluation

alternate valid ruleset hash cannot authorize itself

canonical ruleset drift fails closed
```

---

# 74. Canonical registry tests

Mandatory:

```text
DEFAULT_TOOL_REGISTRY control hash exactly equals:
9ef9033c4501c41bb76bc8e39e3dc023633d4e67161ad3676ec2d5d24ae8af8f
```

and every policy-relevant tool field must match the expected canonical declaration.

---

# 75. Registry substitution adversarial tests

Mandatory:

```text
caller cannot pass alternate registry to public PDP

caller cannot pass alternate registry to public PEP

downgraded jira.issue.comment registry cannot produce ALLOW

downgraded servicenow.incident.update registry cannot produce ALLOW

alternate valid registry with matching ToolName set is inadmissible

canonical registry drift fails closed
```

---

# 76. Decision-lineage tests

Mandatory:

```text
ruleset_content_hash exact

registry_control_content_hash exact

tool_request_content_hash exact

wrong ruleset hash rejected

wrong registry hash rejected

wrong request hash rejected
```

---

# 77. Exact policy result tests

For the canonical synthetic identity:

```text
jira.issue.read -> ALLOW
jira.issue.comment -> APPROVAL_REQUIRED
servicenow.incident.read -> ALLOW
servicenow.incident.update -> APPROVAL_REQUIRED
kubernetes.resource.read -> ALLOW
cloud.resource.read -> ALLOW
database.query.read -> ALLOW
```

---

# 78. Denial tests

Mandatory:

```text
wrong tenant -> DENY

missing incident-responder -> DENY

missing payments-operations -> DENY

STANDARD assurance -> DENY

expired identity -> DENY
```

---

# 79. PEP recomputation tests

Mandatory:

```text
exact canonical decision accepted

forged ALLOW rejected

forged route rejected

forged reason rejected

forged rule ID rejected

forged registry hash rejected

forged ruleset hash rejected

altered ToolRequest rejected

altered identity session rejected

altered canonical policy source causes fail-closed

altered canonical registry source causes fail-closed
```

---

# 80. Regression tests

Mandatory:

```text
CT01 regression
CT02 regression
CT03 regression
retrieval authorization regression

Phase7 registry regression
Phase7 contracts regression
Phase7 dispatcher regression
Phase7E regression

full repository regression
```

---

# Part XXII — Implementation boundary implications

## 81. Future implementation must not invent policy

The future implementation agent is not authorized to decide:

```text
which tenant is allowed
which role is required
which group is required
which assurance level is required
which tool receives a rule
```

R4 already determines those values.

---

# 82. Future implementation must not invent registry authority

The future implementation agent is not authorized to choose another registry source.

R4 selects:

```text
DEFAULT_TOOL_REGISTRY
```

only.

---

# 83. Future implementation file boundary

R4 does **not** freeze a source-code implementation file boundary.

That boundary requires a later implementation-authority review after architecture materialization and acceptance.

---

# Part XXIII — Nonclaims

## 84. Explicit nonclaims

R4 does not establish:

```text
PHASE8_IMPLEMENTATION

PDP_PRODUCER_PROVENANCE
PEP_PRODUCER_PROVENANCE

POLICY_SIGNATURE
POLICY_NONREPUDIATION
EXTERNAL_POLICY_ISSUER

REGISTRY_PRODUCER_PROVENANCE
REGISTRY_SIGNATURE

PROCESS_MEMORY_TAMPER_RESISTANCE
TRUSTED_EXECUTION_ENVIRONMENT

RESOURCE_LEVEL_TOOL_AUTHORIZATION
TRUSTED_RESOURCE_ENVIRONMENT

HUMAN_APPROVAL
TRUSTED_TOOL_EXECUTION

REAL_TOOL_EXECUTION
NETWORK_ACCESS
CREDENTIAL_ACCESS
FILESYSTEM_MUTATION
INFRASTRUCTURE_MUTATION
EXTERNAL_SYSTEM_MUTATION

PRODUCTION_DEPLOYMENT
EXTERNAL_CUSTOMER_USE
```

---

# Part XXIV — R3 findings resolved

## 85. R3-F1

```text
R3_F1_CALLER_SUPPLIED_POLICY_SUBSTITUTION=
RESOLVED_AT_R4_CANDIDATE_LEVEL

PUBLIC_PDP_RULESET_PARAMETER=REMOVED
PUBLIC_PEP_RULESET_PARAMETER=REMOVED

CANONICAL_LOCAL_RULESET=DEFINED
```

---

# 86. R3-F2

```text
R3_F2_UNRESOLVED_INITIAL_POLICY_CONTENT=
RESOLVED_AT_R4_CANDIDATE_LEVEL

EXACT_RULE_COUNT=7
EXACT_RULE_IDS=DEFINED
EXACT_TOOL_BINDINGS=DEFINED
EXACT_TENANT=DEFINED
EXACT_ROLE=DEFINED
EXACT_GROUP=DEFINED
EXACT_ASSURANCE=DEFINED
```

---

# 87. R3-F3

```text
R3_F3_CALLER_SUPPLIED_REGISTRY_SUBSTITUTION=
RESOLVED_AT_R4_CANDIDATE_LEVEL

PUBLIC_PDP_REGISTRY_PARAMETER=REMOVED
PUBLIC_PEP_REGISTRY_PARAMETER=REMOVED

CANONICAL_REGISTRY=
DEFAULT_TOOL_REGISTRY
```

---

# 88. R3-F4

```text
R3_F4_MISSING_REGISTRY_CONTROL_IDENTITY=
RESOLVED_AT_R4_CANDIDATE_LEVEL

REGISTRY_CONTROL_CONTENT_HASH=DEFINED

EXPECTED_HASH=
9ef9033c4501c41bb76bc8e39e3dc023633d4e67161ad3676ec2d5d24ae8af8f
```

---

# Part XXV — Exact future documentation boundary

## 89. Proposed R4 file

If a later independent review grants materialization authority:

```text
docs/policy/
PHASE_8_DETERMINISTIC_POLICY_BASED_ROUTING_
ARCHITECTURE_AND_AUTHORITY_GATE_R4.md
```

---

# 90. Exact one-file boundary

```text
PROPOSED_FILE_COUNT=1

PROPOSED_OPERATION=ADD

PROPOSED_FILE=
docs/policy/PHASE_8_DETERMINISTIC_POLICY_BASED_ROUTING_ARCHITECTURE_AND_AUTHORITY_GATE_R4.md

R1_FILE_MATERIALIZATION=NO
R2_FILE_MATERIALIZATION=NO
R3_FILE_MATERIALIZATION=NO

EXISTING_FILE_MUTATION=NONE
SOURCE_MUTATION=NONE
TEST_MUTATION=NONE
STATUS_MUTATION=NONE
WORKFLOW_MUTATION=NONE

SECOND_FILE_AUTHORITY=NONE
```

Expected parent:

```text
b3baf6f0d8648e70ea2bd69c70d68de3787d1a5a
```

If `main` moves before materialization, R4 must be re-anchored.

---

# Part XXVI — Final R4 candidate disposition

## 91. Candidate state

```text
PHASE_8_R4_ARCHITECTURE_CANDIDATE=
PREPARED_COMPLETE_STANDALONE

R3_FINDINGS_F1_F4=
RESOLVED_AT_R4_CANDIDATE_LEVEL

CANONICAL_POLICY_AUTHORITY_SOURCE=
DEFAULT_PHASE8_TOOL_POLICY_RULESET

CANONICAL_REGISTRY_SOURCE=
DEFAULT_TOOL_REGISTRY

EXPECTED_POLICY_RULESET_HASH=
2b8d6ca8dbbc67e105a8e96d657eeb8451dbc4295b7ff40f2b467e65ad839e8d

EXPECTED_REGISTRY_CONTROL_HASH=
9ef9033c4501c41bb76bc8e39e3dc023633d4e67161ad3676ec2d5d24ae8af8f

CALLER_POLICY_SUBSTITUTION=PROHIBITED
CALLER_REGISTRY_SUBSTITUTION=PROHIBITED

PEP_EXACT_DECISION_RECOMPUTATION=
PRESERVED

PHASE9_STARTED=NO

R4_REPOSITORY_MATERIALIZATION_AUTHORITY=NONE
R4_IMPLEMENTATION_AUTHORITY=NONE

R4_STATUS=
NONCANONICAL_UNMATERIALIZED_ARCHITECTURE_CANDIDATE
```

The only authorized next effect is independent architecture review of this exact R4 candidate.

No repository materialization or implementation is authorized.
