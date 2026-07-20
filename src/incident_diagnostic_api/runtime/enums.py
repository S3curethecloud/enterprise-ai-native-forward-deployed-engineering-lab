"""Bounded enumerations for the Phase 4 deterministic runtime."""

from enum import StrEnum
from types import MappingProxyType
from typing import Final


class RuntimeState(StrEnum):
    """Explicit states in the bounded diagnostic workflow."""

    RECEIVED = "received"
    REQUEST_VALIDATING = "request_validating"
    IDENTITY_VALIDATING = "identity_validating"
    POLICY_EVALUATING = "policy_evaluating"
    EVIDENCE_PENDING = "evidence_pending"
    EVIDENCE_ASSESSING = "evidence_assessing"
    GENERATION_PENDING = "generation_pending"
    RESPONSE_VALIDATING = "response_validating"
    COMPLETED_RECOMMENDATION = "completed_recommendation"
    COMPLETED_ABSTENTION = "completed_abstention"
    COMPLETED_DENIAL = "completed_denial"
    COMPLETED_FAILURE = "completed_failure"
    COMPLETED_SECURITY_STOP = "completed_security_stop"


class RuntimeStateType(StrEnum):
    """Lifecycle classification for a runtime state."""

    INITIAL = "initial"
    ACTIVE = "active"
    TERMINAL = "terminal"


class TransitionCommand(StrEnum):
    """Commands accepted by the deterministic transition boundary."""

    BEGIN_REQUEST_VALIDATION = "begin_request_validation"
    REQUEST_VALIDATED = "request_validated"
    REQUEST_REJECTED = "request_rejected"

    IDENTITY_VALIDATED = "identity_validated"
    IDENTITY_DENIED = "identity_denied"
    IDENTITY_FAILED = "identity_failed"

    POLICY_ALLOWED = "policy_allowed"
    POLICY_DENIED = "policy_denied"
    POLICY_FAILED = "policy_failed"

    EVIDENCE_AVAILABLE = "evidence_available"
    EVIDENCE_INSUFFICIENT = "evidence_insufficient"
    EVIDENCE_FAILED = "evidence_failed"
    EVIDENCE_SECURITY_STOP = "evidence_security_stop"

    EVIDENCE_SUFFICIENT = "evidence_sufficient"
    EVIDENCE_CONFLICTED = "evidence_conflicted"
    ASSESSMENT_FAILED = "assessment_failed"
    ASSESSMENT_SECURITY_STOP = "assessment_security_stop"

    GENERATION_COMPLETED = "generation_completed"
    GENERATION_ABSTAINED = "generation_abstained"
    GENERATION_FAILED = "generation_failed"
    GENERATION_SECURITY_STOP = "generation_security_stop"

    RESPONSE_VALIDATED = "response_validated"
    RESPONSE_ABSTAINED = "response_abstained"
    RESPONSE_REJECTED = "response_rejected"
    RESPONSE_SECURITY_STOP = "response_security_stop"

    TRANSIENT_FAILURE = "transient_failure"
    RETRY_CURRENT_STAGE = "retry_current_stage"


class FailureClassification(StrEnum):
    """Bounded classifications for failed or stopped processing."""

    TRANSIENT = "transient"
    PERMANENT = "permanent"
    DENIAL = "denial"
    ABSTENTION = "abstention"
    SECURITY = "security"


class RuntimeReasonCode(StrEnum):
    """Controlled reason codes emitted by the local runtime."""

    RUNTIME_CREATED = "RUNTIME_CREATED"

    REQUEST_VALIDATION_STARTED = "REQUEST_VALIDATION_STARTED"
    REQUEST_VALIDATED = "REQUEST_VALIDATED"
    INVALID_REQUEST = "INVALID_REQUEST"

    IDENTITY_VALIDATED = "IDENTITY_VALIDATED"
    IDENTITY_REQUIRED = "IDENTITY_REQUIRED"
    IDENTITY_EXPIRED = "IDENTITY_EXPIRED"

    POLICY_ALLOWED = "POLICY_ALLOWED"
    ACCESS_DENIED = "ACCESS_DENIED"
    POLICY_UNAVAILABLE = "POLICY_UNAVAILABLE"
    AUTHORIZATION_EXPIRED = "AUTHORIZATION_EXPIRED"

    EVIDENCE_AVAILABLE = "EVIDENCE_AVAILABLE"
    EVIDENCE_SUFFICIENT = "EVIDENCE_SUFFICIENT"
    EVIDENCE_INSUFFICIENT = "EVIDENCE_INSUFFICIENT"
    EVIDENCE_CONFLICT = "EVIDENCE_CONFLICT"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    EVIDENCE_INTEGRITY_FAILURE = "EVIDENCE_INTEGRITY_FAILURE"

    GENERATION_COMPLETED = "GENERATION_COMPLETED"
    GENERATION_ABSTAINED = "GENERATION_ABSTAINED"
    GENERATION_FAILED = "GENERATION_FAILED"

    RESPONSE_VALIDATED = "RESPONSE_VALIDATED"
    RESPONSE_INVALID = "RESPONSE_INVALID"

    TRANSIENT_FAILURE_RECORDED = "TRANSIENT_FAILURE_RECORDED"
    RETRY_SCHEDULED = "RETRY_SCHEDULED"
    STEP_BUDGET_EXHAUSTED = "STEP_BUDGET_EXHAUSTED"
    RETRY_BUDGET_EXHAUSTED = "RETRY_BUDGET_EXHAUSTED"
    STAGE_RETRY_BUDGET_EXHAUSTED = "STAGE_RETRY_BUDGET_EXHAUSTED"

    INVALID_TRANSITION = "INVALID_TRANSITION"
    VERSION_CONFLICT = "VERSION_CONFLICT"

    CHECKPOINT_INTEGRITY_FAILURE = "CHECKPOINT_INTEGRITY_FAILURE"
    REPLAY_DIVERGENCE = "REPLAY_DIVERGENCE"
    REPLAY_VERIFIED = "REPLAY_VERIFIED"

    SECURITY_CONTAINMENT = "SECURITY_CONTAINMENT"


INITIAL_STATES: Final[frozenset[RuntimeState]] = frozenset(
    {
        RuntimeState.RECEIVED,
    }
)

ACTIVE_STATES: Final[frozenset[RuntimeState]] = frozenset(
    {
        RuntimeState.REQUEST_VALIDATING,
        RuntimeState.IDENTITY_VALIDATING,
        RuntimeState.POLICY_EVALUATING,
        RuntimeState.EVIDENCE_PENDING,
        RuntimeState.EVIDENCE_ASSESSING,
        RuntimeState.GENERATION_PENDING,
        RuntimeState.RESPONSE_VALIDATING,
    }
)

TERMINAL_STATES: Final[frozenset[RuntimeState]] = frozenset(
    {
        RuntimeState.COMPLETED_RECOMMENDATION,
        RuntimeState.COMPLETED_ABSTENTION,
        RuntimeState.COMPLETED_DENIAL,
        RuntimeState.COMPLETED_FAILURE,
        RuntimeState.COMPLETED_SECURITY_STOP,
    }
)

_STATE_TYPES: Final[dict[RuntimeState, RuntimeStateType]] = {
    RuntimeState.RECEIVED: RuntimeStateType.INITIAL,
    **{state: RuntimeStateType.ACTIVE for state in ACTIVE_STATES},
    **{state: RuntimeStateType.TERMINAL for state in TERMINAL_STATES},
}

STATE_TYPES: Final = MappingProxyType(_STATE_TYPES)


def state_type(state: RuntimeState) -> RuntimeStateType:
    """Return the lifecycle classification for a runtime state."""

    return STATE_TYPES[state]


def is_terminal_state(state: RuntimeState) -> bool:
    """Return whether a state permanently ends runtime processing."""

    return state in TERMINAL_STATES
