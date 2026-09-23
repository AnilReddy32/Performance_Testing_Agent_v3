from typing import Any

from security_agent.models.assessment import (
    AssessmentState,
    SecurityAssessment,
    SecurityEvidence,
)
from security_agent.models.response import SecurityStatus
from security_agent.security.scoring import calculate_security_score


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
) -> SecurityResponse:
    """
    Convert internal assessment state into the external
    SecurityResponse contract.

    Multi-control security scoring is intentionally not calculated
    here until a centralized scoring model is introduced.
    """

    status = determine_overall_status(state)

    issues: list[str] = []
    recommendations: list[str] = []

    for assessment in state.assessments:
        issues.extend(assessment.issues)
        recommendations.extend(assessment.recommendations)

    issues.extend(state.missing_evidence)
    issues.extend(state.conflicts)

    security_score = calculate_security_score(state.assessments)

    return SecurityResponse(
        status=status,
        security_score=security_score,
        issues=issues,
        recommendations=recommendations,
    )