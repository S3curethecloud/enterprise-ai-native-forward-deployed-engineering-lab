"""Explicit stop-condition evaluation for the Phase 4 runtime."""

from enum import StrEnum
from types import MappingProxyType
from typing import Final, Self

from pydantic import model_validator

from incident_diagnostic_api.contracts.common import (
    ContractModel,
    ReasonCode,
    ShortText,
    Timestamp,
)
from incident_diagnostic_api.runtime.budgets import RuntimeBudgetLimits
from incident_diagnostic_api.runtime.enums import (
    RuntimeReasonCode,
    RuntimeState,
)
from incident_diagnostic_api.runtime.models import RuntimeStateRecord


class StopDisposition(StrEnum):
    """Permitted outcomes from deterministic stop evaluation."""

    CONTINUE = "continue"
    COMPLETE_RECOMMENDATION = "complete_recommendation"
    ABSTAIN = "abstain"
    DENY = "deny"
    FAIL = "fail"
    SECURITY_STOP = "security_stop"


class StopCondition(StrEnum):
    """Bounded conditions that can stop local runtime coordination."""

    NONE = "none"
    TERMINAL_STATE = "terminal_state"
    AUTHORIZATION_EXPIRED = "authorization_expired"
    STEP_BUDGET_EXHAUSTED = "step_budget_exhausted"
    RETRY_BUDGET_EXHAUSTED = "retry_budget_exhausted"
    STAGE_RETRY_BUDGET_EXHAUSTED = "stage_retry_budget_exhausted"


class StopDecision(ContractModel):
    """Immutable result from deterministic stop evaluation."""

    should_stop: bool
    disposition: StopDisposition
    condition: StopCondition
    reason_code: RuntimeReasonCode | ReasonCode | None = None
    safe_message: ShortText
    evaluated_at: Timestamp

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        """Keep continuation and stop fields internally consistent."""

        if self.should_stop:
            if self.disposition is StopDisposition.CONTINUE:
                raise ValueError("a stop decision cannot use the continue disposition")

            if self.condition is StopCondition.NONE:
                raise ValueError("a stop decision requires an explicit condition")

            if self.reason_code is None:
                raise ValueError("a stop decision requires an explicit reason code")
        else:
            if self.disposition is not StopDisposition.CONTINUE:
                raise ValueError("a continuation decision must use continue disposition")

            if self.condition is not StopCondition.NONE:
                raise ValueError("a continuation decision cannot declare a stop condition")

            if self.reason_code is not None:
                raise ValueError("a continuation decision cannot declare a reason code")

        return self

    @property
    def allows_continuation(self) -> bool:
        """Return whether runtime coordination may continue."""

        return not self.should_stop


_TERMINAL_DISPOSITIONS: Final[dict[RuntimeState, StopDisposition]] = {
    RuntimeState.COMPLETED_RECOMMENDATION: (StopDisposition.COMPLETE_RECOMMENDATION),
    RuntimeState.COMPLETED_ABSTENTION: StopDisposition.ABSTAIN,
    RuntimeState.COMPLETED_DENIAL: StopDisposition.DENY,
    RuntimeState.COMPLETED_FAILURE: StopDisposition.FAIL,
    RuntimeState.COMPLETED_SECURITY_STOP: StopDisposition.SECURITY_STOP,
}

TERMINAL_DISPOSITIONS: Final = MappingProxyType(_TERMINAL_DISPOSITIONS)


def _latest_reason_code(
    record: RuntimeStateRecord,
) -> RuntimeReasonCode | ReasonCode:
    """Return the latest recorded reason or a controlled fallback."""

    if record.reason_codes:
        return record.reason_codes[-1]

    return RuntimeReasonCode.INVALID_TRANSITION


def _continue_decision(evaluated_at: Timestamp) -> StopDecision:
    """Build the canonical continue decision."""

    return StopDecision(
        should_stop=False,
        disposition=StopDisposition.CONTINUE,
        condition=StopCondition.NONE,
        safe_message="Runtime coordination may continue.",
        evaluated_at=evaluated_at,
    )


def evaluate_pre_transition_stop(
    record: RuntimeStateRecord,
    limits: RuntimeBudgetLimits,
    evaluated_at: Timestamp,
) -> StopDecision:
    """Evaluate deterministic stops before a normal transition."""

    terminal_disposition = TERMINAL_DISPOSITIONS.get(record.state)

    if terminal_disposition is not None:
        return StopDecision(
            should_stop=True,
            disposition=terminal_disposition,
            condition=StopCondition.TERMINAL_STATE,
            reason_code=_latest_reason_code(record),
            safe_message="The workflow is already terminal.",
            evaluated_at=evaluated_at,
        )

    if (
        record.authorization_expires_at is not None
        and evaluated_at >= record.authorization_expires_at
    ):
        return StopDecision(
            should_stop=True,
            disposition=StopDisposition.DENY,
            condition=StopCondition.AUTHORIZATION_EXPIRED,
            reason_code=RuntimeReasonCode.AUTHORIZATION_EXPIRED,
            safe_message="The referenced authorization has expired.",
            evaluated_at=evaluated_at,
        )

    if record.step_count >= limits.max_steps:
        return StopDecision(
            should_stop=True,
            disposition=StopDisposition.FAIL,
            condition=StopCondition.STEP_BUDGET_EXHAUSTED,
            reason_code=RuntimeReasonCode.STEP_BUDGET_EXHAUSTED,
            safe_message="The workflow step budget is exhausted.",
            evaluated_at=evaluated_at,
        )

    return _continue_decision(evaluated_at)


def evaluate_retry_stop(
    record: RuntimeStateRecord,
    limits: RuntimeBudgetLimits,
    evaluated_at: Timestamp,
) -> StopDecision:
    """Evaluate deterministic stops before retrying the current state."""

    pre_transition = evaluate_pre_transition_stop(
        record,
        limits,
        evaluated_at,
    )

    if pre_transition.should_stop:
        return pre_transition

    if record.retry_count >= limits.max_retries:
        return StopDecision(
            should_stop=True,
            disposition=StopDisposition.FAIL,
            condition=StopCondition.RETRY_BUDGET_EXHAUSTED,
            reason_code=RuntimeReasonCode.RETRY_BUDGET_EXHAUSTED,
            safe_message="The workflow retry budget is exhausted.",
            evaluated_at=evaluated_at,
        )

    if record.retry_count_for(record.state) >= limits.max_stage_retries:
        return StopDecision(
            should_stop=True,
            disposition=StopDisposition.FAIL,
            condition=StopCondition.STAGE_RETRY_BUDGET_EXHAUSTED,
            reason_code=(RuntimeReasonCode.STAGE_RETRY_BUDGET_EXHAUSTED),
            safe_message="The current-stage retry budget is exhausted.",
            evaluated_at=evaluated_at,
        )

    return _continue_decision(evaluated_at)
