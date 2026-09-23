from security_agent.models.assessment import (
    AssessmentState,
    SecurityAssessment,
    SecurityEvidence,
)
from security_agent.models.response import SecurityStatus


def test_security_evidence_defaults():
    evidence = SecurityEvidence(
        source="application_profile",
    )

    assert evidence.source == "application_profile"
    assert evidence.data == {}


def test_security_evidence_with_data():
    evidence = SecurityEvidence(
        source="application_profile",
        data={
            "authentication": {
                "enabled": True,
                "type": "JWT",
            }
        },
    )

    assert evidence.source == "application_profile"
    assert evidence.data["authentication"]["enabled"] is True
    assert evidence.data["authentication"]["type"] == "JWT"


def test_security_assessment_defaults():
    assessment = SecurityAssessment(
        control="JWT",
        result=SecurityStatus.PASS,
        security_score="100%",
    )

    assert assessment.control == "JWT"
    assert assessment.result == SecurityStatus.PASS
    assert assessment.security_score == "100%"
    assert assessment.issues == []
    assert assessment.recommendations == []
    assert assessment.evidence_sources == []


def test_security_assessment_with_details():
    assessment = SecurityAssessment(
        control="JWT",
        result=SecurityStatus.FAIL,
        security_score="0%",
        issues=[
            "JWT expiration validation is disabled."
        ],
        recommendations=[
            "Enable JWT expiration validation."
        ],
        evidence_sources=[
            "application_profile"
        ],
    )

    assert assessment.control == "JWT"
    assert assessment.result == SecurityStatus.FAIL
    assert assessment.security_score == "0%"

    assert assessment.issues == [
        "JWT expiration validation is disabled."
    ]

    assert assessment.recommendations == [
        "Enable JWT expiration validation."
    ]

    assert assessment.evidence_sources == [
        "application_profile"
    ]


def test_assessment_state_defaults():
    state = AssessmentState(
        objective="Check JWT authentication"
    )

    assert state.objective == "Check JWT authentication"
    assert state.evidence == []
    assert state.assessments == []
    assert state.missing_evidence == []
    assert state.conflicts == []


def test_assessment_state_with_evidence():
    evidence = SecurityEvidence(
        source="application_profile",
        data={
            "authentication": {
                "enabled": True,
                "type": "JWT",
            }
        },
    )

    state = AssessmentState(
        objective="Check JWT authentication",
        evidence=[evidence],
    )

    assert state.objective == "Check JWT authentication"
    assert len(state.evidence) == 1
    assert state.evidence[0].source == "application_profile"
    assert state.evidence[0].data["authentication"]["type"] == "JWT"


def test_assessment_state_with_assessment():
    assessment = SecurityAssessment(
        control="JWT",
        result=SecurityStatus.PASS,
        security_score="100%",
        evidence_sources=[
            "application_profile"
        ],
    )

    state = AssessmentState(
        objective="Check JWT authentication",
        assessments=[assessment],
    )

    assert len(state.assessments) == 1
    assert state.assessments[0].control == "JWT"
    assert state.assessments[0].result == SecurityStatus.PASS
    assert state.assessments[0].security_score == "100%"


def test_assessment_state_with_missing_evidence():
    state = AssessmentState(
        objective="Check OAuth configuration",
        missing_evidence=[
            "OAuth configuration is unavailable."
        ],
    )

    assert state.missing_evidence == [
        "OAuth configuration is unavailable."
    ]


def test_assessment_state_with_conflicts():
    state = AssessmentState(
        objective="Check JWT authentication",
        conflicts=[
            "Conflicting assessment results detected for security control 'JWT'."
        ],
    )

    assert len(state.conflicts) == 1
    assert "JWT" in state.conflicts[0]


def test_assessment_state_complete():
    evidence = SecurityEvidence(
        source="application_profile",
        data={
            "authentication": {
                "enabled": True,
                "type": "JWT",
            }
        },
    )

    assessment = SecurityAssessment(
        control="JWT",
        result=SecurityStatus.PASS,
        security_score="100%",
        evidence_sources=[
            "application_profile"
        ],
    )

    state = AssessmentState(
        objective="Check JWT authentication",
        evidence=[evidence],
        assessments=[assessment],
    )

    assert state.objective == "Check JWT authentication"
    assert len(state.evidence) == 1
    assert len(state.assessments) == 1
    assert state.missing_evidence == []
    assert state.conflicts == []