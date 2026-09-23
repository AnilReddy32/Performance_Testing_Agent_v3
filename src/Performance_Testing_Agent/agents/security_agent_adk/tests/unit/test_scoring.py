from security_agent.models.assessment import SecurityAssessment
from security_agent.models.response import SecurityStatus
from security_agent.security.scoring import calculate_security_score


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


def test_warning_returns_na():
    assessments = [
        make_assessment("JWT", SecurityStatus.PASS, "100%"),
        make_assessment("OAuth", SecurityStatus.WARNING, "N/A"),
    ]

    assert calculate_security_score(assessments) == "N/A"


def test_na_score_returns_na():
    assessments = [
        make_assessment("JWT", SecurityStatus.PASS, "100%"),
        make_assessment("OAuth", SecurityStatus.PASS, "N/A"),
    ]

    assert calculate_security_score(assessments) == "N/A"


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