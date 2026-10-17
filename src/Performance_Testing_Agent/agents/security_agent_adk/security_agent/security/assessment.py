from typing import Any

from security_agent.models.assessment import (
    AssessmentState,
    SecurityAssessment,
    SecurityEvidence,
)
from security_agent.models.response import SecurityControlResult, SecurityStatus
from security_agent.models.request import SecurityAssessmentRequest
from security_agent.security.scoring import calculate_control_result_score


_CONTROL_ALIASES = {
    "auth": "authentication",
    "authn": "authentication",
    "authentication_security": "authentication",
    "jwt_security": "jwt",
    "jwt_validation": "jwt",
    "authorization": "authorization_rbac",
    "rbac": "authorization_rbac",
    "role_based_access_control": "authorization_rbac",
    "oauth_security": "oauth",
    "multi_factor_authentication": "mfa",
    "endpoint_security": "api_security",
    "rate_limit": "rate_limiting",
    "rate_limiting_configuration": "rate_limiting",
    "sql_injection_prevention": "sql_injection",
    "xss_prevention": "xss",
    "csrf_protection": "csrf",
}


def normalize_control_name(control: str) -> str:
    """Normalize validator labels to stable contract control identifiers."""

    normalized = "_".join(control.casefold().replace("-", " ").split())
    return _CONTROL_ALIASES.get(normalized, normalized)


def add_evidence(
    state: AssessmentState,
    source: str,
    data: dict[str, Any],
) -> AssessmentState:
    """
    Add retrieved evidence to the assessment state.
    """

    state.evidence.append(
        SecurityEvidence(
            source=source,
            data=data,
        )
    )

    return state


def add_missing_evidence(
    state: AssessmentState,
    requirement: str,
) -> AssessmentState:
    """
    Record evidence required for an assessment but not available.
    """

    if requirement not in state.missing_evidence:
        state.missing_evidence.append(requirement)

    return state


def add_assessment(
    state: AssessmentState,
    control: str,
    result: dict[str, Any],
    evidence_sources: list[str] | None = None,
) -> AssessmentState:
    """
    Add a deterministic validator result to the assessment state.
    """

    state.assessments.append(
        SecurityAssessment(
            control=control,
            result=SecurityStatus(result["status"]),
            severity=(
                str(result.get("severity", "unknown")).casefold()
                if str(result.get("severity", "unknown")).casefold()
                in {"critical", "high", "medium", "low", "unknown"}
                else "unknown"
            ),
            security_score=result["security_score"],
            issues=result.get("issues", []),
            recommendations=result.get("recommendations", []),
            evidence_sources=evidence_sources or [],
        )
    )

    return state

def determine_overall_status(
    state: AssessmentState,
) -> SecurityStatus:
    """
    Determine the current overall assessment status.

    This does not calculate a security score.
    """

    if state.conflicts:
        return SecurityStatus.WARNING

    if state.missing_evidence:
        return SecurityStatus.WARNING

    if not state.assessments:
        return SecurityStatus.WARNING

    if any(
        assessment.result == SecurityStatus.FAIL
        for assessment in state.assessments
    ):
        return SecurityStatus.FAIL

    if any(
        assessment.result == SecurityStatus.WARNING
        for assessment in state.assessments
    ):
        return SecurityStatus.WARNING

    return SecurityStatus.PASS

def detect_conflicts(
    state: AssessmentState,
) -> list[str]:
    """
    Detect conflicting results for the same security control.
    """

    results_by_control: dict[str, set[SecurityStatus]] = {}

    for assessment in state.assessments:
        results_by_control.setdefault(
            assessment.control,
            set(),
        ).add(assessment.result)

    conflicts: list[str] = []

    for control, results in results_by_control.items():
        if len(results) > 1:
            conflicts.append(
                f"Conflicting assessment results detected for "
                f"security control '{control}'."
            )

    return conflicts


def update_conflicts(
    state: AssessmentState,
) -> AssessmentState:
    """
    Refresh conflict information in the assessment state.
    """

    state.conflicts = detect_conflicts(state)

    return state

from security_agent.models.response import SecurityResponse


def build_security_response(
    state: AssessmentState,
    *,
    evaluation: dict[str, Any] | None = None,
    live_result: dict[str, Any] | None = None,
) -> SecurityResponse:
    """
    Convert internal assessment state into the external
    SecurityResponse contract.

    Multi-control security scoring is intentionally not calculated
    here until a centralized scoring model is introduced.
    """

    request = state.request_context
    if request is not None and evaluation is not None:
        return _build_evaluated_response(request, evaluation, live_result)

    if request and request.profile_match_status != "matched":
        # Never allow evidence from a non-matching application profile to be
        # reported as findings about this job's target.
        state.assessments.clear()
        state.evidence.clear()
        add_missing_evidence(
            state,
            request.profile_match_reason
            or "No unique application security profile matches the trusted job target.",
        )
    requested_controls = request.requested_controls if request else []
    assessed_controls = list(
        dict.fromkeys(
            normalize_control_name(assessment.control)
            for assessment in state.assessments
        )
    )
    assessed_control_set = set(assessed_controls)
    not_assessed_controls = [
        control
        for control in requested_controls
        if normalize_control_name(control) not in assessed_control_set
    ]
    for control in not_assessed_controls:
        add_missing_evidence(
            state,
            f"Requested security control '{control}' was not assessed.",
        )
    if request and request.job_id and not request.target_origin:
        add_missing_evidence(
            state,
            "The current job has no valid trusted target origin for security assessment.",
        )

    status = determine_overall_status(state)

    issues: list[str] = []
    recommendations: list[str] = []

    for assessment in state.assessments:
        issues.extend(assessment.issues)
        recommendations.extend(assessment.recommendations)

    issues.extend(state.missing_evidence)
    issues.extend(state.conflicts)

    security_score, security_score_basis = calculate_control_result_score(
        [
            {
                "assessment_status": "assessed",
                "security_score": assessment.security_score,
            }
            for assessment in state.assessments
        ]
    )
    if state.missing_evidence and security_score != "N/A":
        security_score_basis += (
            f" {len(state.missing_evidence)} missing-evidence item(s) were excluded; "
            "the score is partial and does not cover the full requested assessment."
        )

    evidence_references = list(
        dict.fromkeys(
            [evidence.source for evidence in state.evidence]
            + [
                source
                for assessment in state.assessments
                for source in assessment.evidence_sources
            ]
        )
    )
    limitations = list(dict.fromkeys(state.missing_evidence + state.conflicts))
    if request and not request.live_testing_authorized:
        limitations.append(
            "Live security testing was not authorized or performed; this result is configuration-only."
        )

    normalized_requested = {
        normalize_control_name(control) for control in requested_controls
    }
    assessed_requested_count = len(normalized_requested & assessed_control_set)
    control_results = [
        SecurityControlResult(
            control=normalize_control_name(assessment.control),
            status=assessment.result,
            severity=assessment.severity,
            security_score=assessment.security_score,
            issues=assessment.issues,
            recommendations=assessment.recommendations,
            evidence_references=assessment.evidence_sources,
        )
        for assessment in state.assessments
    ]

    return SecurityResponse(
        status=status,
        security_score=security_score,
        security_score_basis=security_score_basis,
        issues=issues,
        recommendations=recommendations,
        job_id=request.job_id if request else None,
        test_case_id=request.test_case_id if request else None,
        test_case_name=request.test_case_name if request else None,
        target_origin=request.target_origin if request else None,
        configured_application=request.configured_application if request else None,
        profile_match_status=request.profile_match_status if request else "no_match",
        profile_id=request.profile_id if request else None,
        profile_version=request.profile_version if request else None,
        profile_match_reason=request.profile_match_reason if request else None,
        endpoint=request.endpoint if request else None,
        method=request.method if request else None,
        environment=request.environment if request else None,
        execution_mode=request.execution_mode if request else None,
        assessment_mode="configuration_only",
        live_testing_authorized=False,
        requested_controls=requested_controls,
        requested_controls_source=(
            request.requested_controls_source if request else "overall_security_default"
        ),
        assessed_controls=assessed_controls,
        not_assessed_controls=not_assessed_controls,
        coverage={
            "requested_count": len(requested_controls),
            "assessed_count": assessed_requested_count,
            "not_assessed_count": len(not_assessed_controls),
        },
        control_results=control_results,
        evidence_references=evidence_references,
        limitations=list(dict.fromkeys(limitations)),
    )


def _build_evaluated_response(
    request: SecurityAssessmentRequest,
    evaluation: dict[str, Any],
    live_result: dict[str, Any] | None = None,
) -> SecurityResponse:
    """Build the production response only from trusted deterministic evaluation."""
    control_results = evaluation.get("control_results", [])
    control_results = [result for result in control_results if isinstance(result, dict)]
    if "external_surface" in request.requested_controls and request.live_testing_requested:
        if (
            isinstance(live_result, dict)
            and live_result.get("status") == "completed"
            and live_result.get("authorized") is True
            and live_result.get("job_id") == request.job_id
        ):
            observed_headers = live_result.get("observed_security_headers")
            observed_headers = (
                {str(key).lower(): value for key, value in observed_headers.items()}
                if isinstance(observed_headers, dict)
                else {}
            )
            has_hsts = bool(observed_headers.get("strict-transport-security"))
            control_results.append(
                {
                    "control": "external_surface",
                    "assessment_status": "assessed",
                    "assessment_basis": "live_observation",
                    "status": "PASS" if has_hsts else "WARNING",
                    "security_score": "100%" if has_hsts else "0%",
                    "security_score_basis": (
                        "Single HEAD response observation: the HSTS header was "
                        + ("present." if has_hsts else "not present.")
                    ),
                    "severity": "low" if has_hsts else "medium",
                    "required_evidence": ["one authorized HEAD response"],
                    "available_evidence": {
                        "target_origin": live_result.get("target_origin"),
                        "endpoint": live_result.get("endpoint"),
                        "method": live_result.get("method"),
                        "response_status_code": live_result.get("response_status_code"),
                        "observed_security_headers": sorted(observed_headers),
                    },
                    "missing_evidence": [],
                    "issues": (
                        [] if has_hsts else [
                            "Strict-Transport-Security was not present in the observed response; this single response does not establish the full origin policy."
                        ]
                    ),
                    "recommendations": (
                        [] if has_hsts else [
                            "Review whether an HSTS policy is appropriate for this HTTPS API origin."
                        ]
                    ),
                    "evidence_references": [f"live-observation:{request.job_id}"],
                }
            )
        else:
            unavailable_reason = (
                live_result.get("reason") or live_result.get("error")
                if isinstance(live_result, dict)
                else None
            )
            control_results.append(
                {
                    "control": "external_surface",
                    "assessment_status": "not_assessed",
                    "assessment_basis": "live_observation",
                    "status": "WARNING",
                    "severity": "unknown",
                    "required_evidence": ["one authorized HEAD response"],
                    "available_evidence": {},
                    "missing_evidence": [
                        str(unavailable_reason or "No authorized external surface observation was completed.")
                    ],
                    "issues": [
                        "The external API surface observation did not complete, so no response-security findings are claimed."
                    ],
                    "recommendations": [],
                    "evidence_references": [],
                }
            )
    assessed = [
        result for result in control_results
        if result.get("assessment_status") == "assessed"
    ]
    not_assessed = [
        result for result in control_results
        if result.get("assessment_status") != "assessed"
    ]
    profile_needed_for_requested_controls = any(
        control != "external_surface" for control in request.requested_controls
    )
    if any(result.get("status") == "FAIL" for result in assessed):
        overall_status = SecurityStatus.FAIL
    elif not_assessed or any(result.get("status") != "PASS" for result in assessed):
        overall_status = SecurityStatus.WARNING
    elif not assessed:
        overall_status = SecurityStatus.WARNING
    else:
        overall_status = SecurityStatus.PASS
    if (
        evaluation.get("profile_match_reason")
        and profile_needed_for_requested_controls
        and overall_status == SecurityStatus.PASS
    ):
        # A passing response-header observation is a limited surface result,
        # not a full application-configuration assessment.
        overall_status = SecurityStatus.WARNING

    issues: list[str] = []
    recommendations: list[str] = []
    evidence_references: list[str] = []
    limitations: list[str] = []
    for result in control_results:
        issues.extend(result.get("issues", []))
        recommendations.extend(result.get("recommendations", []))
        evidence_references.extend(result.get("evidence_references", []))
        if result.get("assessment_status") != "assessed":
            missing = result.get("missing_evidence", [])
            limitations.extend(missing)
            if missing:
                issues.append(
                    f"{result.get('control', 'Security control')} was not assessed; "
                    f"missing evidence: {', '.join(missing)}."
                )
    scope_note = (
        "Scope limitation: configuration validator outcomes describe profile "
        "declarations; any live result is a separate single-request observation "
        "and does not prove control effectiveness."
    )
    # The current Analysis contract forwards only the legacy flat issue and
    # recommendation fields, so carry this scope statement through that
    # compatible field as well as the richer limitations field.
    issues.append(scope_note)
    live_status = "not_requested" if not request.live_testing_requested else "not_run"
    live_authorized = False
    live_mode = "configuration_only"
    safe_live_result: dict[str, Any] | None = None
    if live_result is not None:
        live_status_value = live_result.get("status")
        if live_status_value in {"blocked", "completed", "failed"}:
            live_status = live_status_value
            live_authorized = live_result.get("authorized") is True
            safe_live_result = {
                key: live_result.get(key)
                for key in (
                    "status", "authorized", "job_id", "test_case_id", "target_origin",
                    "endpoint", "method", "environment", "requests_sent",
                    "response_status_code", "elapsed_ms", "observed_security_headers",
                    "error", "reason", "limitations",
                )
                if key in live_result
            }
            if live_status in {"completed", "failed"} and live_authorized:
                live_mode = "configuration_and_live"
            if live_status == "blocked":
                issues.append(
                    "Requested live security check was blocked: "
                    + str(live_result.get("reason", "the trusted safety checks did not allow it."))
                )
            elif live_status == "failed":
                issues.append(
                    "Authorized live security observation failed: "
                    + str(live_result.get("error", "no response was received."))
                )
            elif live_status == "completed":
                issues.append(
                    "Live HEAD observation completed with HTTP status "
                    f"{live_result.get('response_status_code')}; response headers are observations only, not proof of control effectiveness."
                )
    # A versioned application profile is needed for configuration controls,
    # but not for a one-request external-surface observation scoped to the
    # trusted workload target. Avoid presenting a missing profile as a blocker
    # when the only requested control is external_surface.
    if evaluation.get("profile_match_reason") and profile_needed_for_requested_controls:
        limitations.append(evaluation["profile_match_reason"])
        issues.append(
            f"No matching application security profile: {evaluation['profile_match_reason']}"
        )
    if not request.requested_controls:
        no_controls_note = "No security control was selected from the objective; no control was assessed."
        limitations.append(no_controls_note)
        issues.append(no_controls_note)
    if not live_authorized:
        limitations.append(
            "No runtime security checks were performed; results describe configuration declarations only."
        )
    if request.live_testing_requested and live_status == "not_run":
        issues.append("Live security check was requested, but no live result was recorded.")
    if request.live_testing_requested and live_status in {"not_run", "blocked", "failed"}:
        limitations.append("The requested live security observation did not complete.")
        if overall_status == SecurityStatus.PASS:
            overall_status = SecurityStatus.WARNING

    normalized_results = [
        SecurityControlResult(
            control=result["control"],
            assessment_status=result.get("assessment_status", "not_assessed"),
            status=result.get("status", "WARNING"),
            assessment_basis=result.get(
                "assessment_basis", "configuration_declaration"
            ),
            severity=result.get("severity", "unknown"),
            security_score=str(result.get("security_score", "N/A")),
            security_score_basis=str(result.get("security_score_basis", "")),
            required_evidence=result.get("required_evidence", []),
            evidence_fields=list(result.get("available_evidence", {}).keys()),
            missing_evidence=result.get("missing_evidence", []),
            issues=result.get("issues", []),
            recommendations=result.get("recommendations", []),
            evidence_references=result.get("evidence_references", []),
        )
        for result in control_results
    ]
    security_score, security_score_basis = calculate_control_result_score(control_results)
    return SecurityResponse(
        status=overall_status,
        security_score=security_score,
        security_score_basis=security_score_basis,
        issues=list(dict.fromkeys(issues)),
        recommendations=list(dict.fromkeys(recommendations)),
        job_id=request.job_id,
        test_case_id=request.test_case_id,
        test_case_name=request.test_case_name,
        target_origin=request.target_origin,
        configured_application=request.configured_application,
        profile_match_status=evaluation.get("profile_match_status", request.profile_match_status),
        profile_id=evaluation.get("profile_id", request.profile_id),
        profile_version=evaluation.get("profile_version", request.profile_version),
        profile_match_reason=evaluation.get("profile_match_reason", request.profile_match_reason),
        endpoint=request.endpoint,
        method=request.method,
        environment=request.environment,
        execution_mode=request.execution_mode,
        assessment_mode=live_mode,
        live_testing_requested=request.live_testing_requested,
        live_testing_authorized=live_authorized,
        live_testing_status=live_status,
        live_test_result=safe_live_result,
        requested_controls=request.requested_controls,
        requested_controls_source=request.requested_controls_source,
        assessed_controls=[result["control"] for result in assessed],
        not_assessed_controls=[result["control"] for result in not_assessed],
        coverage={
            "requested_count": len(request.requested_controls),
            "assessed_count": len(assessed),
            "not_assessed_count": len(not_assessed),
        },
        required_evidence_by_control=request.required_evidence_by_control,
        control_results=normalized_results,
        evidence_references=list(dict.fromkeys(evidence_references)),
        limitations=list(dict.fromkeys(limitations)),
    )
