"""Tests for the authoritative Phase 4 runtime transition table."""

import pytest

from incident_diagnostic_api.runtime import (
    TERMINAL_STATES,
    TRANSITIONS,
    InvalidTransitionError,
    RuntimeReasonCode,
    RuntimeState,
    TerminalStateTransitionError,
    TransitionCommand,
    allowed_commands,
    is_transition_allowed,
    resolve_transition,
)

EXPECTED_TRANSITIONS = {
    (
        RuntimeState.RECEIVED,
        TransitionCommand.BEGIN_REQUEST_VALIDATION,
        RuntimeState.REQUEST_VALIDATING,
    ),
    (
        RuntimeState.REQUEST_VALIDATING,
        TransitionCommand.REQUEST_VALIDATED,
        RuntimeState.IDENTITY_VALIDATING,
    ),
    (
        RuntimeState.REQUEST_VALIDATING,
        TransitionCommand.REQUEST_REJECTED,
        RuntimeState.COMPLETED_FAILURE,
    ),
    (
        RuntimeState.IDENTITY_VALIDATING,
        TransitionCommand.IDENTITY_VALIDATED,
        RuntimeState.POLICY_EVALUATING,
    ),
    (
        RuntimeState.IDENTITY_VALIDATING,
        TransitionCommand.IDENTITY_DENIED,
        RuntimeState.COMPLETED_DENIAL,
    ),
    (
        RuntimeState.IDENTITY_VALIDATING,
        TransitionCommand.IDENTITY_FAILED,
        RuntimeState.COMPLETED_FAILURE,
    ),
    (
        RuntimeState.POLICY_EVALUATING,
        TransitionCommand.POLICY_ALLOWED,
        RuntimeState.EVIDENCE_PENDING,
    ),
    (
        RuntimeState.POLICY_EVALUATING,
        TransitionCommand.POLICY_DENIED,
        RuntimeState.COMPLETED_DENIAL,
    ),
    (
        RuntimeState.POLICY_EVALUATING,
        TransitionCommand.POLICY_FAILED,
        RuntimeState.COMPLETED_FAILURE,
    ),
    (
        RuntimeState.EVIDENCE_PENDING,
        TransitionCommand.EVIDENCE_AVAILABLE,
        RuntimeState.EVIDENCE_ASSESSING,
    ),
    (
        RuntimeState.EVIDENCE_PENDING,
        TransitionCommand.EVIDENCE_INSUFFICIENT,
        RuntimeState.COMPLETED_ABSTENTION,
    ),
    (
        RuntimeState.EVIDENCE_PENDING,
        TransitionCommand.EVIDENCE_FAILED,
        RuntimeState.COMPLETED_FAILURE,
    ),
    (
        RuntimeState.EVIDENCE_PENDING,
        TransitionCommand.EVIDENCE_SECURITY_STOP,
        RuntimeState.COMPLETED_SECURITY_STOP,
    ),
    (
        RuntimeState.EVIDENCE_ASSESSING,
        TransitionCommand.EVIDENCE_SUFFICIENT,
        RuntimeState.GENERATION_PENDING,
    ),
    (
        RuntimeState.EVIDENCE_ASSESSING,
        TransitionCommand.EVIDENCE_CONFLICTED,
        RuntimeState.COMPLETED_ABSTENTION,
    ),
    (
        RuntimeState.EVIDENCE_ASSESSING,
        TransitionCommand.ASSESSMENT_FAILED,
        RuntimeState.COMPLETED_FAILURE,
    ),
    (
        RuntimeState.EVIDENCE_ASSESSING,
        TransitionCommand.ASSESSMENT_SECURITY_STOP,
        RuntimeState.COMPLETED_SECURITY_STOP,
    ),
    (
        RuntimeState.GENERATION_PENDING,
        TransitionCommand.GENERATION_COMPLETED,
        RuntimeState.RESPONSE_VALIDATING,
    ),
    (
        RuntimeState.GENERATION_PENDING,
        TransitionCommand.GENERATION_ABSTAINED,
        RuntimeState.COMPLETED_ABSTENTION,
    ),
    (
        RuntimeState.GENERATION_PENDING,
        TransitionCommand.GENERATION_FAILED,
        RuntimeState.COMPLETED_FAILURE,
    ),
    (
        RuntimeState.GENERATION_PENDING,
        TransitionCommand.GENERATION_SECURITY_STOP,
        RuntimeState.COMPLETED_SECURITY_STOP,
    ),
    (
        RuntimeState.RESPONSE_VALIDATING,
        TransitionCommand.RESPONSE_VALIDATED,
        RuntimeState.COMPLETED_RECOMMENDATION,
    ),
    (
        RuntimeState.RESPONSE_VALIDATING,
        TransitionCommand.RESPONSE_ABSTAINED,
        RuntimeState.COMPLETED_ABSTENTION,
    ),
    (
        RuntimeState.RESPONSE_VALIDATING,
        TransitionCommand.RESPONSE_REJECTED,
        RuntimeState.COMPLETED_FAILURE,
    ),
    (
        RuntimeState.RESPONSE_VALIDATING,
        TransitionCommand.RESPONSE_SECURITY_STOP,
        RuntimeState.COMPLETED_SECURITY_STOP,
    ),
}


def test_exactly_25_authoritative_transitions_are_defined() -> None:
    """The executable table exactly matches the approved design."""

    actual = {
        (
            transition.source,
            transition.command,
            transition.target,
        )
        for transition in TRANSITIONS.values()
    }

    assert len(TRANSITIONS) == 25
    assert actual == EXPECTED_TRANSITIONS


@pytest.mark.parametrize(
    ("source", "command", "target"),
    tuple(EXPECTED_TRANSITIONS),
)
def test_every_authorized_transition_resolves(
    source: RuntimeState,
    command: TransitionCommand,
    target: RuntimeState,
) -> None:
    """Every approved state-command pair resolves deterministically."""

    transition = resolve_transition(source, command)

    assert transition.source is source
    assert transition.command is command
    assert transition.target is target
    assert is_transition_allowed(source, command)


def test_transition_keys_match_their_definitions() -> None:
    """No mapping key can disagree with its transition payload."""

    for (source, command), transition in TRANSITIONS.items():
        assert transition.source is source
        assert transition.command is command


@pytest.mark.parametrize("state", list(RuntimeState))
def test_allowed_commands_match_authoritative_table(
    state: RuntimeState,
) -> None:
    """Command discovery is derived only from the approved table."""

    expected = tuple(
        sorted(
            (command for source, command in TRANSITIONS if source is state),
            key=lambda command: command.value,
        )
    )

    assert allowed_commands(state) == expected


@pytest.mark.parametrize(
    "terminal_state",
    tuple(TERMINAL_STATES),
)
@pytest.mark.parametrize("command", list(TransitionCommand))
def test_terminal_states_reject_every_command(
    terminal_state: RuntimeState,
    command: TransitionCommand,
) -> None:
    """No command can restart or escape a terminal workflow."""

    with pytest.raises(TerminalStateTransitionError) as captured:
        resolve_transition(terminal_state, command)

    error = captured.value

    assert error.reason_code is RuntimeReasonCode.INVALID_TRANSITION
    assert error.current_state is terminal_state
    assert error.command is command
    assert not is_transition_allowed(terminal_state, command)


@pytest.mark.parametrize(
    ("state", "command"),
    [
        (
            RuntimeState.RECEIVED,
            TransitionCommand.RESPONSE_VALIDATED,
        ),
        (
            RuntimeState.REQUEST_VALIDATING,
            TransitionCommand.POLICY_ALLOWED,
        ),
        (
            RuntimeState.IDENTITY_VALIDATING,
            TransitionCommand.EVIDENCE_AVAILABLE,
        ),
        (
            RuntimeState.POLICY_EVALUATING,
            TransitionCommand.REQUEST_VALIDATED,
        ),
        (
            RuntimeState.EVIDENCE_PENDING,
            TransitionCommand.GENERATION_COMPLETED,
        ),
        (
            RuntimeState.EVIDENCE_ASSESSING,
            TransitionCommand.RESPONSE_VALIDATED,
        ),
        (
            RuntimeState.GENERATION_PENDING,
            TransitionCommand.POLICY_ALLOWED,
        ),
        (
            RuntimeState.RESPONSE_VALIDATING,
            TransitionCommand.EVIDENCE_SUFFICIENT,
        ),
    ],
)
def test_invalid_active_state_commands_fail_closed(
    state: RuntimeState,
    command: TransitionCommand,
) -> None:
    """Commands absent from the table are rejected without inference."""

    with pytest.raises(InvalidTransitionError) as captured:
        resolve_transition(state, command)

    error = captured.value

    assert error.reason_code is RuntimeReasonCode.INVALID_TRANSITION
    assert error.current_state is state
    assert error.command is command
    assert not is_transition_allowed(state, command)


def test_retry_control_commands_are_not_normal_state_transitions() -> None:
    """Retry commands require the separate budget mechanism in Phase 4D."""

    for state in RuntimeState:
        assert not is_transition_allowed(
            state,
            TransitionCommand.TRANSIENT_FAILURE,
        )
        assert not is_transition_allowed(
            state,
            TransitionCommand.RETRY_CURRENT_STAGE,
        )


def test_security_stop_routes_are_explicit() -> None:
    """Only approved security commands reach security containment."""

    security_routes = {
        (transition.source, transition.command)
        for transition in TRANSITIONS.values()
        if transition.target is RuntimeState.COMPLETED_SECURITY_STOP
    }

    assert security_routes == {
        (
            RuntimeState.EVIDENCE_PENDING,
            TransitionCommand.EVIDENCE_SECURITY_STOP,
        ),
        (
            RuntimeState.EVIDENCE_ASSESSING,
            TransitionCommand.ASSESSMENT_SECURITY_STOP,
        ),
        (
            RuntimeState.GENERATION_PENDING,
            TransitionCommand.GENERATION_SECURITY_STOP,
        ),
        (
            RuntimeState.RESPONSE_VALIDATING,
            TransitionCommand.RESPONSE_SECURITY_STOP,
        ),
    }


def test_recommendation_has_one_explicit_entry_route() -> None:
    """A recommendation requires successful response validation."""

    recommendation_routes = {
        (transition.source, transition.command)
        for transition in TRANSITIONS.values()
        if transition.target is RuntimeState.COMPLETED_RECOMMENDATION
    }

    assert recommendation_routes == {
        (
            RuntimeState.RESPONSE_VALIDATING,
            TransitionCommand.RESPONSE_VALIDATED,
        )
    }
