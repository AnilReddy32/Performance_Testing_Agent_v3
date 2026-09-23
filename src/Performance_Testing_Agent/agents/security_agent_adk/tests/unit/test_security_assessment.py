from security_agent.models.assessment import (
    AssessmentState,
    SecurityAssessment,
    SecurityEvidence,
)
from security_agent.models.response import SecurityStatus
from security_agent.security.assessment import (
    add_assessment,
    add_evidence,
    add_missing_evidence,
    build_security_response,
    determine_overall_status,
    detect_conflicts,
    update_conflicts,
)


def test_add_evidence():
    state = AssessmentState(
        objective="Check authentication"
    )

    result = add_evidence(
        state=state,
        source="application_profile",
        data={
            "authentication": {
                "enabled": True,
                "type": "JWT",
            }
        },
    )

    assert result is state
    assert len(result.evidence) == 1

    assert result.evidence[0].source == "application_profile"
    assert result.evidence[0].data["authentication"]["enabled"] is True


def test_add_multiple_evidence():
    state = AssessmentState(
        objective="Check application security"
    )

    add_evidence(
        state,
        "application_profile",
        {"authentication": {"enabled": True}},
    )

    add_evidence(
        state,
        "api_information",
        {"endpoints": ["/login", "/users"]},
    )

    assert len(state.evidence) == 2
    assert state.evidence[0].source == "application_profile"
    assert state.evidence[1].source == "api_information"


def test_add_missing_evidence():
    state = AssessmentState(
        objective="Check OAuth configuration"
    )

    result = add_missing_evidence(
        state,
        "OAuth configuration is unavailable.",
    )

    assert result is state
    assert result.missing_evidence == [
        "OAuth configuration is unavailable."
    ]


def test_add_missing_evidence_does_not_duplicate():
    state = AssessmentState(
        objective="Check OAuth configuration"
    )

    requirement = "OAuth configuration is unavailable."

    add_missing_evidence(state, requirement)
    add_missing_evidence(state, requirement)

    assert state.missing_evidence == [requirement]


def test_add_assessment():
    state = AssessmentState(
        objective="Check JWT authentication"
    )

    validator_result = {
        "status": "PASS",
        "security_score": "100%",
        "issues": [],
        "recommendations": [],
    }

    result = add_assessment(
        state=state,
        control="JWT",
        result=validator_result,
        evidence_sources=["application_profile"],
    )

    assert result is state
    assert len(result.assessments) == 1

    assessment = result.assessments[0]

    assert assessment.control == "JWT"
    assert assessment.result == SecurityStatus.PASS
    assert assessment.security_score == "100%"
    assert assessment.issues == []
    assert assessment.recommendations == []
    assert assessment.evidence_sources == [
        "application_profile"
    ]


def test_add_assessment_with_issues_and_recommendations():
    state = AssessmentState(
        objective="Check JWT authentication"
    )

    validator_result = {
        "status": "FAIL",
        "security_score": "0%",
        "issues": [
            "JWT expiration validation is disabled."
        ],
        "recommendations": [
            "Enable JWT expiration validation."
        ],
    }

    add_assessment(
        state=state,
        control="JWT",
        result=validator_result,
    )

    assessment = state.assessments[0]

    assert assessment.result == SecurityStatus.FAIL
    assert assessment.security_score == "0%"
    assert assessment.issues == [
        "JWT expiration validation is disabled."
    ]
    assert assessment.recommendations == [
        "Enable JWT expiration validation."
    ]
    assert assessment.evidence_sources == []


def test_determine_overall_status_no_assessments():
    state = AssessmentState(
        objective="Check security"
    )

    assert determine_overall_status(state) == SecurityStatus.WARNING


def test_determine_overall_status_pass():
    state = AssessmentState(
        objective="Check security",
        assessments=[
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.PASS,
                security_score="100%",
            )
        ],
    )

    assert determine_overall_status(state) == SecurityStatus.PASS


def test_determine_overall_status_fail():
    state = AssessmentState(
        objective="Check security",
        assessments=[
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.FAIL,
                security_score="0%",
            )
        ],
    )

    assert determine_overall_status(state) == SecurityStatus.FAIL


def test_determine_overall_status_warning():
    state = AssessmentState(
        objective="Check security",
        assessments=[
            SecurityAssessment(
                control="OAuth",
                result=SecurityStatus.WARNING,
                security_score="N/A",
            )
        ],
    )

    assert determine_overall_status(state) == SecurityStatus.WARNING


def test_determine_overall_status_fail_takes_precedence_over_warning():
    state = AssessmentState(
        objective="Check security",
        assessments=[
            SecurityAssessment(
                control="OAuth",
                result=SecurityStatus.WARNING,
                security_score="N/A",
            ),
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.FAIL,
                security_score="0%",
            ),
        ],
    )

    assert determine_overall_status(state) == SecurityStatus.FAIL


def test_determine_overall_status_conflict_returns_warning():
    state = AssessmentState(
        objective="Check security",
        conflicts=[
            "Conflicting assessment results detected."
        ],
        assessments=[
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.PASS,
                security_score="100%",
            )
        ],
    )

    assert determine_overall_status(state) == SecurityStatus.WARNING


def test_determine_overall_status_missing_evidence_returns_warning():
    state = AssessmentState(
        objective="Check security",
        missing_evidence=[
            "OAuth configuration is unavailable."
        ],
    )

    assert determine_overall_status(state) == SecurityStatus.WARNING


def test_detect_conflicts_no_conflicts():
    state = AssessmentState(
        objective="Check JWT"
    )

    state.assessments.extend(
        [
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.PASS,
                security_score="100%",
            ),
            SecurityAssessment(
                control="OAuth",
                result=SecurityStatus.PASS,
                security_score="100%",
            ),
        ]
    )

    assert detect_conflicts(state) == []


def test_detect_conflicts_same_control_different_results():
    state = AssessmentState(
        objective="Check JWT"
    )

    state.assessments.extend(
        [
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.PASS,
                security_score="100%",
            ),
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.FAIL,
                security_score="0%",
            ),
        ]
    )

    conflicts = detect_conflicts(state)

    assert len(conflicts) == 1
    assert conflicts[0] == (
        "Conflicting assessment results detected for "
        "security control 'JWT'."
    )


def test_detect_conflicts_same_control_same_result():
    state = AssessmentState(
        objective="Check JWT"
    )

    state.assessments.extend(
        [
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.PASS,
                security_score="100%",
            ),
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.PASS,
                security_score="100%",
            ),
        ]
    )

    assert detect_conflicts(state) == []


def test_update_conflicts():
    state = AssessmentState(
        objective="Check JWT"
    )

    state.assessments.extend(
        [
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.PASS,
                security_score="100%",
            ),
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.FAIL,
                security_score="0%",
            ),
        ]
    )

    result = update_conflicts(state)

    assert result is state
    assert len(result.conflicts) == 1
    assert "JWT" in result.conflicts[0]


def test_update_conflicts_clears_old_conflicts():
    state = AssessmentState(
        objective="Check security",
        conflicts=[
            "Old conflict"
        ],
        assessments=[
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.PASS,
                security_score="100%",
            )
        ],
    )

    update_conflicts(state)

    assert state.conflicts == []


def test_build_security_response_single_pass():
    state = AssessmentState(
        objective="Check JWT authentication",
        assessments=[
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.PASS,
                security_score="100%",
            )
        ],
    )

    response = build_security_response(state)

    assert response.status == SecurityStatus.PASS
    assert response.security_score == "100%"
    assert response.issues == []
    assert response.recommendations == []


def test_build_security_response_single_fail():
    state = AssessmentState(
        objective="Check JWT authentication",
        assessments=[
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.FAIL,
                security_score="0%",
                issues=[
                    "JWT expiration validation is disabled."
                ],
                recommendations=[
                    "Enable JWT expiration validation."
                ],
            )
        ],
    )

    response = build_security_response(state)

    assert response.status == SecurityStatus.FAIL
    assert response.security_score == "0%"

    assert response.issues == [
        "JWT expiration validation is disabled."
    ]

    assert response.recommendations == [
        "Enable JWT expiration validation."
    ]


def test_build_security_response_multiple_assessments_uses_centralized_score():
    state = AssessmentState(
        objective="Check multiple security controls",
        assessments=[
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.PASS,
                security_score="100%",
            ),
            SecurityAssessment(
                control="RBAC",
                result=SecurityStatus.FAIL,
                security_score="0%",
                issues=[
                    "RBAC validation is incomplete."
                ],
                recommendations=[
                    "Review RBAC permissions."
                ],
            ),
        ],
    )

    response = build_security_response(state)

    assert response.status == SecurityStatus.FAIL

    # Centralized scoring:
    # (100 + 0) / 2 = 50
    assert response.security_score == "50%"

    assert response.issues == [
        "RBAC validation is incomplete."
    ]

    assert response.recommendations == [
        "Review RBAC permissions."
    ]


def test_build_security_response_warning_has_na_score():
    state = AssessmentState(
        objective="Check OAuth",
        assessments=[
            SecurityAssessment(
                control="OAuth",
                result=SecurityStatus.WARNING,
                security_score="N/A",
            )
        ],
    )

    response = build_security_response(state)

    assert response.status == SecurityStatus.WARNING
    assert response.security_score == "N/A"


def test_build_security_response_missing_evidence():
    state = AssessmentState(
        objective="Check OAuth",
        missing_evidence=[
            "OAuth configuration is unavailable."
        ],
    )

    response = build_security_response(state)

    assert response.status == SecurityStatus.WARNING
    assert response.security_score == "N/A"

    assert response.issues == [
        "OAuth configuration is unavailable."
    ]


def test_build_security_response_conflict():
    state = AssessmentState(
        objective="Check JWT",
        assessments=[
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.PASS,
                security_score="100%",
            ),
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.FAIL,
                security_score="0%",
            ),
        ],
    )

    update_conflicts(state)

    response = build_security_response(state)

    assert response.status == SecurityStatus.WARNING
    assert response.security_score == "50%"

    assert response.issues == [
        "Conflicting assessment results detected for "
        "security control 'JWT'."
    ]

def test_build_security_response_collects_all_issues_and_recommendations():
    state = AssessmentState(
        objective="Check security",
        assessments=[
            SecurityAssessment(
                control="JWT",
                result=SecurityStatus.PASS,
                security_score="100%",
                issues=["JWT issue"],
                recommendations=["JWT recommendation"],
            ),
            SecurityAssessment(
                control="RBAC",
                result=SecurityStatus.FAIL,
                security_score="0%",
                issues=["RBAC issue"],
                recommendations=["RBAC recommendation"],
            ),
        ],
        missing_evidence=[
            "OAuth configuration unavailable."
        ],
        conflicts=[
            "Conflicting assessment results detected."
        ],
    )

    response = build_security_response(state)

    assert response.status == SecurityStatus.WARNING
    assert response.security_score == "50%"

    assert response.issues == [
        "JWT issue",
        "RBAC issue",
        "OAuth configuration unavailable.",
        "Conflicting assessment results detected.",
    ]

    assert response.recommendations == [
        "JWT recommendation",
        "RBAC recommendation",
    ]