"""Structured, job-scoped context for Security Agent assessments."""

from typing import Any, Literal
import re
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field
from security_agent.passive.config import passive_assessment_enabled
from security_agent.security.profiles import select_profile


SUPPORTED_SECURITY_CONTROLS = (
    "authentication",
    "jwt",
    "authorization_rbac",
    "oauth",
    "mfa",
    "api_security",
    "rate_limiting",
    "sql_injection",
    "xss",
    "csrf",
    "external_surface",
)

_CONTROL_TERMS = {
    "authentication": ("authentication", "authn"),
    "jwt": ("jwt", "json web token"),
    "authorization_rbac": ("authorization", "rbac", "role-based access"),
    "oauth": ("oauth",),
    "mfa": ("mfa", "multi-factor", "multifactor"),
    "api_security": ("api security", "endpoint security"),
    "rate_limiting": ("rate limit", "rate limiting", "throttling"),
    "sql_injection": ("sql injection", "sql security"),
    "xss": ("xss", "cross-site scripting"),
    "csrf": ("csrf", "cross-site request forgery"),
}
_LIVE_SECURITY_REQUEST = re.compile(
    r"\b(?:live|active|runtime)\s+security\s+(?:check|test|assessment|probe)s?\b"
    r"|\bsecurity\s+(?:live|active|runtime)\s+(?:check|test|assessment|probe)s?\b"
    r"|\b(?:authorize|authorized|perform|run|execute|conduct)\b"
    r"[^.!?\n]{0,100}\b(?:live|active|runtime)\b"
    r"[^.!?\n]{0,60}\bsecurity\b",
    re.IGNORECASE,
)
_CONFIGURATION_ONLY_REQUEST = re.compile(
    r"\b(?:configuration[- ]only|config[- ]only|without\s+(?:any\s+)?live\s+"
    r"(?:checks?|probes?|testing)|do\s+not\s+(?:send|run|perform)\s+(?:any\s+)?"
    r"(?:live\s+)?(?:checks?|probes?|testing)|no\s+live\s+(?:checks?|probes?|testing))\b",
    re.IGNORECASE,
)
_SECURITY_ASSESSMENT_REQUEST = re.compile(
    r"\b(?:security\s+(?:assessment|audit|review|check|posture)|"
    r"assess\s+(?:the\s+)?security|check\s+(?:the\s+)?security|"
    r"evaluate\s+(?:the\s+)?security|review\s+(?:the\s+)?security)\b",
    re.IGNORECASE,
)


def is_explicit_live_security_request(objective: str) -> bool:
    """Use safe live observations for security requests unless explicitly opted out.

    This preserves a clear configuration-only opt-out while allowing ordinary
    requests to assess an API to collect bounded, allowlisted surface evidence.
    """
    if _CONFIGURATION_ONLY_REQUEST.search(objective):
        return False
    return bool(
        _LIVE_SECURITY_REQUEST.search(objective)
        or _SECURITY_ASSESSMENT_REQUEST.search(objective)
    )

CONTROL_REQUIRED_EVIDENCE = {
    "authentication": ["authentication.enabled", "authentication.type"],
    "jwt": [
        "authentication.enabled", "authentication.type", "authentication.jwt.signature_validation",
        "authentication.jwt.expiration_validation", "authentication.jwt.issuer_validation",
        "authentication.jwt.audience_validation", "authentication.jwt.algorithm_validation",
        "authentication.jwt.allowed_algorithms",
    ],
    "authorization_rbac": [
        "authorization.enabled", "authorization.type", "authorization.roles",
        "authorization.role_permission_validation", "api.endpoint.authorization_required",
        "api.endpoint.allowed_roles",
    ],
    "oauth": [
        "oauth.enabled", "oauth.provider", "oauth.flow", "oauth.token_endpoint_auth_method",
        "oauth.redirect_uri_validation", "oauth.state_parameter_validation",
        "oauth.scope_validation", "oauth.pkce_enabled",
    ],
    "mfa": [
        "mfa.enabled", "mfa.methods", "mfa.enforcement_enabled", "mfa.required_for_admin",
        "mfa.recovery_protection", "mfa.bypass_protection",
    ],
    "api_security": [
        "api.endpoint.path", "api.endpoint.method", "api.endpoint.authentication_required",
        "api.endpoint.authorization_required",
    ],
    "rate_limiting": [
        "api.endpoint.path", "api.endpoint.method", "api.endpoint.rate_limit.enabled",
        "api.endpoint.rate_limit.requests_per_minute",
    ],
    "sql_injection": ["sql_security.parameterized_queries", "sql_security.prepared_statements"],
    "xss": ["xss_security.input_sanitization", "xss_security.output_encoding"],
    "csrf": ["csrf_security.protection_enabled", "csrf_security.csrf_token_validation"],
    "external_surface": ["authorized live surface observation"],
}


def _requested_controls(objective: str) -> tuple[list[str], str]:
    normalized = objective.casefold()
    controls = [
        control
        for control, terms in _CONTROL_TERMS.items()
        if any(term in normalized for term in terms)
    ]
    if controls:
        return controls, "explicit_request"
    broad_security_request = any(
        phrase in normalized
        for phrase in (
            "security assessment",
            "overall security",
            "comprehensive security",
            "full security",
            "security posture",
            "security review",
            "security audit",
            "check security",
        )
    )
    if broad_security_request:
        return list(SUPPORTED_SECURITY_CONTROLS), "overall_security_default"
    return [], "no_control_selected"


class SecurityAssessmentRequest(BaseModel):
    """Inputs Security may rely on for a performance-job assessment."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    schema_version: Literal["1.0"] = "1.0"
    objective: str = Field(min_length=1)
    job_id: str | None = None
    test_case_id: str | None = None
    test_case_name: str | None = None
    execution_mode: Literal["REAL", "SIMULATED"] | None = None
    target_origin: str | None = None
    configured_application: str | None = None
    profile_match_status: Literal["matched", "no_match", "ambiguous"] = "no_match"
    profile_id: str | None = None
    profile_version: str | None = None
    profile_match_reason: str | None = None
    endpoint: str | None = None
    method: str | None = None
    environment: str | None = None
    requested_controls: list[str] = Field(default_factory=list)
    required_evidence_by_control: dict[str, list[str]] = Field(default_factory=dict)
    requested_controls_source: Literal[
        "explicit_request", "overall_security_default", "no_control_selected"
    ] = "overall_security_default"
    assessment_mode: Literal["configuration_only", "configuration_and_live"] = "configuration_only"
    live_testing_requested: bool = False
    live_testing_authorized: bool = False
    # True when the passive external-surface assessment applies: always for the
    # automatic assessment, and for an explicit request that did not opt out.
    passive_assessment_requested: bool = False


class SecurityRequest(BaseModel):
    """Backward-compatible request shape used by the standalone agent API."""

    query: str = Field(
        ...,
        min_length=1,
        description="Security assessment request provided to the Security Agent.",
    )


def build_security_assessment_request(
    objective: str,
    session_state: dict[str, Any],
    *,
    auto_passive: bool = False,
) -> SecurityAssessmentRequest:
    """Build the contract from the objective and trusted execution state.

    Target identity comes only from the workload profile in session state;
    prose in the objective cannot replace the active job's target.
    A general security request may request the bounded passive external-surface
    assessment (or, when that is switched off, one bounded HEAD observation
    that is still subject to the live-test kill switch and exact job scope).
    ``auto_passive`` marks the automatic assessment of a REAL run: it assesses
    only the external surface, whatever the objective says.
    """

    profile = session_state.get("workload_profile")
    profile = profile if isinstance(profile, dict) else {}
    try:
        profile_selection = select_profile(session_state)
    except (OSError, ValueError) as exc:
        profile_selection = {
            "status": "no_match",
            "reason": f"The versioned application profile registry could not be used: {exc}",
        }
    target_origin = None
    target_url = profile.get("target_url")
    if isinstance(target_url, str) and target_url.strip():
        try:
            parsed = urlsplit(target_url.strip())
            if parsed.scheme in {"http", "https"} and parsed.hostname:
                hostname = parsed.hostname.lower()
                authority = f"[{hostname}]" if ":" in hostname else hostname
                if parsed.port is not None:
                    authority = f"{authority}:{parsed.port}"
                target_origin = f"{parsed.scheme.lower()}://{authority}"
        except ValueError:
            target_origin = None

    execution_mode = session_state.get("execution_mode")
    if execution_mode not in {"REAL", "SIMULATED"}:
        execution_mode = None

    controls, controls_source = _requested_controls(objective)
    if profile_selection["status"] != "matched" and controls_source == "overall_security_default":
        # Without an owned configuration profile, assess only the observable
        # external surface instead of claiming scope over internal controls.
        controls = ["external_surface"]
    live_requested = is_explicit_live_security_request(objective)
    passive_requested = False
    if auto_passive:
        # The automatic assessment never widens to configuration controls; only
        # an explicit security request does that.
        controls, controls_source = ["external_surface"], "overall_security_default"
        passive_requested = passive_assessment_enabled()
    elif live_requested and passive_assessment_enabled():
        passive_requested = True
    # A passive observation is a live observation of the target.
    live_requested = live_requested or passive_requested
    if live_requested and "external_surface" not in controls:
        controls.append("external_surface")
    test_case_id = session_state.get("test_case_id")
    test_case_name = session_state.get("test_case_name")
    job_id = session_state.get("job_id")

    configured_application = (
        profile.get("application")
        or profile.get("application_name")
        or session_state.get("application_name")
        or session_state.get("application")
    )
    if not isinstance(configured_application, str):
        # This is a target identifier derived from trusted job state, not an
        # assertion of ownership or access to the provider's internals.
        configured_application = (
            urlsplit(target_origin).hostname if target_origin is not None else None
        )

    return SecurityAssessmentRequest(
        objective=objective.strip() or "Security assessment",
        job_id=job_id if isinstance(job_id, str) and job_id else None,
        test_case_id=(
            test_case_id if isinstance(test_case_id, str) and test_case_id else None
        ),
        test_case_name=(
            test_case_name
            if isinstance(test_case_name, str) and test_case_name
            else None
        ),
        execution_mode=execution_mode,
        target_origin=target_origin,
        configured_application=configured_application,
        profile_match_status=profile_selection["status"],
        profile_id=profile_selection.get("profile_id"),
        profile_version=profile_selection.get("profile_version"),
        profile_match_reason=profile_selection.get("reason"),
        endpoint=(profile.get("endpoint") if isinstance(profile.get("endpoint"), str) else None),
        method=(profile.get("method") if isinstance(profile.get("method"), str) else None),
        environment=(
            profile.get("environment")
            if isinstance(profile.get("environment"), str)
            else None
        ),
        requested_controls=controls,
        required_evidence_by_control={
            control: CONTROL_REQUIRED_EVIDENCE[control] for control in controls
        },
        requested_controls_source=controls_source,
        assessment_mode="configuration_and_live" if live_requested else "configuration_only",
        live_testing_requested=live_requested,
        live_testing_authorized=False,
        passive_assessment_requested=passive_requested,
    )
