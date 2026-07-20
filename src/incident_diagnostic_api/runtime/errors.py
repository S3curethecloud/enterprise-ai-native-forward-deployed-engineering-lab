"""Controlled exceptions for the Phase 4 deterministic runtime."""

from dataclasses import dataclass

from incident_diagnostic_api.runtime.enums import (
    RuntimeReasonCode,
    RuntimeState,
    TransitionCommand,
)


@dataclass(frozen=True, slots=True)
class RuntimeTransitionError(Exception):
    """Base exception for a rejected runtime transition."""

    message: str
    reason_code: RuntimeReasonCode
    current_state: RuntimeState
    command: TransitionCommand

    def __str__(self) -> str:
        """Return a controlled, non-sensitive error description."""

        return self.message


class InvalidTransitionError(RuntimeTransitionError):
    """Raised when a command is invalid for the current state."""

    def __init__(
        self,
        *,
        current_state: RuntimeState,
        command: TransitionCommand,
    ) -> None:
        super().__init__(
            message=(f"command {command.value!r} is not valid from state {current_state.value!r}"),
            reason_code=RuntimeReasonCode.INVALID_TRANSITION,
            current_state=current_state,
            command=command,
        )


class TerminalStateTransitionError(RuntimeTransitionError):
    """Raised when a command attempts to leave a terminal state."""

    def __init__(
        self,
        *,
        current_state: RuntimeState,
        command: TransitionCommand,
    ) -> None:
        super().__init__(
            message=(f"terminal state {current_state.value!r} does not accept transition commands"),
            reason_code=RuntimeReasonCode.INVALID_TRANSITION,
            current_state=current_state,
            command=command,
        )
