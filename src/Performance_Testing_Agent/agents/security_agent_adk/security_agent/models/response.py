from enum import Enum
from pydantic import BaseModel, Field


class SecurityStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"


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
        description="Security score represented as a percentage."
    )

    issues: list[str] = Field(
        default_factory=list,
        description="Security issues identified during the assessment."
    )

    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommended actions based on identified issues."
    )