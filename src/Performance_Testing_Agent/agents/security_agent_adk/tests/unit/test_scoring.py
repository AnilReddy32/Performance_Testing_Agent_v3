from security_agent.models.assessment import SecurityAssessment
from security_agent.models.response import SecurityStatus
from security_agent.security.scoring import (
    calculate_control_result_score,
    calculate_security_score,
)


def make_assessment(
    control: str,
    result: SecurityStatus,
    score: str,
) -> SecurityAssessment:
    return SecurityAssessment(
        control=control,
        result=result,
        security_score=score,
    )


def test_no_assessments_returns_na():
    assert calculate_security_score([]) == "N/A"


def test_single_pass_returns_100():
    assessments = [
        make_assessment(
            "JWT",
            SecurityStatus.PASS,
            "100%",
        )
    ]

    assert calculate_security_score(assessments) == "100%"


def test_single_fail_returns_0():
    assessments = [
        make_assessment(
            "JWT",
            SecurityStatus.FAIL,
            "0%",
        )
    ]

    assert calculate_security_score(assessments) == "0%"


def test_multiple_pass_assessments_return_100():
    assessments = [
        make_assessment("JWT", SecurityStatus.PASS, "100%"),
        make_assessment("RBAC", SecurityStatus.PASS, "100%"),
        make_assessment("MFA", SecurityStatus.PASS, "100%"),
    ]

    assert calculate_security_score(assessments) == "100%"


def test_multiple_assessments_are_averaged():
    assessments = [
        make_assessment("JWT", SecurityStatus.PASS, "100%"),
        make_assessment("RBAC", SecurityStatus.FAIL, "0%"),
        make_assessment("MFA", SecurityStatus.PASS, "100%"),
    ]

    assert calculate_security_score(assessments) == "66.67%"


def test_warning_with_numeric_score_is_included():
    assessments = [
        make_assessment("JWT", SecurityStatus.PASS, "100%"),
        make_assessment("OAuth", SecurityStatus.WARNING, "50%"),
    ]

    assert calculate_security_score(assessments) == "75%"


def test_na_score_is_excluded_when_another_numeric_score_exists():
    assessments = [
        make_assessment("JWT", SecurityStatus.PASS, "100%"),
        make_assessment("OAuth", SecurityStatus.PASS, "N/A"),
    ]

    assert calculate_security_score(assessments) == "100%"


def test_invalid_score_format_returns_na():
    assessments = [
        make_assessment("JWT", SecurityStatus.PASS, "unknown"),
    ]

    assert calculate_security_score(assessments) == "N/A"


def test_score_outside_valid_range_returns_na():
    assessments = [
        make_assessment("JWT", SecurityStatus.PASS, "120%"),
    ]

    assert calculate_security_score(assessments) == "N/A"


def test_control_result_score_includes_warning_and_excludes_unassessed():
    score, basis = calculate_control_result_score([
        {
            "control": "rate_limiting",
            "assessment_status": "assessed",
            "status": "WARNING",
            "security_score": "60%",
            "security_score_basis": "Validator-provided configuration score.",
        },
        {
            "control": "oauth",
            "assessment_status": "not_assessed",
            "status": "WARNING",
            "security_score": "N/A",
        },
    ])

    assert score == "60%"
    assert "overall status is reported separately" in basis


def test_control_result_score_is_na_without_numeric_assessed_results():
    score, basis = calculate_control_result_score([
        {
            "control": "oauth",
            "assessment_status": "not_assessed",
            "security_score": "N/A",
        }
    ])

    assert score == "N/A"
    assert "No assessed control" in basis
