from typing import Any
from pydantic import BaseModel, Field
from security_agent.models.response import SecurityStatus


class SecurityEvidence(BaseModel):
    """
    Evidence retrieved during a security assessment.
    """

    source: str = Field(
        ...,
        description="Tool or source that provided the evidence.",
    )

    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Evidence returned by the source.",
    )


class SecurityAssessment(BaseModel):
    """
    Result produced by a deterministic security validator.
    """

    control: str = Field(
        ...,
        description="Security control assessed.",
    )

    result: SecurityStatus = Field(
        ...,
        description="Assessment result.",
    )

    security_score: str = Field(
        ...,
        description="Validator-provided security score.",
    )

    issues: list[str] = Field(
        default_factory=list,
    )

    recommendations: list[str] = Field(
        default_factory=list,
    )

    evidence_sources: list[str] = Field(
        default_factory=list,
        description="Evidence sources used for this assessment.",
    )


class AssessmentState(BaseModel):
    """
    Internal state maintained throughout a Security Agent assessment.

    This model is intentionally separate from SecurityResponse.
    """

    objective: str = Field(
        ...,
        description="Original security assessment objective.",
    )

    evidence: list[SecurityEvidence] = Field(
        default_factory=list,
    )

    assessments: list[SecurityAssessment] = Field(
        default_factory=list,
    )

    missing_evidence: list[str] = Field(
        default_factory=list,
    )

    conflicts: list[str] = Field(
        default_factory=list,
    )