from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class SecurityStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"


class SecurityControlResult(BaseModel):
    """Result and evidence references for one assessed security control."""

    control: str
    assessment_status: Literal["assessed", "not_assessed"] = "assessed"
    status: SecurityStatus
    assessment_basis: Literal[
        "configuration_declaration", "live_observation"
    ] = "configuration_declaration"
    severity: Literal["critical", "high", "medium", "low", "unknown"] = "unknown"
    security_score: str = "N/A"
    security_score_basis: str = ""
    required_evidence: list[str] = Field(default_factory=list)
    evidence_fields: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    evidence_references: list[str] = Field(default_factory=list)


class SecurityResponse(BaseModel):
    """
    Standard output contract for the Security Agent.
    """

    status: SecurityStatus = Field(
        ...,
        description="Overall result of the requested security assessment."
    )

    security_score: str = Field(
        ...,
        description="Mean of numeric scores from assessed controls, or N/A when none can be calculated."
    )

    security_score_basis: str = Field(
        default="",
        description="Explains which assessed controls contribute to the score and what was excluded.",
    )

    issues: list[str] = Field(
        default_factory=list,
        description="Security issues identified during the assessment."
    )

    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommended actions based on identified issues."
    )

    schema_version: Literal["1.0"] = "1.0"
    job_id: str | None = None
    test_case_id: str | None = None
    test_case_name: str | None = None
    target_origin: str | None = None
    configured_application: str | None = None
    profile_match_status: Literal["matched", "no_match", "ambiguous"] = "no_match"
    profile_id: str | None = None
    profile_version: str | None = None
    profile_match_reason: str | None = None
    endpoint: str | None = None
    method: str | None = None
    environment: str | None = None
    execution_mode: Literal["REAL", "SIMULATED"] | None = None
    assessment_mode: Literal["configuration_only", "configuration_and_live"] = "configuration_only"
    live_testing_requested: bool = False
    live_testing_authorized: bool = False
    live_testing_status: Literal[
        "not_requested", "not_run", "blocked", "completed", "failed"
    ] = "not_requested"
    live_test_result: dict[str, Any] | None = None
    requested_controls: list[str] = Field(default_factory=list)
    requested_controls_source: Literal[
        "explicit_request", "overall_security_default", "no_control_selected"
    ] = "overall_security_default"
    assessed_controls: list[str] = Field(default_factory=list)
    not_assessed_controls: list[str] = Field(default_factory=list)
    coverage: dict[str, Any] = Field(default_factory=dict)
    required_evidence_by_control: dict[str, list[str]] = Field(default_factory=dict)
    control_results: list[SecurityControlResult] = Field(default_factory=list)
    evidence_references: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
