"""Bounded enumerations shared by the Phase 3 executable contracts."""

from enum import StrEnum


class Environment(StrEnum):
    """Supported incident environments."""

    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class RequestType(StrEnum):
    """Operations accepted by the initial slice."""

    DIAGNOSTIC_RECOMMENDATION = "diagnostic_recommendation"


class AuthenticationMethod(StrEnum):
    """Approved logical enterprise authentication methods."""

    OIDC = "oidc"
    SAML = "saml"
    MTLS = "mtls"


class AssuranceLevel(StrEnum):
    """Logical authentication assurance classifications."""

    STANDARD = "standard"
    ELEVATED = "elevated"
    HIGH = "high"


class PolicyOperation(StrEnum):
    """Operations understood by the initial deterministic policy boundary."""

    VALIDATE_DIAGNOSTIC_REQUEST = "validate_diagnostic_request"
    RETRIEVE_RUNBOOK_EVIDENCE = "retrieve_runbook_evidence"
    GENERATE_DIAGNOSTIC_RECOMMENDATION = "generate_diagnostic_recommendation"
    RETURN_DIAGNOSTIC_RESPONSE = "return_diagnostic_response"


class PolicyOutcome(StrEnum):
    """Deterministic policy results."""

    ALLOW = "allow"
    DENY = "deny"
    CONSTRAIN = "constrain"


class SourceType(StrEnum):
    """Evidence sources permitted by the initial logical contract."""

    RUNBOOK = "runbook"
    SERVICE_METADATA = "service_metadata"


class FreshnessStatus(StrEnum):
    """Freshness classification supplied with evidence."""

    CURRENT = "current"
    STALE = "stale"
    UNKNOWN = "unknown"


class SensitivityClassification(StrEnum):
    """Initial bounded information classifications."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ResponseStatus(StrEnum):
    """Possible top-level diagnostic outcomes."""

    RECOMMENDATION = "recommendation"
    ABSTENTION = "abstention"
    ERROR = "error"


class ConfidenceClassification(StrEnum):
    """Bounded confidence language for recommendations."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class SupportType(StrEnum):
    """Relationship between a claim and cited evidence."""

    DIRECT = "direct"
    CORROBORATING = "corroborating"
    CONFLICTING = "conflicting"


class ActionClass(StrEnum):
    """Authority classification for recommended next steps."""

    HUMAN_REVIEW_REQUIRED = "human_review_required"


class ExecutionStatus(StrEnum):
    """Execution posture for every initial-slice recommendation."""

    NOT_EXECUTED = "not_executed"


class ErrorCategory(StrEnum):
    """Controlled error categories."""

    VALIDATION = "validation"
    IDENTITY = "identity"
    AUTHORIZATION = "authorization"
    EVIDENCE = "evidence"
    DEPENDENCY = "dependency"
    RESPONSE = "response"
    INTERNAL = "internal"


class ErrorCode(StrEnum):
    """Controlled non-sensitive error codes."""

    INVALID_REQUEST = "INVALID_REQUEST"
    UNSUPPORTED_VERSION = "UNSUPPORTED_VERSION"
    IDENTITY_REQUIRED = "IDENTITY_REQUIRED"
    IDENTITY_EXPIRED = "IDENTITY_EXPIRED"
    ACCESS_DENIED = "ACCESS_DENIED"
    SERVICE_UNSUPPORTED = "SERVICE_UNSUPPORTED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    EVIDENCE_INSUFFICIENT = "EVIDENCE_INSUFFICIENT"
    EVIDENCE_CONFLICT = "EVIDENCE_CONFLICT"
    POLICY_UNAVAILABLE = "POLICY_UNAVAILABLE"
    RESPONSE_INVALID = "RESPONSE_INVALID"
    DEPENDENCY_FAILURE = "DEPENDENCY_FAILURE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class LifecycleStage(StrEnum):
    """Traceable stages in the bounded diagnostic lifecycle."""

    ADMISSION = "admission"
    IDENTITY = "identity"
    POLICY = "policy"
    RETRIEVAL = "retrieval"
    EVIDENCE_ASSESSMENT = "evidence_assessment"
    GENERATION = "generation"
    RESPONSE_VALIDATION = "response_validation"
    RESPONSE_DELIVERY = "response_delivery"
    OBSERVABILITY = "observability"


class TraceOutcome(StrEnum):
    """Possible outcomes for a lifecycle event."""

    STARTED = "started"
    SUCCEEDED = "succeeded"
    DENIED = "denied"
    ABSTAINED = "abstained"
    FAILED = "failed"


class TraceEventName(StrEnum):
    """Allowlisted lifecycle event names."""

    REQUEST_RECEIVED = "request_received"
    REQUEST_VALIDATED = "request_validated"
    IDENTITY_VALIDATED = "identity_validated"
    POLICY_EVALUATED = "policy_evaluated"
    RETRIEVAL_STARTED = "retrieval_started"
    RETRIEVAL_COMPLETED = "retrieval_completed"
    EVIDENCE_ASSESSED = "evidence_assessed"
    GENERATION_STARTED = "generation_started"
    GENERATION_COMPLETED = "generation_completed"
    RESPONSE_VALIDATED = "response_validated"
    RESPONSE_RETURNED = "response_returned"
    REQUEST_DENIED = "request_denied"
    REQUEST_ABSTAINED = "request_abstained"
    REQUEST_FAILED = "request_failed"
    RUNTIME_TRANSITION_APPLIED = "runtime_transition_applied"
    RUNTIME_RETRY_SCHEDULED = "runtime_retry_scheduled"
    RUNTIME_STOP_ENFORCED = "runtime_stop_enforced"
