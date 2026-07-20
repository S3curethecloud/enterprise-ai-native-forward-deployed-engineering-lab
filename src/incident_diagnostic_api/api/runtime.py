"""Local-only HTTP routes for deterministic Phase 4 coordination."""

from typing import Annotated, Any, NoReturn

from fastapi import APIRouter, Depends, Request, status

from incident_diagnostic_api.api.runtime_errors import (
    RuntimeApiError,
    RuntimeApiErrorCode,
    raise_runtime_api_error,
)
from incident_diagnostic_api.api.runtime_models import (
    RuntimeRetryApiRequest,
    RuntimeStartRequest,
    RuntimeTransitionRequest,
)
from incident_diagnostic_api.runtime import (
    CheckpointNotFoundError,
    CheckpointVersionConflictError,
    DeterministicRuntimeEngine,
    ReplayIntegrityError,
    ReplayResult,
    RuntimeBudgetExceededError,
    RuntimeCheckpoint,
    RuntimeExecutionStoppedError,
    RuntimeStartResult,
    RuntimeStateRecord,
    RuntimeStepResult,
    RuntimeTransitionError,
    TraceGenerationError,
)

router = APIRouter(
    prefix="/v1/runtime",
    tags=["deterministic-runtime"],
)

RUNTIME_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {
        "model": RuntimeApiError,
        "description": "The local workflow does not exist.",
    },
    409: {
        "model": RuntimeApiError,
        "description": "The deterministic runtime rejected the operation.",
    },
    500: {
        "model": RuntimeApiError,
        "description": "Runtime evidence could not be verified safely.",
    },
}


def get_runtime_engine(request: Request) -> DeterministicRuntimeEngine:
    """Return the application-scoped deterministic runtime engine."""

    engine = getattr(request.app.state, "runtime_engine", None)

    if not isinstance(engine, DeterministicRuntimeEngine):
        raise_runtime_api_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=RuntimeApiErrorCode.RUNTIME_INTERNAL_ERROR,
            safe_message="The local runtime engine is unavailable.",
        )

    return engine


def raise_not_found(error: CheckpointNotFoundError) -> NoReturn:
    """Translate a missing local workflow into a controlled HTTP error."""

    raise_runtime_api_error(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code=RuntimeApiErrorCode.WORKFLOW_NOT_FOUND,
        safe_message="The requested local workflow does not exist.",
        workflow_id=error.workflow_id,
    )


def raise_version_conflict(error: CheckpointVersionConflictError) -> NoReturn:
    """Translate optimistic concurrency failure without leaking internals."""

    raise_runtime_api_error(
        status_code=status.HTTP_409_CONFLICT,
        error_code=RuntimeApiErrorCode.VERSION_CONFLICT,
        safe_message="The expected runtime state version is stale.",
        workflow_id=error.workflow_id,
        reason_code=error.reason_code,
    )


@router.post(
    "/workflows",
    response_model=RuntimeStartResult,
    status_code=status.HTTP_201_CREATED,
    responses=RUNTIME_ERROR_RESPONSES,
    summary="Create one deterministic local workflow",
)
def start_runtime_workflow(
    request: RuntimeStartRequest,
    engine: Annotated[
        DeterministicRuntimeEngine,
        Depends(get_runtime_engine),
    ],
) -> RuntimeStartResult:
    """Create genesis state, checkpoint evidence, and a CT-07 trace."""

    try:
        return engine.start(
            request.record,
            event_id=request.event_id,
            timestamp=request.timestamp,
        )
    except CheckpointVersionConflictError as error:
        raise_version_conflict(error)
    except TraceGenerationError as error:
        raise_runtime_api_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=RuntimeApiErrorCode.RUNTIME_INTERNAL_ERROR,
            safe_message="Runtime genesis evidence could not be generated safely.",
            workflow_id=request.record.workflow_id,
            reason_code=error.reason_code,
        )


@router.get(
    "/workflows/{workflow_id}",
    response_model=RuntimeStateRecord,
    responses=RUNTIME_ERROR_RESPONSES,
    summary="Read the latest immutable workflow state",
)
def get_runtime_workflow(
    workflow_id: str,
    engine: Annotated[
        DeterministicRuntimeEngine,
        Depends(get_runtime_engine),
    ],
) -> RuntimeStateRecord:
    """Return the latest immutable snapshot for one local workflow."""

    try:
        return engine.current(workflow_id)
    except CheckpointNotFoundError as error:
        raise_not_found(error)


@router.post(
    "/workflows/{workflow_id}/transitions",
    response_model=RuntimeStepResult,
    responses=RUNTIME_ERROR_RESPONSES,
    summary="Apply one deterministic runtime transition",
)
def apply_runtime_transition(
    workflow_id: str,
    request: RuntimeTransitionRequest,
    engine: Annotated[
        DeterministicRuntimeEngine,
        Depends(get_runtime_engine),
    ],
) -> RuntimeStepResult:
    """Apply one allowlisted transition with optimistic concurrency."""

    try:
        return engine.apply_transition(
            workflow_id,
            expected_state_version=request.expected_state_version,
            command=request.command,
            event_id=request.event_id,
            timestamp=request.timestamp,
            context=request.context,
            duration_ms=request.duration_ms,
        )
    except CheckpointNotFoundError as error:
        raise_not_found(error)
    except CheckpointVersionConflictError as error:
        raise_version_conflict(error)
    except RuntimeTransitionError as error:
        raise_runtime_api_error(
            status_code=status.HTTP_409_CONFLICT,
            error_code=RuntimeApiErrorCode.INVALID_TRANSITION,
            safe_message=str(error),
            workflow_id=workflow_id,
            state=error.current_state,
            reason_code=error.reason_code,
        )
    except RuntimeBudgetExceededError as error:
        raise_runtime_api_error(
            status_code=status.HTTP_409_CONFLICT,
            error_code=RuntimeApiErrorCode.BUDGET_EXHAUSTED,
            safe_message=str(error),
            workflow_id=workflow_id,
            state=error.state,
            reason_code=error.reason_code,
        )
    except RuntimeExecutionStoppedError as error:
        raise_runtime_api_error(
            status_code=status.HTTP_409_CONFLICT,
            error_code=RuntimeApiErrorCode.EXECUTION_STOPPED,
            safe_message=error.decision.safe_message,
            workflow_id=workflow_id,
            reason_code=error.decision.reason_code,
        )
    except TraceGenerationError as error:
        raise_runtime_api_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=RuntimeApiErrorCode.RUNTIME_INTERNAL_ERROR,
            safe_message="Runtime trace evidence could not be generated safely.",
            workflow_id=workflow_id,
            reason_code=error.reason_code,
        )


@router.post(
    "/workflows/{workflow_id}/retries",
    response_model=RuntimeStepResult,
    responses=RUNTIME_ERROR_RESPONSES,
    summary="Schedule one bounded transient retry",
)
def schedule_runtime_retry(
    workflow_id: str,
    request: RuntimeRetryApiRequest,
    engine: Annotated[
        DeterministicRuntimeEngine,
        Depends(get_runtime_engine),
    ],
) -> RuntimeStepResult:
    """Schedule a retry only when typed transient-failure evidence exists."""

    try:
        return engine.schedule_retry(
            workflow_id,
            expected_state_version=request.expected_state_version,
            retry_request=request.retry_request,
            event_id=request.event_id,
            timestamp=request.timestamp,
            duration_ms=request.duration_ms,
        )
    except CheckpointNotFoundError as error:
        raise_not_found(error)
    except CheckpointVersionConflictError as error:
        raise_version_conflict(error)
    except RuntimeBudgetExceededError as error:
        raise_runtime_api_error(
            status_code=status.HTTP_409_CONFLICT,
            error_code=RuntimeApiErrorCode.BUDGET_EXHAUSTED,
            safe_message=str(error),
            workflow_id=workflow_id,
            state=error.state,
            reason_code=error.reason_code,
        )
    except RuntimeExecutionStoppedError as error:
        raise_runtime_api_error(
            status_code=status.HTTP_409_CONFLICT,
            error_code=RuntimeApiErrorCode.EXECUTION_STOPPED,
            safe_message=error.decision.safe_message,
            workflow_id=workflow_id,
            reason_code=error.decision.reason_code,
        )
    except TraceGenerationError as error:
        raise_runtime_api_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=RuntimeApiErrorCode.RUNTIME_INTERNAL_ERROR,
            safe_message="Runtime trace evidence could not be generated safely.",
            workflow_id=workflow_id,
            reason_code=error.reason_code,
        )


@router.get(
    "/workflows/{workflow_id}/checkpoints",
    response_model=tuple[RuntimeCheckpoint, ...],
    responses=RUNTIME_ERROR_RESPONSES,
    summary="Read append-only checkpoint evidence",
)
def get_runtime_checkpoints(
    workflow_id: str,
    engine: Annotated[
        DeterministicRuntimeEngine,
        Depends(get_runtime_engine),
    ],
) -> tuple[RuntimeCheckpoint, ...]:
    """Return immutable checkpoint history for one local workflow."""

    try:
        return engine.checkpoint_history(workflow_id)
    except CheckpointNotFoundError as error:
        raise_not_found(error)


@router.get(
    "/workflows/{workflow_id}/replay",
    response_model=ReplayResult,
    responses=RUNTIME_ERROR_RESPONSES,
    summary="Replay and verify deterministic checkpoint history",
)
def replay_runtime_workflow(
    workflow_id: str,
    engine: Annotated[
        DeterministicRuntimeEngine,
        Depends(get_runtime_engine),
    ],
) -> ReplayResult:
    """Reconstruct one workflow and verify its checkpoint chain."""

    try:
        return engine.replay(workflow_id)
    except CheckpointNotFoundError as error:
        raise_not_found(error)
    except ReplayIntegrityError as error:
        raise_runtime_api_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=RuntimeApiErrorCode.REPLAY_INTEGRITY_FAILURE,
            safe_message="Runtime checkpoint evidence failed integrity verification.",
            workflow_id=workflow_id,
            reason_code=error.reason_code,
        )
