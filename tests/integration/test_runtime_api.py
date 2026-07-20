"""Integration tests for the local deterministic Phase 4 runtime API."""

from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from fastapi.testclient import TestClient

from incident_diagnostic_api.api.app import create_app
from incident_diagnostic_api.api.runtime_errors import (
    RuntimeApiError,
    RuntimeApiErrorCode,
)
from incident_diagnostic_api.api.runtime_models import (
    RuntimeRetryApiRequest,
    RuntimeStartRequest,
    RuntimeTransitionRequest,
)
from incident_diagnostic_api.core.config import Settings
from incident_diagnostic_api.runtime import (
    FailureClassification,
    ReplayResult,
    RuntimeRetryRequest,
    RuntimeStartResult,
    RuntimeState,
    RuntimeStateRecord,
    RuntimeStepResult,
    TransitionCommand,
)

NOW = datetime(2026, 7, 19, 18, 30, tzinfo=UTC)


def create_runtime_client() -> TestClient:
    """Create one isolated runtime-service client."""

    settings = Settings(
        environment="test",
        service_name="runtime",
        port=8001,
    )

    return TestClient(create_app(settings))


def start_request(
    *,
    workflow_id: str = "workflow-api-101",
) -> RuntimeStartRequest:
    """Return a valid genesis request."""

    return RuntimeStartRequest(
        record=RuntimeStateRecord(
            workflow_id=workflow_id,
            request_id=f"request-{workflow_id}",
            trace_id=f"trace-{workflow_id}",
            created_at=NOW,
            updated_at=NOW,
        ),
        event_id=f"event-{workflow_id}-0",
        timestamp=NOW,
    )


def post_start(
    client: TestClient,
    *,
    workflow_id: str = "workflow-api-101",
) -> RuntimeStartResult:
    """Create one workflow and return its validated result."""

    response = client.post(
        "/v1/runtime/workflows",
        json=start_request(workflow_id=workflow_id).model_dump(mode="json"),
    )

    assert response.status_code == 201
    return RuntimeStartResult.model_validate(response.json())


def transition_request(
    *,
    expected_state_version: int,
    command: TransitionCommand,
    event_number: int,
) -> RuntimeTransitionRequest:
    """Return one valid deterministic transition request."""

    return RuntimeTransitionRequest(
        expected_state_version=expected_state_version,
        command=command,
        event_id=f"event-api-{event_number}",
        timestamp=NOW + timedelta(seconds=event_number),
    )


def error_from_response(payload: dict[str, Any]) -> RuntimeApiError:
    """Validate the controlled error nested in FastAPI's detail field."""

    return RuntimeApiError.model_validate(payload["detail"])


def test_runtime_workflow_can_be_created_and_read() -> None:
    with create_runtime_client() as client:
        started = post_start(client)
        response = client.get("/v1/runtime/workflows/workflow-api-101")

    assert started.snapshot.state is RuntimeState.RECEIVED
    assert started.snapshot.state_version == 0
    assert started.checkpoint.sequence == 0
    assert response.status_code == 200

    current = RuntimeStateRecord.model_validate(response.json())

    assert current == started.snapshot


def test_runtime_transition_returns_state_checkpoint_and_trace() -> None:
    with create_runtime_client() as client:
        post_start(client)

        request = transition_request(
            expected_state_version=0,
            command=TransitionCommand.BEGIN_REQUEST_VALIDATION,
            event_number=1,
        )
        response = client.post(
            "/v1/runtime/workflows/workflow-api-101/transitions",
            json=request.model_dump(mode="json"),
            headers={"X-Correlation-ID": "runtime-transition-101"},
        )

    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == "runtime-transition-101"

    result = RuntimeStepResult.model_validate(response.json())

    assert result.command is TransitionCommand.BEGIN_REQUEST_VALIDATION
    assert result.snapshot.state is RuntimeState.REQUEST_VALIDATING
    assert result.snapshot.state_version == 1
    assert result.checkpoint.sequence == 1
    assert result.trace_event.event_name.value == "runtime_transition_applied"


def test_runtime_retry_requires_typed_transient_failure() -> None:
    with create_runtime_client() as client:
        post_start(client)

        transition = transition_request(
            expected_state_version=0,
            command=TransitionCommand.BEGIN_REQUEST_VALIDATION,
            event_number=1,
        )
        client.post(
            "/v1/runtime/workflows/workflow-api-101/transitions",
            json=transition.model_dump(mode="json"),
        )

        retry = RuntimeRetryApiRequest(
            expected_state_version=1,
            retry_request=RuntimeRetryRequest(
                failure_classification=FailureClassification.TRANSIENT,
                failure_reason_code="DEPENDENCY_FAILURE",
            ),
            event_id="event-api-retry-1",
            timestamp=NOW + timedelta(seconds=2),
        )
        response = client.post(
            "/v1/runtime/workflows/workflow-api-101/retries",
            json=retry.model_dump(mode="json"),
        )

    assert response.status_code == 200

    result = RuntimeStepResult.model_validate(response.json())

    assert result.snapshot.state is RuntimeState.REQUEST_VALIDATING
    assert result.snapshot.state_version == 2
    assert result.snapshot.retry_count == 1
    assert result.trace_event.event_name.value == "runtime_retry_scheduled"


def test_checkpoint_history_and_replay_are_available() -> None:
    with create_runtime_client() as client:
        post_start(client)

        transition = transition_request(
            expected_state_version=0,
            command=TransitionCommand.BEGIN_REQUEST_VALIDATION,
            event_number=1,
        )
        client.post(
            "/v1/runtime/workflows/workflow-api-101/transitions",
            json=transition.model_dump(mode="json"),
        )

        history_response = client.get("/v1/runtime/workflows/workflow-api-101/checkpoints")
        replay_response = client.get("/v1/runtime/workflows/workflow-api-101/replay")

    assert history_response.status_code == 200
    assert len(history_response.json()) == 2
    assert replay_response.status_code == 200

    replay = ReplayResult.model_validate(replay_response.json())

    assert replay.verified is True
    assert replay.checkpoint_count == 2
    assert replay.final_state is RuntimeState.REQUEST_VALIDATING
    assert replay.final_state_version == 1


def test_missing_workflow_returns_controlled_404() -> None:
    with create_runtime_client() as client:
        response = client.get("/v1/runtime/workflows/missing-workflow")

    assert response.status_code == 404

    error = error_from_response(response.json())

    assert error.error_code is RuntimeApiErrorCode.WORKFLOW_NOT_FOUND
    assert error.workflow_id == "missing-workflow"
    assert error.retryable is False


def test_stale_state_version_returns_controlled_409() -> None:
    with create_runtime_client() as client:
        post_start(client)

        first = transition_request(
            expected_state_version=0,
            command=TransitionCommand.BEGIN_REQUEST_VALIDATION,
            event_number=1,
        )
        client.post(
            "/v1/runtime/workflows/workflow-api-101/transitions",
            json=first.model_dump(mode="json"),
        )

        stale = transition_request(
            expected_state_version=0,
            command=TransitionCommand.REQUEST_VALIDATED,
            event_number=2,
        )
        response = client.post(
            "/v1/runtime/workflows/workflow-api-101/transitions",
            json=stale.model_dump(mode="json"),
        )

    assert response.status_code == 409

    error = error_from_response(response.json())

    assert error.error_code is RuntimeApiErrorCode.VERSION_CONFLICT
    assert error.workflow_id == "workflow-api-101"
    assert error.retryable is False


def test_invalid_transition_returns_controlled_409_without_mutation() -> None:
    with create_runtime_client() as client:
        post_start(client)

        invalid = transition_request(
            expected_state_version=0,
            command=TransitionCommand.RESPONSE_VALIDATED,
            event_number=1,
        )
        response = client.post(
            "/v1/runtime/workflows/workflow-api-101/transitions",
            json=invalid.model_dump(mode="json"),
        )
        current_response = client.get("/v1/runtime/workflows/workflow-api-101")

    assert response.status_code == 409

    error = error_from_response(response.json())
    current = RuntimeStateRecord.model_validate(current_response.json())

    assert error.error_code is RuntimeApiErrorCode.INVALID_TRANSITION
    assert error.state is RuntimeState.RECEIVED
    assert current.state is RuntimeState.RECEIVED
    assert current.state_version == 0


def test_duplicate_workflow_returns_controlled_version_conflict() -> None:
    with create_runtime_client() as client:
        post_start(client)
        response = client.post(
            "/v1/runtime/workflows",
            json=start_request().model_dump(mode="json"),
        )

    assert response.status_code == 409

    error = error_from_response(response.json())

    assert error.error_code is RuntimeApiErrorCode.VERSION_CONFLICT
    assert error.workflow_id == "workflow-api-101"


def test_gateway_and_evidence_do_not_expose_runtime_routes() -> None:
    isolated_services: tuple[
        tuple[Literal["gateway", "evidence"], int],
        ...,
    ] = (
        ("gateway", 8000),
        ("evidence", 8002),
    )

    for service_name, port in isolated_services:
        settings = Settings(
            environment="test",
            service_name=service_name,
            port=port,
        )

        with TestClient(create_app(settings)) as client:
            response = client.post(
                "/v1/runtime/workflows",
                json=start_request().model_dump(mode="json"),
            )

        assert response.status_code == 404
