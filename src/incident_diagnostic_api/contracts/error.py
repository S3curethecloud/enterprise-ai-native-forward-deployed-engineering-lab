"""CT-06 executable controlled-error contract."""

from typing import Self

from pydantic import model_validator

from incident_diagnostic_api.contracts.common import (
    OpaqueIdentifier,
    ShortText,
    Timestamp,
    VersionedContract,
)
from incident_diagnostic_api.contracts.enums import (
    ErrorCategory,
    ErrorCode,
    LifecycleStage,
)
from incident_diagnostic_api.contracts.response import PolicyOutcomeReference

EXPECTED_CATEGORIES: dict[ErrorCode, ErrorCategory] = {
    ErrorCode.INVALID_REQUEST: ErrorCategory.VALIDATION,
    ErrorCode.UNSUPPORTED_VERSION: ErrorCategory.VALIDATION,
    ErrorCode.IDENTITY_REQUIRED: ErrorCategory.IDENTITY,
    ErrorCode.IDENTITY_EXPIRED: ErrorCategory.IDENTITY,
    ErrorCode.ACCESS_DENIED: ErrorCategory.AUTHORIZATION,
    ErrorCode.SERVICE_UNSUPPORTED: ErrorCategory.VALIDATION,
    ErrorCode.SOURCE_UNAVAILABLE: ErrorCategory.EVIDENCE,
    ErrorCode.EVIDENCE_INSUFFICIENT: ErrorCategory.EVIDENCE,
    ErrorCode.EVIDENCE_CONFLICT: ErrorCategory.EVIDENCE,
    ErrorCode.POLICY_UNAVAILABLE: ErrorCategory.DEPENDENCY,
    ErrorCode.RESPONSE_INVALID: ErrorCategory.RESPONSE,
    ErrorCode.DEPENDENCY_FAILURE: ErrorCategory.DEPENDENCY,
    ErrorCode.INTERNAL_ERROR: ErrorCategory.INTERNAL,
}

EXPECTED_RETRYABILITY: dict[ErrorCode, bool] = {
    ErrorCode.INVALID_REQUEST: False,
    ErrorCode.UNSUPPORTED_VERSION: False,
    ErrorCode.IDENTITY_REQUIRED: False,
    ErrorCode.IDENTITY_EXPIRED: True,
    ErrorCode.ACCESS_DENIED: False,
    ErrorCode.SERVICE_UNSUPPORTED: False,
    ErrorCode.SOURCE_UNAVAILABLE: True,
    ErrorCode.EVIDENCE_INSUFFICIENT: False,
    ErrorCode.EVIDENCE_CONFLICT: False,
    ErrorCode.POLICY_UNAVAILABLE: True,
    ErrorCode.RESPONSE_INVALID: True,
    ErrorCode.DEPENDENCY_FAILURE: True,
}


class ControlledError(VersionedContract):
    """Bounded non-sensitive error returned by a trusted component."""

    request_id: OpaqueIdentifier | None = None
    trace_id: OpaqueIdentifier
    error_code: ErrorCode
    error_category: ErrorCategory
    safe_message: ShortText
    retryable: bool
    failed_stage: LifecycleStage
    policy_outcome: PolicyOutcomeReference | None = None
    occurred_at: Timestamp

    @model_validator(mode="after")
    def validate_error_invariants(self) -> Self:
        """Enforce deterministic category and retry behavior."""

        expected_category = EXPECTED_CATEGORIES[self.error_code]
        if self.error_category is not expected_category:
            raise ValueError("error category does not match the controlled error code")

        expected_retryability = EXPECTED_RETRYABILITY.get(self.error_code)
        if expected_retryability is not None and self.retryable is not expected_retryability:
            raise ValueError("retryable value does not match the controlled error code")

        if self.error_code is ErrorCode.ACCESS_DENIED and self.policy_outcome is None:
            raise ValueError("access denial requires a policy outcome reference")

        return self
