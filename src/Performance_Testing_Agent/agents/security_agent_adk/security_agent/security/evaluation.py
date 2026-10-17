"""Deterministic, profile-scoped configuration control evaluation."""

from typing import Any

from security_agent.models.request import (
    CONTROL_REQUIRED_EVIDENCE,
    SecurityAssessmentRequest,
)
from security_agent.security.profiles import find_profile_endpoint
from security_agent.security.authentication import validate_authentication
from security_agent.security.jwt import validate_jwt
from security_agent.security.authorization import validate_rbac
from security_agent.security.oauth import validate_oauth
from security_agent.security.mfa import validate_mfa
from security_agent.security.api import validate_api_security
from security_agent.security.rate_limit import validate_rate_limiting
from security_agent.security.sql_injection import validate_sql_injection
from security_agent.security.xss import validate_xss
from security_agent.security.csrf import validate_csrf


def _value_at(data: dict[str, Any], dotted_path: str) -> Any:
    current: Any = data
    for component in dotted_path.split("."):
        if not isinstance(current, dict) or component not in current:
            return None
        current = current[component]
    return current


def _required_value(
    profile: dict[str, Any], endpoint_config: dict[str, Any] | None, path: str
) -> Any:
    if path.startswith("api.endpoint."):
        if endpoint_config is None:
            return None
        return _value_at(endpoint_config, path.removeprefix("api.endpoint."))
    return _value_at(profile, path)


def _run_validator(
    control: str,
    profile: dict[str, Any],
    endpoint_config: dict[str, Any] | None,
) -> dict[str, Any]:
    if control == "authentication":
        return validate_authentication(profile.get("authentication"))
    if control == "jwt":
        return validate_jwt(profile.get("authentication"))
    if control == "authorization_rbac":
        endpoints = [endpoint_config] if endpoint_config is not None else None
        return validate_rbac(profile.get("authorization"), endpoints)
    if control == "oauth":
        return validate_oauth(profile.get("oauth"))
    if control == "mfa":
        return validate_mfa(profile.get("mfa"))
    if control == "api_security":
        endpoints = [endpoint_config] if endpoint_config is not None else []
        return validate_api_security(endpoints)
    if control == "rate_limiting":
        endpoints = [endpoint_config] if endpoint_config is not None else []
        return validate_rate_limiting(endpoints)
    if control == "sql_injection":
        return validate_sql_injection(profile.get("sql_security"))
    if control == "xss":
        return validate_xss(profile.get("xss_security"))
    if control == "csrf":
        return validate_csrf(profile.get("csrf_security"))
    return {
        "status": "WARNING",
        "issues": [f"No deterministic validator is available for '{control}'."],
        "recommendations": [],
    }


def evaluate_configured_controls(
    request: SecurityAssessmentRequest,
    profile_selection: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate requested controls only against the uniquely matched profile."""
    profile = profile_selection.get("data") if profile_selection.get("status") == "matched" else None
    if not isinstance(profile, dict):
        profile = {}

    endpoint_config = find_profile_endpoint(profile, request.endpoint, request.method)
    results: list[dict[str, Any]] = []
    missing_by_control: dict[str, list[str]] = {}

    for control in request.requested_controls:
        if control == "external_surface" and request.live_testing_requested:
            # This control is populated only from the bounded live observation
            # at finalization, never from profile declarations.
            continue
        required = CONTROL_REQUIRED_EVIDENCE.get(control, [])
        missing = [
            name
            for name in required
            if _required_value(profile, endpoint_config, name) is None
        ]
        if profile_selection.get("status") != "matched":
            missing = list(required)
        elif control in {"authorization_rbac", "api_security", "rate_limiting"} and endpoint_config is None:
            missing = list(dict.fromkeys(missing + ["api.endpoint matching the trusted endpoint and method"]))

        evidence = {
            name: _required_value(profile, endpoint_config, name)
            for name in required
            if _required_value(profile, endpoint_config, name) is not None
        }
        if profile_selection.get("status") == "matched":
            evidence_reference = (
                f"profile:{profile_selection.get('profile_id')}@"
                f"{profile_selection.get('profile_version')}"
            )
        else:
            evidence_reference = None

        if missing:
            missing_by_control[control] = missing
            results.append(
                {
                    "control": control,
                    "assessment_status": "not_assessed",
                    "status": "WARNING",
                    "assessment_basis": "configuration_declaration",
                    "security_score": "N/A",
                    "severity": "unknown",
                    "required_evidence": required,
                    "available_evidence": evidence,
                    "evidence_references": [evidence_reference] if evidence_reference else [],
                    "missing_evidence": missing,
                    "issues": ["Required configuration evidence is unavailable; this control was not assessed."],
                    "recommendations": [
                        "Provide the listed configuration evidence for the selected application profile."
                    ],
                }
            )
            continue

        validator_result = _run_validator(control, profile, endpoint_config)
        results.append(
            {
                "control": control,
                "assessment_status": "assessed",
                "status": str(validator_result.get("status", "WARNING")),
                "assessment_basis": "configuration_declaration",
                "security_score": str(validator_result.get("security_score", "N/A")),
                "security_score_basis": (
                    f"Validator-provided {control} configuration score."
                    if validator_result.get("security_score", "N/A") != "N/A"
                    else "This validator did not produce a numeric score."
                ),
                "severity": validator_result.get("severity", "unknown"),
                "required_evidence": required,
                "available_evidence": evidence,
                "evidence_references": [evidence_reference] if evidence_reference else [],
                "missing_evidence": [],
                "issues": [
                    f"Profile configuration declares: {issue}"
                    for issue in validator_result.get("issues", [])
                ],
                "recommendations": validator_result.get("recommendations", []),
            }
        )

    return {
        "profile_match_status": profile_selection.get("status", "no_match"),
        "profile_id": profile_selection.get("profile_id"),
        "profile_version": profile_selection.get("profile_version"),
        "profile_match_reason": profile_selection.get("reason"),
        "requested_controls": request.requested_controls,
        "required_evidence_by_control": request.required_evidence_by_control,
        "control_results": results,
        "missing_evidence_by_control": missing_by_control,
        "assessment_mode": "configuration_only",
        "live_testing_authorized": False,
    }
