"""
Schemas for the Report Agent.

ReportInput is a re-export of the Analysis Agent's output -- keeping it as
its own name here (rather than just importing AnalysisOutput) makes the
contract between the two agents explicit and lets it evolve independently
if you ever add report-specific fields (e.g. a requested output format).
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from ..analysis.schemas import AnalysisOutput


class ReportInput(AnalysisOutput):
    """Exactly what Analysis Agent produces, optionally with a requested
    output format the orchestrator/user can specify."""
    requested_format: Literal["txt", "pdf", "both"] = "pdf"


class ReportSection(BaseModel):
    title: str
    content: str


class ReportOutput(BaseModel):
    job_id: str
    application: str
    scenario: str
    overall_status: Optional[str] = None
    report_format: str  # txt | pdf
    file_path: str
    generated_at: str
    sections: List[ReportSection] = Field(default_factory=list)
    rejected: bool = False  # true when the underlying analysis was invalid
