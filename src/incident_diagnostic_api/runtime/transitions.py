"""Authoritative transitions for the Phase 4 deterministic runtime."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

from incident_diagnostic_api.runtime.enums import (
    RuntimeReasonCode,
    RuntimeState,
    TransitionCommand,
    is_terminal_state,
)
from incident_diagnostic_api.runtime.errors import (
    InvalidTransitionError,
    TerminalStateTransitionError,
)


@dataclass(frozen=True, slots=True)
class TransitionDefinition:
    """One explicitly authorized runtime transition."""

    source: RuntimeState
    command: TransitionCommand
    target: RuntimeState
    reason_code: RuntimeReasonCode


type TransitionKey = tuple[RuntimeState, TransitionCommand]


_TRANSITIONS: Final[dict[TransitionKey, TransitionDefinition]] = {
    (
        RuntimeState.RECEIVED,
        TransitionCommand.BEGIN_REQUEST_VALIDATION,
    ): TransitionDefinition(
        source=RuntimeState.RECEIVED,
        command=TransitionCommand.BEGIN_REQUEST_VALIDATION,
        target=RuntimeState.REQUEST_VALIDATING,
        reason_code=RuntimeReasonCode.REQUEST_VALIDATION_STARTED,
    ),
    (
        RuntimeState.REQUEST_VALIDATING,
        TransitionCommand.REQUEST_VALIDATED,
    ): TransitionDefinition(
        source=RuntimeState.REQUEST_VALIDATING,
        command=TransitionCommand.REQUEST_VALIDATED,
        target=RuntimeState.IDENTITY_VALIDATING,
        reason_code=RuntimeReasonCode.REQUEST_VALIDATED,
    ),
    (
        RuntimeState.REQUEST_VALIDATING,
        TransitionCommand.REQUEST_REJECTED,
    ): TransitionDefinition(
        source=RuntimeState.REQUEST_VALIDATING,
        command=TransitionCommand.REQUEST_REJECTED,
        target=RuntimeState.COMPLETED_FAILURE,
        reason_code=RuntimeReasonCode.INVALID_REQUEST,
    ),
    (
        RuntimeState.IDENTITY_VALIDATING,
        TransitionCommand.IDENTITY_VALIDATED,
    ): TransitionDefinition(
        source=RuntimeState.IDENTITY_VALIDATING,
        command=TransitionCommand.IDENTITY_VALIDATED,
        target=RuntimeState.POLICY_EVALUATING,
        reason_code=RuntimeReasonCode.IDENTITY_VALIDATED,
    ),
    (
        RuntimeState.IDENTITY_VALIDATING,
        TransitionCommand.IDENTITY_DENIED,
    ): TransitionDefinition(
        source=RuntimeState.IDENTITY_VALIDATING,
        command=TransitionCommand.IDENTITY_DENIED,
        target=RuntimeState.COMPLETED_DENIAL,
        reason_code=RuntimeReasonCode.ACCESS_DENIED,
    ),
    (
        RuntimeState.IDENTITY_VALIDATING,
        TransitionCommand.IDENTITY_FAILED,
    ): TransitionDefinition(
        source=RuntimeState.IDENTITY_VALIDATING,
        command=TransitionCommand.IDENTITY_FAILED,
        target=RuntimeState.COMPLETED_FAILURE,
        reason_code=RuntimeReasonCode.IDENTITY_REQUIRED,
    ),
    (
        RuntimeState.POLICY_EVALUATING,
        TransitionCommand.POLICY_ALLOWED,
    ): TransitionDefinition(
        source=RuntimeState.POLICY_EVALUATING,
        command=TransitionCommand.POLICY_ALLOWED,
        target=RuntimeState.EVIDENCE_PENDING,
        reason_code=RuntimeReasonCode.POLICY_ALLOWED,
    ),
    (
        RuntimeState.POLICY_EVALUATING,
        TransitionCommand.POLICY_DENIED,
    ): TransitionDefinition(
        source=RuntimeState.POLICY_EVALUATING,
        command=TransitionCommand.POLICY_DENIED,
        target=RuntimeState.COMPLETED_DENIAL,
        reason_code=RuntimeReasonCode.ACCESS_DENIED,
    ),
    (
        RuntimeState.POLICY_EVALUATING,
        TransitionCommand.POLICY_FAILED,
    ): TransitionDefinition(
        source=RuntimeState.POLICY_EVALUATING,
        command=TransitionCommand.POLICY_FAILED,
        target=RuntimeState.COMPLETED_FAILURE,
        reason_code=RuntimeReasonCode.POLICY_UNAVAILABLE,
    ),
    (
        RuntimeState.EVIDENCE_PENDING,
        TransitionCommand.EVIDENCE_AVAILABLE,
    ): TransitionDefinition(
        source=RuntimeState.EVIDENCE_PENDING,
        command=TransitionCommand.EVIDENCE_AVAILABLE,
        target=RuntimeState.EVIDENCE_ASSESSING,
        reason_code=RuntimeReasonCode.EVIDENCE_AVAILABLE,
    ),
    (
        RuntimeState.EVIDENCE_PENDING,
        TransitionCommand.EVIDENCE_INSUFFICIENT,
    ): TransitionDefinition(
        source=RuntimeState.EVIDENCE_PENDING,
        command=TransitionCommand.EVIDENCE_INSUFFICIENT,
        target=RuntimeState.COMPLETED_ABSTENTION,
        reason_code=RuntimeReasonCode.EVIDENCE_INSUFFICIENT,
    ),
    (
        RuntimeState.EVIDENCE_PENDING,
        TransitionCommand.EVIDENCE_FAILED,
    ): TransitionDefinition(
        source=RuntimeState.EVIDENCE_PENDING,
        command=TransitionCommand.EVIDENCE_FAILED,
        target=RuntimeState.COMPLETED_FAILURE,
        reason_code=RuntimeReasonCode.SOURCE_UNAVAILABLE,
    ),
    (
        RuntimeState.EVIDENCE_PENDING,
        TransitionCommand.EVIDENCE_SECURITY_STOP,
    ): TransitionDefinition(
        source=RuntimeState.EVIDENCE_PENDING,
        command=TransitionCommand.EVIDENCE_SECURITY_STOP,
        target=RuntimeState.COMPLETED_SECURITY_STOP,
        reason_code=RuntimeReasonCode.SECURITY_CONTAINMENT,
    ),
    (
        RuntimeState.EVIDENCE_ASSESSING,
        TransitionCommand.EVIDENCE_SUFFICIENT,
    ): TransitionDefinition(
        source=RuntimeState.EVIDENCE_ASSESSING,
        command=TransitionCommand.EVIDENCE_SUFFICIENT,
        target=RuntimeState.GENERATION_PENDING,
        reason_code=RuntimeReasonCode.EVIDENCE_SUFFICIENT,
    ),
    (
        RuntimeState.EVIDENCE_ASSESSING,
        TransitionCommand.EVIDENCE_CONFLICTED,
    ): TransitionDefinition(
        source=RuntimeState.EVIDENCE_ASSESSING,
        command=TransitionCommand.EVIDENCE_CONFLICTED,
        target=RuntimeState.COMPLETED_ABSTENTION,
        reason_code=RuntimeReasonCode.EVIDENCE_CONFLICT,
    ),
    (
        RuntimeState.EVIDENCE_ASSESSING,
        TransitionCommand.ASSESSMENT_FAILED,
    ): TransitionDefinition(
        source=RuntimeState.EVIDENCE_ASSESSING,
        command=TransitionCommand.ASSESSMENT_FAILED,
        target=RuntimeState.COMPLETED_FAILURE,
        reason_code=RuntimeReasonCode.EVIDENCE_INTEGRITY_FAILURE,
    ),
    (
        RuntimeState.EVIDENCE_ASSESSING,
        TransitionCommand.ASSESSMENT_SECURITY_STOP,
    ): TransitionDefinition(
        source=RuntimeState.EVIDENCE_ASSESSING,
        command=TransitionCommand.ASSESSMENT_SECURITY_STOP,
        target=RuntimeState.COMPLETED_SECURITY_STOP,
        reason_code=RuntimeReasonCode.SECURITY_CONTAINMENT,
    ),
    (
        RuntimeState.GENERATION_PENDING,
        TransitionCommand.GENERATION_COMPLETED,
    ): TransitionDefinition(
        source=RuntimeState.GENERATION_PENDING,
        command=TransitionCommand.GENERATION_COMPLETED,
        target=RuntimeState.RESPONSE_VALIDATING,
        reason_code=RuntimeReasonCode.GENERATION_COMPLETED,
    ),
    (
        RuntimeState.GENERATION_PENDING,
        TransitionCommand.GENERATION_ABSTAINED,
    ): TransitionDefinition(
        source=RuntimeState.GENERATION_PENDING,
        command=TransitionCommand.GENERATION_ABSTAINED,
        target=RuntimeState.COMPLETED_ABSTENTION,
        reason_code=RuntimeReasonCode.GENERATION_ABSTAINED,
    ),
    (
        RuntimeState.GENERATION_PENDING,
        TransitionCommand.GENERATION_FAILED,
    ): TransitionDefinition(
        source=RuntimeState.GENERATION_PENDING,
        command=TransitionCommand.GENERATION_FAILED,
        target=RuntimeState.COMPLETED_FAILURE,
        reason_code=RuntimeReasonCode.GENERATION_FAILED,
    ),
    (
        RuntimeState.GENERATION_PENDING,
        TransitionCommand.GENERATION_SECURITY_STOP,
    ): TransitionDefinition(
        source=RuntimeState.GENERATION_PENDING,
        command=TransitionCommand.GENERATION_SECURITY_STOP,
        target=RuntimeState.COMPLETED_SECURITY_STOP,
        reason_code=RuntimeReasonCode.SECURITY_CONTAINMENT,
    ),
    (
        RuntimeState.RESPONSE_VALIDATING,
        TransitionCommand.RESPONSE_VALIDATED,
    ): TransitionDefinition(
        source=RuntimeState.RESPONSE_VALIDATING,
        command=TransitionCommand.RESPONSE_VALIDATED,
        target=RuntimeState.COMPLETED_RECOMMENDATION,
        reason_code=RuntimeReasonCode.RESPONSE_VALIDATED,
    ),
    (
        RuntimeState.RESPONSE_VALIDATING,
        TransitionCommand.RESPONSE_ABSTAINED,
    ): TransitionDefinition(
        source=RuntimeState.RESPONSE_VALIDATING,
        command=TransitionCommand.RESPONSE_ABSTAINED,
        target=RuntimeState.COMPLETED_ABSTENTION,
        reason_code=RuntimeReasonCode.RESPONSE_INVALID,
    ),
    (
        RuntimeState.RESPONSE_VALIDATING,
        TransitionCommand.RESPONSE_REJECTED,
    ): TransitionDefinition(
        source=RuntimeState.RESPONSE_VALIDATING,
        command=TransitionCommand.RESPONSE_REJECTED,
        target=RuntimeState.COMPLETED_FAILURE,
        reason_code=RuntimeReasonCode.RESPONSE_INVALID,
    ),
    (
        RuntimeState.RESPONSE_VALIDATING,
        TransitionCommand.RESPONSE_SECURITY_STOP,
    ): TransitionDefinition(
        source=RuntimeState.RESPONSE_VALIDATING,
        command=TransitionCommand.RESPONSE_SECURITY_STOP,
        target=RuntimeState.COMPLETED_SECURITY_STOP,
        reason_code=RuntimeReasonCode.SECURITY_CONTAINMENT,
    ),
}

TRANSITIONS: Final = MappingProxyType(_TRANSITIONS)


def allowed_commands(state: RuntimeState) -> tuple[TransitionCommand, ...]:
    """Return the sorted commands explicitly authorized from a state."""

    return tuple(
        sorted(
            (command for source, command in TRANSITIONS if source is state),
            key=lambda command: command.value,
        )
    )


def is_transition_allowed(
    state: RuntimeState,
    command: TransitionCommand,
) -> bool:
    """Return whether an exact state-command pair is authorized."""

    return (state, command) in TRANSITIONS


def resolve_transition(
    state: RuntimeState,
    command: TransitionCommand,
) -> TransitionDefinition:
    """Resolve an authorized transition or fail closed."""

    if is_terminal_state(state):
        raise TerminalStateTransitionError(
            current_state=state,
            command=command,
        )

    transition = TRANSITIONS.get((state, command))

    if transition is None:
        raise InvalidTransitionError(
            current_state=state,
            command=command,
        )

    return transition
