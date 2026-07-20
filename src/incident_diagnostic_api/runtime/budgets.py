"""Deterministic step and retry budgets for the Phase 4 runtime."""

from dataclasses import dataclass
from typing import Self

from pydantic import Field, model_validator

from incident_diagnostic_api.contracts.common import ContractModel
from incident_diagnostic_api.runtime.enums import (
    RuntimeReasonCode,
    RuntimeState,
    is_terminal_state,
)
from incident_diagnostic_api.runtime.models import (
    RuntimeStateRecord,
    StageRetryCount,
)


class RuntimeBudgetLimits(ContractModel):
    """Immutable limits for one bounded workflow execution."""

    max_steps: int = Field(default=16, ge=1, le=32)
    max_retries: int = Field(default=2, ge=0, le=5)
    max_stage_retries: int = Field(default=1, ge=0, le=4)

    @model_validator(mode="after")
    def validate_retry_relationship(self) -> Self:
        """Keep a per-stage budget within the total retry budget."""

        if self.max_stage_retries > self.max_retries:
            raise ValueError("max_stage_retries cannot exceed max_retries")

        return self


@dataclass(frozen=True, slots=True)
class RuntimeBudgetExceededError(Exception):
    """Controlled failure raised when a runtime budget is exhausted."""

    message: str
    reason_code: RuntimeReasonCode
    state: RuntimeState
    current_count: int
    maximum_count: int

    def __str__(self) -> str:
        """Return a controlled, non-sensitive error description."""

        return self.message


def ensure_step_budget(
    record: RuntimeStateRecord,
    limits: RuntimeBudgetLimits,
) -> None:
    """Ensure another state-changing step may be recorded."""

    if is_terminal_state(record.state):
        raise RuntimeBudgetExceededError(
            message=(f"terminal state {record.state.value!r} cannot consume another step"),
            reason_code=RuntimeReasonCode.INVALID_TRANSITION,
            state=record.state,
            current_count=record.step_count,
            maximum_count=limits.max_steps,
        )

    if record.step_count >= limits.max_steps:
        raise RuntimeBudgetExceededError(
            message=(f"step budget exhausted at {record.step_count} of {limits.max_steps}"),
            reason_code=RuntimeReasonCode.STEP_BUDGET_EXHAUSTED,
            state=record.state,
            current_count=record.step_count,
            maximum_count=limits.max_steps,
        )


def ensure_retry_budget(
    record: RuntimeStateRecord,
    limits: RuntimeBudgetLimits,
) -> None:
    """Ensure one retry is allowed for the current active state."""

    ensure_step_budget(record, limits)

    if record.retry_count >= limits.max_retries:
        raise RuntimeBudgetExceededError(
            message=(f"retry budget exhausted at {record.retry_count} of {limits.max_retries}"),
            reason_code=RuntimeReasonCode.RETRY_BUDGET_EXHAUSTED,
            state=record.state,
            current_count=record.retry_count,
            maximum_count=limits.max_retries,
        )

    stage_retry_count = record.retry_count_for(record.state)

    if stage_retry_count >= limits.max_stage_retries:
        raise RuntimeBudgetExceededError(
            message=(
                f"stage retry budget for {record.state.value!r} "
                f"exhausted at {stage_retry_count} "
                f"of {limits.max_stage_retries}"
            ),
            reason_code=(RuntimeReasonCode.STAGE_RETRY_BUDGET_EXHAUSTED),
            state=record.state,
            current_count=stage_retry_count,
            maximum_count=limits.max_stage_retries,
        )


def increment_stage_retry_counts(
    record: RuntimeStateRecord,
) -> tuple[StageRetryCount, ...]:
    """Return an immutable stage-counter tuple for one accepted retry."""

    updated: list[StageRetryCount] = []
    found_current_state = False

    for item in record.stage_retry_counts:
        if item.state is record.state:
            updated.append(
                StageRetryCount(
                    state=item.state,
                    retry_count=item.retry_count + 1,
                )
            )
            found_current_state = True
        else:
            updated.append(item)

    if not found_current_state:
        updated.append(
            StageRetryCount(
                state=record.state,
                retry_count=1,
            )
        )

    return tuple(sorted(updated, key=lambda item: item.state.value))
